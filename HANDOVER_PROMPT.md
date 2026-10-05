# HANDOVER PROMPT — Penggantian AutoClaw (GLM) untuk Project SCRAPE_TKA

> Kamu mengambil alih peran AI asisten utama untuk project **SCRAPE_TKA**
> (root: `D:\PROJECTS\SCRAPE_TKA`). Baca seluruh dokumen ini sebelum bekerja.
> Semua konteks, kebiasaan user, status pekerjaan, kontrak data, dan jebakan
> teknis ada di sini. Jangan ulangi kesalahan yang tercatat di §9.

---

## 1. KONTEKS PROJECT & USER

- Project: **TKA Master** — platform latihan soal TKA Pusmendik Indonesia
  (CBT: soal → jawab → pembahasan → AI Tutor). Sudah JALAN dan dipakai orang.
- Bahasa kerja: **Indonesia santai** (user pakai "lu/gue"). Jawab singkat,
  langsung ke poin, tanpa basa-basi. User benci jawaban bertele-tele.
- **Prinsip #1 user: JANGAN NIPU.** Semua angka yang tampil di UI harus data
  nyata dari project (jumlah soal, progres user, kuota). DILARANG menampilkan
  angka karangan ala AI (contoh terlarang: "Skor 92", "Akurasi 62%",
  "84/100 kuota", "Rian Pratama Kelas 12"). Kalau data belum ada, tampilkan
  keadaan kosong yang jujur.
- User ingin cepat & simpel: kalau ada 2 cara, pilih yang simpel.
- User sedang memakai strategi multi-AI paralel (Stitch untuk desain, Zcode/
  GLM untuk halaman Modul, Antigravity/Gemini untuk halaman Progres, dan kamu
  sebagai integrator + pengerja bagian yang tidak dikerjakan mereka).

---

## 2. LINGKUNGAN (PENTING — ada jebakan)

- Windows 11, shell **PowerShell 5.1**. Backslash = pemisah path.
- Python: versi embedded di PATH **mengabaikan PYTHONPATH** dan tidak bisa
  import module di folder project. Solusi resmi: launcher
  `scratch/_run_server.py` (menambahkan root ke sys.path lalu menjalankan
  server.py). Menjalankan server:
  ```
  $env:PORT='8080'; python scratch\_run_server.py        # server utama
  $env:PORT='8081'; $env:PUBLIC_DEMO='1'; python scratch\_run_server.py   # server demo publik
  ```
  Alternatif user: dobel-klik `start_server.bat` / `bagikan_online.bat`.
- **JANGAN menjalankan dua server di port yang sama** — Windows mengizinkan
  dua proses bind port sama, request masuk acak ke salah satu, dan ini pernah
  bikin bug misterius (log_visitor campur, kode lama/baru acak). Sebelum
  menyalakan server, cek: `netstat -ano | Select-String ':8080' | Select-String 'LISTENING'`
  dan bunuh proses lama: `taskkill /PID <pid> /F`.
- Node.js 24 + `playwright-core` terpasang di `scratch/` (node_modules di
  scratch), Chromium headless terpasang. Skrip tes ada di `scratch/`.
- Quote PowerShell mudah bentrok dengan python -c "..." → tulis script ke
  file `scratch/_x.py` lalu `python scratch\_x.py`.
- Server menyajikan HTML/JS/CSS/JSON dengan `Cache-Control: no-store`, jadi
  perubahan langsung terlihat; tetap sarankan user Ctrl+Shift+R.

---

## 3. PETA FILE PENTING

### App utama (JANGAN dirusak; backup sebelum edit besar)
- `server.py` — server HTTP (port 8080 utama; 8081 = mode demo publik
  PUBLIC_DEMO=1, mematikan endpoint admin; route `/` = landing, `/app` = app,
  `/pengunjung` = dashboard pengunjung butuh `?key=tka-admin`).
