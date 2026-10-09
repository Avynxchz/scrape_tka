# HANDOFF — TKA Master Fase 0-5 untuk Gemini 3.8 Flash

**Tanggal:** 10 Okt 2026
**Repo:** https://github.com/Avynxchz/scrape_tka
**Branch kerja:** `dev` (JANGAN sentuh `main` — masih di `3605aab`, tunggu Agus bilang "MERGE")
**Preview:** https://tka-master-preview.up.railway.app
**Dokumen acuan:** `docs/01_BRIEF_MUSE.md`, `docs/02_LAMPIRAN_MUSE.md`, `docs/STATUS.md`, `docs/BUGS.md`

## Aturan Tetap Agus
- Bahasa SANGAT sederhana. Setiap istilah teknis langsung kasih arti dalam kurung. Contoh: `JWT [bukti identitas login]`.
- Jangan tulis "selesai/fixed" tanpa bukti nyata (screenshot, output tes, atau verifikasi browser).
- Semua yang belum diuji = label **TIDAK TERVERIFIKASI**.
- Satu tugas kecil = satu commit kecil. Tidak ada refactor tak terkait.
- Push ke `dev` boleh. `main` dilarang tanpa "MERGE".
- Maksimal 3x percobaan push per fase, lalu laporkan error persis dan berhenti.
- Jangan commit rahasia/data pribadi.
- File `app.js` (~237KB) dan `style.css` (~153KB) TIDAK BISA di-push via API (kegedean). Harus via upload manual oleh Agus lewat GitHub web. File kecil (server.py, dll.) bisa via API.
- Agus non-programmer, ngetes dari HP Android. Instruksi harus 1 langkah klik-per-klik, browser-first.

---

## STATUS FASE

### Fase 0: 85%
**Sudah:** docs/, feature_flags.py, GET /api/flags, branch dev, backup.
**Kurang:**
- Flag runtime masih pakai SQLite di Railway (ephemeral [hilang tiap deploy]). Harusnya pindah ke Supabase.
- Backup belum terkonfirmasi penuh.

### Fase 1: 90%
**Sudah:** docs/AUDIT.md (8A + 6B + 4C).
**Kurang:** Minor, tidak kritis.

### Fase 2: 60%
**Sudah:**
- T2.1: Gzip aset statis (app.js 220KB → 57KB).
- T2.5/T2.7: Landing page jujur (tidak ada klaim palsu).
- T2.11: Verifikasi JWT Supabase di server (auth_verify.py, AUTH_VERIFY default OFF).
- T2.4 (kuota): Terverifikasi live.
**Kurang:**
- T2.4: Kuota TIDAK kepotong kalau pengiriman AI gagal (sinyal jelek). Saat ini kepotong.
- T2.6: Tombol "Lapor bug" untuk user. Belum ada.
- T2.10: Keputusan provider AI berbayar vs multi-key gratis. Menunggu keputusan Agus.
- Error monitoring & beberapa tugas performa belum terbukti.

### Fase 3: 70%
**Sudah:**
- T3.1: Tabel `attempts` di Supabase + migrasi 004 (idempotency via client_attempt_id).
- T3.2: AttemptRecorder (rekam per soal: jawaban pertama/terakhir, waktu aktif, Ragu-ragu, kunjungan).
- T3.3: Upload attempt + badge "✓ Hasil tersimpan di akunmu".
- T3.6: Konsen perekaman (modal + privacy.html).
- Bugfix: login (2.1), items+idempotency (2.2), CSS (2.3/2.4).
**Kurang:**
- T3.4: Tamu-claim — hasil tryout sebagai tamu bisa diklaim setelah login.
- T3.5 (ASLI): Pemulihan setelah refresh/tab ditutup lalu lanjut. (Catatan: yang dulu disebut "T3.5 terverifikasi" itu sebenarnya T3.3 — upload berhasil. T3.5 asli belum dites.)
- Offline→online: antrean offline kekirim pas online lagi.
- T3.8: Taksonomi — label topik per soal.
- Bukti manual idempotency (kirim payload sama 2x → tepat 1 baris).
- **BUG-001:** Progress (tka_progress) cuma di localStorage, tidak sync antar device. Perlu kolom `progress` JSONB di tabel `users` + endpoint sync.
- **BUG-002:** Login tidak persistent. Fix parsial sudah di-push (logout bersihkan key). Perlu verifikasi.

