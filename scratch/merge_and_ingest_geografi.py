# -*- coding: utf-8 -*-
"""merge_and_ingest_geografi.py
Parses, audits, and ingests the 10 Geografi solutions from user into:
- data/solution_sources/GEO_PAKET_1_SOLUTIONS.json
- data/solution_sources/registry.json
- data/geografi_paket_1_learning.json
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import solution_loader
from _repair_keys import parse_official_row

KUNCI_PATH = os.path.join(ROOT, "data", "kunci", "geografi_paket_1_kunci.json")
SOL_PATH = os.path.join(ROOT, "data", "solution_sources", "GEO_PAKET_1_SOLUTIONS.json")
REG_PATH = os.path.join(ROOT, "data", "solution_sources", "registry.json")
LRN_PATH = os.path.join(ROOT, "data", "geografi_paket_1_learning.json")

# Data from User (Batch 1: Soal 1-5, Batch 2: Soal 6-10)
USER_SOLUTIONS_RAW = [
    # SOAL 1
    {
      "question_id": "geo_p1_q01",
      "question_number": 1,
      "official_answer": {
        "format": "multiple",
        "correct": ["A", "C"]
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Interpretasi citra penginderaan jauh",
        "Banjir rob (tidal flooding) pesisir",
        "Topografi dataran aluvial pesisir",
        "Perumusan masalah geografis berbasis data spasial"
      ],
      "glossary": [
        {"term": "Rob", "meaning": "Genangan air laut ke daratan akibat pasang naik yang melampaui elevasi lahan pesisir yang rendah dan datar."},
        {"term": "Interpretasi citra", "meaning": "Proses mengenali objek pada citra berdasarkan rona, bentuk, pola, ukuran, dan tekstur untuk menarik kesimpulan keruangan."},
        {"term": "Dataran aluvial pesisir", "meaning": "Daratan rendah hasil pengendapan sedimen sungai dan laut, umumnya memiliki elevasi mendekati muka laut sehingga rentan tergenang."}
      ],
      "reasoning": "Citra memperlihatkan genangan air laut yang merambah ke tambak, sawah, permukiman, dan jalan di dataran rendah yang berbatasan langsung dengan laut. Karena genangan hanya mungkin terjadi jika elevasi wilayah tersebut rendah dan datar, maka fenomena ini berkaitan erat dengan hubungan antara pasang air laut dan topografi wilayah (opsi C). Selain itu, karena tambak, sawah, permukiman, dan jalan yang terendam merupakan basis mata pencaharian dan mobilitas penduduk, dampak yang paling mendesak untuk diteliti lebih lanjut adalah pengaruhnya terhadap perekonomian penduduk (opsi A). Opsi B terlalu umum karena menanyakan jenis-jenis bencana alam secara luas, padahal citra hanya menunjukkan satu fenomena spesifik yaitu rob. Opsi D dan E membahas isu pendidikan lingkungan dan mitigasi di sekolah yang tidak dapat dijawab atau diverifikasi langsung dari citra satelit tersebut.",
      "steps": [
        {"step": 1, "title": "Interpretasi Unsur Citra Satelit", "explanation": "Mengenali rona hijau kebiruan sebagai badan air laut, pola petak-petak sebagai tambak/sawah, serta kluster garis dan bangunan sebagai jalan dan permukiman yang tergenang."},
        {"step": 2, "title": "Analisis Kaitan Genangan dengan Topografi Rendah", "explanation": "Menyimpulkan bahwa genangan hanya bisa merambah jauh ke daratan jika wilayah tersebut memiliki topografi rendah dan datar, sehingga terjadi keterkaitan langsung dengan pasang air laut."},
        {"step": 3, "title": "Penilaian Dampak terhadap Aktivitas Ekonomi Lahan", "explanation": "Mengidentifikasi bahwa lahan yang tergenang merupakan area produksi (tambak, sawah) dan infrastruktur (jalan), sehingga dampaknya langsung menyentuh perekonomian penduduk setempat."},
        {"step": 4, "title": "Seleksi Rumusan Masalah Berbasis Data Spasial", "explanation": "Menyaring pilihan rumusan masalah dengan menyingkirkan opsi yang terlalu umum atau di luar konteks citra, dan mempertahankan opsi yang benar-benar dapat dijawab dengan data spasial yang tersedia."}
      ],
      "why_correct": "Kombinasi A dan C tepat karena keduanya dapat dijawab langsung menggunakan data spasial pada citra: satu berkaitan dengan variabel fisik (topografi-pasang laut), satu lagi dengan dampak sosial-ekonomi wilayah, sedangkan opsi lain bersifat terlalu umum atau berada di luar cakupan data citra.",
      "tips": [
        "Cocokkan setiap pilihan rumusan masalah dengan unsur visual spesifik yang benar-benar tampak pada citra, bukan opsi yang bersifat umum.",
        "Rumusan masalah geografis yang baik menghubungkan fenomena fisik (topografi, iklim, hidrologi) dengan dampak sosial-ekonomi wilayah."
      ],
      "common_mistakes": [
        "Memilih opsi B karena dianggap 'aman' dan umum, padahal soal menuntut spesifisitas terhadap fenomena rob yang tampak di citra.",
        "Terjebak memilih D atau E karena beranggapan soal geografi selalu bermuara pada isu lingkungan sekolah, padahal fokus soal ini adalah analisis spasial citra."
      ],
      "soal_serupa": {
        "pertanyaan": "Sebuah citra satelit pesisir Kabupaten Pekalongan memperlihatkan genangan air laut merambah ke area tambak garam, permukiman nelayan, dan jalan pantura di dataran rendah dekat garis pantai. Rumusan masalah manakah yang tepat untuk menindaklanjuti fenomena tersebut?",
        "opsi": [
          {"key": "A", "text": "Bagaimana pengaruh genangan air laut terhadap aktivitas ekonomi nelayan dan petani garam?"},
          {"key": "B", "text": "Apa saja jenis awan yang menyebabkan hujan deras di wilayah pesisir?"},
          {"key": "C", "text": "Bagaimana hubungan antara pasang air laut dengan kondisi topografi rendah wilayah pesisir Pekalongan?"},
          {"key": "D", "text": "Mengapa nelayan perlu memahami pentingnya pelestarian terumbu karang?"}
        ],
        "kunci": "A, C",
        "pembahasan_singkat": "A dan C tepat karena genangan yang merambah ke tambak garam dan permukiman berkaitan langsung dengan topografi rendah pesisir (C) serta berdampak pada perekonomian nelayan dan petani garam (A); B dan D tidak relevan dengan data yang tampak pada citra."
      }
    },
    # SOAL 2
    {
      "question_id": "geo_p1_q02",
      "question_number": 2,
      "official_answer": {
        "format": "per_statement",
        "statements": {"A": "Benar", "B": "Benar", "C": "Salah"}
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Danau purba (paleolake) akibat bendungan vulkanik",
        "Sedimentasi dan pengeringan danau",
        "Bukti arkeologis hunian purba",
        "Interpretasi data primer (grafik dan peta)"
      ],
      "glossary": [
        {"term": "Danau purba (paleolake)", "meaning": "Danau yang terbentuk pada masa lampau akibat proses geologis tertentu dan kini telah mengering atau menyusut jauh dari ukuran aslinya."},
        {"term": "Obsidian", "meaning": "Batuan vulkanik berupa kaca alami yang sering dimanfaatkan manusia purba sebagai bahan perkakas serpih bermata tajam."},
        {"term": "Curug", "meaning": "Istilah Sunda untuk air terjun; dalam konteks ini menjadi titik ambang alami yang tererosi hingga membuka jalur drainase danau."}
      ],
      "reasoning": "Grafik menunjukkan kedalaman danau mencapai puncak sekitar 32-33 meter setelah erupsi Gunung Sunda 125.000 tahun lalu, membuktikan bahwa Cekungan Bandung memang pernah terendam air dalam skala danau besar, sehingga pernyataan A benar. Grafik juga memperlihatkan penurunan tajam kedalaman setelah longsor 16.000 tahun lalu hingga mencapai nol sekitar 5.000 tahun lalu, dan peta inset menunjukkan sebaran temuan obsidian di sekeliling tepi bekas danau, yang mengindikasikan hunian manusia purba berkembang setelah proses pengeringan berlangsung, sehingga pernyataan B benar. Namun, tidak ada satu pun data pada teks, grafik, maupun peta yang menyebutkan aktivitas pertanian di utara danau; yang disebutkan hanya perkakas obsidian sebagai bukti hunian, sehingga klaim spesifik tentang pengembangan pertanian tidak didukung data dan dinyatakan salah (C).",
      "steps": [
        {"step": 1, "title": "Membaca Kurva Fluktuasi Kedalaman Danau", "explanation": "Mengidentifikasi tiga fase utama pada grafik: pembendungan oleh erupsi Gunung Sunda (125.000 SM), pembukaan kembali aliran akibat longsor (16.000 SM), dan pengeringan total (5.000 SM)."},
        {"step": 2, "title": "Mengaitkan Fase Geologis dengan Bukti Arkeologis", "explanation": "Menghubungkan periode pengeringan danau dengan sebaran temuan obsidian pada peta inset untuk menilai kapan manusia mulai menghuni kawasan tepi danau secara intensif."},
        {"step": 3, "title": "Verifikasi Klaim terhadap Data yang Tersedia", "explanation": "Mengecek setiap pernyataan terhadap fakta eksplisit pada teks, grafik, dan peta; pernyataan yang tidak memiliki dasar data eksplisit, seperti klaim aktivitas pertanian, dinyatakan tidak terbukti atau salah."}
      ],
      "why_correct": "A benar karena grafik membuktikan adanya genangan air berkedalaman puluhan meter di masa lampau; B benar karena korelasi waktu antara pengeringan danau dan sebaran artefak obsidian di tepi bekas cekungan; C salah karena data yang tersedia hanya menyebut perkakas obsidian sebagai bukti hunian, bukan aktivitas pertanian.",
      "tips": [
        "Cocokkan setiap pernyataan Benar-Salah dengan bukti eksplisit pada grafik, peta, atau teks; jangan menyimpulkan sesuatu yang tidak tertulis.",
        "Perhatikan sumbu waktu pada grafik untuk memastikan urutan kejadian geologis dan arkeologis tidak tertukar."
      ],
      "common_mistakes": [
        "Menganggap pernyataan C benar karena mengasosiasikan 'danau purba yang subur' dengan otomatis adanya pertanian, padahal stimulus hanya menyebut perkakas, bukan pertanian.",
        "Salah membaca sumbu waktu grafik sehingga keliru menentukan urutan fase pengeringan danau dan waktu munculnya bukti hunian."
      ],
      "soal_serupa": {
        "pertanyaan": "Sebuah grafik menunjukkan bahwa Danau Purba X terbentuk akibat bendungan aliran sungai oleh material erupsi gunung berapi sekitar 80.000 tahun lalu dengan kedalaman puncak 25 meter, kemudian mengalami penurunan drastis akibat jebolnya tanggul alami 10.000 tahun lalu hingga akhirnya mengering sekitar 4.000 tahun lalu. Peta inset menunjukkan sebaran alat serpih batu di sekeliling bekas cekungan danau. Manakah pernyataan yang paling tepat berdasarkan data tersebut?",
        "opsi": [
          {"key": "A", "text": "Wilayah cekungan tersebut tidak pernah tergenang air dalam sejarah geologisnya."},
          {"key": "B", "text": "Manusia purba diperkirakan mulai menghuni kawasan tersebut setelah danau mengalami pengeringan."},
          {"key": "C", "text": "Sebaran alat serpih membuktikan adanya aktivitas pertanian intensif di kawasan tersebut."},
          {"key": "D", "text": "Kedalaman danau terus meningkat tanpa henti sejak awal pembentukannya."}
        ],
        "kunci": "B",
        "pembahasan_singkat": "B benar karena sebaran alat serpih di sekeliling bekas cekungan berkorelasi dengan periode setelah danau mengering; A dan D bertentangan dengan grafik yang jelas menunjukkan fluktuasi kedalaman, sedangkan C tidak didukung data karena hanya alat serpih yang disebutkan, bukan bukti pertanian."
      }
    },
    # SOAL 3
    {
      "question_id": "geo_p1_q03",
      "question_number": 3,
      "official_answer": {
        "format": "per_statement",
        "statements": {"A": "Salah", "B": "Benar", "C": "Benar"}
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Abrasi pantai",
        "Alih fungsi lahan mangrove",
        "Restorasi ekosistem pesisir",
        "Pembangunan berkelanjutan (sustainable development)"
      ],
      "glossary": [
        {"term": "Abrasi", "meaning": "Proses pengikisan garis pantai oleh energi gelombang laut, yang dapat dipercepat oleh hilangnya vegetasi pelindung seperti mangrove."},
        {"term": "Mangrove", "meaning": "Ekosistem hutan bakau di zona pasang-surut yang berfungsi meredam energi gelombang dan menahan sedimen pesisir."},
        {"term": "Ekowisata berbasis konservasi", "meaning": "Model wisata yang memadukan pelestarian lingkungan dengan pemberdayaan ekonomi masyarakat lokal."}
      ],
      "reasoning": "Teks secara eksplisit menyatakan bahwa abrasi 'diperparah oleh konversi hutan mangrove menjadi tambak udang', yakni aktivitas antropogenik, sehingga penyebabnya bukan murni faktor alami; teks bahkan menyebut kombinasi faktor alami dan aktivitas manusia, sehingga pernyataan A yang menyatakan penyebabnya murni alami dinilai salah. Program restorasi yang memadukan penanaman mangrove dengan pemberdayaan masyarakat sebagai pengelola wisata edukasi persis mencontohkan prinsip pembangunan berkelanjutan yang menyeimbangkan aspek ekologi dan ekonomi, sehingga pernyataan B benar. Data monitoring tahun 2023 secara kuantitatif menunjukkan penurunan laju abrasi rata-rata 10 persen per tahun di titik-titik kritis setelah program penanaman berjalan, sehingga secara empiris mendukung klaim bahwa penanaman mangrove efektif mengurangi abrasi, menjadikan pernyataan C benar.",
      "steps": [
        {"step": 1, "title": "Mengidentifikasi Penyebab Abrasi dari Teks", "explanation": "Membedakan antara faktor alami murni dan faktor antropogenik (alih fungsi lahan menjadi tambak udang) yang disebutkan secara eksplisit dalam narasi kasus."},
        {"step": 2, "title": "Menilai Kriteria Pengelolaan Berkelanjutan", "explanation": "Mencocokkan program ekowisata berbasis konservasi dengan prinsip keberlanjutan yang mencakup dimensi ekologi, ekonomi, dan sosial masyarakat."},
        {"step": 3, "title": "Menganalisis Data Kuantitatif Hasil Monitoring", "explanation": "Menggunakan angka penurunan laju abrasi 10 persen per tahun sebagai bukti empiris efektivitas program restorasi mangrove."}
      ],
      "why_correct": "A salah karena penyebab abrasi bukan murni alami, melainkan diperparah oleh alih fungsi lahan mangrove menjadi tambak; B benar karena ekowisata berbasis konservasi memenuhi prinsip pengelolaan berkelanjutan; C benar karena data monitoring membuktikan penurunan laju abrasi setelah penanaman mangrove.",
      "tips": [
        "Waspadai kata seperti 'murni' atau 'hanya' dalam pernyataan Benar-Salah, karena sering menjebak jika teks aslinya menyebutkan kombinasi beberapa faktor.",
        "Data kuantitatif (persentase, angka statistik) dalam teks biasanya menjadi bukti langsung untuk menilai kebenaran suatu pernyataan."
      ],
      "common_mistakes": [
        "Langsung menganggap pernyataan A benar karena abrasi identik dengan proses alam, tanpa membaca detail bahwa teks menyebut kombinasi dengan aktivitas manusia sebagai faktor pemberat.",
        "Mengabaikan angka spesifik hasil monitoring sehingga ragu-ragu menilai pernyataan C meskipun datanya eksplisit dan mendukung."
      ],
      "soal_serupa": {
        "pertanyaan": "Kawasan Segara Anakan di Cilacap mengalami degradasi hutan mangrove akibat kombinasi sedimentasi alami dari Sungai Citanduy dan alih fungsi lahan menjadi tambak ikan oleh penduduk. Pemerintah bersama masyarakat kemudian melakukan penanaman kembali mangrove sekaligus mengembangkan wisata edukasi ekosistem pesisir, yang berhasil menekan laju kerusakan garis pantai. Pernyataan manakah yang paling tepat berdasarkan kasus tersebut?",
        "opsi": [
          {"key": "A", "text": "Kerusakan mangrove Segara Anakan murni disebabkan oleh proses sedimentasi alami tanpa campur tangan manusia."},
          {"key": "B", "text": "Program penanaman mangrove dan wisata edukasi mencerminkan prinsip pengelolaan sumber daya berkelanjutan."},
          {"key": "C", "text": "Wisata edukasi ekosistem pesisir tidak memberikan manfaat ekonomi bagi masyarakat setempat."},
          {"key": "D", "text": "Penanaman mangrove terbukti tidak berpengaruh terhadap laju kerusakan garis pantai."}
        ],
        "kunci": "B",
        "pembahasan_singkat": "B benar karena memadukan konservasi ekologi dan pemberdayaan ekonomi masyarakat sesuai prinsip keberlanjutan; A salah karena kerusakan disebabkan kombinasi faktor alami dan manusia; C dan D bertentangan dengan hasil positif program yang disebutkan."
      }
    },
    # SOAL 4
    {
      "question_id": "geo_p1_q04",
      "question_number": 4,
      "official_answer": {
        "format": "per_statement",
        "statements": {"A": "Benar", "B": "Salah", "C": "Benar"}
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Vulkanisme dan kesuburan tanah",
        "Tanah andosol",
        "Perbedaan pelapukan abu vulkanik dan aliran lava",
        "Siklus pemulihan lahan pascaerupsi"
      ],
      "glossary": [
        {"term": "Andosol", "meaning": "Jenis tanah vulkanik berwarna gelap, kaya bahan organik dan mineral hasil pelapukan abu vulkanik, sangat subur untuk pertanian hortikultura."},
        {"term": "Piroklastik", "meaning": "Material vulkanik lepas berupa abu, lapili, dan bom vulkanik yang dikeluarkan saat erupsi eksplosif."},
        {"term": "Aliran lava", "meaning": "Magma cair yang keluar ke permukaan dan membeku menjadi batuan beku masif seperti basalt atau andesit, berbeda tekstur dan sifat dari abu vulkanik."}
      ],
      "reasoning": "Abu vulkanik yang telah melapuk mengandung unsur hara makro seperti kalium dan fosfor serta unsur mikro lain yang esensial bagi tanaman, sebagaimana terlihat pada kesuburan tanah andosol di sekitar gunung api aktif pada foto lahan sayuran yang subur, sehingga pernyataan A benar. Namun, generalisasi bahwa letusan gunung berapi 'selalu' merusak 'seluruh' lahan pertanian dan membuatnya tak terpakai 'selama puluhan tahun' tidak akurat, karena foto justru menunjukkan lahan pascaletusan kembali produktif dalam waktu yang relatif singkat setelah abu melapuk, sehingga pernyataan mutlak ini dinilai salah (B). Berbeda dengan abu vulkanik yang berbentuk partikel halus dan cepat melapuk, aliran lava membeku menjadi batuan beku masif yang proses pelapukannya menjadi tanah membutuhkan rentang waktu geologis yang sangat panjang, sehingga secara praktis dalam skala waktu manusia lahan bekas aliran lava dianggap tidak dapat dimanfaatkan kembali untuk pertanian, menjadikan pernyataan C benar.",
      "steps": [
        {"step": 1, "title": "Mengidentifikasi Kandungan Hara Abu Vulkanik", "explanation": "Menjelaskan proses pelapukan abu vulkanik yang menghasilkan mineral kalium, fosfor, dan kalsium sehingga meningkatkan kesuburan tanah di sekitar gunung api."},
        {"step": 2, "title": "Mengkritisi Pernyataan Absolut atau Generalisasi Berlebihan", "explanation": "Menguji kata 'selalu' dan 'seluruh' pada pernyataan B terhadap bukti visual lahan yang justru kembali subur dan produktif pascaerupsi."},
        {"step": 3, "title": "Membandingkan Material Piroklastik dengan Aliran Lava", "explanation": "Membedakan sifat fisik dan kecepatan pelapukan antara abu vulkanik yang halus dan cepat menyuburkan tanah dengan aliran lava yang padat dan sangat lambat melapuk."}
      ],
      "why_correct": "A benar karena didukung fakta agronomis kesuburan tanah andosol dari pelapukan abu vulkanik; B salah karena memuat generalisasi mutlak yang bertentangan dengan bukti lapangan berupa lahan yang justru subur; C benar karena aliran lava yang padat memerlukan waktu pelapukan jauh lebih lama dibanding abu vulkanik, sehingga secara praktis belum dapat segera dimanfaatkan kembali.",
      "tips": [
        "Waspadai kata-kata mutlak seperti 'selalu', 'tidak pernah', atau 'seluruh' dalam pernyataan Benar-Salah karena sering menjadi kunci pernyataan tersebut salah, kecuali benar-benar didukung fakta mutlak.",
        "Bedakan karakteristik abu vulkanik (partikel halus, cepat menyuburkan tanah) dengan lava (batuan padat, sangat lambat melapuk) saat menjawab soal vulkanisme dan pertanian."
      ],
      "common_mistakes": [
        "Menyamakan abu vulkanik dan lava sebagai satu material yang sama, sehingga salah menilai pernyataan C.",
        "Terpaku pada gambar sayuran yang subur lalu menganggap pernyataan B otomatis benar tanpa mencermati kata 'selalu' dan 'puluhan tahun' yang bersifat generalisasi berlebihan."
      ],
      "soal_serupa": {
        "pertanyaan": "Di lereng Gunung Kelud, lahan yang tertutup abu vulkanik hasil erupsi tahun-tahun sebelumnya kini kembali ditanami tembakau dan sayuran dengan hasil melimpah, sementara area yang dilalui aliran lava membeku tetap berupa hamparan batuan tandus tanpa vegetasi hingga bertahun-tahun kemudian. Pernyataan manakah yang paling tepat menjelaskan fenomena tersebut?",
        "opsi": [
          {"key": "A", "text": "Abu vulkanik dan aliran lava memiliki kecepatan pelapukan yang sama sehingga sama-sama cepat subur."},
          {"key": "B", "text": "Abu vulkanik melapuk lebih cepat menjadi tanah subur dibanding batuan lava yang padat dan masif."},
          {"key": "C", "text": "Lahan yang dilalui aliran lava selalu lebih subur daripada lahan yang tertutup abu vulkanik."},
          {"key": "D", "text": "Kesuburan lahan vulkanik tidak berkaitan dengan jenis material yang dikeluarkan saat erupsi."}
        ],
        "kunci": "B",
        "pembahasan_singkat": "B benar karena abu vulkanik yang berpartikel halus melapuk jauh lebih cepat menjadi tanah subur dibanding batuan lava masif yang membutuhkan waktu pelapukan sangat lama, sesuai kontras kondisi lahan pada ilustrasi."
      }
    },
    # SOAL 5
    {
      "question_id": "geo_p1_q05",
      "question_number": 5,
      "official_answer": {
        "format": "single",
        "correct": ["B"]
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Interpretasi citra penginderaan jauh gunung api",
        "Pemetaan Kawasan Rawan Bencana (KRB)",
        "Produk aplikasi citra satelit",
        "Zonasi bahaya vulkanik"
      ],
      "glossary": [
        {"term": "KRB (Kawasan Rawan Bencana)", "meaning": "Zona wilayah yang berpotensi terdampak bahaya tertentu, dalam hal ini erupsi gunung api, berdasarkan sejarah dan karakter bahaya letusan sebelumnya."},
        {"term": "Piroklastik", "meaning": "Aliran material panas hasil letusan eksplosif yang bergerak menuruni lereng gunung api mengikuti alur lembah."},
        {"term": "Interpretasi citra multispektral", "meaning": "Analisis pola rona dan bentuk objek pada citra satelit untuk mengekstraksi informasi tematik seperti sebaran aliran lahar atau piroklastik."}
      ],
      "reasoning": "Citra yang diberikan menampilkan unsur-unsur kebencanaan vulkanik secara spesifik, yaitu sebaran aliran piroklastik, jatuhan abu, dan lahar yang menyebar radial mengikuti lembah sungai di sekitar kaldera. Data spasial berupa pola aliran material vulkanik terhadap topografi semacam ini merupakan input utama untuk menyusun peta Kawasan Rawan Bencana letusan gunung api, yang memetakan zona-zona berisiko berdasarkan jalur sebaran material erupsi sebelumnya. Peta jenis vegetasi dan peta penggunaan lahan memang dapat diturunkan dari citra optik secara umum, tetapi tidak secara spesifik memanfaatkan unsur bahaya vulkanik yang ditonjolkan pada citra ini; peta stratigrafi batuan memerlukan data susunan lapisan bawah permukaan yang tidak tersedia dari citra optik; peta oksigen terlarut merupakan parameter kualitas perairan yang tidak relevan dengan objek darat vulkanik pada citra tersebut.",
      "steps": [
        {"step": 1, "title": "Mengenali Unsur Interpretasi Citra Vulkanik", "explanation": "Mengidentifikasi kaldera, kubah lava, aliran piroklastik, dan sebaran lahar sebagai objek utama yang tampak pada citra."},
        {"step": 2, "title": "Menghubungkan Pola Sebaran Material dengan Potensi Bahaya", "explanation": "Menganalisis arah radial aliran piroklastik dan lahar yang mengikuti lembah sungai sebagai indikator jalur bahaya potensial di masa depan."},
        {"step": 3, "title": "Menentukan Produk Pemetaan yang Sesuai", "explanation": "Mencocokkan data spasial bahaya vulkanik yang teridentifikasi dengan jenis produk pemetaan tematik yang paling relevan, yaitu peta Kawasan Rawan Bencana."}
      ],
      "why_correct": "Data spasial yang tampak, berupa aliran piroklastik, lahar, dan jatuhan abu di sekitar kaldera aktif, merupakan unsur kunci penyusun peta Kawasan Rawan Bencana letusan gunung api, sehingga opsi B adalah produk analisis paling sesuai dibanding opsi lain yang tidak relevan dengan fokus kebencanaan vulkanik pada citra.",
      "tips": [
        "Saat soal menampilkan citra dengan unsur bahaya seperti aliran piroklastik, lahar, longsor, atau banjir, arahkan jawaban ke produk peta tematik kebencanaan (KRB), bukan peta umum seperti vegetasi atau penggunaan lahan.",
        "Kenali ciri visual aliran piroklastik dan lahar, yaitu pola menyebar radial mengikuti lembah atau sungai dari puncak gunung api."
      ],
      "common_mistakes": [
        "Memilih peta penggunaan lahan karena melihat hutan dan area lain pada citra, padahal fokus data citra adalah unsur bahaya vulkanik, bukan pemanfaatan lahan.",
        "Memilih peta stratigrafi batuan karena mengasosiasikan gunung api dengan batuan, padahal stratigrafi memerlukan data susunan lapisan bawah permukaan yang tidak dapat diperoleh dari citra optik permukaan."
      ],
      "soal_serupa": {
        "pertanyaan": "Sebuah citra satelit resolusi tinggi memperlihatkan kawah aktif Gunung Sinabung dengan jejak aliran piroklastik dan lahar yang menyebar mengikuti lembah-lembah sungai di lerengnya, serta beberapa desa yang berada di sekitar jalur aliran tersebut. Produk analisis yang paling tepat dihasilkan dari citra tersebut adalah ....",
        "opsi": [
          {"key": "A", "text": "peta jenis tanah"},
          {"key": "B", "text": "peta kawasan rawan bencana"},
          {"key": "C", "text": "peta kepadatan penduduk"},
          {"key": "D", "text": "peta iklim wilayah"}
        ],
        "kunci": "B",
        "pembahasan_singkat": "B tepat karena jejak aliran piroklastik dan lahar yang mengikuti lembah sungai adalah data spasial utama untuk menyusun peta Kawasan Rawan Bencana, sedangkan opsi lain tidak relevan dengan unsur bahaya vulkanik yang ditonjolkan pada citra."
      }
    },
    # SOAL 6
    {
      "question_id": "geo_p1_q06",
      "question_number": 6,
      "official_answer": {
        "format": "single",
        "correct": ["D"]
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Megapolitan dan wilayah fungsional kota",
        "Peri-urbanisasi",
        "Migrasi dan pertumbuhan penduduk perkotaan",
        "Kota satelit"
      ],
      "glossary": [
        {"term": "Megapolitan", "meaning": "Kawasan perkotaan raksasa yang terbentuk dari penggabungan beberapa kota atau wilayah metropolitan yang saling terhubung secara fungsional."},
        {"term": "Peri-urbanisasi", "meaning": "Proses penyebaran penduduk dan aktivitas perkotaan ke wilayah pinggiran (peri-urban) di luar batas kota inti akibat tekanan ruang di pusat kota."},
        {"term": "Kota satelit", "meaning": "Kota kecil hingga menengah di sekitar kota besar yang berkembang menampung limpahan penduduk dan aktivitas ekonomi dari kota inti."}
      ],
      "reasoning": "Tekanan ruang, infrastruktur, dan layanan publik di Jakarta yang terus meningkat akibat migrasi, sementara lahan di pusat kota semakin terbatas dan mahal, mendorong pola pergerakan penduduk yang paling realistis, yaitu menyebar ke wilayah pinggiran dan kota-kota satelit di luar Jabodetabek, sesuai dengan konsep peri-urbanisasi yang menjadi ciri khas pertumbuhan kawasan megapolitan (opsi D). Opsi C yang menyatakan konsentrasi di pusat kota justru bertentangan dengan realitas keterbatasan ruang kota inti yang mendorong ekspansi wilayah fungsional ke luar. Opsi A bertentangan dengan tren migrasi yang terus meningkat sesuai stimulus, sedangkan opsi B dan E terlalu sempit karena mengasumsikan pemerataan mutlak atau konsentrasi hanya di kawasan industri tertentu, yang tidak mencerminkan pola umum perkembangan kawasan megapolitan.",
      "steps": [
        {"step": 1, "title": "Mengidentifikasi Tekanan Ruang di Kota Inti", "explanation": "Menganalisis bahwa migrasi terus-menerus menyebabkan keterbatasan lahan, kemacetan, dan naiknya harga properti di kota inti Jakarta."},
        {"step": 2, "title": "Menghubungkan Tekanan Ruang dengan Teori Perkembangan Kota", "explanation": "Menerapkan konsep peri-urbanisasi, yaitu limpahan penduduk dan aktivitas kota inti menyebar ke wilayah pinggiran dan kota-kota satelit yang lahannya lebih luas dan terjangkau."},
        {"step": 3, "title": "Memvalidasi Pola dengan Konteks Megapolitan Jabodetabek", "explanation": "Mengaitkan fenomena riil pertumbuhan kota-kota penyangga seperti Bekasi, Tangerang, Bogor, dan Depok sebagai bukti nyata pola peri-urbanisasi pada kawasan megapolitan Jakarta."}
      ],
      "why_correct": "Opsi D adalah pola paling logis dan sesuai teori perkembangan kota karena migrasi terus-menerus ke Jakarta yang lahannya terbatas mendorong penyebaran penduduk ke wilayah pinggiran dan kota satelit, sebagaimana dicirikan oleh perkembangan kawasan megapolitan itu sendiri.",
      "tips": [
        "Pahami bahwa istilah 'megapolitan' identik dengan perluasan wilayah fungsional kota ke luar batas administratif inti, sehingga jawaban yang tepat biasanya mengarah pada penyebaran, bukan pemusatan, penduduk.",
        "Kenali istilah kunci seperti peri-urbanisasi, konurbasi, dan kota satelit sebagai penanda pola spasial pada soal-soal dinamika kota besar."
      ],
      "common_mistakes": [
        "Memilih opsi C karena berpikir kota besar selalu menarik penduduk ke pusatnya, padahal soal justru menekankan perluasan wilayah fungsional ke luar Jabodetabek.",
        "Memilih opsi A karena mengasosiasikan tekanan hidup kota dengan migrasi balik ke desa, padahal stimulus menegaskan migrasi terus meningkat."
      ],
      "soal_serupa": {
        "pertanyaan": "Kawasan Bandung Raya yang mencakup Kota Bandung, Kabupaten Bandung, Kabupaten Bandung Barat, dan Kota Cimahi terus mengalami tekanan ruang akibat migrasi penduduk dan keterbatasan lahan di Kota Bandung sebagai kota inti. Bagaimana kemungkinan pola pergerakan penduduk di kawasan tersebut berkembang di masa depan?",
        "opsi": [
          {"key": "A", "text": "Penduduk akan terkonsentrasi penuh di pusat Kota Bandung karena fasilitas terlengkap."},
          {"key": "B", "text": "Urbanisasi akan berhenti karena masyarakat memilih menetap permanen di kampung halaman."},
          {"key": "C", "text": "Penduduk akan menyebar ke wilayah pinggiran seperti Kabupaten Bandung Barat dan Cimahi membentuk pola peri-urbanisasi."},
          {"key": "D", "text": "Pergerakan penduduk hanya akan terjadi di satu kawasan industri tertentu saja."}
        ],
        "kunci": "C",
        "pembahasan_singkat": "C benar karena keterbatasan lahan di kota inti mendorong penyebaran penduduk ke wilayah pinggiran seperti Kabupaten Bandung Barat dan Cimahi, membentuk pola peri-urbanisasi khas kawasan megapolitan; opsi lain bertentangan dengan tren migrasi dan keterbatasan ruang yang disebutkan."
      }
    },
    # SOAL 7
    {
      "question_id": "geo_p1_q07",
      "question_number": 7,
      "official_answer": {
        "format": "per_statement",
        "statements": {"A": "Benar", "B": "Benar", "C": "Salah"}
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Persebaran bioma dunia",
        "Pola adaptasi manusia terhadap lingkungan (posibilisme lingkungan)",
        "Peta tematik sejarah keruangan",
        "Zona iklim dan corak kehidupan"
      ],
      "glossary": [
        {"term": "Bioma", "meaning": "Ekosistem berskala besar yang dicirikan oleh iklim dan vegetasi dominan tertentu, seperti hutan hujan tropis, tundra, atau stepa."},
        {"term": "Berburu dan meramu (hunter-gatherer)", "meaning": "Pola pemenuhan kebutuhan hidup dengan mengandalkan sumber daya alam liar tanpa budidaya menetap, umum ditemukan di lingkungan bersumber daya musiman atau ekstrem."},
        {"term": "Posibilisme lingkungan", "meaning": "Konsep yang menjelaskan bahwa kondisi lingkungan (iklim, bioma) membuka berbagai kemungkinan pola aktivitas manusia, bukan menentukannya secara mutlak."}
      ],
      "reasoning": "Legenda peta secara eksplisit mengelompokkan Asia Tenggara dan Nusantara ke dalam kategori Agraris berwarna merah muda, sejalan dengan narasi bahwa curah hujan tinggi dan tanah subur di kawasan tropis mendukung pertanian menetap seperti padi sawah, sehingga pernyataan A benar. Wilayah lintang tinggi seperti Kanada utara, Alaska, dan Siberia utara dikategorikan sebagai Berburu dan Meramu berwarna hijau zaitun, sesuai kondisi iklim dingin ekstrem yang tidak mendukung pertanian menetap, sehingga pernyataan B benar. Namun, peta tidak mengkategorikan lintang sedang secara umum sebagai kelompok berburu musiman; kawasan lintang sedang seperti Eropa justru masuk kategori Agraris, sedangkan kategori kombinasi agraris/berburu-meramu hanya berlaku spesifik untuk kawasan stepa Asia Tengah, bukan lintang sedang secara keseluruhan, sehingga pernyataan C tidak didukung data peta dan dinyatakan salah.",
      "steps": [
        {"step": 1, "title": "Membaca Legenda Peta Tematik Bioma", "explanation": "Mengidentifikasi kategori warna pada peta, yaitu Agraris, Berburu-Meramu, Kombinasi, Tutupan Es, dan Wilayah Tidak Dihuni, beserta cakupan wilayahnya."},
        {"step": 2, "title": "Mencocokkan Wilayah Tropis dengan Pola Agraris", "explanation": "Menghubungkan kategori Agraris pada Asia Tenggara dan Nusantara dengan narasi curah hujan tinggi dan tanah subur yang mendukung pertanian padi sawah."},
        {"step": 3, "title": "Mencocokkan Wilayah Lintang Tinggi dengan Pola Berburu-Meramu", "explanation": "Menghubungkan kategori Berburu dan Meramu pada kawasan lingkar kutub dengan kondisi iklim dingin ekstrem yang tidak mendukung pertanian menetap."},
        {"step": 4, "title": "Menguji Klaim Wilayah Lintang Sedang terhadap Legenda Peta", "explanation": "Memeriksa bahwa lintang sedang seperti Eropa tercatat sebagai Agraris pada peta, bukan berburu musiman, sehingga pernyataan tentang lintang sedang dinyatakan tidak sesuai data."}
      ],
      "why_correct": "A benar karena sesuai kategori Agraris pada Asia Tenggara dan Nusantara di peta; B benar karena sesuai kategori Berburu dan Meramu pada kawasan lingkar kutub; C salah karena lintang sedang pada peta dikategorikan Agraris, bukan berburu musiman, dan kategori kombinasi hanya berlaku untuk kawasan stepa Asia Tengah.",
      "tips": [
        "Selalu rujuk legenda peta tematik secara presisi; jangan menyamaratakan kategori 'lintang sedang' dengan kategori lain yang tidak eksplisit tercantum.",
        "Hubungkan pola aktivitas manusia (agraris atau berburu) dengan kondisi iklim dan bioma spesifik yang disebutkan pada legenda, bukan asumsi umum."
      ],
      "common_mistakes": [
        "Menganggap semua wilayah non-tropis otomatis berburu-meramu, padahal Eropa sebagai wilayah lintang sedang dikategorikan Agraris pada peta.",
        "Mengabaikan bahwa kategori kombinasi agraris/berburu-meramu hanya berlaku untuk kawasan stepa Asia Tengah, bukan lintang sedang secara umum."
      ],
      "soal_serupa": {
        "pertanyaan": "Peta tematik dunia tahun 1500 M menunjukkan bahwa kawasan Afrika Barat dan Tengah yang beriklim tropis dikategorikan sebagai wilayah agraris, kawasan Siberia utara yang beriklim dingin ekstrem dikategorikan sebagai wilayah berburu dan meramu, dan kawasan stepa Asia Tengah dikategorikan sebagai kombinasi keduanya. Manakah pernyataan yang paling tepat berdasarkan peta tersebut?",
        "opsi": [
          {"key": "A", "text": "Semua wilayah beriklim dingin tanpa kecuali selalu bergantung pada pertanian menetap."},
          {"key": "B", "text": "Kondisi iklim dan bioma suatu wilayah berkaitan erat dengan corak pemenuhan kebutuhan hidup penduduknya."},
          {"key": "C", "text": "Wilayah stepa Asia Tengah sepenuhnya bergantung pada pertanian menetap seperti Afrika Barat."},
          {"key": "D", "text": "Persebaran bioma tidak memiliki pengaruh terhadap pola aktivitas ekonomi masyarakat purba."}
        ],
        "kunci": "B",
        "pembahasan_singkat": "B benar karena mencerminkan prinsip umum keterkaitan bioma-iklim dengan corak kehidupan yang tergambar jelas pada peta, yaitu agraris di kawasan tropis, berburu-meramu di kutub, dan kombinasi di stepa; A, C, dan D bertentangan dengan data legenda peta."
      }
    },
    # SOAL 8
    {
      "question_id": "geo_p1_q08",
      "question_number": 8,
      "official_answer": {
        "format": "multiple",
        "correct": ["A", "B", "D"]
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Interaksi keruangan dan konektivitas regional ASEAN",
        "Letak geografis strategis Indonesia (posisi silang dunia)",
        "Interpretasi data statistik pariwisata",
        "Diferensiasi pasar wisatawan internasional"
      ],
      "glossary": [
        {"term": "Konektivitas regional", "meaning": "Tingkat keterhubungan suatu wilayah dengan wilayah lain melalui jalur transportasi, perdagangan, dan pergerakan manusia yang memudahkan interaksi antarnegara."},
        {"term": "Letak geografis strategis (posisi silang)", "meaning": "Kedudukan suatu wilayah pada jalur pelayaran atau penerbangan internasional yang menghubungkan berbagai kawasan dunia, sehingga meningkatkan aksesibilitas dan peluang kunjungan."},
        {"term": "Diferensiasi pasar wisatawan", "meaning": "Variasi asal-usul dan karakteristik wisatawan yang berkunjung ke suatu destinasi, mencerminkan luas atau sempitnya jangkauan pasar pariwisata."}
      ],
      "reasoning": "Data menunjukkan asal wisatawan terbanyak ke Indonesia adalah Malaysia (anggota ASEAN) dan Tiongkok (Asia Timur), sehingga pernyataan A tentang dominasi wisatawan dari kawasan ASEAN dan Asia Timur yang mendukung konektivitas regional terbukti benar. Karena Tiongkok bukan anggota ASEAN, tingginya kunjungan dari negara tersebut menunjukkan bahwa pasar wisata Indonesia telah meluas melampaui kawasan ASEAN saja, sehingga pernyataan B juga benar. Sebaliknya, data justru menunjukkan jumlah wisatawan asing ke Thailand (28 juta) jauh lebih besar daripada Indonesia (10,5 juta), sehingga klaim pada pernyataan C bahwa Indonesia lebih unggul dari Thailand secara numerik adalah keliru dan tidak didukung data. Pernyataan D didukung oleh prinsip letak geografis Indonesia yang berada pada jalur pelayaran dan penerbangan internasional atau posisi silang dunia, sehingga secara konseptual memang memperbesar peluang akses wisatawan dari berbagai kawasan, menjadikannya benar. Pernyataan E tidak dapat diverifikasi karena tabel data tidak memuat informasi mengenai wisatawan asal Eropa sama sekali, sehingga simpulan tersebut merupakan generalisasi berlebihan di luar cakupan data yang tersedia.",
      "steps": [
        {"step": 1, "title": "Mengidentifikasi Asal Wisatawan Terbanyak dari Tabel", "explanation": "Membaca kolom asal terbanyak pada data pariwisata Indonesia, yaitu Malaysia dan Tiongkok, untuk menentukan kawasan asal dominan."},
        {"step": 2, "title": "Mengklasifikasikan Asal Wisatawan Berdasarkan Kawasan", "explanation": "Mengelompokkan Malaysia sebagai representasi ASEAN dan Tiongkok sebagai representasi Asia Timur untuk menilai cakupan pasar wisata Indonesia."},
        {"step": 3, "title": "Membandingkan Angka Kunjungan Antarnegara", "explanation": "Membandingkan angka 10,5 juta wisatawan Indonesia dengan 28 juta wisatawan Thailand untuk menguji kebenaran klaim keunggulan numerik pada pernyataan C."},
        {"step": 4, "title": "Mengaitkan Letak Geografis dengan Peluang Aksesibilitas", "explanation": "Menghubungkan konsep posisi silang dunia Indonesia dengan potensi peningkatan akses wisatawan dari berbagai kawasan, sekaligus menyaring klaim yang tidak didukung data eksplisit seperti asal wisatawan Eropa pada pernyataan E."}
      ],
      "why_correct": "A dan B benar karena didukung data asal wisatawan Malaysia dan Tiongkok yang menunjukkan cakupan pasar ASEAN sekaligus Asia Timur; D benar karena sesuai prinsip letak geografis strategis Indonesia sebagai jalur internasional; sedangkan C keliru karena bertentangan langsung dengan angka pada tabel, dan E tidak dapat dibuktikan karena data wisatawan Eropa tidak tersedia dalam tabel.",
      "tips": [
        "Pada soal pilihan ganda kompleks berbasis tabel, selalu verifikasi klaim numerik seperti 'lebih besar' atau 'lebih kecil' langsung dengan angka pada tabel sebelum menilai benar atau salah.",
        "Waspadai pernyataan yang menyimpulkan sesuatu di luar cakupan data yang disediakan, seperti klaim tentang wisatawan Eropa padahal tabel tidak memuat data tersebut."
      ],
      "common_mistakes": [
        "Memilih C karena asumsi bahwa Indonesia sebagai negara besar pasti unggul dalam jumlah wisatawan, tanpa mengecek angka aktual pada tabel.",
        "Memilih E karena generalisasi berlebihan, padahal tabel tidak menyediakan data apa pun tentang wisatawan asal Eropa sehingga klaim tersebut tidak dapat diverifikasi."
      ],
      "soal_serupa": {
        "pertanyaan": "Data pariwisata tahun 2024 menunjukkan wisatawan asing ke Vietnam sebanyak 8,5 juta dengan asal terbanyak Korea Selatan dan Jepang, sedangkan wisatawan asing ke Singapura sebanyak 19 juta dengan asal terbanyak Indonesia dan Malaysia. Pilih pernyataan yang benar terkait pola kunjungan wisatawan tersebut!",
        "opsi": [
          {"key": "A", "text": "Sebagian besar wisatawan Vietnam berasal dari kawasan Asia Timur, mencerminkan konektivitas lintas kawasan."},
          {"key": "B", "text": "Jumlah wisatawan Singapura lebih kecil daripada Vietnam karena letak geografisnya kurang strategis."},
          {"key": "C", "text": "Dominasi wisatawan Singapura dari ASEAN, yaitu Indonesia dan Malaysia, mencerminkan kuatnya konektivitas regional."},
          {"key": "D", "text": "Data tersebut membuktikan bahwa wisatawan Eropa mendominasi kunjungan ke kedua negara."}
        ],
        "kunci": "A, C",
        "pembahasan_singkat": "A dan C benar karena Vietnam didominasi wisatawan Asia Timur (Korea Selatan, Jepang) dan Singapura didominasi wisatawan ASEAN (Indonesia, Malaysia), keduanya mencerminkan konektivitas regional; B salah karena data menunjukkan Singapura justru jauh lebih besar dari Vietnam; D salah karena data tidak menyebutkan wisatawan Eropa sama sekali."
      }
    },
    # SOAL 9
    {
      "question_id": "geo_p1_q09",
      "question_number": 9,
      "official_answer": {
        "format": "single",
        "correct": ["C"]
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Konsep esensial geografi (10 konsep dasar)",
        "Keterkaitan faktor fisik dan manusia (prinsip interelasi)",
        "Banjir perkotaan (urban flooding)",
        "Alih fungsi lahan dan drainase perkotaan"
      ],
      "glossary": [
        {"term": "Prinsip interelasi/keterkaitan keruangan", "meaning": "Prinsip geografi yang menjelaskan hubungan sebab-akibat antara fenomena fisik seperti curah hujan dan topografi dengan fenomena manusia seperti alih fungsi lahan dan tata kelola kota dalam suatu ruang."},
        {"term": "Alih fungsi lahan", "meaning": "Perubahan peruntukan lahan, misalnya dari daerah resapan air menjadi permukiman, yang mengurangi kapasitas infiltrasi air hujan ke dalam tanah."},
        {"term": "Normalisasi sungai", "meaning": "Upaya rekayasa hidrologi untuk mengembalikan atau memperbesar kapasitas tampung sungai guna mengurangi risiko banjir."}
      ],
      "reasoning": "Penyebab banjir di Bekasi yang dipaparkan dalam stimulus merupakan gabungan antara faktor fisik alami, yaitu curah hujan tinggi pada Januari hingga Maret dan pendangkalan sungai, dengan faktor manusia, yaitu alih fungsi lahan menjadi permukiman, sistem drainase buruk, dan tumpukan sampah. Kombinasi sebab-akibat lintas faktor fisik dan manusia inilah yang secara tepat dijelaskan oleh konsep keterkaitan antara faktor fisik dan manusia atau prinsip interelasi dalam geografi, karena banjir tidak dapat dijelaskan hanya dari satu sisi saja, sehingga opsi C tepat. Opsi A, B, D, dan E menggabungkan istilah-istilah konsep geografi seperti interaksi, diferensiasi, aglomerasi, jarak, dan lokasi secara tidak tepat atau tidak secara langsung menjelaskan hubungan sebab-akibat fisik-manusia yang menjadi inti permasalahan banjir pada stimulus.",
      "steps": [
        {"step": 1, "title": "Memilah Faktor Fisik Penyebab Banjir", "explanation": "Mengidentifikasi curah hujan tinggi dan pendangkalan sungai sebagai unsur fisik alami yang berkontribusi pada banjir di Bekasi."},
        {"step": 2, "title": "Memilah Faktor Manusia Penyebab Banjir", "explanation": "Mengidentifikasi alih fungsi lahan, sistem drainase buruk, dan tumpukan sampah sebagai unsur aktivitas manusia yang memperparah banjir."},
        {"step": 3, "title": "Menerapkan Konsep Esensial Geografi yang Relevan", "explanation": "Menyimpulkan bahwa gabungan faktor fisik dan manusia tersebut paling tepat dijelaskan dengan konsep keterkaitan atau interelasi antara faktor fisik dan manusia, bukan konsep lain seperti diferensiasi area atau aglomerasi yang tidak berfokus pada hubungan sebab-akibat lintas faktor."}
      ],
      "why_correct": "Konsep keterkaitan faktor fisik dan manusia paling tepat karena secara eksplisit menjelaskan hubungan sebab-akibat antara kondisi fisik, seperti curah hujan dan pendangkalan sungai, dengan aktivitas manusia, seperti alih fungsi lahan, drainase buruk, dan sampah, yang bersama-sama menyebabkan banjir di Bekasi sesuai seluruh unsur penyebab yang disebutkan dalam stimulus.",
      "tips": [
        "Ketika stimulus memuat penyebab bencana yang berasal dari unsur fisik dan unsur manusia sekaligus, jawaban yang tepat biasanya mengarah pada konsep keterkaitan atau interelasi, bukan konsep tunggal seperti lokasi atau jarak.",
        "Bedakan konsep esensial geografi seperti interaksi, interelasi, dan diferensiasi area agar tidak tertukar penerapannya pada kasus bencana."
      ],
      "common_mistakes": [
        "Memilih opsi A atau B karena istilah 'interaksi' dan 'diferensiasi area' terdengar mirip, padahal kedua konsep tersebut tidak secara spesifik menjelaskan hubungan sebab-akibat fisik-manusia seperti pada kasus banjir Bekasi.",
        "Memilih opsi D karena tergiur istilah 'lokasi bencana', padahal konsep tersebut tidak baku dan tidak secara tepat mencakup keseluruhan unsur fisik-manusia dalam stimulus."
      ],
      "soal_serupa": {
        "pertanyaan": "Kawasan Puncak, Kabupaten Bogor, kerap mengalami tanah longsor saat musim hujan. Curah hujan tinggi yang jatuh di lereng-lereng curam diperparah oleh alih fungsi lahan dari kawasan hutan lindung menjadi vila dan lahan pertanian sayuran tanpa terasering yang memadai, sehingga daya serap tanah terhadap air menurun drastis. Konsep geografi yang paling tepat digunakan untuk menjelaskan penyebab longsor tersebut adalah ....",
        "opsi": [
          {"key": "A", "text": "Interaksi dan diferensiasi area antarwilayah pegunungan."},
          {"key": "B", "text": "Keterkaitan antara faktor fisik dan manusia dalam suatu ruang."},
          {"key": "C", "text": "Aglomerasi permukiman di kawasan wisata pegunungan."},
          {"key": "D", "text": "Jarak dan keterjangkauan lokasi wisata Puncak."}
        ],
        "kunci": "B",
        "pembahasan_singkat": "B benar karena longsor disebabkan gabungan faktor fisik (curah hujan tinggi, lereng curam) dan faktor manusia (alih fungsi hutan lindung menjadi vila dan lahan pertanian tanpa terasering), sesuai prinsip keterkaitan fisik-manusia; opsi lain tidak menjelaskan hubungan sebab-akibat tersebut secara tepat."
      }
    },
    # SOAL 10
    {
      "question_id": "geo_p1_q10",
      "question_number": 10,
      "official_answer": {
        "format": "single",
        "correct": ["B"]
      },
      "needs_manual_review": False,
      "review_reason": None,
      "concept_kunci": [
        "Sistem Informasi Geografis (SIG)",
        "Analisis jaringan (network analysis) dan perutean optimal",
        "Teknologi geospasial dalam layanan publik",
        "Perbedaan SIG dengan penginderaan jauh (remote sensing)"
      ],
      "glossary": [
        {"term": "SIG (Sistem Informasi Geografis)", "meaning": "Sistem yang mengumpulkan, menyimpan, mengelola, menganalisis, dan menampilkan data yang bereferensi geografis untuk mendukung pengambilan keputusan spasial."},
        {"term": "Analisis jaringan (network analysis)", "meaning": "Fungsi analisis dalam SIG untuk menentukan rute optimal, jarak terpendek, atau waktu tempuh tercepat pada suatu jaringan jalan berdasarkan atribut seperti tingkat kemacetan."},
        {"term": "Penginderaan jauh (remote sensing)", "meaning": "Teknik memperoleh data permukaan bumi dari jarak jauh menggunakan sensor pada satelit atau pesawat, berbeda fungsi dengan SIG yang mengolah dan menganalisis data tersebut."}
      ],
      "reasoning": "Aplikasi yang mencari rute tercepat menuju lokasi vaksinasi dengan mempertimbangkan tingkat kemacetan memerlukan kemampuan menyimpan data lokasi seperti titik vaksinasi dan jaringan jalan, serta menganalisis dan menampilkan rute optimal berdasarkan atribut kemacetan secara real-time, yang merupakan fungsi inti dari Sistem Informasi Geografis, sehingga opsi B tepat. Remote sensing berfungsi mendeteksi kondisi permukaan bumi dari jarak jauh, bukan mendeteksi suhu tubuh individu maupun menghitung rute, sehingga opsi A tidak sesuai. Peta kontur hanya menggambarkan ketinggian medan dan tidak relevan dengan pertimbangan kemacetan lalu lintas perkotaan, sehingga opsi C tidak tepat. Sistem manual berbasis input teks tidak memanfaatkan teknologi geospasial sama sekali, sehingga opsi D tidak sesuai. Sensor cahaya bukan metode yang digunakan untuk mendeteksi kepadatan lalu lintas dalam aplikasi peta digital, karena data kemacetan umumnya diperoleh dari data pergerakan pengguna yang diolah dalam sistem SIG, sehingga opsi E tidak tepat.",
      "steps": [
        {"step": 1, "title": "Mengidentifikasi Kebutuhan Fungsional Aplikasi", "explanation": "Menganalisis bahwa aplikasi memerlukan data lokasi vaksinasi, jaringan jalan, dan tingkat kemacetan secara terintegrasi untuk menentukan rute tercepat."},
        {"step": 2, "title": "Mencocokkan Kebutuhan dengan Fungsi Teknologi Geospasial", "explanation": "Membandingkan fungsi SIG dalam mengelola, menganalisis, dan menampilkan data spasial serta rute optimal dengan teknologi lain seperti penginderaan jauh atau peta kontur yang tidak memiliki fungsi analisis rute."},
        {"step": 3, "title": "Menyimpulkan Peran SIG dalam Analisis Rute Optimal", "explanation": "Menegaskan bahwa fungsi analisis jaringan dalam SIG adalah komponen yang memungkinkan penentuan rute tercepat berdasarkan variabel kemacetan lalu lintas."}
      ],
      "why_correct": "SIG adalah satu-satunya teknologi geospasial yang memiliki kemampuan mengelola data lokasi sekaligus menganalisis dan menampilkan rute optimal berdasarkan tingkat kemacetan, sesuai kebutuhan fungsional aplikasi pada stimulus, sedangkan opsi lain tidak memiliki kapabilitas analisis rute tersebut.",
      "tips": [
        "Bedakan fungsi SIG dalam mengelola dan menganalisis data spasial, termasuk perutean, dengan penginderaan jauh yang berfungsi memperoleh data dari jarak jauh.",
        "Kata kunci seperti 'rute tercepat', 'mempertimbangkan kemacetan', atau 'lokasi optimal' hampir selalu mengarah pada fungsi analisis jaringan dalam SIG."
      ],
      "common_mistakes": [
        "Memilih opsi A karena mengasosiasikan semua teknologi berbasis satelit dengan penginderaan jauh, padahal remote sensing tidak berfungsi menghitung rute atau mendeteksi kemacetan individu.",
        "Memilih opsi E karena istilah 'sensor' terdengar berkaitan dengan teknologi canggih, padahal deteksi kepadatan lalu lintas pada aplikasi peta umumnya berasal dari data pergerakan GPS pengguna yang diproses SIG, bukan sensor cahaya."
      ],
      "soal_serupa": {
        "pertanyaan": "Sebuah aplikasi transportasi daring digunakan pengemudi untuk menemukan rute tercepat mengantar penumpang ke bandara dengan mempertimbangkan kepadatan lalu lintas secara real-time. Teknologi geospasial apa yang paling berperan dalam aplikasi tersebut?",
        "opsi": [
          {"key": "A", "text": "Penginderaan jauh untuk memantau suhu udara di sekitar bandara."},
          {"key": "B", "text": "Sistem Informasi Geografis untuk mengelola data lokasi dan menghitung rute optimal."},
          {"key": "C", "text": "Peta topografi untuk menampilkan ketinggian wilayah sekitar bandara."},
          {"key": "D", "text": "Pencatatan manual oleh petugas lalu lintas di setiap persimpangan."}
        ],
        "kunci": "B",
        "pembahasan_singkat": "B benar karena aplikasi memerlukan pengelolaan data lokasi dan analisis rute optimal berdasarkan kepadatan lalu lintas secara real-time, yang merupakan fungsi inti Sistem Informasi Geografis; opsi lain tidak memiliki kapabilitas tersebut."
      }
    }
]

def main():
    print("=== MEMULAI AUDIT INTEGRITAS & INGESTION LAYER 3 GEOGRAFI PAKET 1 ===")
    
    # Urutkan berdasarkan question_number 1..10
    sorted_solutions = sorted(USER_SOLUTIONS_RAW, key=lambda x: x["question_number"])
    
    # Pastikan kompatibilitas soal_serupa: sediakan baik 'opsi' maupun 'pilihan'
    for s in sorted_solutions:
        sim = s["soal_serupa"]
        if "opsi" in sim and "pilihan" not in sim:
            sim["pilihan"] = sim["opsi"]
        elif "pilihan" in sim and "opsi" not in sim:
            sim["opsi"] = sim["pilihan"]
            
    doc = {
        "package": 1,
        "subject": "Geografi",
        "solutions": sorted_solutions
    }
    
    # 1. Validasi via solution_loader
    solution_loader.validate_solution_doc(doc)
    print("[PASS] Validasi skema solution_loader 10/10 berhasil.")
    
    # 2. Cross-check kunci resmi Pusmendik
    kunci_data = json.load(open(KUNCI_PATH, encoding="utf-8"))
    raw_rows = kunci_data["raw_rows"]
    
    mismatches = []
    for s in sorted_solutions:
        qnum = s["question_number"]
        row = raw_rows.get(str(qnum))
        kind, payload = parse_official_row(row["kunci"])
        sol_ans = s["official_answer"]
        
        ok = False
        if kind == "bs":
            ok = (sol_ans.get("statements") == payload)
        elif kind == "multi":
            ok = (sorted(sol_ans.get("correct", [])) == sorted(payload))
        elif kind == "single":
            ok = (sol_ans.get("correct") == payload)
            
        if not ok:
            mismatches.append((qnum, sol_ans, payload))
            s["needs_manual_review"] = True
            s["review_reason"] = f"Key mismatch with official: {payload}"
            print(f"[FAIL] Soal {qnum} KUNCI MISMATCH! Sol={sol_ans} vs Pusmendik={payload}")
        else:
            s["needs_manual_review"] = False
            print(f"[MATCH OK] Soal {qnum:02d} ({kind}): Kunci cocok 100% dengan Pusmendik -> {payload}")
            
    if mismatches:
        print(f"\n[PERINGATAN] Ditemukan {len(mismatches)} mismatch kunci resmi!")
    else:
        print("\n[SEMPURNA] 10/10 Soal memiliki kunci identik 100% dengan Kunci Resmi Pusmendik!")

    # 3. Tulis file L3 ke data/solution_sources/GEO_PAKET_1_SOLUTIONS.json
    with open(SOL_PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"[SAVED] File solusi L3 tersimpan di: {SOL_PATH}")
    
    # 4. Daftarkan di registry.json
    reg = json.load(open(REG_PATH, encoding="utf-8"))
    reg["geo_paket_1"] = {
        "active_source": "GEO_PAKET_1_SOLUTIONS.json"
    }
    with open(REG_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    print(f"[REGISTERED] geo_paket_1 aktif di {REG_PATH}")
    
    # 5. Enrich data/geografi_paket_1_learning.json
    lrn_data = json.load(open(LRN_PATH, encoding="utf-8"))
    sol_map = {s["question_number"]: s for s in sorted_solutions}
    
    for q in lrn_data["soal"]:
        no = q["nomor"]
        s = sol_map.get(no)
        if s:
            # Bangun glosarium_simbol dari glossary
            glosarium = []
            for g in s.get("glossary", []):
                glosarium.append({
                    "simbol": g.get("term"),
                    "nama": g.get("term"),
                    "arti": g.get("meaning")
                })
            # Bangun langkah_penyelesaian
            langkah = []
            for st in s.get("steps", []):
                langkah.append(f"**Langkah {st.get('step')}: {st.get('title')}**\n{st.get('explanation')}")
                
            pembahasan = {
                "glosarium_simbol": glosarium,
                "mengapa_begini": s.get("reasoning", ""),
                "konsep_kunci": ", ".join(s.get("concept_kunci", [])),
                "langkah_penyelesaian": langkah,
                "tips_trik": " ".join(s.get("tips", [])),
                "why_correct": s.get("why_correct", ""),
                "common_mistakes": s.get("common_mistakes", [])
            }
            q["pembahasan"] = pembahasan
            ss = s.get("soal_serupa", {})
            if ss:
                ss_clean = dict(ss)
                if "pembahasan" not in ss_clean and "pembahasan_singkat" in ss_clean:
                    ss_clean["pembahasan"] = ss_clean["pembahasan_singkat"]
                if "pilihan" not in ss_clean and "opsi" in ss_clean:
                    ss_clean["pilihan"] = ss_clean["opsi"]
                q["soal_serupa"] = ss_clean
            
    with open(LRN_PATH, "w", encoding="utf-8") as f:
        json.dump(lrn_data, f, ensure_ascii=False, indent=2)
    print(f"[ENRICHED] {LRN_PATH} berhasil diperkaya dengan 5 Pilar & Soal Serupa!")
    
    # 6. Test solution_loader
    loaded_doc, meta = solution_loader.load_solution_doc("geografi", 1)
    assert loaded_doc is not None, "Gagal memuat via solution_loader"
    print(f"[LOADER TEST] solution_loader.load_solution_doc('geografi', 1) -> SUKSES ({len(loaded_doc['solutions'])} solusi)")

if __name__ == "__main__":
    main()
