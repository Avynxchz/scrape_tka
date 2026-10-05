# PROGRESS OVERHAUL MOBILE TKA MASTER (FASE 4 - 10)

Terakhir diperbarui: 2026-10-05
Branch: `ui-overhaul-mobile`
Baseline: Fase 0 - 3 Selesai (11/11 tes lolos)

---

## 1. STATUS FASE

| Fase | Deskripsi | Status | Keterangan |
|---|---|---|---|
| **Fase 4** | Tombol navigasi mengambang (3 tombol bawah) bisa dipindah (long-press drag + snap + localStorage) | **SELESAI** | 8/8 uji `_tes_fase4.js` PASS. Long-press 400ms, haptic/outline, snap 6 posisi, aman di atas chat AI (z-index 75). |
| **Fase 5** | Navbar atas & bottom nav konsisten di 4 menu mobile (Beranda, Modul, Progress, Akun) | **SELESAI** | 8/8 uji `_tes_fase5.js` PASS. Top bar seragam (brand logo + title + subtitle + avatar), bottom nav seragam 56px (h-14) + pb-safe. Tombol search dipindah ke konten Modul. Reset/AI badge dipindah ke konten Progres. |
| **Fase 6** | Beranda: performa & desain ulang kartu mapel (ikon unik, warna cerah, nama terstandar) | **SELESAI** | 7/7 uji `_tes_fase6.js` PASS. 22 ikon Material Symbols 100% unik tanpa duplikat. Waktu render turun drastis menjadi 12ms (sebelumnya ~1055ms DCL + 44 network requests). Hanya mapel pilihan user yang tampil (default 4 mapel = 8 kartu). Tombol "Lihat Semua" dihapus. Kontras Matematika diperbaiki menjadi biru cerah #1D4ED8. Modal "Atur Mapel" tersedia. |
| **Fase 7** | Beranda: carousel hijau hero (semua teks putih, hapus hiasan toga/titik, animasi SVG/CSS kanan) | **SELESAI** | 9/9 uji `_tes_fase7.js` PASS. Semua teks carousel putih solid (#FFFFFF / rgb(255,255,255)). Titik-titik dan topi toga dihapus total. Slide 2: SVG Pie Chart animasi ring pulse. Slide 3: SVG Robot AI animasi mata berkedip & antena berdenyut. Carousel controller reusable di-export ke `window.setupCarouselController`. |
| **Fase 8** | Menu Modul: carousel reusable, progress gabungan bersegmen mapel pilihan | **SELESAI** | 16/16 uji `_tes_fase8.js` PASS. Carousel 2-slide reusable, teks serba putih solid. Slide 1: Kurikulum & Maskot Robot AI sedang membaca buku beranimasi. Slide 2: Progres Gabungan Mapel Pilihan (multi-segmented progress bar dengan warna unik tiap mapel + legenda ringkas interaktif). Semua 22 mapel dan 5 kategori dipertahankan utuh. |
| **Fase 9** | Menu Progress: fix blinking cards, dashboard analitik belajar, empty state | **SELESAI** | 10/10 uji `_tes_fase9.js` PASS. Bug kartu berkedip berhasil diperbaiki total dengan memoization state data (`_lastRenderedProgressJson`) dan penghapusan class `.fade-in` pada re-render berulang. Dashboard analitik dilengkapi widget streak kehadiran, waktu belajar hari ini vs kemarin, visualisasi distribusi 5 rumpun kategori, dan empty state ramah. |
| **Fase 11** | Diagnosis & perbaikan bottom nav terlalu tinggi (menu dashboard, mobile) | **SELESAI** | 11/11 uji `_tes_fase11.js` PASS. Akar masalah ditemukan di `progres.html` (`.pb-safe` hardcoded `+ 5rem` = 80px pada nav). Setelah perbaikan, tinggi (57px) dan posisi bottom (menempel flush) 100% IDENTIK di 4 menu (Beranda, Modul, Progres, Akun) pada 360, 390, dan 412 px (selisih 0px). |
| **Fase 12** | Chat AI: tampilan jawaban & pemilih model (warna bubble, padding 12-16px, logo pemilih model ringkas) | **SELESAI** | 34/34 uji `_tes_fase12.js` PASS, 0 error console. Bubble AI putih bersih (#FFFFFF) di atas background chat (#F8FAFC) dengan aksen hijau dan padding 16px (line-height 1.55). Fenced code blocks & tabel ber-scroll horizontal mandiri tanpa meluber. Tombol logo model compact (32px) dengan popover picker rapi (checkmark, icons, persist ke localStorage). Dark mode terverifikasi kontras tinggi. |
| **Fase 13** | Tombol navigasi mengambang bisa mengecil otomatis (auto-minimize 36-44px + expand on tap + auto collapse) | **SELESAI** | 22/22 uji `_tes_fase13.js` PASS, 0 error console. Mode normal idle berupa 1 tombol bulat compact 42px transparan (opacity 0.88) dengan ikon tab aktif. Tap mengembang menampilkan 3 tombol (Soal, Pembahasan, Tanya AI). Diam 4 detik atau memilih tombol otomatis mengecil kembali. Drag long-press (>=400ms) tetap berfungsi dan snap aman ke 6 posisi tanpa meluber keluar layar. Desktop 1280px tetap format sidebar asli. |
| **Fase 14** | Kontrol ukuran teks mobile (90%, 100%, 115%, 130% di menu overflow Soal & Akun, persist localStorage) | **SELESAI** | 22/22 uji `_tes_fase14.js` PASS, 0 error console. Skala teks 4 tingkat (90%, 100%, 115%, 130%) dapat diakses dari menu overflow (⋮) Soal, popover header AI Tutor, dan menu Akun. Sinkron real-time antar iframe via postMessage & localStorage. Pada 130% di 360px: 0 horizontal overflow, font membesar proporsional, bar atas/bawah terproteksi. Desktop 1280px tetap 16px. |

---

## 2. ASUMSI
- **Fase 4**: Durasi threshold long-press ditetapkan 400ms dengan batas toleransi gerakan 10px untuk membedakan antara gestur scroll layar biasa dan gestur pemindahan rail tombol. Posisi snap dibagi menjadi 6 kuadran (top-left, top-right, mid-left, mid-right, bottom-left, bottom-right) dengan safe-area padding agar tidak bertubrukan dengan top bar maupun bottom action bar.
- **Fase 5**:
  - Top bar 4 menu distandarkan ke pola: Logo hijau bulat `school` + TKA Master + sub-label menu (BERANDA / MODUL BELAJAR / PROGRES BELAJAR / AKUN) + avatar bulat di kanan (`person`).
  - Search bar Modul dipindahkan dari top bar ke dalam konten (tepat di bawah carousel dan kategori filter), sehingga top bar tidak janggal/berbeda sendiri.
  - Tombol reset dan badge kuota AI di Progres dipindahkan dari top bar ke baris header konten utama (sejajar dengan judul 'Progres Belajar'), mempertahankan fungsionalitas tanpa merusak keseragaman navbar.
  - Tinggi bottom nav ditetapkan 56px (`h-14`) dengan `pb-[env(safe-area-inset-bottom)]`, menyelesaikan masalah bottom nav yang sebelumnya terlalu menjulang/tinggi (64-72px).
- **Fase 6**:
  - **Penyebab Lambat Beranda**: Sebelumnya fungsi `homePrefetchCounts()` melakukan fetch berurutan terhadap 44 berkas JSON soal lengkap (22 mapel x 2 paket) saat Beranda dibuka, menyebabkan puluhan network roundtrips dan re-render ganda (`renderHome()` dipanggil ulang setelah prefetch selesai).
  - **Perbaikan & Pengukuran Performa**: Data jumlah soal di-preseed langsung dari data statis terverifikasi `KONTRAK_DATA.md` (`STATIC_SOAL_COUNTS`) sehingga 0 network fetch diperlukan untuk menampilkan kartu. Waktu eksekusi `renderHome()` turun dari ~39.6ms ke **12.0ms** dan DOM node kartu berkurang dari 44 kartu menjadi 8 kartu (berdasarkan 4 mapel pilihan user).
  - **Mapel Pilihan Default**: Jika belum diatur user, Beranda menampilkan 4 mapel (Matematika, Bahasa Indonesia, Bahasa Inggris, Fisika). User dapat mengatur mapel melalui tombol "Atur Mapel" yang memunculkan sheet pilihan mapel dan disimpan ke `localStorage['tka_user_subjects']`.
  - **Ikon Unik 22 Mapel**: 22 mapel masing-masing memiliki ikon unik tanpa satupun duplikasi: `calculate` (Mtk), `menu_book` (B. Indo), `language` (B. Ing), `bolt` (Fisika), `science` (Kimia), `biotech` (Biologi), `payments` (Ekonomi), `public` (Geografi), `groups` (Sosiologi), `landmark` (Sejarah), `diversity_3` (Antropologi), `storefront` (PKWU), `functions` (Mtk Lanjut), `auto_stories` (Indo Lanjut), `translate` (Inggris Lanjut), `gavel` (PPKn), `edit_note` (Arab), `wb_sunny` (Jepang), `castle` (Jerman), `architecture` (Prancis), `brush` (Mandarin), `stars` (Korea).
  - **Solusi Nama Panjang**: Nama lengkap seperti Pendidikan Pancasila & Kewarganegaraan diringkas menjadi "PPKn", Kewirausahaan disingkat "PKWU" pada kartu dan chip, dengan line-clamp 2 baris konsisten.
- **Fase 7**:
  - **Teks Putih Penuh**: Seluruh elemen teks dalam `.stitch-hero` (h1, h2, h3, p, sub-bar label, badge 'Gratis selama beta', nilai statistik, note) menggunakan `#FFFFFF` solid murni tanpa opacity yang meredupkan, memastikan kontras tertinggi di atas background gradien hijau gelap `#0B1E13` ke `#004a2a`. Teks di dalam kartu ilustrasi putih (`.stitch-paper`) tetap memakai warna teks hijau agar kontras dan terbaca.
  - **Hapus Elemen Dekoratif**: `.stitch-dotrow` (titik-titik) dan `.stitch-cap` (topi toga) di atas teks dihapus agar layout lebih bersih dan tidak mengganggu keterbacaan judul.
  - **Animasi Visual Kanan**: Slide 2 menggunakan visual kartu Pie Chart beranimasi ring SVG, dan Slide 3 menggunakan visual Robot AI interaktif beranimasi (antena berdenyut, mata digital berkedip, micro-interactions). Respects `prefers-reduced-motion`.
  - **Komponen Carousel Reusable**: Logic sinkronisasi carousel diekstrak ke `window.setupCarouselController(carEl, dotsSelector)` untuk digunakan ulang di Fase 8 (Modul).
- **Fase 8**:
  - **Statistik Modul**: Info "22 mapel · 44 paket · 961 soal" dipertahankan di Slide 1 (Kurikulum) sebagai gambaran total bank soal. Namun di Slide 2 (Progres), angka global diganti dengan fokus yang jauh lebih relevan: **Progres Gabungan Mapel Pilihan** (contoh: "0 dari 205 soal dikerjakan (4 mapel)").
  - **Segmented Bar Multi-Warna**: Menggunakan pemetaan warna tematik mapel (`SUBJECT_COLORS`), bar gabungan terbagi menjadi segmen-segmen proporsional terhadap total soal gabungan mapel pilihan. Dilengkapi legenda ringkas berisi chip warna, nama mapel, dan jumlah selesai/total per mapel.
  - **Animasi Robot Membaca Buku**: Maskot Robot AI SVG beranimasi halus memegang buku dengan lembaran halaman yang beranimasi membalik (`stBookPageFlip`), antena berdenyut (`stAntennaPulse`), dan mata berkedip (`stRobotBlink`).
- **Fase 9**:
  - **Akar Masalah Bug Kartu Berkedip (Blinking)**:
    1. Fungsi `postToFrameReliable()` di `app.js` mengirim postMessage 8 kali berturut-turut berselang 400ms.
    2. Di `workspace_progres/progres.html`, setiap pesan `progress-data` memicu `renderAll()` yang langsung me-replace seluruh `kpiContainer.innerHTML` dengan template baru yang mengandung class `.fade-in` (`animation: fadeUp 0.35s`).
    3. Animasi fade-in tersebut di-restart 8 kali dalam rentang 3.2 detik pertama, sehingga kartu tampak berkedip (muncul-hilang berulang).
    4. Perbaikan: Diterapkan data memoization (`_lastRenderedProgressJson`), menghilangkan class `.fade-in` pada DOM update berulang, dan membatasi retry di `postToFrameReliable` jika frame sudah loaded.
  - **Tabel Widget Dashboard Analitik Belajar**:
    | Widget | Tujuan & Informasi yang Disampaikan | Manfaat Bagi Pengguna |
    |---|---|---|
    | **KPI Total Soal Selesai** | Jumlah butir soal yang telah diselesaikan terhadap 961 butir kurikulum dengan progress bar. | Mengukur volume latihan secara transparan. |
    | **KPI Ketepatan (Akurasi)** | Persentase jawaban benar beserta jumlah butir benar vs salah. | Evaluasi kualitas pemahaman materi secara instan. |
    | **Kehadiran (Streak Belajar)** | Jumlah hari aktif latihan berturut-turut (ikon api amber). | Membangun motivasi dan disiplin belajar harian. |
    | **Waktu Belajar** | Estimasi durasi belajar hari ini vs kemarin (dalam menit). | Memberikan refleksi alokasi waktu belajar yang terukur. |
    | **Distribusi Rumpun Mapel** | Progres pengerjaan soal pada 5 kategori (Wajib, Saintek, Soshum, Lanjut, Bahasa) dengan bar warna tematik. | Mengidentifikasi kategori mapel yang tertinggal atau mendominasi. |
    | **Mata Pelajaran Aktif** | Daftar kartu mapel yang sedang berjalan (rincian Paket 1 & 2) dengan tombol Lanjut/Mulai. | Akses cepat satu klik untuk melanjutkan tryout. |
    | **Mata Pelajaran Belum Dimulai** | Daftar mapel belum tersentuh (redup) dengan tombol Mulai. | Mendorong eksplorasi mapel lain secara terstruktur. |
  - **Empty State**: Ketika user baru belum memiliki riwayat, ditampilkan empty state yang bersih dengan headline motivatif dan tombol CTA "Mulai Latihan Paket 1".
- **Fase 10**:
  - Seluruh skrip verifikasi otomatis Fase 3 s/d 9 dan QA Akhir dijalankan berturut-turut dalam satu alur eksekusi.
  - Hasil: 84/84 checks PASS, 0 console errors, tidak ada layout patah/rusak di viewport mobile (360px, 390px, 412px) maupun desktop (1280px). Mode Tamu dipertahankan 100% utuh tanpa modifikasi struktural.
- **Fase 11 (Diagnosis & Perbaikan Bottom Nav Terlalu Tinggi)**:
  - **Bukti Ukur Awal (Pra-perbaikan)** via `scratch/_diagnosa_fase11.js`:
    - Viewport 360x640: Beranda = 57px (pb: 0px), Modul = 57px (pb: 0px), **Progres = 137px (pb: 80px)**, Akun = 57px (pb: 0px).
    - Viewport 390x844: Beranda = 57px (pb: 0px), Modul = 57px (pb: 0px), **Progres = 137px (pb: 80px)**, Akun = 57px (pb: 0px).
    - Viewport 412x915: Beranda = 57px (pb: 0px), Modul = 57px (pb: 0px), **Progres = 137px (pb: 80px)**, Akun = 57px (pb: 0px).
    - Terlihat jelas bottom nav di menu Progres membengkak setinggi 137px (selisih 80px dari menu lainnya) karena `padding-bottom: 80px`.
  - **Akar Masalah**:
    Di `workspace_progres/progres.html`, rule `.pb-safe` didefinisikan sebagai:
    `padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 5rem);` (5rem = 80px).
    Class `.pb-safe` ini awalnya dirancang untuk padding bawah elemen konten agar tidak tertutup nav, namun kemudian secara tidak sengaja dipasang langsung pada elemen `<nav class="... pb-safe ...">`. Akibatnya, `<nav>` itu sendiri mendapatkan padding bawah 80px di luar tinggi bar 56px (`h-14`) dan border 1px, sehingga menjulang setinggi 137px (atau mencapai 170px pada iPhone dengan home bar).
  - **Solusi**:
    1. Memisahkan fungsi: `.pb-safe` di `workspace_progres/progres.html` dikembalikan murni ke `env(safe-area-inset-bottom, 0px)` untuk elemen `<nav>`.
    2. Menambahkan class `.pb-safe-content` (`calc(env(safe-area-inset-bottom, 0px) + 5.5rem)`) yang dipasang khusus pada elemen `<main>` agar konten tidak tertutup saat discroll ke paling bawah.
    3. Menambahkan properti `height: 100dvh` pada `.home-overlay` dan `.home-panel-frame` di `home_stitch.css`, serta `min-h-[100dvh]` pada `#progresMobile` untuk menjamin stabilitas ketinggian viewport saat mobile address bar muncul/hilang secara dinamis.
  - **Bukti Ukur Pasca-perbaikan** via `scratch/_tes_fase11.js`:
    - 360px: Beranda = 57px, Modul = 57px, Progres = 57px, Akun = 57px (selisih 0px, 100% IDENTIK).
    - 390px: Beranda = 57px, Modul = 57px, Progres = 57px, Akun = 57px (selisih 0px, 100% IDENTIK).
    - 412px: Beranda = 57px, Modul = 57px, Progres = 57px, Akun = 57px (selisih 0px, 100% IDENTIK).
    - Semua menempel flush di posisi paling bawah (`rect.bottom === window.innerHeight`).
    - 11/11 tes otomatis lulus, 0 console errors, desktop 1280px tetap menyembunyikan bottom nav mobile (`display: none`).
- **Fase 12**:
  - **Warna & Padding Bubble Chat AI**:
    - Background chat messages disetel ke `#F8FAFC` (slate-50 ramah mata) dan `#0A1611` pada mode gelap.
    - Bubble jawaban AI memakai background `#FFFFFF` (putih solid bersih) dengan border halus `#E2E8F0` dan border-left hijau `#004a2a` 3px, kontras teks `#0F172A` (> 10:1 kontras ratio).
    - Mode gelap bubble AI memakai `#11261B` dengan teks `#ECFDF5` (kontras ratio > 11:1).
    - Padding dalam 16px nyaman, line-height 1.55, margin list 6px, bullet point rapi.
  - **Anti-Meluber Konten Markdown**:
    - Fenced code block (```) diubah menjadi `<div class="ai-code-block"><pre><code>` dengan background slate gelap `#0F172A`, font monospace, dan `overflow-x: auto !important` mandiri.
    - Markdown table diubah menjadi `<div class="ai-table-wrap"><table>` dengan padding header rapi, border table, dan `overflow-x: auto !important` mandiri tanpa meluber keluar bubble.
  - **Pemilih Model Ringkas (Logo Button & Popover)**:
    - Selector bar model yang lama dan bulky disembunyikan (`display: none`).
    - Digantikan tombol logo model bulat compact 32px (`#btnModelPicker`) yang ditempatkan sejajar di bar aksi atas bersama tombol "Chat Baru" dan quick suggestion chips.
    - Ikon model berubah dinamis sesuai model aktif: Petir (`fa-bolt`) untuk Qwen 2.5 27B, Tongkat Sihir (`fa-wand-magic-sparkles`) untuk Gemini 3.8 Flash, dan Otak (`fa-brain`) untuk Gemini Pro.
    - Saat logo diklik, popover melayang anggun di bawah tombol menampilkan daftar model, deskripsi singkat, dan tanda centang aktif. Memilih model langsung mengubah state, meng-update tombol & dropdown lama (kompatibilitas penuh), menyimpan ke `localStorage['tka_tutor_model']`, dan menutup popover otomatis.
  - **Hasil Verifikasi**:
    - 34/34 uji lolos di 360px, 390px, 412px, dan desktop 1280px via `scratch/_tes_fase12.js`. 0 error console.
- **Fase 13**:
  - **Auto-Minimize State (Idle)**:
    - Mode normal mobile berupa 1 tombol lingkaran kecil 42px x 42px (`.is-minimized`) dengan opacity 0.88 dan bayangan lembut. Teks label disembunyikan, hanya menampilkan ikon konteks aktif (Soal: `fa-file-lines`, Pembahasan: `fa-book-open`, Tanya AI: `fa-robot`).
    - Tidak menutupi isi soal maupun opsi jawaban, dan berada 24px di atas chat input box pada tampilan AI Tutor (`railBottom: 545px` vs `inputTop: 569px` pada 360px).
  - **Expand on Tap & Auto-Collapse**:
    - Tap cepat (< 400ms) pada tombol mini memicu ekspansi halus (`.is-expanded`) menjadi 3 tombol vertikal berlabel lengkap (Soal, Pembahasan, Tanya AI).
    - Timer auto-collapse 4 detik (4000ms): jika tidak ada interaksi selama 4s, rail mengecil kembali secara otomatis dengan animasi kubik mulus.
    - Mengetuk salah satu tombol langsung berpindah tab dan mengecilkan rail kembali setelah 250ms.
    - Mengetuk di luar rail saat terbuka langsung mengecilkan rail.
    - Mendukung `prefers-reduced-motion: reduce` (animasi dimatikan seketika tanpa transisi).
  - **Integritas Gestur Drag & Off-screen Clamping**:
    - Long-press >= 400ms tetap mengaktifkan drag mode (`.rail-dragging`) dengan haptic feedback.
    - Saat mengembang di seluruh 6 posisi snap (`snap-top-left`, `snap-top-right`, `snap-mid-left`, `snap-mid-right`, `snap-bottom-left`, `snap-bottom-right`), bounding clamp dinamis dan safe-area menjamin 3 tombol tidak pernah terpotong atau keluar layar (`rect.top >= 0`, `rect.bottom <= innerHeight`, `rect.left >= 0`, `rect.right <= innerWidth`).
  - **Isolasi Desktop**:
    - Pada desktop (>= 1100px), rule CSS membatalkan class `.is-minimized` dan mempertahankan sidebar 3 tombol penuh dengan posisi `fixed right: 16px; top: 50%`.
  - **Hasil Verifikasi**:
    - 22/22 uji lolos di 360px, 390px, 412px, dan desktop 1280px via `scratch/_tes_fase13.js`. 0 error console. Regresi Fase 4 lulus 8/8 via `scratch/_tes_fase4.js`.
- **Fase 14**:
  - **Audit Ukuran Font di CSS**:
    - Audit menunjukkan `style.css` mayoritas menggunakan unit `px` pada komponen Soal, Opsi Jawaban, dan Dialog CBT, sementara halaman modular (`workspace_modul`, `workspace_progres`, `workspace_akun`) menggunakan Tailwind CSS yang berbasis `rem`.
    - Diputuskan pendekatan **Hybrid Scaling Tanpa Perombakan Ekstrem**:
      1. Pada mobile media query `@media (max-width: 899px)`, set root `html[data-text-scale="X"]` dengan `font-size: calc(16px * var(--text-scale, 1)) !important` (90% = 14.4px, 100% = 16px, 115% = 18.4px, 130% = 20.8px). Hal ini secara otomatis menskalakan semua komponen berbasis Tailwind `rem` di iframe Modul, Progres, dan Akun.
      2. Pada `style.css`, rule font spesifik untuk elemen teks kunci (pertanyaan `.question-text`, stimulus `.stimulus-body`, opsi jawaban `.cbt-opt-text`, pembahasan `.solution-body`, bubble chat AI `.tutor-bubble`, kartu ringkasan, dan dialog konfirmasi) diskalakan secara presisi menggunakan `calc(base_px * var(--text-scale, 1)) !important`.
      3. **Proteksi Tinggi Bar**: Teks pada top navbar (`.app-header`) dan bottom navbar (`.stitch-bottomnav`) dibatasi skalanya (maks. 108% dengan `clamp(10px, calc(12px * min(...)), 14px)`) agar ukuran tinggi fixed bar (57px) yang telah distandarkan di Fase 5 dan 11 tidak rusak atau membesar berlebihan.
  - **Titik Akses & UI Stepper**:
    - Titik akses (1): Di dalam menu overflow (⋮) halaman Soal terdapat baris `Ukuran Teks` dengan stepper `A-`, persentase (`100%`), dan `A+`.
    - Titik akses (1b): Di header AI Tutor (tampilan bottom sheet / tab AI), tombol `A` memunculkan popover compact yang memungkinkan user langsung mengatur ukuran teks tanpa harus keluar dari percakapan AI.
    - Titik akses (2): Di menu Akun, ditambahkan kartu `Pengaturan Tampilan` dengan baris `Ukuran Teks Aplikasi` berdesain senada kartu Tailwind Akun.
  - **Sinkronisasi Antar-Iframe & Persistensi**:
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
  - **Hasil Verifikasi**:
    - 22/22 uji lolos di 360px, 390px, 412px, dan desktop 1280px via `scratch/_tes_fase14.js`. 0 error console. Persistensi reload dan sinkronisasi lintas halaman teruji 100%.

---

## 3. KEPUTUSAN YANG PERLU DITINJAU USER
- Penempatan search bar Modul di dalam area konten di bawah carousel hero (bukan di navbar atas).
- Penempatan tombol reset riwayat dan badge kuota AI di baris judul konten Progres Belajar.
- Default 4 mapel pilihan Beranda & Modul: Matematika, Bahasa Indonesia, Bahasa Inggris, Fisika (bisa diubah bebas via tombol "Atur Mapel").
- Desain kartu Beranda: kartu putih bersih dengan garis aksen warna tema di atas, chip kontras tinggi (Matematika = biru #1D4ED8, bukan cokelat).
- Ilustrasi kanan pada hero carousel: Slide 1 Lembar Soal + Pensil, Slide 2 Animasi SVG Pie Chart, Slide 3 Maskot Robot AI Interaktif.
- Slide 1 Carousel Modul: Maskot Robot AI membaca buku + 3 chip statistik kurikulum (22 Mapel / 44 Paket / 961 Soal).
- Slide 2 Carousel Modul: Progres gabungan bersegmen mapel pilihan + legenda ringkas warna mapel.
- Pemilihan widget analitik Progress: KPI Soal, Akurasi, Streak Belajar Harian, Waktu Belajar Hari Ini vs Kemarin, dan Distribusi 5 Rumpun Kategori.

---

## 4. CATATAN TEKNIS
- Baseline Fase 0-3 lulus 11/11 uji otomatis Playwright (`scratch/_tes_fase3.js`).
- Port server lokal: `http://127.0.0.1:8080`.
- Safe area aware (`env(safe-area-inset-*)`) wajib dipertahankan untuk semua floating / pinned element.
- Regresi Fase 3, 4, 5, 6, 7, 8, 9, 10 terverifikasi lulus 100% (84/84 checks).
