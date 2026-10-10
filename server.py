import re
import os
import json
import gzip
import traceback
import html as html_lib
import urllib.parse
import urllib.request
import urllib.error
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

import solution_loader  # noqa: E402  (sumber Layer 3: solusi spesifik Claude)
import tutor_engine    # noqa: E402  (mesin tutor konversasional berbasis LLM)
import tutor_llm       # noqa: E402  (abstraksi provider LLM)
import visitor_log     # noqa: E402  (pencatat pengunjung + dashboard /pengunjung)
import tutor_store     # noqa: E402  (persistensi percakapan — SQLite)
import feature_flags   # noqa: E402  (feature flags Autopsi/Sprint — FASE 0 T0.7)
import auth_verify     # noqa: E402  (verifikasi JWT Supabase — FASE 2 T2.11)
try:
    from autopsy import analyzer as autopsy_analyzer  # noqa: E402  (Fase 4)
    from autopsy import evidence as autopsy_evidence  # noqa: E402  (Fase A2)
    from autopsy import coach as autopsy_coach        # noqa: E402  (Fase A3)
    from autopsy import quota as autopsy_quota        # noqa: E402  (Fase A5)
except ImportError:
    autopsy_analyzer = None
    autopsy_evidence = None
    autopsy_coach = None
    autopsy_quota = None

tutor_store.init_db()  # skema ai_tutor_* dibuat idempoten saat server dimuat
feature_flags.init_flags()  # tabel feature_flags + seed 7 flag OFF (idempoten)

# ============================================================================
# CONCURRENCY QUEUE UNTUK 50 USER (SEMAPHORE)
# ============================================================================
MAX_CONCURRENT_LLM = int(os.environ.get("LLM_MAX_CONCURRENT", "6"))
_llm_concurrency_semaphore = threading.Semaphore(MAX_CONCURRENT_LLM)
_COACH_CACHE = {}         # {attempt_id: coach_result_dict}
_COACH_RATE_LIMIT = {}    # {user_id: [timestamps]}

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# MODE DEMO PUBLIK (bagikan via tunnel)
# Saat PUBLIC_DEMO=1 (dipakai oleh bagikan_online.ps1), endpoint administratif
# dimatikan supaya pengunjung publik tidak bisa:
#   - me-reset kuota AI (/api/tutor/reset_quota)
#   - menyalakan/menghapus swarm scraper yang memakai API key (/api/swarm/*)
#   - memakai endpoint tutor legacy tanpa kuota (/api/ai-tutor)
# ============================================================================
PUBLIC_DEMO = os.environ.get("PUBLIC_DEMO", "0") == "1"
DEMO_BLOCKED_PATHS = ('/api/tutor/reset_quota', '/api/swarm/start', '/api/swarm/reset', '/api/ai-tutor',
                       # Endpoint tutor pemakai kuota LLM (dulu bocor ke publik saat demo)
                       '/api/tutor/chat', '/api/tutor/new', '/api/tutor/state')

# Dashboard pengunjung hanya boleh dibuka di server utama (bukan demo publik).
# '/pengunjung.html' ikut diblokir: cek lama hanya cocok path eksak '/pengunjung',
# padahal file statisnya bisa diakses langsung lewat static serving.
ADMIN_VISITOR_PATHS = ('/pengunjung', '/pengunjung.html', '/api/admin/visitors')

# FAIL-FAST keamanan: kunci admin dashboard pengunjung WAJIB diset lewat env
# VISITOR_ADMIN_KEY. Nilai default "tka-admin" (mudah ditebak) tidak boleh lagi
# dipakai — server menolak start bila env belum diset.
if not os.environ.get("VISITOR_ADMIN_KEY"):
    raise SystemExit(
        "FATAL: VISITOR_ADMIN_KEY belum diset. "
        "Set environment variable VISITOR_ADMIN_KEY dengan kunci acak yang kuat "
        "sebelum menjalankan server."
    )

# ============================================================================
# KONSTANTA KEAMANAN (Fase 2)
# ============================================================================
# Batas ukuran body POST: request lebih besar ditolak 413 di awal do_POST.
MAX_POST_BYTES = 1 * 1024 * 1024
# Drain dibatasi agar koneksi tetap bersih tanpa menyedot memori tak terbatas.
MAX_DRAIN_BYTES = 8 * 1024 * 1024

# Allowlist ekstensi file statis frontend yang boleh disajikan.
_STATIC_EXTS = (
    '.html', '.htm', '.css', '.js', '.mjs', '.map',
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.otf', '.eot',
    '.json', '.txt', '.xml', '.webmanifest', '.mp4', '.webm', '.mp3',
)
_IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico')
# Direktori top-level yang isinya boleh disajikan (selain root proyek).
# 'data' ditangani khusus: hanya file gambar di dalam folder images/.
_STATIC_OK_TOPDIRS = ('images', 'cbt_images', 'tka',
                      'workspace_akun', 'workspace_modul', 'workspace_progres',
                      'vendor')

# ============================================================================
# INDEKS NAMA FILE data/ (Fase 2, Fix 5)
# Dibangun SEKALI saat server start — menggantikan os.walk() per-request
# yang lambat di folder data/ (~268MB) pada find_question_image_paths &
# translate_path.
# ============================================================================
def _build_data_file_index():
    idx = {}
    data_root = os.path.join(BASE_DIR, "data")
    try:
        for root, _dirs, files in os.walk(data_root):
            for fn in files:
                idx.setdefault(fn, []).append(os.path.join(root, fn))
    except Exception:
        pass
    return idx

_DATA_FILE_INDEX = _build_data_file_index()

# ============================================================================
# LOG ERROR SERVER (Fase 2, Fix 3c)
# Traceback lengkap HANYA ditulis ke file ini — klien menerima pesan generik.
# ============================================================================
_ERROR_LOG_PATH = os.path.join(BASE_DIR, "scratch", "server_errors.log")


def _log_server_error(exc, context=""):
    """Tulis traceback lengkap ke scratch/server_errors.log (tidak ke klien)."""
    try:
        os.makedirs(os.path.dirname(_ERROR_LOG_PATH), exist_ok=True)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(_ERROR_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(f"[{ts}] {context} :: {type(exc).__name__}: {exc}\n")
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=fh)
            fh.write("\n")
    except Exception:
        pass

# ============================================================================
# LAPISAN KANONIS (data/canonical_questions/) — sumber konteks AI
# ============================================================================
# Konteks soal untuk AI Tutor & Tata Cara Penyelesaian kini bersumber dari
# lapisan kanonis: teks soal verbatim + formula $data-latex$ resmi + transkripsi
# vision + kunci resmi + langkah penyelesaian hasil Claude (solution_steps_claude).
# Learning JSON tetap dipakai untuk quick prompts & fallback UI.
CANON_DIR = os.path.join(BASE_DIR, "data", "canonical_questions")
SUBJECT_SLUGS = {
    "matematika": {1: "matematika_paket_1", 2: "matematika_paket_2"},
    "bahasa_inggris": {1: "bahasa_inggris_paket_1", 2: "bahasa_inggris_paket_2"},
    "ekonomi": {1: "ekonomi_paket_1", 2: "ekonomi_paket_2"},
    "kewirausahaan": {1: "kewirausahaan_paket_1", 2: "kewirausahaan_paket_2"},
    "geografi": {1: "geografi_paket_1", 2: "geografi_paket_2"},
    "fisika": {1: "fisika_paket_1", 2: "fisika_paket_2"},
    "kimia": {1: "kimia_paket_1", 2: "kimia_paket_2"},
    "biologi": {1: "biologi_paket_1", 2: "biologi_paket_2"},
    "bahasa_indonesia": {1: "bahasa_indonesia_paket_1", 2: "bahasa_indonesia_paket_2"},
    "sosiologi": {1: "sosiologi_paket_1", 2: "sosiologi_paket_2"},
    "sejarah": {1: "sejarah_paket_1", 2: "sejarah_paket_2"},
    "antropologi": {1: "antropologi_paket_1", 2: "antropologi_paket_2"},
    "ppkn": {1: "ppkn_paket_1", 2: "ppkn_paket_2"},
    "matematika_lanjut": {1: "matematika_lanjut_paket_1", 2: "matematika_lanjut_paket_2"},
    "bahasa_indonesia_lanjut": {1: "bahasa_indonesia_lanjut_paket_1", 2: "bahasa_indonesia_lanjut_paket_2"},
    "bahasa_inggris_lanjut": {1: "bahasa_inggris_lanjut_paket_1", 2: "bahasa_inggris_lanjut_paket_2"},
    "bahasa_arab": {1: "bahasa_arab_paket_1", 2: "bahasa_arab_paket_2"},
    "bahasa_jepang": {1: "bahasa_jepang_paket_1", 2: "bahasa_jepang_paket_2"},
    "bahasa_jerman": {1: "bahasa_jerman_paket_1", 2: "bahasa_jerman_paket_2"},
    "bahasa_prancis": {1: "bahasa_prancis_paket_1", 2: "bahasa_prancis_paket_2"},
    "bahasa_mandarin": {1: "bahasa_mandarin_paket_1", 2: "bahasa_mandarin_paket_2"},
    "bahasa_korea": {1: "bahasa_korea_paket_1", 2: "bahasa_korea_paket_2"},
}
_canon_cache = {}
_lrn_cache = {}
_sidecar_cache = {}


def load_sidecar_doc(subject, paket):
    slug = get_subject_slug(subject, paket)
    path = os.path.join(BASE_DIR, "data", f"{slug}_sidecar_transcriptions.json")
    if not os.path.exists(path):
        return {}
    mtime = os.path.getmtime(path)
    cached = _sidecar_cache.get(slug)
    if cached and cached.get("_mtime") == mtime:
        return cached["doc"]
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:
        doc = {}
    _sidecar_cache[slug] = {"doc": doc, "_mtime": mtime}
    return doc


def get_subject_slug(subject, paket):
    if subject in SUBJECT_SLUGS and paket in SUBJECT_SLUGS[subject]:
        return SUBJECT_SLUGS[subject][paket]
    return f"{subject}_paket_{paket}"


def load_canonical_doc(subject, paket):
    slug = get_subject_slug(subject, paket)
    path = os.path.join(CANON_DIR, f"{slug}.json")
    if not os.path.exists(path):
        return None
    mtime = os.path.getmtime(path)
    cached = _canon_cache.get(slug)
    if cached and cached.get("_mtime") == mtime:
        return cached["doc"]
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    _canon_cache[slug] = {"doc": doc, "_mtime": mtime}
    return doc


def load_learning_doc(subject, paket):
    slug = get_subject_slug(subject, paket)
    path = os.path.join(BASE_DIR, "data", f"{slug}_learning.json")
    if not os.path.exists(path):
        return None
    mtime = os.path.getmtime(path)
    cached = _lrn_cache.get(slug)
    if cached and cached.get("_mtime") == mtime:
        return cached["doc"]
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    _lrn_cache[slug] = {"doc": doc, "_mtime": mtime}
    return doc


def canonical_for(subject, paket, nomor):
    doc = load_canonical_doc(subject, paket)
    if doc and "questions" in doc:
        for q in doc["questions"]:
            if q.get("question_number") == nomor or q.get("number") == nomor:
                if "question_number" not in q and "number" in q:
                    q["question_number"] = q["number"]
                return q
    lrn = learning_for(subject, paket, nomor)
    if lrn:
        return {
            "id": lrn.get("id", f"{subject}_{paket}_{nomor}"),
            "number": nomor,
            "question_number": nomor,
            "type": lrn.get("tipe_soal", "Pilihan Ganda"),
            "stimulus": lrn.get("stimulus", {}).get("text", ""),
            "question": lrn.get("pertanyaan", {}).get("text", ""),
            "options": lrn.get("pilihan_jawaban", []),
            "visual_context": {},
            "official_answer": lrn.get("kunci_jawaban")
        }
    return None


def learning_for(subject, paket, nomor):
    doc = load_learning_doc(subject, paket)
    if not doc:
        return None
    for q in doc["soal"]:
        if q["nomor"] == nomor:
            return q
    return None


def format_visual_context(vc):
    """Susun visual_context kanonis menjadi teks yang dapat dibaca AI/siswa."""
    lines = []
    for f in vc.get("formulas", []):
        src = "data-latex resmi" if f.get("source") == "official data-latex" else "transkripsi vision"
        lines.append(f"- Formula ({src}): ${f['latex']}$")
    for grp, label in (("tables", "Tabel"), ("graphs", "Grafik"), ("diagrams", "Diagram"), ("others", "Visual lain")):
        for v in vc.get(grp, []):
            desc = v.get("description")
            if desc:
                lines.append(f"- {label} ({v.get('image', '')}):\n  {desc}")
            else:
                lines.append(f"- {label} ({v.get('image', '')}): [belum tertranskripsi]")
    n_unres = len(vc.get("unresolved", []))
    if n_unres:
        lines.append(f"- CATATAN: {n_unres} elemen visual belum terwakili teks (lihat gambar asli).")
    return "\n".join(lines) if lines else "Soal ini tidak memiliki elemen visual."


def format_kunci_display(q_data):
    """Format kunci jawaban (PG/PGK/pernyataan) menjadi string tampilan."""
    kunci = q_data.get("kunci_jawaban", "-")
    if isinstance(kunci, list):
        if kunci and all(":" in str(x) for x in kunci):
            return ", ".join(f"{str(x).split(':', 1)[0]} ({str(x).split(':', 1)[1]})" for x in kunci)
        return ", ".join(str(x) for x in kunci)
    return str(kunci)


# Konstanta backslash untuk clean_katex_artifacts() (rekonstruksi "\frac" dst.
# dari karakter kontrol peninggalan escape LaTeX yang salah tulis).
BS = "\\"


