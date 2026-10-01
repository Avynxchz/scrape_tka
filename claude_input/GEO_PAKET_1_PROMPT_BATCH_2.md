# PROMPT REASONING L3 (MICRO-BATCH 2: SOAL 6 s.d. 10)
## TARGET: GEOGRAFI PAKET 1 (SMA/SMK PILIHAN) — 5 PILAR PEDAGOGIS & SOAL SERUPA

Anda adalah AI Senior Geography Specialist & Curriculum Designer untuk Kurikulum Merdeka (TKA SMA/SMK).
Tugas Anda adalah menghasilkan solusi pedagogis komprehensif berstandar **Layer 3 (5 Pilar)** dan **1 Soal Serupa (Drill Practice)** untuk 5 butir soal di bawah ini (Soal 6 s.d. 10).

### ATURAN KERJA & BATASAN KETAT (ZERO COMPROMISE):
1. **KUNCI RESMI ADALAH GROUND TRUTH HARGA MATI**:
   Nilai `official_answer` telah disediakan berdasarkan hasil reviu resmi Pusmendik Kemendikdasmen. DILARANG MENIMPA ATAU MENGUBAH KUNCI RESMI DENGAN ALASAN APAPUN. Semua penjelasan wajib membuktikan kebenaran kunci resmi tersebut.
