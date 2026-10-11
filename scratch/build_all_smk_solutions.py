# -*- coding: utf-8 -*-
"""scratch/build_all_smk_solutions.py
Menghasilkan solusi 5 Pilar (Layer 3) dan Soal Serupa untuk 5 mapel SMK,
mendaftarkannya ke registry.json, dan menyuntikkannya ke file *_learning.json.
"""
import os
import sys
import json

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA_DEV"
sys.path.insert(0, BASE_DIR)
import solution_loader

DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
REG_PATH = os.path.join(SOL_DIR, "registry.json")
os.makedirs(SOL_DIR, exist_ok=True)

# 1. TEKNIK MESIN
TEKNIK_MESIN_SOLUTIONS = {
    "package": 1,
    "subject": "Teknik Mesin",
    "slug": "teknik_mesin_paket_1",
    "solutions": [
        {
            "question_number": 1,
            "question_id": "tms_p1_q01",
            "question_title": "Keselamatan Kerja Pengoperasian Mesin Bubut",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["K3 Pemesinan", "Mesin Bubut", "Potensi Bahaya APD"],
            "concept_kunci": ["Keselamatan Kerja Mesin Bubut", "Bahaya Bahu Terlilit Spindel"],
            "glossary": [
                {"term": "Mesin Bubut", "meaning": "Mesin perkakas yang memutar benda kerja untuk pemotongan silindris, ulir, maupun perataan muka."},
                {"term": "Spindel", "meaning": "Poros utama mesin bubut yang berputar membawa cekam pencekam benda kerja."}
            ],
            "diketahui": "• Situasi bengkel pemesinan: seorang siswa mengoperasikan mesin bubut memakai sarung tangan longgar\n• Di sekitar mesin terdapat serpihan logam (tatal) yang belum dibersihkan\n• Siswa lain sudah memakai kacamata pelindung dan sepatu keselamatan",
            "ditanyakan": "Potensi bahaya yang paling berisiko menyebabkan kecelakaan kerja fatal pada situasi bengkel tersebut.",
            "reasoning": "Pada mesin perkakas dengan bagian berputar kencang seperti mesin bubut, penggunaan sarung tangan—khususnya yang longgar—dilarang keras oleh standar K3. Bagian kain sarung tangan dapat dengan mudah tersangkut cekam (chuck) atau tatal berputar, yang seketika menarik jari, tangan, dan lengan operator ke putaran spindel berdaya tinggi, memicu kecelakaan kerja fatal berupa fraktur hingga amputasi.",
            "steps": [
                {
                    "step": 1,
                    "title": "Analisis Mekanisme Bahaya Komponen Mesin Berputar",
                    "explanation": "Mesin bubut bekerja dengan memutar benda kerja pada kecepatan ratusan hingga ribuan rpm. Benda lentur atau longgar di dekat poros putar memiliki risiko mekanis tertinggi berupa lilitan (entanglement)."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Tingkat Keparahan Risiko (Risk Severity)",
                    "explanation": "Serpihan logam belum dibersihkan berisiko menimbulkan luka gores atau terpeleset, namun penggunaan sarung tangan longgar pada bagian berputar memiliki tingkat risiko fatal/kritis karena dapat merenggut nyawa atau mematahkan lengan operator."
                },
                {
                    "step": 3,
                    "title": "Konfirmasi Standar Operasional Prosedur (SOP) K3",
                    "explanation": "SOP bengkel pemesinan melarang keras pemakaian sarung tangan kain, jam tangan, pakaian gombrang, atau rambut terurai saat mengoperasikan mesin bubut."
                }
            ],
            "why_correct": "Opsi C benar karena pengoperasian mesin bubut menggunakan sarung tangan longgar berpotensi fatal tersangkut putaran cekam spindel dan menarik tubuh operator ke putaran mesin.",
            "tips": ["Aturan emas bengkel bubut: jangan pernah memakai sarung tangan kain di dekat benda kerja atau spindel yang sedang berputar!"],
            "common_mistakes": ["Terkecoh memilih serpihan logam (Opsi B) yang memang berbahaya, namun tingkat keparahannya jauh di bawah risiko lilitan fatal sarung tangan."],
            "official_answer": {"format": "single", "correct": ["C"]},
            "soal_serupa": {
                "pertanyaan": "Saat mengoperasikan mesin frais (milling machine), seorang praktikan mengenakan jaket bertali panjang dan jam tangan logam. Bahaya paling kritis yang dapat terjadi adalah...",
                "pilihan": [
                    {"key": "A", "text": "Arbor pisau frais menjadi cepat tumpul."},
                    {"key": "B", "text": "Tali jaket dan jam tangan tersangkut putaran arbor pisau frais dan menarik tubuh ke meja mesin."},
                    {"key": "C", "text": "Aliran cairan pendingin (coolant) tersumbat oleh tali jaket."},
                    {"key": "D", "text": "Motor listrik mengalami kelebihan beban (overload)."}
                ],
                "kunci": "B",
                "pembahasan": "Bagian pakaian dan aksesoris longgar sangat rentan terlilit komponen mesin berputar kencang."
            }
        },
        {
            "question_number": 2,
            "question_id": "tms_p1_q02",
            "question_title": "Prosedur Pra-Operasional Pembubutan Aman",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["SOP Pembubutan", "K3 Mesin Bubut", "Checklist Operasional"],
            "concept_kunci": ["Pelepasan Kunci Cekam", "APD Kacamata", "Kebersihan Mesin", "Penyetelan Kecepatan"],
            "glossary": [
                {"term": "Kunci Cekam (Chuck Key)", "meaning": "Kunci T khusus untuk mengencangkan rahang cekam pada mesin bubut."},
                {"term": "Kecepatan Putaran (RPM)", "meaning": "Frekuensi putaran poros spindel per menit yang disesuaikan dengan diameter benda kerja dan bahan pahat."}
            ],
            "diketahui": "• Kondisi sebelum proses pembubutan:\n  1. Kunci cekam masih terpasang pada cekam mesin\n  2. Siswa belum menggunakan kacamata pelindung\n  3. Benda kerja sudah terpasang pada cekam\n  4. Serpihan logam dari pekerjaan sebelumnya masih berada di sekitar mesin\n  5. Pengaturan kecepatan mesin belum diperiksa",
            "ditanyakan": "Tindakan yang harus dilakukan siswa sebelum menghidupkan mesin bubut (Pilihan Ganda Kompleks).",
            "reasoning": "Sebelum menyalakan daya mesin bubut, operator wajib: (1) mencabut kunci cekam agar tidak terlempar menjadi proyektil maut saat mesin berputar, (2) memakai kacamata pelindung untuk mencegah tatal panas mengenai mata, (3) membersihkan serpihan logam agar tidak mengganjal eretan, dan (4) memeriksa pengaturan kecepatan putar sesuai diameter benda kerja.",
            "steps": [
                {
                    "step": 1,
                    "title": "Evaluasi Bahaya Kunci Cekam Menancap",
                    "explanation": "Kunci cekam yang tertinggal pada chuck akan terlempar dengan energi kinetik tinggi saat mesin hidup. Tindakan wajib: lepaskan kunci cekam seketika (Opsi A benar)."
                },
                {
                    "step": 2,
                    "title": "Verifikasi Perlindungan Diri dan Area Kerja",
                    "explanation": "Operator wajib mengenakan kacamata keselamatan (Opsi B benar) serta membersihkan serpihan logam di meja mesin sebelum memulai pembubutan (Opsi D benar)."
                },
                {
                    "step": 3,
                    "title": "Penyetelan Parameter Pemotongan",
                    "explanation": "Kecepatan potong ($C_s$) harus disesuaikan dengan rumus putaran $n = \\frac{1000 \\cdot C_s}{\\pi \\cdot d}$, sehingga kecepatan mesin harus diperiksa dan diatur terlebih dahulu (Opsi E benar)."
                }
            ],
            "why_correct": "Pernyataan A, B, D, dan E benar karena keempat tindakan tersebut merupakan prosedur standar operasional (SOP) pra-pembubutan guna mencegah lontaran proyektil, melindungi mata, menjaga kebersihan area geser bed mesin, serta memastikan kecepatan putar tepat.",
            "tips": ["Selalu biasakan tangan kiri memegang kunci chuck dan tangan kanan melepaskannya sebelum tangan beralih ke tombol ON."],
            "common_mistakes": ["Mengabaikan pelepasan kunci cekam atau beranggapan kunci cekam akan jatuh sendiri dengan aman saat mesin hidup."],
            "official_answer": {"format": "multiple", "correct": ["A", "B", "D", "E"]},
            "soal_serupa": {
                "pertanyaan": "Sebelum menjalankan mesin gerinda silindris, langkah keselamatan kerja awal yang wajib diperiksa operator adalah...",
                "pilihan": [
                    {"key": "A", "text": "Memeriksa kekencangan batu gerinda, menyetel pelindung kaca, dan menggunakan kacamata keselamatan."},
                    {"key": "B", "text": "Langsung menyentuhkan benda kerja ke roda gerinda saat sakelar dinyalakan."},
                    {"key": "C", "text": "Mematikan cairan pendingin (coolant) selama 10 menit pertama."},
                    {"key": "D", "text": "Membuka seluruh tutup pelindung roda gerinda agar pandangan lebih jelas."}
                ],
                "kunci": "A",
                "pembahasan": "Pengecekan fisik batu gerinda, penutup pelindung, dan pemakaian kacamata pelindung adalah syarat mutlak keselamatan operasional penggerindaan."
            }
        },
        {
            "question_number": 3,
            "question_id": "tms_p1_q03",
            "question_title": "Penanggulangan Kebakaran Bengkel Pemesinan (APAR)",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Tanggap Darurat", "K3 Pemadam Kebakaran", "APAR Dry Powder"],
            "concept_kunci": ["Kebakaran Listrik & Logam", "APAR Serbuk Kimia Kering"],
            "glossary": [
                {"term": "APAR", "meaning": "Alat Pemadam Api Ringan berupa tabung portabel bertekanan untuk memadamkan api tahap awal."},
                {"term": "Dry Powder", "meaning": "Bahan pemadam serbuk kimia kering (monoamonium fosfat) yang efektif memadamkan kebakaran kelas A, B, dan C."}
            ],
            "diketahui": "• Terjadi percikan api dari panel motor listrik mesin bubut di bengkel\n• Api mulai membesar di dekat saluran pendingin dan kabel panel kontrol",
            "ditanyakan": "Langkah pertama yang paling tepat dan aman dalam memadamkan kobaran api tersebut.",
            "reasoning": "Kebakaran yang melibatkan instalasi kelistrikan (Kelas C) dan cairan pelumas/minyak pendingin (Kelas B) tidak boleh disiram menggunakan air karena air menghantarkan arus listrik (risiko tersengat) dan dapat menyebarkan minyak yang terbakar. Prosedur yang benar adalah menggunakan APAR jenis serbuk kimia kering (dry chemical powder) atau CO2 yang tidak menghantarkan listrik serta mampu memutus suplai oksigen.",
            "steps": [
                {
                    "step": 1,
                    "title": "Klasifikasi Kebakaran Bengkel",
                    "explanation": "Kebakaran pada panel motor listrik merupakan kelas C (kelistrikan bertegangan) bercampur pelumas kelas B."
                },
                {
                    "step": 2,
                    "title": "Pemilihan Media Pemadam yang Tepat",
                    "explanation": "Penggunaan air dilarang keras. Media pemadam yang wajib digunakan adalah APAR Dry Chemical Powder atau Karbon Dioksida ($CO_2$)."
                },
                {
                    "step": 3,
                    "title": "Prosedur Pemadaman PASS",
                    "explanation": "Ambil APAR jenis dry chemical powder terdekat, cabut pin pengaman (Pull), arahkan corong ke pangkal api (Aim), tekan tuas (Squeeze), dan sapukan merata (Sweep)."
                }
            ],
            "why_correct": "Opsi D benar karena APAR jenis dry powder aman digunakan untuk memadamkan api yang melibatkan peralatan listrik bertegangan dan cairan pendingin tanpa risiko sengatan listrik bagi operator.",
            "tips": ["Ingat teknik PASS (Pull, Aim, Squeeze, Sweep) saat mengoperasikan tabung APAR di bengkel."],
            "common_mistakes": ["Menyiram api dengan air pada kebakaran peralatan listrik yang sedang terhubung ke sumber daya."],
            "official_answer": {"format": "single", "correct": ["D"]},
            "soal_serupa": {
                "pertanyaan": "Ketika oli pelumas hidrolik pada mesin pres panas tumpah dan menyala di dekat instalasi listrik, alat pemadam yang paling tepat digunakan adalah...",
                "pilihan": [
                    {"key": "A", "text": "Ember berisi air bersih."},
                    {"key": "B", "text": "APAR serbuk kimia kering (dry powder) atau CO2."},
                    {"key": "C", "text": "Kain lap basah berukuran kecil."},
                    {"key": "D", "text": "Kipas angin bertenaga tinggi untuk meniup api."}
                ],
                "kunci": "B",
                "pembahasan": "Kebakaran minyak (Kelas B) dan kelistrikan (Kelas C) harus dipadamkan dengan APAR serbuk kimia atau gas CO2 untuk mencegah konduksi listrik dan penyebaran api."
            }
        },
        {
            "question_number": 4,
            "question_id": "tms_p1_q04",
            "question_title": "Sistem Toleransi dan Suaian Poros-Lubang",
            "difficulty": "Sulit",
            "estimated_time_seconds": 120,
            "concept_tags": ["Metrologi Industri", "Suaian Pasak/Paksa", "Toleransi ISO"],
            "concept_kunci": ["Suaian Sesak (Interference Fit)", "Sistem Basis Lubang H7", "Penyimpangan Poros p6/s6"],
            "glossary": [
                {"term": "Suaian Sesak (Interference Fit)", "meaning": "Suaian di mana ukuran poros selalu lebih besar daripada ukuran lubang sebelum dirakit."},
                {"term": "Basis Lubang (H)", "meaning": "Sistem standar di mana penyimpangan bawah lubang adalah nol ($EI = 0$)."}
            ],
            "diketahui": "• Komponen pasangan roda gigi dengan poros transmisi memerlukan suaian sesak/paksa (interference fit)\n• Standar toleransi sistem ISO berbasis lubang dasar",
            "ditanyakan": "Pernyataan yang benar mengenai penentuan toleransi lubang dan poros untuk suaian tersebut (Pilihan Ganda Kompleks).",
            "reasoning": "Dalam sistem basis lubang (hole basis system), lubang standar ditetapkan dengan simbol huruf kapital $H$, umumnya kelas kualitas $H7$ (penyimpangan bawah = 0). Untuk menghasilkan suaian sesak (interference fit) di mana poros tidak boleh berputar relatif terhadap lubang tanpa pasak, daerah toleransi poros harus berada di atas lubang, yang dilambangkan dengan huruf kecil seperti $p6, r6,$ atau $s6$.",
            "steps": [
                {
                    "step": 1,
                    "title": "Analisis Sistem Basis Lubang ISO",
                    "explanation": "Pada sistem basis lubang, ukuran lubang menggunakan toleransi standar kelas $H7$. Hal ini mempermudah proses manufaktur karena reamer/mandrel lubang berukuran standar (Opsi A benar)."
                },
                {
                    "step": 2,
                    "title": "Penentuan Tingkat Suaian Poros",
                    "explanation": "Huruf toleransi poros dari $a$ hingga $h$ menghasilkan suaian longgar, $j$ hingga $n$ suaian transisi, dan $p$ hingga $z$ menghasilkan suaian sesak/paksa. Oleh karena itu, ukuran poros menggunakan kelas $p6$ atau $s6$ (Opsi B benar)."
                }
            ],
            "why_correct": "Pernyataan A dan B benar karena dalam sistem basis lubang standar ISO, lubang menggunakan toleransi H7 dan poros menggunakan daerah toleransi p6 atau s6 untuk menjamin terjadinya suaian sesak (interference fit).",
            "tips": ["Ingat urutan huruf ISO suaian poros: a-h (longgar), j-n (pas/transisi), p-z (sesak)."],
            "common_mistakes": ["Memilih suaian longgar (g6 atau f7) untuk komponen yang membutuhkan ikatan kaku tanpa slip seperti roda gigi tetap."],
            "official_answer": {"format": "multiple", "correct": ["A", "B"]},
            "soal_serupa": {
                "pertanyaan": "Pada perakitan bantalan gelinding (bearing) pada poros pompa yang harus dapat dilepas saat perawatan (suaian pas/transisi), toleransi poros yang tepat pada sistem lubang H7 adalah...",
                "pilihan": [
                    {"key": "A", "text": "k6 atau m6"},
                    {"key": "B", "text": "s6 atau t6"},
                    {"key": "C", "text": "c11 atau d10"},
                    {"key": "D", "text": "h7 atau h6 saja"}
                ],
                "kunci": "A",
                "pembahasan": "Suaian transisi (antara pas dan sedikit sesak) pada sistem H7 menggunakan toleransi poros daerah j6, k6, atau m6."
            }
        },
        {
            "question_number": 5,
            "question_id": "tms_p1_q05",
            "question_title": "Perlakuan Panas dan Pengerasan Permukaan Logam",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Metalurgi Fisik", "Heat Treatment", "Case Hardening / Karburasi"],
            "concept_kunci": ["Pengerasan Permukaan", "Ketangguhan Inti Baja"],
            "glossary": [
                {"term": "Karburasi (Carburizing)", "meaning": "Proses penambahan unsur karbon pada permukaan baja karbon rendah pada suhu austenit."},
                {"term": "Case Hardening", "meaning": "Perlakuan panas untuk menghasilkan lapisan kulit yang sangat keras namun intinya tetap ulet/tangguh."}
            ],
            "diketahui": "• Poros roda gigi transmisi mobil menerima gaya gesek terus-menerus pada gigi dan beban kejut puntir pada intinya\n• Diterapkan perlakuan panas pengerasan permukaan (case hardening)",
            "ditanyakan": "Tujuan utama diterapkannya proses pengerasan permukaan tersebut.",
            "reasoning": "Roda gigi dan poros transmisi memerlukan sifat mekanik ganda yang bertolak belakang: permukaan kontak gigi harus sangat keras dan tahan terhadap keausan akibat gesekan roda gigi lain, sementara inti poros harus tetap liat dan tangguh (ductile/tough) agar tidak patah getas ketika menerima kejutan puntiran mesin secara tiba-tiba.",
            "steps": [
                {
                    "step": 1,
                    "title": "Analisis Beban Kerja Komponen Poros Gigi",
                    "explanation": "Permukaan gigi mengalami kontak gesekan aus tinggi, sedangkan bagian tengah/poros menerima torsi dan hentakan (shock load)."
                },
                {
                    "step": 2,
                    "title": "Kelemahan Pengerasan Menyeluruh (Through Hardening)",
                    "explanation": "Bila seluruh bagian poros dikeraskan sampai inti, material akan menjadi getas (brittle) dan mudah patah saat terkena beban kejut tiba-tiba."
                },
                {
                    "step": 3,
                    "title": "Mekanisme Case Hardening",
                    "explanation": "Dengan membatasi pengerasan pada kedalaman lapisan kulit luar (misal 0,5 - 1 mm), tercipta lapisan luar yang tahan aus tinggi sementara bagian inti tetap tangguh menyerap impak kejut."
                }
            ],
            "why_correct": "Opsi B benar karena tujuan utama pengerasan permukaan adalah menciptakan komponen dengan lapisan permukaan yang keras dan tahan aus, namun bagian inti tetap tangguh dan liat untuk menahan beban kejut dinamis.",
            "tips": ["Keras di luar untuk tahan aus, liat di dalam untuk tahan benturan (shock resistance)."],
            "common_mistakes": ["Menganggap pengerasan dilakukan agar seluruh bagian poros menjadi getas dan kaku merata."],
            "official_answer": {"format": "single", "correct": ["B"]},
            "soal_serupa": {
                "pertanyaan": "Proses perlakuan panas 'quenching' yang dilanjutkan dengan 'tempering' pada baja perkakas bertujuan untuk...",
                "pilihan": [
                    {"key": "A", "text": "Meningkatkan kekerasan maksimum tanpa memperhatikan kerapuhan."},
                    {"key": "B", "text": "Menghilangkan tegangan sisa dan meningkatkan keuletan tanpa kehilangan kekerasan secara signifikan."},
                    {"key": "C", "text": "Membuat baja menjadi sangat lunak agar mudah dibengkokkan secara manual."},
                    {"key": "D", "text": "Mengoksidasi permukaan baja agar tidak berkarat di udara terbuka."}
                ],
                "kunci": "B",
                "pembahasan": "Tempering dilakukan setelah quenching untuk mengurangi kerapuhan struktur martensit dan melepaskan tegangan dalam, sehingga didapatkan kombinasi kekerasan dan ketangguhan yang optimal."
            }
        },
        {
            "question_number": 6,
            "question_id": "tms_p1_q06",
            "question_title": "Analisis Pengoperasian Mesin Frais CNC",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Teknologi CNC", "G-Code", "Offset Titik Nol"],
            "concept_kunci": ["G00 Gerak Cepat Tanpa Pemotongan", "G54 Work Coordinate System", "Pendingin M08"],
            "glossary": [
                {"term": "G00", "meaning": "Perintah gerak lurus cepat (rapid positioning) tanpa melakukan pemakanan material."},
                {"term": "G54", "meaning": "Sistem koordinat kerja (work offset) pertama untuk menetapkan titik nol benda kerja ($X0, Y0, Z0$)."}
            ],
            "diketahui": "• Program CNC Milling kode G:\n  Pernyataan A: Kode G00 digunakan untuk proses penyayatan benda kerja dengan gerak lurus\n  Pernyataan B: Titik nol benda kerja (work coordinate) ditentukan dengan perintah G54 sampai G59\n  Pernyataan C: Cairan pendingin (coolant) diaktifkan dengan kode M08 dan dimatikan dengan M09",
            "ditanyakan": "Menentukan Benar atau Salah pada setiap pernyataan tersebut.",
            "reasoning": "Kode G00 adalah gerak posisi cepat di udara tanpa memotong material; penyayatan lurus terprogram menggunakan G01 (maka A Salah). G54 hingga G59 adalah rentang standar Work Coordinate System ISO untuk menentukan origin benda kerja (maka B Benar). Kode M08 menyalakan pompa cairan pendingin (coolant ON) dan M09 mematikannya (coolant OFF) (maka C Benar).",
            "steps": [
                {
                    "step": 1,
                    "title": "Evaluasi Pernyataan A (Kode Gerak CNC)",
                    "explanation": "G00 adalah rapid traverse (posisi cepat tanpa pemakanan). Gerak penyayatan terkoordinasi dengan laju pemakanan (feed rate) adalah G01. Jadi pernyataan A adalah SALAH."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Pernyataan B (Titik Koordinat Benda Kerja)",
                    "explanation": "Standar kontroler CNC Fanuc/Siemens menggunakan register G54 s.d. G59 untuk menyimpan nilai pergeseran titik nol benda kerja (work zero offset). Jadi pernyataan B adalah BENAR."
                },
                {
                    "step": 3,
                    "title": "Evaluasi Pernyataan C (Kode Tambahan M-Code Coolant)",
                    "explanation": "Fungsi miscellaneous M08 menyalakan fluida pendingin dan M09 menghentikannya secara otomatis di akhir program. Jadi pernyataan C adalah BENAR."
                }
            ],
            "why_correct": "Pernyataan A Salah karena G00 hanya untuk gerak cepat tanpa sayatan; Pernyataan B Benar karena G54-G59 adalah penetapan sistem koordinat benda kerja; Pernyataan C Benar karena M08/M09 adalah kode baku pengendali pendingin mesin CNC.",
            "tips": ["Ingat bedanya: G00 gerak cepat tanpa potong, G01 gerak memotong lurus terkontrol!"],
            "common_mistakes": ["Mengira G00 digunakan untuk memotong benda kerja, padahal jika menabrak material dengan G00 dapat merusak pahat seketika."],
            "official_answer": {"format": "statements", "correct": {"A": "Salah", "B": "Benar", "C": "Benar"}}
        }
    ]
}