- `index.html` — halaman app (soal CBT + AI Tutor + Home overlay).
- `app.js` — logika app. Berisi `SUBJECT_CATALOG` (22 mapel), `switchSubject`,
  `switchPackage`, `renderQuestion`, serta blok HOME (homeOpen/homeClose/
  renderHome/homePrefetchCounts/homePkgCount/homePkgProgress/
  homeProgressSummary/homeSendDesktopData + listener postMessage).
- `style.css` — semua CSS app + Home overlay mobile (class `.stitch-*`).
- `landing.html` — landing page (desain Stitch mobile-first, Tailwind CDN +
  GSAP + Lenis + Plus Jakarta Sans; backup lama di
  `backup_audit_fix_20261003/landing_old.html`).
- `tutor_engine.py`, `tutor_llm.py`, `tutor_store.py` — AI Tutor (jangan
  diubah tanpa perlu; kuota tamu 5/hari, reset 00.00 WIB).
- `visitor_log.py` + `data/visitors_<PORT>.jsonl` — pencatat pengunjung.

### Home (karya terakhir — LIHAT §7 STATUS)
- `home_stitch.html` — TIDAK terpakai lagi untuk mobile (versi awal iframe
  eksperimen). Mobile memakai markup inline `.stitch-*` di `index.html` +
  `home_stitch.css`. Boleh dihapus atau diabaikan.
- `home_stitch.css` — CSS Home overlay (mobile + media query untuk iframe
  desktop ≥900px). `?v=` belum dinaikkan — naikkan saat mengubah.
- `home_desktop.html` — **SAAT INI CORRUPT (19.980 bytes)**. Detail perbaikan
  di §7. Sumber kebenaran untuk rebuild: `scratch/_desk_head.html` (4.620),
  `scratch/_desk_body.html` (36.910 — body lengkap utuh),
  `scratch/_desk_bridge.js` (bridge + renderProgress terbaru).
- `home_stitch_source.html` — kode Stitch mobile asli (referensi).
- `scratch/_stitch_desktop_raw.html` — kode Stitch desktop asli (referensi).

### Hasil AI paralel (sudah diverifikasi bersih, siap integrasi)
- `workspace_modul/modul.html` — halaman Modul (wrapper `#modulDesktop` /
  `#modulMobile`, media query 900px, postMessage open-package ✓).
- `workspace_progres/progres.html` — halaman Progres (wrapper
  `#progresDesktop` / `#progresMobile`; angka karangan "84/100" sudah
  diganti "Kuota AI Tamu: 5/hari" & "AI: 5/hari").

### Dokumen kontrak (beri ke AI mana pun)
- `ATURAN_AI.md` — aturan wilayah file + disiplin teknis + kontrak postMessage.
- `KONTRAK_DATA.md` — tabel 22 mapel + jumlah soal REAL + format localStorage.
- `PROMPT_ZCODE_MODUL.md`, `PROMPT_ANTIGRAVITY_PROGRES.md` — prompt yang
  dipakai user.
- `BRIEF_AUTOCLAW_BERANDA_DESKTOP.md` — brief tugasmu (desktop Beranda).

### Backup & arsip
- `backup_audit_fix_20261003/` — backup JSON data, app.js, style.css,
  index.html, landing_old.html, index_home_overlay_backup.html.
- `arsip_screenshot_lama/` — 40 screenshot debug lama (jangan dihapus).

---

## 4. DATA REAL (sumber kebenaran)

