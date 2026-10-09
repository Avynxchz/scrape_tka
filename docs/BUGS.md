# Daftar Bug TKA Master

Format status: `[belum selesai]` atau `[sudah diselesaikan pada tanggal X]`.
Setiap bug baru wajib dicatat di sini.

## Bug Aktif

### BUG-001: Progress desktop 0% padahal HP sudah ngisi [belum selesai]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Login pakai akun yang sama (agus putra) di desktop, tapi progress belajar masih 0%. Di HP (mobile) kelihatan sudah pernah ngisi mapel tertentu.
- **Dugaan:** Progress disimpan di localStorage HP saja, tidak sync ke server.
- **Status:** Perlu investigasi.

### BUG-002: Login tidak persistent [belum selesai]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Selalu harus login ulang. Setelah logout masuk ke landing page yang nunjukin tombol login Google. Anehnya, kalau sudah pernah login lalu pilih "coba tanpa akun Google", malah masuk ke akun Google.
- **Status:** Perlu investigasi.

### BUG-003: Layout Autopsi overflow [belum selesai]
- **Lapor:** Agus, 9 Okt 2026 18:05 WIB
- **Deskripsi:** Section Autopsi di halaman hasil terlalu besar, overflow di desktop & mobile. Harus zoom out 50% baru kelihatan bagus.
- **Keputusan:** Diperbaiki setelah Gate A.
- **Status:** Backlog.

### BUG-004: URL routing tidak jelas [belum selesai]
- **Lapor:** Agus, 9 Okt 2026 18:32 WIB
- **Deskripsi:** URL tidak pindah-pindah (pakai query param + hash). Susah debug & share link. Minta URL khusus: /app/beranda, /app/modul, /app/soal, dll.
- **Keputusan:** Refactor besar, setelah 26 Okt.
- **Status:** Backlog.

## Bug Selesai

### BUG-005: Overlay Beranda nutupin kuis di desktop [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Ditemukan Muse via browser test, 9 Okt 2026 21:37 WIB
- **Deskripsi:** `#homeOverlay` menutupi seluruh kuis di desktop dan tidak bisa ditutup (tidak ada tombol ×). Opsi jawaban tidak bisa diklik.
- **Fix:** Auto-close overlay jika URL mengandung `?subject=`.
- **File:** app.js
- **Status:** Menunggu upload manual Agus.

### BUG-006: Opsi jawaban bisa diklik lagi setelah Cek Jawaban [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Setelah klik "Cek Jawaban", opsi masih bisa diklik dan jawaban bisa dicek ulang. Khawatir jawaban pertama ketimpa.
- **Fix:** Kunci opsi via `window._answerChecked[nomor]` — `selectOption()` return early jika sudah dicek.
- **File:** app.js
- **Status:** Menunggu upload manual Agus.

### BUG-007: Teks opsi geser-geser saat logo centang muncul [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Teks opsi berubah-ubah/geser karena logo centang baru muncul (layout shift).
- **Fix:** CSS `.opt-check` selalu reserve space 24px (visibility hidden saat tidak aktif).
- **File:** style.css
- **Status:** Menunggu upload manual Agus.

### BUG-008: Popup mobile terlalu besar [sudah diselesaikan pada 10 Okt 2026]
- **Lapor:** Agus, 10 Okt 2026 01:26 WIB
- **Deskripsi:** Popup di mobile terlalu besar dan menghalangi. Desktop oke.
- **Fix:** CSS media query max-width 640px — batasi ukuran popup.
- **File:** style.css
- **Status:** Menunggu upload manual Agus.
