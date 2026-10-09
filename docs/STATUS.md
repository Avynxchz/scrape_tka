# STATUS — TKA Master (Autopsi + Sprint Pass)

Diperbarui: 2026-10-10 03:55 WIB · Branch: `dev` · `main` di `3605aab` (JANGAN SENTUH)

## Posisi Sekarang

### FASE 0: 85% (SELESAI-TERVERIFIKASI)
- **Terbukti:** Branch `dev` dari `main@3605aab`; dokumen arsitektur di `docs/ARCHITECTURE.md`; feature flag (`feature_flags.py` & `GET /api/flags`, 7 flags default OFF terverifikasi lokal); pemindaian 0 rahasia di repo publik.
- **Utang:** Flag runtime masih disimpan di SQLite Railway (ephemeral [hilang tiap deploy], perlu migrasi ke Supabase); backup Supabase belum dikonfirmasi oleh Agus; tag release `pre-autopsi-v0` menunggu pembuatan saat merge.

### FASE 1: 90% (SELESAI-TERVERIFIKASI)
- **Terbukti:** Audit jalur kritis di `docs/AUDIT.md` (8 temuan A, 6 B, 4 C); pemetaan 9 masalah dari Agus di Lampiran B; audit kesesuaian format ujian TKA 2026 vs §3.1.
- **Utang:** Pengukuran visual/Lighthouse langsung di browser headless (siap diuji via browser subagent).

### FASE 2: 60% (SEBAGIAN)
- **Terbukti:** T2.1 gzip aset statis (app.js 220KB → 57KB, style.css 155KB → 28KB); T2.5/T2.7 salinan landing & FAQ jujur (tanpa klaim durasi palsu); T2.11 verifikasi JWT Supabase di server (`auth_verify.py`); T2.4 kode benar (kuota dipotong setelah respons AI sukses tersimpan di `server.py` baris 1679-1683).
- **Utang:** T2.4 pengujian skenario gagal-kirim; T2.6 tombol "Lapor bug" di antarmuka kuis; T2.10 penentuan kebijakan provider AI (menunggu Agus); error monitoring.

### FASE 3: 70% (SEBAGIAN)
- **Terbukti:** Skema `attempts` + `feature_flags` di Supabase (migrasi 003); AttemptRecorder di `app.js` (rekam jawaban pertama/akhir, waktu aktif, ragu, ganti pilihan, kunjungan); endpoint `POST /api/attempts` verifikasi JWT dengan idempotency via client_attempt_id (commit `25d09b0`).
- **Utang:** T3.4 klaim hasil tamu setelah login; T3.5 pemulihan tryout setelah refresh/tab tertutup lalu lanjut; sinkronisasi antrean offline saat kembali online; T3.8 pelabelan taksonomi topik per soal; BUG-001 (progress sync desktop-mobile); BUG-002 (login persistent).

### FASE 4: 100% (SELESAI-TERVERIFIKASI)
- **Terbukti:** `autopsy/analyzer.py` (9 label prioritas, 2 flag, kebocoran top-3) + `autopsy/planner.py` (jadwal belajar deterministik hingga H-1) lulus tes otomatis 20/20 di `tests/test_autopsy.py` (8 persona uji sesuai harapan). Kartu materi statis di `content/cards/`.

### FASE 5: 85% (SEBAGIAN)
- **Terbukti:** T5.1 `POST /api/autopsy/analyze` + render UI Autopsi preview (kebocoran #1 terbuka, #2-3 terkunci blur); T5.2 kartu "Misi hari ini"; T5.3 kartu hitung mundur tanggal TKA; T5.4 halaman `/admin/autopsi` & `/api/admin/autopsy_full`; BUG-009 kartu Beranda selalu tampil terverifikasi di viewport HP 390x844 baik di `/app` maupun URL berhash.
- **Utang:** BUG-003: layout Autopsi overflow di layar mobile HP (390x844); T5.4 belum diuji end-to-end dengan attempt riil; Gate A (demo ke 5 orang asing) menunggu verifikasi Agus.

---

## Daftar Bug & Status Verifikasi
- **BUG-001:** Progress desktop 0% (belum selesai — Tugas D).
- **BUG-002:** Login tidak persistent (belum selesai — Tugas E).
- **BUG-003:** Layout Autopsi overflow di HP 390x844 (belum selesai — Tugas C).
- **BUG-004:** URL routing tidak jelas (backlog setelah 26 Okt).
- **BUG-005:** Overlay Beranda nutupin kuis desktop (TIDAK TERVERIFIKASI — Tugas B).
- **BUG-006:** Opsi diklik setelah cek (TIDAK TERVERIFIKASI — Tugas B).
- **BUG-007:** Teks geser centang (TIDAK TERVERIFIKASI — Tugas B).
- **BUG-008:** Popup mobile besar (TIDAK TERVERIFIKASI — Tugas B).
- **BUG-009:** Kartu Beranda tidak muncul (SELESAI-TERVERIFIKASI — Tugas A).

---

## Langkah Berikutnya
1. **Tugas A:** Perbaiki BUG-009 di `app.js` (`window.__homeFirst = true;`), buktikan di browser headless ukuran HP (390x844) dengan URL berhash dan tanpa hash.
2. **Tugas B:** Verifikasi BUG-005..008 satu per satu di browser headless.
3. **Tugas C:** Atasi overflow Autopsi (BUG-003) di resolusi 390x844.
4. **Tugas D:** Konfirmasi migrasi SQL 004/005, selesaikan BUG-001 (sync progress).
5. **Tugas E:** Selesaikan BUG-002 (login persistent).
6. **Tugas F:** Pindahkan admin key dari URL ke header/body.
7. **Tugas G:** Bereskan utang Fase 3 & 2.
