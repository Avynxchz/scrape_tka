# LAPORAN AKHIR: OVERHAUL UI MOBILE TKA MASTER (FASE 4 - FASE 10)

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

---

## (B) FILE YANG DIUBAH & DAFTAR COMMIT

### File yang Diubah:
1. `index.html`: Penyesuaian hero carousel Beranda (hapus dekorasi toga/titik, markup SVG Pie Chart & Robot AI), integrasi modal Atur Mapel, standarisasi top bar.
2. `home_stitch.css`: Warna teks hero carousel serba putih (#FFFFFF), keyframes animasi (`stPieSpin`, `stPiePulse`, `stAntennaPulse`, `stRobotBlink`, `stFloat`), kartu mapel kontras tinggi, styling modal Atur Mapel.
3. `app.js`: Drag & snap logic `#workRail`, pengelolaan mapel pilihan user (`getUserSelectedSubjects`), pre-seeded counts, reusable carousel controller, optimasi pengiriman `postToFrameReliable`.
4. `workspace_modul/modul.html`: Carousel reusable 2-slide, SVG animasi robot membaca buku, segmented progress bar multi-warna, legenda ringkas mapel pilihan, search bar dalam konten.
5. `workspace_progres/progres.html`: Perbaikan anti-blinking memoized render, dashboard analitik belajar (streak, waktu belajar, distribusi 5 kategori), empty state bersih.
6. `scratch/_tes_fase4.js` s/d `scratch/_tes_fase9.js`, `scratch/_qa_akhir_fase10.js`: Rangkaian skrip uji otomatis Playwright komprehensif.
7. `scratch/PROGRESS.md`: Catatan status progres, asumsi, dan serah-terima teknis setiap fase.

### Daftar Commit Git (Branch: `ui-overhaul-mobile`):
- `5166788`: *Fase 4: Tombol navigasi floating bisa dipindah (long-press drag + snap + localStorage persistence)*
- `3d1a4de`: *Fase 5: Standarisasi top bar dan bottom nav seragam di 4 menu mobile*
- `7dff081`: *Fase 6: Beranda performa render instan, filter mapel pilihan, ikon unik 22 mapel, dan desain kartu kontras tinggi*
- `cf5cdc7`: *Fase 7: Carousel hero serba putih, hapus elemen toga/titik, animasi SVG pie chart & robot AI*
- `0ca9163`: *Fase 8: Carousel modul serba putih, robot membaca buku, dan progres gabungan bersegmen mapel pilihan*
- `4c85ec0`: *Fase 9: Perbaiki bug kedipan kartu, dashboard analitik belajar (streak, waktu, distribusi kategori), dan empty state rapi*
- `e3fd4bc`: *Fase 10: Skrip QA akhir komprehensif Playwright lintas 4 viewport & 5 menu utama*

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
| **TOTAL KESELURUHAN** | **Rangkaian Lengkap Fase 3 - Fase 10** | **84/84 PASS (100%)** |

---

## (D) ASUMSI & KEPUTUSAN YANG PERLU DITINJAU USER

1. **Penyebab Lambat Beranda & Solusinya (Fase 6)**:
   - *Penyebab*: `homePrefetchCounts()` sebelumnya melakukan `fetch` berantai terhadap 44 berkas JSON soal lengkap (22 mapel x 2 paket) saat Beranda dibuka, menyebabkan puluhan network latency dan re-render ganda.
   - *Solusi*: Jumlah butir soal di-preseed langsung dari kontrak data statis `KONTRAK_DATA.md` (`STATIC_SOAL_COUNTS`). Render time turun drastis dari ~39.6ms ke **12.0ms** tanpa ada blocking fetch.
2. **Solusi Nama Panjang Mapel (Fase 6)**:
   - Mapel bernama panjang disingkat pada kartu dan chip (contoh: "PPKn" untuk Pendidikan Pancasila dan Kewarganegaraan, "PKWU" untuk Prakarya dan Kewirausahaan). Teks judul menggunakan line-clamp 2 baris konsisten dengan ellipsis jika terjadi pembungkusan teks.
3. **Penyebab Bug Kartu Berkedip di Menu Progres & Solusinya (Fase 9)**:
   - *Penyebab*: `postToFrameReliable` di `app.js` mengirim pesan `progress-data` sebanyak 8 kali berselang 400ms saat frame dibuka. Setiap pesan memicu `renderMobile()` yang menimpa `kpiContainer.innerHTML` dengan template berkelas `.fade-in` (`animation: fadeUp 0.35s`). Akibatnya animasi fade-in di-restart 8 kali dalam 3.2 detik pertama.
   - *Solusi*: Diterapkan data memoization (`_lastRenderedProgressJson`). Jika data identik, DOM tidak dibongkar. Class `.fade-in` pada DOM update berulang dihapus. Kartu kini 100% stabil.
4. **Keputusan Statistik Modul (Fase 8)**:
   - Info kurikulum "22 mapel · 44 paket · 961 soal" dipertahankan di Slide 1 sebagai referensi cakupan bank soal. Namun di Slide 2, angka global diganti menjadi **Progres Gabungan Mapel Pilihan** (contoh: 4 mapel x 25 soal = 100 soal, multi-segmen berwarna) karena jauh lebih memotivasi siswa untuk menyelesaikan target tryout mereka.
5. **Tabel Widget Dashboard Analitik Progres (Fase 9)**:
   - **KPI Soal Selesai**: Total soal dikerjakan terhadap 961 butir dengan progress bar.
   - **KPI Ketepatan / Akurasi**: Persentase benar vs salah dengan rasio jelas.
   - **Streak Kehadiran**: Jumlah hari aktif latihan berturut-turut (ikon api amber) untuk menjaga konsistensi.
   - **Waktu Belajar**: Estimasi durasi latihan hari ini vs kemarin (dalam menit).
   - **Distribusi Rumpun Mapel**: Progress bar horizontal untuk 5 rumpun (Wajib, Saintek, Soshum, Lanjut, Bahasa).
   - **Mapel Aktif & Mapel Belum Dimulai**: Akses langsung satu klik untuk melanjutkan atau memulai tryout.
   - **Empty State**: Tampilan bersih motivatif dengan tombol CTA langsung ke Paket 1.

---

## (E) CARA MENGECEK HASIL DI MOBILE & DESKTOP

1. **Jalankan Server Lokal**:
   Pastikan server berjalan pada port 8080 (contoh: `npx http-server -p 8080 .` atau runner python).
2. **Mengecek di Mobile (DevTools Responsive Mode)**:
   - Buka Chrome/Edge DevTools (F12 atau Ctrl+Shift+I).
   - Aktifkan Device Toolbar (Ctrl+Shift+M).
   - Pilih preset: **iPhone 12/14/15 Pro (390x844)**, **Galaxy S8/S20 (360x740)**, atau **Pixel 7 (412x915)**.
   - Akses: `http://127.0.0.1:8080/app?subject=matematika&paket=1`.
   - **Uji Fase 4**: Tekan dan tahan (long-press 400ms) pada tombol melayang di pojok kanan bawah (Soal/Pembahasan/Tanya AI), geser ke kiri/tengah/atas, lalu lepaskan (tombol akan snap).
   - **Uji Fase 5, 6, 7**: Klik tombol Beranda di topbar (ikon rumah) -> Konfirmasi "Ya". Perhatikan top bar seragam, hero carousel serba putih (geser slide 1, 2, 3), 4 mapel pilihan, dan tombol "Atur Mapel".
   - **Uji Fase 8**: Klik tab "Modul" di bottom nav. Geser hero carousel: lihat animasi maskot robot AI membaca buku di slide 1 dan segmented bar multi-warna di slide 2.
   - **Uji Fase 9**: Klik tab "Progres" di bottom nav. Perhatikan kartu langsung stabil tanpa kedipan (blinking), widget streak kehadiran, waktu belajar hari ini vs kemarin, dan distribusi kategori.
3. **Mengecek di Desktop**:
   - Matikan Device Toolbar (lebar layar >= 1280px).
   - Tampilan desktop tetap memiliki layout lebar, dashboard desktop via iframe, dan navbar soal hijau tanpa perubahan negatif.
4. **Melihat Hasil Screenshot Otomatis**:
   Semua tangkapan layar verifikasi tersimpan di folder:
   - `scratch/screenshots_fase7/`
   - `scratch/screenshots_fase8/`
   - `scratch/screenshots_fase9/`
   - `scratch/screenshots_qa_akhir/`

---

## (F) HAL-HAL KECIL YANG BELUM RAPI (CATATAN MINOR)

1. **Sinkronisasi Mapel Pilihan Antar Iframe**:
   - Saat ini pemilihan mapel disimpan di `localStorage['tka_user_subjects']`. Jika user mengubah mapel di modal Beranda, Beranda langsung terupdate seketika. Namun iframe Modul baru akan membaca pilihan terbaru saat user berpindah tab atau saat iframe di-reload.
2. **Estimasi Waktu Belajar Real vs Timestamp**:
   - Saat ini estimasi waktu belajar dihitung dari jumlah butir soal dikalikan rata-rata waktu pengerjaan (~1.8 menit/soal). Jika nanti ada modul timer sesi aktif di backend/storage, metrik ini dapat langsung dihubungkan ke durasi timer pengerjaan aktual per sesi.
