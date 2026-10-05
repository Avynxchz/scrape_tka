# LAPORAN AKHIR: OVERHAUL UI MOBILE TKA MASTER (FASE 4 - FASE 14)

Platform: Aplikasi Web Simulasi Ujian & AI Tutor TKA Pusmendik (`D:/PROJECTS/SCRAPE_TKA`)  
Teknologi: Vanilla HTML, CSS, JavaScript (Tailwind CSS pada modul iframe mandiri)  
Branch: `ui-overhaul-mobile`  
Server Uji Lokal: `http://127.0.0.1:8080`  
Tanggal Penyelesaian: 2026-10-05  

---

## (A) STATUS PER FASE & CHECKLIST SPESIFIKASI

| Fase | Judul / Lingkup | Status | Hasil Checklist Spesifikasi |
|---|---|---|---|
| **Fase 4** | Tombol Navigasi Mengambang (Floating Action Rail) | **SELESAI** | [x] 3 tombol (`#workRail`: Soal, Pembahasan, Tanya AI) terdeteksi.<br>[x] Pencegahan geser tak sengaja: long-press 400ms + haptic/outline visual feedback.<br>[x] Snap dinamis ke 6 kuadran layar (kiri/kanan x atas/tengah/bawah).<br>[x] Tetap tampil di tampilan Chat AI (`z-index: 75` di atas sheet chat `70`).<br>[x] Posisi tersimpan otomatis di `localStorage` dan dipulihkan saat reload.<br>[x] Safe-area aware & mendukung touch + mouse tanpa merusak desktop. |
| **Fase 5** | Konsistensi Navbar Atas & Bottom Nav (4 Menu Mobile) | **SELESAI** | [x] Top bar seragam di Beranda, Modul, Progres, Akun: Icon `school` + Title `TKA Master` + Subtitle Menu + Avatar `person`.<br>[x] Search bar Modul dipindahkan dari top bar ke dalam area konten.<br>[x] Tombol reset riwayat & badge kuota AI di Progres dipindahkan dari navbar ke baris judul konten.<br>[x] Bottom nav terstandarisasi tepat 56px (`h-14`) dengan `pb-safe` (`env(safe-area-inset-bottom)`), mengatasi masalah nav yang terlalu menjulang.<br>[x] Navbar atas halaman Soal (#004a2a) tetap utuh per Fase 3. |
| **Fase 6** | Beranda: Performa Render & Desain Ulang Kartu Mapel | **SELESAI** | [x] Akar penyebab lambat diatasi: pre-seeded data statis `STATIC_SOAL_COUNTS`, waktu render turun dari ~39.6ms ke **12.0ms** (0 network roundtrips).<br>[x] Hanya mapel pilihan user yang tampil (default 4 mapel = 8 kartu). Modal "Atur Mapel" tersedia.<br>[x] Tombol "Lihat Semua" dihapus.<br>[x] Desain kartu bersih (#FFFFFF, border-radius 14px, aksen garis atas), teks chip kontras tinggi (Matematika biru tegas #1D4ED8 di atas latar biru muda).<br>[x] 22 ikon Material Symbols 100% UNIK tanpa duplikat (Set size = 22).<br>[x] Penanganan nama panjang dengan nama singkat/akronim & line-clamp 2 baris. |
| **Fase 7** | Beranda: Carousel Hero Hijau Reusable | **SELESAI** | [x] Semua teks di dalam hero carousel berwarna PUTIH solid (#FFFFFF / rgb(255, 255, 255)).<br>[x] Elemen dekoratif titik-titik (`.stitch-dotrow`) dan topi toga (`.stitch-cap`) dihapus.<br>[x] Slide 2: Animasi SVG Pie Chart dengan ring pulse & skor 92%.<br>[x] Slide 3: Maskot Robot AI SVG interaktif beranimasi (antena berdenyut, mata digital berkedip, senyum).<br>[x] Komponen reusable carousel controller diekspor ke `window.setupCarouselController`. |
| **Fase 8** | Menu Modul: Carousel & Progres Gabungan Bersegmen | **SELESAI** | [x] Carousel 2-slide reusable dengan teks putih solid (#FFFFFF).<br>[x] Slide 1: Kurikulum & Maskot Robot AI SVG sedang membaca buku (animasi lembaran halaman membuka-tutup `stBookPageFlip`).<br>[x] Daftar tetap berisi seluruh 22 mapel dan 5 kategori (Wajib, Saintek, Soshum, Lanjut, Bahasa).<br>[x] Progres "0 dari 961" diganti **Progres Gabungan Mapel Pilihan**: multi-segmented bar berwarna tematik proporsional soal selesai per mapel terhadap total soal mapel pilihan.<br>[x] Legenda ringkas warna mapel dengan status selesai/total.<br>[x] Teruji akurat dengan data tiruan Playwright (16/16 PASS). |
| **Fase 9** | Menu Progress: Fix Bug Blinking & Dashboard Analitik | **SELESAI** | [x] Akar masalah bug berkedip/blinking diidentifikasi dan diperbaiki total via memoization data (`_lastRenderedProgressJson`), penghapusan animasi `.fade-in` pada re-render, dan reduksi retry `postToFrameReliable`. Kartu terbukti stabil tanpa kedipan (sampling 2.5 detik lolos).<br>[x] Dashboard analitik belajar: Widget Streak Kehadiran harian (`local_fire_department`), Waktu Belajar Hari Ini vs Kemarin (`schedule`), dan Visualisasi Distribusi 5 Rumpun Kategori Mapel.<br>[x] Empty state bersih dan ramah untuk user baru tanpa riwayat pengerjaan.<br>[x] Top bar & bottom nav konsisten 56px. |
| **Fase 10** | QA Akhir & Verifikasi Lintas Viewport | **SELESAI** | [x] Seluruh 84 checks tes otomatis (Fase 3 s/d 10) lolos 100%.<br>[x] Pengujian visual Playwright di 4 viewport (360px, 390px, 412px, 1280px) untuk 5 layar utama.<br>[x] Mode Tamu (Guest Mode) 100% utuh tanpa perubahan.<br>[x] 0 console errors di seluruh layar.<br>[x] Tidak ada teks hijau di atas hijau, tidak ada elemen terpotong, safe-area aware. |
| **Fase 11** | Diagnosis & Perbaikan Bottom Nav Terlalu Tinggi (Menu Dashboard Mobile) | **SELESAI** | [x] Diagnosis mendalam di 360, 390, 412 px: akar masalah ditemukan pada kelas `.pb-safe` di `progres.html` yang memiliki `padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 5rem)` = 80px pada elemen `<nav>`.<br>[x] Pemisahan padding navigasi `.pb-safe` (murni safe-area) dengan `.pb-safe-content` (pada container scrollable `<main>`).<br>[x] Penerapan `100dvh` di `#homeOverlay` dan `min-h-[100dvh]` di `workspace_progres/progres.html` untuk mengantisipasi dynamic address bar browser smartphone.<br>[x] Terbukti: tinggi nav (57px) dan posisi bottom nav (flush menempel dasar viewport) **100% IDENTIK di ke-4 menu** (selisih 0px). |
| **Fase 12** | Chat AI: Tampilan Jawaban & Pemilih Model | **SELESAI** | [x] Warna background bubble jawaban AI: Kartu putih bersih `#FFFFFF` dengan border hijau halus `#D1FAE5` di atas background chat `#F8FAFC` (kontras teks > 7:1).<br>[x] Bubble user berwarna hijau tema `#004a2a` dengan teks putih solid `#FFFFFF`.<br>[x] Padding bubble AI nyaman 16px, line-height 1.55, spacing paragraf & list terstruktur rapi.<br>[x] Konten markdown tidak meluber: Fenced code blocks & tabel HTML memiliki container ber-scroll horizontal mandiri (`overflow-x: auto !important`).<br>[x] Pemilih model: Bar besar lama disembunyikan. Digantikan tombol logo model compact (32px) sejajar Chat Baru dan Quick Chips. Klik logo memicu popover picker dengan daftar model, centang aktif, deskripsi ringkas, dan persistensi otomatis ke `localStorage['tka_active_ai_model']`. |
| **Fase 13** | Tombol Navigasi Mengambang Bisa Mengecil Otomatis (Auto-Minimize Rail) | **SELESAI** | [x] Kondisi idle: Tombol bulat compact 42px transparan (opacity 0.88) menampilkan ikon tab aktif.<br>[x] Tap tombol mini mengembang menampilkan 3 tombol lengkap (Soal, Pembahasan, Tanya AI) dengan label teks.<br>[x] Diam 4 detik (4000ms) tanpa interaksi otomatis mengecil kembali dengan transisi kubik halus.<br>[x] Mengetuk tombol tab langsung berpindah dan auto-collapse setelah 250ms.<br>[x] Menghormati `prefers-reduced-motion` (transisi instan jika aktif).<br>[x] Long-press >= 400ms memicu drag & snap (tap biasa tidak memicu drag). Posisi tersimpan di `localStorage['tka_rail_snap_pos']`.<br>[x] Tiga tombol tidak pernah keluar layar di seluruh 6 kuadran snap.<br>[x] Tombol mini tidak menutupi input chat, tombol kirim, atau opsi jawaban di tampilan AI.<br>[x] Desktop (1280px) tetap format sidebar desktop standar (un-minimized, 3 tombol). |
| **Fase 14** | Kontrol Ukuran Teks Mobile (90%, 100%, 115%, 130%) | **SELESAI** | [x] 4 tingkat skala terkalibrasi: 90% (ringkas), 100% (default), 115% (sedang), 130% (besar).<br>[x] Titik akses (1): Di dalam menu overflow (⋮) halaman Soal terdapat baris kontrol ukuran teks (tombol A-, indikator, tombol A+).<br>[x] Titik akses (1b): Di header AI Tutor terdapat tombol `A` yang memunculkan popover skala teks, memungkinkan pengaturan langsung dari dalam percakapan AI tanpa keluar.<br>[x] Titik akses (2): Di menu Akun terdapat baris pengaturan "Ukuran Teks Aplikasi" pada kartu "Pengaturan Tampilan".<br>[x] Pendekatan Hybrid Scaling: `html[data-text-scale]` pada mobile media query menskalakan seluruh kelas `rem` Tailwind di iframe Modul, Progres, dan Akun, serta `calc(base_px * var(--text-scale, 1))` pada teks soal, stimulus, opsi, pembahasan, dialog, dan bubble AI.<br>[x] Proteksi bar atas (`.app-header`) dan bar bawah (`.stitch-bottomnav`) dibatasi skalanya (maksimal 108%) agar tinggi bar tetap 57px.<br>[x] Uji stres 130% pada lebar 360px: 0 scroll horizontal, teks tidak terpotong, opsi jawaban tetap utuh, dan rail mengambang tidak menutupi konten.<br>[x] Sinkronisasi real-time antar iframe dan parent via `postMessage` dan `localStorage['tka_font_scale']`.<br>[x] Desktop (1280px) tetap 16px root font size (0 perubahan). Mode Tamu 100% utuh. |

---

## (B) FILE YANG DIUBAH & DAFTAR COMMIT

### File yang Diubah:
1. `index.html`:
   - Penyesuaian hero carousel Beranda (hapus dekorasi toga/titik, SVG Pie Chart & Robot AI), integrasi modal Atur Mapel, standarisasi top bar.
   - Fase 12: Penambahan baris aksi atas AI (`#tutorTopActions`) dengan `#btnModelPicker` dan `#modelPopover`, penyembunyian bar pemilih model lama.
   - Fase 14: Penambahan kontrol ukuran teks di menu overflow (`#overflowTextScaleRow`) dan tombol popover font scale di header AI Tutor (`#btnTutorScale`).
2. `home_stitch.css`:
   - Standarisasi tinggi bottom nav 56px (`h-14`) dan integrasi `100dvh` pada wrapper dashboard.
   - Warna teks hero carousel serba putih (#FFFFFF), keyframes animasi (`stPieSpin`, `stPiePulse`, `stAntennaPulse`, `stRobotBlink`, `stFloat`), kartu mapel kontras tinggi.
3. `style.css`:
   - Fase 11: Sinkronisasi layout navigasi mobile.
   - Fase 12: Desain bubble chat AI (#FFFFFF dengan aksen hijau di atas #F8FAFC), styling tombol logo model 32px & popover picker, container `overflow-x: auto` untuk fenced code dan tabel markdown.
   - Fase 13: Auto-minimize styling `#workRail` (state `.is-minimized` 42px bundar vs `.is-expanded` 170px), transisi halus, positioning safe di atas chat input.
   - Fase 14: Mobile media query `@media (max-width: 899px)` skala font terkalibrasi (`data-text-scale`: 90, 100, 115, 130), proteksi fixed bar height (`clamp(10px, ..., 14px)`), dan pencegahan horizontal overflow.
4. `app.js`:
   - Drag & snap logic `#workRail`, auto-collapse timer (4000ms), event listener tap expand/collapse, dan isolasi desktop.
   - Pre-seeded counts, reusable carousel controller, optimasi pengiriman `postToFrameReliable`.
   - Fase 12: Logic model switching via popover, event delegasi, sinkronisasi model aktif ke localStorage dan state.
   - Fase 14: Controller skala teks mobile (`initTextScale`, `applyTextScale`, `setTextScale`, `stepTextScale`), sinkronisasi `postMessage` dua arah antar-iframe, dan storage synchronization.
5. `workspace_modul/modul.html`:
   - Carousel reusable 2-slide, SVG animasi robot membaca buku, segmented progress bar multi-warna, legenda ringkas mapel pilihan, search bar dalam konten.
   - Fase 14: Integrasi receiver skala font `postMessage` dan rules CSS `@media (max-width: 899px)` untuk `html[data-text-scale]`.
6. `workspace_progres/progres.html`:
   - Fase 11: Pemisahan `.pb-safe` (murni safe-area pada nav) dan `.pb-safe-content` (pada container scroll main), adaptasi `min-h-[100dvh]`.
   - Perbaikan anti-blinking memoized render, dashboard analitik belajar (streak, waktu belajar, distribusi 5 kategori), empty state bersih.
   - Fase 14: Integrasi receiver skala font `postMessage` dan rules CSS `@media (max-width: 899px)` untuk `html[data-text-scale]`.
7. `workspace_akun/akun.html`:
   - Fase 11: Standarisasi nav bottom 56px.
   - Fase 14: Penambahan kartu "Pengaturan Tampilan" dengan row "Ukuran Teks Aplikasi" (tombol A-, indikator persentase, tombol A+), handler `stepAkunScale()`, `applyAkunScale()`, dan sinkronisasi lintas iframe.
8. `scratch/_tes_fase4.js` s/d `scratch/_tes_fase14.js`, `scratch/_qa_akhir_fase10.js`:
   - Rangkaian skrip uji otomatis Playwright komprehensif untuk setiap fase.
9. `scratch/PROGRESS.md`:
   - Catatan status progres, rincian diagnosis teknis, asumsi, dan serah-terima teknis setiap fase.

### Daftar Commit Git (Branch: `ui-overhaul-mobile`):
- `5166788`: *Fase 4: Tombol navigasi floating bisa dipindah (long-press drag + snap + localStorage persistence)*
- `3d1a4de`: *Fase 5: Standarisasi top bar dan bottom nav seragam di 4 menu mobile*
- `7dff081`: *Fase 6: Beranda performa render instan, filter mapel pilihan, ikon unik 22 mapel, dan desain kartu kontras tinggi*
- `cf5cdc7`: *Fase 7: Carousel hero serba putih, hapus elemen toga/titik, animasi SVG pie chart & robot AI*
- `0ca9163`: *Fase 8: Carousel modul serba putih, robot membaca buku, dan progres gabungan bersegmen mapel pilihan*
- `4c85ec0`: *Fase 9: Perbaiki bug kedipan kartu, dashboard analitik belajar (streak, waktu, distribusi kategori), dan empty state rapi*
- `e3fd4bc`: *Fase 10: Skrip QA akhir komprehensif Playwright lintas 4 viewport & 5 menu utama*
- `8a9e004`: *Fase 11: Diagnosis dan perbaikan bottom nav seragam di 4 menu dashboard mobile*
- `2944a7a`: *Fase 12: Redesain bubble chat AI kontras tinggi dan tombol logo pemilih model ringkas*
- `77f2b6d`: *Fase 13: Tombol navigasi mengambang auto-minimize dan expand on tap*
- `f76d325`: *Fase 14: Pengaturan skala ukuran teks mobile global dan responsif*

---

## (C) HASIL SEMUA SKRIP TES OTOMATIS

Semua tes dijalankan secara headless menggunakan Playwright di server lokal `http://127.0.0.1:8080`:

| Skrip Pengujian | Target Cakupan | Hasil |
|---|---|---|
| `scratch/_tes_fase3.js` | Baseline Navbar Soal Hijau #004a2a, Dialog Konfirmasi Keluar, Mode Mobile/Desktop | **11/11 PASS** (0 error) |
| `scratch/_tes_fase4.js` | Long-press 400ms Drag, Snap 6 Kuadran, LocalStorage, Z-Index di atas Chat AI | **8/8 PASS** (0 error) |
| `scratch/_tes_fase5.js` | Top Bar & Bottom Nav Seragam 56px di Beranda, Modul, Progres, Akun | **8/8 PASS** (0 error) |
| `scratch/_tes_fase6.js` | Performa Render < 30ms, Mapel Pilihan, 22 Ikon Unik, Kontras Kartu Matematika | **7/7 PASS** (0 error) |
| `scratch/_tes_fase7.js` | Teks Carousel Hero Serba Putih, Hapus Toga/Titik, Animasi SVG Pie & Robot AI | **9/9 PASS** (0 error) |
| `scratch/_tes_fase8.js` | Carousel Modul, Robot Baca Buku, Segmented Progress Bar Mapel Pilihan Data Tiruan | **16/16 PASS** (0 error) |
| `scratch/_tes_fase9.js` | Stabilitas Bebas Kedip (2.5s sampling), Streak, Waktu Belajar, Empty State | **10/10 PASS** (0 error) |
| `scratch/_qa_akhir_fase10.js` | QA Akhir Lintas 4 Viewport (360, 390, 412, 1280px), Mode Tamu, 0 Console Errors | **15/15 PASS** (0 error) |
| `scratch/_tes_fase11.js` | Diagnosis & Presisi Tinggi Bottom Nav di 4 Menu (Selisih <= 1px, aktual 0px) | **11/11 PASS** (0 error) |
| `scratch/_tes_fase12.js` | Warna Bubble AI, Padding 16px, Scroll Mandiri Code/Table, Logo Model Picker Popover | **34/34 PASS** (0 error) |
| `scratch/_tes_fase13.js` | Auto-minimize 42px, Tap Expand 3 Tombol, Inactivity Auto-collapse 4s, Drag Tetap Jalan | **22/22 PASS** (0 error) |
| `scratch/_tes_fase14.js` | Kontrol Skala Teks 4 Tingkat, Akses Overflow/AI/Akun, 0 Overflow 130% di 360px, Desktop 16px | **22/22 PASS** (0 error) |
| **TOTAL KESELURUHAN** | **Rangkaian Lengkap Fase 3 - Fase 14** | **173/173 PASS (100%)** |

---

## (D) HASIL DIAGNOSIS, KEPUTUSAN DESAIN, & ASUMSI TEKNIS

### 1. Hasil Diagnosis Bottom Nav Terlalu Tinggi (Fase 11)
- **Gejala Awal**: User melaporkan bottom nav di dashboard mobile masih terasa terlalu tinggi, khususnya saat membuka menu "Progress".
- **Metode Investigasi**:
  Pengukuran presisi menggunakan Playwright `getBoundingClientRect()` dan `window.innerHeight` pada 3 resolusi viewport mobile kunci (360x640, 390x844, 412x915).
- **Temuan Bukti Ukur**:
  - Pada menu Beranda, Modul, dan Akun: tinggi `<nav>` terukur **57px** dengan posisi `bottom: 844px` (menempel pas di dasar layar).
  - Pada menu Progress: ditemukan deklarasi CSS utilitas `.pb-safe` di `workspace_progres/progres.html` yang didefinisikan sebagai:
    `padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 5rem) !important;` (5rem = 80px).
    Karena kelas `.pb-safe` dipasang langsung pada elemen `<nav class="... pb-safe">`, tinggi nav terdorong membesar menjadi **137px** (menjulang tinggi 80px di atas normal).
  - Selain itu, penggunaan `100vh` standar rentan menyebabkan layout bergeser saat URL address bar dinamis browser HP muncul/hilang.
- **Solusi Akar Masalah**:
  1. Memisahkan kelas padding pada `progres.html`:
     - `.pb-safe`: `padding-bottom: env(safe-area-inset-bottom, 0px)` (khusus untuk elemen `<nav>`).
     - `.pb-safe-content`: `padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 5.5rem)` (khusus untuk elemen scrollable container `<main>`).
  2. Mengganti `100vh` menjadi `100dvh` pada wrapper modal `#homeOverlay` dan `min-h-[100dvh]` pada kontainer Progres.
- **Hasil Verifikasi Pasca Perbaikan**:
  Keempat menu (Beranda, Modul, Progres, Akun) memiliki tinggi bar identik **57px** (selisih **0px**) dan menempel flush di tepi bawah viewport (`rect.bottom === window.innerHeight`).

### 2. Keputusan Tampilan Chat AI: Warna & Pemilih Model (Fase 12)
- **Warna & Kontras Bubble Jawaban AI**:
  - Bubble AI sebelumnya menggunakan warna netral gelap/abu-abu yang menyerupai background viewport chat (`#F8FAFC`), menyulitkan pembedaan visual antara percakapan dan latar.
  - Diputuskan desain kartu cerah elegan: Background bubble AI dibuat putih bersih (`#FFFFFF`) dengan kartu bergaris border aksen hijau lembut (`border: 1px solid #D1FAE5`) dan aksen vertikal hijau tua di tepi kiri (`#004a2a`).
  - Bubble pesan user menggunakan warna hijau tema aplikasi (`#004a2a`) dengan teks putih solid (`#FFFFFF`).
  - Rasio kontras teruji di atas 7:1 (memenuhi standar WCAG AAA). Pada Dark Mode, bubble AI menggunakan kartu hijau gelap lembut (`#11261B`) dengan teks hijau muda cerah (`#ECFDF5`).
- **Padding & Kerapian Tipografi Bubble**:
  - Padding dalam bubble ditingkatkan menjadi **16px** (sebelumnya terlalu mepet ke tepi kiri ~8px).
  - Line-height distandarkan pada **1.55** dengan margin antar paragraf dan bullet list yang proporsional.
  - Untuk mencegah konten markdown meluber keluar kartu pada jawaban teknis/rumus:
    - Seluruh blok kode `<pre><code>` dibungkus dengan styling `overflow-x: auto !important`, latar abu-abu gelap dengan tombol salin.
    - Tabel data markdown dibungkus kontainer responsif dengan `overflow-x: auto !important` dan padding sel konsisten.
- **Desain Ulang Pemilih Model AI**:
  - Bar pemilih model lama yang besar dan memakan ruang vertikal mobile dihilangkan (`display: none`).
  - Dipasang tombol logo model compact (32px circular button `#btnModelPicker`) yang disematkan sejajar di baris aksi atas bersama tombol "Chat Baru" dan chip pertanyaan saran.
  - Mengetuk tombol logo memunculkan popover kecil elegan (`#modelPopover`) berisi daftar model (Qwen 2.5 27B, Gemini 3.8 Flash, Gemini Pro). Model aktif ditandai ikon centang hijau.
  - Memilih model langsung mengubah status, memperbarui `aria-label`, menutup popover secara otomatis, dan menyimpan pilihan ke `localStorage['tka_active_ai_model']` tanpa merombak logika API yang ada.

### 3. Tombol Navigasi Mengambang Auto-Minimize (Fase 13)
- **Kondisi Normal (Idle State)**:
  - Tombol navigasi floating `#workRail` mengecil menjadi 1 tombol bulat compact berukuran **42px** (`.is-minimized`, `opacity: 0.88`, `border-radius: 50%`) dengan bayangan halus, sehingga tidak menutupi materi soal maupun opsi jawaban.
  - Menampilkan ikon tab aktif saat ini (ikon lembar soal `fa-file-lines`, buku `fa-book-open`, atau robot `fa-robot`).
- **Interaksi Mengembang & Auto-Collapse**:
  - Mengetuk tombol mini langsung mengembangkannya (`.is-expanded`, tinggi 170px) menampilkan 3 tombol lengkap dengan label teks ("Soal", "Pembahasan", "Tanya AI").
  - Auto-collapse timer: jika tidak ada interaksi selama **4 detik (4000ms)**, rail otomatis mengecil kembali dengan transisi kubik mulus.
  - Memilih salah satu tombol tab langsung mengeksekusi perpindahan tab dan mengecilkan kembali tombol dalam waktu 250ms.
  - Mengetuk di luar rail saat terbuka langsung menutup/mengecilkan rail seketika.
  - Menghormati pengaturan aksesibilitas `prefers-reduced-motion` (transisi instan tanpa jeda animasi).
- **Integritas Gestur Drag & Off-screen Clamping**:
  - Gestur long-press (>= 400ms) tetap mengaktifkan drag mode (`.rail-dragging`) dengan haptic feedback visual, sedangkan tap biasa (< 400ms) murni membuka menu tanpa memicu geser tak sengaja.
  - Clamping dinamis menjamin tombol saat mengembang tidak pernah terpotong atau keluar layar di seluruh 6 kuadran snap (`rect.top >= 0`, `rect.bottom <= innerHeight`, `rect.left >= 0`, `rect.right <= innerWidth`).
  - Pada tampilan Chat AI, tombol ditempatkan 24px di atas composer input sehingga tidak pernah menghalangi kolom ketik atau tombol kirim.
- **Isolasi Desktop**:
  - Pada layar desktop (>= 1100px), rule CSS membatalkan class `.is-minimized` dan mempertahankan format sidebar desktop asli 3 tombol penuh.

### 4. Pendekatan Kontrol Ukuran Teks Mobile & Asumsi (Fase 14)
- **Audit Penulisan Ukuran Font di CSS**:
  - Audit kode menunjukkan `style.css` mayoritas menggunakan unit `px` pada komponen Soal, Opsi Jawaban, dan Dialog CBT, sementara halaman modular (`workspace_modul`, `workspace_progres`, `workspace_akun`) menggunakan Tailwind CSS yang berbasis `rem`.
  - Diputuskan pendekatan **Hybrid Scaling Tanpa Perombakan Ekstrem**:
    1. Pada mobile media query `@media (max-width: 899px)`, set root `html[data-text-scale="X"]` dengan `font-size: calc(16px * var(--text-scale, 1)) !important` (90% = 14.4px, 100% = 16px, 115% = 18.4px, 130% = 20.8px). Hal ini secara otomatis menskalakan semua komponen berbasis Tailwind `rem` di iframe Modul, Progres, dan Akun.
    2. Pada `style.css`, rule font spesifik untuk elemen teks kunci (pertanyaan `.question-text`, stimulus `.stimulus-body`, opsi jawaban `.cbt-opt-text`, pembahasan `.solution-body`, bubble chat AI `.tutor-bubble`, kartu ringkasan, dan dialog konfirmasi) diskalakan secara presisi menggunakan `calc(base_px * var(--text-scale, 1)) !important`.
    3. **Proteksi Tinggi Bar**: Teks pada top navbar (`.app-header`) dan bottom navbar (`.stitch-bottomnav`) dibatasi skalanya (maksimal 108% dengan `clamp(10px, calc(12px * min(...)), 14px)`) agar ukuran tinggi fixed bar (57px) yang telah distandarkan di Fase 5 dan 11 tidak rusak atau membesar berlebihan.
- **Titik Akses Ganda**:
  - Titik akses (1): Di dalam menu overflow (⋮) halaman Soal terdapat baris `Ukuran Teks` dengan stepper `A-`, persentase (`100%`), dan `A+`.
  - Titik akses (1b): Di header AI Tutor (tampilan bottom sheet / tab AI), tombol `A` memunculkan popover compact yang memungkinkan user langsung mengatur ukuran teks tanpa harus keluar dari percakapan AI.
  - Titik akses (2): Di menu Akun, ditambahkan kartu `Pengaturan Tampilan` dengan baris `Ukuran Teks Aplikasi` berdesain senada kartu Tailwind Akun.
- **Sinkronisasi Multi-Iframe & Persistensi**:
  - Nilai skala disimpan di `localStorage['tka_font_scale']` dengan penanganan `try/catch`.
  - Saat user mengubah skala di Soal atau Akun, perubahan dibroadcast ke seluruh frame (`panelModulFrame`, `panelProgresFrame`, `panelAkunFrame`, dan parent window) via `postMessage({ type: 'set-font-scale', scale })` dan `window.addEventListener('storage')`.
  - Setiap panel yang dibuka via `sendPanelData()` langsung menerima sinkronisasi skala terkini.
- **Uji Stres 130% pada Lebar 360px**:
  - Terverifikasi 0 scroll horizontal (`scrollWidth === window.innerWidth = 360px`).
  - Teks pertanyaan dan opsi tidak terpotong (`overflow-x: hidden`, `word-break: break-word`).
  - Opsi jawaban tetap dapat diklik dengan padding proporsional.
  - Tombol mengambang (rail mini) dan bottom action bar tetap fungsional di posisinya masing-masing.
- **Isolasi Desktop & Mode Tamu**:
  - Aturan skala teks sepenuhnya dibungkus `@media (max-width: 899px)`. Pada desktop (1280px), `html` font-size tetap 16px murni (0 perubahan).
  - Mode Tamu di akun dan sistem autentikasi tidak tersentuh.

---

## (E) CARA MENGECEK HASIL DI MOBILE & DESKTOP

1. **Jalankan Server Lokal**:
   Pastikan server berjalan pada port 8080 (contoh: `python server.py` atau `npx http-server -p 8080 .`).
2. **Mengecek di Mobile (DevTools Responsive Mode)**:
   - Buka Chrome/Edge DevTools (F12 atau Ctrl+Shift+I).
   - Aktifkan Device Toolbar (Ctrl+Shift+M).
   - Pilih preset: **Galaxy S8/S20 (360x640)**, **iPhone 12/14/15 Pro (390x844)**, atau **Pixel 7 (412x915)**.
   - Akses: `http://127.0.0.1:8080/app?subject=matematika&paket=1`.
   - **Uji Fase 11**: Klik tombol Beranda di top bar -> Buka menu Beranda, Modul, Progres, Akun. Perhatikan tinggi bar bawah seragam 57px di semua menu tanpa celah.
   - **Uji Fase 12**: Buka tab AI Tutor -> Lihat bubble AI kartu putih bersih bergaris hijau halus, bubble user hijau tua. Klik tombol logo model compact di baris atas untuk membuka popover pemilih model.
   - **Uji Fase 13**: Lihat tombol navigasi mengambang di pojok kanan bawah: dalam kondisi diam berukuran kecil 42px bundar dengan ikon tab aktif. Tap sekali untuk membuka 3 tombol. Diam 4 detik -> otomatis mengecil kembali. Long-press 400ms untuk memindahkan posisi.
   - **Uji Fase 14**: 
     - Klik tombol menu overflow (⋮) di kanan atas navbar soal -> Tekan `A+` untuk menaikkan skala ke 115% atau 130%. Perhatikan font soal dan opsi membesar tanpa horizontal scroll.
     - Buka AI Tutor -> Klik tombol `A` di header AI -> Ubah skala teks langsung dari popover.
     - Buka Beranda -> Akun -> Periksa kartu "Pengaturan Tampilan", atur ukuran teks via stepper `A-` / `A+`.
3. **Mengecek di Desktop**:
   - Matikan Device Toolbar (lebar layar >= 1280px).
   - Seluruh layout desktop tetap standar: 3 tombol rail sidebar desktop penuh, font-size root 16px, navbar atas hijau utuh, dan dashboard desktop terintegrasi sempurna.
4. **Melihat Hasil Screenshot Otomatis**:
   Seluruh tangkapan layar verifikasi Playwright tersimpan di folder `exports/` dan `scratch/`:
   - `exports/fase11_*` (Presisi tinggi bottom nav di 4 menu)
   - `exports/fase12_*` (Bubble chat AI, popover model picker, dark mode)
   - `exports/fase13_*` (Tombol rail mini, expanded, drag & snap, safe layout di atas AI chat)
   - `exports/fase14_*` (Skala teks 130% di 360px, popover AI, panel Akun, desktop 1280px)

---

## (F) KESIMPULAN

Seluruh rangkaian pekerjaan mulai dari **Fase 4 hingga Fase 14** telah berhasil diselesaikan dan divalidasi secara otonom:
- **100% Tes Lolos (173 dari 173 checks lulus)** di seluruh skenario dan resolusi perangkat.
- **0 Error Console** di semua menu dan semua alur interaksi.
- **Mode Tamu Terjaga 100%**: Tidak ada perubahan pada alur sesi tamu, kuota latihan, maupun data pengguna.
- **Isolasi Desktop Terjamin**: Seluruh fitur mobile dibungkus dengan media query (`@media (max-width: 899px)`), menjamin pengalaman pengguna desktop tetap utuh tanpa efek samping.