22 mapel, 44 paket, **961 soal**. key | nama | P1 | P2:
matematika | Matematika (Wajib) | 46 | 25 ·
bahasa_indonesia | Bahasa Indonesia (Wajib) | 20 | 25 ·
bahasa_inggris | Bahasa Inggris (Wajib) | 20 | 25 ·
fisika | Fisika (Peminatan) | 20 | 24 ·
kimia | Kimia (Peminatan) | 20 | 24 ·
biologi | Biologi (Peminatan) | 20 | 29 ·
ekonomi | Ekonomi | 20 | 29 ·
geografi | Geografi | 10 | 29 ·
sosiologi | Sosiologi | 20 | 30 ·
sejarah | Sejarah | 10 | 29 ·
antropologi | Antropologi | 10 | 30 ·
kewirausahaan | Kewirausahaan (PKWU) | 10 | 30 ·
matematika_lanjut | Matematika Lanjut | 20 | 25 ·
bahasa_indonesia_lanjut | B. Indonesia Lanjut | 10 | 29 ·
bahasa_inggris_lanjut | B. Inggris Lanjut | 10 | 29 ·
ppkn | PPKn | 20 | 29 ·
bahasa_arab | Bahasa Arab | 10 | 29 ·
bahasa_jepang | Bahasa Jepang | 10 | 29 ·
bahasa_jerman | Bahasa Jerman | 10 | 29 ·
bahasa_prancis | Bahasa Prancis | 10 | 29 ·
bahasa_mandarin | Bahasa Mandarin | 10 | 29 ·
bahasa_korea | Bahasa Korea | 10 | 29

Estimasi durasi: ±1 menit/soal (Paket 1 MTK = ±45 menit).
Kategori: WAJIB = matematika, bahasa_indonesia, bahasa_inggris ·
SAINTEK = fisika, kimia, biologi · SOSHUM = ekonomi, geografi, sosiologi,
sejarah, antropologi, kewirausahaan · LANJUT = matematika_lanjut,
bahasa_indonesia_lanjut, bahasa_inggris_lanjut · BAHASA/LINTAS = ppkn,
bahasa_arab, bahasa_jepang, bahasa_jerman, bahasa_prancis, bahasa_mandarin,
bahasa_korea.

**Format progres localStorage** (kunci `tka_progress`):
`tka_progress[subjectKey][pkgNumber][nomorSoal] = { kunci:"B", benar:true }`
Dibaca oleh `homePkgProgress` & `homeProgressSummary` di app.js dan harus
dibaca juga oleh progres.html. **PERHATIAN: app BELUM menulis ke kunci ini**
saat user menjawab soal (jawaban masih di memori, `state.userAnswers`).
Salah satu tugas backwards: tulis ke `tka_progress` setiap jawaban tercatat
(cari `selectOption` / tempat `state.userAnswers[key][nomor]` di-set di
app.js), lalu panggil ulang render ringkasan.

**Design tokens Stitch (wajib untuk semua halaman baru):**
primary #004a2a · primary-container #1b633e · accent-mint #22C55E ·
tertiary-fixed #ffdcc3 · tertiary #643300 · surface #f6fafe ·
surface-card #FFFFFF · border-subtle #E2E8F0 · text #0F172A ·
text-muted #64748B · secondary #56615c. Font 'Plus Jakarta Sans' (400–800),
ikon 'Material Symbols Outlined', radius 12–20px, light mode, shadow lembut.

---

## 5. ARSITEKTUR SAAT INI (alur user)

1. `/` = landing.html (desain Stitch, sudah oke, jangan diutak-atik).
2. Klik "Mulai latihan" → `/app` → **Home overlay** muncul pertama
   (kecuali URL punya hash `#soal-N`).
   - **Mobile (<900px):** markup `.stitch-*` inline di index.html + CSS di
     home_stitch.css. Kartu dirender `renderHome()` dari app.js.
   - **Desktop (≥900px):** `<iframe id="homeDesktopFrame"
     src="/home_desktop.html">` fullscreen; versi mobile disembunyikan via
     media query di home_stitch.css.
3. Klik kartu paket (di mobile atau di iframe desktop) → postMessage
   `{type:'open-package', subject, pkg}` → app.js listener → homeClose() →
   switchSubject + switchPackage → soal tampil.
