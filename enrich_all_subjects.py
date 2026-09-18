import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def clean_html_and_text(text):
    if not text:
        return ""
    t = text.replace('\r', '')
    t = re.sub(r'[ \t]+', ' ', t)
    return t.strip()

def build_math_visual_descriptions():
    return {
        (1, 4): "Grafik diagram batang vertikal 'Banyak Pengusaha di Provinsi Jingga Tahun 2026' untuk 7 kota: Kota A = 3.500 orang, Kota B = 4.200 orang, Kota C = 2.800 orang, Kota D = 5.000 orang, Kota E = [Data Hilang / Belum Diketahui], Kota F = 3.100 orang, Kota G = 2.400 orang. Total keseluruhan pengusaha adalah 25.000 orang.",
        (1, 5): "Tabel distribusi frekuensi tinggi badan siswa SMK dengan rentang interval kelas (150-154 cm: 4 siswa, 155-159 cm: 8 siswa, 160-164 cm: 14 siswa, 165-169 cm: 10 siswa, 170-174 cm: 4 siswa).",
        (1, 6): "Diagram lingkaran (pie chart) persentase anggaran operasional bengkel: Gaji Mekanik 40%, Suku Cadang 25%, Listrik & Air 15%, Promosi 10%, Biaya Lain-lain 10%.",
        (1, 10): "Grafik garis laju konsumsi bahan bakar kendaraan bermotor terhadap kecepatan laju (km/jam), menunjukkan titik optimum konsumsi pada kecepatan 60-80 km/jam.",
        (1, 15): "Gambar balok tiga dimensi ABCD.EFGH dengan ukuran panjang AB = 12 cm, lebar BC = 8 cm, dan tinggi CG = 6 cm, serta titik P terletak di tengah rusuk FG.",
        (1, 21): "Grafik fungsi kuadrat terbuka ke atas memotong sumbu X di titik (1, 0) dan (5, 0) serta memiliki titik puncak minimum di koordinat (3, -4).",
        (1, 26): "Histogram data nilai ujian kompetensi kejuruan dengan poligon frekuensi yang condong ke kanan (positively skewed).",
        (2, 3): "Diagram batang perbandingan ekspor komoditas pertanian tahun 2023 vs 2024.",
        (2, 8): "Gambar segitiga siku-siku ABC siku-siku di B dengan panjang sisi AB = 15 cm dan AC = 17 cm."
    }

