# BLUEPRINT & PRD: STANDAR OPERASIONAL PROSEDUR (SOP) OTOMASI END-TO-END SEMUA MAPEL TKA
> **Versi Dokumen:** 2.0 (Post-Fisika & Geografi Lessons Learned)  
> **Status:** Mandatory Architectural Standard  
> **Tujuan:** Menjamin pipeline otomatisasi dari scraping portal Pusmendik hingga CBT & AI Tutor berjalan 100% presisi tanpa bug gambar hilang, kunci meleset, atau konteks AI kosong.

---

## 1. LATAR BELAKANG & AUDIT KEGAGALAN (LESSONS LEARNED)

Pada implementasi **Fisika** dan **Geografi**, sistem mengalami beberapa kendala penyesuaian berulang. Audit forensik menemukan 4 akar masalah krusial:

### A. Masalah 1: Gambar Diagram Hilang / Broken Image
* **Akar Masalah:**
  1. Pusmendik tidak konsisten: Gambar kadang ditaruh pada field `stimulus.images`, namun sangat sering disisipkan langsung sebagai tag `<img src="...">` di dalam string HTML mentah `pertanyaan.html` atau opsi jawaban.
  2. Direktori simpanan tersebar di `data/<mapel>/paket_<n>/images/`, sedangkan server awal hanya mencari di folder `data/paket_1/` dan `data/paket_2/`.
