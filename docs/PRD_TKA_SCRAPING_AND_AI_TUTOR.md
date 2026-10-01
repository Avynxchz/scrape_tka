# PRODUCT REQUIREMENTS DOCUMENT (PRD)
# CBT-TKA: End-to-End Scraping Pipeline, Isomorphic Drill Practice, & Multi-Key AI Tutor Engine

---

| Dokumen | Spesifikasi Produk & Teknis (PRD) |
| :--- | :--- |
| **Nama Sistem** | Platform Simulasi TKA & AI Tutor Interaktif (Multi-Subject) |
| **Versi** | 1.0.0 |
| **Status** | Approved / Living Architecture |
| **Ruang Lingkup** | Scraping Portal Pusmendik, Canonical Layer 2, Soal Serupa, AI Mega-Prompt, & Multi-Key Groq Resiliency |

---

## 1. Latar Belakang & Tujuan Produk

Platform ini dirancang untuk menyajikan simulasi ujian Tes Kompetensi Akademik (TKA) berstandar resmi Pusmendik Kemendikdasmen dengan nilai tambah pembelajaran mandiri yang mendalam:
1. **Integritas Konten**: Soal, opsi, gambar, dan kunci jawaban 100% otentik dari sumber resmi.
2. **Latihan Pemantapan (Soal Serupa)**: Menguji apakah siswa benar-benar paham konsep setelah membaca pembahasan, bukan sekadar menghafal opsi jawaban.
3. **Bimbingan AI Tutor Real-Time**: Memberikan asisten guru privat 2-arah yang sabar, cepat (~1.5 detik), tidak membocorkan kerumitan teknis, dan tahan terhadap lonjakan beban pengguna dengan sistem rotasi multi-API key.

---

## 2. Modul 1: Protokol Scraping Portal Pusmendik CBT

### 2.1 Alur Gateway & Sesi Ujian (Playwright Automation)
Portal resmi Pusmendik (`https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/`) menggunakan sistem sesi berundak. Scraper wajib mengikuti protokol deterministik berikut:

```
[1. Form Selector]
   ├── #jenjang       : "sma" | "smp" | "sd"
   ├── #jenis_mapel   : "1" (Wajib) | "2" (Pilihan)
   └── #mapel_toggle  : Klik opsi .mapel-option[data-value="..."]
         ↓
[2. Gerbang Login Demo]
   └── Klik button.custom-btn -> Redirect ke /login/ -> Klik button:has-text('Login')
         ↓
[3. Konfirmasi Data Peserta & Refresh Token]
   ├── Klik button:has-text('Refresh') pada widget Token
   ├── Regex Capture Token: r"Token\s*[:=]\s*([A-Z0-9]{6})"
   ├── Isi Form: #nama_peserta="Peserta Simulasi", #tgl="01", #bulan="01", #tahun="2005"
   ├── Input Token: #input-token = Token hasil regex
   └── Klik button:has-text('Submit')
         ↓
[4. Konfirmasi Tes & Masuk Bilik Ujian]
   ├── Klik button:has-text('Mulai') pada halaman /konfirmasi_tes/
   └── Tunggu selector .soal-soal atau #soal-no-1 muncul (timeout 30 detik)
```

### 2.2 Ekstraksi Konten Soal (Bilik Ujian)
Di dalam bilik ujian, scraper mengekstrak:
1. **Stimulus Bacaan** (`.cont-soal`): Teks narasi, grafik, peta, dan tabel data.
2. **Pertanyaan Utama** (`.isi-soal`): Teks instruksi soal dan formula sebaris.
3. **Opsi Jawaban**: Mendeteksi tipe interaksi:
   - `input[type="radio"]` -> Pilihan Ganda Tunggal
   - `input[type="checkbox"]` -> Pilihan Ganda Kompleks
   - `table.table-striped` -> Tabel Pernyataan (Benar-Salah / Kategori Label)

### 2.3 Pemanenan Kunci Jawaban Resmi (Ground Truth Harvester)
- Kunci jawaban tidak ditebak oleh AI.
- Scraper bernavigasi ke soal terakhir (nomor 25) -> Klik **"Selesai Tes"** -> Konfirmasi Selesai.
- Portal Pusmendik memunculkan halaman **Rekap Hasil Ujian** yang menampilkan tabel kunci jawaban resmi seluruh nomor soal.
- Scraper menyedot seluruh tabel kunci ini sebagai *Ground Truth Otoritatif*.