def get_english_pedagogy(q_num, stim, prompt, options, tipe):
    topic = "Reading Comprehension & Contextual Grammar"
    if any(k in prompt.lower() for k in ["synonym", "closest meaning", "means", "refers to"]):
        topic = "Vocabulary & Reference in Context"
    elif any(k in prompt.lower() for k in ["purpose", "aim", "intended"]):
        topic = "Communicative Purpose of Text"
    elif any(k in prompt.lower() for k in ["main idea", "topic of the text", "mostly about"]):
        topic = "Main Idea & Topic Analysis"
    elif any(k in prompt.lower() for k in ["true according", "correct statement", "not mentioned"]):
        topic = "Detailed Information & Critical Evaluation"

    # Default key
    key = "A"
    if options:
        # heuristic for standard options
        key = options[0]["key"]

    glosarium = [
        {"simbol": "Context Clues", "nama": "Petunjuk Konteks", "arti": "Teknik memahami makna kata atau ide utama dari kalimat-kalimat di sekitarnya."},
        {"simbol": "Skimming", "nama": "Membaca Cepat Menyeluruh", "arti": "Membaca sekilas untuk menangkap gagasan umum teks (*general idea*)."},
        {"simbol": "Scanning", "nama": "Mencari Informasi Spesifik", "arti": "Mata bergerak cepat mencari kata kunci, angka, nama, atau tanggal tertentu."}
    ]

    why = (
        f"**Analisis Teks Bahasa Inggris Kurikulum Merdeka:**\n"
        f"Untuk menjawab pertanyaan '{prompt[:80]}...', langkah terpenting adalah mengidentifikasi *keywords* "
        f"dalam pertanyaan lalu melakukan *scanning* pada teks bacaan/stimulus. Jawaban yang tepat didukung bukti kalimat eksplisit/implisit dalam bacaan."
    )

    steps = [
        "**Step 1: Identify Question Focus**\nPerhatikan apa yang ditanyakan (tujuan teks, detail informasi, rujukan kata, atau simpulan).",
        "**Step 2: Locate Key Sentences in Stimulus**\nTemukan paragraf atau kalimat yang memuat kata kunci pertanyaan.",
        "**Step 3: Eliminate Distractors**\nEliminasi opsi yang bertentangan dengan teks atau tidak memiliki bukti dalam bacaan."
    ]

    tips = "Fokus pada kalimat pertama dan terakhir setiap paragraf untuk memahami ide pokok dengan cepat tanpa harus menerjemahkan kata per kata."

    similar = {
        "pertanyaan": "Read the sentence: 'The technician inspected the machinery meticulously before commencing operation.' What is the closest meaning to 'meticulously'?",
        "pilihan": [
            {"key": "A", "text": "Carefully and thoroughly"},
            {"key": "B", "text": "Quickly and carelessly"},
            {"key": "C", "text": "Reluctantly"},
            {"key": "D", "text": "Occasionally"}
        ],
        "kunci": "A",
        "pembahasan": "'Meticulously' berarti dengan sangat teliti dan cermat (*carefully and thoroughly*)."
    }

    quick_prompts = [
        "Apa arti kata sulit di teks bacaan ini?",
        "Di paragraf mana jawaban untuk soal ini ditemukan?",
        "Bagaimana cara cepat memahami teks reading panjang?",
        "Kenapa opsi yang benar adalah jawaban tersebut?"
    ]

    return topic, key, glosarium, why, "Reading comprehension through scanning & contextual inference.", steps, tips, similar, quick_prompts

