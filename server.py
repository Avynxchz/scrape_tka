import re
import os
import sys
import json
import urllib.request
import urllib.parse
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

import solution_loader  # noqa: E402  (sumber Layer 3: solusi spesifik Claude)
import tutor_engine    # noqa: E402  (mesin tutor konversasional berbasis LLM)
import tutor_llm       # noqa: E402  (abstraksi provider LLM)
import tutor_store     # noqa: E402  (persistensi percakapan — SQLite)
import legacy_tutor    # noqa: E402  (arsip mesin heuristik lama)

tutor_store.init_db()  # skema ai_tutor_* dibuat idempoten saat server dimuat

# ============================================================================
# ANTI-SPAM RATE LIMITER PER USER
# ============================================================================
_user_rate_limits = {}
_rate_limit_lock = threading.Lock()

# ============================================================================
# CONCURRENCY QUEUE UNTUK 50 USER (SEMAPHORE)
# ============================================================================
MAX_CONCURRENT_LLM = int(os.environ.get("LLM_MAX_CONCURRENT", "6"))
_llm_concurrency_semaphore = threading.Semaphore(MAX_CONCURRENT_LLM)

def _check_user_rate_limit(user_key):
    """Mencegah satu user melakukan spam agar kuota user lain tetap terjaga."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return True, None
    cooldown = float(os.environ.get("RATE_LIMIT_COOLDOWN_SEC", "1.5"))
    max_per_min = int(os.environ.get("RATE_LIMIT_MAX_PER_MIN", "20"))
    if cooldown <= 0:
        return True, None
    now = time.time()
    with _rate_limit_lock:
        timestamps = _user_rate_limits.get(user_key, [])
        timestamps = [t for t in timestamps if now - t < 60]
        if timestamps:
            if (now - timestamps[-1]) < cooldown:
                wait_sec = round(cooldown - (now - timestamps[-1]), 1)
                return False, f"Santai dulu ya, tunggu {wait_sec} detik sebelum mengirim pesan berikutnya."
            if len(timestamps) >= max_per_min:
                return False, "Batas pengiriman pesan per menit tercapai. Tunggu sebentar ya!"
        timestamps.append(now)
        _user_rate_limits[user_key] = timestamps
        return True, None

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
            # Cari rekursif di folder data bila letak gambar ada di subfolder lain
            for root, dirs, files in os.walk(os.path.join(BASE_DIR, "data")):
                if fn in files:
                    cand = os.path.join(root, fn)
                    if cand not in found_paths:
                        found_paths.append(cand)
                    break

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

# Arsip mesin tutor heuristik berbasis aturan dipindahkan ke legacy_tutor.py
get_ai_tutor_response = legacy_tutor.get_ai_tutor_response


_client_active_context = {}  # ip -> {"subject": ..., "paket": ...}

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

                for root, dirs, files in os.walk(data_root):
                    if filename in files:
                        return os.path.join(root, filename)

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

    def _send_json(self, status, obj, cookie_value=None):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        if cookie_value:
            self.send_header('Set-Cookie',
                             f'tutor_uid={cookie_value}; Path=/; HttpOnly; '
                             f'SameSite=Lax; Max-Age=31536000')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        _track_client_context(self)
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

        if self.path.split('?', 1)[0] == '/api/tutor/state':
            # Muat ulang percakapan tersimpan soal ini (resume tanpa isi kosong)
            try:
                params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                subject = params.get('subject', ['matematika'])[0]
                paket = int(params.get('paket', ['1'])[0])
                nomor = int(params.get('nomor', ['1'])[0])
                user_key, new_cookie = self._tutor_session()
                ctx = resolve_tutor_context(subject, paket, nomor)
                if not ctx:
                    return self._send_json(404, {"status": "error",
                                                 "message": "Soal tidak ditemukan."},
                                           cookie_value=new_cookie)
                conv = tutor_store.get_or_create_conversation(
                    user_key, ctx["canonical_id"], subject, paket, nomor, create=False)
                messages = tutor_store.get_messages(conv["id"]) if conv else []
                user_quota = tutor_store.get_user_quota(user_key)
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
                return self._send_json(500, {"status": "error", "message": str(e)})

        if self.path.split('?', 1)[0] == '/api/swarm/status':
            try:
                from pipeline.swarm_manager import swarm_engine
                return self._send_json(200, swarm_engine.get_status())
            except Exception as e:
                return self._send_json(500, {"status": "error", "message": str(e)})

        if self.path.split('?', 1)[0] == '/api/swarm/subjects':
            try:
                from pipeline.subject_catalog import get_full_catalog
                return self._send_json(200, get_full_catalog())
            except Exception as e:
                return self._send_json(500, {"status": "error", "message": str(e)})

        return super().do_GET()

    def do_POST(self):
        _track_client_context(self)
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
                return self._send_json(500, {"status": "error", "message": str(e)})

        if self.path == '/api/swarm/reset':
            try:
                from pipeline.swarm_manager import swarm_engine
                swarm_engine.reset()
                return self._send_json(200, {"status": "success", "message": "Swarm status reset."})
            except Exception as e:
                return self._send_json(500, {"status": "error", "message": str(e)})

        if self.path == '/api/ai-tutor':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                payload = json.loads(post_data)
                paket = payload.get('paket', 1)
                nomor = payload.get('nomor', 1)
                user_msg = payload.get('message', '')
                q_data = payload.get('question_data', {})

                # Subject dari frontend (payload root) diprioritaskan
                subject = payload.get('subject')
                if subject:
                    q_data['subject'] = subject

                # --- Konteks kanonis (sumber kebenaran AI) ---------------------
                canon = canonical_for(subject, paket, nomor)
                lrn_q = learning_for(subject, paket, nomor)
                canon_ctx = build_canonical_context(canon, lrn_q) if canon else None
                if canon_ctx:
                    q_data['_canonical'] = canon_ctx

                # Layer 3 aktif (solusi spesifik Claude dari sumber registry)
                if subject:
                    try:
                        _l3 = solution_loader.get_solution(
                            subject, paket, nomor, format_kunci_display(lrn_q or {}))
                    except Exception:
                        _l3 = None
                    if _l3:
                        q_data['_solution_layer3'] = _l3

                reply = get_ai_tutor_response(paket, nomor, user_msg, q_data)
                
                response_data = {
                    "status": "success",
                    "reply": reply,
                    "nomor": nomor
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

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
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            except LookupError as e:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

        elif self.path == '/api/tutor/chat':
            # =============================================================
            # AI Tutor konversasional: LLM + Layer2 + Layer3 + riwayat DB.
            # Urutan hidup: validasi -> resolusi soal -> simpan pesan user ->
            # susun konteks -> LLM -> simpan balasan. LLM gagal => pesan user
            # TETAP tersimpan, TIDAK ada balasan palsu, UI menampilkan retry.
            # =============================================================
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
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
                user_key, new_cookie = self._tutor_session()
                # Cooldown 10s & Kuota Harian (10x free / 100x langganan) per user
                quota_ok, quota_reason, wait_sec, user_quota = tutor_store.consume_user_quota(user_key, cooldown_seconds=10)
                if not quota_ok:
                    if quota_reason == "cooldown":
                        limit_msg = f"Santai dulu ya, tunggu {wait_sec} detik sebelum mengirim pertanyaan berikutnya."
                    else:
                        limit = user_quota.get("daily_limit", 10)
                        limit_msg = f"Batas kuota harian ({limit} pertanyaan) kamu untuk hari ini telah tercapai. Berlangganan untuk 100 pertanyaan per hari!"
                    return self._send_json(429, {
                        "status": "rate_limited",
                        "reason": quota_reason,
                        "error_kind": "rate_limit",
                        "retryable": quota_reason == "cooldown",
                        "wait_seconds": wait_sec,
                        "quota": user_quota,
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
                return self._send_json(200, {
                    "status": "success", "reply": reply,
                    "conversation_id": conv_id, "message_id": am["id"],
                    "intent": meta.get("intent"),
                    "model": model_name,
                    "quota": user_quota,
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_json(500, {"status": "error", "message": str(e)})

        elif self.path == '/api/tutor/new':
            # Mulai percakapan BARU utk soal ini; riwayat lama diarsipkan,
            # tidak dihapus (auditable). Frontend menampilkan chat bersih.
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                payload = json.loads(post_data)
                subject = payload.get('subject', 'matematika')
                paket = int(payload.get('paket', 1))
                nomor = int(payload.get('nomor', 1))
                ctx = resolve_tutor_context(subject, paket, nomor)
                if not ctx:
                    return self._send_json(404, {"status": "error",
                                                 "message": "Soal tidak ditemukan."})
                user_key, new_cookie = self._tutor_session()
                conv = tutor_store.start_new_conversation(
                    user_key, ctx["canonical_id"], subject, paket, nomor)
                return self._send_json(200, {
                    "status": "success", "conversation_id": conv["id"],
                    "messages": [], "summary": None,
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_json(500, {"status": "error", "message": str(e)})

        elif self.path == '/api/tutor/reset_quota':
            try:
                user_key, new_cookie = self._tutor_session()
                quota = tutor_store.reset_user_quota(user_key)
                return self._send_json(200, {
                    "status": "success",
                    "message": "Kuota berhasil di-refresh kembali penuh!",
                    "quota": quota,
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_json(500, {"status": "error", "message": str(e)})

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
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