---

## 3. Modul 2: Pemrosesan Media & Canonical JSON (Layer 2)

### 3.1 Manajemen Aset Media Gambar
- Seluruh gambar (stimulus, prompt, dan opsi) diunduh lokal dengan penamaan deterministik:
  `soal_{nomor:02d}_stimulus_{idx:02d}.png` atau `soal_{nomor:02d}_opt_{key}.png`.
- Lokasi penyimpanan: `data/media/<jenjang>/<mapel>/paket_<n>/images/`.
- Di dalam file JSON, URL absolut diubah menjadi path relatif (`images/soal_01_stimulus_01.png`) agar aplikasi fleksibel dipindahkan ke lingkungan server mana pun.

### 3.2 Prinsip Double-Channel (Pemisahan Tampilan Siswa vs Konteks AI)
- **Human Channel (Tampilan Siswa)**:
  Siswa melihat gambar visual asli. Dilarang keras menampilkan teks transkripsi bahasa Inggris internal AI seperti `[Diagram — soal_18_stimulus_01.png]: Illustration with two parts...` pada tampilan soal ataupun pembahasan.
- **AI Vision Channel (Konteks Model)**:
  Model reasoning yang hanya berbasis teks menerima deskripsi teknis gambar (nilai sumbu, kurva, angka ukuran kardus, tabel) melalui kolom `visual_context` pada JSON Kanonis. Kolom ini disembunyikan (`display: none`) dari pandangan murid.

### 3.3 Preservasi Formula Matematika
Gambar rumus Pusmendik yang memiliki atribut `data-latex="..."` diekstrak ke dalam array `formulas`:
```json
"formulas": [
  {"latex": "\\lim_{x \\to 0} \\frac{\\sin(2x)}{x} = 2", "source": "official data-latex"}
]
```
Hal ini mencegah kerusakan formula akibat kegagalan optical character recognition (OCR).

---

## 4. Modul 3: Spesifikasi Soal yang Mirip (Soal Serupa / Drill Practice)

### 4.1 Tujuan Pedagogis
Memberikan sarana evaluasi mandiri (*isomorphic transfer test*) tepat setelah siswa membaca pembahasan. Menguji pemahaman konsep riil dan mencegah ilusi pemahaman akibat menghafal opsi soal asli.

### 4.2 Larangan Template Generic (Anti-Pattern Guard)
File data lama memiliki cacat di mana satu template soal serupa di-copy-paste ke seluruh 25 nomor.
- **Kaidah Ketat**: Setiap nomor soal **wajib memiliki soal serupa yang unik**, dengan angka, skenario cerita, atau variabel yang diubah secara proporsional.
- **Pendeteksi Otomatis Frontend**:
  Fungsi `_isGenericSim(sim)` di frontend mendeteksi apakah teks pertanyaan dipakai di lebih dari 1 soal. Jika terdeteksi kembar, sistem otomatis menyembunyikan kartu latihan tersebut agar tidak menyesatkan siswa.

### 4.3 Spesifikasi Skema JSON Soal Serupa
```json
"soal_serupa": {
  "pertanyaan": "String deskripsi soal serupa yang menguji konsep yang persis sama dengan soal asli tetapi menggunakan angka/variabel berbeda.",
  "pilihan": [
    {"key": "A", "text": "Pilihan A"},
    {"key": "B", "text": "Pilihan B"},
    {"key": "C", "text": "Pilihan C"},
    {"key": "D", "text": "Pilihan D"}
  ],
  "kunci": "A",
  "pembahasan": "Penjelasan singkat langkah penyelesaian soal serupa ini agar siswa langsung tahu di mana letak kekeliruannya bila salah menjawab."
}
```

### 4.4 Interaksi Siswa & State Machine di UI
```
[Siswa Membuka Kartu Latihan Pemantapan]
       ↓
[Pilih Opsi (A, B, C, D)] -> Opsi ter-highlight
       ↓
[Klik "Periksa Jawaban Latihan"]
       ├── JIKA BENAR:
       │   • Kartu opsi berubah hijau (.correct)
       │   • Muncul banner sukses: "Keren! Pemahaman konsepmu pada materi ini sudah solid."
       └── JIKA SALAH:
           • Kartu opsi yang dipilih berubah merah (.incorrect)
           • Kartu opsi kunci resmi berubah hijau
           • Muncul kotak evaluasi berisi pembahasan ringkas soal serupa
```