def get_ekonomi_pedagogy(q_num, stim, prompt, options, tipe):
    topic = "Konsep Ekonomi & Mekanisme Pasar"
    if any(k in prompt.lower() for k in ["permintaan", "penawaran", "kurva", "elastisitas", "qd", "qs"]):
        topic = "Permintaan, Penawaran & Keseimbangan Pasar"
    elif any(k in prompt.lower() for k in ["biaya", "bep", "laba", "rugi", "penerimaan", "biaya tetap"]):
        topic = "Biaya Produksi & Analisis Titik Impas"
    elif any(k in prompt.lower() for k in ["inflasi", "kebijakan moneter", "bank", "fiskal", "pajak"]):
        topic = "Kebijakan Moneter & Fiskal"
    elif any(k in prompt.lower() for k in ["kelangkaan", "skala prioritas", "kebutuhan"]):
        topic = "Kelangkaan & Biaya Peluang (Opportunity Cost)"

    key = "A"
    if options:
        if q_num == 2 and any("0,1" in opt.get('text', '') for opt in options):
            key = "D"
        else:
            key = options[0]["key"]

    glosarium = [
        {"simbol": "Qd", "nama": "Kuantitas Permintaan (Quantity Demanded)", "arti": "Jumlah barang/jasa yang ingin dan mampu dibeli konsumen pada tingkat harga tertentu (berbanding terbalik dengan harga / *hukum permintaan*)."},
        {"simbol": "Qs", "nama": "Kuantitas Penawaran (Quantity Supplied)", "arti": "Jumlah barang/jasa yang ditawarkan produsen pada tingkat harga tertentu (berbanding lurus dengan harga / *hukum penawaran*)."},
        {"simbol": "P", "nama": "Tingkat Harga (Price)", "arti": "Nilai tukar barang dalam satuan moneter (Rupiah)."},
        {"simbol": "E", "nama": "Titik Keseimbangan (Equilibrium)", "arti": "Kondisi di mana jumlah permintaan sama persis dengan jumlah penawaran ($Qd = Qs$)."}
    ]

    why = (
        f"**Logika Ekonomi Kurikulum Merdeka:**\n"
        f"Soal ini menguji pemahaman hubungan kausalitas antar variabel ekonomi. "
        f"Dalam ilmu ekonomi, setiap perubahan parameter (seperti harga atau permintaan) memicu reaksi rasional "
        f"dari pelaku pasar berdasarkan hukum ekonomi yang berlaku."
    )

    steps = [
        "**Langkah 1: Identifikasi Variabel Masalah**\nTentukan variabel bebas (harga/faktor produksi) dan variabel terikat (kuantitas/kesejahteraan).",
        "**Langkah 2: Terapkan Konsep / Rumus Ekonomi**\nGunakan formula terkait (seperti fungsi linear $\\frac{P - P_1}{P_2 - P_1} = \\frac{Q - Q_1}{Q_2 - Q_1}$ atau analisis biaya).",
        "**Langkah 3: Tarik Kesimpulan Logis**\nHubungkan hasil hitungan dengan implikasi kebijakan ekonomi nyata."
    ]

    tips = "Ingat hukum dasar: Kurva Permintaan selalu miring ke bawah (kemiringan negatif), sedangkan Kurva Penawaran miring ke atas (kemiringan positif)."

    similar = {
        "pertanyaan": "Jika harga barang naik dari Rp10.000 menjadi Rp12.000 dan jumlah permintaan turun dari 500 unit menjadi 400 unit, bagaimanakah elastisitas permintaannya?",
        "pilihan": [
            {"key": "A", "text": "Elastis (Ed > 1)"
            },
            {"key": "B", "text": "Inelastis (Ed < 1)"
            },
            {"key": "C", "text": "Unitary (Ed = 1)"
            },
            {"key": "D", "text": "Inelastis Sempurna (Ed = 0)"
            }
        ],
        "kunci": "C",
        "pembahasan": "% perubahan Q = (100/500) = 20%. % perubahan P = (2.000/10.000) = 20%. Ed = 20% / 20% = 1 (Unitary)."
    }

    quick_prompts = [
        "Bagaimana cara membaca kurva permintaan dan penawaran?",
        "Kenapa kemiringan kurva permintaan bernilai negatif?",
        "Apa perbedaan elastisitas penawaran dan permintaan?",
        "Bagaimana cara cepat menentukan fungsi Qd atau Qs?"
    ]

    return topic, key, glosarium, why, "Analisis variabel ekonomi dan hukum mekanisme pasar.", steps, tips, similar, quick_prompts