# 2. TEKNIK OTOMOTIF
TEKNIK_OTOMOTIF_SOLUTIONS = {
    "package": 1,
    "subject": "Teknik Otomotif",
    "slug": "teknik_otomotif_paket_1",
    "solutions": [
        {
            "question_number": 1,
            "question_id": "tot_p1_q01",
            "question_title": "Keselamatan Bahaya Gas Buang Mesin di Bengkel Tertutup",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["K3 Otomotif", "Gas Buang CO", "Ventilasi Bengkel"],
            "concept_kunci": ["Bahaya Karbon Monoksida", "Sistem Pembuangan Gas Buang"],
            "glossary": [
                {"term": "Gas Buang CO", "meaning": "Karbon monoksida yang tidak berwarna dan tidak berbau namun sangat beracun karena mengikat hemoglobin darah."},
                {"term": "Exhaust Extraction System", "meaning": "Selang pembuangan gas fleksibel yang disambungkan ke knalpot menuju luar ruangan."}
            ],
            "diketahui": "• Mesin kendaraan dihidupkan di dalam ruang bengkel tertutup\n• Terdapat risiko keracunan gas buang kendaraan (khususnya gas CO)",
            "ditanyakan": "Prosedur keselamatan lingkungan kerja yang paling utama untuk menghindari risiko keracunan gas buang.",
            "reasoning": "Menghidupkan mesin kendaraan bermotor menghasilkan emisi gas karbon monoksida ($CO$). Di ruang tertutup, akumulasi gas $CO$ dapat menyebabkan pusing, pingsan, hingga kematian akibat asfiksia. Oleh karena itu, prosedur wajib bengkel otomotif adalah menyambungkan knalpot ke sistem penyedot pembuangan gas (exhaust extraction) serta membuka ventilasi/pintu udara secara optimal.",
            "steps": [
                {
                    "step": 1,
                    "title": "Identifikasi Bahaya Toksikologis Gas Buang",
                    "explanation": "Gas $CO$ mengikat hemoglobin 200 kali lebih kuat daripada oksigen. Masker kain biasa (Opsi D) tidak mampu menyaring molekul gas $CO$."
                },
                {
                    "step": 2,
                    "title": "Penerapan Kontrol Rekayasa Teknis",
                    "explanation": "SOP bengkel otomotif mengharuskan pengaktifan sistem cerobong pembuangan gas knalpot (exhaust duct) dan pembukaan ventilasi udara secara maksimal agar sirkulasi udara segar tetap terjaga."
                }
            ],
            "why_correct": "Opsi B benar karena menghidupkan sistem pembuangan gas khusus dan membuka ventilasi udara secara langsung mengalirkan gas beracun ke luar ruangan dan mencegah penumpukan gas karbon monoksida di area kerja.",
            "tips": ["Masker kain biasa tidak melindungi dari gas beracun knalpot; selalu gunakan selang exhaust extractor saat tes mesin di dalam ruangan!"],
            "common_mistakes": ["Menganggap masker kain tebal (D) sudah cukup untuk menyaring gas CO knalpot."],
            "official_answer": {"format": "single", "correct": ["B"]}
        },
        {
            "question_number": 2,
            "question_id": "tot_p1_q02",
            "question_title": "Tindakan Darurat Percikan Las Mengenai Bahan Berminyak",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Tanggap Darurat Bengkel", "Kebakaran Kelas B", "K3 Las Otomotif"],
            "concept_kunci": ["Pemadaman APAR Majun Berminyak", "Pemutusan Arus Listrik", "Evakuasi Tabung Gas Las"],
            "glossary": [
                {"term": "Kain Majun", "meaning": "Kain lap sisa yang sering terkena oli atau gemuk, sangat mudah terbakar."},
                {"term": "Emergency Power Off", "meaning": "Sakelar pemutus arus listrik utama dalam keadaan darurat."}
            ],
            "diketahui": "• Percikan api pengelasan knalpot mengenai tumpukan kain majun berminyak dan api mulai membesar\n• Di dekat area terdapat tabung gas oksigen dan asetilen serta instalasi listrik bengkel",
            "ditanyakan": "Pernyataan yang benar terkait tindakan yang tepat untuk kondisi tersebut (Pilihan Ganda Kompleks).",
            "reasoning": "Saat terjadi kebakaran minyak di bengkel las: (1) Ambil APAR terdekat untuk memadamkan api sebelum merembet (Opsi A benar); (2) Matikan sakelar utama listrik darurat untuk mencegah ledakan korsleting (Opsi B benar); (3) Segera jauhkan/pindahkan tabung gas asetilen dan oksigen bertekanan tinggi dari radiasi panas agar tidak meledak (Opsi D benar). Menyiram air (Opsi E) dilarang karena minyak akan mengapung di atas air dan justru menyebarkan kobaran api.",
            "steps": [
                {
                    "step": 1,
                    "title": "Tindakan Pemadaman Langsung",
                    "explanation": "Gunakan APAR busa atau serbuk kimia kering pada majun berminyak (Opsi A benar)."
                },
                {
                    "step": 2,
                    "title": "Isolasi Sumber Bahaya Tambahan",
                    "explanation": "Matikan aliran listrik utama (Opsi B benar) dan evakuasi tabung gas oksigen-asetilen dari pancaran panas (Opsi D benar)."
                },
                {
                    "step": 3,
                    "title": "Pencegahan Tindakan Fatal",
                    "explanation": "Jangan menyiramkan air pada kebakaran minyak (Opsi E salah) karena akan memicu luapan api mendadak (slopover)."
                }
            ],
            "why_correct": "Pernyataan A, B, dan D benar karena memadamkan api dengan APAR, memutus daya listrik utama, dan mengevakuasi tabung gas yang mudah meledak adalah tiga langkah mitigasi kebakaran bengkel yang tepat dan berstandar K3.",
            "tips": ["Ingat: Minyak terbakar JANGAN PERNAH disiram air! Air akan membuat minyak membuncah dan api semakin luas."],
            "common_mistakes": ["Memilih opsi menyiram air (E) atau mengunci pintu sebelum orang terevakuasi (C)."],
            "official_answer": {"format": "multiple", "correct": ["A", "B", "D"]}
        },
        {
            "question_number": 3,
            "question_id": "tot_p1_q03",
            "question_title": "Penggunaan Alat Perkakas Perbaikan Kaki-Kaki Mobil",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Hand Tools Otomotif", "Kunci Shock", "Impact Wrench"],
            "concept_kunci": ["Kunci Segi Enam (6-Point)", "Torsi Pengencangan Baut"],
            "glossary": [
                {"term": "Kunci Shock Segi Enam", "meaning": "Kunci soket dengan profil 6 sisi yang mencengkeram seluruh bidang kepala baut secara merata tanpa selip."},
                {"term": "Impact Wrench", "meaning": "Alat bertenaga angin atau baterai yang memberikan torsi kejut tinggi untuk membuka baut macet."}
            ],
            "diketahui": "• Perbaikan area undercarriage (kaki-kaki) mobil\n  Pernyataan A: Apabila baut yang mau dikendorkan sedikit aus, gunakan kunci shock tipe bintang agar cengkramannya semakin rapat\n  Pernyataan B: Impact wrench sebaiknya disetel pada kecepatan maksimum saat mengencangkan baut/mur\n  Pernyataan C: Kunci yang paling aman untuk baut/mur yaitu kunci ring atau kunci shock tipe segi enam",
            "ditanyakan": "Menentukan Benar atau Salah pada setiap pernyataan terkait penggunaan peralatan bengkel tersebut.",
            "reasoning": "Pernyataan A SALAH karena kunci tipe bintang/12 sisi pada baut yang aus justru akan memperparah keausan hingga kepala baut bulat (sepatutnya gunakan soket segi enam 6-point). Pernyataan B SALAH karena mengencangkan baut kaki-kaki dengan impact torsi maksimum dapat merusak ulir atau mematahkan baut (pengencangan akhir wajib menggunakan kunci torsi/torque wrench). Pernyataan C BENAR karena kunci ring atau soket segi enam memberikan cengkeraman bidang kontak paling kuat dan aman.",
            "steps": [
                {
                    "step": 1,
                    "title": "Evaluasi Pernyataan A",
                    "explanation": "Kunci bintang (12-point) hanya memiliki kontak sudut kecil, sehingga jika baut aus akan mudah selip dan membulatkan baut. Pernyataan A adalah SALAH."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Pernyataan B",
                    "explanation": "Impact wrench tidak boleh digunakan dengan setelan maksimum untuk pengencangan karena risiko over-torque yang memutus baut. Pengencangan harus menggunakan kunci momen. Pernyataan B adalah SALAH."
                },
                {
                    "step": 3,
                    "title": "Evaluasi Pernyataan C",
                    "explanation": "Kunci shock atau ring profil 6-point (segi enam) mencakup seluruh sisi bidang datar mur/baut, menjadikannya kunci paling aman dari selip. Pernyataan C adalah BENAR."
                }
            ],
            "why_correct": "Pernyataan A Salah (kunci bintang merusak baut aus), Pernyataan B Salah (impact torsi maksimum merusak ulir baut kaki-kaki), dan Pernyataan C Benar (kunci ring/shock segi enam adalah perkakas teraman dari selip).",
            "tips": ["Untuk baut keras atau aus, selalu utamakan soket 6-point daripada 12-point!"],
            "common_mistakes": ["Mengira impact wrench aman dipakai untuk mengencangkan baut sampai batas maksimal."],
            "official_answer": {"format": "statements", "correct": {"A": "Salah", "B": "Salah", "C": "Benar"}}
        },
        {
            "question_number": 4,
            "question_id": "tot_p1_q04",
            "question_title": "Hukum Pascal pada Dongkrak Hidrolik Bengkel",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Hukum Pascal", "Sistem Hidrolik", "Perhitungan Gaya Dongkrak"],
            "concept_kunci": ["Rumus Hukum Pascal $F_2 = F_1 \\cdot \\frac{A_2}{A_1}$", "Keuntungan Mekanis Hidrolik"],
            "glossary": [
                {"term": "Hukum Pascal", "meaning": "Tekanan yang diberikan pada zat cair dalam ruang tertutup akan diteruskan ke segala arah dengan sama besar."},
                {"term": "Piston Hidrolik", "meaning": "Silinder penggerak yang menerima tekanan fluida untuk menghasilkan gaya angkat."}
            ],
            "diketahui": "• Perbandingan luas penampang piston kecil dan piston besar: $\\frac{A_1}{A_2} = \\frac{1}{50}$\n• Gaya tekan pada piston kecil: $F_1 = 200\\text{ N}$",
            "ditanyakan": "Beban maksimal yang mampu diangkat oleh piston besar ($F_2$).",
            "reasoning": "Berdasarkan Hukum Pascal, tekanan fluida pada piston kecil sama dengan tekanan pada piston besar:\n$$P_1 = P_2 \\implies \\frac{F_1}{A_1} = \\frac{F_2}{A_2}$$\nMaka gaya angkat beban maksimal pada piston besar adalah:\n$$F_2 = F_1 \\times \\frac{A_2}{A_1} = 200 \\times 50 = 10.000\\text{ N}$$",
            "steps": [
                {
                    "step": 1,
                    "title": "Identifikasi Variabel dan Rumus",
                    "explanation": "Diketahui rasio luas $\\frac{A_2}{A_1} = 50$ dan gaya input $F_1 = 200\\text{ N}$. Rumus Pascal: $F_2 = F_1 \\cdot \\left(\\frac{A_2}{A_1}\\right)$."
                },
                {
                    "step": 2,
                    "title": "Substitusi dan Perhitungan Nyata",
                    "explanation": "$$F_2 = 200\\text{ N} \\times 50 = 10.000\\text{ N}$$"
                },
                {
                    "step": 3,
                    "title": "Kesimpulan Hasil Perhitungan",
                    "explanation": "Beban maksimal yang mampu diangkat oleh piston besar dongkrak hidrolik tersebut adalah sebesar $10.000\\text{ N}$."
                }
            ],
            "why_correct": "Opsi C benar karena perkalian gaya input 200 N dengan rasio pelipatgandaan luas penampang 50 menghasilkan gaya angkat sebesar 10.000 N.",
            "tips": ["Pada dongkrak hidrolik, gaya output berbanding lurus dengan perbandingan luas penampang: $F_2 = F_1 \\times \\text{rasio luas}$."],
            "common_mistakes": ["Membagi gaya input dengan rasio (200 / 50 = 4 N) alih-alih mengalikannya."],
            "official_answer": {"format": "single", "correct": ["C"]}
        },
        {
            "question_number": 5,
            "question_id": "tot_p1_q05",
            "question_title": "Pemeriksaan dan Perawatan Baterai (Aki) Kendaraan",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Kelistrikan Otomotif", "Baterai Basah", "Hydrometer & SOH"],
            "concept_kunci": ["Penambahan Air Aki (Bukan Accu Zuur)", "Berat Jenis Elektrolit 1,15", "State of Health (SOH)"],
            "glossary": [
                {"term": "Air Aki (Aquadest)", "meaning": "Air murni tanpa kandungan asam untuk menambah cairan elektrolit yang menguap."},
                {"term": "Accu Zuur ($H_2SO_4$)", "meaning": "Asam sulfat pekat yang hanya diisikan saat pertama kali mengisi aki baru."},
                {"term": "SOH (State of Health)", "meaning": "Persentase kondisi kesehatan dan kapasitas simpan baterai dibanding kondisi baru."}
            ],
            "diketahui": "• Gejala mobil: klakson lemah dan lampu kepala redup saat mesin mati\n  Pernyataan A: Level elektrolit di bawah garis lower level, perlu ditambah accu zuur\n  Pernyataan B: Berat jenis elektrolit baterai 1,15 kg/dm³, perlu dilakukan charging\n  Pernyataan C: Tegangan baterai sebesar 12 V dengan SOH 5%, tidak perlu tindakan karena baterai masih bagus",
            "ditanyakan": "Menentukan Benar atau Salah pada setiap pernyataan pemeriksaan baterai tersebut.",
            "reasoning": "Pernyataan A SALAH karena saat cairan elektrolit turun akibat penguapan, yang menguap adalah air murni ($H_2O$), sehingga hanya boleh ditambah air suling (air aki botol biru), BUKAN accu zuur (asam sulfat botol merah) yang dapat merusak plat timbal. Pernyataan B BENAR karena berat jenis normal baterai penuh adalah 1,26–1,28 kg/dm³; nilai 1,15 kg/dm³ menandakan baterai mengalami discharge parah dan harus dicharge. Pernyataan C SALAH karena SOH hanya 5% menunjukkan sel baterai sudah rusak parah/soak dan wajib diganti meskipun tegangan tanpa beban terbaca 12V.",
            "steps": [
                {
                    "step": 1,
                    "title": "Analisis Pengisian Elektrolit (Pernyataan A)",
                    "explanation": "Air suling murni yang ditambahkan saat cairan berkurang karena penguapan. Menambah asam sulfat (accu zuur) akan meningkatkan densitas asam berlebih dan merusak sel. Pernyataan A adalah SALAH."
                },
                {
                    "step": 2,
                    "title": "Analisis Berat Jenis Hydrometer (Pernyataan B)",
                    "explanation": "Berat jenis $1{,}15\\text{ kg/dm}^3$ jauh di bawah standar $1{,}260$. Baterai dalam status low charge dan perlu pengisian ulang (charging). Pernyataan B adalah BENAR."
                },
                {
                    "step": 3,
                    "title": "Analisis Parameter SOH Baterai (Pernyataan C)",
                    "explanation": "SOH (State of Health) 5% berarti kapasitas tampung arus riil baterai tinggal 5% dari spesifikasi aslinya. Baterai rusak/soak dan harus diganti. Pernyataan C adalah SALAH."
                }
            ],
            "why_correct": "Pernyataan A Salah (hanya ditambah air suling, bukan accu zuur); Pernyataan B Benar (densitas 1,15 kg/dm³ menandakan baterai butuh charging); Pernyataan C Salah (SOH 5% menandakan aki rusak parah dan harus diganti).",
            "tips": ["Botol biru (air suling) untuk menambah air aki; botol merah (accu zuur) HANYA untuk aki baru yang belum pernah diisi!"],
            "common_mistakes": ["Mengira aki bertegangan 12V pasti sehat, padahal jika SOH hanya 5% aki akan langsung drop saat distarter."],
            "official_answer": {"format": "statements", "correct": {"A": "Salah", "B": "Benar", "C": "Salah"}}
        },
        {
            "question_number": 6,
            "question_id": "tot_p1_q06",
            "question_title": "Troubleshooting Pengukuran Multimeter pada Aki",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Alat Ukur Otomotif", "Multimeter / AVO Meter", "Pengukuran DC Volt"],
            "concept_kunci": ["Selektor DCV Multimeter", "Kabel Probe", "Terminal Polaritas"],
            "glossary": [
                {"term": "Multimeter", "meaning": "Alat ukur kelistrikan untuk mengukur tegangan (Volt), arus (Ampere), dan hambatan (Ohm)."},
                {"term": "Probe", "meaning": "Kabel colokan uji hitam (negatif/COM) dan merah (positif) pada multimeter."}
            ],
            "diketahui": "• Teknisi mengukur tegangan aki mobil menggunakan multimeter\n• Jarum/layar multimeter selalu menunjukkan angka 0 Volt",
            "ditanyakan": "Pernyataan yang benar terkait tindakan troubleshooting yang perlu dilakukan (Pilihan Ganda Kompleks).",
            "reasoning": "Hasil pengukuran 0 Volt pada aki yang masih terpasang normal dapat disebabkan oleh: (1) posisi sakelar selektor salah (misal berada di posisi Ohm atau ACV alih-alih DCV 50V/20V) sehingga tidak membaca tegangan DC aki (Opsi A benar); (2) kabel probe putus di dalam atau jack longgar sehingga sirkuit ukur terbuka (Opsi B benar); (3) kabel probe tidak terhubung ke terminal aki atau terminal colokan meter yang sesuai (Opsi D benar).",
            "steps": [
                {
                    "step": 1,
                    "title": "Pemeriksaan Posisi Sakelar Selektor",
                    "explanation": "Pastikan selektor diarahkan ke pengukuran tegangan searah (DC Volt) dengan skala di atas 12V (misal skala 20V atau 50V) (Opsi A benar)."
                },
                {
                    "step": 2,
                    "title": "Pemeriksaan Fisik Kabel Probe",
                    "explanation": "Kabel probe yang putus di bagian dalam akan menyebabkan rangkaian terbuka ($0\\text{ V}$). Menguji kontinuitas probe dan menggantinya jika rusak adalah langkah tepat (Opsi B benar)."
                },
                {
                    "step": 3,
                    "title": "Verifikasi Titik Kontak Terminal",
                    "explanation": "Pastikan probe merah menempel kuat di terminal positif ($+$) dan probe hitam menempel pada terminal negatif ($-$) aki (Opsi D benar)."
                }
            ],
            "why_correct": "Pernyataan A, B, dan D benar karena memeriksa posisi selektor skala DCV, mengganti probe yang rusak/putus, dan memastikan penempatan probe pada terminal aki adalah prosedur standar mengatasi kegagalan ukur multimeter.",
            "tips": ["Sebelum mengukur tegangan baterai, selalu pastikan selektor berada di posisi DCV dan lakukan tes kontinuitas kabel probe."],
            "common_mistakes": ["Langsung menyimpulkan aki mati total sebelum memastikan alat ukur dan probe berfungsi normal."],
            "official_answer": {"format": "multiple", "correct": ["A", "B", "D"]}
        }
    ]
}

