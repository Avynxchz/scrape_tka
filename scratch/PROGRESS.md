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
| **Fase 6** | Beranda: performa & desain ulang kartu mapel (ikon unik, warna cerah, nama terstandar) | BELUM | Sedang dikerjakan |
| **Fase 7** | Beranda: carousel hijau hero (semua teks putih, hapus hiasan toga/titik, animasi SVG/CSS kanan) | BELUM | Menunggu eksekusi |
| **Fase 8** | Menu Modul: carousel reusable, progress gabungan bersegmen mapel pilihan | BELUM | Menunggu eksekusi (tergantung F5 & F7) |
| **Fase 9** | Menu Progress: fix blinking cards, dashboard analitik belajar, empty state | BELUM | Menunggu eksekusi (tergantung F5) |
| **Fase 10** | QA Akhir: regresi Fase 3-9, 0 console error, verifikasi 360/390/412px & desktop | BELUM | Menunggu eksekusi |

---

## 2. ASUMSI
- **Fase 4**: Durasi threshold long-press ditetapkan 400ms dengan batas toleransi gerakan 10px untuk membedakan antara gestur scroll layar biasa dan gestur pemindahan rail tombol. Posisi snap dibagi menjadi 6 kuadran (top-left, top-right, mid-left, mid-right, bottom-left, bottom-right) dengan safe-area padding agar tidak bertubrukan dengan top bar maupun bottom action bar.
- **Fase 5**:
  - Top bar 4 menu distandarkan ke pola: Logo hijau bulat `school` + TKA Master + sub-label menu (BERANDA / MODUL BELAJAR / PROGRES BELAJAR / AKUN) + avatar bulat di kanan (`person`).
  - Search bar Modul dipindahkan dari top bar ke dalam konten (tepat di bawah carousel dan kategori filter), sehingga top bar tidak janggal/berbeda sendiri.
  - Tombol reset dan badge kuota AI di Progres dipindahkan dari top bar ke baris header konten utama (sejajar dengan judul 'Progres Belajar'), mempertahankan fungsionalitas tanpa merusak keseragaman navbar.
  - Tinggi bottom nav ditetapkan 56px (`h-14`) dengan `pb-[env(safe-area-inset-bottom)]`, menyelesaikan masalah bottom nav yang sebelumnya terlalu menjulang/tinggi (64-72px).

---

## 3. KEPUTUSAN YANG PERLU DITINJAU USER
- Penempatan search bar Modul di dalam area konten di bawah carousel hero (bukan di navbar atas).
- Penempatan tombol reset riwayat dan badge kuota AI di baris judul konten Progres Belajar.

---

## 4. CATATAN TEKNIS
- Baseline Fase 0-3 lulus 11/11 uji otomatis Playwright (`scratch/_tes_fase3.js`).
- Port server lokal: `http://127.0.0.1:8080`.
- Safe area aware (`env(safe-area-inset-*)`) wajib dipertahankan untuk semua floating / pinned element.
