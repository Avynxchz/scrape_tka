# -*- coding: utf-8 -*-
"""legacy_tutor.py — Mesin AI Tutor heuristik berbasis aturan lama.

Modul ini dipertahankan murni untuk kompatibilitas ke belakang (backwards-compatibility)
dan fixture test. Frontend modern kini menggunakan modul tutor_engine + tutor_llm
melalui endpoint /api/tutor/chat.
"""


def format_kunci_display_legacy(q_data):
    kunci = q_data.get("kunci_jawaban", "-")
    if isinstance(kunci, list):
        if kunci and all(":" in str(x) for x in kunci):
            return ", ".join(f"{str(x).split(':', 1)[0]} ({str(x).split(':', 1)[1]})" for x in kunci)
        return ", ".join(str(x) for x in kunci)
    return str(kunci)


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
        "kewirausahaan": "Produk Kreatif & Kewirausahaan",
        "geografi": "Geografi"
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

    if any(k in msg_lower for k in ["langkah", "cara pengerjaan", "tahapan", "cara kerja", "cara jawab"]):
        l3_steps = (_l3 or {}).get('steps') or []
        if l3_steps:
            res = f"### Langkah Demi Langkah Menyelesaikan Soal Nomor {nomor} (dari solusi spesifik soal):\n\n"
            for stp in l3_steps:
                res += f"**Langkah {stp.get('step', '')}: {stp.get('title', '')}**\n{stp.get('explanation', '')}\n\n"
            if (_l3.get('review') or {}).get('needs_manual_review'):
                res += _review_note
            return res
        return (
            f"Langkah penyelesaian (Layer 3) untuk soal nomor {nomor} belum tersedia — "
            "sumber solusi aktif belum memuat soal ini, dan langkah generik lama "
            "sengaja tidak dipakai karena bukan penjelasan spesifik soal ini.\n\n"
            f"Sementara itu, berikut konteks lengkap soalnya sebagai acuan bersama:\n\n"
            f"{(canon_ctx or {}).get('soal_text', '(konteks soal tidak tersedia)')}"
        )

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

    if any(k in msg_lower for k in ["kunci", "jawaban benar", "opsi benar"]):
        kunci_disp = (canon_ctx or {}).get('kunci_display') or format_kunci_display_legacy(q_data)
        return (
            f"Kunci jawaban yang tepat untuk soal nomor {nomor} ini adalah **{kunci_disp}**.\n\n"
            f"Silakan telaah pembahasannya di bagian bawah atau tanyakan langkah mana yang belum kamu pahami!"
        )

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
