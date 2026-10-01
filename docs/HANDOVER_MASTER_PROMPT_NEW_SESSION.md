# MASTER PROMPT & HANDOVER UNTUK SESI BARU
> **Dokumen Transisi & Blueprint Arsitektur TKA Learning Platform**  
> **Status:** Siap di-copy-paste ke sesi baru Antigravity / Agentic IDE  
> **Tujuan:** Menjalankan ulang seluruh pipeline dengan standar arsitektur 5 fase yang benar, memperbaiki semua bug fatal (opsi A-L, klasifikasi matriks keliru, gambar hilang, kuota & payment), serta mematuhi visi bisnis pemilik proyek.

---

```markdown
Halo Antigravity, saya ingin melanjutkan dan membenahi secara total proyek **TKA Simulasi & AI Learning Platform** (repositori: `d:\PROJECTS\SCRAPE_TKA`).
Sesi sebelumnya mengalami context window overload dan beberapa bug fatal pada pipeline data. Di sesi ini, kamu WAJIB membaca dan mematuhi seluruh spesifikasi di bawah ini TANPA mengambil jalan pintas dan TANPA mengulangi kesalahan masa lalu.

---

### 1. TUJUAN BISNIS & PRODUK (THE BIG PICTURE)
Platform ini dibangun untuk menyelesaikan masalah nyata: bimbingan belajar TKA (Tes Kemampuan Akademik SMA Kemdikbud) sangat mahal. Platform ini menyediakan pembelajaran mandiri berbasis soal simulasi resmi Pusmendik dengan dua pendekatan utama:
1. **Belajar 1-Arah**: Tab "Tata Cara & Langkah Penyelesaian" 5 Pilar (Konsep, Glosarium/Data, Langkah Step-by-Step, Alasan Mengapa Benar, Tips Cepat & Jebakan).
2. **Belajar 2-Arah**: AI Tutor Interaktif di sidebar yang memandu siswa secara sabar, melihat gambar diagram secara multimodal, dan terikat pada kunci resmi.
3. **Latihan Soal Mirip**: Menghasilkan soal serupa tanpa gambar untuk menguji pemahaman konsep siswa.

**Rencana Komersialisasi & Monetisasi:**
- Otentikasi: Login menggunakan **Google OAuth** agar riwayat percakapan dan progres siswa tersimpan di akun masing-masing.
- Sistem Kuota & Anti-Spam: Pengguna gratis dibatasi **10 pesan/hari** (mencegah kehabisan kuota API jika ada 50+ user bersamaan).
- Sistem Pembayaran Online: Integrasi payment gateway (misal Midtrans/Xendit) agar pengguna dari luar kota bisa berlangganan paket penuh (100 pesan/hari atau unlimited).

---

### 2. AUDIT KEGAGALAN FATAL SESI LALU (DILARANG KERAS DIULANGI!)
Kamu wajib tahu kesalahan fatal yang terjadi di sesi sebelumnya agar tidak mengulanginya:
1. **Bug Opsi A sampai L (Kasus Biologi Paket 1 Nomor 9)**:
   - *Penyebab*: Scraper menemukan tabel HTML hasil uji laboratorium klinis darah di dalam soal, lalu secara naif menganggap tabel data tersebut adalah tabel pilihan jawaban! Akibatnya, nilai angka laboratorium (279, 32.6, 12.4, dsb.) dijadikan opsi jawaban A, B, C, D, E, F, G, H, I, J, K, L! Sementara opsi pilihan kotak centang aslinya yang ada di bawah tabel terabaikan.
   - *Aturan Baku*: Scraper HARUS membedakan antara **Tabel Data Stimulus** (tidak ada input radio/checkbox di dalamnya) dengan **Tabel Pilihan Jawaban** (memiliki elemen `<input type="radio">` atau `<input type="checkbox">`).
2. **Bug Semua Soal Menjadi "Matriks" & Opsi Jawaban Hilang (Kasus Kimia Paket 1 Nomor 1)**:
   - *Penyebab*: Aturan deteksi matriks memeriksa `len(inputs) >= 4`. Akibatnya, soal Pilihan Ganda biasa yang punya 5 opsi (A, B, C, D, E) keliru diklasifikasikan sebagai tipe "Matriks", dan opsi jawabannya dimasukkan ke field `pernyataan` bukan `pilihan_jawaban`. Di frontend, opsi jawaban menjadi tidak muncul sama sekali!
   - *Aturan Baku*: Tipe "Matriks / Benar-Salah" HANYA berlaku jika ada tabel dengan multi-baris di mana setiap baris memiliki radio button independen (misal pilihan per baris 1, 2, 3). Soal PG biasa yang hanya memilih satu opsi dari daftar WAJIB tetap bertipe `Pilihan Ganda` dan disimpan di `pilihan_jawaban`.
3. **Bug Pembahasan Generic / Seragam**:
   - Pembahasan 5 pilar tidak boleh menggunakan template generic. Pembahasan harus spesifik membahas data dan angka soal tersebut.
4. **Bug Penempatan Gambar & Ukuran**:
   - Gambar tidak boleh digantikan oleh teks mentah transkripsi di tampilan CBT siswa. Siswa harus melihat gambar asli dengan ukuran proporsional dan estetik.

---

### 3. ARSITEKTUR 5 FASE STANDAR RESMI

#### FASE 1: SCRAPING VERBATIM 100% (PORTAL PUSMENDIK CBT)
- URL: `https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/`
- Alur: Pilih Jenjang (SMA) -> Jenis Mapel (1=Wajib, 2=Pilihan) -> Pilih Mapel -> Login Demo -> Refresh Token 1x -> Isi Form -> Mulai Tes.
- Mengambil:
  1. Seluruh teks stimulus, body soal, pertanyaan.
  2. Seluruh gambar asli (stimulus, prompt, dan opsi) diunduh lokal ke: `data/<mapel>/paket_<n>/images/`.
  3. Seluruh pilihan jawaban / pernyataan tabel yang valid.
  4. **Kunci Jawaban Resmi Otoritatif**: Di akhir tes, lompat ke nomor terakhir, klik opsi terakhir, submit `finish_tes`, masuk ke `review_hasil`, sedot tabel kunci resmi, dan simpan ke `data/kunci/<slug>_kunci.json`. Kunci resmi adalah SINGLE GROUND TRUTH (MUTLAK).

#### FASE 2: DATA CLEANING & REPAIR (DATA CLEANSER)
- Pisahkan data mentah kotor ke struktur bersih:
  - Ekstrak tag `<img data-latex="...">` menjadi rumus KaTeX `$formula$`.
  - Bersihkan tag XML/script yang rusak.
  - Normalisasi tipe soal: `Pilihan Ganda`, `Pilihan Ganda Kompleks`, `Benar-Salah`, atau `Matriks`.
  - Pastikan semua file gambar yang tertulis di JSON benar-benar ada di disk fisik (`os.path.isfile`).

#### FASE 3: VISION TRANSCRIPTION & PENCIPTAAN 2 TIPE FILE
Fase ini menghasilkan DUA tipe representasi:
- **Tipe A (File Asli / Human Visual untuk CBT App)**:
  - Menyimpan path relatif ke gambar asli (`images/soal_xx.png`).
  - Digunakan langsung oleh frontend CBT (`index.html`) agar siswa melihat grafik, bagan, dan peta asli dengan layout rapi.
- **Tipe B (File Teks Transkripsi Lengkap untuk AI Reasoning)**:
  - AI Vision mentranskripsi seluruh isi gambar menjadi teks deskriptif teknis yang mendalam (misal: struktur kimia, angka pada grafik, sumbu diagram, bagan sel).
  - Teks transkripsi ini disatukan ke dalam file JSON/MD sehingga model AI di Fase 4 dapat membaca seluruh konteks visual tanpa buta konteks dan tanpa batasan token media.

#### FASE 4: AI REASONING (5 PILAR PEDAGOGIS + SOAL MIRIP)
- Menggunakan data Tipe B + Kunci Otoritatif Resmi.
- Model AI (Claude / Gemini Pro) menghasilkan pembahasan terstruktur:
  1. **Konsep Kunci**: Teori dan rumus dasar.
  2. **Glosarium & Data Soal**: Variabel diketahui dan ditanyakan.
  3. **Langkah Penyelesaian Rinci**: Step-by-step terperinci.
  4. **Alasan Mengapa Pilihan Ini Benar**: Pembuktian logis mengapa kunci resmi tepat.
  5. **Tips Cepat & Jebakan Umum**: Trik eliminasi dan jebakan yang harus dihindari siswa.
  6. **Soal Latihan Serupa (Similar Practice Question)**: Soal berbasis teks yang setipe untuk menguji pemahaman siswa.
- KUNCI RESMI DARI PUSMENDIK DIKUNCI MATI. AI DILARANG MENGARANG ATAU MEMBANTAH KUNCI.
- Output disimpan di: `data/solution_sources/<SLUG_UPPER>_SOLUTIONS.json`.

#### FASE 5: INTEGRASI CBT, SERVING, & QUALITY AUDITOR
1. **Quality Gate Otomatis**:
   - Jalankan validator `solution_loader.validate_solution_doc()`.
   - Cek 100% kesesuaian kunci resmi.
   - Daftarkan ke `data/solution_sources/registry.json`.
2. **Serving Backend & Frontend**:
   - Backend `server.py` melayani API `/api/solution`, `/api/tutor/chat`, dan image serving rekursif.
   - Frontend `index.html` & `app.js` menampilkan kartu 5 pilar dan CBT yang rapi.
   - AI Tutor terhubung dengan konteks Layer 2 + 5 Pilar + Multimodal Vision (Gemini 3 Flash).
3. **Auditor Akhir**: Memverifikasi bahwa tidak ada gambar yang hilang, tidak ada opsi A-L palsu, dan semua soal berfungsi sempurna sebelum diserahkan ke Bos (User).

---

### 4. TUGAS PERTAMA KAMU DI SESI BARU
1. Konfirmasi bahwa kamu telah membaca dan memahami master prompt ini seutuhnya.
2. Tinjau struktur folder `d:\PROJECTS\SCRAPE_TKA\data\` dan periksa mapel mana saja yang sudah ada vs yang perlu diaudit.
3. Tunggu instruksi spesifik dari saya mengenai mapel mana yang akan kita audit dan eksekusi berikutnya secara presisi.
```
