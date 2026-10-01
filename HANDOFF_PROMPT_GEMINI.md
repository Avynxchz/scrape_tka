# HANDOFF PROMPT — LANJUTKAN PROJECT SCRAPE_TKA (untuk Gemini)

> Gemini, baca prompt ini SAMPAI HABIS sebelum melakukan apa pun. Ini adalah handoff lengkap dari sesi kerja AI sebelumnya (AutoClaw) bersama owner project. Kamu mewarisi SEMUA konteks di bawah ini — jangan ulangi pekerjaan yang sudah selesai, cukup lanjutkan dari bagian "TUGAS TERBUKA" di bagian akhir.

---

## 1. KONTEKS PROJECT

- **Project:** `SCRAPE_TKA` di `D:\PROJECTS\SCRAPE_TKA` — aplikasi CBT (Computer-Based Test) simulasi ujian TKA (Pusmendik, Kemendikdasmen) dengan AI Tutor.
- **Stack:** Frontend vanilla (`index.html`, `app.js`, `style.css`), backend Python stdlib (`server.py`, port 8080), database tutor (`ai_tutor.db`), pipeline swarm 5 divisi (`pipeline/swarm_manager.py`), data JSON di `data/` (±160 MB).
- **Tujuan owner:** pipeline fase 1–5 "perfect by default" — tekan tombol swarm di `swarm.html`, semua mapel masuk lengkap (soal, opsi, gambar + penempatan, kunci) + pembahasan berkualitas tanpa perbaikan manual — supaya bisa bulk-scrape 21 paket yang belum di-scrape sambil ngejar waktu (rencana lanjut: OAuth login, database, deploy).
- **Fase swarm:**
  1. **Divisi 1 Scout** — scraping Pusmendik + kunci resmi (`scraper_tka.py`, `pipeline/01_ingress_*.py`), cache per paket.
  2. **Divisi 2 Architect** — normalisasi + pemisahan artefak Tipe A (CBT visual) & Tipe B (AI text), pakai `text_quality.py`.
  3. **Divisi 3 Visionary** — transkripsi gambar via **Google AI Studio Playground gratis** (Playwright → Chrome remote debugging port 9222; `pipeline/playwright_aistudio_bridge.py`, fungsi `run_phase_3_via_playwright`).
  4. **Divisi 4 Reasoning** — solusi 5 pilar (diketahui/ditanyakan/konsep/langkah/tips) + soal serupa, juga via AI Studio (`run_phase_4_via_playwright`), fallback API `gemini_reasoner.py`.
  5. **Divisi 5 Auditor** — audit deterministik 9 kriteria + hot-reload registry (`data/solution_sources/registry.json` → `solution_loader.py`).
- **Tutor AI:** `tutor_llm.py` — failover lintas provider Gemini→Groq (3 kunci round-robin, cooldown 20s), default UI diarahkan ke Qwen/Groq. `.env` berisi `LLM_API_KEYS` (3) + `GEMINI_API_KEYS` (3). JANGAN jalankan API tutor tanpa perlu — kuota terbatas.
- **Rendering matematika:** KaTeX 0.16.9 via CDN (auto-render, delimiters `$$`, `$`, `\(`, `\[`). Fungsi `renderMath()` di `app.js` (±baris 2502). Helper `_fmtText`/`_escHtml` di `app.js` ±baris 1132–1145. Server membersihkan payload `/api/solution` via `clean_katex_artifacts()` (`server.py` ±baris 198).
- **Data saat ini:** 25 file `data/*_learning.json` = **601 soal** (BI 45, Bing 45, Bio 49, Eko 49, Fis 44, Geo 39, PKW 40, Kim 44, MTK 71, MTL 45, Sejarah 39, Sos 20). 23 file solusi aktif di `data/solution_sources/` ditunjuk `registry.json`. 23 paket live / 44 total katalog (`/api/swarm/subjects`).
- **Catatan struktur:** `data/paket_1_learning.json` & `paket_2_learning.json` adalah file generik LEGACY (isinya matematika, 46+ soal "hotel") — BUKAN file aktif mapel lain; jangan dijadikan patokan jumlah soal mapel.

---

## 2. RIWAYAT SESI SEBELUMNYA (ZCode/GLM — sebelum saya)