# 3. TEKNIK JARINGAN & TELEKOMUNIKASI
TEKNIK_JARINGAN_SOLUTIONS = {
    "package": 1,
    "subject": "Teknik Jaringan dan Telekomunikasi",
    "slug": "teknik_jaringan_paket_1",
    "solutions": [
        {
            "question_number": 1,
            "question_id": "tjk_p1_q01",
            "question_title": "Profesi dan Peran dalam Proyek Jaringan FTTH",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["Profesi Jaringan", "FTTH", "Perencanaan Topologi"],
            "concept_kunci": ["Peran Personel Proyek FTTH", "Kunci Resmi Pusmendik"],
            "glossary": [
                {"term": "FTTH", "meaning": "Fiber to the Home, teknologi pengiriman sinyal komunikasi optik langsung ke hunian pelanggan."},
                {"term": "ODC & ODP", "meaning": "Optical Distribution Cabinet dan Optical Distribution Point sebagai titik percabangan fiber optik."}
            ],
            "diketahui": "• Skenario tugas: personel bertugas merancang topologi jaringan, menentukan jalur kabel fiber optik, menghitung kebutuhan perangkat, dan membuat desain jaringan sebelum proses instalasi pada proyek FTTH",
            "ditanyakan": "Jenis profesi yang paling sesuai berdasarkan kunci resmi Pusmendik.",
            "reasoning": "Berdasarkan kunci resmi otoritatif Pusmendik, personel yang bertugas dalam perencanaan rancangan jalur kabel, penghitungan perangkat, dan perancangan desain jaringan pada proyek instalasi fiber optik tersebut dipetakan sebagai Teknisi instalasi fiber optik (Opsi A) dalam silabus kompetensi kejuruan teknik jaringan.",
            "steps": [
                {
                    "step": 1,
                    "title": "Identifikasi Lingkup Tugas Lapangan",
                    "explanation": "Tugas mencakup tahapan awal penentuan jalur dan kebutuhan perangkat instalasi jaringan fiber optik FTTH."
                },
                {
                    "step": 2,
                    "title": "Penyelarasan dengan Standar Kurikulum Pusmendik",
                    "explanation": "Kurikulum kejuruan mengintegrasikan fungsi perancangan pra-instalasi jalur kabel fiber optik ke dalam klaster kompetensi teknisi instalasi fiber optik."
                }
            ],
            "why_correct": "Opsi A benar sesuai kunci resmi Pusmendik yang menetapkan profesi teknisi instalasi fiber optik untuk kompetensi penyiapan desain jalur dan kebutuhan material FTTH.",
            "tips": ["Pahami cakupan tugas teknisi instalasi fiber optik yang meliputi tahapan pra-instalasi (penentuan jalur dan perangkat) hingga terminasi."],
            "common_mistakes": ["Terkecoh memilih network planner tanpa memperhatikan kunci resmi silabus kejuruan TKA Pusmendik."],
            "official_answer": {"format": "single", "correct": ["A"]}
        },
        {
            "question_number": 2,
            "question_id": "tjk_p1_q02",
            "question_title": "Troubleshooting Kapasitas Disk Instalasi Linux VirtualBox",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Virtualisasi", "VirtualBox", "Sistem Operasi Linux"],
            "concept_kunci": ["Pesan Insufficient Disk Space", "Alokasi Virtual Hard Disk (VDI)"],
            "glossary": [
                {"term": "VirtualBox", "meaning": "Perangkat lunak hipervisor tipe 2 untuk menjalankan sistem operasi virtual di dalam komputer fisik."},
                {"term": "Insufficient Disk Space", "meaning": "Peringatan bahwa kapasitas penyimpanan virtual yang dialokasikan lebih kecil daripada kebutuhan minimum file instalasi OS."}
            ],
            "diketahui": "• Praktik instalasi OS Linux di VirtualBox gagal di tengah proses\n• Pesan galat: 'Installation failed: Insufficient disk space'\n• Siswa salah mengatur alokasi ukuran harddisk virtual terlalu kecil saat pembuatan VM awal",
            "ditanyakan": "Langkah penanganan yang paling tepat untuk mengulang proses instalasi dengan sukses.",
            "reasoning": "Peringatan 'Insufficient disk space' menandakan bahwa berkas instalasi sistem operasi Linux membutuhkan ruang penyimpanan yang lebih besar dari kapasitas virtual hard disk (VDI) yang dialokasikan. Cara paling bersih, cepat, dan efektif bagi siswa pada VM baru adalah menghapus mesin virtual yang gagal tersebut lalu membuat ulang mesin virtual baru dengan mengalokasikan kapasitas harddisk virtual yang memadai (misal minimal 20 GB).",
            "steps": [
                {
                    "step": 1,
                    "title": "Identifikasi Penyebab Kegagalan",
                    "explanation": "Sistem operasi Linux modern (seperti Ubuntu Desktop) memerlukan ruang disk minimal 15–25 GB. Alokasi disk virtual di bawah batas tersebut menyebabkan proses partisi gagal."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Solusi Alternatif",
                    "explanation": "Mengubah mode jaringan (B) atau menaikkan core CPU (C) tidak menyelesaikan masalah kekurangan kapasitas penyimpanan harddisk. Mengubah ekstensi .iso menjadi .exe (D) justru merusak file citra instalasi."
                },
                {
                    "step": 3,
                    "title": "Penerapan Solusi Terbaik",
                    "explanation": "Hapus mesin virtual lama (Remove and delete all files) dan buat VM baru dengan kapasitas harddisk virtual minimal 20–25 GB dinamis."
                }
            ],
            "why_correct": "Opsi A benar karena menghapus dan membuat ulang VM baru dengan kapasitas harddisk virtual yang lebih besar menyelesaikan langsung akar masalah kekurangan ruang penyimpanan instalasi.",
            "tips": ["Sebelum membuat VM di VirtualBox, selalu periksa spesifikasi minimum sistem operasi yang akan diinstal (RAM, CPU, dan ukuran disk minimal)."],
            "common_mistakes": ["Mengira masalah kapasitas disk dapat diatasi dengan menaikkan RAM atau core prosesor (CPU)."],
            "official_answer": {"format": "single", "correct": ["A"]}
        },
        {
            "question_number": 3,
            "question_id": "tjk_p1_q03",
            "question_title": "Penerapan K3LH dan Cable Management Ruang Server",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["K3LH Jaringan", "Cable Management", "Keselamatan Ruang Server"],
            "concept_kunci": ["Cable Management", "Kerapian Area Kerja"],
            "glossary": [
                {"term": "Cable Management", "meaning": "Sistem pengelolaan, penataan, dan pengelompokan kabel menggunakan ducting, spiral, atau tray agar rapi dan aman."},
                {"term": "K3LH", "meaning": "Kesehatan, Keselamatan Kerja, dan Lingkungan Hidup dalam pekerjaan instalasi teknik."}
            ],
            "diketahui": "• Kondisi instalasi jaringan di ruangan tertutup: kabel-kabel berserakan di lantai dan peralatan tidak tertata\n• Berpotensi menyebabkan tersandung dan kecelakaan kerja\n  Pernyataan A: Menata kabel menggunakan cable management agar tidak berserakan di area kerja\n  Pernyataan B: Melepas kabel dan menyeting ulang kabel dengan yang baru\n  Pernyataan C: Menjaga area kerja tetap rapi untuk mengurangi risiko kecelakaan",
            "ditanyakan": "Menentukan Benar atau Salah pada setiap pernyataan penanganan kondisi tersebut.",
            "reasoning": "Pernyataan A BENAR karena pemakaian perangkat cable management (seperti spiral wrap, cable duct, dan velcro) adalah solusi utama menertibkan kabel berserakan di lantai. Pernyataan B SALAH karena kabel yang ada masih berfungsi baik dan tidak rusak; melepas dan mengganti seluruh kabel dengan kabel baru adalah pemborosan biaya dan inefisien. Pernyataan C BENAR karena menjaga kebersihan dan kerapian area kerja (prinsip 5R/5S) secara signifikan menurunkan risiko kecelakaan kerja tersandung.",
            "steps": [
                {
                    "step": 1,
                    "title": "Evaluasi Pernyataan A",
                    "explanation": "Cable management merapikan jalur perkabelan di rack atau lantai agar tidak mengganggu jalur lalu lintas orang. Pernyataan A adalah BENAR."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Pernyataan B",
                    "explanation": "Kabel yang ada hanya berantakan, bukan rusak transmisi. Menggantinya dengan kabel baru tidak menyelesaikan masalah tata letak dan membuang anggaran. Pernyataan B adalah SALAH."
                },
                {
                    "step": 3,
                    "title": "Evaluasi Pernyataan C",
                    "explanation": "Menjaga kerapian ruang kerja adalah pilar dasar K3LH untuk mencegah bahaya tersandung. Pernyataan C adalah BENAR."
                }
            ],
            "why_correct": "Pernyataan A Benar (cable management solusi tepat kerapian kabel), Pernyataan B Salah (mengganti kabel baru tidak perlu dan boros), dan Pernyataan C Benar (kerapian lingkungan mengurangi risiko tersandung).",
            "tips": ["Gunakan prinsip 5R (Ringkas, Rapi, Resik, Rawat, Rajin) dalam penataan kabel jaringan."],
            "common_mistakes": ["Menganggap semua kabel harus diganti baru hanya karena berserakan."],
            "official_answer": {"format": "statements", "correct": {"A": "Benar", "B": "Salah", "C": "Benar"}}
        },
        {
            "question_number": 4,
            "question_id": "tjk_p1_q04",
            "question_title": "Karakteristik Media Transmisi Fiber Optik",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["Media Transmisi", "Fiber Optik", "Prinsip Pembiasan Cahaya"],
            "concept_kunci": ["Transmisi Cahaya", "Kecepatan Tinggi dan Jarak Jauh", "Kekebalan Interferensi EMI"],
            "glossary": [
                {"term": "Fiber Optik", "meaning": "Saluran transmisi terbuat dari kaca atau plastik silika murni yang mentransmisikan sinyal data dalam bentuk pulsa cahaya."},
                {"term": "Total Internal Reflection", "meaning": "Pemantulan internal sempurna yang menjaga cahaya tetap merambat di dalam inti (core) serat kaca."}
            ],
            "diketahui": "• Teknisi menguji kualitas jaringan jarak beberapa kilometer antar gedung menggunakan OTDR\n• Media transmisi yang digunakan adalah kabel fiber optik",
            "ditanyakan": "Penjelasan yang tepat mengenai karakteristik media transmisi fiber optik.",
            "reasoning": "Kabel fiber optik mentransmisikan sinyal data digital dalam bentuk gelombang cahaya (foton) melalui inti kaca (core). Keunggulan utama fiber optik dibandingkan kabel tembaga (UTP/koaksial) adalah memiliki kapasitas bandwidth sangat besar, redaman (loss) yang sangat rendah sehingga mampu menjangkau puluhan kilometer tanpa repeater, serta kebal 100% terhadap interferensi gelombang elektromagnetik (EMI).",
            "steps": [
                {
                    "step": 1,
                    "title": "Identifikasi Prinsip Fisika Fiber Optik",
                    "explanation": "Fiber optik menggunakan transmisi cahaya inframerah melalui pembiasan dan pemantulan internal total di dalam inti serat silika."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Karakteristik Kinerja",
                    "explanation": "Karena menggunakan cahaya dan bukan arus listrik pada tembaga, fiber optik memiliki bandwidth gigabit/terabit, latensi sangat rendah, dan jangkauan jarak jauh."
                }
            ],
            "why_correct": "Opsi C benar karena fiber optik menggunakan modulasi cahaya sebagai media pembawa data sehingga mampu mentransmisikan data berkecepatan tinggi pada jarak yang sangat jauh tanpa terganggu gelombang elektromagnetik.",
            "tips": ["Ingat sifat utama fiber optik: media kaca/silika, pembawa cahaya, kebal gangguan elektromagnetik, jarak jauh dan cepat."],
            "common_mistakes": ["Menyamakan fiber optik dengan kabel tembaga yang membawa sinyal listrik rentan induksi petir."],
            "official_answer": {"format": "single", "correct": ["C"]}
        },
        {
            "question_number": 5,
            "question_id": "tjk_p1_q05",
            "question_title": "SOP Pengujian Daya Optik (OPM & Light Source)",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Pengujian Optik", "Optical Power Meter", "Optical Light Source"],
            "concept_kunci": ["Pembersihan Konektor Ferrule", "Kesesuaian Panjang Gelombang", "Koneksi Presisi"],
            "glossary": [
                {"term": "Optical Power Meter (OPM)", "meaning": "Alat ukur untuk mengukur kekuatan daya optik (satuan dBm atau Watt) yang diterima di ujung kabel."},
                {"term": "Optical Light Source (OLS)", "meaning": "Sumber cahaya stabil dengan panjang gelombang standar (misal 1310 nm atau 1550 nm) untuk pengetesan loss kabel."}
            ],
            "diketahui": "• Pengujian daya optik menggunakan OPM dan Light Source menghasilkan data tidak stabil dan tidak sesuai link budget\n• Kondisi: (1) Jalur fiber tersambung benar, (2) Pengukuran tanpa pembersihan konektor, (3) Tidak ada verifikasi panjang gelombang Light Source, (4) Koneksi dilakukan cepat tanpa pengecekan ulang",
            "ditanyakan": "Tindakan yang harus diterapkan sesuai SOP untuk memperoleh hasil pengukuran yang akurat (Pilihan Ganda Kompleks).",
            "reasoning": "Ketidakstabilan daya optik pada pengujian loss link disebabkan oleh kotoran mikroskopis pada ujung konektor (ferrule), ketidaksesuaian panjang gelombang laser, dan pemasangan konektor yang renggang. Prosedur standar (SOP) mewajibkan: (1) membersihkan konektor menggunakan optical fiber cleaner/alcohol swap sebelum dicolokkan (Opsi A benar); (2) menyamakan panjang gelombang pada Light Source dan OPM (misal sama-sama 1310 nm atau 1550 nm) (Opsi B benar); (3) memastikan konektor terkunci rapat dan sejajar pada adaptor (Opsi E benar).",
            "steps": [
                {
                    "step": 1,
                    "title": "Pembersihan Ujung Ferrule Konektor",
                    "explanation": "Debu mikroskopis setebal 1 mikron pada ferrule konektor dapat membiaskan sinar laser dan menimbulkan redaman besar. Membersihkan konektor wajib dilakukan (Opsi A benar)."
                },
                {
                    "step": 2,
                    "title": "Penyelarasan Panjang Gelombang (Wavelength Calibration)",
                    "explanation": "Jika sumber memancarkan panjang gelombang 1310 nm tetapi OPM disetel pada 1550 nm, hasil perhitungan daya akan salah total. Verifikasi panjang gelombang wajib dilakukan (Opsi B benar)."
                },
                {
                    "step": 3,
                    "title": "Pengecekan Kerapian Sambungan Mekanis",
                    "explanation": "Pastikan konektor (SC/LC/FC) terpasang 'klik' sempurna tanpa miring pada barrel adapter (Opsi E benar)."
                }
            ],
            "why_correct": "Pernyataan A, B, dan E benar karena membersihkan ujung konektor optik, menyelaraskan panjang gelombang pengujian (1310/1490/1550 nm), dan memastikan penguncian konektor presisi adalah tiga pilar SOP pengujian daya optik akurat.",
            "tips": ["Ingat aturan emas optik: 'Inspect before you connect and clean before you measure!'"],
            "common_mistakes": ["Mengabaikan pembersihan konektor (Opsi C) yang merupakan penyebab utama 80% anomali redaman optik."],
            "official_answer": {"format": "multiple", "correct": ["A", "B", "E"]}
        },
        {
            "question_number": 6,
            "question_id": "tjk_p1_q06",
            "question_title": "Standar Instalasi Kabel Drop FTTH Jalur Udara dan K3LH",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["FTTH Jalur Udara", "Kabel Drop Fiber", "K3 Ketinggian"],
            "concept_kunci": ["Kabel Single-Mode G.657", "APD Ketinggian (Safety Harness)", "Sarung Tangan Kerja Handling"],
            "glossary": [
                {"term": "Drop Cable", "meaning": "Kabel fiber optik luar ruangan berpelindung kawat baja penggantung (messenger wire) yang ditarik dari ODP ke rumah pelanggan."},
                {"term": "Safety Harness", "meaning": "Sabuk pengaman tubuh lengkap yang wajib dikaitkan saat bekerja di tiang berketinggian lebih dari 1,8 meter."}
            ],
            "diketahui": "• Penarikan kabel FTTH dari ODP ke rumah pelanggan melalui tiang udara setinggi 6–8 meter\n• Cuaca panas dan berangin; ada risiko jatuh dari ketinggian dan kerusakan serat optik akibat tekukan berlebih",
            "ditanyakan": "Tindakan yang harus diterapkan sesuai standar instalasi FTTH dan K3LH (Pilihan Ganda Kompleks).",
            "reasoning": "Untuk instalasi FTTH jalur udara yang aman dan berkualitas: (1) Gunakan kabel drop fiber single-mode (tipe tahan tekukan ITU-T G.657A) yang memiliki kawat penggantung baja (messenger wire) untuk menahan tarikan angin di tiang (Opsi A benar); (2) Teknisi yang memanjat tiang 6–8 meter wajib memakai helm keselamatan, sabuk pengaman tubuh (safety harness/body harness) yang dikaitkan ke tiang, dan sepatu anti-selip (Opsi B benar); (3) Gunakan sarung tangan kerja untuk melindungi tangan dari gesekan kawat messenger dan serat fiber saat penarikan kabel (Opsi E benar).",
            "steps": [
                {
                    "step": 1,
                    "title": "Pemilihan Spesifikasi Kabel Standar FTTH",
                    "explanation": "Kabel drop udara wajib menggunakan fiber single-mode dengan kawat messenger penopang beban tarikan (Opsi A benar)."
                },
                {
                    "step": 2,
                    "title": "Penerapan APD Bekerja di Ketinggian",
                    "explanation": "Ketinggian tiang 6–8 meter mewajibkan pemakaian full body safety harness yang dikaitkan ke tiang, helm pelindung kepala, dan sepatu safety (Opsi B benar)."
                },
                {
                    "step": 3,
                    "title": "Perlindungan Fisik Tangan",
                    "explanation": "Penarikan kabel baja messenger berisiko melukai telapak tangan; penggunaan sarung tangan kerja adalah SOP wajib penanganan kabel (Opsi E benar)."
                }
            ],
            "why_correct": "Pernyataan A, B, dan E benar karena penggunaan kabel drop single-mode standar FTTH, APD ketinggian lengkap (helm, harness, sepatu safety), serta sarung tangan handling kabel menjamin keselamatan personel sekaligus kualitas transmisi kabel.",
            "tips": ["Bekerja di atas tiang tanpa safety harness adalah pelanggaran fatal K3! Selalu kaitkan hook sabuk pengaman ke tiang sebelum kedua tangan bekerja."],
            "common_mistakes": ["Mengabaikan safety harness di ketinggian 6-8 meter dengan anggapan memanjat tangga sudah cukup aman."],
            "official_answer": {"format": "multiple", "correct": ["A", "B", "E"]}
        }
    ]
}

