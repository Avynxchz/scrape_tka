# Laporan FASE 5 — Layar Autopsi (preview gratis) + Misi hari ini + mode demo

Tanggal: 2026-10-09
Branch: `dev`
Status: **SELESAI** (menunggu Gate A dari Agus)

## Ringkasan
Fase 5 mengimplementasikan layar Autopsi pasca-tryout (preview gratis), kartu "Misi hari ini", date picker tanggal TKA dengan hitung mundur, dan mode demo admin untuk Gate A.

## Tugas

### T5.1 — Halaman hasil: Autopsi preview ✅
- **Server:** `POST /api/autopsy/analyze` — terima data attempt (items, n_questions, duration_limit_s, ended_by), jalankan `autopsy/analyzer.py`, kembalikan preview (kebocoran #1 lengkap, #2-3 hanya label terkunci). Butuh login (JWT).
- **Frontend:** `renderAutopsiSection()` di `app.js` — dipanggil setelah `renderReviewHasil()`, fetch ke endpoint, tampilkan:
  - Kebocoran #1 terbuka lengkap (label, bukti, contoh soal, tombol "Pelajari").
  - Kebocoran #2-3 di-blur dengan overlay "🔒 Buka dengan Paket Sprint".
  - Indikator "data tipis" jika data kurang.
- **Bukti:** Screenshot user 2026-10-09 18:05 WIB — Autopsi muncul dengan benar.
- **Catatan:** Layout terlalu besar (overflow di desktop & mobile). Agus minta diperbaiki nanti (masuk backlog).

### T5.2 — Kartu "Misi hari ini" di Beranda ✅
- **Mobile** (`app.js` → `getTkaCardsHtml()`): kartu kuning di atas daftar mapel, isi dari `localStorage.tka_last_autopsy` (kebocoran #1 terakhir). Jika belum ada: "Kerjakan 1 tryout untuk membuka misi harianmu."
- **Desktop** (`home_desktop.html`): script inject kartu yang sama sebelum filter mapel.
- **Bukti:** Verifikasi browser 2026-10-09 — kartu muncul di DOM mobile & visual desktop.

### T5.3 — Date picker "Tanggal TKA kamu?" + hitung mundur ✅
- **Mobile/Desktop:** kartu hijau gradient dengan "H-n" (misal H-17) + `<input type="date" min="2026-10-26" max="2026-11-29">`.
- Default: 2026-10-26. Tersimpan di `localStorage.tka_date`.
- **Server:** `POST /api/user/tka_date` — simpan ke Supabase `users.tka_date` (best effort, tidak blokir UI).
- Catatan "Tanyakan jadwal ke sekolahmu jika ragu."
- **Bukti:** Verifikasi browser 2026-10-09 — kartu muncul dengan H-17.

### T5.4 — Mode demo admin ✅
- **Halaman:** `GET /admin/autopsi?key=VISITOR_ADMIN_KEY` — form input attempt_id.
- **API:** `GET /api/admin/autopsy_full?key=...&attempt_id=...` — ambil attempt dari Supabase (service key), jalankan analyzer penuh, kembalikan semua kebocoran + skor.
- **Fitur:** "Lihat Autopsi Penuh" (bypass pass untuk demo) + "Salin Teks untuk WA" (format ringkas untuk Gate A).
- **Status:** Kode selesai, belum diuji dengan attempt nyata (butuh admin key dari Agus).

### T5.5 — Ringan ✅
- Tidak ada library baru. Tidak ada animasi berat. Inline styles saja.
- Bahasa: "Terburu-buru", "Overthinking", dll. — perilaku, bukan sifat.

## Bug yang diperbaiki selama Fase 5
1. **Syntax error** di `app.js` (kutip tunggal ganda di `onclick="alert('...')"`). Terdeteksi via `node --check`. Pelajaran: selalu cek sintaks sebelum kirim file ke Agus.
2. **Kartu ketimpa `innerHTML`**: `renderHome()` memanggil `main.innerHTML = ...` setelah prepend kartu. Diperbaiki: kartu jadi bagian dari string innerHTML.
3. **Kartu tidak muncul di desktop**: homepage desktop pakai `home_desktop.html` terpisah (iframe), bukan `renderHome()`. Ditambahkan script inject terpisah.

## File yang diubah
- `server.py`: `/api/autopsy/analyze`, `/api/user/tka_date`, `/admin/autopsi`, `/api/admin/autopsy_full`.
- `app.js`: `getTkaCardsHtml()`, `renderAutopsiSection()`, `window._lastFinishedAttempt`.
- `home_desktop.html`: script inject kartu T5.2/T5.3.
- `docs/BACKLOG.md`: URL routing jelas (usulan Agus).

## Yang belum (masuk Gate A / backlog)
- **Gate A:** Tunjukkan Autopsi ke 5 orang asing. Target: minimal 3 berkata "iya bener".
- **Layout Autopsi:** Terlalu besar, overflow di desktop & mobile. Perbaiki setelah Gate A.
- **T5.4 belum diuji** dengan attempt nyata (butuh admin key).

## Keputusan
Fase 5 SELESAI. **Tunggu Gate A dari Agus** sebelum lanjut ke Fase 6 (paywall).