---

## 5. Modul 4: Mesin Konteks AI Tutor (Mega-Prompt Assembly)

### 5.1 Struktur Mega-Prompt Terpadu (`tutor_engine.py`)
AI Tutor tidak boleh menjawab secara spekulatif tanpa konteks soal. Setiap panggilan ke model AI dibungkus dengan 8 blok hierarki:

```xml
<role>
Guru privat TKA yang sabar, hangat, to the point, menggunakan bahasa Indonesia santai namun edukatif.
</role>

<student_context>
Ringkasan pengalaman belajar siswa pada soal ini (rolling summary dari percakapan sebelumnya).
</student_context>

<question_context>
Soal aktif (Layer 2): ID soal, mata pelajaran, teks stimulus, teks pertanyaan, daftar formula KaTeX resmi ($data-latex$).
</question_context>

<official_answer>
Kunci jawaban resmi Pusmendik sebagai otoritas mutlak penilaian.
</official_answer>

<solution_reference>
Referensi solusi 5 Pilar (Layer 3): Konsep kunci, glosarium istilah, langkah 1-2-3 tercepat, trik cepat, dan jebakan umum.
</solution_reference>

<recent_history>
12 percakapan terakhir antara siswa dan tutor agar paham pesan pendek rujukan ("kenapa?", "terus?", "kok bisa?").
</recent_history>

<current_message>
Pertanyaan siswa saat ini.
</current_message>

<behavior_rules>
1. Hemat token & to the point: buang basa-basi klise ("Tentu, mari kita bahas...").
2. Struktur rapi: Paragraf 1 langsung inti, langkah menggunakan penomoran 1., 2. dengan spasi lega.
3. Rumus matematika wajib KaTeX: $inline$ dan $$block math$$.
4. Trik Cepat: awali dengan "⚡ Tips Cepat: ...".
5. Akhiri dengan 1 pertanyaan pendek cek pemahaman.
</behavior_rules>
```

---

## 6. Modul 5: Sistem Rotasi Multi-Key Groq & Concurrency Guard

Untuk memastikan ketersediaan layanan (*high availability*) saat diakses banyak pengguna tanpa terbentur batas kecepatan API Groq:

```
[Request Chat Siswa]
       ↓
[Semaphore Concurrency Queue (server.py)]
  └── MAX_CONCURRENT_LLM = 6 (Maks 6 request paralel; ke-7 antre max 40 detik)
       ↓
[Rotasi Key Round-Robin (tutor_llm.py)]
  ├── Mengambil key berurutan: Key 1 -> Key 2 -> Key 3 -> Key 1
  └── Mengecek apakah key terpilih sedang dalam masa karantina cooldown 429
       ↓
[Eksekusi Request HTTP POST ke Groq Cloud]
       ├── JIKA BERHASIL (HTTP 200):
       │   └── Kembalikan teks + nama model aktual (misal: "qwen/qwen3.8-27b")
       └── JIKA TERKENA RATE LIMIT (HTTP 429):
           ├── Tandai Key tersebut: mark_key_rate_limited(key, cooldown_seconds=25)
           ├── Putar ke key berikutnya secara instan (next_api_key)
           └── Siswa di browser TIDAK merasakan error; jawaban tetap keluar dalam ~1.5 detik
```

---

## 7. Modul 6: Proteksi Pengguna (Cooldown 10 Detik & Kuota Harian)

### 7.1 Skema Database SQLite (`ai_tutor.db`)
Tabel `ai_tutor_users` melacak penggunaan per pengguna anonim / akun login:
```sql
CREATE TABLE IF NOT EXISTS ai_tutor_users (
    user_key           TEXT PRIMARY KEY,
    tier               TEXT NOT NULL DEFAULT 'free', -- 'free' | 'subscriber'
    daily_date         TEXT,                         -- 'YYYY-MM-DD'
    daily_count        INTEGER NOT NULL DEFAULT 0,
    last_request_time  REAL NOT NULL DEFAULT 0,      -- unix epoch timestamp
    created_at         TEXT NOT NULL,
    updated_at         TEXT NOT NULL
);
```

