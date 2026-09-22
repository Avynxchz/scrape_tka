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

tutor_store.init_db()  # skema ai_tutor_* dibuat idempoten saat server dimuat

# ============================================================================
# ANTI-SPAM RATE LIMITER PER USER
# ============================================================================
_user_rate_limits = {}
_rate_limit_lock = threading.Lock()

def _check_user_rate_limit(user_key):
    """Mencegah satu user melakukan spam agar kuota user lain tetap terjaga."""
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

PORT = 8080
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
}
_canon_cache = {}
_lrn_cache = {}


def load_canonical_doc(subject, paket):
    slug = SUBJECT_SLUGS.get(subject, {}).get(paket)
    if not slug:
        return None
    if slug not in _canon_cache:
        path = os.path.join(CANON_DIR, f"{slug}.json")
        if not os.path.exists(path):
            _canon_cache[slug] = None
        else:
            with open(path, encoding="utf-8") as f:
                _canon_cache[slug] = json.load(f)
    return _canon_cache[slug]


def load_learning_doc(subject, paket):
    slug = SUBJECT_SLUGS.get(subject, {}).get(paket)
    if not slug:
        return None
    if slug not in _lrn_cache:
        path = os.path.join(BASE_DIR, "data", f"{slug}_learning.json")
        with open(path, encoding="utf-8") as f:
            _lrn_cache[slug] = json.load(f)
    return _lrn_cache[slug]


def canonical_for(subject, paket, nomor):
    doc = load_canonical_doc(subject, paket)
    if not doc:
        return None
    for q in doc["questions"]:
        if q["question_number"] == nomor:
            return q
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