def clean_katex_artifacts(text):
    """Bersihkan artefak rendering KaTeX DOM innerText & teks rusak hasil
    ekstraksi DOM (rumus pecah per karakter + duplikat gema KaTeX).

    Perbaikan utama didelegasikan ke text_quality.repair_math_text (pemetaan
    huruf matematika unicode, penggabungan baris pecah per karakter, buang
    gema duplikat); replacements LaTeX mentah (\\times, \\neq, dll.) tetap
    dijalankan sebagai lapis tambahan.
    """
    if not text or not isinstance(text, str):
        return text

    # (a) Rekonstruksi karakter kontrol peninggalan escape LaTeX yang salah tulis
    # saat generasi data ("\frac" tertulis sebagai FF+rac, "\rightarrow" sebagai
    # CR+ightarrow, dst.). CR/FF/VT/BS/BEL diikuti huruf = hampir pasti kasus ini;
    # \n dan \t tidak disentuh karena dipakai sebagai whitespace sah.
    _ctl_map = {chr(8): 'b', chr(11): 'v', chr(12): 'f', chr(7): 'a', chr(13): 'r'}
    text = re.sub(
        '([' + ''.join(_ctl_map.keys()) + '])([a-zA-Z]+)',
        lambda m: BS + _ctl_map[m.group(1)] + m.group(2),
        text,
    )

    # (b) Audit Kimi T-32/T-19/T-01: buang label internal & pembuka sirkular yang
    # membocorkan metadata ke siswa tanpa menambah penjelasan apa pun.
    text = re.sub(r'Kunci Pusmendik \[[^\]]*\]', '', text)
    text = re.sub(r'[Ss]esuai penetapan kunci resmi,?\s*', 'Hasil evaluasi: ', text)
    text = re.sub(r'[Bb]erdasarkan kunci resmi,?\s*', 'Hasil evaluasi: ', text)

    import text_quality
    text = text_quality.repair_math_text(text)

    # Ganti duplikasi LaTeX mentah yang diekstrak berantakan
    replacements = [
        (r'(?<![a-zA-Z])\\?times(?![a-zA-Z])', r'×'),
        (r'(?<![a-zA-Z])\\?neq(?![a-zA-Z])', r'≠'),
        (r'(?<![a-zA-Z])\\?leq(?![a-zA-Z])', r'≤'),
        (r'(?<![a-zA-Z])\\?geq(?![a-zA-Z])', r'≥'),
        (r'(?<![a-zA-Z])\\?pm(?![a-zA-Z])', r'±'),
        (r'(?<![a-zA-Z])\\?approx(?![a-zA-Z])', r'≈'),
        (r'(?<![a-zA-Z])\\?rightarrow(?![a-zA-Z])', r'→'),
        (r'(?<![a-zA-Z])\\?leftarrow(?![a-zA-Z])', r'←'),
        (r'(?<![a-zA-Z])\\?cdot(?![a-zA-Z])', r'·'),
        (r'(?<![a-zA-Z])\\?circ(?![a-zA-Z])', r'°'),
        (r'(?<![a-zA-Z])\\?degree(?![a-zA-Z])', r'°'),
    ]
    for pat, rep in replacements:
        text = re.sub(pat, rep, text)

    # Hapus spasi / baris kosong berlebih
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def build_canonical_context(canon, lrn_q, subject=None, paket=None):
    """Bungkus satu soal kanonis menjadi konteks teks lengkap untuk AI Tutor."""
    vc = canon.get("visual_context", {}) if canon else {}
    sidecars = load_sidecar_doc(subject, paket) if subject and paket else {}
    parts = []

    # 1. Stimulus Teks
    stim_text = (
        (canon.get("stimulus_text") if canon else "")
        or (canon.get("stimulus") if canon else "")
        or (lrn_q.get("stimulus", {}).get("text") if lrn_q else "")
    )
    if stim_text and stim_text.strip():
        parts.append("[STIMULUS]\n" + stim_text.strip())

    # 2. Pertanyaan / Soal Teks
    q_text = (
        (canon.get("question_text") if canon else "")
        or (canon.get("question") if canon else "")
        or (lrn_q.get("pertanyaan", {}).get("text") if lrn_q else "")
    )
    if q_text and q_text.strip():
        parts.append("[SOAL]\n" + q_text.strip())

    # 3. Pilihan Jawaban / Pernyataan
    statements = (lrn_q.get("pernyataan") if lrn_q else None) or (canon.get("statements") if canon else None)
    options = (lrn_q.get("pilihan_jawaban") if lrn_q else None) or (canon.get("options") if canon else None)

    if statements:
        st_lines = []
        for s in statements:
            k = s.get("key", "")
            txt = s.get("text") or s.get("display") or ""
            img_note = f" [Gambar: {s['image']['filename']}]" if s.get("image") else ""
            st_lines.append(f"  {k}. {txt}{img_note}")
        parts.append("[PERNYATAAN / ITEM KONDISI]\n" + "\n".join(st_lines))
    elif options:
        opt_lines = []
        if isinstance(options, dict):
            for k, v in options.items():
                opt_lines.append(f"  {k}. {v}")
        elif isinstance(options, list):
            for opt in options:
                k = opt.get("key", "")
                txt = opt.get("full_display") or opt.get("text") or (f"${opt['latex']}$" if opt.get("latex") else "")
                img_note = f" [Gambar: {opt['image']['filename']}]" if opt.get("image") else ""
                opt_lines.append(f"  {k}. {txt}{img_note}")
        if opt_lines:
            parts.append("[OPSI JAWABAN]\n" + "\n".join(opt_lines))

    # 4. Gambar dan Elemen Visual & Transkripsi Sidecar
    imgs = []
    if lrn_q:
        imgs = lrn_q.get("stimulus", {}).get("images", []) + lrn_q.get("pertanyaan", {}).get("images", [])
    img_lines = []
    for im in imgs:
        fn = im.get("filename", "") if isinstance(im, dict) else os.path.basename(str(im))
        if fn:
            img_lines.append(f"- Diagram/Gambar: {fn}")
            if fn in sidecars:
                desc = sidecars[fn].get("description", "")
                if desc:
                    img_lines.append(f"  [Transkripsi Teks & Rumus Gambar {fn}]:\n  {desc}")

    visual_text = format_visual_context(vc)
    if img_lines:
        visual_desc = "\n".join(img_lines)
        if visual_text and visual_text != "Soal ini tidak memiliki elemen visual.":
            visual_desc += "\n" + visual_text
        parts.append("[KONTEKS VISUAL / GAMBAR SOAL]\n" + visual_desc)
    elif visual_text and visual_text != "Soal ini tidak memiliki elemen visual.":
        parts.append("[KONTEKS VISUAL]\n" + visual_text)

    # 5. Kunci Resmi
    kunci_disp = format_kunci_display(lrn_q or {})
    parts.append(f"[KUNCI RESMI] {kunci_disp}")

    # 6. Informasi Diketahui dari Diagram / Soal
    if lrn_q and lrn_q.get("pembahasan"):
        pb = lrn_q["pembahasan"]
        if pb.get("diketahui"):
            parts.append(f"[INFORMASI DIKETAHUI DARI DIAGRAM & SOAL]\n{pb['diketahui']}")

    return {
        "id": (canon.get("id") if canon else None) or (lrn_q.get("id") if lrn_q else "q_unknown"),
        "type": (canon.get("type") if canon else None) or (lrn_q.get("tipe_soal") if lrn_q else "Pilihan Ganda"),
        "transcription_status": canon.get("transcription_status") if canon else "available",
        "soal_text": "\n\n".join(parts),
        "visual_text": (visual_desc if img_lines else visual_text) if (img_lines or (visual_text and visual_text != "Soal ini tidak memiliki elemen visual.")) else "Soal ini tidak memiliki elemen visual.",
        "formulas": [
            {"latex": f.get("latex", ""), "source": f.get("source", "")}
            for f in (canon.get("visual_context", {}).get("formulas", []) if canon else [])
        ],
        "langkah_claude": (canon.get("solution_steps_claude") if canon else []) or [],
        "kunci_display": kunci_disp,
    }


def collect_visual_items(canon):
    """Item visual (Layer 2) untuk panel — transkripsi teks dari gambar asli soal."""
    vc = canon.get("visual_context", {})
    items = []
    for grp, label in (("tables", "Tabel"), ("graphs", "Grafik"), ("diagrams", "Diagram"), ("others", "Visual")):
        for v in vc.get(grp, []):
            if v.get("description"):
                items.append({"kind": label, "description": v["description"]})
    return items


def _split_glossary_term(term):
    """Pecah istilah glosarium 'X (Y)' -> (simbol X, nama Y); tanpa kurung -> nama kosong."""
    t = str(term).strip()
    if t.endswith(")") and "(" in t:
        sym, name = t[:-1].split("(", 1)
        return sym.strip(), name.strip()
    return t, ""


def build_solution_payload(canon, lrn_q, subject=None, paket=None):
    """Payload pembahasan untuk panel 'Tata Cara & Langkah Penyelesaian Soal'.

    Konten = SOLUSI SPESIFIK SOAL (Layer 3) dari sumber AKTIF di registry
    (data/solution_sources/registry.json — mis. hasil Claude Sonnet Extra).
    Tidak ada fallback ke enrichment generik lama (q.pembahasan) di sini:
    bila sumber aktif/soal tidak ada, return None -> panel menampilkan state
    jujur 'Pembahasan belum tersedia'.

    Kunci yang ditampilkan SELALU kunci otoritatif (lrn_q). Kunci pada file
    solusi Claude hanya di-cross-check; hasilnya dilaporkan (bukan direkonsiliasi).
    Flag needs_manual_review dipertahankan apa adanya dari file sumber.
    """
    kunci_disp = format_kunci_display(lrn_q or {})
    sol = None
    if subject and paket:
        try:
            q_num = canon.get("question_number") or canon.get("number")
            sol = solution_loader.get_solution(subject, paket, q_num, kunci_disp)
        except Exception:
            sol = None
    if not sol:
        return None

    glosarium = []
    for g in sol.get("glossary", []):
        sym, name = _split_glossary_term(g.get("term", ""))
        glosarium.append({"simbol": sym, "nama": name, "arti": g.get("meaning", "")})

    mengapa = "\n\n".join(x for x in (clean_katex_artifacts(sol.get("reasoning")), clean_katex_artifacts(sol.get("why_correct"))) if x)
    langkah = [
        clean_katex_artifacts(f"{st.get('step', i + 1)}. {st.get('title', '')} — {st.get('explanation', '')}".strip(" —"))
        for i, st in enumerate(sol.get("steps", []))
    ]
    tips_lines = [f"• {clean_katex_artifacts(t)}" for t in sol.get("tips", [])]
    tips_lines += [f"⚠️ Jebakan umum: {clean_katex_artifacts(m)}" for m in sol.get("common_mistakes", [])]

    # Diketahui/Ditanyakan: ambil dari solusi bila ada, JANGAN auto-generate
    # dari stimulus_text mentah (berisi transkripsi AI yang tidak layak baca).
    diketahui = clean_katex_artifacts(sol.get("diketahui")) if sol.get("diketahui") else None
    ditanyakan = clean_katex_artifacts(sol.get("ditanyakan")) if sol.get("ditanyakan") else None

    return {
        "pembahasan": {
            "diketahui": diketahui,
            "ditanyakan": ditanyakan,
            "konsep_kunci": sol.get("concept_kunci", []),
            "glosarium_simbol": glosarium,
            "mengapa_begini": mengapa or None,
            "langkah_penyelesaian": langkah,
            "tips_trik": "\n".join(tips_lines) or None,
            "tips_list": [clean_katex_artifacts(t) for t in sol.get("tips", [])],
            "mistakes_list": [clean_katex_artifacts(m) for m in sol.get("common_mistakes", [])],
        },
        # Soal serupa (latihan pemantapan) ikut dalam payload agar AI Tutor
        # mengetahui latihan yang tampil ke siswa beserta kunci & pembahasannya.
        "soal_serupa": (lrn_q.get("soal_serupa") if lrn_q else None),
        "review": sol.get("review"),
        "key_crosscheck": sol.get("key_crosscheck"),
        "source": sol.get("source"),
        "visual_items": collect_visual_items(canon),
        "visual_unresolved": len(canon.get("visual_context", {}).get("unresolved", [])),
        "answer_display": kunci_disp,
        "canonical_id": canon["id"],
    }


SUBJECT_NAMES = {
    "matematika": "Matematika",
    "bahasa_inggris": "Bahasa Inggris",
    "ekonomi": "Ekonomi",
    "kewirausahaan": "Produk Kreatif & Kewirausahaan",
    "geografi": "Geografi",
    "fisika": "Fisika",
    "kimia": "Kimia",
    "biologi": "Biologi",
    "teknik_mesin": "Teknik Mesin (SMK)",
    "teknik_otomotif": "Teknik Otomotif (SMK)",
    "teknik_jaringan": "Teknik Jaringan dan Telekomunikasi (SMK)",
    "akuntansi": "Akuntansi dan Keuangan Lembaga (SMK)",
    "manajemen_perkantoran": "Manajemen Perkantoran dan Layanan Bisnis (SMK)",
}


def find_question_image_paths(subject, paket, lrn_q, canon):
    """Kumpulkan file gambar PNG/JPG fisik lokal yang ada pada soal untuk multimodal vision."""
    filenames = []

    # 1. Dari stimulus & pertanyaan learning json
    if lrn_q:
        for im in lrn_q.get("stimulus", {}).get("images", []) + lrn_q.get("pertanyaan", {}).get("images", []):
            if isinstance(im, dict) and im.get("filename"):
                filenames.append(im["filename"])
            elif isinstance(im, str):
                filenames.append(os.path.basename(im))

        # Regex dari html jika ada tag img
        for html_chunk in [lrn_q.get("stimulus", {}).get("html", ""), lrn_q.get("pertanyaan", {}).get("html", "")]:
            for m in re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_chunk or ""):
                filenames.append(os.path.basename(m))

    # 2. Dari canonical json
    if canon:
        for im in canon.get("images", []):
            if isinstance(im, dict) and im.get("filename"):
                filenames.append(im["filename"])
            elif isinstance(im, str):
                filenames.append(os.path.basename(im))

    # Hilangkan duplikat sembari menjaga urutan
    seen = set()
    unique_filenames = []
    for fn in filenames:
        clean_fn = fn.split("?")[0].strip()
        if clean_fn and clean_fn not in seen and not clean_fn.endswith((".gif", ".ico")):
            seen.add(clean_fn)
            unique_filenames.append(clean_fn)

    # Direktori pencarian fisik
    search_dirs = [
        os.path.join(BASE_DIR, "data", subject, f"paket_{paket}", "images"),
        os.path.join(BASE_DIR, "data", f"paket_{paket}", "images"),
        os.path.join(BASE_DIR, "data", subject, "images"),
        os.path.join(BASE_DIR, "data", "fisika", f"paket_{paket}", "images"),
        os.path.join(BASE_DIR, "data", "geografi", f"paket_{paket}", "images"),
    ]

    found_paths = []
    for fn in unique_filenames:
        found = False
        for d in search_dirs:
            cand = os.path.join(d, fn)
            if os.path.isfile(cand):
                if cand not in found_paths:
                    found_paths.append(cand)
                found = True
                break
        if not found:
            # Fallback: cari di indeks nama file (dibangun sekali saat start,
            # bukan os.walk per-request). Ambil kandidat pertama seperti dulu.
            hits = _DATA_FILE_INDEX.get(fn)
            if hits and hits[0] not in found_paths:
                found_paths.append(hits[0])

    return found_paths


