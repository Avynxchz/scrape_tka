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
| **Fase 10** | QA Akhir: regresi Fase 3-9, 0 console error, verifikasi 360/390/412px & desktop | **SELESAI** | 15/15 uji `_qa_akhir_fase10.js` PASS. Total 84/84 pengujian otomatis seluruh fase lulus 100%. Mode Tamu utuh, desktop aman, 0 console errors, tidak ada teks hijau di atas hijau, safe-area aware. |

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