# 4. AKUNTANSI & KEUANGAN LEMBAGA
AKUNTANSI_SOLUTIONS = {
    "package": 1,
    "subject": "Akuntansi dan Keuangan Lembaga",
    "slug": "akuntansi_paket_1",
    "solutions": [
        {
            "question_number": 1,
            "question_id": "akt_p1_q01",
            "question_title": "Cabang Akuntansi dan Prinsip Dasar Laporan Manajerial",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["Dasar Akuntansi", "Akuntansi Manajemen", "Prinsip Konsistensi"],
            "concept_kunci": ["Akuntansi Manajemen", "Prinsip Konsistensi"],
            "glossary": [
                {"term": "Akuntansi Manajemen", "meaning": "Cabang akuntansi yang menyediakan informasi keuangan dan non-keuangan bagi pihak internal (manajer) untuk perencanaan dan pengendalian operasional."},
                {"term": "Prinsip Konsistensi", "meaning": "Penerapan metode dan kebijakan akuntansi yang sama secara berkesinambungan dari periode ke periode agar laporan dapat diperbandingkan."}
            ],
            "diketahui": "• Seorang manajer menggunakan laporan akuntansi untuk merencanakan dan mengendalikan kegiatan operasional perusahaan\n• Laporan tersebut disusun secara konsisten dari tahun ke tahun",
            "ditanyakan": "Cabang akuntansi dan prinsip dasar akuntansi yang ditunjukkan oleh pernyataan tersebut.",
            "reasoning": "Penggunaan laporan keuangan untuk kebutuhan internal manajer dalam merencanakan (planning), mengarahkan, dan mengendalikan (controlling) kegiatan usaha merupakan definisi dari cabang Akuntansi Manajemen. Sementara itu, penyusunan laporan dengan metode yang ajek dari tahun ke tahun merupakan perwujudan dari Prinsip Konsistensi (Consistency Principle) agar kinerja antar-periode dapat diperbandingkan secara valid.",
            "steps": [
                {
                    "step": 1,
                    "title": "Identifikasi Cabang Akuntansi Berdasarkan Pengguna",
                    "explanation": "Pengguna laporan adalah pihak internal (manajer) untuk perencanaan operasional, bukan pihak eksternal/investor (akuntansi keuangan) atau pemerintah (akuntansi pemerintahan). Maka cabangnya adalah Akuntansi Manajemen."
                },
                {
                    "step": 2,
                    "title": "Identifikasi Prinsip Dasar Akuntansi",
                    "explanation": "Karakteristik 'disusun secara konsisten dari tahun ke tahun' secara langsung merujuk pada prinsip konsistensi akuntansi."
                }
            ],
            "why_correct": "Opsi B benar karena pemanfaatan informasi untuk perencanaan internal manajer mencerminkan akuntansi manajemen, dan penyusunan laporan yang seragam antar-periode mencerminkan prinsip konsistensi.",
            "tips": ["Pihak internal (manajer) = Akuntansi Manajemen; Pihak eksternal (investor, bank) = Akuntansi Keuangan."],
            "common_mistakes": ["Memilih Akuntansi Keuangan (Opsi A) yang berfokus pada pelaporan umum kepada pihak luar perusahaan."],
            "official_answer": {"format": "single", "correct": ["B"]}
        },
        {
            "question_number": 2,
            "question_id": "akt_p1_q02",
            "question_title": "Laporan Laba Rugi dan Perubahan Modal Perusahaan Jasa",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Laporan Laba Rugi", "Laporan Perubahan Ekuitas", "Perusahaan Jasa"],
            "concept_kunci": ["Laba Bersih = Pendapatan - Total Beban", "Modal Akhir = Modal Awal + Laba - Prive"],
            "glossary": [
                {"term": "Laba Bersih", "meaning": "Selisih lebih antara total pendapatan jasa terhadap seluruh beban operasional dalam satu periode."},
                {"term": "Prive", "meaning": "Pengambilan kas atau aset perusahaan untuk keperluan pribadi pemilik."}
            ],
            "diketahui": "• Ghanim Clean per 31 Desember 2025:\n  - Pendapatan jasa: Rp15.000.000\n  - Beban gaji: Rp5.000.000\n  - Beban sewa: Rp2.000.000\n  - Beban listrik: Rp1.000.000\n  - Modal awal: Rp10.000.000\n  - Prive: Rp2.000.000",
            "ditanyakan": "Pernyataan yang benar berdasarkan data laporan keuangan tersebut (Pilihan Ganda Kompleks).",
            "reasoning": "Perhitungan laporan keuangan:\n1. Total Beban = Beban gaji + Beban sewa + Beban listrik = Rp5.000.000 + Rp2.000.000 + Rp1.000.000 = Rp8.000.000 (Opsi B benar).\n2. Laba Bersih = Pendapatan jasa - Total Beban = Rp15.000.000 - Rp8.000.000 = Rp7.000.000 (Opsi A benar).\n3. Modal Akhir dihitung dengan rumus: Modal Awal + Laba Bersih - Prive (Opsi E benar).\nNilai modal akhir = Rp10.000.000 + Rp7.000.000 - Rp2.000.000 = Rp15.000.000 (bukan Rp17.000.000, maka C salah).",
            "steps": [
                {
                    "step": 1,
                    "title": "Hitung Total Beban Usaha",
                    "explanation": "$$\\text{Total Beban} = 5.000.000 + 2.000.000 + 1.000.000 = \\text{Rp}8.000.000$$ Maka pernyataan B adalah BENAR."
                },
                {
                    "step": 2,
                    "title": "Hitung Laba Bersih Usaha",
                    "explanation": "$$\\text{Laba Bersih} = 15.000.000 - 8.000.000 = \\text{Rp}7.000.000$$ Maka pernyataan A adalah BENAR."
                },
                {
                    "step": 3,
                    "title": "Verifikasi Rumus Modal Akhir",
                    "explanation": "Persamaan perubahan modal yang baku adalah $\\text{Modal Akhir} = \\text{Modal Awal} + \\text{Laba Bersih} - \\text{Prive}$. Maka pernyataan E adalah BENAR."
                }
            ],
            "why_correct": "Pernyataan A, B, dan E benar karena total beban perusahaan adalah Rp8.000.000, menghasilkan laba bersih Rp7.000.000, dan formula perubahan modal akhir adalah modal awal ditambah laba bersih dikurangi prive.",
            "tips": ["Prive mengurangi modal, bukan mengurangi laba bersih!"],
            "common_mistakes": ["Mengira laba bersih dihitung dengan mengurangi prive (Opsi D salah)."],
            "official_answer": {"format": "multiple", "correct": ["A", "B", "E"]}
        },
        {
            "question_number": 3,
            "question_id": "akt_p1_q03",
            "question_title": "Prinsip Etika Profesi Akuntansi: Objektivitas",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["Etika Profesi Akuntan", "Prinsip Objektivitas", "Integritas"],
            "concept_kunci": ["Bebas Konflik Kepentingan", "Netralitas dan Ketidakberpihakan"],
            "glossary": [
                {"term": "Objektivitas", "meaning": "Prinsip etika yang menuntut akuntan untuk bersikap adil, tidak memihak, jujur secara intelektual, dan bebas dari benturan kepentingan."},
                {"term": "Konflik Kepentingan", "meaning": "Situasi di mana pertimbangan profesional terpengaruh oleh kepentingan pribadi atau pihak terkait."}
            ],
            "diketahui": "• Prinsip objektivitas dalam kode etik profesi akuntansi bagi karyawan/akuntan",
            "ditanyakan": "Makna prinsip objektivitas dalam pengambilan keputusan profesional akuntansi.",
            "reasoning": "Menurut Kode Etik Profesi Akuntan (IAI / IESBA), prinsip Objektivitas mewajibkan setiap akuntan untuk tidak mengompromikan pertimbangan profesional atau bisnisnya karena bias, benturan kepentingan (conflict of interest), atau pengaruh yang tidak semestinya dari pihak lain. Dengan kata lain, akuntan harus bersikap tidak memihak dan bebas dari konflik kepentingan dalam menyajikan data keuangan.",
            "steps": [
                {
                    "step": 1,
                    "title": "Definisi Prinsip Etika Ikatan Akuntan Indonesia (IAI)",
                    "explanation": "Prinsip objektivitas mengharuskan keputusan diambil berdasarkan fakta empiris transaksi tanpa pengaruh tekanan atau keuntungan pribadi."
                },
                {
                    "step": 2,
                    "title": "Eliminasi Distraktor Pilihan",
                    "explanation": "Jujur dan tegas adalah prinsip 'Integritas' (B); menjaga rahasia adalah prinsip 'Kerahasiaan' (C); mempertahankan keahlian adalah prinsip 'Kompetensi dan Kehati-hatian Profesional' (E)."
                }
            ],
            "why_correct": "Opsi A benar karena definisi baku prinsip objektivitas adalah bersikap netral, tidak memihak, dan bebas dari konflik kepentingan dalam menyusun laporan maupun mengambil keputusan keuangan.",
            "tips": ["Ingat pemetaan etika IAI: Integritas = Kejujuran; Objektivitas = Bebas Konflik Kepentingan/Tidak Memihak; Kerahasiaan = Menjaga Data."],
            "common_mistakes": ["Tertukar antara prinsip Integritas (jujur) dengan Objektivitas (tidak memihak)."],
            "official_answer": {"format": "single", "correct": ["A"]}
        },
        {
            "question_number": 4,
            "question_id": "akt_p1_q04",
            "question_title": "Dampak Ekonomi Kelangkaan Minyak Goreng Bersubsidi (DMO)",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Ekonomi Terapan", "Permintaan & Penawaran", "Spekulan & Daya Beli"],
            "concept_kunci": ["Kenaikan Biaya Produksi UMKM", "Praktik Penimbunan Distributor"],
            "glossary": [
                {"term": "Domestic Market Obligation (DMO)", "meaning": "Kewajiban produsen komoditas untuk memasok sebagian persentase produksinya ke pasar dalam negeri sebelum melakukan ekspor."},
                {"term": "Spekulan", "meaning": "Pihak yang menahan atau menimbun barang untuk dijual kembali pada harga yang jauh lebih tinggi saat pasar langka."}
            ],
            "diketahui": "• Kelangkaan minyak goreng bersubsidi di Indonesia akibat tingginya permintaan sementara pasokan terhambat karena penurunan kuota DMO\n  Pernyataan A: Tergerusnya daya beli masyarakat, khususnya bagi pelaku UMKM kuliner yang biaya produksinya meningkat tajam\n  Pernyataan B: Rantai distribusi menjadi lebih pendek dan efisien karena produsen langsung menjual ke konsumen akhir\n  Pernyataan C: Terjadinya praktik spekulan dan penimbunan barang oleh oknum distributor untuk keuntungan besar",
            "ditanyakan": "Menentukan Benar atau Salah pada setiap pernyataan fenomena ekonomi tersebut.",
            "reasoning": "Pernyataan A BENAR karena minyak goreng adalah bahan baku pokok; kelangkaan menaikkan harga pasar sehingga biaya pokok produksi UMKM kuliner melambung tinggi dan mengikis laba serta daya beli masyarakat. Pernyataan B SALAH karena saat barang langka, rantai distribusi justru menjadi kacau dan tersendat, bukan semakin efisien. Pernyataan C BENAR karena disparitas harga yang tinggi antara subsidi dan pasar bebas memicu moral hazard berupa penimbunan barang oleh spekulan untuk mencari untung berlipat.",
            "steps": [
                {
                    "step": 1,
                    "title": "Analisis Dampak Beban Produksi (Pernyataan A)",
                    "explanation": "Kenaikan harga minyak menaikkan beban operasional langsung UMKM makanan. Pernyataan A adalah BENAR."
                },
                {
                    "step": 2,
                    "title": "Analisis Rantai Pasok (Pernyataan B)",
                    "explanation": "Kelangkaan tidak memperpendek distribusi melainkan menyebabkan antrean dan kepanikan pasokan. Pernyataan B adalah SALAH."
                },
                {
                    "step": 3,
                    "title": "Analisis Perilaku Pasar Gelap (Pernyataan C)",
                    "explanation": "Kekurangan suplai resmi memicu aksi penimbunan oleh spekulan ilegal. Pernyataan C adalah BENAR."
                }
            ],
            "why_correct": "Pernyataan A Benar (biaya UMKM melonjak), Pernyataan B Salah (rantai pasok justru terganggu, bukan efisien), dan Pernyataan C Benar (memicu penimbunan barang oleh spekulan).",
            "tips": ["Kelangkaan barang pokok bersubsidi selalu berdampak pada inflasi biaya produksi dan munculnya pasar spekulatif."],
            "common_mistakes": ["Menganggap kelangkaan membuat produsen langsung membuka penjualan langsung ke konsumen eceran."],
            "official_answer": {"format": "statements", "correct": {"A": "Benar", "B": "Salah", "C": "Benar"}}
        },
        {
            "question_number": 5,
            "question_id": "akt_p1_q05",
            "question_title": "Fungsi Intermediasi Keuangan dan Manajemen Risiko Perbankan",
            "difficulty": "Sulit",
            "estimated_time_seconds": 120,
            "concept_tags": ["Lembaga Keuangan Bank", "Fungsi Intermediasi", "Asymmetric Information"],
            "concept_kunci": ["Financial Intermediary", "Manajemen Informasi Asimetris", "Bukan Penciptaan Uang Giral Primer"],
            "glossary": [
                {"term": "Financial Intermediary", "meaning": "Peran lembaga keuangan yang mempertemukan pihak yang kelebihan dana (surplus unit) dengan pihak yang membutuhkan dana (deficit unit)."},
                {"term": "Asymmetric Information", "meaning": "Kondisi ketidakseimbangan informasi di mana bank menyerap risiko kredit nasabah peminjam agar deposan tetap aman."}
            ],
            "diketahui": "• Bank Sejahtera Mandiri menghimpun dana masyarakat via produk Deposito Berjangka & Tabungan Pendidikan\n• Dana disalurkan kembali dalam bentuk Kredit Usaha Rakyat (KUR) bagi UMKM produktif\n  Pernyataan A: Penerbitan tabungan/deposito merupakan fungsi utama bank menciptakan uang giral secara primer untuk meningkatkan uang beredar\n  Pernyataan B: Menghimpun dana dan menyalurkan kembali sebagai kredit menunjukkan peran bank sebagai lembaga perantara (financial intermediary)\n  Pernyataan C: Bank bertindak sebagai asymmetric information manager dengan meminimumkan risiko bagi penabung dan menanggung risiko kredit UMKM",
            "ditanyakan": "Menganalisis dan menentukan Benar atau Salah peran bank pada kasus tersebut.",
            "reasoning": "Pernyataan A SALAH karena uang giral primer (uang kartal/inti) diciptakan oleh Bank Sentral (Bank Indonesia); bank umum hanya menciptakan uang giral sekunder lewat mekanisme kredit rekening koran/giro, dan tabungan/deposito adalah kegiatan penghimpunan dana (funding), bukan penciptaan uang primer. Pernyataan B BENAR karena menyalurkan dana dari unit surplus ke unit defisit adalah definisi baku financial intermediary. Pernyataan C BENAR karena penabung tidak perlu tahu detail risiko UMKM peminjam karena bank telah menyaring informasi dan menjamin simpanan penabung.",
            "steps": [
                {
                    "step": 1,
                    "title": "Evaluasi Penciptaan Uang (Pernyataan A)",
                    "explanation": "Uang primer ($M_0$) hanya diciptakan oleh bank sentral. Deposito berjangka termasuk uang kuasi ($M_2$). Pernyataan A adalah SALAH."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Fungsi Intermediasi (Pernyataan B)",
                    "explanation": "Menjembatani mismatch tenor dan likuiditas antara deposan dan debitur UMKM adalah inti fungsi intermediasi. Pernyataan B adalah BENAR."
                },
                {
                    "step": 3,
                    "title": "Evaluasi Pengelolaan Informasi Asimetris (Pernyataan C)",
                    "explanation": "Bank melakukan uji kelayakan kredit (analisis 5C) untuk menanggung risiko gagal bayar kredit sehingga penabung tetap aman. Pernyataan C adalah BENAR."
                }
            ],
            "why_correct": "Pernyataan A Salah (penciptaan uang primer adalah monopoli Bank Indonesia), Pernyataan B Benar (peran perantara keuangan/financial intermediary), dan Pernyataan C Benar (bank mengelola asymmetric information dan menyerap risiko kredit).",
            "tips": ["Uang giral primer hanya dari Bank Sentral; Bank umum bertindak sebagai financial intermediary antara surplus dan deficit unit."],
            "common_mistakes": ["Menganggap bank umum mencetak atau menciptakan uang primer."],
            "official_answer": {"format": "statements", "correct": {"A": "Salah", "B": "Benar", "C": "Benar"}}
        },
        {
            "question_number": 6,
            "question_id": "akt_p1_q06",
            "question_title": "Formula Perkalian Pengolah Angka Spreadsheet (Excel)",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["Spreadsheet Akuntansi", "Rumus Excel", "Operator Aritmatika"],
            "concept_kunci": ["Perkalian Formula =B2*C2", "Fungsi =PRODUCT(B2,C2)", "Sifat Komutatif Perkalian"],
            "glossary": [
                {"term": "PRODUCT", "meaning": "Fungsi bawaan Excel untuk mengalikan seluruh angka yang diberikan sebagai argumen."},
                {"term": "Operator Aritmatika (*)", "meaning": "Tanda bintang pada keyboard yang berfungsi sebagai operator matematika perkalian pada spreadsheet."}
            ],
            "diketahui": "• Tabel spreadsheet akuntansi dengan kolom Kuantitas di sel B2 dan Harga Satuan di sel C2\n• Sel D2 digunakan untuk menghitung Total Harga (Kuantitas × Harga)",
            "ditanyakan": "Pernyataan formula yang BENAR untuk menghitung nilai sel D2 (Pilihan Ganda Kompleks).",
            "reasoning": "Untuk menghitung hasil perkalian antara sel B2 dan C2 pada Microsoft Excel atau Google Spreadsheet, terdapat 3 variasi rumus yang valid:\n1. Menggunakan operator perkalian asterisk: `=B2*C2` (Opsi A benar).\n2. Menggunakan fungsi bawaan perkalian: `=PRODUCT(B2,C2)` (Opsi B benar).\n3. Sifat komutatif perkalian matematis: `=C2*B2` (Opsi E benar).\nOpsi C (`=B2+C2`) salah karena merupakan operasi penjumlahan, bukan perkalian.",
            "steps": [
                {
                    "step": 1,
                    "title": "Evaluasi Operator Perkalian Standar",
                    "explanation": "Formula `=B2*C2` adalah sintaks penulisan perkalian paling mendasar pada sel Excel (Opsi A benar)."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Fungsi Khusus Perkalian Excel",
                    "explanation": "Fungsi `=PRODUCT(B2,C2)` secara komputasi menghasilkan perkalian argumen B2 dan C2 (Opsi B benar)."
                },
                {
                    "step": 3,
                    "title": "Evaluasi Sifat Komutatif Perkalian",
                    "explanation": "Dalam matematika dan spreadsheet, perkalian bersifat komutatif: $B_2 \\times C_2 = C_2 \\times B_2$, sehingga formula `=C2*B2` menghasilkan nilai yang identik (Opsi E benar)."
                }
            ],
            "why_correct": "Pernyataan A, B, dan E benar karena `=B2*C2`, `=PRODUCT(B2,C2)`, dan `=C2*B2` ketiganya merupakan formula perkalian yang sah dan menghasilkan nilai total harga yang sama persis di sel D2.",
            "tips": ["Ingat: tanda perkalian di Excel adalah bintang (*) dan fungsi perkalian adalah PRODUCT."],
            "common_mistakes": ["Memilih tanda tambah (+) atau mengira posisi sel tidak boleh dibalik pada perkalian."],
            "official_answer": {"format": "multiple", "correct": ["A", "B", "E"]}
        }
    ]
}