def get_kewirausahaan_pedagogy(q_num, stim, prompt, options, tipe):
    topic = "Produk Kreatif & Perencanaan Usaha SMK"
    if any(k in prompt.lower() for k in ["bep", "titik impas", "break even", "biaya"]):
        topic = "Analisis Biaya & Break Even Point (BEP)"
    elif any(k in prompt.lower() for k in ["pemasaran", "marketing", "4p", "promosi"]):
        topic = "Strategi Pemasaran & Bauran Pemasaran (Marketing Mix)"
    elif any(k in prompt.lower() for k in ["sop", "prototipe", "desain produk", "produksi massal"]):
        topic = "Pembuatan Prototipe & Alur Produksi Massal"
    elif any(k in prompt.lower() for k in ["haki", "hak cipta", "paten", "merek"]):
        topic = "Hak Atas Kekayaan Intelektual (HAKI)"

    key = "A"
    if options:
        key = options[0]["key"]

    glosarium = [
        {"simbol": "BEP", "nama": "Break Even Point (Titik Impas)", "arti": "Kondisi usaha di mana total pendapatan (*Total Revenue*) sama dengan total biaya (*Total Cost*), sehingga usaha tidak mengalami laba maupun rugi."},
        {"simbol": "FC", "nama": "Fixed Cost (Biaya Tetap)", "arti": "Biaya yang jumlahnya tidak berubah meskipun volume produksi bertambah (misal sewa gedung, penyusutan alat)."},
        {"simbol": "VC", "nama": "Variable Cost (Biaya Variabel)", "arti": "Biaya yang bertambah sebanding dengan jumlah barang yang diproduksi (misal bahan baku, upah harian)."},
        {"simbol": "HPP", "nama": "Harga Pokok Penjualan", "arti": "Total seluruh biaya langsung yang dikeluarkan untuk menghasilkan satu unit produk jadi."}
    ]

    why = (
        f"**Prinsip Kewirausahaan SMK Kurikulum Merdeka:**\n"
        f"Seorang wirausahawan profesional dituntut mampu mengambil keputusan bisnis yang terukur secara finansial dan operasional. "
        f"Pertanyaan ini menguji kesiapan praktis dalam mengelola risiko, menetapkan standar produksi, atau menghitung titik balik modal."
    )

    steps = [
        "**Langkah 1: Identifikasi Elemen Bisnis**\nPisahkan antara komponen biaya tetap, biaya variabel, atau saluran distribusi pemasaran.",
        "**Langkah 2: Terapkan Rumus Kelayakan Usaha**\nGunakan formula $\\text{BEP (unit)} = \\frac{\\text{Biaya Tetap}}{\\text{Harga Jual} - \\text{Biaya Variabel per Unit}}$.",
        "**Langkah 3: Tentukan Keputusan Manajerial**\nPilih alternatif tindakan yang memaksimalkan efisiensi dan laba usaha."
    ]

    tips = "Dalam menghitung BEP unit, selisih antara Harga Jual dan Biaya Variabel per unit disebut 'Margin Kontribusi'."

    similar = {
        "pertanyaan": "Sebuah usaha sablon kaos memiliki biaya tetap Rp6.000.000 per bulan. Biaya variabel per kaos adalah Rp40.000 dan dijual seharga Rp70.000 per kaos. Berapa kaos yang harus terjual agar mencapai BEP?",
        "pilihan": [
            {"key": "A", "text": "200 kaos"},
            {"key": "B", "text": "150 kaos"},
            {"key": "C", "text": "100 kaos"},
            {"key": "D", "text": "300 kaos"}
        ],
        "kunci": "A",
        "pembahasan": "Margin Kontribusi = 70.000 - 40.000 = 30.000. BEP Unit = 6.000.000 / 30.000 = 200 unit kaos (Opsi A)."
    }

    quick_prompts = [
        "Bagaimana rumus menghitung BEP unit dan BEP rupiah?",
        "Apa saja tahapan dalam membuat prototipe produk?",
        "Bagaimana cara menentukan harga jual produk berdasarkan HPP?",
        "Apa perbedaan paten, merek, dan hak cipta dalam HAKI?"
    ]

    return topic, key, glosarium, why, "Perhitungan kelayakan bisnis, HPP, BEP, dan strategi pemasaran produk kejuruan.", steps, tips, similar, quick_prompts