### 7.2 Aturan Pembatasan
1. **Cooldown Antar Pertanyaan (10 Detik)**:
   - Setelah siswa mengirim 1 pertanyaan, tombol kirim dinonaktifkan dengan visual countdown (`10s`, `9s`, `8s`...).
   - Input chat terkunci sementara dengan pesan: *"Tunggu X detik sebelum bertanya lagi..."*.
   - Backend memvalidasi `now - last_request_time < 10.0`. Percobaan spam/bypass menghasilkan HTTP `429 (cooldown)`.
2. **Batas Kuota Harian**:
   - Akun **Gratis (`free`)**: 10 pertanyaan per hari.
   - Akun **Langganan (`subscriber`)**: 100 pertanyaan per hari.
   - Reset otomatis setiap pergantian tanggal (`daily_date != today`).
   - Sisa kuota ditampilkan real-time di UI header AI Tutor: `⚡ 9/10 Tanya`. Jika kuota habis, input terkunci secara permanen sampai hari berikutnya atau hingga pengguna upgrade.

---

## 8. Modul 7: Standarisasi Struktur Repositori Skalabel

Untuk mendukung puluhan mata pelajaran (SD, SMP, SMA, Wajib, Pilihan), seluruh file ditata rapi dalam arsitektur berikut:

```text
SCRAPE_TKA/
├── core/                         # Core Backend Server & Engines
│   ├── server.py                 # HTTP Server & Endpoints
│   ├── tutor_engine.py           # Mega-Prompt & Guardrails
│   ├── tutor_llm.py              # Provider LLM & Multi-Key Rotator
│   ├── tutor_store.py            # SQLite Store (Users, Sessions, Quota)
│   └── solution_loader.py        # Dynamic Solution Registry Router
│
├── pipeline/                     # Offline Automation Scripts
│   ├── 01_scraper_exam.py        # Playwright Question & Image Scraper
│   ├── 02_scraper_kunci.py       # Playwright Answer Key Harvester
│   ├── 03_build_canonical.py     # Raw HTML to Layer 2 Canonical Parser
│   ├── 04_generate_layer3.py     # AI Pedagogical Solution Batch Generator
│   └── 05_validate_integrity.py  # Integrity, Schema & Key Audit Runner
│
├── web/                          # Frontend Application
│   ├── index.html                # CBT App & AI Tutor Layout
│   ├── style.css                 # Responsive Design, KaTeX, Badges
│   └── app.js                    # CBT Navigation, KaTeX Engine, Chat Stream
│
├── data/                         # Data Assets
│   ├── ai_tutor.db               # SQLite Database
│   ├── raw_html/                 # Backup Raw Pusmendik Exam HTML
│   ├── media/                    # Local Question & Option Images
│   │   └── sma/<mapel>/paket_<n>/images/
│   ├── canonical/                # Layer 2: Single-Truth Canonical JSONs
│   │   └── sma/<mapel>_paket_<n>.json
│   └── solutions/                # Layer 3: 5 Pillars Pedagogical Solutions
│       ├── registry.json         # Master Router Sumber Solusi Aktif
│       └── <MAPEL>_PAKET_<N>_SOLUTIONS_EXTRA.json
│
└── tests/                        # Automated Pytest Suite
    ├── test_api_server.py
    ├── test_tutor_conversation.py
    └── test_solution_integrity.py
```

---

## 9. Kesimpulan & Status Kesiapan

Arsitektur pada dokumen PRD ini:
1. **Sudah Teruji**: Memiliki 63 unit test aktif yang lolos 100% pada suite pytest.
2. **Resilient**: Kebal terhadap rate-limit Groq melalui perputaran 3 API key otomatis.
3. **Akurat**: Menjamin keterikatan mutlak antara soal asli, formula KaTeX, kunci resmi Pusmendik, dan penjelasan AI Tutor.
4. **Siap di-Scale**: Pola ini dapat diaplikasikan langsung ke mata pelajaran **Ekonomi**, **Bahasa Inggris**, **Bahasa Indonesia**, dan mapel saintek/soshum lainnya.