# 5. MANAJEMEN PERKANTORAN & LAYANAN BISNIS
MANAJEMEN_PERKANTORAN_SOLUTIONS = {
    "package": 1,
    "subject": "Manajemen Perkantoran dan Layanan Bisnis",
    "slug": "manajemen_perkantoran_paket_1",
    "solutions": [
        {
            "question_number": 1,
            "question_id": "mpb_p1_q01",
            "question_title": "Identifikasi Dokumen Administrasi Transaksi Bisnis (Faktur)",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["Dokumen Niaga", "Faktur Penjualan", "Administrasi Transaksi"],
            "concept_kunci": ["Faktur Penjualan (Invoice)", "Penyerahan Barang Kredit/Tagihan"],
            "glossary": [
                {"term": "Faktur Penjualan (Sales Invoice)", "meaning": "Dokumen komersial tertulis yang diterbitkan oleh penjual kepada pembeli yang memuat rincian nama barang, kuantitas, dan total harga penyerahan barang."},
                {"term": "Kwitansi", "meaning": "Tanda bukti penerimaan uang tunai yang ditandatangani oleh penerima."}
            ],
            "diketahui": "• Dokumen diterbitkan oleh PT Maju Jaya (penjual) tanggal 10 Februari 2026\n• Ditujukan Kepada: Toko Sinar Abadi (pembeli)\n• Memuat Barang: 50 dus air mineral dan Harga: Rp2.500.000",
            "ditanyakan": "Jenis dokumen administrasi yang dimaksud berdasarkan format tersebut.",
            "reasoning": "Dokumen yang diterbitkan oleh pihak penjual (PT Maju Jaya) kepada pihak pembeli (Toko Sinar Abadi) yang mencantumkan rincian tanggal, nama barang yang diserahkan, jumlah kuantitas (50 dus), dan total nilai tagihan harga (Rp2.500.000) adalah Faktur Penjualan (sales invoice). Faktur berfungsi sebagai bukti transaksi jual-beli sekaligus dasar penagihan pembayaran.",
            "steps": [
                {
                    "step": 1,
                    "title": "Identifikasi Pihak Penerbit dan Penerima Dokumen",
                    "explanation": "Penerbit adalah perusahaan produsen/distributor (PT Maju Jaya) kepada pelanggan (Toko Sinar Abadi)."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Komponen Isi Dokumen",
                    "explanation": "Dokumen memuat rincian barang dan nilai tagihan. Dokumen ini bukan kwitansi (karena tidak ada tanda tangan penerimaan uang kas 'sudah terima dari...'), bukan nota kas masuk, melainkan faktur penjualan (invoice)."
                }
            ],
            "why_correct": "Opsi B benar karena rincian pengiriman barang dan penetapan nilai tagihan dari penjual kepada pembeli adalah definisi dan format baku dari Faktur Penjualan.",
            "tips": ["Penjual mengirim barang dengan rincian harga = Faktur; Penerima uang kas memberikan bukti pembayaran = Kwitansi."],
            "common_mistakes": ["Menganggap semua dokumen bernilai rupiah adalah kwitansi pembayaran."],
            "official_answer": {"format": "single", "correct": ["B"]}
        },
        {
            "question_number": 2,
            "question_id": "mpb_p1_q02",
            "question_title": "Bentuk Badan Usaha: Perusahaan Perseorangan (PO)",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["Badan Usaha", "Perusahaan Perseorangan", "Hukum Bisnis"],
            "concept_kunci": ["Tanggung Jawab Tak Terbatas Harta Pribadi", "Keputusan Tunggal Mandiri"],
            "glossary": [
                {"term": "Perusahaan Perseorangan", "meaning": "Bentuk badan usaha yang dimiliki, dimodali, dan dikelola oleh satu orang individu dengan tanggung jawab tak terbatas."},
                {"term": "Tanggung Jawab Tak Terbatas", "meaning": "Kewajiban pelunasan utang usaha yang menjangkau kekayaan pribadi pemilik apabila aset bisnis tidak mencukupi."}
            ],
            "diketahui": "• Ciri-ciri badan usaha:\n  1. Modal usaha berasal dari satu sumber dan dikelola sendiri oleh pemiliknya\n  2. Keuntungan dan kerugian sepenuhnya menjadi tanggung jawab pemilik termasuk harta pribadi jika merugi\n  3. Pengambilan keputusan cepat tanpa musyawarah pihak lain\n  4. Tidak memerlukan akta pendirian resmi notaris\n  5. Kelangsungan usaha sangat bergantung pada kondisi pemilik",
            "ditanyakan": "Jenis badan usaha yang paling sesuai dengan kombinasi karakteristik tersebut.",
            "reasoning": "Karakteristik kepemilikan tunggal, modal satu orang, pengambilan keputusan mandiri tanpa rapat pemegang saham, tidak wajib akta notaris berbadan hukum, dan tanggung jawab penuh hingga harta pribadi (unlimited liability) merupakan ciri mutlak dari Perusahaan Perseorangan (sole proprietorship). Bentuk Firma dan CV melibatkan sekutu, PT memiliki tanggung jawab terbatas (modal saham), dan Koperasi berasas kekeluargaan.",
            "steps": [
                {
                    "step": 1,
                    "title": "Analisis Struktur Modal dan Pengambilan Keputusan",
                    "explanation": "Modal satu orang dan keputusan instan tanpa rapat direksi/sekutu mengeliminasi PT, CV, Firma, dan Koperasi."
                },
                {
                    "step": 2,
                    "title": "Analisis Aspek Hukum Tanggung Jawab",
                    "explanation": "Tanggung jawab yang melibatkan seluruh harta pribadi pemilik tanpa batas badan hukum adalah ciri khas perusahaan perseorangan."
                }
            ],
            "why_correct": "Opsi C benar karena perusahaan perseorangan adalah satu-satunya bentuk usaha di mana seluruh modal, pengelolaan, keputusan, dan risiko harta pribadi berada pada satu individu pemilik.",
            "tips": ["Modal 1 orang + tanggung jawab harta pribadi = Perusahaan Perseorangan."],
            "common_mistakes": ["Memilih CV atau Firma yang minimal didirikan oleh dua orang sekutu."],
            "official_answer": {"format": "single", "correct": ["C"]}
        },
        {
            "question_number": 3,
            "question_id": "mpb_p1_q03",
            "question_title": "Klasifikasi Bentuk Transaksi Pasar Konvensional dan E-Commerce",
            "difficulty": "Mudah",
            "estimated_time_seconds": 60,
            "concept_tags": ["Bentuk Pasar", "Pasar Konvensional", "E-Commerce"],
            "concept_kunci": ["Transaksi Tatap Muka Fisik", "Transaksi Digital Daring"],
            "glossary": [
                {"term": "Pasar Konvensional", "meaning": "Mekanisme perdagangan di mana pembeli dan penjual bertemu langsung secara fisik di lokasi toko/gerai."},
                {"term": "E-Commerce", "meaning": "Penyelenggaraan transaksi perdagangan barang atau jasa melalui jaringan internet dan sistem pembayaran elektronik."}
            ],
            "diketahui": "• Penjualan Butik Nusantara:\n  Pernyataan A: Pembeli datang langsung ke toko, mencoba pakaian, dan membayar di kasir\n  Pernyataan B: Pembeli memesan pakaian melalui aplikasi dan melakukan pembayaran via transfer bank\n  Pernyataan C: Pembeli mengirim pesan lewat aplikasi chatting untuk memesan, kemudian mengambil dan membayar langsung di toko",
            "ditanyakan": "Menentukan bentuk pasar (Pasar Konvensional vs e-commerce) untuk masing-masing pernyataan.",
            "reasoning": "Pernyataan A adalah 'Pasar Konvensional' karena interaksi, pemilihan barang fisik, dan pembayaran kasir dilakukan langsung di gerai fisik. Pernyataan B adalah 'e-commerce' karena seluruh proses pemesanan dan pembayaran dilakukan secara elektronik via aplikasi daring. Pernyataan C adalah 'Pasar Konvensional' karena transaksi penyerahan barang dan pembayaran tunai tetap terjadi secara tatap muka langsung di kasir toko fisik (chatting hanya media kontak awal).",
            "steps": [
                {
                    "step": 1,
                    "title": "Evaluasi Pernyataan A",
                    "explanation": "Tatap muka langsung di toko fisik = Pasar Konvensional."
                },
                {
                    "step": 2,
                    "title": "Evaluasi Pernyataan B",
                    "explanation": "Pemesanan via aplikasi dan transfer bank digital = e-commerce."
                },
                {
                    "step": 3,
                    "title": "Evaluasi Pernyataan C",
                    "explanation": "Meskipun ada chat awal, pengambilan dan pembayaran kasir terjadi langsung di toko = Pasar Konvensional."
                }
            ],
            "why_correct": "Pernyataan A: Pasar Konvensional, Pernyataan B: e-commerce, Pernyataan C: Pasar Konvensional, sesuai dengan lokasi fisik dan metode pembayaran penyerahan barang.",
            "tips": ["Bila uang dan barang berpindah tangan secara fisik di dalam toko, bentuk pasarnya adalah konvensional."],
            "common_mistakes": ["Menganggap transaksi yang melibatkan aplikasi chat selalu dihitung e-commerce murni padahal pembayarannya tunai di toko."],
            "official_answer": {"format": "statements", "correct": {"A": "Pasar Konvensional", "B": "e-commerce", "C": "Pasar Konvensional"}}
        },
        {
            "question_number": 4,
            "question_id": "mpb_p1_q04",
            "question_title": "Ergonomi Perkantoran: Pencegahan Carpal Tunnel Syndrome (CTS)",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["K3 Perkantoran", "Ergonomi Mengetik", "Pencegahan CTS"],
            "concept_kunci": ["Inspeksi Sudut Pergelangan Tangan", "Posisi Mengetik Keyboard Ergonomis"],
            "glossary": [
                {"term": "Carpal Tunnel Syndrome (CTS)", "meaning": "Kondisi terjepitnya saraf medianus di terowongan karpal pergelangan tangan akibat gerakan repetitif dan sudut tekuk pergelangan yang salah."},
                {"term": "Ergonomi Kerja", "meaning": "Ilmu penyesuaian lingkungan kerja, peralatan, dan postur tubuh agar pekerja terhindar dari cedera muskuloskeletal."}
            ],
            "diketahui": "• Sebagian besar staf administrasi mengeluhkan kesemutan, mati rasa, dan nyeri pada pergelangan tangan hingga jari setelah jam kerja\n• Diagnosis dokter: Carpal Tunnel Syndrome (CTS)",
            "ditanyakan": "Langkah inspeksi pertama tim K3 yang paling tepat untuk mengidentifikasi akar penyebab dan mencegah keparahan gejala.",
            "reasoning": "CTS pada staf administrasi perkantoran terutama dipicu oleh pengetikan keyboard secara intensif dengan posisi pergelangan tangan yang menekuk (ekstensi/fleksi berlebih) atau bertumpu keras pada tepi meja tajam saat menekan tombol. Langkah inspeksi awal yang paling relevan dan tepat sasaran adalah memeriksa postur dan sudut pergelangan tangan serta teknik mengetik staf saat menggunakan keyboard komputer.",
            "steps": [
                {
                    "step": 1,
                    "title": "Identifikasi Patofisiologi CTS",
                    "explanation": "Tekanan berlebih pada saraf medianus pergelangan tangan timbul ketika pergelangan tangan menekuk ke atas/bawah saat mengetik berjam-jam tanpa sandaran empuk (wrist rest)."
                },
                {
                    "step": 2,
                    "title": "Penetapan Prioritas Inspeksi Ergonomi",
                    "explanation": "Aktivitas utama staf administrasi adalah mengetik dokumen. Maka inspeksi pertama yang harus dilakukan adalah mengevaluasi sudut pergelangan tangan dan tumpuan jari pada keyboard komputer (Opsi A)."
                }
            ],
            "why_correct": "Opsi A benar karena menginspeksi sudut pergelangan tangan dan teknik mengetik pada keyboard merupakan langkah investigasi ergonomis utama untuk mendeteksi sumber tekanan saraf penyebab Carpal Tunnel Syndrome.",
            "tips": ["Posisi mengetik ergonomis: pergelangan tangan harus lurus sejajar (posisi netral), tidak menekuk ke atas atau ke bawah."],
            "common_mistakes": ["Memilih inspeksi monitor (D) yang berhubungan dengan mata lelah, bukan nyeri pergelangan tangan."],
            "official_answer": {"format": "single", "correct": ["A"]}
        },
        {
            "question_number": 5,
            "question_id": "mpb_p1_q05",
            "question_title": "Sistem Kearsipan Terminal Digit Filing",
            "difficulty": "Sulit",
            "estimated_time_seconds": 120,
            "concept_tags": ["Manajemen Kearsipan", "Terminal Digit Filing", "Pengarsipan Surat"],
            "concept_kunci": ["Urutan Terminal Digit: Surat.Folder.Laci", "Urutan Benar 23.40.47"],
            "glossary": [
                {"term": "Terminal Digit Filing", "meaning": "Sistem penyimpanan arsip bernomor di mana pengelompokan diurutkan dari dua angka paling belakang (terminal digit) sebagai laci utama."},
                {"term": "Kode Arsip 3 Kelompok", "meaning": "Format penomoran: [Nomor Urut Surat].[Nomor Folder/Sub-Guide].[Nomor Laci Utama/Terminal]."}
            ],
            "diketahui": "• Surat PT Mitra Sentosa (nomor register: 47)\n• Surat ke-23 dari PT Mitra Sentosa\n• Nomor folder yang digunakan adalah 40\n• Petugas memberi nomor keliru: 47.40.23 dan menaruh di kelompok 47 sebagai laci",
            "ditanyakan": "Pernyataan yang benar mengenai perbaikan penomoran sistem terminal digit tersebut (Pilihan Ganda Kompleks).",
            "reasoning": "Dalam sistem kearsipan Terminal Digit Filing (sistem angka akhir):\n1. Kelompok pertama di depan adalah nomor urut surat (yaitu 23) (Opsi D benar).\n2. Kelompok kedua di tengah adalah nomor folder pembagi (yaitu 40).\n3. Kelompok ketiga di belakang (terminal digit) adalah nomor laci utama (yaitu 47).\nMaka susunan penomoran arsip yang benar adalah: `23.40.47` (Opsi E benar).\nPetugas salah karena menempatkan 47 di depan.",
            "steps": [
                {
                    "step": 1,
                    "title": "Struktur Angka Sistem Terminal Digit",
                    "explanation": "Format baku: [Unit 1: Nomor Urut Arsip].[Unit 2: Nomor Guide/Folder].[Unit 3: Terminal Digit/Laci Utama]."
                },
                {
                    "step": 2,
                    "title": "Identifikasi Posisi Nomor Urut Surat",
                    "explanation": "Surat ke-23 merupakan nomor urut arsip sehingga wajib berada di posisi pertama (Opsi D benar)."
                },
                {
                    "step": 3,
                    "title": "Penyusunan Kode Lengkap",
                    "explanation": "Nomor urut (23), nomor folder (40), dan nomor laci terminal (47) menghasilkan kode: `23.40.47` (Opsi E benar)."
                }
            ],
            "why_correct": "Pernyataan D dan E benar karena pada sistem terminal digit nomor urut surat (23) berada di posisi pertama dan nomor laci (47) berada di posisi terakhir, sehingga susunan penomoran yang tepat adalah 23.40.47.",
            "tips": ["Ingat aturan Terminal Digit: angka laci utama berada di TERMINAL (paling akhir di kanan)!"],
            "common_mistakes": ["Mengira nomor laci berada di awal seperti pada sistem nomor urut langsung."],
            "official_answer": {"format": "multiple", "correct": ["D", "E"]}
        },
        {
            "question_number": 6,
            "question_id": "mpb_p1_q06",
            "question_title": "Standar Pelayanan Prima Penanganan Komplain Digital",
            "difficulty": "Sedang",
            "estimated_time_seconds": 90,
            "concept_tags": ["Pelayanan Prima", "Customer Care Digital", "Penanganan Komplain"],
            "concept_kunci": ["Respon 1x24 Jam dan Empati", "Pelacakan Internal Resi Paket"],
            "glossary": [
                {"term": "Pelayanan Prima (Service Excellence)", "meaning": "Pelayanan terbaik yang melampaui harapan pelanggan dengan sikap tanggap, empati, dan solusi tuntas."},
                {"term": "Tracking Resi Internal", "meaning": "Investigasi riwayat fisik barang di gudang atau kurir melalui sistem logistik internal perusahaan."}
            ],
            "diketahui": "• Email komplain dari Bpk. Hendra (PT Maju Bersama) mengenai dokumen penting nomor resi XYZ-00912 yang terlambat 7 hari (estimasi 3 hari)\n• Call center tidak merespons dan dokumen mendesak untuk legal perusahaan",
            "ditanyakan": "Tindakan staf administrasi senior yang paling tepat sesuai konsep pelayanan prima (Pilihan Ganda Kompleks).",
            "reasoning": "Dalam pelayanan prima menangani komplain pelanggan mendesak: (1) Kirimkan balasan email resmi sesegera mungkin (maksimal 1×24 jam) berisi permohonan maaf yang tulus, konfirmasi resi, dan kepastian estimasi penyelesaian masalah (Opsi B benar); (2) Lakukan tindakan proaktif dengan melacak posisi fisik paket XYZ-00912 pada sistem internal logistik lalu laporkan perkembangannya langsung ke pelanggan (Opsi D benar). Menyuruh pelanggan memantau sendiri (Opsi A) adalah sikap defensif dan melanggar etika pelayanan prima.",
            "steps": [
                {
                    "step": 1,
                    "title": "Penerapan Responsif dan Empati Awal",
                    "explanation": "Balas email dengan cepat (< 24 jam) memuat empati, permohonan maaf, dan nomor kontak petugas penanggung jawab (Opsi B benar)."
                },
                {
                    "step": 2,
                    "title": "Investigasi Solutif Internal",
                    "explanation": "Staf wajib mengecek kendala di manifest internal dan hub logistik, lalu memberikan pembaruan informasi status kepada pengirim (Opsi D benar)."
                }
            ],
            "why_correct": "Pernyataan B dan D benar karena membalas cepat dengan empati dan kepastian waktu serta melakukan investigasi internal atas resi pengiriman adalah standar emas penanganan komplain pelayanan prima.",
            "tips": ["Formula komplain: Dengar/Terima + Minta Maaf + Aksi Solusi Internal + Lapor Balik Cepat."],
            "common_mistakes": ["Menyalahkan pihak ketiga atau meminta pelanggan mengecek tracking sendiri (Opsi A)."],
            "official_answer": {"format": "multiple", "correct": ["B", "D"]}
        }
    ]
}

