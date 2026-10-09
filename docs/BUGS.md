# Daftar Bug TKA Master

Format status: `[belum selesai]`, `[TIDAK TERVERIFIKASI]`, atau `[sudah diselesaikan pada tanggal X]`.
Setiap bug baru wajib dicatat di sini.

## Bug Aktif

### BUG-001: Progress desktop 0% padahal HP sudah ngisi [belum selesai]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Login pakai akun yang sama (agus putra) di desktop, tapi progress belajar masih 0%. Di HP (mobile) kelihatan sudah pernah ngisi mapel tertentu.
- **Dugaan:** Progress disimpan di localStorage HP saja, tidak sync ke server.
- **Status:** Perlu investigasi & implementasi sync server (Tugas D).

### BUG-002: Login tidak persistent [belum selesai]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Selalu harus login ulang. Setelah logout masuk ke landing page yang nunjukin tombol login Google. Anehnya, kalau sudah pernah login lalu pilih "coba tanpa akun Google", malah masuk ke akun Google.
- **Status:** Perlu reproduksi & investigasi akar masalah (Tugas E).

### BUG-003: Layout Autopsi overflow [belum selesai]
- **Lapor:** Agus, 9 Okt 2026 18:05 WIB
- **Deskripsi:** Section Autopsi di halaman hasil terlalu besar, overflow di desktop & mobile (390x844). Harus zoom out 50% baru kelihatan bagus.
- **Keputusan:** Selesaikan sebelum Gate A (Tugas C).
- **Status:** Dalam antrean pengerjaan.

### BUG-004: URL routing tidak jelas [belum selesai]
- **Lapor:** Agus, 9 Okt 2026 18:32 WIB
- **Deskripsi:** URL tidak pindah-pindah (pakai query param + hash). Susah debug & share link. Minta URL khusus: /app/beranda, /app/modul, /app/soal, dll.
- **Keputusan:** Refactor besar, setelah 26 Okt.
- **Status:** Backlog.

## Bug Selesai

### BUG-009: Kartu Beranda tidak muncul [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Gemini / Agus, 10 Okt 2026
- **Deskripsi:** Kartu Beranda ("Tanggal TKA kamu" dan "Misi hari ini") tidak muncul saat reload / buka ulang. Penyebab: di `app.js` ~baris 361 `window.__homeFirst = !window.location.hash.startsWith('#soal-')`; fungsi `renderQuestion()` menulis `#soal-N` ke URL (baris ~1599), sehingga saat dibuka ulang dengan hash, `window.__homeFirst` bernilai false dan melewati `homeOpen()`, menyebabkan `#hoMain` kosong.
- **Solusi:** Ganti jadi `window.__homeFirst = true;`.
- **Bukti:** Terverifikasi via Chromium headless ukuran HP 390x844 untuk dua URL (`/app` dan `/app?subject=matematika&paket=1#soal-1`), dua-duanya memuat kartu "Tanggal TKA kamu" dan "Misi hari ini".
- **File:** `app.js`
- **Status:** SELESAI-TERVERIFIKASI.

### BUG-005: Overlay Beranda nutupin kuis di desktop [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Ditemukan Muse via browser test, 9 Okt 2026 21:37 WIB
- **Deskripsi:** `#homeOverlay` menutupi seluruh kuis di desktop dan tidak bisa ditutup. Opsi jawaban tidak bisa diklik.
- **Hasil Verifikasi:** SELESAI-TERVERIFIKASI. Diuji via Chromium headless di desktop (1280x800) dan HP (390x844). Saat kartu paket diklik, `homeClose()` menutup `#homeOverlay` (`home-hidden` aktif) dan lembar kuis tampil penuh dengan opsi jawaban yang dapat diklik secara normal.
- **File:** `app.js`

### BUG-006: Opsi jawaban bisa diklik lagi setelah Cek Jawaban [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Setelah klik "Cek Jawaban", opsi masih bisa diklik dan jawaban bisa dicek ulang. Khawatir jawaban pertama ketimpa.
- **Hasil Verifikasi:** SELESAI-TERVERIFIKASI. Diuji di browser headless (390x844). Setelah tombol "Cek Jawaban" diklik, percobaan memilih Opsi B tidak memindahkan pilihan (jawaban tetap terkunci di Opsi A) karena `selectOption()` membaca `window._answerChecked[q.nomor]`.
- **File:** `app.js`

### BUG-007: Teks opsi geser-geser saat logo centang muncul [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Teks opsi berubah-ubah/geser karena logo centang baru muncul (layout shift).
- **Temuan Jujur:** Class `.opt-check` di rule CSS lama sama sekali tidak berefek karena tidak pernah dipakai di HTML `app.js`. Centang sebenarnya dirender via pseudo-element `.option-item.selected::after`. Akibatnya, saat opsi diklik, lebar teks tertekan sebesar -24.25px.
- **Perbaikan Nyata:** Di `style.css`, rule `.option-item::after` diberi `visibility: hidden;` secara permanen sehingga ruang centang sudah di-reserve sejak awal. Saat `.selected`, hanya diubah menjadi `visibility: visible`.
- **Hasil Verifikasi:** SELESAI-TERVERIFIKASI. Pengukuran DOM membuktikan pergeseran posisi X = 0px dan perubahan lebar teks = 0.0px (0 layout shift).
- **File:** `style.css`

### BUG-008: Popup mobile terlalu besar [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Popup di mobile terlalu besar dan menghalangi. Desktop oke.
- **Hasil Verifikasi:** SELESAI-TERVERIFIKASI. Diuji di viewport HP (390x844). Rule media query membatasi lebar modal maksimal 358px (`calc(100vw - 32px)`). Baik Modal Daftar Soal (358x673px) maupun Modal Konfirmasi Selesai (358x356px) tampil rapi tanpa overflow horizontal maupun vertikal (`overflowsX: false`, `overflowsY: false`).
- **File:** `style.css`
