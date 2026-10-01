# PROMPT REASONING L3 (MICRO-BATCH 1: SOAL 1 s.d. 5)
## TARGET: GEOGRAFI PAKET 1 (SMA/SMK PILIHAN) — 5 PILAR PEDAGOGIS & SOAL SERUPA

Anda adalah AI Senior Geography Specialist & Curriculum Designer untuk Kurikulum Merdeka (TKA SMA/SMK).
Tugas Anda adalah menghasilkan solusi pedagogis komprehensif berstandar **Layer 3 (5 Pilar)** dan **1 Soal Serupa (Drill Practice)** untuk 5 butir soal di bawah ini.

### ATURAN KERJA & BATASAN KETAT (ZERO COMPROMISE):
1. **KUNCI RESMI ADALAH GROUND TRUTH HARGA MATI**:
   Nilai `official_answer` telah disediakan berdasarkan hasil reviu resmi Pusmendik Kemendikdasmen. DILARANG MENIMPA ATAU MENGUBAH KUNCI RESMI DENGAN ALASAN APAPUN. Semua penjelasan wajib membuktikan kebenaran kunci resmi tersebut.
2. **DILARANG SOLUSI GENERIK / BOILERPLATE**:
   Setiap `steps` (Langkah Penyelesaian) wajib memuat konsep geografi nyata (misal: analisis citra satelit, resolusi spasial/spektral, geomorfologi Danau Bandung Purba, erupsi kuarter Gunung Sunda, dinamika sedimentasi dan abrasi pesisir, peruntukan tanah andosol, pemetaan KRB vulkanik). Dilarang menuliskan langkah umum seperti "Identifikasi Masalah" atau "Tarik Kesimpulan".
3. **SOAL SERUPA WAJIB ISOMORFIK & LENGKAP**:
   Buat 1 soal baru dengan prinsip geografi yang identik, tetapi dengan skenario/lokasi/studi kasus baru. Sediakan opsi A-D, kunci jawaban huruf tunggal, dan pembahasan singkat logis.
4. **FORMAT OUTPUT WAJIB VALID JSON**:
   Keluarkan HANYA JSON array atau JSON objek sesuai schema di bawah ini tanpa teks pengantar atau penutup.

---

### KONTRAK SKEMA JSON OUTPUT:
```json
{
  "package": 1,
  "subject": "Geografi",
  "solutions": [
    {
      "question_id": "geo_p1_q01",
      "question_number": 1,
      "official_answer": {
        "format": "multiple",
        "correct": ["A", "C"]
      },
      "needs_manual_review": false,
      "review_reason": null,
      "concept_kunci": [
        "Nama konsep geografi 1",
        "Nama konsep geografi 2"
      ],
      "glossary": [
        {"term": "Istilah Geografi", "meaning": "Penjelasan istilah secara ilmiah & ringkas"}
      ],
      "reasoning": "Paragraf analisis geografis mendalam yang menjelaskan mengapa kunci resmi benar...",
      "steps": [
        {"step": 1, "title": "Judul Tahap Spesifik Geografi", "explanation": "Penjelasan tahap..."},
        {"step": 2, "title": "Judul Tahap Spesifik Geografi", "explanation": "Penjelasan tahap..."}
      ],
      "why_correct": "Penjelasan presisi mengapa kombinasi kunci opsi resmi adalah jawaban yang paling tepat.",
      "tips": [
        "Tips praktis menganalisis soal model ini..."
      ],
      "common_mistakes": [
        "Kekeliruan siswa yang menyebabkan memilih opsi salah..."
      ],
      "soal_serupa": {
        "pertanyaan": "Teks soal serupa baru...",
        "opsi": [
          {"key": "A", "text": "Pilihan A"},
          {"key": "B", "text": "Pilihan B"},
          {"key": "C", "text": "Pilihan C"},
          {"key": "D", "text": "Pilihan D"}
        ],
        "kunci": "A",
        "pembahasan_singkat": "Penjelasan singkat jawaban soal serupa..."
      }
    }
  ]
}
```

---

### DATA BUTIR SOAL BATCH 1 (SOAL 1 - 5)

#### SOAL 1 [geo_p1_q01] — Pilihan Ganda Kompleks
- **Stimulus:**
Perhatikan gambar tangkapan citra satelit berikut!
berdasarkan tangkapan citra satelit tersebut, seorang kepala daerah mengidentifikasi terdapatnya indikasi banjir pada wilayah yang berbatasan dengan laut.
- **Visual Context (Citra Satelit):**
Tangkapan citra satelit vertikal pesisir pantai dan dataran rendah. Garis pantai membentang dari barat daya ke timur laut berbatasan dengan laut berwarna hijau kebiruan. Terlihat genangan air laut (banjir rob/inundasi) merambah masuk ke area tambak, lahan pertanian, dan jaringan permukiman serta jalan di dataran aluvial pantai. Di daratan terlihat pola petak-petak tambak/sawah, jaringan jalan, dan beberapa kluster bangunan/pabrik di dekat zona genangan.
- **Pertanyaan:**
Berdasarkan informasi tersebut, seorang peneliti akan menindaklanjuti permasalahan tersebut. Rumusan masalah manakah yang tepat?
- **Pilihan Jawaban:**
  [A] Bagaimana pengaruh bencana terhadap perekonomian penduduk?
  [B] Apa saja jenis-jenis bencana alam yang berdampak luas terhadap masyarakat?
  [C] Bagaimana hubungan antara pasang air laut dengan topografi wilayah?
  [D] Mengapa siswa perlu mengetahui pentingnya menjaga lingkungan secara berkelanjutan?
  [E] Bagaimana bentuk mitigasi bencana beserta dengan contohnya yang konkret di sekolah?
