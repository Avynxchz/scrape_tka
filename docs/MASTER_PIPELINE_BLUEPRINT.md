# MASTER PIPELINE BLUEPRINT: TKA SIMULASI & AI LEARNING PLATFORM
> Dokumen Spesifikasi Arsitektur, Otomasi Scraping, Pemrosesan Vision, Generasi Solusi AI, dan Penataan Repositori.

---

## DAFTAR ISI
1. [Arsitektur Sistem (3-Layer Data Architecture)](#1-arsitektur-sistem-3-layer-data-architecture)
2. [Standarisasi Struktur Folder & File (Scalable Hierarchy)](#2-standarisasi-struktur-folder--file-scalable-hierarchy)
3. [Protokol Scraping Portal Pusmendik CBT](#3-protokol-scraping-portal-pusmendik-cbt)
4. [Pemrosesan Soal Bergambar & Vision Transcription (Layer 2)](#4-pemrosesan-soal-bergambar--vision-transcription-layer-2)
5. [Generasi Solusi Pedagogis (Layer 3) & Penanganan Token Limit](#5-generasi-solusi-pedagogis-layer-3--penanganan-token-limit)
6. [Audit, Verifikasi Kunci Otoritatif, & Integrasi Registry](#6-audit-verifikasi-kunci-otoritatif--integrasi-registry)
7. [Integrasi Ganda: Tata Cara Pembahasan & AI Tutor 2-Arah](#7-integrasi-ganda-tata-cara-pembahasan--ai-tutor-2-arah)

---

## 1. Arsitektur Sistem (3-Layer Data Architecture)

Untuk menjamin skalabilitas ratusan mata pelajaran (SD, SMP, SMA, Wajib, dan Pilihan), platform memisahkan data menjadi tiga lapisan yang berdiri sendiri (*decoupled*):

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: Raw Scraped Data (Pusmendik HTML & Original Media) │
│ • Tangkapan asli exam HTML dari bilik ujian CBT             │
│ • File gambar asli (stimulus, prompt, opsi) diunduh lokal   │
│ • Rekap kunci jawaban resmi dari halaman hasil ujian        │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Parsing, Extraction & Sanitasi)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: Canonical Question Layer (JSON Single-Truth)       │
│ • Teks soal verbatim + atribut $data-latex$ resmi           │
│ • Normalisasi tipe soal: PG Tunggal, PG Kompleks, B-S Tabel │
│ • Double-channel: Gambar visual untuk siswa vs Vision       │
│   transcription untuk asupan reasoning model AI             │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Batch Reasoning Model: Claude/R1)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: Pedagogical Solution Layer (Human-Readable 5 Pilar)│
│ • 5 Pilar: Konsep, Glosarium, Alur Logika, Langkah Cepat,   │
│   dan Jebakan Soal (Bukan template kaku / teks generic)     │
│ • Terhubung via registry.json (Hot-swapping tanpa ubah kode)│
│ • Menyuplai: (1) Tab Tata Cara & (2) Konteks AI Tutor       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Standarisasi Struktur Folder & File (Scalable Hierarchy)

Repositori ditata secara modular agar dapat menampung jenjang **SD, SMP, dan SMA** (Mata Pelajaran Wajib dan Pilihan):

```text
SCRAPE_TKA/
│
├── core/                         # ENGINE UTAMA BACKEND (Universal lintas mapel)
│   ├── server.py                 # HTTP Server & API Router (/api/tutor/..., /api/solution)
│   ├── tutor_engine.py           # Mesin prompt AI Tutor konversasional & guardrails
│   ├── tutor_llm.py              # Provider LLM (Groq, OpenRouter, Ollama) + key rotators
│   ├── tutor_store.py            # SQLite manager (ai_tutor_users, sessions, quota, cooldown)
│   └── solution_loader.py        # Dynamic solution registry loader
│
├── pipeline/                     # TOOLING & PIPELINE OTOMASI OFFLINE
│   ├── 01_scraper_exam.py        # Playwright: Masuk portal, download HTML & gambar
│   ├── 02_scraper_kunci.py       # Playwright: Selesaikan tes & sedot kunci resmi
│   ├── 03_build_canonical.py     # Parser: HTML mentah -> Canonical Layer 2 JSON
│   ├── 04_generate_layer3.py     # Batch AI Generator: 5 pilar solusi (Claude/Reasoning)
│   └── 05_validate_integrity.py  # Audit runner: Validasi schema & cross-check kunci
│
├── web/                          # FRONTEND INTERFACE (CBT Learner App)
│   ├── index.html                # UI CBT Pusmendik modern + Sidebar AI Tutor
│   ├── style.css                 # Desain typography, KaTeX layout, badge model & quota
│   └── app.js                    # Navigasi soal, engine matematika KaTeX, chat stream
│
├── data/                         # DATABASE & DATA ASSETS TERSTRUKTUR
│   ├── ai_tutor.db               # SQLite database pengguna, kuota, tier & riwayat obrolan
│   │
│   ├── raw_html/                 # Backup tangkapan mentah HTML Pusmendik
│   │   └── sma/
│   │       ├── matematika/
│   │       └── ekonomi/
│   │
│   ├── media/                    # Seluruh aset gambar soal & opsi
│   │   └── sma/
│   │       ├── matematika/
│   │       │   ├── paket_1/images/
│   │       │   └── paket_2/images/
│   │       └── ekonomi/
│   │           ├── paket_1/images/
│   │           └── paket_2/images/
│   │
│   ├── canonical/                # LAYER 2: Sumber Kebenaran Soal & Formula (JSON)
│   │   └── sma/
│   │       ├── matematika_paket_1.json
│   │       ├── matematika_paket_2.json
│   │       ├── ekonomi_paket_1.json
│   │       └── ekonomi_paket_2.json
│   │
│   └── solutions/                # LAYER 3: Pembahasan 5 Pilar Human-Readable
│       ├── registry.json         # Router penentu file solusi aktif tiap mapel/paket
│       ├── MTK_PAKET_2_EXTRA.json
│       ├── EKO_PAKET_2_EXTRA.json
│       └── ...
│
└── tests/                        # AUTOMATED PYTEST SUITE
    ├── test_api_server.py
    ├── test_tutor_conversation.py
    └── test_solution_integrity.py
```

---

## 3. Protokol Scraping Portal Pusmendik CBT

Portal Pusmendik (`https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/`) menggunakan alur multi-step session. Otomasi Playwright dijalankan dengan urutan:

```
[Halaman Awal: Pemilihan Jenjang & Mapel]
  1. Pilih dropdown `#jenjang`: "sma", "smp", atau "sd".
  2. Pilih dropdown `#jenis_mapel`:
     - "1" = Mata Pelajaran Wajib (MTK, B. Indo, B. Inggris).
     - "2" = Mata Pelajaran Pilihan (Ekonomi, Fisika, Kimia, PKWU, dll).
  3. Buka custom dropdown `#mapel_toggle` dan klik `.mapel-option[data-value="..."]`.
  4. Klik tombol "Mulai Simulasi".
        ↓
[Gerbang Login Demo]
  5. URL beralih ke `/login/` -> Klik tombol "Login" (Kredensial demo otomatis terisi).
        ↓
[Konfirmasi Data Peserta & Refresh Token]
  6. URL beralih ke `/konfirmasi_data/`.
  7. ATURAN KRUSIAL: Klik tombol "Refresh" token satu kali.
  8. Ekstrak string token 6 karakter via Regex: `r"Token\s*[:=]\s*([A-Z0-9]{6})"`.
  9. Isi form `#nama_peserta` ("Peserta Simulasi"), tanggal lahir (`#tgl="01"`, `#bulan="01"`, `#tahun="2005"`).
 10. Masukkan token ke `#input-token` lalu klik "Submit".
        ↓
[Konfirmasi Tes & Masuk Bilik Ujian]
 11. URL beralih ke `/konfirmasi_tes/` -> Klik tombol "Mulai".
 12. Tunggu container `.soal-soal` termuat penuh.
 13. Ekstrak seluruh innerHTML bilik ujian (semua 25 atau 30 nomor soal).
        ↓
[Penyedotan Kunci Jawaban Resmi (Ground Truth)]
 14. Scraper melompat ke nomor terakhir (nomor 25).
 15. Klik tombol "Selesai Tes" -> Konfirmasi "Selesai".
 16. Halaman diarahkan ke rekap hasil tes Pusmendik yang memuat tabel kunci jawaban resmi untuk seluruh nomor soal.
 17. Scraper mengekstrak dan menyimpan kunci jawaban resmi tersebut ke `kunci_resmi.json`.
```

---

## 4. Pemrosesan Soal Bergambar & Vision Transcription (Layer 2)

Soal TKA memiliki 3 letak gambar:
1. **Gambar Stimulus** (di dalam `.cont-soal`): grafik, diagram, peta, atau teks narasi bergambar.
2. **Gambar Pertanyaan / Formula** (di dalam `.isi-soal`): rumus matematika inline atau bagan kasus.
3. **Gambar Opsi Jawaban** (di dalam elemen tabel opsi A, B, C, D, E).

### A. Strategi Unduh & Pengalamatan Relatif
- Semua gambar diunduh menggunakan penamaan deterministik:
  `soal_{nomor:02d}_stimulus_{idx:02d}.png` atau `soal_{nomor:02d}_opt_{key}.png`.
- Disimpan di: `data/media/<jenjang>/<mapel>/paket_<n>/images/`.
- Di dalam file JSON, path ditulis relatif (`images/soal_01_stimulus_01.png`), sehingga frontend dapat membaca aset secara dinamis tanpa hardcode absolute path.

### B. Prinsip Double-Channel (Pemisahan Tampilan Siswa vs Konteks AI)
- **Tampilan Siswa (Human View)**:
  Siswa **hanya melihat gambar visual asli**. Dilarang keras menampilkan teks transkrip gambar mentah bahasa Inggris seperti `[Diagram — soal_18_stimulus_01.png]: Illustration with two parts...` pada tampilan soal ataupun pembahasan.
- **Konteks AI (AI Vision Context)**:
  Model AI berbasis teks tidak dapat melihat gambar secara langsung. Oleh karena itu, skrip transkripsi vision (`_vision_batch.py`) menganalisis gambar dan menghasilkan representasi teks terstruktur:
  ```json
  {
    "visual_id": "V018",
    "representation_type": "diagram",
    "latex": null,
    "description": "Diagram kardus helm dengan dimensi 30 cm x 24 cm x 20 cm dan bak truk 3 m x 1.8 m x 1.6 m.",
    "confidence": "high"
  }
  ```
  Data ini disimpan di dalam kolom `visual_context` pada Canonical JSON (Layer 2) khusus untuk dikirim ke prompt AI reasoning, namun disembunyikan (`display: none`) dari pandangan siswa di UI.

### C. Ekstraksi Atribut `data-latex`
Simbol matematika pada tag gambar Pusmendik (`<img data-latex="...">`) diekstrak ke dalam array `formulas`:
```json
"formulas": [
  {"latex": "x^2 + 5x + 6 = 0", "source": "official data-latex"}
]
```
Hal ini memastikan rumus tidak berubah menjadi teks cacat akibat proses OCR biasa.

---

## 5. Generasi Solusi Pedagogis (Layer 3) & Penanganan Token Limit

Setelah Canonical JSON (Layer 2) terbentuk, kita membutuhkan model AI reasoning paling canggih (seperti **Claude 3.5 Sonnet**, **Claude 3.7 Sonnet (Thinking)**, atau **DeepSeek-R1**) untuk menghasilkan langkah pembahasan manusiawi berstandar tinggi.

### A. Pemilihan Model Terbaik
- **Model Utama**: `Claude 3.5 / 3.7 Sonnet`
  - *Alasan*: Penguasaan pedagogi bahasa Indonesia paling natural, mampu menghasilkan langkah matematis & analisis ekonomi tanpa kaku, serta sangat patuh pada format JSON ketat (*strict schema*).
- **Model Alternatif / Hemat Biaya**: `DeepSeek-R1` atau `Qwen-2.5-72b`
  - *Alasan*: Kemampuan reasoning deduktif yang kuat dengan biaya token terjangkau.

### B. Masalah Token Limit & Solusi "Micro-Batching"
Bila kita mengirim 25 soal sekaligus dalam 1 prompt ke model AI:
1. **Context/Output Truncation**: Model akan memotong jawaban di tengah jalan karena melewati batas `max_tokens` (biasanya 4096 atau 8192 token).
2. **Model Degradation (Kemalasan AI)**: Menjelang soal nomor 15 ke atas, AI mulai menghasilkan jawaban ringkas, generic, dan tidak detail.
3. **HTTP 429 Rate Limit (TPM/TPD)**: Melewati kuota token per menit pada provider API.

#### Solusi Standar Emas:
1. **Micro-Batching (5 Soal per Siklus)**:
   - Skrip generator (`pipeline/04_generate_layer3.py`) membagi 25 soal menjadi 5 batch:
     - Batch 1: Soal 1–5
     - Batch 2: Soal 6–10
     - Batch 3: Soal 11–15
     - Batch 4: Soal 16–20
     - Batch 5: Soal 21–25
2. **Idempotent Checkpointing (Fitur Resume)**:
   - Setiap batch yang selesai langsung ditulis ke file sementara (`.tmp.json`).
   - Jika koneksi terputus atau token habis di batch 3, skrip **tidak perlu mengulang dari soal nomor 1**. Saat dijalankan lagi, skrip otomatis membaca checkpoint dan melanjutkan mulai dari nomor 11.
3. **Rotasi Multi-API Key**:
   - Skrip mendukung daftar API key bergilir (`LLM_API_KEYS`). Jika key-1 terkena batas rate limit (HTTP 429), sistem otomatis memberi cooldown 25 detik pada key tersebut dan beralih ke key-2 tanpa menghentikan proses.

### C. Kontrak Format 5 Pilar Pedagogis
Setiap soal wajib menghasilkan JSON dengan struktur ketat berikut:
```json
{
  "question_id": "eko_p2_q01",
  "question_number": 1,
  "official_answer": {
    "format": "single",
    "correct": ["C"]
  },
  "concept_kunci": ["Pergeseran Kurva Permintaan", "Faktor Pendapatan Konsumen"],
  "glossary": [
    {"term": "Ceteris Paribus", "meaning": "Asumsi bahwa faktor-faktor lain dianggap tetap/konstan."}
  ],
  "reasoning": "Soal ini menguji pengaruh kenaikan upah riil terhadap barang normal...",
  "steps": [
    {"step": 1, "title": "Analisis Jenis Barang", "explanation": "..."},
    {"step": 2, "title": "Arah Pergeseran Kurva", "explanation": "..."}
  ],
  "why_correct": "Pilihan C benar karena kurva bergeser ke kanan atas...",
  "tips": ["Ingat aturan praktis: Kenaikan pendapatan selalu menggeser kurva barang normal ke KANAN."],
  "common_mistakes": ["Terkecoh menganggap harga barang itu sendiri yang berubah."],
  "diketahui": "Gunakan HANYA jika soal berbentuk hitungan konkret!",
  "ditanyakan": "Gunakan HANYA jika soal berbentuk hitungan konkret!"
}
```

---

## 6. Audit, Verifikasi Kunci Otoritatif, & Integrasi Registry

Sebelum file solusi dipublikasikan ke aplikasi pengguna, file tersebut wajib melewati gerbang validasi otomatis:

1. **Uji Validitas Skema**:
   - Memastikan tidak ada field wajib yang hilang (`validate_solution_doc`).
2. **Cross-Check Kunci Otoritatif**:
   - Membandingkan `official_answer.correct` hasil AI dengan kunci jawaban resmi Pusmendik.
   - **Kaidah Otoritas**: Kunci Pusmendik tidak boleh diganti secara sepihak. Bila hasil hitungan AI berbeda dengan kunci resmi, soal diberi tanda:
     `"needs_manual_review": true`, `"review_reason": "Pusmendik mengunci opsi C, sedangkan perhitungan matematis menghasilkan opsi B."`
3. **Pendaftaran di `registry.json`**:
   - Begitu file solusi siap (misal `EKO_PAKET_2_EXTRA.json`), file didaftarkan pada `data/solutions/registry.json`:
     ```json
     {
       "eko_paket_2": {
         "active_source": "EKO_PAKET_2_EXTRA.json"
       }
     }
     ```
   - Sistem backend langsung membaca file ini tanpa perlu merestart server ataupun memodifikasi kode JavaScript frontend.

---

## 7. Integrasi Ganda: Tata Cara Pembahasan & AI Tutor 2-Arah

File Layer 3 yang telah divalidasi memiliki fungsi ganda (*dual-purpose*):

1. **Tab "Tata Cara & Pembahasan" (Frontend)**:
   - Menampilkan kartu interaktif 5 pilar (Timeline Steps, Glosarium, Tips Cepat, dan Jebakan Soal) yang mudah dibaca oleh siswa.
2. **Konteks AI Tutor Cerdas**:
   - Dijadikan referensi dasar (*grounding truth*) bagi AI Tutor di sidebar.
   - Saat siswa bertanya: *"Bisa jelaskan langkah nomor 2 lebih sederhana?"* atau *"Kenapa jawabannya bukan D?"*, AI Tutor membaca Layer 3 dan memberikan bimbingan personal yang sabar dan konsisten dengan kunci resmi.
   - Dilengkapi sistem **Cooldown 10 Detik** dan **Kuota Harian** (10x gratis / 100x langganan) untuk menjaga keamanan token saat diakses banyak pengguna.