* **Solusi Baku:**
  1. Parser scraping menggunakan regex HTML untuk menyedot seluruh tag `<img>` dari stimulus, soal, dan opsi tanpa ada yang tertinggal.
  2. Endpoint `/images/<filename>` di [`server.py`](file:///d:/PROJECTS/SCRAPE_TKA/server.py) memiliki mekanisme **Multi-Directory Fallback + Recursive Search**, sehingga gambar di folder mapel apa pun langsung ditemukan dan disajikan ke browser.
  3. AI Tutor Vision membaca path fisik file PNG langsung dari disk lokal dan mengubahnya menjadi base64 inline data untuk dikirim ke Gemini 3 Flash.

### B. Masalah 2: Kunci Jawaban Resmi Ngawur / Mismatch
* **Akar Masalah:**
  1. Pada tipe soal **Tabel Benar-Salah (BS)** dan **Pilihan Ganda Kompleks (PGK)**, data scraping mentah dari bilik ujian hanya merekam status radio button yang belum tentu lengkap.
  2. Saat prompt AI (Claude/Gemini) dibuat tanpa menyertakan kunci resmi otoritatif, AI disuruh menebak/menghitung sendiri. Jika ada ambiguitas soal atau perbedaan interpretasi kurikulum, AI menghasilkan kunci yang bertolak belakang dengan kunci resmi Kemdikbud/Pusmendik.
* **Solusi Baku:**
  1. Kunci resmi **TIDAK BOLEH DITEBAK**. Kunci resmi wajib disedot langsung dari **halaman rekap hasil tes (`review_hasil`)** di akhir simulasi Pusmendik melalui skrip automated Playwright ([`_harvest_keys.py`](file:///d:/PROJECTS/SCRAPE_TKA/_harvest_keys.py)).
  2. Format dinormalisasi secara baku:
     * PG Tunggal: `"kunci": "A"`
     * PG Kompleks: `"kunci": ["A", "C"]`
     * Tabel Benar-Salah: `"kunci": {"A": "Benar", "B": "Salah", "C": "Benar"}`
  3. Kunci otoritatif ini **DIKUNCI MATI** ke dalam prompt pembuatan Layer 3. AI dilarang keras membantah atau mengarang kunci sendiri.

### C. Masalah 3: Konteks AI Tutor Kosong / Halusinasi
* **Akar Masalah:**
  1. Mesin AI Tutor awalnya hanya membaca `stimulus.text`. Pada soal sains/geografi, stimulus teksnya sering hanya berbunyi: *"Perhatikan gambar berikut!"*. Akibatnya AI Tutor tidak tahu apa diagramnya, tidak tahu tabel datanya, dan tidak tahu apa yang ditanyakan.
* **Solusi Baku:**
  1. Menggunakan arsitektur **Dual-Channel**:
     * **Channel 1 (Vision Multimodal)**: AI Tutor membaca file gambar PNG asli secara langsung menggunakan Gemini 3 Flash Vision.
     * **Channel 2 (Canonical Context Layer 2)**: Menyuplai teks stimulus, teks pertanyaan, daftar pernyataan/opsi, formula LaTeX resmi (`data-latex`), dan data diketahui ke system prompt tutor.

### D. Masalah 4: Pembahasan 5 Pilar Tidak Seragam
* **Akar Masalah:**
  1. Pembahasan yang dibuat manual atau parsial sering tidak memuat 5 pilar pedagogis lengkap (Konsep, Glosarium/Data, Langkah Rinci, Alur Logika, Tips & Jebakan), membuat tampilan UI menjadi kosong atau tidak terstruktur.
* **Solusi Baku:**
  1. Seluruh pembahasan wajib melewati kontrak skema JSON Layer 3 yang divalidasi oleh [`solution_loader.validate_solution_doc()`](file:///d:/PROJECTS/SCRAPE_TKA/solution_loader.py) sebelum didaftarkan ke `registry.json`.

---

## 2. BLUEPRINT 5 DIVISI OTOMASI STANDAR

Setiap penambahan mata pelajaran baru wajib menempuh alur 5 divisi yang terisolasi dan deterministik berikut:

```
┌────────────────────────────────────────────────────────────────────────┐
│ DIVISI 1: Scraping Portal Pusmendik CBT                                │
│ Input : Jenjang (SMA), Jenis Mapel (1=Wajib, 2=Pilihan), Mapel ID      │
│ Output: Raw Exam HTML + Aset Gambar PNG + Kunci Otoritatif             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ DIVISI 2: Normalisasi Layer 2 (Canonical JSON Data)                   │
│ Input : Raw Data & Hasil Panen Kunci                                   │
│ Output: `<mapel>_paket_<n>_learning.json` & Image Asset Catalog        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ DIVISI 3: AI Reasoning & 5 Pilar Solution Generator (Layer 3)          │
│ Input : Canonical JSON + File Gambar PNG + Kunci Otoritatif            │
│ Model : Claude 3.5/3.7 Sonnet ATAU Gemini Pro / DeepSeek-R1 (Micro-Batch)│
│ Output: `<MAPEL>_PAKET_<N>_SOLUTIONS.json` (5 Pilar Pedagogis Lengkap) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ DIVISI 4: Quality Gate & Automated Integrity Audit                     │
│ Validasi: Schema 5 Pilar, 100% Cocok Kunci Pusmendik, File Gambar Utuh │
│ Output: Pendaftaran ke `data/solution_sources/registry.json`           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ DIVISI 5: CBT Serving & Multimodal AI Tutor Synchronization            │
│ Target: Web UI http://localhost:8080/                                  │
│ Output: Tab Pembahasan 5 Pilar Aktif + AI Tutor Multi-Turn Vision Ready│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. SPESIFIKASI TEKNIS PER DIVISI

### DIVISI 1: SCRAPING PORTAL PUSMENDIK CBT

* **Alat Utama:** Playwright Headless Browser ([`scraper_tka.py`](file:///d:/PROJECTS/SCRAPE_TKA/scraper_tka.py) & [`_harvest_keys.py`](file:///d:/PROJECTS/SCRAPE_TKA/_harvest_keys.py)).
* **Protokol Eksekusi:**
  1. Buka URL: `https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/`.
  2. Pilih `#jenjang`: `"sma"`.
  3. Pilih `#jenis_mapel`: `"1"` (Wajib) atau `"2"` (Pilihan).
  4. Buka `#mapel_toggle`, klik `.mapel-option[data-value="<ID>"]`.
  5. Masuk ke halaman login -> Klik Login Demo.
  6. Refresh token satu kali -> Ambil regex `Token\s*[:=]\s*([A-Z0-9]{6})`.
  7. Isi form peserta dan masukkan token -> Klik Submit -> Klik Mulai Tes.
  8. **Sedot Soal & Media:**
     * Ekstrak innerHTML bilik ujian seluruh nomor soal.
     * Unduh seluruh file gambar stimulus dan opsi ke:
       `data/<mapel>/paket_<n>/images/` dengan penamaan deterministik:
       `soal_{nomor:02d}_stimulus_{idx:02d}.png` atau nama hash asli dari server Pusmendik.
  9. **Sedot Kunci Otoritatif (Ground Truth):**
     * Jalankan `window.lihatSoal(total_soal)` via JavaScript injection.
     * Klik opsi soal terakhir dengan `{force: true}`.
     * Klik `#nextSoal` -> Masuk ke halaman `finish_tes`.
     * Klik `SELESAI TES` -> Redirect ke `review_hasil`.
     * Ekstrak tabel review hasil:
       * Kolom 1: Nomor Soal
       * Kolom 2: Jawaban Peserta
       * Kolom 3: Kunci Jawaban Resmi Pusmendik
     * Simpan ke file: `data/kunci/<mapel>_paket_<n>_kunci.json`.

---

### DIVISI 2: NORMALISASI LAYER 2 (CANONICAL DATA REPAIR)

* **Alat Utama:** Script Parser & Data Enricher.
* **Protokol Eksekusi:**
  1. **Sanitasi HTML:** Bersihkan script tracker, inline style merusak, dan tag tidak perlu.
  2. **Ekstraksi KaTeX:** Konversi tag `<img data-latex="...">` menjadi teks rumus LaTeX: `$data-latex$`.
  3. **Normalisasi Format Tipe Soal:**
     * `Pilihan Ganda`: Opsi A, B, C, D, E.
     * `Pilihan Ganda Kompleks`: Checklist kotak centang (bisa memilih > 1).
     * `Benar / Salah`: Tabel pernyataan dengan kolom Benar dan Salah.
  4. **Image Binding Audit:**
     * Cek apakah semua file gambar yang tertulis di JSON benar-benar ada di direktori fisik disk (`os.path.isfile`).
     * Jika ada gambar hilang, tandai untuk re-download langsung via URL remote Pusmendik.
  5. **Binding Kunci Otoritatif:**
     * Masukkan kunci resmi yang didapat dari Divisi 1 ke dalam field `kunci_jawaban` pada:
       `data/<mapel>_paket_<n>_learning.json`.

---

### DIVISI 3: GENERASI SOLUSI 5 PILAR LAYER 3 (AI REASONING)

* **Alat Utama:** Micro-Batch Prompting Generator (Claude 3.5 / 3.7 Sonnet atau Gemini Pro Vision).
* **Strategi Micro-Batching (Anti-Token Limit & Kemalasan AI):**
  * 25 soal dibagi menjadi 5 batch (masing-masing 5 soal per batch).
  * Menyertakan file gambar PNG asli atau transkripsi diagram ke dalam prompt.
* **Aturan Mutlak (Strict System Prompt Constraints):**
  * **KUNCI RESMI TIDAK BOLEH DIUBAH.** Jawaban akhir wajib membuktikan mengapa kunci resmi tersebut benar.
  * Jika ada interpretasi ganda, jelaskan dasar logika yang digunakan oleh pembuat soal resmi.
* **Kontrak Output JSON 5 Pilar:**
  ```json
  {
    "question_id": "<prefix>_p<paket>_q<nomor:02d>",
    "question_number": 1,
    "official_answer": {
      "format": "single",
      "correct": ["A"]
    },
    "concept_kunci": ["Hukum Hess", "Termokimia"],
    "glossary": [
      {"term": "ΔH (Entalpi)", "meaning": "Perubahan kalor reaksi pada tekanan tetap."}
    ],
    "diketahui": "ΔH1 = -393.5 kJ, ΔH2 = -285.8 kJ",
    "ditanyakan": "Perubahan entalpi pembentukan standar benzena",
    "steps": [
      {"step": 1, "title": "Penyusunan Persamaan Reaksi", "explanation": "..."},
      {"step": 2, "title": "Eliminasi dan Penjumlahan Entalpi", "explanation": "..."}
    ],
    "why_correct": "Pilihan A benar karena hasil penjumlahan aljabar entalpi reaksi adalah +49.0 kJ.",
    "tips": ["Balik reaksi jika senyawa berada di sisi yang berlawanan dan kalikan koefisiennya."],
    "common_mistakes": ["Lupa membalik tanda positif/negatif entalpi saat reaksi dibalik."]
  }
  ```
* **Penyimpanan:** File disimpan di `data/solution_sources/<MAPEL>_PAKET_<N>_SOLUTIONS.json`.

---

### DIVISI 4: QUALITY GATE & AUTOMATED INTEGRITY AUDIT

Sebelum file solusi boleh didaftarkan ke sistem produksi, script validator wajib dijalankan:

1. **Uji Skema 5 Pilar:**
   * Menjalankan `solution_loader.validate_solution_doc(doc)`.
   * Memastikan field `concept_kunci`, `glossary`, `steps`, `why_correct`, `tips`, dan `common_mistakes` tidak boleh kosong atau bertipe salah.
2. **Audit Kunci 100% Match:**
   * Script mencocokkan `doc["official_answer"]` dengan `data/kunci/<mapel>_paket_<n>_kunci.json`.
   * Jika ada perbedaan 1 karakter pun, build digagalkan (*loud failure*).
3. **Audit Fisik Gambar:**
   * Script memeriksa apakah semua gambar yang direferensikan soal ada di disk fisik.
4. **Pendaftaran Otomatis ke Registry:**
   * Tambahkan konfigurasi ke `data/solution_sources/registry.json`:
     ```json
     "<slug>_paket_<n>": {
       "active_source": "<MAPEL>_PAKET_<N>_SOLUTIONS.json"
     }
     ```

---

### DIVISI 5: CBT SERVING & MULTIMODAL AI TUTOR SYNC

1. **Konfigurasi Backend ([`server.py`](file:///d:/PROJECTS/SCRAPE_TKA/server.py)):**
   * Daftarkan mapel baru ke dictionary `SUBJECT_SLUGS` dan `SUBJECT_NAMES`.
   * Verifikasi rute `/images/<file>` dapat melayani gambar mapel baru tersebut.
2. **Konfigurasi Frontend ([`index.html`](file:///d:/PROJECTS/SCRAPE_TKA/index.html) & [`app.js`](file:///d:/PROJECTS/SCRAPE_TKA/app.js)):**
   * Daftarkan mapel baru ke selector mata pelajaran di UI CBT.
3. **Verifikasi AI Tutor Multimodal:**
   * AI Tutor membaca konteks Layer 2 + Layer 3.
   * Saat siswa bertanya mengenai diagram, Gemini 3 Flash langsung menerima gambar PNG lokal dari backend dan merespons pertanyaan siswa secara akurat tanpa bertele-tele.
4. **Verifikasi Tombol Testing Admin:**
   * Tombol `Reset Kuota` dan `+ Chat Baru` tetap aktif selama masa uji coba admin.

---

## 4. RENCANA EKSEKUSI: UJI COBA 2 MATA PELAJARAN (PAKET 1 & PAKET 2)

Sesuai permintaan untuk menguji coba 2 mata pelajaran (4 paket ujian lengkap):

### Pilihan Mapel Uji Coba:
1. **Mata Pelajaran 1: KIMIA (SMA Pilihan)**
   * **Paket 1:** ID `9` (Jenis Mapel: `2`)
   * **Paket 2:** ID `89` (Jenis Mapel: `2`)
   * *Alasan Pemilihan:* Menguji ketahanan parsing rumus molekul, reaksi kimia, tabel data periodik, dan diagram reaksi.
2. **Mata Pelajaran 2: BIOLOGI (SMA Pilihan)**
   * **Paket 1:** ID `10` (Jenis Mapel: `2`)
   * **Paket 2:** ID `90` (Jenis Mapel: `2`)
   * *Alasan Pemilihan:* Menguji ketahanan penanganan gambar mikroskopis, organ, bagan siklus sel, dan soal tipe tabel Benar-Salah.

*(Alternatif jika ingin mapel sosial/bahasa: Sosiologi ID 14 & 94 atau Bahasa Indonesia ID 2 & 83).*

---

## 5. CHECKLIST VERIFIKASI SEBELUM EKSEKUSI

- [x] Akar masalah Fisika & Geografi teridentifikasi dan tersolusi di codebase.
- [x] Multi-directory recursive image serving di `server.py` aktif.
- [x] Ekstraksi kunci otoritatif Pusmendik di `_harvest_keys.py` aktif.
- [x] AI Tutor Gemini 3 Flash multimodal vision aktif.
- [x] Validator skema `solution_loader.py` aktif.
- [ ] Persetujuan User terhadap Blueprint ini untuk memulai eksekusi.