def resolve_tutor_context(subject, paket, nomor):
    """Kumpulkan konteks tutor utk satu soal: Layer 2 + Layer 3 + kunci resmi.

    Kunci resmi (Layer 2) tetap satu-satunya otoritas; Layer 3 hanya referensi.
    """
    canon = canonical_for(subject, paket, nomor)
    lrn_q = learning_for(subject, paket, nomor)
    if not canon and not lrn_q:
        return None
    canon_ctx = build_canonical_context(canon, lrn_q, subject=subject, paket=paket)
    solution = build_solution_payload(canon, lrn_q, subject, paket)
    image_paths = find_question_image_paths(subject, paket, lrn_q, canon)
    return {
        "canonical_id": canon["id"] if canon else f"{subject}_p{paket}_q{nomor}",
        "canon_ctx": canon_ctx,
        "solution": solution,           # berisi pembahasan/review/source/crosscheck
        "official_answer": canon_ctx["kunci_display"],
        "subject_name": SUBJECT_NAMES.get(subject, subject.title()),
        "subject": subject,
        "paket": paket,
        "nomor": nomor,
        "image_paths": image_paths,
    }


def _refresh_tutor_summary(conversation_id):
    """Perbarui ringkasan bergulir bila percakapan panjang (gagal = abaikan)."""
    try:
        tutor_store.maybe_summarize(conversation_id, tutor_engine.summarize_older)
    except Exception:
        pass

# (Arsip mesin tutor heuristik berbasis aturan tetap ada di legacy_tutor.py,
#  tetapi endpoint /api/ai-tutor sudah dihapus — lihat do_POST -> 410 Gone.)


_client_active_context = {}  # ip -> {"subject": ..., "paket": ...}

# ============================================================================
# HALAMAN /audit — snapshot konten soal+pembahasan server-rendered (tanpa JS).
# Dipakai reviewer otomatis / model AI yang hanya bisa fetch HTML mentah.
# ============================================================================
_AUDIT_IMG_RE = re.compile(r'<img[^>]*>', re.I)