### Fase 4: 100%
**Sudah:** `autopsy/analyzer.py`, `autopsy/planner.py`, `config/exam.json`, `config/analyzer.json`. Tes: 20/20 lulus.

### Fase 5: 95%
**Sudah:**
- T5.1: `POST /api/autopsy/analyze` + tampil di hasil (kebocoran #1 terbuka, #2-3 blur). Terverifikasi via screenshot.
- T5.2: Kartu "Misi hari ini" di Beranda (mobile + desktop). Terverifikasi via browser.
- T5.3: Date picker tanggal TKA + hitung mundur H-n. Terverifikasi via browser.
- T5.4: `/admin/autopsi` + `/api/admin/autopsy_full` (mode demo). Kode selesai, BELUM dites pakai attempt nyata.
- T5.5: Ringan, tanpa library baru.
**Kurang:**
- T5.4 belum diuji end-to-end (butuh admin key dari Agus).
- Layout Autopsi overflow (masuk backlog, perbaiki setelah Gate A).

---

## DAFTAR BUG (docs/BUGS.md)

**[belum selesai]:**
- BUG-001: Progress desktop 0% (perlu sync server)
- BUG-002: Login tidak persistent (fix parsial pushed, perlu verifikasi)
- BUG-003: Layout Autopsi overflow (setelah Gate A)
- BUG-004: URL routing (setelah 26 Okt)

**[sudah diselesaikan pada 10 Okt 2026]:**
- BUG-005: Overlay nutupin kuis desktop → auto-close jika ?subject=
- BUG-006: Opsi diklik setelah cek → kunci via _answerChecked
- BUG-007: Teks geser centang → CSS reserve space
- BUG-008: Popup mobile besar → CSS media query

---

## TUGAS SELANJUTNYA (prioritas)

1. **Verifikasi BUG-005 s/d BUG-008** — Agus sudah upload app.js + style.css. Cek via browser apakah overlay auto-close, opsi terkunci, teks tidak geser, popup mobile pas.
2. **BUG-001 (progress sync):**
   - Agus jalankan SQL: `db/migrations/005_progress_sync.sql` (tambah kolom `progress` JSONB di `users`).
   - Buat endpoint `GET/POST /api/user/progress` di server.py.
   - Update app.js: sync `tka_progress` ke server saat login + saat ada perubahan (debounce).
3. **BUG-002 (login):** Verifikasi fix logout. Jika masih bermasalah, investigasi session restore.
4. **T3.4, T3.5, T3.8, offline→online** — tugas Fase 3 yang belum.
5. **T2.4, T2.6** — tugas Fase 2 yang belum.
6. **Gate A:** Agus tunjukkan Autopsi ke 5 orang asing, target ≥3 bilang "iya bener". JANGAN lanjut Fase 6 sebelum ini lolos.

---

## CONTOH PROMPT CLAUDE (untuk referensi gaya instruksi)

Claude biasanya kasih instruksi seperti ini:

> "Audit ulang Fase 0-4. Jangan percaya laporan lama. Baca docs/01_BRIEF_MUSE.md, cek setiap tugas di brief, verifikasi dengan bukti nyata (bukan klaim). Laporkan persentase per fase dengan bukti."

> "Mulai Fase 5 (T5.1 dan T5.4 dulu). T5.1: endpoint /api/autopsy/analyze yang terima attempt data dan kembalikan hasil analyzer (preview: kebocoran #1 lengkap). T5.4: halaman /admin/autopsi untuk demo."

> "Cari akar masalah upload attempt gagal. Reproduksi dulu, jangan asal tebak. Cek rantai: browser → server → Supabase."

Gaya Claude: selalu minta bukti, selalu suruh reproduksi dulu sebelum fix, tidak percaya klaim tanpa verifikasi.