- **KUNCI RESMI PUSMENDIK:** `{"format": "multiple", "correct": ["A", "C"]}`

---

#### SOAL 2 [geo_p1_q02] — Benar-Salah
- **Stimulus:**
Danau Bandung Purba
Danau Bandung purba terbentuk sekitar 125.000 tahun lalu ketika material erupsi Gunung Sunda membendung aliran Sungai Citarum Purba. Kedalaman rata-rata danau Bandung Purba saat itu sekitar 20-30 meter. Peristiwa gempa bumi dan longsor akibat erosi di antara Curug Cukangrahong dan Curug Halimun sekitar 16.000 tahun lalu berakibat air danau ini mengalir ke utara. Dampaknya adalah air danau mulai terkuras kemudian membuat bentang lahan Cekungan Bandung menjadi rawa dan berangsur-angsur mengering. Danau Bandung Purba juga menjadi wilayah yang dihuni oleh manusia sejak lama dengan ditemukan adanya perkakas obsidian yang tersebar di sekitarnya.
- **Visual Context (Grafik & Inset Peta):**
Grafik riwayat fluktuasi kedalaman Danau Bandung Purba dan inset peta geomorfologi Cekungan Bandung. Sumbu vertikal (Y) menunjukkan 'Kedalaman Danau Bandung Purba' (0 sampai 35 meter). Sumbu horizontal (X) menandai linimasa: (1) '125.000 SM Erupsi Gunung Sunda Membendung aliran Sungai Citarum Purba' dengan titik puncak kedalaman danau mencapai ~32-33 meter; (2) '16.000 SM Longsor di Bandung Utara Membuka kembali aliran sungai Citarum Purba' dengan kedalaman menurun tajam ke ~20 meter lalu ~15 meter; (3) '5.000 SM Danau Bandung Purba berangsur surut dan menghilang' dengan kedalaman mencapai 0 meter hingga tahun 2000 M. Inset peta di kanan atas menampilkan rekonsiliasi bentuk Danau Bandung Purba (Barat dan Timur), jalur aliran Ci Tarum, Curug Jompong, serta sebaran titik hitam lokasi penemuan artefak perkakas obsidian/kendan manusia purba di sekeliling tepi danau purba.
- **Pertanyaan:**
Tentukan apakah pernyataan tentang fenomena Bandung Purba terkait aktivitas manusia berikut Benar atau Salah!
- **Pernyataan:**
  [A] Data menunjukkan bahwa Bandung pernah berada di bawah permukaan air.
  [B] Manusia mulai menempati kawasan Danau Bandung Purba setelah mengering.
  [C] Manusia mulai mengembangkan pertanian di utara danau.
- **KUNCI RESMI PUSMENDIK:** `{"format": "per_statement", "statements": {"A": "Benar", "B": "Benar", "C": "Salah"}}`

---

#### SOAL 3 [geo_p1_q03] — Benar-Salah
- **Stimulus:**
Studi Kasus Abrasi Pantai Demak
Sumber: googlemap.com
Kawasan pesisir di Desa Bedono, Kabupaten Demak, Jawa Tengah, mengalami abrasi parah sejak tahun 1990-an akibat kombinasi faktor alami dan aktivitas manusia (lihat gambar). Sekitar 6 km² daratan tenggelam, memaksa ratusan keluarga meninggalkan rumah mereka. Kerusakan ini diperparah oleh konversi hutan mangrove menjadi tambak udang tanpa mempertimbangkan daya dukung lingkungan. Data Dinas Lingkungan Hidup tahun 2022 mencatat bahwa hanya sekitar 20% dari luasan mangrove awal yang masih bertahan, menyebabkan kerusakan ekosistem pesisir dan memperparah risiko bencana.
Sejak 2015, berbagai upaya rehabilitasi dilakukan oleh pemerintah daerah, LSM, dan masyarakat setempat. Program restorasi mangrove ditargetkan menanam kembali 150.000 bibit mangrove hingga tahun 2025. Selain itu, dikembangkan konsep ekowisata berbasis konservasi, di mana masyarakat diberdayakan sebagai pengelola kawasan wisata edukasi mangrove. Hasil awal monitoring tahun 2023 menunjukkan bahwa 65% dari bibit mangrove yang ditanam berhasil tumbuh, mengurangi kecepatan abrasi rata-rata sebesar 10% per tahun di beberapa titik kritis. Program ini juga meningkatkan pendapatan tambahan masyarakat hingga 20% melalui sektor ekowisata.
- **Visual Context (Citra Satelit Abrasi Pesisir Demak):**
Citra satelit Google Maps kawasan pesisir Desa Bedono, Kecamatan Sayung, Kabupaten Demak, Jawa Tengah. Tampak sebuah poligon bergaris merah di pesisir utara menandai daratan seluas ~6 km² yang telah tenggelam dan terabrasi oleh laut Jawa (ditunjukkan oleh tanda panah merah besar dari laut). Di dalam dan sekitar zona tergenang terdapat titik lokasi Makam Syekh Abdullah Mudzakir yang kini berada di tengah laut, Jembatan Morosan, dan Rumpon Mbak Roh. Di sisi tenggara daratan terlihat jalur Jalan Tol Semarang-Demak, Gerbang Tol Sayung, SPBU Pertamina Onggorawe, serta kawasan industri Jateng Land Industrial Park Sayung.
- **Pertanyaan:**
Tentukan fakta berikut ini Benar atau Salah terkait keberlanjutan pengelolaan SDA berdasarkan prinsip konservasi dan restorasi lingkungan!
- **Pernyataan:**
  [A] Kerusakan hutan mangrove di Desa Bedono disebabkan oleh faktor alami.
  [B] Contoh pengelolaan berkelanjutan adalah ekowisata berbasis konservasi.
  [C] Penanaman mangrove terbukti dapat mengurangi abrasi pantai.