def _audit_text(fragment):
    """HTML Pusmendik -> teks polos (pertahankan $math$, tandai gambar)."""
    s = fragment or ''

    # Tabel dirender ulang sebagai baris "sel | sel" agar data tabel tidak hilang
    def _table_to_text(m):
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(0), re.I | re.S)
        lines = []
        for r in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.I | re.S)
            cells = [re.sub(r'<[^>]+>', ' ', c).strip() for c in cells]
            lines.append(' | '.join(c for c in cells if c))
        return '\n' + '\n'.join(lines) + '\n'
    s = re.sub(r'<table[^>]*>.*?</table>', _table_to_text, s, flags=re.I | re.S)

    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'</(p|div|li|tr|h[1-6]|td)>', '\n', s, flags=re.I)

    # Gambar: formula data-latex direkonstruksi sebagai $..$; alt text dipertahankan.
    # (Audit Kimi T-02..T-16: [GAMBAR] telanjang membuat soal tampak rusak padahal
    # aplikasi merendernya normal.)
    def _img_to_text(m):
        tag = m.group(0)
        lat = re.search(r'data-latex="([^"]*)"', tag)
        if lat:
            lat = html_lib.unescape(lat.group(1)).strip()
            if lat:
                return ' $' + lat + '$ '
        alt = re.search(r'alt="([^"]*)"', tag)
        if alt and alt.group(1).strip() and alt.group(1) != f'Pilihan {""}':
            return ' [GAMBAR: ' + alt.group(1).strip() + '] '
        srcm = re.search(r'src="([^"]*)"', tag)
        fn = srcm.group(1).split('/')[-1] if srcm else '?'
        return ' [GAMBAR: ' + fn + '] '
    s = _AUDIT_IMG_RE.sub(_img_to_text, s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html_lib.unescape(s)
    s = re.sub(r'<sup>|</sup>', '^', s, flags=re.I)
    s = re.sub(r'<sub>|</sub>', '_', s, flags=re.I)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n\s*\n+', '\n\n', s)
    return s.strip()


def _audit_option_text(opt):
    if isinstance(opt, str):
        return _audit_text(opt)
    if opt.get('text'):
        return _audit_text(opt['text'])
    if opt.get('latex'):
        return '$' + str(opt['latex']).strip('$') + '$'
    if opt.get('image'):
        img = opt['image']
        name = img.get('filename') if isinstance(img, dict) else str(img)
        return f"[GAMBAR OPSI: {name}]"
    return '(kosong)'


def _audit_block(label, value):
    if value in (None, '', [], '-'):
        return ''
    return f"<p><strong>{html_lib.escape(label)}:</strong></p><div class=\"blk\">{value}</div>"


def _audit_collect(subject, paket, dari, sampai):
    """Kumpulkan soal+pembahasan sebagai data teks polos utk renderer HTML/TXT."""
    items = []
    for nomor in range(dari, sampai + 1):
        lrn_q = learning_for(subject, paket, nomor)
        canon = canonical_for(subject, paket, nomor)
        if not lrn_q and not canon:
            items.append({"nomor": nomor, "missing": True})
            continue

        tipe = (lrn_q or {}).get('tipe_soal') or (canon or {}).get('type') or 'Pilihan Ganda'
        topik = (lrn_q or {}).get('topik') or ''
        # Utamakan html (memuat <img data-latex> & tabel) di atas text agar
        # halaman audit setia ke soal asli (audit Kimi T-02..T-16).
        stim = ((lrn_q or {}).get('stimulus') or {}).get('html') or (lrn_q or {}).get('stimulus', {}).get('text') or (canon or {}).get('stimulus') or ''
        tanya = ((lrn_q or {}).get('pertanyaan') or {}).get('html') or (lrn_q or {}).get('pertanyaan', {}).get('text') or (canon or {}).get('question') or ''
        pilihan = (lrn_q or {}).get('pilihan_jawaban') or (canon or {}).get('options') or []
        kunci = (lrn_q or {}).get('kunci_jawaban') or (canon or {}).get('official_answer')
        pernyataan = (lrn_q or {}).get('pernyataan') or []

        pembahasan = None
        answer_display = None
        review = {}
        try:
            sol = build_solution_payload(canon, lrn_q, subject, paket)
            pembahasan = sol.get('pembahasan') or {}
            answer_display = sol.get('answer_display')
            review = sol.get('review') or {}
        except Exception:
            pembahasan = None

        if isinstance(kunci, dict):
            kunci_txt = '; '.join(f"{k}: {v}" for k, v in kunci.items())
        elif isinstance(kunci, list):
            kunci_txt = ', '.join(str(k) for k in kunci)
        else:
            kunci_txt = str(kunci or '-')
        if answer_display:
            kunci_txt += f" (answer_display: {answer_display})"

        blk = []
        if pembahasan:
            if pembahasan.get('diketahui'):
                blk.append(('Diketahui', _audit_text(pembahasan['diketahui'])))
            if pembahasan.get('ditanyakan'):
                blk.append(('Ditanyakan', _audit_text(pembahasan['ditanyakan'])))
            if pembahasan.get('konsep_kunci'):
                blk.append(('Konsep kunci', _audit_join_list(pembahasan['konsep_kunci'])))
            if pembahasan.get('mengapa_begini'):
                blk.append(('Mengapa rumus ini dipakai', _audit_text(pembahasan['mengapa_begini'])))
            langkah = pembahasan.get('langkah_penyelesaian') or []
            if langkah:
                step_txt = '\n\n'.join(
                    f"Langkah {i}: {_audit_text(str(s))}" for i, s in enumerate(langkah, 1))
                blk.append(('Langkah penyelesaian', step_txt))
            if pembahasan.get('glosarium_simbol'):
                glos = '\n'.join(f"{g.get('simbol', '')} = {g.get('arti', '')}"
                                 for g in pembahasan['glosarium_simbol'])
                blk.append(('Glosarium simbol', glos))
            if pembahasan.get('tips_list'):
                blk.append(('Tips', _audit_join_list(pembahasan['tips_list'])))
            if pembahasan.get('mistakes_list'):
                blk.append(('Jebakan umum', _audit_join_list(pembahasan['mistakes_list'])))
        warn = None
        if review.get('needs_manual_review'):
            warn = str(review.get('review_reason', ''))

        items.append({
            "nomor": nomor, "missing": False, "tipe": str(tipe), "topik": str(topik),
            "stimulus": _audit_text(stim), "pertanyaan": _audit_text(tanya),
            "pernyataan": [
                (
                    lambda st: f"{st.get('key', '')}) " + (
                        _audit_text(st.get('html') or st.get('text', ''))
                        or (f"[GAMBAR PERNYATAAN: {(st.get('image') or {}).get('filename', '?')}]" if st.get('image') else '(kosong)')
                    )
                )(st)
                for st in pernyataan
            ],
            "opsi": [f"{(o.get('key', '?') if isinstance(o, dict) else '?')}) {_audit_option_text(o)}"
                     for o in pilihan],
            "kunci": kunci_txt, "pembahasan": blk, "warn": warn,
        })
    return items


def render_audit_text(subject, paket, dari, sampai):
    items = _audit_collect(subject, paket, dari, sampai)
    out = [
        f"AUDIT KONTEN — {subject} Paket {paket} — Nomor {dari}-{sampai}",
        "Teks di dalam $...$ adalah LaTeX matematika. [GAMBAR] = gambar soal/opsi asli",
        "yang hanya terlihat di aplikasi interaktif.",
        "=" * 60,
    ]
    for it in items:
        out.append("")
        out.append("=" * 60)
        if it.get("missing"):
            out.append(f"SOAL {it['nomor']} — (tidak ditemukan di data)")
            continue
        out.append(f"SOAL {it['nomor']} — {it['tipe']}")
        if it["topik"]:
            out.append(f"Topik: {it['topik']}")
        if it["stimulus"]:
            out.append("")
            out.append("STIMULUS:")
            out.append(it["stimulus"])
        if it["pertanyaan"]:
            out.append("")
            out.append("PERTANYAAN:")
            out.append(it["pertanyaan"])
        if it["pernyataan"]:
            out.append("")
            out.append("PERNYATAAN:")
            out.extend(it["pernyataan"])
        if it["opsi"]:
            out.append("")
            out.append("OPSI JAWABAN:")
            out.extend(it["opsi"])
        out.append("")
        out.append(f"KUNCI RESMI: {it['kunci']}")
        if it["pembahasan"]:
            out.append("")
            out.append("PEMBAHASAN (Layer 3):")
            for label, txt in it["pembahasan"]:
                out.append(f"--- {label} ---")
                out.append(txt)
        else:
            out.append("PEMBAHASAN: belum tersedia untuk soal ini.")
        if it["warn"]:
            out.append(f"PERLU VERIFIKASI MANUAL: {it['warn']}")
    return "\n".join(out)


def render_audit_page(subject, paket, dari, sampai):
    esc = html_lib.escape
    items = _audit_collect(subject, paket, dari, sampai)
    sections = []
    for it in items:
        rows = [f"<h2 id=\"soal-{it['nomor']}\">SOAL {it['nomor']} — {esc(it['tipe'])}</h2>"]
        if it.get("missing"):
            sections.append(f"<section>{''.join(rows)}<p>(tidak ditemukan di data)</p></section>")
            continue
        if it["topik"]:
            rows.append(f"<p class=\"meta\">Topik: {esc(it['topik'])}</p>")
        if it["stimulus"]:
            rows.append(_audit_block('STIMULUS', esc(it["stimulus"])))
        if it["pertanyaan"]:
            rows.append(_audit_block('PERTANYAAN', esc(it["pertanyaan"])))
        if it["pernyataan"]:
            rows.append(_audit_block('PERNYATAAN', '<br>'.join(esc(p) for p in it["pernyataan"])))
        if it["opsi"]:
            rows.append(_audit_block('OPSI JAWABAN', '<br>'.join(esc(o) for o in it["opsi"])))
        rows.append(f"<p><strong>KUNCI RESMI:</strong> {esc(it['kunci'])}</p>")
        if it["pembahasan"]:
            rows.append("<h3>PEMBAHASAN (Layer 3)</h3>")
            for label, txt in it["pembahasan"]:
                rows.append(_audit_block(label, esc(txt)))
            if it["warn"]:
                rows.append(f"<p class=\"warn\">⚠ PERLU VERIFIKASI MANUAL: {esc(it['warn'])}</p>")
        else:
            rows.append("<p class=\"warn\">PEMBAHASAN: belum tersedia untuk soal ini.</p>")
        sections.append(f"<section>{''.join(rows)}</section>")

    title = f"Audit Konten — {esc(subject)} Paket {paket} (Nomor {dari}–{sampai})"
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="style.css?v=46">
<style>
  .audit-wrap {{ max-width: 860px; margin: 0 auto; padding: 32px 20px 72px; }}
  .audit-wrap h1 {{ font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }}
  .audit-note {{ font-size: 13px; color: var(--text-2); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 14px; background: var(--surface); margin: 16px 0 24px; }}
  .audit-wrap section {{ border: 1px solid var(--border); border-radius: 8px;
    padding: 18px 20px; margin-bottom: 22px; background: var(--bg-card); }}
  .audit-wrap h2 {{ font-size: 16px; font-weight: 600; color: var(--text); margin: 0 0 10px; }}
  .audit-wrap h3 {{ font-size: 13px; font-weight: 600; color: var(--text-3);
    text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 6px; }}
  .audit-wrap p, .audit-wrap .blk {{ font-size: 14.5px; line-height: 1.7; color: var(--text); }}
  .audit-wrap .blk {{ white-space: pre-wrap; }}
  .audit-wrap .meta {{ font-size: 12.5px; color: var(--text-3); }}
  .audit-wrap .warn {{ color: var(--warn); font-weight: 500; }}
</style>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script defer>
window.addEventListener('DOMContentLoaded', function () {{
  if (window.renderMathInElement) renderMathInElement(document.body, {{
    delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}],
    throwOnError: false
  }});
}});
</script>
</head>
<body>
<div class="audit-wrap">
<h1>{title}</h1>
<div class="audit-note">Halaman statis untuk reviewer otomatis — konten apa adanya dari data.
Teks di dalam <code>$...$</code> adalah LaTeX matematika. [GAMBAR] = gambar soal/opsi asli
yang hanya terlihat di aplikasi. Halaman interaktif: <code>/app</code>.</div>
{''.join(sections)}
</div>
</body>
</html>"""


def _audit_join_list(items):
    return ' | '.join(_audit_text(str(x)) for x in items) if items else '-'


def _track_client_context(handler):
    try:
        ip = handler.client_address[0] if hasattr(handler, 'client_address') and handler.client_address else '127.0.0.1'
        path = handler.path
        m = re.search(r'data/([a-z0-9_]+)_paket_(\d+)_learning\.json', path)
        if m:
            _client_active_context[ip] = {"subject": m.group(1), "paket": int(m.group(2))}
            return
        if 'subject=' in path:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(path).query)
            if 'subject' in qs:
                subj = qs['subject'][0]
                pkt = int(qs['paket'][0]) if 'paket' in qs else 1
                _client_active_context[ip] = {"subject": subj, "paket": pkt}
                return
    except Exception:
        pass


def _verify_supabase_token(token):
    """Verifikasi token user via Supabase Auth API (GET /auth/v1/user).
    Bekerja untuk semua alg (HS256/ES256/RS256) tanpa butuh JWT_SECRET.
    Mengembalikan (ok: bool, user: dict|None)."""
    try:
        if not token:
            return False, None
        sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
        sb_key = os.environ.get('SUPABASE_ANON_KEY', '')
        if not sb_url or not sb_key:
            return False, None
        req = urllib.request.Request(
            sb_url + '/auth/v1/user',
            headers={'apikey': sb_key, 'Authorization': 'Bearer ' + token})
        with urllib.request.urlopen(req, timeout=10) as resp:
            user = json.loads(resp.read().decode('utf-8') or '{}')
        if isinstance(user, dict) and user.get('id'):
            return True, user
        return False, None
    except Exception:
        return False, None


def clean_attempt_items(raw_items):
    """Normalisasi dan sanitasi items attempt secara toleran terhadap bentuk data nyata.
    Mendukung list, dict bertingkat (mis. {'1': {...}}), atau string JSON.
    Mengembalikan (ok: bool, error_message: str, clean_items: list[dict])."""
    if isinstance(raw_items, str):
        try:
            raw_items = json.loads(raw_items)
        except Exception:
            raw_items = None
    if isinstance(raw_items, dict):
        try:
            raw_items = [v for k, v in sorted(raw_items.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else str(kv[0]))]
        except Exception:
            raw_items = list(raw_items.values())

    if not isinstance(raw_items, list) or not (1 <= len(raw_items) <= 200):
        t_name = type(raw_items).__name__
        l_info = len(raw_items) if hasattr(raw_items, '__len__') else 'N/A'
        return False, f"Items tidak valid (harus 1-200 soal; tipe={t_name}, panjang={l_info}).", []

    clean_items = []
    for it in raw_items:
        if not isinstance(it, dict):
            continue
        active_ms = max(0, min(int(it.get("active_ms") or 0), 3600000))
        change_count = max(0, min(int(it.get("change_count") if it.get("change_count") is not None else it.get("ganti_jawaban") or 0), 100))
        flagged_ragu = bool(it.get("flagged_ragu") if it.get("flagged_ragu") is not None else it.get("ragu"))

        # Jejak kejadian (maksimal 5 event)
        raw_jejak = it.get("jejak") or []
        clean_jejak = []
        if isinstance(raw_jejak, list):
            for ev in raw_jejak[:5]:
                if isinstance(ev, dict):
                    clean_jejak.append({
                        "t_detik": max(0, min(int(ev.get("t_detik") or 0), 86400)),
                        "aksi": str(ev.get("aksi") or "")[:16],
                        "opsi": (str(ev.get("opsi") or "")[:32]) if ev.get("opsi") is not None else None,
                    })

        waktu_detik = int(it.get("waktu_detik") if it.get("waktu_detik") is not None else round(active_ms / 1000))

        clean_items.append({
            "soal_id": str(it.get("soal_id") or "")[:128],
            "position": int(it.get("position") or 0),
            "topic_id": (str(it.get("topic_id") or "")[:128] or None),
            "first_answer": (str(it.get("first_answer") or "")[:64] or None),
            "final_answer": (str(it.get("final_answer") or "")[:64] or None),
            "active_ms": active_ms,
            "first_answer_ms": it.get("first_answer_ms"),
            "change_count": change_count,
            "flagged_ragu": flagged_ragu,
            "visit_count": max(0, min(int(it.get("visit_count") or 0), 1000)),
            # Ekstensi A1 Guru Autopsi:
            "waktu_detik": waktu_detik,
            "ganti_jawaban": change_count,
            "ragu": flagged_ragu,
            "jejak": clean_jejak,
        })

    if not clean_items:
        return False, "Semua item di dalam items tidak valid.", []

    return True, "", clean_items


class AppRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Disable caching for html/js/css/json and root so frontend changes are always picked up immediately
        clean = self.path.split('?', 1)[0].split('#', 1)[0].lower()
        if clean.endswith(('.html', '.js', '.css', '.json')) or clean in ('', '/'):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

    def translate_path(self, path):
        # 1. First, check if the standard path directly resolves to an existing file on disk
        std_path = super().translate_path(path)
        if os.path.isfile(std_path):
            return std_path

        # 2. If file does not exist at requested location, handle image fallbacks
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        is_image_req = (
            clean_path.startswith('/images/')
            or clean_path.startswith('/tka/cbt_images/')
            or '/cbt_images/' in clean_path
            or clean_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'))
        )
        if is_image_req:
            filename = os.path.basename(clean_path)
            if not filename:
                return std_path

            data_root = os.path.join(BASE_DIR, "data")

            # Check active subject and package from Cookie, Referer, or Client Context
            req_subject = None
            req_paket = None

            cookie_hdr = self.headers.get('Cookie', '') if hasattr(self, 'headers') and self.headers else ''
            if cookie_hdr:
                for c in cookie_hdr.split(';'):
                    c = c.strip()
                    if c.startswith('active_subject='):
                        req_subject = c.split('=', 1)[1].strip()
                    elif c.startswith('active_paket='):
                        try:
                            req_paket = int(c.split('=', 1)[1].strip())
                        except ValueError:
                            pass

            referer = self.headers.get('Referer', '') if hasattr(self, 'headers') and self.headers else ''
            if referer:
                try:
                    parsed_ref = urllib.parse.urlparse(referer)
                    q_params = urllib.parse.parse_qs(parsed_ref.query)
                    if 'subject' in q_params and not req_subject:
                        req_subject = q_params['subject'][0]
                    if 'paket' in q_params and not req_paket:
                        try:
                            req_paket = int(q_params['paket'][0])
                        except ValueError:
                            pass
                except Exception:
                    pass

            client_ip = self.client_address[0] if hasattr(self, 'client_address') and self.client_address else '127.0.0.1'
            if not req_subject and client_ip in _client_active_context:
                cached = _client_active_context[client_ip]
                req_subject = cached.get('subject')
                if not req_paket:
                    req_paket = cached.get('paket')

            # Priority 1: Check active subject and package
            if req_subject:
                if req_paket:
                    cand = os.path.join(data_root, req_subject, f"paket_{req_paket}", "images", filename)
                    if os.path.isfile(cand):
                        return cand
                for p in ["paket_1", "paket_2"]:
                    cand = os.path.join(data_root, req_subject, p, "images", filename)
                    if os.path.isfile(cand):
                        return cand
                cand = os.path.join(data_root, req_subject, "images", filename)
                if os.path.isfile(cand):
                    return cand

            # Priority 2: Check if clean_path contains subject name hint
            for entry in os.scandir(data_root):
                if entry.is_dir() and entry.name in clean_path:
                    for sub in os.scandir(entry.path):
                        if sub.is_dir() and sub.name in clean_path:
                            cand = os.path.join(sub.path, "images", filename)
                            if os.path.isfile(cand):
                                return cand
                    cand = os.path.join(entry.path, "images", filename)
                    if os.path.isfile(cand):
                        return cand

            # Priority 3: For generic question filenames (soal_XX_..., opt_...),
            # NEVER fallback to an arbitrary subject directory! That causes cross-subject pollution.
            is_generic_soal = filename.startswith(("soal_", "opt_"))
            if not is_generic_soal:
                # Globally unique hashes (e.g. 17088_... or \d+_[a-f0-9]{32}) are safe to search anywhere
                for entry in os.scandir(data_root):
                    if entry.is_dir():
                        for sub in os.scandir(entry.path):
                            if sub.is_dir() and sub.name.startswith("paket_"):
                                img_dir = os.path.join(sub.path, "images")
                                cand = os.path.join(img_dir, filename)
                                if os.path.isfile(cand):
                                    return cand
                        cand = os.path.join(entry.path, "images", filename)
                        if os.path.isfile(cand):
                            return cand

                # Fallback terakhir: indeks nama file (dibangun sekali saat start).
                hits = _DATA_FILE_INDEX.get(filename)
                if hits:
                    return hits[0]

        return std_path

    # ---- Sesi pengguna anonim utk percakapan tutor (cookie HMAC, HttpOnly) ---
    def _tutor_session(self):
        """Ambil (user_key, cookie_baru). Tidak ada auth di aplikasi ini;
        kunci anonim per-browser memberi kontinuitas lokal, bukan memori
        lintas perangkat (dilaporkan jujur di dokumentasi)."""
        val = None
        for part in (self.headers.get('Cookie') or '').split(';'):
            p = part.strip()
            if p.startswith('tutor_uid='):
                val = p.split('=', 1)[1].strip()
                break
        user_key = tutor_store.validate_user_cookie_value(val) if val else None
        if user_key:
            return user_key, None
        cookie_val = tutor_store.make_user_cookie_value()
        return cookie_val.split('.', 1)[0], cookie_val

    def _is_logged_in_request(self, payload=None):
        """Deteksi apakah request berasal dari pengguna yang login Google/akun."""
        # 1. Cek headers (X-User-Logged-In, X-User-Email, X-TKA-User)
        hdr_login = (self.headers.get('X-User-Logged-In') or '').strip().lower()
        if hdr_login in ('true', '1'):
            return True
        if (self.headers.get('X-User-Email') or '').strip():
            return True
        # 2. Cek query parameter bila ada
        try:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get('is_logged_in', [''])[0].lower() in ('true', '1') or q.get('user_email', [''])[0].strip():
                return True
        except Exception:
            pass
        # 3. Cek payload JSON bila ada
        if payload and isinstance(payload, dict):
            if payload.get('is_logged_in') is True or (payload.get('user_email') or '').strip():
                return True
        return False

    def _extract_device_info(self, payload=None):
        """Ambil pengenal perangkat (device_id, fingerprint, client_ip) untuk guest anti-abuse."""
        dev_id = (self.headers.get('X-Device-Id') or '').strip()
        dev_fp = (self.headers.get('X-Device-Fingerprint') or '').strip()

        try:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if not dev_id:
                dev_id = (q.get('device_id', [''])[0]).strip()
            if not dev_fp:
                dev_fp = (q.get('device_fp', [''])[0] or q.get('fingerprint', [''])[0]).strip()
        except Exception:
            pass

        if payload and isinstance(payload, dict):
            if not dev_id:
                dev_id = str(payload.get('device_id') or '').strip()
            if not dev_fp:
                dev_fp = str(payload.get('device_fp') or payload.get('fingerprint') or '').strip()

        fwd = (self.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
        client_ip = fwd or (self.client_address[0] if hasattr(self, 'client_address') and self.client_address else '')
        return dev_id or None, dev_fp or None, client_ip or None

    def _cors_allow_origin(self):
        """Nilai header Access-Control-Allow-Origin.

        Hanya mengembalikan Origin bila request benar-benar same-origin
        (host Origin == host request). Respons ber-cookie TIDAK memakai '*'
        agar situs lain tidak bisa membaca respons API lewat browser.
        """
        origin = (self.headers.get('Origin') or '').strip()
        if not origin:
            return None
        host = (self.headers.get('Host') or '').split(':')[0].strip().lower()
        try:
            o_host = (urllib.parse.urlparse(origin).hostname or '').lower()
        except Exception:
            return None
        if o_host and host and o_host == host:
            return origin
        return None

    def _send_json(self, status, obj, cookie_value=None):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        # Fase 2, Fix 6: gzip utk application/json bila klien mendukung
        # (penting utk HP berkuota terbatas).
        accept = (self.headers.get('Accept-Encoding') or '').lower()
        use_gzip = 'gzip' in accept
        if use_gzip:
            body = gzip.compress(body)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        allow_origin = self._cors_allow_origin()
        if allow_origin:
            self.send_header('Access-Control-Allow-Origin', allow_origin)
            self.send_header('Vary', 'Origin, Accept-Encoding')
        elif use_gzip:
            self.send_header('Vary', 'Accept-Encoding')
        if use_gzip:
            self.send_header('Content-Encoding', 'gzip')
        if cookie_value:
            self.send_header('Set-Cookie',
                             f'tutor_uid={cookie_value}; Path=/; HttpOnly; '
                             f'SameSite=Lax; Max-Age=31536000')
        _vck = getattr(self, '_visitor_cookie', None)
        if _vck:
            self.send_header('Set-Cookie', _vck)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_500(self, exc, context="", cookie_value=None):
        """Error 500: pesan generik ke klien, traceback lengkap ke log file."""
        _log_server_error(exc, context or self.path)
        return self._send_json(500, {
            "status": "error",
            "message": "Terjadi kesalahan pada server. Coba lagi beberapa saat.",
        }, cookie_value=cookie_value)

    def _send_body(self, status, content_type, body, extra_headers=None):
        """Kirim respons biner mentah (Fase 3: dedup pola send_response+headers+write
        yang sebelumnya terduplikasi ~6x di do_GET). Header ekstra opsional."""
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        _vck = getattr(self, '_visitor_cookie', None)
        if _vck:
            self.send_header('Set-Cookie', _vck)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static_serve_allowed(self):
        """Allowlist static serving (Fase 2, Fix 4).

        Seluruh folder proyek TIDAK tersaji statis lagi (dulu dokumen .md
        internal ikut terbuka). Hanya file frontend di lokasi wajar:
        root proyek, workspace_akun/modul/progres, prefix gambar, dan
        data/<mapel>/paket_N/images/ (dipakai frontend utk gambar soal).
        """
        clean = urllib.parse.unquote(self.path).split('?', 1)[0].split('#', 1)[0]
        lower = clean.lower()
        parts = [p for p in lower.split('/') if p]
        if not parts:
            return True  # '/' ditangani page_routes sebelum mencapai sini
        if not any(lower.endswith(ext) for ext in _STATIC_EXTS):
            return False
        top = parts[0]
        if top == 'data':
            # /data/... hanya utk:
            # 1. file gambar di dalam folder images/
            # 2. file soal *_learning.json di root data/ (dibutuhkan frontend quiz)
            if 'images' in parts and lower.endswith(_IMAGE_EXTS):
                return True
            if len(parts) == 2 and lower.endswith('_learning.json'):
                return True
            return False
        if top in _STATIC_OK_TOPDIRS:
            return True
        # Root proyek: hanya file langsung (tanpa subdirektori).
        return len(parts) == 1

    def _extract_admin_key(self, payload=None):
        """Ambil kunci admin dari header X-Admin-Key, Authorization, atau POST body.
        Query param 'key' tetap didukung sebagai fallback kompatibilitas."""
        key = (self.headers.get('X-Admin-Key') or '').strip()
        if key:
            return key
        auth = (self.headers.get('Authorization') or '').strip()
        if auth.startswith('Admin '):
            return auth[6:].strip()
        elif auth.startswith('Bearer '):
            bearer = auth[7:].strip()
            import visitor_log as _vl
            if _vl.ADMIN_KEY and bearer == _vl.ADMIN_KEY:
                return bearer
        if isinstance(payload, dict) and payload.get('key'):
            return str(payload['key']).strip()
        try:
            return urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('key', [''])[0].strip()
        except Exception:
            return ''

    def _is_valid_admin(self, payload=None):
        key = self._extract_admin_key(payload)
        import visitor_log as _vl
        return bool(key and _vl.ADMIN_KEY and key == _vl.ADMIN_KEY)

    def log_message(self, format, *args):
        # Redact query string yang mengandung key agar tidak bocor ke log/console
        clean_args = []
        for a in args:
            if isinstance(a, str) and 'key=' in a:
                a = re.sub(r'([?&]key=)[^&\s]+', r'\1[REDACTED]', a)
            clean_args.append(a)
        super().log_message(format, *clean_args)

    def _handle_admin_autopsi_page(self):
        try:
            html = '''<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Demo Autopsi (Admin)</title>
<style>body{font-family:system-ui;max-width:720px;margin:0 auto;padding:20px}
.card{border:1px solid #ddd;border-radius:12px;padding:16px;margin:12px 0}
.locked{filter:blur(6px);user-select:none;pointer-events:none}
button{background:#004a2a;color:#fff;border:0;border-radius:8px;padding:10px 16px;cursor:pointer}
input{padding:10px;border:1px solid #ddd;border-radius:8px;width:100%;box-sizing:border-box}
pre{background:#f5f5f5;padding:12px;border-radius:8px;overflow:auto;font-size:13px}</style>
</head><body>
<h1>Demo Autopsi (Admin)</h1>
<p>Tempel <b>attempt_id</b> dari tabel Supabase <code>attempts</code>, lalu klik Lihat.</p>
<input id="aid" placeholder="attempt_id (uuid)">
<p><button onclick="lihat()">Lihat Autopsi Penuh</button>
<button onclick="salinWA()">Salin Teks untuk WA</button></p>
<div id="out"></div>
<script>
let KEY = new URLSearchParams(location.search).get('key') || sessionStorage.getItem('tka_admin_key') || '';
if (KEY) {
  sessionStorage.setItem('tka_admin_key', KEY);
  if (location.search.includes('key=')) {
    try {
      const u = new URL(location.href);
      u.searchParams.delete('key');
      history.replaceState(null, '', u.pathname + (u.search ? u.search : ''));
    } catch(e) {}
  }
}
async function lihat() {
  const aid = document.getElementById('aid').value.trim();
  if (!aid) return alert('Isi attempt_id dulu');
  if (!KEY) {
    KEY = prompt('Masukkan Kunci Admin:') || '';
    if (KEY) sessionStorage.setItem('tka_admin_key', KEY);
    else return;
  }
  document.getElementById('out').innerHTML = 'Memuat...';
  // Kirim via header X-Admin-Key ke /api/admin/autopsy_full
  const r = await fetch('/api/admin/autopsy_full?attempt_id=' + encodeURIComponent(aid), {
    headers: { 'X-Admin-Key': KEY }
  });
  const j = await r.json();
  if (j.status !== 'success') { document.getElementById('out').innerHTML = 'Gagal: ' + (j.message||r.status); return; }
  window._lastAutopsy = j;
  const k = j.kebocoran || [];
  let h = '<div class="card"><h3>Skor: ' + j.skor_pct + '% (' + j.n_correct + '/' + j.n_answered + ')</h3>';
  h += '<p>Data tipis: ' + (j.data_tipis?'ya':'tidak') + '</p></div>';
  k.forEach((x,i) => {
    h += '<div class="card"><h3>Kebocoran #' + (i+1) + ': ' + x.label + '</h3>';
    h += '<p><b>Bukti:</b> ' + x.bukti + '</p>';
    h += '<p><b>Contoh soal:</b> ' + (x.contoh||[]).join(', ') + '</p></div>';
  });
  document.getElementById('out').innerHTML = h;
}
function salinWA() {
  const j = window._lastAutopsy; if (!j) return alert('Lihat dulu autopsi-nya');
  const k = j.kebocoran || [];
  let t = 'Hasil Autopsi Tryout\\nSkor: ' + j.skor_pct + '%\\n';
  k.forEach((x,i) => { t += (i+1) + '. ' + x.label + ': ' + x.bukti + '\\n'; });
  navigator.clipboard.writeText(t).then(()=>alert('Tersalin!'));
}
</script></body></html>'''
            return self._send_body(200, 'text/html; charset=utf-8', html.encode('utf-8'), {'Cache-Control': 'no-cache'})
        except Exception as e:
            return self._send_500(e, "/admin/autopsi")

    def _handle_admin_autopsy_full(self, payload=None):
        try:
            if PUBLIC_DEMO:
                return self._send_json(403, {"status": "forbidden", "message": "Dimatikan saat demo publik."})
            if not self._is_valid_admin(payload):
                return self._send_json(401, {"status": "unauthorized", "message": "Kunci admin salah atau tidak diberikan."})
            if autopsy_analyzer is None:
                return self._send_json(503, {"status": "error", "message": "Analyzer belum tersedia."})
            
            attempt_id = ''
            if isinstance(payload, dict):
                attempt_id = str(payload.get('attempt_id') or '').strip()
            if not attempt_id:
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                attempt_id = (q.get('attempt_id', [''])[0] or '').strip()
            
            if not attempt_id:
                return self._send_json(400, {"status": "error", "message": "attempt_id wajib."})
            
            sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
            sb_svc = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')
            req = urllib.request.Request(
                sb_url + "/rest/v1/attempts?id=eq." + urllib.parse.quote(attempt_id) + "&select=*",
                headers={"apikey": sb_svc, "Authorization": "Bearer " + sb_svc})
            with urllib.request.urlopen(req, timeout=15) as resp:
                rows = json.loads(resp.read().decode("utf-8") or "[]")
            if not rows:
                return self._send_json(404, {"status": "error", "message": "Attempt tidak ditemukan."})
            att = rows[0]
            items = att.get('items') or []
            attempt_data = {
                'n_questions': int(att.get('n_questions') or len(items)),
                'duration_limit_s': int(att.get('duration_limit_s') or 4500),
                'ended_by': att.get('ended_by') or 'user',
                'kunci': {},
                'items': items,
            }
            result = autopsy_analyzer.analyze(attempt_data)
            n_corr = sum(1 for it in items if it.get('is_correct'))
            return self._send_json(200, {
                "status": "success",
                "skor_pct": round(100 * n_corr / max(1, len([i for i in items if i.get('final_answer')]))),
                "n_correct": n_corr,
                "n_answered": len([i for i in items if i.get('final_answer')]),
                "data_tipis": result.get('data_tipis'),
                "kebocoran": result.get('kebocoran'),
                "rapuh_ids": result.get('rapuh_ids'),
            })
        except Exception as e:
            return self._send_500(e, "/api/admin/autopsy_full")

    def _handle_get_autopsy_coach(self):
        """GET /api/autopsy/coach?attempt_id=... — Mengambil hasil Guru Autopsi ter-cache."""
        try:
            if autopsy_coach is None:
                return self._send_json(503, {"status": "error", "message": "Layanan coach belum tersedia."})
            _auth = self.headers.get('Authorization', '') or ''
            _token = _auth[7:].strip() if _auth.startswith('Bearer ') else ''
            if not _token:
                return self._send_json(401, {"status": "unauthorized", "message": "Login diperlukan."})
            _vok, _user = _verify_supabase_token(_token)
            if not _vok or not (_user or {}).get('id'):
                return self._send_json(401, {"status": "unauthorized", "message": "Token tidak valid atau sesi berakhir."})
            user_id = str(_user['id'])

            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            attempt_id = (q.get('attempt_id', [''])[0] or '').strip()
            if not attempt_id:
                return self._send_json(400, {"status": "error", "message": "attempt_id diperlukan."})

            # Cek memory cache
            cached = _COACH_CACHE.get(attempt_id)
            if cached:
                cached_owner = cached.get("_user_id")
                if cached_owner and cached_owner != user_id and not self._is_valid_admin():
                    return self._send_json(403, {"status": "forbidden", "message": "Anda bukan pemilik attempt ini."})
                res = {k: v for k, v in cached.items() if not k.startswith("_")}
                return self._send_json(200, {"status": "success", "attempt_id": attempt_id, "coach": res, "cached": True})

            # Ambil dari Supabase
            sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
            sb_svc = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')
            if not sb_url or not sb_svc:
                return self._send_json(404, {"status": "error", "message": "Hasil coach belum tersedia."})

            req = urllib.request.Request(
                sb_url + "/rest/v1/attempts?id=eq." + urllib.parse.quote(attempt_id) + "&select=*",
                headers={"apikey": sb_svc, "Authorization": "Bearer " + sb_svc})
            with urllib.request.urlopen(req, timeout=10) as resp:
                rows = json.loads(resp.read().decode("utf-8") or "[]")
            if not rows:
                return self._send_json(404, {"status": "error", "message": "Attempt tidak ditemukan."})

            att = rows[0]
            if str(att.get('user_id')) != user_id and not self._is_valid_admin():
                return self._send_json(403, {"status": "forbidden", "message": "Anda bukan pemilik attempt ini."})

            coach_res = att.get('coach_result')
            if not coach_res:
                return self._send_json(404, {"status": "error", "message": "Hasil coach belum dihitung untuk attempt ini."})

            _COACH_CACHE[attempt_id] = {**coach_res, "_user_id": user_id}
            return self._send_json(200, {"status": "success", "attempt_id": attempt_id, "coach": coach_res, "cached": True})
        except Exception as e:
            return self._send_500(e, "GET /api/autopsy/coach")

    def _handle_post_autopsy_coach(self):
        """POST /api/autopsy/coach — Menjalankan atau mengambil analisis Guru Autopsi."""
        try:
            if autopsy_coach is None or autopsy_evidence is None:
                return self._send_json(503, {"status": "error", "message": "Layanan Guru Autopsi belum tersedia."})
            _auth = self.headers.get('Authorization', '') or ''
            _token = _auth[7:].strip() if _auth.startswith('Bearer ') else ''
            if not _token:
                return self._send_json(401, {
                    "status": "unauthorized",
                    "is_guest": True,
                    "message": "Login Google untuk mendapatkan analisis Guru Autopsi gratis."
                })
            _vok, _user = _verify_supabase_token(_token)
            if not _vok or not (_user or {}).get('id'):
                return self._send_json(401, {"status": "unauthorized", "message": "Token tidak valid atau sesi berakhir."})
            user_id = str(_user['id'])

            # Rate limit check (maks 10 request per menit per user)
            now = time.time()
            user_history = _COACH_RATE_LIMIT.setdefault(user_id, [])
            user_history[:] = [t for t in user_history if now - t < 60]
            if len(user_history) >= 10:
                return self._send_json(429, {"status": "error", "message": "Terlalu banyak permintaan Guru Autopsi. Silakan tunggu 1 menit."})
            user_history.append(now)

            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            payload = json.loads(post_data) if post_data else {}

            attempt_id = str(payload.get('attempt_id') or '').strip()
            attempt_data = payload.get('attempt')

            sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
            sb_svc = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')

            # Jika ada attempt_id, periksa cache dan database
            if attempt_id:
                # 1. Cek memory cache
                cached = _COACH_CACHE.get(attempt_id)
                if cached:
                    cached_owner = cached.get("_user_id")
                    if cached_owner and cached_owner != user_id and not self._is_valid_admin():
                        return self._send_json(403, {"status": "forbidden", "message": "Anda bukan pemilik attempt ini."})
                    res = {k: v for k, v in cached.items() if not k.startswith("_")}
                    return self._send_json(200, {"status": "success", "attempt_id": attempt_id, "coach": res, "cached": True})

                # 2. Ambil attempt dari Supabase
                if sb_url and sb_svc:
                    req = urllib.request.Request(
                        sb_url + "/rest/v1/attempts?id=eq." + urllib.parse.quote(attempt_id) + "&select=*",
                        headers={"apikey": sb_svc, "Authorization": "Bearer " + sb_svc})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        rows = json.loads(resp.read().decode("utf-8") or "[]")
                    if not rows:
                        return self._send_json(404, {"status": "error", "message": "Attempt tidak ditemukan."})
                    att = rows[0]
                    # Ownership check (keamanan Bagian 9)
                    if str(att.get('user_id')) != user_id and not self._is_valid_admin():
                        return self._send_json(403, {"status": "forbidden", "message": "Anda bukan pemilik attempt ini."})
                    if att.get('coach_result'):
                        _COACH_CACHE[attempt_id] = {**att['coach_result'], "_user_id": user_id}
                        return self._send_json(200, {"status": "success", "attempt_id": attempt_id, "coach": att['coach_result'], "cached": True})
                    attempt_data = att

            if not attempt_data:
                return self._send_json(400, {"status": "error", "message": "attempt_id atau payload attempt wajib diisi."})

            # Bangun evidence pack (fungsi murni)
            evidence = autopsy_evidence.build_evidence(attempt_data)

            # Pengecekan kuota & anggaran berbasis database (Bagian 7 A5)
            q_ok = True
            q_reason = ""
            q_usage = {}
            if autopsy_quota:
                q_ok, q_reason, q_usage = autopsy_quota.check_quota(user_id, sb_url, sb_svc)

            if not q_ok:
                # Kuota habis atau dinonaktifkan -> fallback instan ke template (tanpa error mentah)
                coach_out = autopsy_coach.coach_template.generate_template(evidence)
                coach_out["sumber"] = "template"
                meta = {
                    "latensi_ms": 0,
                    "sumber": "template",
                    "alasan": q_reason,
                    "model": "template",
                    "kuota": q_usage,
                }
            else:
                # Panggil layanan Guru AI (dengan fallback template otomatis jika LLM/validasi gagal)
                coach_out, meta = autopsy_coach.generate_coach(evidence)
                if q_usage:
                    meta["kuota"] = q_usage

            # Simpan cache
            if attempt_id:
                _COACH_CACHE[attempt_id] = {**coach_out, "_user_id": user_id}
                if sb_url and sb_svc:
                    try:
                        patch_req = urllib.request.Request(
                            sb_url + "/rest/v1/attempts?id=eq." + urllib.parse.quote(attempt_id),
                            data=json.dumps({"coach_result": coach_out}).encode("utf-8"),
                            method="PATCH",
                            headers={"apikey": sb_svc, "Authorization": "Bearer " + sb_svc, "Content-Type": "application/json"})
                        urllib.request.urlopen(patch_req, timeout=5)
                    except Exception:
                        pass

            return self._send_json(200, {
                "status": "success",
                "attempt_id": attempt_id or None,
                "coach": coach_out,
                "meta": meta,
            })
        except Exception as e:
            return self._send_500(e, "POST /api/autopsy/coach")

    def _handle_get_autopsy_quota(self):
        """GET /api/autopsy/quota — Memeriksa status dan sisa kuota Guru Autopsi."""
        try:
            if autopsy_quota is None:
                return self._send_json(503, {"status": "error", "message": "Layanan kuota belum tersedia."})
            _auth = self.headers.get('Authorization', '') or ''
            _token = _auth[7:].strip() if _auth.startswith('Bearer ') else ''
            if not _token:
                return self._send_json(200, {
                    "status": "guest",
                    "is_guest": True,
                    "message": "Login Google untuk mendapatkan Guru AI gratis.",
                    "limits": autopsy_quota.get_quota_limits(),
                })
            _vok, _user = _verify_supabase_token(_token)
            if not _vok or not (_user or {}).get('id'):
                return self._send_json(401, {"status": "unauthorized", "message": "Token tidak valid atau sesi berakhir."})
            user_id = str(_user['id'])
            sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
            sb_svc = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')
            allowed, reason, usage = autopsy_quota.check_quota(user_id, sb_url, sb_svc)
            return self._send_json(200, {
                "status": "success",
                "user_id": user_id,
                "allowed": allowed,
                "reason": reason,
                "usage": usage,
                "limits": autopsy_quota.get_quota_limits(),
            })
        except Exception as e:
            return self._send_500(e, "GET /api/autopsy/quota")

    def do_HEAD(self):
        # Samakan proteksi static serving utk HEAD (SimpleHTTPRequestHandler
        # punya do_HEAD bawaan yang akan lolos tanpa cek ini).
        if not self._static_serve_allowed():
            return self._send_json(403, {"status": "forbidden",
                                         "message": "Akses statis ke file ini tidak diizinkan."})
        return super().do_HEAD()

    def do_GET(self):
        _track_client_context(self)
        _did, _need_ck = visitor_log.record(self)
        self._visitor_did = _did
        self._visitor_cookie = visitor_log.cookie_header_value(_did) if (_did and _need_ck) else None
        # 1. Proteksi Path Traversal & File Sensitif
        clean_path = urllib.parse.unquote(self.path).split('?', 1)[0].split('#', 1)[0]
        parts = [p for p in clean_path.split('/') if p]

        # Tolak file dan direktori tersembunyi (dimulai dengan titik, mis. .env, .git)
        if any(p.startswith('.') for p in parts):
            return self._send_json(403, {"status": "forbidden", "message": "Akses ditolak: file tersembunyi dilindungi."})

        # Tolak ekstensi file sensitif / internal source code / database
        lower_path = clean_path.lower()
        forbidden_exts = ('.py', '.pyc', '.db', '.sqlite', '.sqlite3', '.bat', '.sh', '.cmd', '.log', '.zip', '.bak', '.env')
        if lower_path.endswith(forbidden_exts) or 'secret' in lower_path:
            return self._send_json(403, {"status": "forbidden", "message": "Akses ditolak: tipe file dilindungi."})

        # 1b. Mode demo publik: matikan endpoint administratif & pemakai kuota LLM.
        # (do_POST punya cek serupa; di sini perlu versi GET untuk /api/tutor/state,
        #  dan path dilucuti query string agar "?subject=..." tidak lolos.)
        if PUBLIC_DEMO and self.path.split('?', 1)[0] in DEMO_BLOCKED_PATHS:
            return self._send_json(403, {"status": "forbidden",
                                         "message": "Endpoint ini dimatikan saat mode demo publik."})

        if self.path.split('?', 1)[0] == '/api/tutor/state':
            # Muat ulang percakapan tersimpan soal ini (resume tanpa isi kosong)
            user_key, new_cookie = self._tutor_session()
            is_login = self._is_logged_in_request()
            dev_id, dev_fp, client_ip = self._extract_device_info()
            current_q = tutor_store.get_user_quota(user_key, device_id=dev_id, fingerprint=dev_fp, ip_address=client_ip)
            if current_q.get("tier") != "subscriber":
                target_tier = "free" if is_login else "guest"
                if current_q.get("tier") != target_tier:
                    tutor_store.set_user_tier(user_key, tier=target_tier)
            try:
                params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                subject = params.get('subject', ['matematika'])[0]
                paket = int(params.get('paket', ['1'])[0])
                nomor = int(params.get('nomor', ['1'])[0])
                ctx = resolve_tutor_context(subject, paket, nomor)
                if not ctx:
                    return self._send_json(404, {"status": "error",
                                                 "message": "Soal tidak ditemukan."},
                                           cookie_value=new_cookie)
                conv = tutor_store.get_or_create_conversation(
                    user_key, ctx["canonical_id"], subject, paket, nomor, create=False)
                messages = tutor_store.get_messages(conv["id"]) if conv else []
                user_quota = tutor_store.get_user_quota(user_key, device_id=dev_id, fingerprint=dev_fp, ip_address=client_ip)
                user_quota["is_logged_in"] = is_login or (user_quota.get("tier") == "subscriber")
                return self._send_json(200, {
                    "status": "success",
                    "canonical_id": ctx["canonical_id"],
                    "provider": tutor_llm.active_provider_info(),
                    "quota": user_quota,
                    "conversation_id": conv["id"] if conv else None,
                    "summary": conv.get("summary") if conv else None,
                    "messages": [{"id": m["id"], "role": m["role"],
                                  "content": m["content"],
                                  "model": m.get("model")} for m in messages],
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_500(e, "/api/tutor/state", cookie_value=new_cookie)

        # FASE 0 T0.7: feature flags. Klien membaca lewat SATU endpoint ini;
        # nilai sudah dihitung di server (sumber kebenaran = tabel feature_flags).
        if self.path.split('?', 1)[0] == '/api/flags':
            try:
                return self._send_json(200, {
                    "status": "success",
                    "version": feature_flags.FLAGS_VERSION,
                    "flags": feature_flags.get_all_flags(),
                })
            except Exception as e:
                return self._send_500(e, "/api/flags")

        if self.path.split('?', 1)[0] == '/api/swarm/status':
            try:
                from pipeline.swarm_manager import swarm_engine
                return self._send_json(200, swarm_engine.get_status())
            except Exception as e:
                return self._send_500(e, "/api/swarm/status")

        if self.path.split('?', 1)[0] == '/api/swarm/subjects':
            try:
                from pipeline.subject_catalog import get_full_catalog
                return self._send_json(200, get_full_catalog())
            except Exception as e:
                return self._send_500(e, "/api/swarm/subjects")

        # BUG-001 (Tugas D): Ambil progress belajar user dari Supabase
        if self.path.split('?', 1)[0] == '/api/user/progress':
            try:
                _auth = self.headers.get('Authorization', '') or ''
                _token = _auth[7:] if _auth.startswith('Bearer ') else ''
                if not _token:
                    return self._send_json(401, {"status": "unauthorized"})
                _vok, _user = _verify_supabase_token(_token)
                if not _vok:
                    return self._send_json(401, {"status": "unauthorized"})
                user_id = _user['id']
                sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
                sb_key = os.environ.get('SUPABASE_ANON_KEY', '')
                req = urllib.request.Request(
                    sb_url + "/rest/v1/users?id=eq." + user_id + "&select=progress,tka_date",
                    headers={"apikey": sb_key, "Authorization": "Bearer " + _token})
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        rows = json.loads(resp.read().decode('utf-8') or '[]')
                    row = rows[0] if rows else {}
                    return self._send_json(200, {
                        "status": "success",
                        "progress": row.get("progress") or {},
                        "tka_date": row.get("tka_date")
                    })
                except urllib.error.HTTPError as he:
                    # T4b: Fallback bila kolom tka_date belum dibuat di Supabase (HTTP 400)
                    if he.code == 400:
                        req_fallback = urllib.request.Request(
                            sb_url + "/rest/v1/users?id=eq." + user_id + "&select=progress",
                            headers={"apikey": sb_key, "Authorization": "Bearer " + _token})
                        with urllib.request.urlopen(req_fallback, timeout=10) as resp_fb:
                            rows_fb = json.loads(resp_fb.read().decode('utf-8') or '[]')
                        row_fb = rows_fb[0] if rows_fb else {}
                        return self._send_json(200, {
                            "status": "success",
                            "progress": row_fb.get("progress") or {},
                            "tka_date": None
                        })
                    raise he
            except Exception as e:
                return self._send_500(e, "/api/user/progress")

        # Dashboard pengunjung (khusus server utama / bukan demo publik)
        if self.path.split('?', 1)[0] in ADMIN_VISITOR_PATHS:
            if PUBLIC_DEMO:
                return self._send_json(403, {"status": "forbidden", "message": "Dimatikan saat demo publik."})
            if not self._is_valid_admin():
                return self._send_json(401, {"status": "unauthorized", "message": "Kunci admin salah atau tidak diberikan."})
            if self.path.split('?', 1)[0] == '/api/admin/visitors':
                body = json.dumps(visitor_log.summary(), ensure_ascii=False).encode('utf-8')
                self._send_body(200, 'application/json; charset=utf-8', body,
                                {'Cache-Control': 'no-store'})
                return
            with open(os.path.join(BASE_DIR, 'pengunjung.html'), 'rb') as fh:
                page_body = fh.read()
            self._send_body(200, 'text/html; charset=utf-8', page_body,
                            {'Cache-Control': 'no-store'})
            return

        # FASE 5 (T5.4): Halaman admin autopsi (GET)
        if self.path.split('?', 1)[0] == '/admin/autopsi':
            if PUBLIC_DEMO:
                return self._send_json(403, {"status": "forbidden", "message": "Dimatikan saat demo publik."})
            if not self._is_valid_admin():
                return self._send_json(401, {"status": "unauthorized", "message": "Kunci admin salah atau tidak diberikan."})
            return self._handle_admin_autopsi_page()

        # FASE 5 (T5.4): API Autopsi Full (GET)
        if self.path.split('?', 1)[0] == '/api/admin/autopsy_full':
            return self._handle_admin_autopsy_full(payload=None)

        # FASE A3: API Guru Autopsi Cached (GET)
        if self.path.split('?', 1)[0] == '/api/autopsy/coach':
            return self._handle_get_autopsy_coach()

        # FASE A5: API Kuota Guru Autopsi (GET)
        if self.path.split('?', 1)[0] == '/api/autopsy/quota':
            return self._handle_get_autopsy_quota()

        # Snapshot konten server-rendered untuk reviewer otomatis (Fase bagikan online):
        # /audit?subject=matematika&paket=1&dari=1&sampai=10  (HTML)
        # /audit.txt?...                                      (teks polos)
        _audit_path = self.path.split('?', 1)[0]
        if _audit_path in ('/audit', '/audit.txt'):
            try:
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                a_subject = qs.get('subject', ['matematika'])[0]
                a_paket = int(qs.get('paket', ['1'])[0])
                a_dari = max(1, int(qs.get('dari', ['1'])[0]))
                a_sampai = min(int(qs.get('sampai', ['10'])[0]), a_dari + 24)
                if _audit_path == '/audit.txt':
                    audit_body = render_audit_text(a_subject, a_paket, a_dari, a_sampai).encode('utf-8')
                    audit_ctype = 'text/plain; charset=utf-8'
                else:
                    audit_body = render_audit_page(a_subject, a_paket, a_dari, a_sampai).encode('utf-8')
                    audit_ctype = 'text/html; charset=utf-8'
                self._send_body(200, audit_ctype, audit_body)
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as e:
                return self._send_500(e, "/audit")
            return

        # Fase 3: halaman statis (landing, legal) & alias /app untuk aplikasi.
        # "/" -> landing.html (fallback index.html bila file tidak ada).
        route_path = urllib.parse.urlparse(self.path).path or '/'
        if len(route_path) > 1 and route_path.endswith('/'):
            route_path = route_path.rstrip('/')
        page_routes = {
            '/': 'landing.html',
            '/app': 'index.html',
            '/privacy': 'privacy.html',
            '/terms': 'terms.html',
        }
        target_page = page_routes.get(route_path)
        if target_page:
            page_file = os.path.join(BASE_DIR, target_page)
            if os.path.isfile(page_file):
                try:
                    with open(page_file, 'rb') as fh:
                        page_body = fh.read()
                    self._send_body(200, 'text/html; charset=utf-8', page_body,
                                    {'Cache-Control': 'no-cache'})
                    return
                except (BrokenPipeError, ConnectionResetError):
                    return
                except Exception as e:
                    return self._send_500(e, f"/page:{target_page}")
            # File halaman tidak ada -> lanjut ke super() (fallback lama).

        # Fase 2, Fix 4: batasi static serving ke allowlist frontend.
        if not self._static_serve_allowed():
            return self._send_json(403, {
                "status": "forbidden",
                "message": "Akses statis ke file ini tidak diizinkan.",
            })

        # T2.1: sajikan aset teks statis (html/css/js/json) dengan gzip bila
        # klien mendukung — transfer ~3-4x lebih kecil untuk HP berkuota.
        if self._send_gzipped_static():
            return

        return super().do_GET()

    _GZIP_STATIC_EXTS = ('.html', '.css', '.js', '.json', '.svg', '.txt')

    def _send_gzipped_static(self):
        """Kirim file statis teks dengan gzip. Kembalikan True bila terkirim."""
        accept = (self.headers.get('Accept-Encoding') or '').lower()
        if 'gzip' not in accept:
            return False
        clean = urllib.parse.unquote(self.path).split('?', 1)[0].split('#', 1)[0]
        if not clean.lower().endswith(self._GZIP_STATIC_EXTS):
            return False
        fpath = self.translate_path(self.path)
        if not os.path.isfile(fpath):
            return False
        size = os.path.getsize(fpath)
        if size < 1024 or size > 2_000_000:
            return False
        try:
            with open(fpath, 'rb') as fh:
                body = gzip.compress(fh.read(), compresslevel=6)
        except OSError:
            return False
        ctype = self.guess_type(fpath)
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Encoding', 'gzip')
        self.send_header('Vary', 'Accept-Encoding')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass
        return True

    def do_POST(self):
        # Fase 2, Fix 3b: tolak body > 1MB di awal (413) sebelum dibaca penuh.
        try:
            _clen = int(self.headers.get('Content-Length', 0) or 0)
        except (TypeError, ValueError):
            _clen = 0
        if _clen > MAX_POST_BYTES:
            # Buang body (dibatasi) agar koneksi tetap bersih, lalu tolak.
            _remaining = min(_clen, MAX_DRAIN_BYTES)
            while _remaining > 0:
                _chunk = self.rfile.read(min(65536, _remaining))
                if not _chunk:
                    break
                _remaining -= len(_chunk)
            if _clen > MAX_DRAIN_BYTES:
                self.close_connection = True
            return self._send_json(413, {
                "status": "error",
                "message": "Ukuran permintaan melebihi batas 1 MB.",
            })
        _track_client_context(self)
        _did, _need_ck = visitor_log.record(self)
        self._visitor_did = _did
        self._visitor_cookie = visitor_log.cookie_header_value(_did) if (_did and _need_ck) else None
        if PUBLIC_DEMO and self.path in DEMO_BLOCKED_PATHS:
            return self._send_json(403, {
                "status": "forbidden",
                "message": "Endpoint ini dimatikan saat mode demo publik.",
            })
        if self.path == '/api/swarm/start':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
                targets = None
                if post_data.strip():
                    try:
                        body = json.loads(post_data)
                        targets = body.get("targets")
                    except Exception:
                        pass
                from pipeline.swarm_manager import swarm_engine
                ok, msg = swarm_engine.start_swarm_pipeline(targets=targets)
                return self._send_json(200 if ok else 400, {"status": "success" if ok else "error", "message": msg})
            except Exception as e:
                return self._send_500(e, "/api/swarm/start")

        if self.path == '/api/swarm/reset':
            try:
                from pipeline.swarm_manager import swarm_engine
                swarm_engine.reset()
                return self._send_json(200, {"status": "success", "message": "Swarm status reset."})
            except Exception as e:
                return self._send_500(e, "/api/swarm/reset")

        if self.path == '/api/ai-tutor':
            # Endpoint legacy DIHAPUS (Fase 2): tanpa kuota/proteksi & duplikasi
            # ~700 baris via legacy_tutor. 410 Gone agar klien lama tahu ini
            # disengaja — gunakan /api/tutor/chat.
            return self._send_json(410, {
                "status": "gone",
                "message": "Endpoint /api/ai-tutor sudah tidak tersedia. Gunakan /api/tutor/chat.",
            })

        elif self.path == '/api/solution':
            # Pembahasan kanonis utk panel 'Tata Cara & Langkah Penyelesaian Soal'
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                payload = json.loads(post_data)
                subject = payload.get('subject', 'matematika')
                paket = int(payload.get('paket', 1))
                nomor = int(payload.get('nomor', 1))
                canon = canonical_for(subject, paket, nomor)
                if not canon:
                    raise LookupError(
                        f"Soal kanonis tidak ditemukan: {subject} paket {paket} nomor {nomor}")
                lrn_q = learning_for(subject, paket, nomor)
                sol = build_solution_payload(canon, lrn_q, subject, paket)
                # Konteks visual (Layer 2) selalu dikirim — transkripsi soal ini,
                # BUKAN pembahasan. Solusi (Layer 3) hanya bila benar-benar ada.
                response_data = {
                    "status": "success" if sol else "pending",
                    "solution": sol,
                    "visual_items": collect_visual_items(canon),
                    "formulas": [
                        {"latex": f.get("latex", ""), "source": f.get("source", "")}
                        for f in canon.get("visual_context", {}).get("formulas", [])
                    ],
                    "visual_unresolved": len(canon.get("visual_context", {}).get("unresolved", [])),
                    "canonical_id": canon["id"],
                    "transcription_status": canon.get("transcription_status"),
                    "message": None if sol else (
                        "Langkah penyelesaian Claude untuk soal ini belum tersedia "
                        "(file solusi Claude belum ada — panel menampilkan status jujur, "
                        "bukan konten generik lama)."
                    ),
                }
                return self._send_json(200, response_data)
            except LookupError:
                # Soal tidak ditemukan — pesan aman tanpa detail internal.
                return self._send_json(404, {"status": "error",
                                             "message": "Soal tidak ditemukan."})
            except Exception as e:
                return self._send_500(e, "/api/solution")

        elif self.path == '/api/tutor/chat':
            # =============================================================
            # AI Tutor konversasional: LLM + Layer2 + Layer3 + riwayat DB.
            # Urutan hidup: validasi -> resolusi soal -> simpan pesan user ->
            # susun konteks -> LLM -> simpan balasan. LLM gagal => pesan user
            # TETAP tersimpan, TIDAK ada balasan palsu, UI menampilkan retry.
            # =============================================================
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            user_key, new_cookie = self._tutor_session()
            try:
                payload = json.loads(post_data)
                subject = payload.get('subject', 'matematika')
                paket = int(payload.get('paket', 1))
                nomor = int(payload.get('nomor', 1))
                message = (payload.get('message') or '').strip()
                model = payload.get('model')
                request_id = payload.get('request_id') or None
                if not message:
                    return self._send_json(400, {"status": "error",
                                                 "message": "Pesan kosong."})
                ctx = resolve_tutor_context(subject, paket, nomor)
                if not ctx:
                    return self._send_json(404, {"status": "error",
                                                 "message": "Soal tidak ditemukan."})

                # Sinkronkan tier kuota jika request berasal dari pengguna login
                is_login = self._is_logged_in_request(payload)
                dev_id, dev_fp, client_ip = self._extract_device_info(payload)
                tier_target = "free" if is_login else None
                if is_login:
                    tutor_store.set_user_tier(user_key, tier="free")

                # Fase 2, Fix 1: cek cooldown & kuota TANPA mengonsumsi.
                # Kuota hanya dipotong SETELAH LLM berhasil menjawab — bila LLM
                # gagal, kuota user tidak hangus.
                _quota = tutor_store.get_user_quota(user_key, cooldown_seconds=10,
                                                    device_id=dev_id, fingerprint=dev_fp, ip_address=client_ip)
                _quota["is_logged_in"] = is_login or (_quota.get("tier") in ("free", "subscriber"))
                if not _quota.get("can_ask"):
                    if _quota.get("cooldown_remaining", 0) > 0:
                        quota_reason = "cooldown"
                        wait_sec = _quota["cooldown_remaining"]
                        limit_msg = f"Santai dulu ya, tunggu {wait_sec} detik sebelum mengirim pertanyaan berikutnya."
                    else:
                        quota_reason = "quota_exceeded"
                        wait_sec = 0
                        limit = _quota.get("daily_limit", 25 if is_login else 5)
                        if not is_login and _quota.get("device_limited"):
                            limit_msg = "Batas 5 pertanyaan gratis untuk perangkat ini telah habis hari ini. Silakan masuk dengan akun Google untuk mendapatkan 25 pertanyaan per hari!"
                        else:
                            limit_msg = f"Batas kuota harian ({limit} pertanyaan) telah tercapai. Kuota direset setiap 00.00 WIB — Masuk Google dapat 25 pertanyaan per hari!"
                    return self._send_json(429, {
                        "status": "rate_limited",
                        "reason": quota_reason,
                        "error_kind": "rate_limit",
                        "retryable": quota_reason == "cooldown",
                        "wait_seconds": wait_sec,
                        "quota": _quota,
                        "message": limit_msg,
                    }, cookie_value=new_cookie)
                conv = tutor_store.get_or_create_conversation(
                    user_key, ctx["canonical_id"], subject, paket, nomor)
                conv_id = conv["id"]
                um, _inserted = tutor_store.add_message(
                    conv_id, 'user', message, request_id=request_id)
                # Riwayat utk prompt: TANPA pesan yang baru saja dikirim
                # (dikirim terpisah sebagai current_message).
                history = tutor_store.get_history_window(
                    conv_id, tutor_engine.DEFAULT_RECENT_WINDOW)
                history_for_prompt = [m for m in history if m["id"] != um["id"]]
                # Antrean konkurensi: batasi beban simultan ke provider LLM
                acquired = _llm_concurrency_semaphore.acquire(timeout=40.0)
                if not acquired:
                    return self._send_json(503, {
                        "status": "busy",
                        "error_kind": "rate_limit",
                        "retryable": True,
                        "message": "Antrean AI Tutor sedang padat. Tunggu beberapa detik lalu kirim ulang ya!",
                    }, cookie_value=new_cookie)

                try:
                    reply, meta = tutor_engine.generate_tutor_response(
                        ctx["canon_ctx"], ctx["solution"], ctx["official_answer"],
                        history_for_prompt, message, summary=conv.get("summary"),
                        subject_name=ctx["subject_name"],
                        model=model,
                        image_paths=ctx.get("image_paths", []))
                except tutor_llm.LLMError as e:
                    _refresh_tutor_summary(conv_id)
                    return self._send_json(502, {
                        "status": "llm_error", "error_kind": e.kind,
                        "retryable": True, "user_message_stored": True,
                        "conversation_id": conv_id,
                        "message": (f"Penjelasan dari AI belum berhasil ({e.kind}). "
                                    f"Pesanmu sudah tersimpan — coba kirim ulang."),
                    }, cookie_value=new_cookie)
                finally:
                    _llm_concurrency_semaphore.release()

                model_name = meta.get("model") or tutor_llm.active_provider_info().get("model") or "AI Tutor"
                am, _ = tutor_store.add_message(
                    conv_id, 'assistant', reply,
                    request_id=(request_id + ':a') if request_id else None,
                    metadata={"intent": meta.get("intent"),
                              "model": model_name,
                              "provider": meta.get("provider") or tutor_llm.active_provider_info()["provider"]})
                _refresh_tutor_summary(conv_id)
                # Konsumsi kuota SETELAH jawaban LLM sukses tersimpan.
                # (LLM gagal -> kuota tidak dipotong; lihat blok LLMError.)
                _ok, _reason, _wait, user_quota = tutor_store.consume_user_quota(
                    user_key, cooldown_seconds=10, tier_override=tier_target,
                    device_id=dev_id, fingerprint=dev_fp, ip_address=client_ip)
                if not _ok:
                    # Balapan antar-request: jawaban sudah terkirim, segarkan
                    # info kuota utk respons.
                    user_quota = tutor_store.get_user_quota(
                        user_key, cooldown_seconds=10,
                        device_id=dev_id, fingerprint=dev_fp, ip_address=client_ip)
                user_quota["is_logged_in"] = is_login or (user_quota.get("tier") in ("free", "subscriber"))
                return self._send_json(200, {
                    "status": "success", "reply": reply,
                    "conversation_id": conv_id, "message_id": am["id"],
                    "intent": meta.get("intent"),
                    "model": model_name,
                    "quota": user_quota,
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_500(e, "/api/tutor/chat", cookie_value=new_cookie)

        elif self.path == '/api/tutor/new':
            # Mulai percakapan BARU utk soal ini; riwayat lama diarsipkan,
            # tidak dihapus (auditable). Frontend menampilkan chat bersih.
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            user_key, new_cookie = self._tutor_session()
            try:
                payload = json.loads(post_data)
                subject = payload.get('subject', 'matematika')
                paket = int(payload.get('paket', 1))
                nomor = int(payload.get('nomor', 1))
                ctx = resolve_tutor_context(subject, paket, nomor)
                if not ctx:
                    return self._send_json(404, {"status": "error",
                                                 "message": "Soal tidak ditemukan."})
                conv = tutor_store.start_new_conversation(
                    user_key, ctx["canonical_id"], subject, paket, nomor)
                return self._send_json(200, {
                    "status": "success", "conversation_id": conv["id"],
                    "messages": [], "summary": None,
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_500(e, "/api/tutor/new", cookie_value=new_cookie)

        elif self.path == '/api/feedback':
            # Fase 5: simpan masukan pengguna (rating 1-5 + pesan opsional).
            # Validasi ketat + rate limit per sesi (jeda 10 menit, maks 3/24 jam).
            content_length = int(self.headers.get('Content-Length', 0))
            _payload_raw = self.rfile.read(content_length).decode('utf-8') or '{}'
            user_key, new_cookie = self._tutor_session()
            try:
                payload = json.loads(_payload_raw)
                try:
                    rating = int(payload.get('rating') or 0)
                except (TypeError, ValueError):
                    rating = 0
                message = str(payload.get('message') or '').strip()[:1000]
                device = 'mobile' if str(payload.get('device') or '').lower() == 'mobile' else 'desktop'
                if rating < 1 or rating > 5:
                    return self._send_json(400, {"status": "error",
                                                 "message": "Rating harus 1-5."})
                allowed, wait_sec = tutor_store.allow_feedback(user_key)
                if not allowed:
                    return self._send_json(429, {
                        "status": "rate_limited",
                        "retry_after": wait_sec,
                        "message": "Masukanmu sudah terkirim baru-baru ini. Terima kasih!",
                    }, cookie_value=new_cookie)
                plan = tutor_store.get_user_quota(user_key).get('tier') or 'guest'
                tutor_store.add_feedback(user_key, rating, message, device, plan)
                return self._send_json(200, {
                    "status": "success",
                    "message": "Terima kasih! Masukanmu terkirim.",
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_500(e, "/api/feedback", cookie_value=new_cookie)

        elif self.path == '/api/bug-reports':
            # FASE 2 (T2.6): Simpan laporan kendala / bug soal dari pengguna
            content_length = int(self.headers.get('Content-Length', 0))
            _payload_raw = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            user_key, new_cookie = self._tutor_session()
            try:
                payload = json.loads(_payload_raw) if _payload_raw else {}
                title = str(payload.get('title') or '').strip()[:200]
                description = str(payload.get('description') or '').strip()[:2000]
                if not description:
                    return self._send_json(400, {"status": "error", "message": "Deskripsi kendala wajib diisi."})
                reports_path = os.path.join(BASE_DIR, 'data', 'bug_reports.jsonl')
                record = {
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "user_key": user_key,
                    "title": title,
                    "description": description,
                    "ip": self.client_address[0]
                }
                with open(reports_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
                return self._send_json(200, {
                    "status": "success",
                    "message": "Laporan kendala berhasil disimpan.",
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_500(e, "/api/bug-reports", cookie_value=new_cookie)

        elif self.path == '/api/tutor/reset_quota':
            user_key, new_cookie = self._tutor_session()
            try:
                quota = tutor_store.reset_user_quota(user_key)
                return self._send_json(200, {
                    "status": "success",
                    "message": "Kuota berhasil di-refresh kembali penuh!",
                    "quota": quota,
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_500(e, "/api/tutor/reset_quota", cookie_value=new_cookie)

        elif self.path == '/api/tutor/sync_user':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            user_key, new_cookie = self._tutor_session()
            try:
                payload = json.loads(post_data) if post_data else {}
                if auth_verify.auth_verify_enabled():
                    # T2.11: JANGAN percaya klaim klien. Tier 'free' hanya bila
                    # JWT Supabase valid (header Authorization: Bearer ...).
                    # Tanpa token valid -> guest (user tidak terkunci, hanya
                    # kuota tamu sampai token terkirim).
                    _vok, _claims = auth_verify.verify_request(self.headers)
                    is_login = bool(_vok)
                    if is_login and isinstance(_claims, dict):
                        payload = dict(payload)
                        payload['email'] = _claims.get('email') or payload.get('email')
                        payload['name'] = (
                            (_claims.get('user_metadata') or {}).get('full_name')
                            or payload.get('name'))
                else:
                    is_login = bool(payload.get('logged_in') or payload.get('email') or payload.get('is_logged_in'))
                tier = "free" if is_login else "guest"
                quota = tutor_store.set_user_tier(user_key, tier=tier)
                quota["is_logged_in"] = is_login
                # Pemantau pengunjung: tautkan perangkat -> identitas login
                # supaya dashboard menampilkan nama, bukan cuma "Android · Chrome".
                if is_login and payload.get('email'):
                    try:
                        visitor_log.identify(
                            getattr(self, '_visitor_did', '') or '',
                            payload.get('email'), payload.get('name') or '')
                    except Exception:
                        pass
                return self._send_json(200, {
                    "status": "success",
                    "tier": tier,
                    "daily_limit": quota.get("daily_limit"),
                    "remaining": quota.get("remaining"),
                    "quota": quota,
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_500(e, "/api/tutor/sync_user", cookie_value=new_cookie)

        elif self.path == '/api/attempts':
            # FASE 3 (T3.2): terima attempt dari klien, teruskan ke Supabase.
            # Identitas dari JWT yang diverifikasi — JANGAN percaya user_id klien.
            # Server meneruskan Bearer token user ke Supabase REST; RLS
            # (attempts_owner) menegakkan user_id = auth.uid().
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8') \
                    if content_length > 0 else '{}'
                payload = json.loads(post_data) if post_data else {}
                _auth = self.headers.get('Authorization', '') or ''
                _token = _auth[len('Bearer '):].strip() \
                    if _auth.startswith('Bearer ') else ''
                if not _token:
                    return self._send_json(401, {
                        "status": "unauthorized",
                        "message": "Login diperlukan untuk menyimpan hasil tryout.",
                    })
                # Verifikasi via Supabase Auth API (mendukung HS256/ES256/RS256).
                _vok, _user = _verify_supabase_token(_token)
                if not _vok or not (_user or {}).get('id'):
                    return self._send_json(401, {
                        "status": "unauthorized",
                        "message": "Sesi login tidak valid atau kadaluarsa. Coba logout lalu login lagi.",
                    })
                user_id = _user['id']
                sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
                sb_key = os.environ.get('SUPABASE_ANON_KEY', '')
                if not sb_url or not sb_key:
                    return self._send_json(503, {
                        "status": "error",
                        "message": "Penyimpanan server belum dikonfigurasi "
                                   "(SUPABASE_URL / SUPABASE_ANON_KEY).",
                    })
                ok_items, err_items, clean_items = clean_attempt_items(payload.get('items'))
                if not ok_items:
                    sys.stderr.write(f"[/api/attempts] 400 Bad Request: {err_items}\n")
                    _log_server_error(ValueError(err_items), context="POST /api/attempts payload.items validation")
                    return self._send_json(400, {
                        "status": "error",
                        "message": err_items,
                    })
                # Idempotency: client_id dari klien jadi client_attempt_id.
                # Kirim dua kali dengan client_id sama -> satu baris.
                client_attempt_id = str(payload.get("client_id") or "")[:64]
                if not client_attempt_id:
                    return self._send_json(400, {
                        "status": "error",
                        "message": "client_id wajib diisi.",
                    })
                # Cek apakah sudah ada (idempotent)
                try:
                    chk = urllib.request.Request(
                        sb_url + "/rest/v1/attempts?user_id=eq." + user_id +
                        "&client_attempt_id=eq." + urllib.parse.quote(client_attempt_id) +
                        "&select=id",
                        headers={"apikey": sb_key, "Authorization": "Bearer " + _token})
                    with urllib.request.urlopen(chk, timeout=10) as cresp:
                        existing = json.loads(cresp.read().decode("utf-8") or "[]")
                    if existing:
                        return self._send_json(200, {
                            "status": "success",
                            "attempt_id": existing[0].get("id"),
                            "duplicate": True,
                        })
                except Exception:
                    pass  # lanjut ke INSERT; constraint UNIQUE jadi pengaman akhir
                row = {
                    "user_id": user_id,  # dari token, bukan dari klien
                    "client_attempt_id": client_attempt_id,
                    "mapel": str(payload.get("subject") or payload.get("mapel") or "")[:64],
                    "paket": max(0, min(int(payload.get("paket") or 0), 99)),
                    "n_questions": max(1, min(int(payload.get("n_questions") or len(clean_items)), 200)),
                    "duration_limit_s": max(0, min(int(payload.get("duration_limit_s") or 0), 86400)),
                    "ended_by": "timer" if payload.get("ended_by") == "timer" else "user",
                    "started_at": payload.get("started_at"),
                    "finished_at": payload.get("finished_at"),
                    "score": payload.get("score") if isinstance(payload.get("score"), int) else None,
                    "items": clean_items,
                }
                req = urllib.request.Request(
                    sb_url + "/rest/v1/attempts",
                    data=json.dumps(row).encode("utf-8"), method="POST",
                    headers={"apikey": sb_key,
                             "Authorization": "Bearer " + _token,
                             "Content-Type": "application/json",
                             "Prefer": "return=representation"})
                try:
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        saved = json.loads(resp.read().decode("utf-8") or "[]")
                    return self._send_json(200, {
                        "status": "success",
                        "attempt_id": (saved[0].get("id") if saved else None),
                    })
                except urllib.error.HTTPError as e:
                    if e.code == 409:
                        # 409 Conflict: client_attempt_id sudah ada (idempotency pengaman akhir)
                        return self._send_json(200, {
                            "status": "success",
                            "duplicate": True,
                            "message": "Attempt sudah tersimpan sebelumnya.",
                        })
                    return self._send_json(502, {
                        "status": "error",
                        "message": f"Supabase menolak penyimpanan (HTTP {e.code}).",
                    })
                except urllib.error.URLError:
                    return self._send_json(502, {
                        "status": "error",
                        "message": "Tidak dapat menghubungi Supabase.",
                    })
            except Exception as e:
                return self._send_500(e, "/api/attempts")

        elif self.path == '/api/autopsy/analyze':
            # FASE 5 (T5.1): analisis Autopsi untuk attempt.
            # Input: {items, n_questions, duration_limit_s, ended_by, mapel}
            # Output: hasil analyzer. Preview gratis = kebocoran #1 terbuka, sisanya terkunci.
            try:
                if autopsy_analyzer is None:
                    return self._send_json(503, {"status": "error", "message": "Analyzer belum tersedia."})
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
                payload = json.loads(post_data) if post_data else {}
                _auth = self.headers.get('Authorization', '') or ''
                _token = _auth[7:] if _auth.startswith('Bearer ') else ''
                is_guest = not bool(_token)
                is_admin = False
                if _token:
                    _vok, _user = _verify_supabase_token(_token)
                    if not _vok and not payload.get('is_guest'):
                        # Cek apakah token admin
                        if self._is_valid_admin():
                            is_admin = True
                        else:
                            is_guest = True
                    elif _vok:
                        # User valid
                        pass
                if self._is_valid_admin() or payload.get('founder_mode'):
                    is_admin = True

                items = payload.get('items')
                if not isinstance(items, list) or not items:
                    return self._send_json(400, {"status": "error", "message": "Items kosong."})
                # Siapkan input analyzer
                attempt_data = {
                    'n_questions': int(payload.get('n_questions') or len(items)),
                    'duration_limit_s': int(payload.get('duration_limit_s') or 4500),
                    'ended_by': payload.get('ended_by') or 'user',
                    'kunci': {},  # is_correct dari klien untuk preview; server hitung ulang saat ada kunci
                    'items': items,
                }
                # Jika klien kirim is_correct, pakai itu (preview). Server akan validasi ulang via kunci di Fase 6+.
                result = autopsy_analyzer.analyze(attempt_data)
                # Kebocoran dibuka semua (Paywall OFF sesuai keputusan produk)
                preview = {
                    'status': 'success',
                    'preview': False,
                    'is_guest': is_guest,
                    'is_founder': is_admin,
                    'n_questions': result.get('n_questions'),
                    'n_answered': result.get('n_answered'),
                    'n_correct': result.get('n_correct'),
                    'data_tipis': result.get('data_tipis'),
                    'kebocoran_1': keb[0] if keb else None,
                    'kebocoran_all': keb,
                    'kebocoran_locked': [],
                    'rapuh_count': len(result.get('rapuh_ids') or []),
                    'topik_prioritas': result.get('topik_prioritas') or [],
                }
                return self._send_json(200, preview)
            except Exception as e:
                return self._send_500(e, "/api/autopsy/analyze")

        elif self.path.split('?', 1)[0] == '/api/autopsy/coach':
            return self._handle_post_autopsy_coach()

        elif self.path.split('?', 1)[0] == '/admin/autopsi':
            if PUBLIC_DEMO:
                return self._send_json(403, {"status": "forbidden", "message": "Dimatikan saat demo publik."})
            if not self._is_valid_admin():
                return self._send_json(401, {"status": "unauthorized", "message": "Kunci admin salah atau tidak diberikan."})
            return self._handle_admin_autopsi_page()

        elif self.path.split('?', 1)[0] == '/api/admin/autopsy_full':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            try:
                payload = json.loads(post_data) if post_data else {}
            except Exception:
                payload = {}
        elif self.path == '/api/user/progress':
            # BUG-001 (Tugas D): simpan progress belajar user ke Supabase.
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 256 * 1024:
                    return self._send_json(413, {"status": "error", "message": "Ukuran data progress melebihi batas 256 KB."})
                _auth = self.headers.get('Authorization', '') or ''
                _token = _auth[7:] if _auth.startswith('Bearer ') else ''
                if not _token:
                    return self._send_json(401, {"status": "unauthorized"})
                _vok, _user = _verify_supabase_token(_token)
                if not _vok:
                    return self._send_json(401, {"status": "unauthorized"})
                user_id = _user['id']
                post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
                payload = json.loads(post_data) if post_data else {}
                progress_data = payload.get('progress')
                if not isinstance(progress_data, dict):
                    return self._send_json(400, {"status": "error", "message": "Format progress harus JSON object."})
                sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
                sb_key = os.environ.get('SUPABASE_ANON_KEY', '')
                req = urllib.request.Request(
                    sb_url + "/rest/v1/users?id=eq." + user_id,
                    data=json.dumps({"progress": progress_data}).encode('utf-8'), method="PATCH",
                    headers={"apikey": sb_key, "Authorization": "Bearer " + _token,
                             "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10):
                    pass
                return self._send_json(200, {"status": "success"})
            except Exception as e:
                return self._send_500(e, "/api/user/progress")

        elif self.path == '/api/user/tka_date':
            # FASE 5 (T5.3): simpan tanggal TKA user.
            try:
                _auth = self.headers.get('Authorization', '') or ''
                _token = _auth[7:] if _auth.startswith('Bearer ') else ''
                if not _token:
                    return self._send_json(401, {"status": "unauthorized"})
                _vok, _user = _verify_supabase_token(_token)
                if not _vok:
                    return self._send_json(401, {"status": "unauthorized"})
                user_id = _user['id']
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
                payload = json.loads(post_data) if post_data else {}
                tka_date = str(payload.get('tka_date') or '')[:10]
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', tka_date):
                    return self._send_json(400, {"status": "error", "message": "Format tanggal salah."})
                sb_url = os.environ.get('SUPABASE_URL', '').rstrip('/')
                sb_key = os.environ.get('SUPABASE_ANON_KEY', '')
                req = urllib.request.Request(
                    sb_url + "/rest/v1/users?id=eq." + user_id,
                    data=json.dumps({"tka_date": tka_date}).encode('utf-8'), method="PATCH",
                    headers={"apikey": sb_key, "Authorization": "Bearer " + _token,
                             "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10):
                    pass
                return self._send_json(200, {"status": "success", "tka_date": tka_date})
            except Exception as e:
                return self._send_500(e, "/api/user/tka_date")

        elif self.path.split('?', 1)[0] == '/api/admin/flags':
            # FASE 0 T0.7: ubah flag TANPA deploy ulang. Proteksi: kunci admin
            # yang sama dengan dashboard /pengunjung (header X-Admin-Key atau JSON body {"key": "..."}).
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length).decode('utf-8') \
                    if content_length > 0 else '{}'
                try:
                    payload = json.loads(post_data) if post_data else {}
                except Exception:
                    payload = {}
                if not self._is_valid_admin(payload):
                    return self._send_json(401, {
                        "status": "unauthorized",
                        "message": "Kunci admin salah atau tidak diberikan.",
                    })
                name = str(payload.get('name', ''))
                enabled = bool(payload.get('enabled', False))
                rollout = payload.get('rollout_pct')
                ok = feature_flags.set_flag(name, enabled, rollout)
                if not ok:
                    return self._send_json(400, {
                        "status": "error",
                        "message": "Nama flag tidak dikenal.",
                        "known": sorted(feature_flags.DEFAULT_FLAGS.keys()),
                    })
                return self._send_json(200, {
                    "status": "success",
                    "flags": feature_flags.get_all_flags(),
                })
            except Exception as e:
                return self._send_500(e, "/api/admin/flags")

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        # Same-origin saja: tidak ada '*' utk respons ber-cookie.
        allow_origin = self._cors_allow_origin()
        if allow_origin:
            self.send_header('Access-Control-Allow-Origin', allow_origin)
            self.send_header('Vary', 'Origin')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Device-Id, X-Device-Fingerprint, X-User-Logged-In, X-User-Email, X-User-Name')
        self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = ThreadingHTTPServer(server_address, AppRequestHandler)
    print(f"[Server] CBT TKA Learning Server with AI Tutor running at http://localhost:{PORT}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Stopping server.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
