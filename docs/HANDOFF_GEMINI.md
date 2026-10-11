# HANDOFF — TKA Master Fase 0-5 untuk Antigravity + Gemini

> [!WARNING]
> **DOKUMEN INI USANG (HISTORIS)** — Rujukan status proyek terkini yang berlaku adalah [docs/STATUS.md](file:///d:/PROJECTS/SCRAPE_TKA_DEV/docs/STATUS.md). Seluruh bug BUG-001 hingga BUG-009 dan Fase 0-5 telah diperbarui sesuai audit 10 Okt 2026.

**Tanggal:** 10 Okt 2026
**Repo:** https://github.com/Avynxchz/scrape_tka
**Branch kerja:** `dev` (JANGAN sentuh `main` — masih di `3605aab`, tunggu Agus bilang "MERGE")
**Preview:** https://tka-master-preview.up.railway.app
**Dokumen acuan:** `docs/01_BRIEF_MUSE.md`, `docs/02_LAMPIRAN_MUSE.md`, `docs/STATUS.md`, `docs/BUGS.md`

## Konteks Transisi
Agus pindah dari Muse ke Antigravity + Gemini sebagai engineer utama proyek.

## Aturan Tetap Agus
- Bahasa SANGAT sederhana. Setiap istilah teknis langsung kasih arti dalam kurung. Contoh: `JWT [bukti identitas login]`.
- Jangan tulis "selesai/fixed" tanpa bukti nyata (screenshot, output tes, atau verifikasi browser).
- Semua yang belum diuji = label **TIDAK TERVERIFIKASI**.
- Satu tugas kecil = satu commit kecil. Tidak ada refactor tak terkait.
- Push ke `dev` boleh. `main` dilarang tanpa "MERGE".
- Maksimal 3x percobaan push per fase, lalu laporkan error persis dan berhenti.
- Jangan commit rahasia/data pribadi.
- Git push langsung dibolehkan, termasuk `app.js` dan `style.css`. Aturan lama upload manual sudah TIDAK berlaku.
- Agus non-programmer, ngetes dari HP Android. Instruksi harus 1 langkah klik-per-klik, browser-first.

---

## STATUS FASE

### Fase 0: 85%
**Sudah:** docs/, feature_flags.py, GET /api/flags, branch dev, backup.
**Kurang:**
- Flag runtime masih pakai SQLite di Railway (ephemeral [hilang tiap deploy]). Harusnya pindah ke Supabase.
- Backup belum terkonfirmasi penuh oleh Agus.

### Fase 1: 90%
**Sudah:** docs/AUDIT.md (8A + 6B + 4C).
**Kurang:** Minor, tidak kritis.

### Fase 2: 60%
**Sudah:**
- T2.1: Gzip aset statis (app.js 220KB → 57KB).
- T2.5/T2.7: Landing page jujur (tidak ada klaim palsu).
- T2.11: Verifikasi JWT Supabase di server (auth_verify.py, AUTH_VERIFY default OFF).
- T2.4 (kuota): Kode benar (kuota dipotong setelah AI sukses tersimpan di server.py ~baris 1679).
**Kurang:**
- T2.4: Belum diuji untuk skenario gagal-kirim (hanya tes skenario gagal-kirim yang belum).
- T2.6: Tombol "Lapor bug" untuk user di antarmuka kuis. Belum ada.
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
- T3.5 (ASLI): Pemulihan setelah refresh/tab ditutup lalu lanjut.
- Offline→online: antrean offline terkirim saat online kembali.
- T3.8: Taksonomi — label topik per soal.
- Bukti manual idempotency (kirim payload sama 2x → tepat 1 baris).
- **BUG-001:** Progress (tka_progress) cuma di localStorage, tidak sync antar device. Perlu kolom `progress` JSONB di tabel `users` + endpoint sync.
- **BUG-002:** Login tidak persistent. Fix parsial sudah di-push (logout bersihkan key). Perlu verifikasi.

### Fase 4: 100%
**Sudah:** `autopsy/analyzer.py`, `autopsy/planner.py`, `config/exam.json`, `config/analyzer.json`. Tes: 20/20 lulus.

### Fase 5: 75% (diturunkan karena kartu Beranda hilang saat URL berhash)
**Sudah:**
- T5.1: `POST /api/autopsy/analyze` + tampil di hasil (kebocoran #1 terbuka, #2-3 blur). Terverifikasi via screenshot.
- T5.2: Kartu "Misi hari ini" di Beranda (mobile + desktop).
- T5.3: Date picker tanggal TKA + hitung mundur H-n.
- T5.4: `/admin/autopsi` + `/api/admin/autopsy_full` (mode demo). Kode selesai, BELUM dites pakai attempt nyata.
- T5.5: Ringan, tanpa library baru.
**Kurang:**
- BUG-009: Kartu Beranda tidak muncul saat URL memiliki hash `#soal-N` (melewati `homeOpen()`). Status diturunkan sampai terverifikasi beres.
- BUG-003: Layout Autopsi overflow di HP 390x844 (harus zoom out 50% baru rapi).
- T5.4: Belum diuji end-to-end (butuh admin key dari Agus).

---

## DAFTAR BUG (docs/BUGS.md)

**[belum selesai]:**
- BUG-001: Progress desktop 0% (perlu sync server)
- BUG-002: Login tidak persistent (fix parsial pushed, perlu verifikasi)
- BUG-003: Layout Autopsi overflow (perlu diselesaikan sebelum Gate A)
- BUG-004: URL routing (backlog, setelah 26 Okt)
- BUG-009: Kartu Beranda tidak muncul saat URL berhash

**[TIDAK TERVERIFIKASI]:**
- BUG-005: Overlay nutupin kuis desktop
- BUG-006: Opsi diklik setelah cek
- BUG-007: Teks geser centang
- BUG-008: Popup mobile besar

---

## TUGAS SELANJUTNYA (prioritas)

1. **Langkah 0**: Perbaikan dokumentasi (HANDOFF_GEMINI.md, BUGS.md, STATUS.md).
2. **Tugas A (BUG-009)**: Ganti `window.__homeFirst = true;`. Verifikasi kartu Beranda muncul di HP 390x844.
3. **Tugas B**: Verifikasi BUG-005..008 satu per satu di browser headless ukuran HP.
4. **Tugas C (BUG-003)**: Layout Autopsi overflow di HP 390x844 sebelum Gate A.
5. **Tugas D (BUG-001)**: Konfirmasi SQL 004/005, endpoint GET/POST `/api/user/progress` + sync.
6. **Tugas E (BUG-002)**: Investigasi & fix login persistent.
7. **Tugas F (Admin)**: Kunci admin pindah ke header/POST body.
8. **Tugas G**: Utang Fase 3 dan 2 (T3.4, T3.5, offline-online, T2.4 gagal-kirim, T2.6 lapor bug).
9. **Gate A**: Agus tunjukkan Autopsi ke 5 orang asing. JANGAN lanjut Fase 6 sebelum ini lolos.