- **KUNCI RESMI PUSMENDIK:** `{"format": "per_statement", "statements": {"A": "Salah", "B": "Benar", "C": "Benar"}}`

---

#### SOAL 4 [geo_p1_q04] — Benar-Salah
- **Stimulus:**
Perhatikan gambar berikut!
Gambar tersebut menunjukkan tanaman sayuran seperti kubis, wortel, dan kentang tumbuh dengan baik di lahan sekitar gunung berapi. Sebagian lahan pernah tertimbun abu vulkanik dari letusan beberapa tahun sebelumnya. Petani menyebut tanah di wilayah tersebut sangat cocok untuk pertanian karena kandungan mineralnya tinggi.
- **Visual Context (Foto Lapangan Pertanian Lereng Gunung Api):**
Foto lanskap pertanian di lereng gunung api aktif. Di latar depan tampak hamparan bedengan tanaman hortikultura/sayuran hijau subur dalam polybag dan bedengan tanah yang dirawat oleh seorang petani bertopi caping. Di latar belakang menjulang tinggi sebuah kerucut gunung api aktif (stratovolcano) dengan puncak berpasir dan kawah vulkanik di bawah langit biru cerah, mengilustrasikan pemanfaatan tanah andosol/vulkanik berunsur hara tinggi untuk aktivitas agraris.
- **Pertanyaan:**
Tentukan Benar atau Salah untuk setiap pernyataan berikut terkait hubungan antara letusan gunung api dengan kondisi lahan!
- **Pernyataan:**
  [A] Abu vulkanik yang jatuh ke permukaan tanah akan memperkaya unsur hara seperti kalium dan fosfor yang bermanfaat bagi tanaman.
  [B] Letusan gunung berapi selalu merusak seluruh lahan pertanian dan membuatnya tidak dapat digunakan selama puluhan tahun.
  [C] Lahan bekas aliran lava tidak pernah bisa dimanfaatkan kembali untuk pertanian.
- **KUNCI RESMI PUSMENDIK:** `{"format": "per_statement", "statements": {"A": "Benar", "B": "Salah", "C": "Benar"}}`

---

#### SOAL 5 [geo_p1_q05] — Pilihan Ganda
- **Stimulus:**
Perhatikan gambar citra satelit berikut dengan seksama!
- **Visual Context (Citra Satelit Kaldera & Aliran Piroklastik):**
Citra satelit optik penginderaan jauh resolusi tinggi memperlihatkan kaldera dan puncak gunung api aktif pasca-letusan dahsyat. Di bagian tengah tampak kawah kaldera besar dengan kubah lava dan endapan aliran piroklastik, jatuhan abu vulkanik, serta lahar berwarna putih keabuan yang menyebar secara radial menuruni lembah-lembah sungai di lereng gunung. Sekitar lereng dikelilingi hutan lebat berwarna hijau tua dan dua danau kawah/danau bendungan vulkanik berwarna gelap di sisi utara. Citra ini merupakan sumber data spasial primer untuk pemetaan kawasan rawan bencana (KRB) letusan gunung api.
- **Pertanyaan:**
Berdasarkan gambar di atas, produk analisis yang dapat dihasilkan dari olahan citra tersebut adalah ….
- **Pilihan Jawaban:**
  [A] peta jenis vegetasi
  [B] peta kawasan rawan bencana
  [C] peta stratigrafi batuan
  [D] peta oksigen terlarut
  [E] peta penggunaan lahan
- **KUNCI RESMI PUSMENDIK:** `{"format": "single", "correct": ["B"]}`