4. Tombol rumah di header app (`#btnHome`, `homeToggle()`) membuka Home lagi.
5. Data dikirim ke iframe desktop via `homeSendDesktopData()`:
   `{type:'home-desktop-data', subjects:[{subject,pkg,label,count,minutes,
   progress}×6], progress:{dikerjakan,benar,tepat}}` — dikirim ulang 5×
   (interval 400ms) untuk keandalan, setelah event load iframe.
6. Bottom nav di Home desktop mengirim `{type:'nav', path:'...'}`.

---

## 6. KONTRAK POSTMESSAGE (jangan diubah sembarangan)

- iframe → parent: `{type:'open-package', subject:'<key>', pkg:1|2}`
- iframe → parent: `{type:'nav', path:'Beranda'|'Modul'|'Progres'|'Akun'}`
- iframe → parent: `{type:'home-desktop-ready'}`
- parent → iframe: `{type:'home-desktop-data', subjects:[...], progress:{...}}`
- parent → iframe (halaman progres, belum aktif):
  `{type:'progress-data', ...}` dan halaman boleh minta dengan
  `{type:'request-data'}`.

---

## 7. STATUS PEKERJAAN — BACA BAGIAN INI TELITI

### ✅ Selesai & teruji (semua tes PASS)
- Landing baru (Stitch) di `landing.html`; konten lama dipertahankan
  (harga Rp20.000, kuota tamu 5/hari, FAQ asli, disclaimer).
- Home mobile (`.stitch-*` inline) + 44 kartu paket + filter; 7/7 tes PASS
  (`scratch/_tes_home.js`).
- Data real per mapel di kartu (bug "Fisika 46 soal" sudah diperbaiki —
  `homePkgCount` kini per-mapel via HOME_SOAL_COUNTS prefetch).
- Popup feedback ke pojok kanan bawah; tab Paket pindah ke kanan header.
- Bersih-bersih: 1.922 field wrapper Pusmendik di 44 JSON (scratch/
  _clean_pusmendik_wrappers.py); validator gambar inline tidak lagi
  mendemosi simbol kecil; screenshot lama diarsipkan.
- `workspace_modul/modul.html` & `workspace_progres/progres.html` sudah
  diverifikasi struktural (wrapper responsive + postMessage benar).

### 🔴 IN-PROGRESS / RUSAK — tugas pertamamu
`home_desktop.html` **corrupt** (19.980 bytes; harusnya ±47.000). Penyebab:
regex pembersih "angka karangan" (scratch/_fix_desktop3.py) melahap blok
besar body (3 section MATA PELAJARAN + aside hilang). JANGAN pakai file itu
sebagai dasar. Cara memperbaiki:

1. Rebuild dari sumber utuh:
   - head: `scratch/_desk_head.html` (sudah bersih dari inline style
     `width:1280px;overflow:hidden` — JANGAN kembalikan style itu; itu
     penyebab iframe tidak bisa scroll)
   - body: `scratch/_desk_body.html` (utuh 36.910 bytes, ada 3 section
     MATA PELAJARAN + aside)
   - bridge: `scratch/_desk_bridge.js` (sudah termasuk renderProgress)
   - susun: head + body + `<script>` bridge `</script>` + `</body></html>`