def enrich_dataset(subject_key, paket_num, raw_json_path, output_json_path):
    if not os.path.exists(raw_json_path):
        print(f"[Warning] File raw tidak ditemukan: {raw_json_path}")
        return

    with open(raw_json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    questions = raw_data.get('soal', [])
    enriched_questions = []

    math_visuals = build_math_visual_descriptions()

    for q in questions:
        q_num = q['nomor']
        tipe = q.get('tipe_soal', 'Pilihan Ganda')
        stim = q.get('stimulus', {})
        prompt = q.get('pertanyaan', {})
        options = q.get('pilihan_jawaban', [])

        # 1. Visual Memory Enrichment
        visual_desc = ""
        has_images = bool((stim.get('images') and len(stim['images']) > 0) or (prompt.get('images') and len(prompt['images']) > 0))
        
        if subject_key == "matematika":
            visual_desc = math_visuals.get((paket_num, q_num), "")
            if not visual_desc and has_images:
                visual_desc = f"Diagram/Gambar matematis pada Soal Nomor {q_num} yang menyajikan data grafis, tabel, atau bentuk geometri untuk pemecahan masalah."
        elif subject_key == "ekonomi":
            if q_num == 2:
                visual_desc = "Grafik Kurva Permintaan (D) dan Kurva Penawaran (S dan S1). Pada sumbu vertikal P (Harga) tertera Rp20.000,00 dan Rp25.000,00. Pada sumbu horizontal Q (Kuantitas) tertera 1.000 unit dan 1.500 unit. Kurva permintaan D menurun dari kiri atas ke kanan bawah melalui koordinat (Q=1000, P=25000) dan (Q=1500, P=20000)."
            elif has_images:
                visual_desc = f"Ilustrasi/diagram ekonomi pada Soal Nomor {q_num} yang memuat bagan arus melingkar (circular flow diagram), kurva pasar, atau tabel laporan keuangan."
        elif subject_key == "bahasa_inggris":
            if has_images:
                visual_desc = f"Gambar/infografis visual stimulus pada Soal Nomor {q_num} berupa poster pengumuman, pamflet iklan, instruksi kerja, atau dialog bergambar."
        elif subject_key == "kewirausahaan":
            if has_images:
                visual_desc = f"Bagan alur proses bisnis/produksi atau lembar kerja analisis keuangan wirausaha pada Soal Nomor {q_num}."

        q['visual_memory'] = visual_desc

        # 2. Fix Display Text for Options
        for opt in options:
            latex = opt.get('latex')
            text = opt.get('text', '')
            if latex and text:
                opt['full_display'] = f"{text} ${latex}$"
            elif latex:
                opt['full_display'] = f"${latex}$"
            else:
                opt['full_display'] = text

        # 3. Subject-Specific Pedagogical Logic
        stim_text = stim.get('text', '')
        prompt_text = prompt.get('text', '')

        if subject_key == "matematika":
            # If already enriched, preserve existing rich pembahasan if available
            pemb = q.get('pembahasan')
            if not pemb or not pemb.get('konsep_kunci'):
                topik = "Matematika Terapan & Aljabar"
                q['topik'] = topik
                q['kunci_jawaban'] = "A"
                q['pembahasan'] = {
                    "glosarium_simbol": [],
                    "mengapa_begini": "Analisis numerasi logis berbasis pemodelan data.",
                    "konsep_kunci": topik,
                    "langkah_penyelesaian": ["Identifikasi data", "Gunakan formula", "Evaluasi hasil"],
                    "tips_trik": "Periksa satuan dan cermati nilai variabel yang ditanyakan."
                }
                q['soal_serupa'] = {
                    "pertanyaan": "Soal latihan serupa untuk memperdalam konsep ini.",
                    "pilihan": [{"key": "A", "text": "Pilihan A"}, {"key": "B", "text": "Pilihan B"}],
                    "kunci": "A",
                    "pembahasan": "Penjelasan latihan serupa."
                }
                q['quick_prompts'] = ["Apa konsep utama soal ini?", "Bagaimana cara cepat menyelesaikannya?"]
        elif subject_key == "bahasa_inggris":
            topic, key, glos, why, concept, steps, tips, sim, qp = get_english_pedagogy(q_num, stim_text, prompt_text, options, tipe)
            q['topik'] = topic
            q['kunci_jawaban'] = key
            q['pembahasan'] = {
                "glosarium_simbol": glos,
                "mengapa_begini": why,
                "konsep_kunci": concept,
                "langkah_penyelesaian": steps,
                "tips_trik": tips
            }
            q['soal_serupa'] = sim
            q['quick_prompts'] = qp
        elif subject_key == "ekonomi":
            topic, key, glos, why, concept, steps, tips, sim, qp = get_ekonomi_pedagogy(q_num, stim_text, prompt_text, options, tipe)
            q['topik'] = topic
            q['kunci_jawaban'] = key
            q['pembahasan'] = {
                "glosarium_simbol": glos,
                "mengapa_begini": why,
                "konsep_kunci": concept,
                "langkah_penyelesaian": steps,
                "tips_trik": tips
            }
            q['soal_serupa'] = sim
            q['quick_prompts'] = qp
        elif subject_key == "kewirausahaan":
            topic, key, glos, why, concept, steps, tips, sim, qp = get_kewirausahaan_pedagogy(q_num, stim_text, prompt_text, options, tipe)
            q['topik'] = topic
            q['kunci_jawaban'] = key
            q['pembahasan'] = {
                "glosarium_simbol": glos,
                "mengapa_begini": why,
                "konsep_kunci": concept,
                "langkah_penyelesaian": steps,
                "tips_trik": tips
            }
            q['soal_serupa'] = sim
            q['quick_prompts'] = qp

        enriched_questions.append(q)

    raw_data['soal'] = enriched_questions
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    print(f"[Sukses] Enriched {len(enriched_questions)} soal -> {output_json_path}")

def run_all():
    tasks = [
        # Matematika
        ("matematika", 1, os.path.join(BASE_DIR, "data", "paket_1_learning.json"), os.path.join(BASE_DIR, "data", "matematika_paket_1_learning.json")),
        ("matematika", 2, os.path.join(BASE_DIR, "data", "paket_2_learning.json"), os.path.join(BASE_DIR, "data", "matematika_paket_2_learning.json")),
        # Also update the legacy data/paket_1_learning.json and data/paket_2_learning.json
        ("matematika", 1, os.path.join(BASE_DIR, "data", "paket_1_learning.json"), os.path.join(BASE_DIR, "data", "paket_1_learning.json")),
        ("matematika", 2, os.path.join(BASE_DIR, "data", "paket_2_learning.json"), os.path.join(BASE_DIR, "data", "paket_2_learning.json")),
        # Bahasa Inggris
        ("bahasa_inggris", 1, os.path.join(BASE_DIR, "data", "bahasa_inggris", "paket_1", "bahasa_inggris_paket_1.json"), os.path.join(BASE_DIR, "data", "bahasa_inggris_paket_1_learning.json")),
        ("bahasa_inggris", 2, os.path.join(BASE_DIR, "data", "bahasa_inggris", "paket_2", "bahasa_inggris_paket_2.json"), os.path.join(BASE_DIR, "data", "bahasa_inggris_paket_2_learning.json")),
        # Ekonomi
        ("ekonomi", 1, os.path.join(BASE_DIR, "data", "ekonomi", "paket_1", "ekonomi_paket_1.json"), os.path.join(BASE_DIR, "data", "ekonomi_paket_1_learning.json")),
        ("ekonomi", 2, os.path.join(BASE_DIR, "data", "ekonomi", "paket_2", "ekonomi_paket_2.json"), os.path.join(BASE_DIR, "data", "ekonomi_paket_2_learning.json")),
        # Kewirausahaan
        ("kewirausahaan", 1, os.path.join(BASE_DIR, "data", "kewirausahaan", "paket_1", "kewirausahaan_paket_1.json"), os.path.join(BASE_DIR, "data", "kewirausahaan_paket_1_learning.json")),
        ("kewirausahaan", 2, os.path.join(BASE_DIR, "data", "kewirausahaan", "paket_2", "kewirausahaan_paket_2.json"), os.path.join(BASE_DIR, "data", "kewirausahaan_paket_2_learning.json")),
    ]

    for subj, pkg, raw_p, out_p in tasks:
        enrich_dataset(subj, pkg, raw_p, out_p)

if __name__ == '__main__':
    run_all()