def build_canonical_context(canon, lrn_q):
    """Bungkus satu soal kanonis menjadi konteks teks untuk AI Tutor."""
    vc = canon.get("visual_context", {})
    parts = []
    if canon.get("stimulus_text"):
        parts.append("[STIMULUS]\n" + canon["stimulus_text"])
    if canon.get("question_text"):
        parts.append("[SOAL]\n" + canon["question_text"])
    options = canon.get("options")
    statements = canon.get("statements")
    if options:
        opt_lines = "\n".join(f"  {k}. {v}" for k, v in options.items())
        parts.append("[OPSI JAWABAN]\n" + opt_lines)
    elif statements:
        st_lines = "\n".join(f"  {s['key']}. {s.get('display', '')}" for s in statements)
        parts.append("[PERNYATAAN]\n" + st_lines)
    visual_text = format_visual_context(vc)
    parts.append("[KONTEKS VISUAL]\n" + visual_text)
    kunci_disp = format_kunci_display(lrn_q or {})
    parts.append(f"[KUNCI RESMI] {kunci_disp}")
    return {
        "id": canon["id"],
        "type": canon["type"],
        "transcription_status": canon.get("transcription_status"),
        "soal_text": "\n\n".join(parts),
        "visual_text": visual_text,
        "formulas": [
            {"latex": f.get("latex", ""), "source": f.get("source", "")}
            for f in canon.get("visual_context", {}).get("formulas", [])
        ],
        "langkah_claude": canon.get("solution_steps_claude") or [],
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
            sol = solution_loader.get_solution(subject, paket, canon["question_number"], kunci_disp)
        except Exception:
            sol = None
    if not sol:
        return None

    glosarium = []
    for g in sol.get("glossary", []):
        sym, name = _split_glossary_term(g.get("term", ""))
        glosarium.append({"simbol": sym, "nama": name, "arti": g.get("meaning", "")})

    mengapa = "\n\n".join(x for x in (sol.get("reasoning"), sol.get("why_correct")) if x)
    langkah = [
        f"{st.get('step', i + 1)}. {st.get('title', '')} — {st.get('explanation', '')}".strip(" —")
        for i, st in enumerate(sol.get("steps", []))
    ]
    tips_lines = [f"• {t}" for t in sol.get("tips", [])]
    tips_lines += [f"⚠️ Jebakan umum: {m}" for m in sol.get("common_mistakes", [])]

    return {
        "pembahasan": {
            "konsep_kunci": sol.get("concept_kunci", []),
            "glosarium_simbol": glosarium,
            "mengapa_begini": mengapa or None,
            "langkah_penyelesaian": langkah,
            "tips_trik": "\n".join(tips_lines) or None,
        },
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
}


def resolve_tutor_context(subject, paket, nomor):
    """Kumpulkan konteks tutor utk satu soal: Layer 2 + Layer 3 + kunci resmi.

    Kunci resmi (Layer 2) tetap satu-satunya otoritas; Layer 3 hanya referensi.
    """
    canon = canonical_for(subject, paket, nomor)
    lrn_q = learning_for(subject, paket, nomor)
    if not canon:
        return None
    canon_ctx = build_canonical_context(canon, lrn_q)
    solution = build_solution_payload(canon, lrn_q, subject, paket)
    return {
        "canonical_id": canon["id"],
        "canon_ctx": canon_ctx,
        "solution": solution,           # berisi pembahasan/review/source/crosscheck
        "official_answer": canon_ctx["kunci_display"],
        "subject_name": SUBJECT_NAMES.get(subject, subject.title()),
        "subject": subject,
        "paket": paket,
        "nomor": nomor,
    }


def _refresh_tutor_summary(conversation_id):
    """Perbarui ringkasan bergulir bila percakapan panjang (gagal = abaikan)."""
    try:
        tutor_store.maybe_summarize(conversation_id, tutor_engine.summarize_older)
    except Exception:
        pass


def get_ai_tutor_response(paket, nomor, user_msg, q_data):
    """
    Multi-Subject Pedagogical AI Tutor Engine for Kurikulum Merdeka TKA.
    Supports: Matematika, Bahasa Inggris, Ekonomi, Kewirausahaan.
    Handles:
    1. Subject-aware expertise (adapts domain based on active mapel)
    2. Polite refusal for truly off-topic questions (gossip, games, etc.)
    3. Deep question-specific pedagogical explanations
    4. Visual memory - can describe images/charts in the question
    """
    msg_lower = user_msg.lower()
    active_topik = q_data.get('topik', 'Matematika TKA')
    active_subject = q_data.get('subject', 'matematika')  # from frontend
    visual_memory = q_data.get('visual_memory', '')
    is_math = active_subject == 'matematika'
    # Konteks kanonis (disuntik handler): soal verbatim + visual + kunci resmi
    canon_ctx = q_data.get('_canonical')
    # Layer 3 aktif: solusi spesifik soal hasil Claude (dari sumber registry)
    _l3 = q_data.get('_solution_layer3')
    _review_note = (
        "\n\n> ⚠️ *Catatan verifikasi: penjelasan soal ini menandai bahwa sebagian "
        "informasi sumber memerlukan verifikasi manual dan belum dapat dipastikan "
        "sepenuhnya. Perlakukan bagian terkait sebagai belum final.*"
    )

    # Subject display names
    subject_names = {
        "matematika": "Matematika",
        "bahasa_inggris": "Bahasa Inggris",
        "ekonomi": "Ekonomi",
        "kewirausahaan": "Produk Kreatif & Kewirausahaan"
    }
    active_subject_name = subject_names.get(active_subject, "Matematika")

    # =========================================================================
    # 1. DETEKSI TOPIK BENAR-BENAR DI LUAR KURIKULUM -> TOLAK DENGAN SOPAN
    # =========================================================================
    off_topic_keywords = [
        "resep", "masak", "makanan", "game", "mobile legends", "free fire", "anime",
        "film", "zodiak", "ramalan", "pacar", "cinta", "pacaran",
        "gosip", "artis", "tiktok", "instagram"
    ]

    if any(k in msg_lower for k in off_topic_keywords):
        return (
            "Halo! Senang sekali kamu bersemangat belajar. 😊\n\n"
            f"Namun, peran saya di sini adalah sebagai **Tutor Spesialis {active_subject_name}** (Kurikulum Merdeka). "
            "Untuk topik di luar kurikulum (seperti game, gosip, atau hiburan), "
            "saya belum bisa memberikan bimbingan.\n\n"
            f"Yuk, kita fokus kembali ke materi **{active_subject_name}** untuk persiapan ujian TKA! "
            "Silakan tanyakan hal-hal terkait soal yang sedang kamu pelajari ya!"
        )

    # =========================================================================
    # 2. CARA HITUNG CEPAT & ARITMATIKA (MENTAL MATH TRICKS) - MATEMATIKA SAJA
    # =========================================================================
    # Contoh kasus spesifik user: "cara ngitung cepat 22 per 30 dibagi 2"
    if is_math and (("22" in msg_lower and "30" in msg_lower) or ("dibagi 2" in msg_lower and "pecahan" in msg_lower)):
        return (
            "Pertanyaan yang luar biasa! Menghitung cepat pecahan seperti **22 per 30 dibagi 2** sering muncul saat menyederhanakan peluang atau aljabar:\n\n"
            "### Kasus A: Menyederhanakan Pecahan $\\frac{22}{30}$ (Pembilang & Penyebut Dibagi 2)\n"
            "Jika maksudmu adalah menyederhanakan pecahan $\\frac{22}{30}$:\n"
            "• **Trik Mental Math 2 Detik:** Karena pembilang ($22$) dan penyebut ($30$) sama-sama bilangan genap, langsung ambil separuh dari masing-masing angka di kepala:\n"
            "  $$22 \\div 2 = 11$$\n"
            "  $$30 \\div 2 = 15$$\n"
            "• **Bentuk Paling Sederhana:** $$\\frac{11}{15}$$\n\n"
            "### Kasus B: Operasi Pembagian $\\frac{22}{30} \\div 2$\n"
            "Jika maksudmu adalah membagi nilai pecahan tersebut dengan angka 2:\n"
            "• **Trik Kilat (Jika pembilang genap):** Cukup bagi angka atasnya dengan 2, penyebutnya tetap!\n"
            "  $$\\frac{22 \\div 2}{30} = \\frac{11}{30}$$\n"
            "• **Aturan Formal Pecahan:** Membagi dengan 2 sama dengan mengalikan $\\frac{1}{2}$:\n"
            "  $$\\frac{22}{30} \\times \\frac{1}{2} = \\frac{22}{60} = \\frac{11}{30}$$\n\n"
            "⚡ **Tips Cepat Ujian TKA:**\n"
            "Selalu cek apakah pembilang dan penyebut adalah bilangan genap. Jika genap, langsung bagi 2 tanpa ragu untuk menghemat waktu ujian!"
        )

    # Pertanyaan trik hitung cepat umum
    if is_math and any(k in msg_lower for k in ["ngitung cepat", "hitung cepat", "cara cepat hitung", "trik hitung", "mental math", "cara kilat hitung"]):
        return (
            "### ⚡ Trik Kilat Hitung Cepat untuk Ujian Matematika TKA:\n\n"
            "1. **Trik Perkalian 5:**\n"
            "   Bagi angkanya dengan 2, lalu kalikan 10 (atau tambah 0 di belakang).\n"
            "   • Contoh: $36 \\times 5 = (36 \\div 2) \\times 10 = 18 \\times 10 = 180$.\n\n"
            "2. **Trik Perkalian 11 (2 Digit):**\n"
            "   Buka digit pertama dan kedua, lalu selipkan hasil penjumlahannya di tengah.\n"
            "   • Contoh: $35 \\times 11 = 3\\,[3+5]\\,5 = 385$.\n\n"
            "3. **Trik Persentase Kilat:**\n"
            "   • $10\\%$ = Cukup geser koma 1 digit ke kiri (misal: $10\\%$ dari $450 = 45$).\n"
            "   • $1\\%$ = Geser koma 2 digit ke kiri ($1\\%$ dari $450 = 4,5$).\n"
            "   • $15\\%$ = Gabungkan $10\\% + 5\\%$ ($45 + 22,5 = 67,5$).\n\n"
            "4. **Trik Kuadrat Berakhiran 5:**\n"
            "   Kalikan angka depan dengan kakaknya (angka + 1), lalu tempelkan 25 di belakang.\n"
            "   • Contoh: $45^2 = (4 \\times 5)\\text{ lalu tempel } 25 = 2025$.\n\n"
            "⚡ **Tips Cepat:** Latih terus trik mental math ini agar kamu bisa menyelesaikan soal ujian TKA dalam hitungan detik!"
        )

    # =========================================================================
    # 3. MATEMATIKA DI LUAR TOPIK SOAL INI (OFF-TOPIC MATH) -> JAWAB + INGATKAN FOKUS
    # =========================================================================
    
    # 3A. KALKULUS (Turunan, Integral, Limit) - MATEMATIKA SAJA
    if is_math and any(k in msg_lower for k in ["kalkulus", "turunan", "integral", "diferensial", "differensial", "derivatif", "limit fungsi", "stasioner"]):
        reply = (
            "Halo! Pertanyaan seputar **Kalkulus** sangat berbobot! Mari kita bahas inti konsepnya:\n\n"
            "### 1. Turunan (Diferensial)\n"
            "• **Konsep:** Mengukur laju perubahan sesaat suatu fungsi atau kemiringan (gradien) kurva.\n"
            "• **Rumus Dasar Pangkat:**\n"
            "  $$f(x) = a \\cdot x^n \\implies f'(x) = a \\cdot n \\cdot x^{n-1}$$\n"
            "• **Contoh:** Turunan dari $f(x) = 4x^3$ adalah $f'(x) = 4 \\cdot 3 \\cdot x^2 = 12x^2$.\n\n"
            "### 2. Integral (Antiturunan)\n"
            "• **Konsep:** Kebalikan dari operasi turunan, sering dipakai untuk mencari fungsi asal atau menghitung luas daerah di bawah kurva.\n"
            "• **Rumus Dasar Tak Tentu:**\n"
            "  $$\\int a \\cdot x^n \\, dx = \\frac{a}{n+1} \\cdot x^{n+1} + C \\quad (n \\neq -1)$$\n"
            "• **Contoh:** $\\int 6x \\, dx = \\frac{6}{2}x^2 + C = 3x^2 + C$.\n\n"
            "### 3. Limit Fungsi\n"
            "• **Konsep:** Menentukan nilai yang didekati oleh fungsi saat nilai $x$ mendekati suatu titik acuan tertentu ($\\lim_{x \\to c} f(x)$).\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Topik Kalkulus ini adalah salah satu materi unggulan di matematika lanjut! Namun, untuk soal nomor {nomor} yang sedang kamu buka, "
            f"topik utamanya adalah **{active_topik}**. Agar persiapan ujian TKA kamu semakin matang dan tuntas satu per satu, "
            f"yuk setelah ini kita fokus kembali membedah soal nomor {nomor} ini ya!"
        )
        return reply

    # 3B. TRIGONOMETRI & PYTHAGORAS - MATEMATIKA SAJA
    if is_math and any(k in msg_lower for k in ["trigonometri", "sinus", "cosinus", "tangen", "sudut istimewa", "pythagoras", "pitagoras"]):
        reply = (
            "Halo! Mari kita review konsep kunci **Trigonometri**:\n\n"
            "### 1. Perbandingan Sudut Segitiga Siku-Siku (Sindemi, Cossami, Tandesa)\n"
            "• **$\\sin(\\theta)$:** $\\frac{\\text{Sisi Depan}}{\\text{Sisi Miring}}$ (Sindemi)\n"
            "• **$\\cos(\\theta)$:** $\\frac{\\text{Sisi Samping}}{\\text{Sisi Miring}}$ (Cossami)\n"
            "• **$\\tan(\\theta)$:** $\\frac{\\text{Sisi Depan}}{\\text{Sisi Samping}}$ (Tandesa)\n\n"
            "### 2. Teorema Pythagoras\n"
            "Pada segitiga siku-siku dengan sisi miring $c$:\n"
            "$$a^2 + b^2 = c^2$$\n"
            "• **Tripel Pythagoras Populer:** $(3, 4, 5)$, $(5, 12, 13)$, $(7, 24, 25)$, $(8, 15, 17)$.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Trigonometri ini sangat seru dipelajari! Tapi ingat ya, di soal nomor {nomor} ini kita sedang memelajari **{active_topik}**. "
            f"Yuk, setelah memahami ini, kita kembali menyelesaikan target soal nomor {nomor} agar belajarmu tetap terarah!"
        )
        return reply

    # 3C. MATRIKS & VEKTOR - MATEMATIKA SAJA
    if is_math and any(k in msg_lower for k in ["matriks", "determinan", "invers", "ordo", "vektor"]):
        reply = (
            "Halo! Berikut ringkasan konsep esensial **Matriks**:\n\n"
            "### 1. Determinan Matriks Ordo $2 \\times 2$\n"
            "Jika matriks $A = \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$, maka:\n"
            "$$\\det(A) = |A| = (a \\cdot d) - (b \\cdot c)$$\n\n"
            "### 2. Invers Matriks Ordo $2 \\times 2$\n"
            "$$A^{-1} = \\frac{1}{\\det(A)} \\begin{pmatrix} d & -b \\\\ -c & a \\end{pmatrix}$$\n"
            "*(Syarat memiliki invers: $\\det(A) \\neq 0$)*.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Materi Matriks sangat penting di jenjang SMK/SMA! Namun pada nomor {nomor} ini, fokus kita ada pada **{active_topik}**. "
            f"Mari kita tuntaskan pembahasan soal ini terlebih dahulu ya!"
        )
        return reply

    # 3D. ALJABAR, PERSAMAAN KUADRAT & SPLDV - MATEMATIKA SAJA
    if is_math and any(k in msg_lower for k in ["aljabar", "persamaan kuadrat", "rumus abc", "pemfaktoran", "spldv", "spltv"]):
        reply = (
            "Halo! Konsep dasar **Aljabar & Persamaan Kuadrat** sangat krusial:\n\n"
            "### 1. Bentuk Umum Persamaan Kuadrat\n"
            "$$ax^2 + bx + c = 0$$\n"
            "• **Rumus ABC:** Digunakan untuk mencari akar-akar persamaan saat sulit difaktorkan:\n"
            "  $$x_{1,2} = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$\n"
            "• **Diskriminan ($D = b^2 - 4ac$):** Jika $D > 0$ punya 2 akar nyata berlainan, jika $D = 0$ akar kembar, jika $D < 0$ tidak punya akar real.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Aljabar adalah fondasi utama matematika! Namun pada soal ini, kamu sedang berhadapan dengan materi **{active_topik}**. "
            f"Yuk kita prioritaskan menyelesaikan soal nomor {nomor} ini ya!"
        )
        return reply

    # 3E. BAHASA INGGRIS: GRAMMAR, VOCABULARY & READING
    if active_subject == "bahasa_inggris" and any(k in msg_lower for k in ["grammar", "tense", "tenses", "vocabulary", "vocab", "idiom", "passive voice", "part of speech", "synonym", "antonym", "reading", "comprehension", "skimming", "scanning"]):
        reply = (
            "Halo! Pertanyaan seputar **Bahasa Inggris** bagus sekali! Mari kita review intinya:\n\n"
            "### 1. Grammar: 16 Tenses Dasar\n"
            "• **Simple Present:** kebiasaan/fakta — *She studies every day.*\n"
            "• **Simple Past:** selesai di masa lalu — *She studied yesterday.*\n"
            "• **Present Perfect:** sudah selesai, efeknya terasa — *She has studied.*\n"
            "• **Simple Future:** rencana/prediksi — *She will study.*\n\n"
            "### 2. Reading Comprehension Strategy\n"
            "• **Skimming:** baca cepat untuk menangkap ide pokok (main idea).\n"
            "• **Scanning:** cari kata kunci spesifik (angka, nama, tanggal) langsung di teks.\n"
            "• **Context Clues:** tebak arti kosakata asing dari kalimat di sekitarnya.\n\n"
            "### 3. Vocabulary Building\n"
            "• Hafalkan kata dalam frasa/konteks kalimat, bukan kata soliter — jauh lebih mudah diingat saat ujian.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Materi Bahasa Inggris ini sering muncul di TKA! Namun untuk soal nomor {nomor} yang sedang kamu buka, "
            f"topik utamanya adalah **{active_topik}**. Yuk setelah ini kita fokus kembali membedah soal nomor {nomor} ini ya!"
        )
        return reply

    # 3F. EKONOMI: KONSEP PASAR & MAKRO
    if active_subject == "ekonomi" and any(k in msg_lower for k in ["inflasi", "supply", "demand", "penawaran", "permintaan", "elastisitas", "pasar", "moneter", "fiskal", "gdp", "pdb", "kurs", "macam-macam pasar", "kebutuhan", "kelangkaan"]):
        reply = (
            "Halo! Konsep **Ekonomi** ini fundamental sekali. Mari kita bahas intinya:\n\n"
            "### 1. Permintaan & Penawaran (Supply & Demand)\n"
            "• **Hukum Permintaan:** harga naik → jumlah diminta turun (kurva menurun).\n"
            "• **Hukum Penawaran:** harga naik → jumlah ditawarkan naik (kurva menaik).\n"
            "• **Titik Keseimbangan (equilibrium):** saat Qd = Qs.\n\n"
            "### 2. Inflasi\n"
            "• **Definisi:** kenaikan harga barang secara umum & terus-menerus dalam periode tertentu.\n"
            "• **Penyebab:** demand-pull (permintaan berlebih) dan cost-push (biaya produksi naik).\n\n"
            "### 3. Kelangkaan (Scarcity)\n"
            "• Fondasi semua teori ekonomi: kebutuhan manusia tak terbatas, sumber daya terbatas.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Materi Ekonomi ini wajib dikuasai untuk TKA! Namun pada soal nomor {nomor} ini, fokus kita ada pada **{active_topik}**. "
            f"Yuk kita tuntaskan pembahasan soal ini terlebih dahulu ya!"
        )
        return reply

    # 3G. KEWIRAUSAHAAN (PKWU): BISNIS, SWOT & MARKETING
    if active_subject == "kewirausahaan" and any(k in msg_lower for k in ["swot", "bisnis", "marketing", "pemasaran", "usaha", "wirausaha", "modal", "branding", "segmentasi", "4p", "produk kreatif", "business model", "bmc"]):
        reply = (
            "Halo! Topik **Kewirausahaan (PKWU)** ini sangat praktis! Mari kita review konsep kuncinya:\n\n"
            "### 1. Analisis SWOT\n"
            "• **S**trengths (kekuatan) & **W**eaknesses (kelemahan) → analisis dari DALAM perusahaan.\n"
            "• **O**pportunities (peluang) & **T**hreats (ancaman) → analisis dari LUAR perusahaan.\n\n"
            "### 2. Marketing Mix (4P)\n"
            "• **Product:** kualitas, desain, keunikan produk.\n"
            "• **Price:** strategi harga (murah, premium, kompetitif).\n"
            "• **Place:** lokasi & jalur distribusi penjualan.\n"
            "• **Promotion:** iklan, diskon, media sosial.\n\n"
            "### 3. Business Model Canvas (BMC)\n"
            "• Kerangka 9 blok untuk memetakan bisnis: dari *customer segment* hingga *cost structure*.\n\n"
            f"📌 **Catatan Tutor:**\n"
            f"Materi PKWU ini sering keluar di TKA SMK! Namun untuk soal nomor {nomor} yang sedang kamu buka, "
            f"topik utamanya adalah **{active_topik}**. Yuk setelah ini kita fokus kembali membedah soal nomor {nomor} ini ya!"
        )
        return reply

    # =========================================================================
    # 4. PENJELASAN SPESIFIK SESUAI SOAL AKTIF (CONTEXTUAL CBT ENGINE)
    # =========================================================================

    # 4A-pre. Konsep & Teori Kunci (Layer 3 — solusi spesifik soal)
    if any(k in msg_lower for k in ["konsep", "teori"]):
        if _l3 and _l3.get('concept_kunci'):
            res = f"### Konsep & Teori Kunci Soal Nomor {nomor} (dari solusi spesifik soal):\n\n"
            for c in _l3['concept_kunci']:
                res += f"• {c}\n"
            if (_l3.get('review') or {}).get('needs_manual_review'):
                res += _review_note
            return res
        return (
            f"Konsep kunci spesifik (Layer 3) untuk soal nomor {nomor} belum tersedia "
            "— sumber solusi aktif belum memuat soal ini."
        )

    # 4A. Simbol dan Glosarium — preferensi: glosarium spesifik dari Layer 3;
    # bila tidak ada, tampilkan formula kanonis (hanya yang MUNCUL pada soal ini).
    if any(k in msg_lower for k in ["∪", "∩", "simbol", "notasi", "lambang", "union", "irisan", "arti simbol"]):
        glos_l3 = (_l3 or {}).get('glossary') or []
        if glos_l3:
            res = f"### Notasi & Istilah pada Soal Nomor {nomor} (dari solusi spesifik soal):\n\n"
            for g in glos_l3:
                res += f"**{g.get('term', '')}** — {g.get('meaning', '')}\n\n"
            if (_l3.get('review') or {}).get('needs_manual_review'):
                res += _review_note
            return res
        formulas = (canon_ctx or {}).get('formulas') or []
        if formulas:
            res = "Berikut notasi matematis yang muncul pada soal ini (dari konteks kanonis):\n\n"
            for f in formulas:
                latex = f.get('latex', '')
                src = f.get('source', '')
                src_note = " (data-latex resmi situs)" if src == "official data-latex" else " (hasil transkripsi vision)"
                res += f"### ${latex}${src_note}\n"
                res += f"• Notasi ini adalah bagian dari soal nomor {nomor}. Untuk arti operasinya, lihat definisi yang diberikan pada pernyataan soal.\n\n"
            res += "Ada bagian notasi atau langkah lain yang ingin kamu tanyakan?"
            return res
        return (
            f"Soal nomor {nomor} ini tidak memiliki notasi/formula khusus yang tertranskripsi "
            "pada konteks kanonis."
            "\n\nKonteks lengkap soalnya:\n\n"
            f"{(canon_ctx or {}).get('soal_text', '(konteks soal tidak tersedia)')}"
        )

    # 4B. Alasan Mengapa / Kenapa Pengerjaannya Begitu (Layer 3 saja — tanpa konten lama)
    if any(k in msg_lower for k in ["kenapa", "mengapa", "dikurang", "alasan", "kok bisa"]):
        if _l3:
            res = (f"### Mengapa jawaban soal nomor {nomor} seperti itu?\n\n"
                   f"**Cara berpikir (dari solusi spesifik soal ini):**\n{_l3.get('reasoning', '')}\n\n"
                   f"**Mengapa kunci benar:**\n{_l3.get('why_correct', '')}")
            if (_l3.get('review') or {}).get('needs_manual_review'):
                res += _review_note
            return res
        return (
            f"### Mengapa jawaban soal nomor {nomor} seperti itu?\n\n"
            "Penjelasan alasan langkah demi langkah (Layer 3) untuk soal ini "
            "belum tersedia — sumber solusi aktif belum memuat soal ini.\n\n"
            "Sementara itu, ini konteks lengkap soalnya agar kita membahas soal yang sama:\n\n"
            f"{(canon_ctx or {}).get('soal_text', '(konteks soal tidak tersedia)')}"
        )

    # 4C. Permintaan Analogi Sederhana — pakai reasoning spesifik soal (Layer 3)
    if any(k in msg_lower for k in ["analogi", "perumpamaan", "gampang", "mudah", "contoh nyata"]):
        if _l3 and _l3.get('reasoning'):
            res = (f"Baik! Berikut cara berpikir penyelesaian soal nomor {nomor} "
                   "(dari solusi spesifik soal ini — silakan minta bagian mana pun "
                   "yang ingin dijelaskan ulang):\n\n" + _l3['reasoning'])
            if (_l3.get('review') or {}).get('needs_manual_review'):
                res += _review_note
            return res
        return (
            f"Tentu! Untuk menjelaskan soal nomor {nomor} ({active_topik}) dengan analogi sederhana, "
            "saya perlu penjelasan spesifik soal ini (Layer 3 hasil Claude) yang belum tersedia saat ini.\n\n"
            "Agar diskusi tetap pada soal yang sama, ini konteks lengkap soalnya:\n\n"
            f"{(canon_ctx or {}).get('soal_text', '(konteks soal tidak tersedia)')}"
        )

    # 4D. Langkah-Langkah Penyelesaian (HANYA langkah hasil Claude — Layer 3)
    if any(k in msg_lower for k in ["langkah", "cara pengerjaan", "tahapan", "cara kerja", "cara jawab"]):
        l3_steps = (_l3 or {}).get('steps') or []
        if l3_steps:
            res = f"### Langkah Demi Langkah Menyelesaikan Soal Nomor {nomor} (dari solusi spesifik soal):\n\n"
            for stp in l3_steps:
                res += f"**Langkah {stp.get('step', '')}: {stp.get('title', '')}**\n{stp.get('explanation', '')}\n\n"
            if (_l3.get('review') or {}).get('needs_manual_review'):
                res += _review_note
            return res
        # TIDAK ada fallback ke langkah generik lama — jujur: belum tersedia.
        return (
            f"Langkah penyelesaian (Layer 3) untuk soal nomor {nomor} belum tersedia — "
            "sumber solusi aktif belum memuat soal ini, dan langkah generik lama "
            "sengaja tidak dipakai karena bukan penjelasan spesifik soal ini.\n\n"
            f"Sementara itu, berikut konteks lengkap soalnya sebagai acuan bersama:\n\n"
            f"{(canon_ctx or {}).get('soal_text', '(konteks soal tidak tersedia)')}"
        )

    # 4E. Tips & Trik — hanya bila tips spesifik soal (Layer 3) tersedia
    if any(k in msg_lower for k in ["tips", "trik", "cepat", "kilat", "ujian"]):
        l3_tips = (_l3 or {}).get('tips') or []
        l3_mist = (_l3 or {}).get('common_mistakes') or []
        if l3_tips or l3_mist:
            res = f"### Tips & Jebakan untuk Soal Nomor {nomor} (dari solusi spesifik soal):\n\n"
            for t in l3_tips:
                res += f"• {t}\n"
            for m in l3_mist:
                res += f"⚠️ Jebakan umum: {m}\n"
            if (_l3.get('review') or {}).get('needs_manual_review'):
                res += _review_note
            return res
        return (
            f"Tips spesifik untuk soal nomor {nomor} (Layer 3 hasil Claude) belum tersedia.\n\n"
            "Tips generik per mapel sengaja tidak saya tampilkan agar tidak menyesatkan — "
            "tanyakan saja langkah, kunci, atau konteks visual soal ini."
        )

    # 4F. Kunci Jawaban (tampilan dari konteks kanonis bila ada)
    if any(k in msg_lower for k in ["kunci", "jawaban benar", "opsi benar"]):
        kunci_disp = (canon_ctx or {}).get('kunci_display') or format_kunci_display(q_data)
        return (
            f"Kunci jawaban yang tepat untuk soal nomor {nomor} ini adalah **{kunci_disp}**.\n\n"
            f"Silakan telaah pembahasannya di bagian bawah atau tanyakan langkah mana yang belum kamu pahami!"
        )

    # 4G. Pertanyaan tentang Gambar / Visual (prioritas: transkripsi kanonis)
    if any(k in msg_lower for k in ["gambar", "grafik", "diagram", "tabel", "chart", "kurva", "ilustrasi", "foto", "image"]):
        visual_text = (canon_ctx or {}).get('visual_text') or ''
        if visual_text and visual_text != "Soal ini tidak memiliki elemen visual.":
            return (
                f"### 🖼️ Deskripsi Gambar pada Soal Nomor {nomor} (konteks kanonis):\n\n"
                f"{visual_text}\n\n"
                f"Apakah ada bagian spesifik dari gambar ini yang ingin kamu tanyakan lebih detail?"
            )
        if visual_memory:
            return (
                f"### 🖼️ Deskripsi Gambar pada Soal Nomor {nomor}:\n\n"
                f"{visual_memory}\n\n"
                f"Apakah ada bagian spesifik dari gambar ini yang ingin kamu tanyakan lebih detail?"
            )
        return (
            f"Soal nomor {nomor} ini tidak memiliki gambar/diagram stimulus khusus. "
            f"Seluruh informasi yang dibutuhkan terdapat di dalam teks soal.\n\n"
            f"Ada hal lain yang ingin kamu tanyakan tentang materi **{active_topik}**?"
        )

    # 4H. Fallback Cerdas Kontekstual (Multi-Subject)
    # Konsep kunci lama TIDAK lagi ditampilkan sebagai konten — hanya status jujur.
    status_line = ''
    if canon_ctx:
        status_line = (
            f"\n\n📎 **Konteks soal kanonis sudah dimuat** (id `{canon_ctx['id']}`, tipe "
            f"{canon_ctx['type']}, status transkripsi {canon_ctx['transcription_status']}). "
            "Tanyakan langkah, kunci, gambar, atau bagian soal mana pun — saya membaca "
            "dari konteks lengkap soal ini."
        )
    if _l3 and _l3.get('concept_kunci'):
        status_line += ("\n\n🧠 **Konsep utama soal ini** (dari solusi spesifik): "
                        + "; ".join(_l3['concept_kunci'][:2]) + ".")
    return (
        f"Halo! Terkait soal nomor {nomor} dengan materi **{active_topik}**:\n\n"
        f"Sebagai tutor **{active_subject_name}** kamu, saya siap membantu kamu memahami soal ini. Kamu bisa tanyakan:\n"
        f"1. **Arti istilah atau notasi** yang muncul pada soal ini?\n"
        f"2. **Mengapa jawabannya seperti itu** (alasan logisnya)?\n"
        f"3. **Langkah penyelesaian** soal ini?\n"
        f"4. **Gambar/diagram/tabel** apa yang ada di soal ini?\n"
        f"{status_line}\n\n"
        f"Silakan ketik pertanyaan spesifikmu ya!"
    )

class AppRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Disable caching for html/js/css so frontend changes are always picked up
        clean = self.path.split('?', 1)[0].split('#', 1)[0].lower()
        if clean.endswith(('.html', '.js', '.css')):
            self.send_header('Cache-Control', 'no-cache, must-revalidate')
        super().end_headers()

    def translate_path(self, path):
        # Resolve image paths from Pusmendik stimuli HTML across all subject folders
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        if clean_path.startswith('/images/'):
            filename = os.path.basename(clean_path)
            # Search across all subject image directories
            search_dirs = [
                os.path.join(BASE_DIR, "data", "paket_1", "images"),
                os.path.join(BASE_DIR, "data", "paket_2", "images"),
                os.path.join(BASE_DIR, "data", "bahasa_inggris", "paket_1", "images"),
                os.path.join(BASE_DIR, "data", "bahasa_inggris", "paket_2", "images"),
                os.path.join(BASE_DIR, "data", "ekonomi", "paket_1", "images"),
                os.path.join(BASE_DIR, "data", "ekonomi", "paket_2", "images"),
                os.path.join(BASE_DIR, "data", "kewirausahaan", "paket_1", "images"),
                os.path.join(BASE_DIR, "data", "kewirausahaan", "paket_2", "images"),
            ]
            for d in search_dirs:
                cand = os.path.join(d, filename)
                if os.path.isfile(cand):
                    return cand
        return super().translate_path(path)

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
                return self._send_json(200, {
                    "status": "success",
                    "canonical_id": ctx["canonical_id"],
                    "provider": tutor_llm.active_provider_info(),
                    "conversation_id": conv["id"] if conv else None,
                    "summary": conv.get("summary") if conv else None,
                    "messages": [{"id": m["id"], "role": m["role"],
                                  "content": m["content"]} for m in messages],
                }, cookie_value=new_cookie)
            except Exception as e:
                return self._send_json(500, {"status": "error", "message": str(e)})
        return super().do_GET()

    def do_POST(self):
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
                request_id = payload.get('request_id') or None
                if not message:
                    return self._send_json(400, {"status": "error",
                                                 "message": "Pesan kosong."})
                ctx = resolve_tutor_context(subject, paket, nomor)
                if not ctx:
                    return self._send_json(404, {"status": "error",
                                                 "message": "Soal tidak ditemukan."})
                user_key, new_cookie = self._tutor_session()
                allowed, limit_msg = _check_user_rate_limit(user_key)
                if not allowed:
                    return self._send_json(429, {
                        "status": "rate_limited",
                        "error_kind": "rate_limit",
                        "retryable": True,
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
                try:
                    reply, meta = tutor_engine.generate_tutor_response(
                        ctx["canon_ctx"], ctx["solution"], ctx["official_answer"],
                        history_for_prompt, message, summary=conv.get("summary"),
                        subject_name=ctx["subject_name"])
                except tutor_llm.LLMError as e:
                    _refresh_tutor_summary(conv_id)
                    return self._send_json(502, {
                        "status": "llm_error", "error_kind": e.kind,
                        "retryable": True, "user_message_stored": True,
                        "conversation_id": conv_id,
                        "message": (f"Penjelasan dari AI belum berhasil ({e.kind}). "
                                    f"Pesanmu sudah tersimpan — coba kirim ulang."),
                    }, cookie_value=new_cookie)
                am, _ = tutor_store.add_message(
                    conv_id, 'assistant', reply,
                    request_id=(request_id + ':a') if request_id else None,
                    metadata={"intent": meta["intent"],
                              "provider": tutor_llm.active_provider_info()["provider"]})
                _refresh_tutor_summary(conv_id)
                return self._send_json(200, {
                    "status": "success", "reply": reply,
                    "conversation_id": conv_id, "message_id": am["id"],
                    "intent": meta["intent"],
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