2. Setelah rebuild, terapkan penggantian angka karangan dengan **replace
   string EXACT** (sudah diverifikasi ada di `scratch/_desk_body.html`;
   JANGAN pakai regex dengan `[\s\S]` — itu yang bikin corrupt):
   - `<span class="font-headline-xl text-headline-xl text-primary font-extrabold">92</span>`
     → beri `id="deskSoalDikerjakan"` dan angka 0 (diisi bridge).
   - `Skor Komposit` → `Soal Dikerjakan`; `/100` (span setelah 92) → hapus;
     `Kategori Tinggi` → `Soal Benar`; `Persentil: 96.8%` →
     `Ketepatan: —` (diisi bridge); `Penalaran Matematika Lanjut` →
     `Jawaban Benar`; `95%` → `—`; `Literasi Sains Terapan` →
     `Jawaban Salah`; `89%` → `—`; `Target: STEI-R ITB` →
     `Dari 961 soal TKA`; `Peluang Lolos 88%` → hapus.
   - `Hasil Diagnostik Terakhir` → `Progres Belajarmu`;
     `Terverifikasi AI` → `Diperbarui otomatis`.
   - `Akun Pro (Masa Beta)` → `Mode Tamu (Beta)`; `Aktif s/d Mei 2025` →
     `Gratis selama beta`; `84/100 Kuota AI Hari Ini` → `Kuota AI Tamu`;
     `Tersisa 84 pertanyaan` → `5 pertanyaan per hari`.
   - `Rian Pratama` → `Tamu`; `Kelas 12 SMA • Saintek` → `Tanpa login · Beta`.
   - Widget `Rata-rata Durasi Belajar` (+ chart Sen–Min + `Target tercapai
     4 dari 7 hari` + `57%`) → ganti seluruh widget dengan kartu teks jujur:
     "±45 menit untuk 46 soal — disarankan 1 paket per hari." (replace string
     yang diawali komentar `<!-- Daily Study Tracker Widget` sampai sebelum
     kartu `Pusat Bantuan TKA` — potong dengan INDEX string, bukan regex rakus.)
   - Card: `60% (12/20 Selesai)` / `40% (8/20 Selesai)` / `30% (6/20 Selesai)`
     → `data-progress-pct` span kosong (diisi bridge dengan angka nyata);
     `Lihat Semua (8 Paket)` → `Lihat Semua`; `>Terjadwal<` → `>Tersedia<`;
     `>Populer<` → `>Tersedia<`;
     `Mekanika Kuantum, Termodinamika &amp; Elektromagnetik` →
     `Mekanika, Termo &amp; Listrik — soal resmi Pusmendik`;
     `Mikro-Makro Ekonomi, Kebijakan Fiskal &amp; Dinamika Pasar` →
     `Mikro-Makro &amp; Pasar — soal resmi Pusmendik`;
     teks `20 Soal HOTS` / `26 Soal HOTS` / `20 Soal Analitis` →
     span ber-ID (diisi bridge: count + menit real).
3. Bridge di `scratch/_desk_bridge.js` SUDAH benar: memetakan 6 kartu
   (urutan section Stitch: MTK, Fisika, Ekonomi — masing-masing Paket 1,2),
   mengisi chip/soal/menit/progres/ribbon "Baru" (sembunyi jika progres >0),
   renderProgress mengisi `deskSoalDikerjakan`, Ketepatan, Benar.
4. Rebuild → jalankan `node scratch\_tes_desktop.js` (tes file langsung) dan
   `node scratch\_tes_desktop_live.js` (tes via server; semua harus PASS:
   overlay tampil, iframe display block, card terisi "46 Soal" dst, klik
   card → overlay tutup + "Soal Nomor 1 dari 46"). Juga
   `node scratch\_tes_desktop_scroll.js` (iframe bisa discroll; inline style
   harus "(tidak ada)"). Lalu `node scratch\_tes_home.js` (mobile 7/7).
5. Screenshot verifikasi: viewport 1280×860 ke
   `http://127.0.0.1:8080/app?subject=matematika&paket=1`, tunggu 5 detik
   (prefetch angka), simpan ke `exports/`.

### 📋 Backlog setelah desktop beres (urutan prioritas)
1. **Persist progres nyata**: saat user menjawab soal (cari titik
   `state.userAnswers` diisi di app.js), tulis juga ke localStorage
   `tka_progress[subject][pkg][nomor] = {kunci, benar}` (kunci = kunci
   resmi soal, benar = jawaban user == kunci). Tanpa ini kartu progres &
   halaman Progres selalu 0%.