2. **DILARANG SOLUSI GENERIK / BOILERPLATE**:
   Setiap `steps` (Langkah Penyelesaian) wajib memuat konsep geografi nyata (misal: proses peri-urbanisasi dan megapolitan Jakarta, persebaran bioma dunia dan corak kehidupan masa lalu 1500 M, analisis data spasial wisatawan ASEAN & konektivitas regional, konsep esensial geografi / keterkaitan fisik-manusia pada banjir Bekasi, teknologi GIS/SIG dalam perutean jaringan transportasi optimal). Dilarang menuliskan langkah umum seperti "Identifikasi Masalah" atau "Tarik Kesimpulan".
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
      "question_id": "geo_p1_q06",
      "question_number": 6,
      "official_answer": {
        "format": "single",
        "correct": ["D"]
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
      "why_correct": "Penjelasan presisi mengapa opsi resmi adalah jawaban yang paling tepat.",
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

### DATA BUTIR SOAL BATCH 2 (SOAL 6 - 10)

#### SOAL 6 [geo_p1_q06] — Pilihan Ganda
- **Stimulus:**
Wilayah Jakarta diproyeksikan akan berkembang menjadi kawasan megapolitan yang melibatkan wilayah di luar Jabodetabek pasca menjadi Ibukota. Pertumbuhan penduduk yang terus meningkat, khususnya akibat migrasi dari berbagai daerah, menyebabkan tekanan terhadap ruang, infrastruktur, dan layanan publik di wilayah Jakarta dan sekitarnya. Keadaan ini mendorong perluasan wilayah fungsional kota hingga menjangkau kawasan yang lebih luas, termasuk kota-kota di provinsi tetangga (Jawa Barat dan Banten).
- **Pertanyaan:**
Berdasarkan dinamika pertumbuhan penduduk yang terus meningkat akibat migrasi, bagaimana kemungkinan pola pergerakan penduduk di wilayah megapolitan Jakarta akan berkembang di masa depan?
- **Pilihan Jawaban:**
  [A] Urbanisasi akan menurun karena masyarakat mulai kembali ke desa akibat tekanan hidup di kota besar.
  [B] Penduduk akan akan bermigrasi secara merata di seluruh wilayah kota karena program industri padat modal.
  [C] Pergerakan penduduk cenderung terkonsentrasi di pusat kota karena akses pekerjaan dan layanan publik yang lebih baik.
  [D] Pergerakan penduduk akan membentuk pola peri-urbanisasi, yaitu menyebar ke wilayah pinggiran dan kota-kota satelit di luar Jabodetabek.
  [E] Dinamika penduduk hanya akan terjadi di kawasan industri besar karena fasilitas penunjangnya paling lengkap.
- **KUNCI RESMI PUSMENDIK:** `{"format": "single", "correct": ["D"]}`

---

#### SOAL 7 [geo_p1_q07] — Benar-Salah
- **Stimulus:**
Wilayah-wilayah di dunia pada sekitar tahun 1500 menunjukkan hubungan erat antara kondisi geografis, termasuk bioma dan iklim, dengan cara manusia memenuhi kebutuhan hidupnya. Aktivitas agraris berkembang pesat di kawasan tropis dengan tanah subur dan curah hujan tinggi, seperti Asia Tenggara, termasuk Nusantara (kini Indonesia), yang dikelilingi oleh hutan hujan tropis. Dalam konteks ini, bioma hutan hujan tropis menyediakan sumber daya alam yang melimpah, mulai dari lahan subur untuk bertani hingga keanekaragaman flora dan fauna yang dapat dimanfaatkan untuk pangan, obat-obatan, dan bahan bangunan. Masyarakat di kepulauan Indonesia mengembangkan sistem pertanian padi sawah, perkebunan rempah-rempah, dan pemanfaatan hasil hutan sebagai bagian dari strategi adaptasi terhadap lingkungannya. Hal ini mencerminkan bahwa persebaran bioma tidak hanya memengaruhi cara hidup, tetapi juga menjadi fondasi penting bagi kesejahteraan masyarakat melalui pemanfaatan sumber daya hayati yang berkelanjutan. Dengan demikian, aktivitas manusia pada masa itu menjadi cerminan awal dari proses pemanfaatan alam yang terstruktur, yang dalam perkembangan selanjutnya menjadi bagian dari sistem ekonomi dan budaya suatu wilayah.
- **Visual Context (Peta Tematik Bioma & Aktivitas Manusia 1500 M):**
Peta tematik dunia proyeksi Robinson tentang hubungan bioma dan aktivitas manusia sekitar tahun 1500 M beserta legenda warna: (1) Warna Merah Muda: 'Agraris' (mencakup kawasan Asia Tenggara/Nusantara, Asia Selatan, Asia Timur, Eropa, Afrika Barat/Tengah, Mesoamerika, dan pesisir Amerika Selatan); (2) Warna Hijau Zaitun: 'Berburu dan Meramu' (mencakup lintang tinggi/lingkar kutub seperti Kanada utara, Alaska, Siberia utara, serta sebagian pedalaman Australia dan Afrika barat daya); (3) Garis Arsir Merah-Hijau: 'Kombinasi Agraris/Berburu dan Meramu' (kawasan stepa Asia Tengah); (4) Putih: 'Tutupan Es' (Greenland dan Antartika); (5) Krem: 'Wilayah tidak dihuni' (pedalaman gurun Sahara).
- **Pertanyaan:**
Tentukan fakta berikut Benar atau Salah terkait kondisi manfaat flora dan fauna terhadap aktivitas manusia pada masa lalu!
- **Pernyataan:**
  [A] Wilayah tropis telah mengembangkan pertanian menetap karena curah hujan tinggi.
  [B] Wilayah lingkar kutub menjadi pusat kelompok berburu dan meramu.
  [C] Kelompok masyarakat di lintang sedang cenderung berburu berdasarkan musim.
- **KUNCI RESMI PUSMENDIK:** `{"format": "per_statement", "statements": {"A": "Benar", "B": "Benar", "C": "Salah"}}`

---

#### SOAL 8 [geo_p1_q08] — Pilihan Ganda Kompleks
- **Stimulus (Tabel Data Perdagangan & Pariwisata Regional ASEAN 2024):**
Tabel Perdagangan, Pariwisata, dan Kerja Sama regional:
- Perdagangan Internasional (Miliar USD):
  - Indonesia: Ekspor Migas 52, Ekspor Non-Migas 263, Impor Migas 63, Impor Non-Migas 117
  - Malaysia: Ekspor Migas 40, Ekspor Non-Migas 250, Impor Migas 50, Impor Non-Migas 110
  - Thailand: Ekspor Migas 30, Ekspor Non-Migas 490, Impor Migas 35, Impor Non-Migas 465
  - Vietnam: Ekspor Migas 20, Ekspor Non-Migas 440, Impor Migas 25, Impor Non-Migas 420
  - Singapura: Ekspor Migas 18, Ekspor Non-Migas 822, Impor Migas 16, Impor Non-Migas 824
- Pariwisata:
  - Indonesia: Wisatawan Asing 10,5 Juta, Asal Terbanyak: Malaysia, Tiongkok
  - Malaysia: Wisatawan Asing 15,3 Juta, Asal Terbanyak: Singapura, Indonesia
  - Thailand: Wisatawan Asing 28 Juta, Asal Terbanyak: Tiongkok, Malaysia
  - Vietnam: Wisatawan Asing 8,5 Juta, Asal Terbanyak: Korea Selatan, Jepang
  - Singapura: Wisatawan Asing 19 Juta, Asal Terbanyak: Indonesia, Malaysia
- Kerja Sama Regional: Ekonomi (ID: 5), Lingkungan (ID: 4), Sosial (ID: 3), Politik (ID: 4).
- **Pertanyaan:**
Berdasarkan data pariwisata Indonesia dan negara ASEAN tahun 2024, pilih semua pernyataan yang benar terkait pola kunjungan wisatawan dan pengaruh letak geografis Indonesia!
- **Pilihan Jawaban:**
  [A] Sebagian besar wisatawan asing ke Indonesia berasal dari kawasan ASEAN dan Asia Timur, mendukung konektivitas regional.
  [B] Meningkatnya kunjungan wisatawan dari Tiongkok mencerminkan perluasan pasar wisata Indonesia di luar ASEAN.
  [C] Jumlah wisatawan asing Indonesia lebih besar dari Thailand karena pengaruh posisi geografis Indonesia yang lebih strategis.
  [D] Lokasi Indonesia yang berada di jalur internasional memperbesar peluang akses wisatawan dari berbagai kawasan dunia.
  [E] Dominasi wisatawan dari Asia menunjukkan bahwa ASEAN belum menarik wisatawan dari kawasan Eropa secara signifikan.
- **KUNCI RESMI PUSMENDIK:** `{"format": "multiple", "correct": ["A", "B", "D"]}`

---

#### SOAL 9 [geo_p1_q09] — Pilihan Ganda
- **Stimulus:**
Setiap musim hujan, wilayah Kota Bekasi kerap dilanda banjir yang menyebabkan kemacetan lalu lintas, kerusakan rumah warga, dan terganggunya aktivitas ekonomi. Berdasarkan data BMKG, curah hujan di wilayah ini cukup tinggi pada bulan Januari hingga Maret. Selain itu, sistem drainase yang buruk, tingginya alih fungsi lahan menjadi permukiman, dan pendangkalan sungai dan tumpukan sampah memperparah kondisi banjir. Pemerintah setempat telah melakukan beberapa upaya seperti normalisasi sungai dan pembangunan waduk.
- **Pertanyaan:**
Konsep geografi yang paling tepat digunakan untuk menjelaskan penyebab banjir tersebut adalah … .
- **Pilihan Jawaban:**
  [A] Interaksi, interdependensi, dan diferensiasi
  [B] Diferensiasi area, lokasi dan interaksi
  [C] Keterkaitan antara faktor fisik dan manusia
  [D] Aglomerasi, interaksi, dan lokasi bencana
  [E] Jarak, lokasi, dan keterkaitan lingkungan
- **KUNCI RESMI PUSMENDIK:** `{"format": "single", "correct": ["C"]}`

---

#### SOAL 10 [geo_p1_q10] — Pilihan Ganda
- **Stimulus:**
Sebuah aplikasi berbasis peta digunakan oleh masyarakat Kota B untuk mencari rute tercepat menuju lokasi vaksinasi COVID-19 dengan mempertimbangkan tingkat kemacetan.
- **Pertanyaan:**
Teknologi geospasial apa yang paling berperan dalam aplikasi tersebut?
- **Pilihan Jawaban:**
  [A] Remote sensing untuk mendeteksi suhu tubuh pengguna.
  [B] GIS menampilkan dan mengelola data lokasi serta rute optimal.
  [C] Peta kontur untuk menghindari wilayah berbukit.
  [D] Sistem manual berbasis input teks dari pengguna.
  [E] Sensor cahaya untuk mendeteksi kepadatan lalu lintas.
- **KUNCI RESMI PUSMENDIK:** `{"format": "single", "correct": ["B"]}`