Sesi lama (share: https://zcode.z.ai/share/bBm7wx5VCryvw7LYO98vwtFoWw_yC4Xr, full transcript terekstrak di `scratch/zai_share_full.md`) sudah menyelesaikan:
1. Akar "pembahasan aneh": ekstraksi DOM fase 2 pakai `get_text("\n")` yang pecah per karakter di batas tag inline → dibuat modul normalizer `text_quality.py` (idempoten: map unicode math italic U+1D400–1D7FF→ASCII, merge baris pecah, word-symbol `times→×` dll, dedupe echo, regex derajat `30 O) → 30°)`), patch fase 2, upgrade `clean_katex_artifacts` server.py → ±547 field direpair (backup `data/backup_text_repair_20260929_050255/` dan `..._051009/`).
2. Solusi MTL P1 20/20 & P2 25/25 yang rusak direpair ulang (±4.875 field math; backup `data/backup_render_fix_20260929/`).
3. Tutor: fallback Gemini→Groq diimplementasi (sebelumnya Gemini 429 = tutor mati total dengan pesan "Penjelasan dari AI belum berhasil (rate_limit)").
4. Bridge AI Studio: anti prompt-echo (`extract_latest_response` memilih turn terpanjang → prompt JSON ikut terpilih), deteksi selesai lebih ketat, chat baru per run untuk FASE 3, fase 3 vision gratis via Playground.
5. Fase 2: preservasi `soal_serupa` saat re-run; auditor + cek tambahan; fix opsi A/B/C/D dobel (`full_display`).
6. **Yang terhenti di sesi itu:** regenerasi MTL P2 + Sejarah P2 dihentikan user di tengah jalan; handoff prompt tidak sempat ditulis (itulah kenapa sesi saya dimulai).

---

## 3. YANG SUDAH SAYA KERJAKAN (sesi AutoClaw, 29 Sep 2026) — JANGAN DIULANG

### 3.1 Ekstraksi history & audit konteks
- Menemukan endpoint share ZCode: `GET https://zcode.z.ai/api/v1/shares/<share_id>/preview` (tanpa auth) → seluruh 14 turn percakapan lama (960K char) terekstrak ke `scratch/zai_share_full.md`.
- Audit arsitektur penuh: jalur render lengkap, status perbaikan, kondisi data (detail di `.zwork/runs/...` — intinya sudah dipadukan ke bagian ini).

### 3.2 Fix rendering panel "soal serupa" (`app.js`) — Pola Bug #1
- Defek: `promptEl.innerText = ...` dan opsi soal serupa diisi via `innerText`/tanpa escape → LaTeX `$...$` TIDAK PERNAH dirender KaTeX (user melihat `lim_{x\to3}\frac...` mentah). Juga `sim.pembahasan` disuntik tanpa escape.
- Fix: 4 titik di panel soal serupa (prompt ±2081, opsi ±2099, feedback ±2172 & ±2178) sekarang pakai `_fmtText(...)` + `innerHTML`, mengikuti pola panel pembahasan. Cache-bust `index.html`: `app.js?v=28`. `node --check` lolos.

### 3.3 Restore Sejarah Paket 2 (kontaminasi lintas-mapel) — Pola Bug #4
- File aktif `data/solution_sources/SEJARAH_PAKET_2_SOLUTIONS.json` pernah berisi 20 solusi KONTAMINASI (q1 "Matriks dan." padahal mapel sejarah; ada trigonometri & kinematika; q21–29 hilang). Sumber: generator lama menimpa dengan jawaban mapel lain.
- Fix: restore dari `data/backup_solutions_20260929/` (29 solusi benar, konten Ki Hajar Dewantara/Banten). Backup versi rusak di `data/backup_restore_sejarah_20260929/`.

### 3.4 Pembersihan data menyeluruh (idempoten)
- Script `scratch/_fix_render_data_20260929.py`: backup ke `data/backup_render_fix_20260929_v2/` (struktur relatif dipertahankan) → bersihkan field user-visible di 25 learning JSON + 23 file solusi via `text_quality.repair_math_text`; field `data_latex` (atribut gambar, LEGITIM) tidak disentuh; field `html` hanya light-fix (mojibake + unicode italic). 18 field dibenahi di 7 file (BI, Bing, Fisika, MTK, MTL P1, paket generik).
- Script `scratch/_fix_righarrow_20260929.py`: bersihkan artefak `rigℎta r row→` (pecahan "rightarrow" dari pipeline ekstraaksi lama) — 62 kemunculan di solusi Sejarah + varian `leftrigℎ t ar ow leftrightarrow → ↔`. Aman dijalankan ulang (idempoten).
- Scanner: `python _scan_render_garbage.py` → kondisi akhir hanya 4 temuan LEGITIM (attribute `data-latex` gambar reaksi reversible kimia P2). Kondisi ini yang diharapkan.

### 3.5 Fix kontaminasi lintas-target fase 4 (AKAR MASALAH BESAR) — Pola Bug #6
- **Gejala:** re-run swarm untuk `sejarah_paket_2` menghasilkan solusi berisi jawaban MTK Lanjut P1 (determinan matriks; similarity raw output antar-slug 0,9998; 20 solusi bukan 29). Audit gagal: "Solusi hanya mencakup 20/29 soal".
- **Akar (ditemukan & dibuktikan):**
  1. `extract_latest_response()` di `pipeline/playwright_aistudio_bridge.py` menerima argumen `turn_index_start` tapi TIDAK PERNAH memakainya — JS-nya memindai SEMUA turn chat dari belakang dan mengambil turn pertama yang ber-JSON → jawaban LAMA mapel lain terpilih.
  2. `run_phase_4_via_playwright()` tidak membuka chat baru — 1 percakapan AI Studio dipakai bergantian antar-target → konteks tercampur (fase 3 sudah benar, fase 4 belum).
- **Fix yang sudah diterapkan di `pipeline/playwright_aistudio_bridge.py` (compile OK):**
  1. `turn_index_start` diteruskan ke `page.evaluate`; pemindaian hanya turn ≥ indeks itu (fallback perilaku lama bila slice kosong).
  2. `run_phase_4_via_playwright`: `page = _resolve_standard_page(browser, page)` + `start_fresh_chat(page)` WAJIB sebelum injeksi prompt — raise RuntimeError jika gagal (1 target = 1 chat baru).
  3. Guard baru `_sanity_check_target_token(slug, raw_text)` (dipanggil ±baris 1107, helper ±869, token generator `_distinctive_tokens_for_slug` ±839): raw output wajib memuat ≥1 token khas target dari learning JSON (mis. "Banten" untuk sejarah) — kalau tidak, output stale DITOLAK sebelum ditulis file.
- **Bukti hasil:** re-run swarm `sejarah_paket_2` (POST `/api/swarm/start` `{"targets":["sejarah_paket_2"]}`) dengan bridge baru → fase 4 sukses 3,5 menit → **Audit Lolos 100%, 0 issues, 0 warnings, 29/29 solusi**. Scan bersih. MT Lanjut P1 juga lolos (0 issues, 1 warning wajar Q4 — transkripsi sumbernya memang miskin).

### 3.6 Fix korupsi on-the-fly di server (AKAR MASALAH "±atrix") — Pola Bug #7
- **Gejala (keluhan owner):** UI menampilkan `T = \begin{±atrix} -3 \\ 2 \end{±atrix}` padahal file di disk berisi `pmatrix` yang benar; `rg "±atrix" data/` = 0 hasil.
- **Akar:** `clean_katex_artifacts()` di `server.py` ±baris 213 memiliki rule `(r'\\?pm', r'±')` TANPA batas kata → substring "pm" di dalam command LaTeX `pmatrix` tersambar jadi `±atrix` SETIAP KALI payload di-serve. Rule serupa (`times`, `neq`, `leq`, `geq`, `approx`, `rightarrow`, `leftarrow`, `cdot`, `circ`, `degree`) berisiko sama.
- **Fix yang sudah diterapkan:** semua 11 rule diberi batas huruf `(?<![a-zA-Z])\\?word(?![a-zA-Z])` — digit tetap lolos (`4times2 → 4×2`), command LaTeX utuh aman (`pmatrix` tidak tersentuh). Compile OK.
- **Bukti:** server uji port 8081 dengan kode baru → `POST /api/solution` `{"subject":"matematika_lanjut","paket":2,"nomor":8}` mengembalikan `T = \begin{pmatrix} -3 \\ 2 \end{pmatrix}` utuh → KaTeX pasti merender matriks vertikal benar. Server uji sudah dimatikan.
- **PENTING:** owner harus RESTART server produksinya (Ctrl+C → `start_server.bat`) agar fix aktif — server lama di port 8080 masih memuat kode lama kalau belum direstart sejak 29 Sep malam.

### 3.7 Fix "diketahui" ambigu MTL P1 q1–q2
- `solutions[0].diketahui` = "Matriks dan." dan `solutions[1].diketahui` = "Matriks,, dan." (keluhan owner dari sesi lama). Penyebab: soal murni gambar, transkripsi teks kosong, AI mengarang kalimat kosong.
- Fix: diisi ulang dari transkripsi vision asli (`data/matematika_lanjut_paket_1_sidecar_transcriptions.json`):
  - q1: `Matriks $P = \begin{pmatrix} 1 & 2 \\ -1 & -4 \end{pmatrix}$ dan $Q = \begin{pmatrix} 2 & 5 \\ -1 & 2 \end{pmatrix}$.`
  - q2: `Matriks $A = \begin{pmatrix} -1 & 2 \\ 3 & 4 \end{pmatrix}$, $B = \begin{pmatrix} -2 & 0 \\ 3 & 3 \end{pmatrix}$, dan $C = \begin{pmatrix} -4 & 4 \\ -3 & 2 \end{pmatrix}$.`
- Script: `scratch/_fix_ambigu_mtl_p1.py`.

### 3.8 Dokumentasi playbook
- `docs/BUG_FIX_PLAYBOOK.md` — 7 pola bug + gejala + akar + solusi + cara deteksi + rutinitas verifikasi pasca-scrape. Filosofi owner: **ketemu bug > solve > catat > pola sama muncul lagi > langsung solve pakai playbook.** WAJIB baca sebelum mengerjakan bug apapun, dan WAJIB menambah pola baru ke situ setiap menemukan bug baru.

### 3.9 Backup penting (JANGAN diubah isinya)
- `data/backup_text_repair_20260929_050255/` & `_051009/` (sesi lama), `data/backup_render_fix_20260929/`, `data/backup_solutions_20260929/` (sumber restore Sejarah), `data/backup_render_fix_20260929_v2/` (sesi saya — sumber terbaik kondisi pra-cleaning).

---

## 4. TUGAS TERBUKA #1 (PRIORITAS) — KETERBACAAN PILAR 1 MTK LANJUT PAKET 2

Owner melaporkan (30 Sep 2026): **di "Tata Cara & Langkah Penyelesaian" matematika_lanjut paket 2, terutama pilar 1 (diketahui), kebanyakan tulisannya membuat mata manusia PUSING.** Ini bug keterbacaan yang BELUM diperbaiki. Fakta pendukung dari audit saya (contoh nyata di `data/solution_sources/MATEMATIKA_LANJUT_PAKET_2_SOLUTIONS.json`):

1. **Saturasi LaTeX inline rapat** — satu baris panjang memuat banyak segmen `$...$` berdempetan, contoh `steps`:
   `"$x' = x - 3 \iff x = x' + 3$ $y' = y + 2 \iff y = y' - 2$"` — dua persamaan digabung satu baris tanpa pemisah visual; matriks `\begin{pmatrix} ... \end{pmatrix}` render inline (kecil & sempit) padahal layak display.
2. **Markdown mentah di field diketahui** — contoh `solutions[2].diketahui` = `"Berikut adalah ekstraksi data dari gambar: ### **KAPASITAS KAMAR HOTEL** | TIPE KAMAR | HOTEL A | ..."` — header markdown + tabel pipa ditampilkan sebagai TEKS POLOS (panel tidak merender markdown). Ini yang paling bikin pusing. Juga `solutions[10].diketahui` = `"### 1. Ekstraksi Data Grafik **Sumbu-X:** ..."` dan prompt-fase-4 jelas mendorong model memformat jawaban seperti itu — file `data/prompts/sejarah_paket_2_5pillar_prompt.txt` & prompt 5-pilar lain menuntut format yang kemudian bocor ke field.
3. Contoh owner verbatim (q8 MTL P2): `Kurva parabola $y = 2x^2 - 5$, translasi matriks $T = \begin{pmatrix} -3 \\ 2 \end{pmatrix}$, dilanjutkan dilatasi $[O, 2]$ dengan pusat $O(0, 0)$.` — secara LaTeX sudah valid (setelah fix ±atrix), tapi tampil padat karena semua elemen (parabola + matriks + dilatasi + pusat) dirempet satu paragraf.

**Arahan pengerjaan (usulan, silakan perbaiki jika ada cara lebih baik):**
- **Level data (utama):** tulis normalisasi khusus field `diketahui`/`langkah_penyelesaian` untuk MTL P2 (dan pola serupa di mapel lain): (a) pecah rumus-rumus berdempet `$...$ $...$` menjadi baris sendiri-sendiri; (b) ubah `\begin{pmatrix}...` inline yang panjang menjadi `$$\begin{pmatrix}...$$` (display math, center, lebih besar) — hati-hati di dalam kalimat pendek biarkan inline; (c) **buang/parsing markdown mentah**: `### Judul` → teks bersih (bold hilang, cukup teks), tabel pipa `| a | b |` → ubah menjadi kalimat terstruktur atau daftar multi-baris ("Tipe A: 20, Tipe B: 15, ...") — jangan biarkan karakter `|`, `#`, `**` tampil; (d) pecah kalimat terlalu panjang (>`150` char tanpa `.`) pada tanda hubung logis.
- **Level prompt (pencegahan permanen):** perbaiki template prompt 5-pilar di `pipeline/` (cari generator prompt fase 4 di swarm_manager/bridge) agar MENLARANG markdown (`###`, `**`, tabel pipa) pada field diketahui/ditanyakan dan mewajibkan: satu konsep = satu baris, matriks besar di baris sendiri, tanpa preamble "Berikut adalah ekstraksi data dari gambar".
- **Level CSS (opsional pendukung):** `style.css` — beri margin antar segmen math display di panel pembahasan (`.bs-latex`, `katex-display`), line-height nyaman.
- **Proses yang diwajibkan owner:** identifikasi dulu SEMUA kasus di SEMUA mapel (perluas `scratch/_audit_pilar_full.py` — sudah ada, pola 1–7 — dengan deteksi markdown mentah `^###|^\*\*|\|.*\|`), laporkan daftar file+nomor, baru perbaiki dengan script idempoten + backup ke `backup_render_fix_20260929_v2/`, lalu scan ulang sampai bersih, lalu VERIFIKASI lewat API (bandingkan output `/api/solution` vs file — ingat Pola Bug #7) dan spot-check visual di browser.
- Setelah selesai: tambahkan sebagai **Pola Bug #8** di `docs/BUG_FIX_PLAYBOOK.md`.

## 5. TUGAS TERBUKA #2 (SETELAH #1) — PERSIAPAN BULK-SCRAPE
- 21 paket belum di-scrape (`get_unscraped_subjects()`; kategori: Bahasa Asing, Bahasa Tingkat Lanjut, Kejuruan, Lintas Minat, dst).
- Resep final yang sudah TERVERIFIKASI: swarm fase 1–5 via `POST /api/swarm/start {"targets": [slug,...]}` (maks 2–3 paket per gelombang), Chrome debug 9222 harus hidup (`start_chrome_debug.bat`, login AI Studio tetap), setelah tiap gelombang jalankan: `python scratch/_fix_render_data_20260929.py` (cleaner segar) → `python _scan_render_garbage.py` (target: hanya 4 temuan legitim data_latex kimia) → cek jumlah solusi = jumlah soal per paket → cek `/api/solution` vs file → tambah backup.
- Kalau audit fase 5 gagal "Solusi hanya mencakup N/M soal" → cek dulu kontaminasi lintas-target (Pola Bug #6) sebelum regenerasi.

## 6. ATURAN KERJA (WAJIB)
1. Bahasa komunikasi: Indonesia santai (gua/lo).
2. Backup SEBELUM menulis file data apa pun (folder backup baru atau `backup_render_fix_20260929_v2`).
3. Perbaikan teks HANYA via `text_quality.py` / script idempoten — jangan bikin normalizer duplikat; JANGAN pernah regex sembari pada teks ber-LateX (ingat Pola Bug #7 — selalu batas huruf).
4. Encoding WAJIB `utf-8` di setiap baca/tulis (file di Windows, CRLF di server.py — hati-hati saat patch).
5. Scan + verifikasi API setelah setiap perubahan; `python -m py_compile` untuk .py, `node --check` untuk .js, naikkan `?v=` di `index.html` setelah edit `app.js`.
6. Jangan commit git; jangan jalankan tutor API (kuota); jangan hapus folder backup.
7. Endpoint penting: `GET /api/swarm/subjects`, `GET /api/swarm/status`, `POST /api/swarm/start`, `POST /api/solution {subject, paket, nomor}`, `POST /api/ai-tutor`. Server port 8080 (owner jalankan sendiri; minta restart setelah perubahan server.py).
8. File sementara taruh di `scratch/`; laporan audit taruh di `scratch/`.

## 7. KONDISI AKHIR SAAT HANDOFF (29 Sep 2026 malam)
- Scan penuh bersih: hanya 4 temuan legitim (data_latex kimia). MTL P1 & Sejarah P2 lolos audit 100% (resep final terbukti).
- `app.js?v=28`, bridge anti-kontaminasi, `server.py` anti-±atrix — semua compile OK dan terbukti via API.
- Satu-satunya keluhan aktif owner: keterbacaan pilar 1 MTL P2 (Tugas #1) + bulk-scrape 21 paket tersisa (Tugas #2).

Mulai dari Tugas #1. Selesaikan, laporkan, lanjut Tugas #2. Semangat, Gemini — owner ngejar deadline. 🚀