2. **Integrasi panel Modul & Progres**: pasang `workspace_modul/modul.html`
   dan `workspace_progres/progres.html` sebagai panel/iframe di app,
   sambungkan bottom nav Home desktop (`{type:'nav'}`) + nav mobile agar
   Beranda/Modul/Progres berganti panel. Kirim `progress-data` ke halaman
   progres saat dibuka. Naikkan `?v=` cache CSS yang berubah.
3. Verifikasi konten modul.html & progres.html terhadap KONTRAK_DATA.md
   (jumlah soal & nama mapel persis; progres.html "84/100" sudah dibersihkan
   sebagian — cek ulang tidak ada sisa).
4. Bottom nav item "Akun" → sembunyikan atau arahkan ke halaman FAQ/CTA;
   jangan tampilkan tombol yang tidak punya halaman.
5. Opsional: endpoint ringkasan di server.py (satu request untuk semua
   jumlah soal) agar Home tidak fetch 44 JSON saat pertama dibuka.
6. Setelah semuanya stabil: bump semua `?v=` (style.css v47→v48,
   home_stitch.css v1→v2), minta user hard-refresh, lalu user akan audit
   manual per mapel/paket seperti biasa (pola laporannya: nomor soal yang
   aneh, scroll kejauhan, gambar salah ukuran — pola fix-nya sudah ada di
   app.js formatPusmendikHtml & validator).

---

## 8. CARA KERJA YANG DIHARAPKAN USER

- Singkat, santai, jujur. Kalau ada bug, akui + tunjukkan penyebab + fix.
- Sebelum edit besar: **backup dulu** ke folder `backup_audit_fix_20261003/`
  (pattern yang sudah berjalan).
- Setelah edit: verifikasi nyata (tes Playwright di scratch/ + screenshot ke
  `exports/`), jangan cuma klaim. Tapi jangan berlebihan — user tidak suka
  proses bertele-tele di chat; ringkas saja hasilnya.
- Kalau user paste kode Stitch baru: taruh sesuai halaman (modul/progres/
  beranda), selalu sinkron dengan KONTRAK_DATA.md dan bersihkan angka fiktif.
- Deliver file dengan deliver_file bila ada file jadi yang perlu dikirim.

## 9. JANGAN LAKUKAN (kesalahan yang sudah pernah terjadi)

1. Regex dengan `[\s\S]{0,N}` untuk "membersihkan" HTML → melahap konten
   besar (penyebab home_desktop corrupt). Pakai replace string exact/index.
2. Dua server di port sama → gejala tidak konsisten. Selalu cek netstat.
3. `python -c "..."` dengan banyak quote → tulis file .py di scratch/.
4. Mengarang angka UI (prinsip user).
5. Mengedit file inti saat masih eksperimen → kerjakan di scratch/, backup,
   baru terapkan.
6. Menjalankan server tanpa cek port → tabrakan server lama/baru.
7. Lupa bahwa python embedded butuh `scratch/_run_server.py` (PYTHONPATH
   tidak berfungsi).

## 10. SARANA TES CEPAT

```
# server (jika belum jalan)
$env:PORT='8080'; python scratch\_run_server.py

# tes (dari root): 
node scratch\_tes_home.js          # mobile home 7/7 PASS
node scratch\_tes_desktop_live.js  # desktop via server 4/4 PASS
node scratch\_tes_desktop.js       # bridge file langsung
node scratch\_tes_desktop_scroll.js# iframe scrollable + inline style hilang
```

Semua tes harus PASS sebelum menyatakan selesai. Lapor hasilnya apa adanya.

---

## 11. KATA PERTAMA KE USER

Mulai dengan konfirmasi singkat bahwa kamu sudah membaca handover ini, lalu
langsung kerjakan tugas #7 (perbaikan home_desktop.html) dan laporkan hasil
tesnya. User akan mengirim kode/feedback tambahan setelahnya.