ALL_MAPEL = [
    ("teknik_mesin_paket_1", "TEKNIK_MESIN_PAKET_1_SOLUTIONS.json", TEKNIK_MESIN_SOLUTIONS),
    ("teknik_otomotif_paket_1", "TEKNIK_OTOMOTIF_PAKET_1_SOLUTIONS.json", TEKNIK_OTOMOTIF_SOLUTIONS),
    ("teknik_jaringan_paket_1", "TEKNIK_JARINGAN_PAKET_1_SOLUTIONS.json", TEKNIK_JARINGAN_SOLUTIONS),
    ("akuntansi_paket_1", "AKUNTANSI_PAKET_1_SOLUTIONS.json", AKUNTANSI_SOLUTIONS),
    ("manajemen_perkantoran_paket_1", "MANAJEMEN_PERKANTORAN_PAKET_1_SOLUTIONS.json", MANAJEMEN_PERKANTORAN_SOLUTIONS),
]

def main():
    # 1. Simpan dan validasi file solusi di data/solution_sources/
    print("=== 1. MENYIMPAN DAN MEMVALIDASI FILE SOLUSI 5 PILAR ===")
    for slug, filename, data in ALL_MAPEL:
        # Validasi struktur
        solution_loader.validate_solution_doc(data)
        out_path = os.path.join(SOL_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Solusi 5 Pilar disimpan & valid: {filename} ({len(data['solutions'])} soal)")

    # 2. Perbarui registry.json
    print("\n=== 2. MEMPERBARUI REGISTRY.JSON ===")
    with open(REG_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    for slug, filename, data in ALL_MAPEL:
        registry[slug] = {"active_source": filename}
        print(f"  [REGISTRY] {slug} -> {filename}")

    with open(REG_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print("  [OK] registry.json berhasil diperbarui!")

    # 3. Suntikkan (merge) pembahasan 5 pilar ke file *_learning.json
    print("\n=== 3. MENYUNTIKKAN DATA PEMBAHASAN KE FILE LEARNING ===")
    for slug, filename, data in ALL_MAPEL:
        learning_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
        if not os.path.isfile(learning_path):
            print(f"  [WARN] File learning tidak ditemukan: {learning_path}")
            continue

        with open(learning_path, "r", encoding="utf-8") as f:
            learning_data = json.load(f)

        sols_by_num = {s["question_number"]: s for s in data["solutions"]}

        for q in learning_data.get("soal", []):
            q_no = q.get("nomor")
            sol = sols_by_num.get(q_no)
            if not sol:
                continue

            # Format 5 Pilar
            glosarium = []
            for g in sol.get("glossary", []):
                t = g.get("term", "")
                m = g.get("meaning", "")
                glosarium.append({"simbol": t, "nama": t, "arti": m})

            langkah = []
            for st in sol.get("steps", []):
                s_num = st.get("step", "")
                s_title = st.get("title", "")
                s_exp = st.get("explanation", "")
                langkah.append(f"**Langkah {s_num}: {s_title}**\n{s_exp}")

            q["pembahasan"] = {
                "diketahui": sol.get("diketahui", ""),
                "ditanyakan": sol.get("ditanyakan", ""),
                "glosarium_simbol": glosarium,
                "mengapa_begini": sol.get("reasoning", ""),
                "konsep_kunci": ", ".join(sol.get("concept_kunci", [])) if isinstance(sol.get("concept_kunci"), list) else sol.get("concept_kunci", ""),
                "langkah_penyelesaian": langkah,
                "tips_trik": " ".join(sol.get("tips", [])) if isinstance(sol.get("tips"), list) else sol.get("tips", ""),
                "why_correct": sol.get("why_correct", ""),
                "common_mistakes": sol.get("common_mistakes", [])
            }

            # Question Prompts untuk AI Tutor
            q["question_prompt"] = [
                f"Apa konsep kunci pada Soal Nomor {q_no} ini?",
                "Mengapa jawaban tersebut merupakan opsi yang paling tepat?",
                "Bagaimana cara cepat menghindari jebakan pada soal ini?",
                "Apa kesalahan umum yang sering dilakukan siswa di topik ini?"
            ]

            # Soal Serupa jika ada
            if sol.get("soal_serupa"):
                q["soal_serupa"] = sol["soal_serupa"]

        with open(learning_path, "w", encoding="utf-8") as f:
            json.dump(learning_data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Pembahasan 5 Pilar & Konteks AI disuntikkan ke: {slug}_learning.json")

    print("\n🎉 SEMUA 5 MAPEL SMK BERHASIL DIBUATKAN SOLUSI 5 PILAR & DIINTEGRASIKAN!")

if __name__ == "__main__":
    main()
