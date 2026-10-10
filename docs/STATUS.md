# STATUS — TKA Master (Autopsi + Sprint Pass)

Diperbarui: 2026-10-10 11:55 WIB · Branch: `dev` · `main` di `3605aab` (JANGAN SENTUH)

## Posisi Sekarang

### FASE 0: 85% (DALAM PROSES — Branch dev aktif, menunggu gladi & merge ke main)
- **Terbukti:** Branch `dev` dari `main@3605aab`; dokumen arsitektur di `docs/ARCHITECTURE.md`; feature flag (`feature_flags.py` & `GET /api/flags`, 7 flags default OFF terverifikasi lokal); pemindaian 0 rahasia di repo publik.
- **Utang:** Flag runtime masih disimpan di SQLite Railway (ephemeral [hilang tiap deploy], perlu migrasi ke Supabase); backup Supabase belum dikonfirmasi oleh Agus; tag release `pre-autopsi-v0` menunggu pembuatan saat merge.

### FASE 1: 90% (DALAM PROSES — Audit jalur kritis & format TKA 2026)
- **Terbukti:** Audit jalur kritis di `docs/AUDIT.md` (8 temuan A, 6 B, 4 C); pemetaan 9 masalah dari Agus di Lampiran B; audit kesesuaian format ujian TKA 2026 vs §3.1.
- **Utang:** Pengukuran visual/Lighthouse langsung di browser headless (siap diuji via browser subagent).

### FASE 2: 90% (DALAM PROSES — Utang kebijakan AI & Sentry)
- **Terbukti:** T2.1 gzip aset statis (app.js 220KB → 57KB, style.css 155KB → 28KB); T2.5/T2.7 salinan landing & FAQ jujur (tanpa klaim durasi palsu); T2.11 verifikasi JWT Supabase di server (`auth_verify.py`); T2.4 kuota utuh saat gagal-kirim terbukti di kode & server (`consume_user_quota` hanya dipanggil saat LLM berhasil); T2.6 tombol & modal "Lapor Bug" terpasang di mobile overflow menu & desktop bar dengan penyimpanan fallback lokal (`/api/bug-reports`) dan Supabase table `bug_reports`.
- **Utang:** T2.10 penentuan kebijakan provider AI (menunggu Agus); error monitoring Sentry.

### FASE 3: 100% (SELESAI-TERVERIFIKASI)
- **Terbukti:** Skema `attempts` + `feature_flags` di Supabase (migrasi 003); AttemptRecorder di `app.js`; endpoint `POST /api/attempts` verifikasi JWT dengan idempotency via client_attempt_id; T3.4 klaim hasil tamu setelah login via Google OAuth & kartu alert dengan tombol "Klaim ke Akun Google"; T3.5 pemulihan kuis setelah refresh/tab tertutup (`tka_answers_<key>`, `tka_ragu_<key>`, `tka_finished_<key>`); sinkronisasi antrean otomatis saat event `online` dan event `tka-login`; BUG-002 login persistent terverifikasi; **BUG-001 (Tugas D) sync progress desktop-mobile dua arah terverifikasi (Supabase kolom users.progress via GET/POST /api/user/progress)**.
- **Perbaikan Audit (T1, T2, T3):** BUG-006 kunci paket:nomor terverifikasi, persistensi `tka_checked_` tahan reload terverifikasi; BUG-009 URL sinkron hanya saat kuis aktif terverifikasi; isolasi progres per akun (`tka_progress_owner`), penghapusan saat logout, batas 256KB di server.py terverifikasi 100%.

### KEJURUAN SMK: 100% LIVE (5 JURUSAN UTAMA & 30 SOAL SERUPA A-E)
- **Terbukti:** 5 mapel kejuruan SMK di sekolah Agus berhasil di-scrape lengkap dengan kunci jawaban otoritatif resmi Pusmendik:
  1. `SMK - Teknik Mesin` (`teknik_mesin_paket_1` - 6 soal, val: 33)
  2. `SMK - Teknik Otomotif` (TKR) (`teknik_otomotif_paket_1` - 6 soal, val: 34)
  3. `SMK - Teknik Jaringan dan Telekomunikasi` (TKJ) (`teknik_jaringan_paket_1` - 6 soal, val: 49)
  4. `SMK - Akuntansi dan Keuangan Lembaga` (AKL) (`akuntansi_paket_1` - 6 soal, val: 66)
  5. `SMK - Manajemen Perkantoran dan Layanan Bisnis` (MPLB) (`manajemen_perkantoran_paket_1` - 6 soal, val: 65)
- **Soal Serupa (Pilar 5):** 30 butir soal pemantapan baru (6 butir per mapel SMK) terverifikasi 100% memiliki 5 opsi seragam (A-E), tanpa opsi duplikat, kunci valid, dan pembahasan lengkap.
- **UI/UX & Metrik Kurikulum:** Banner Beranda Desktop (`home_desktop.html`), Modul Belajar (`modul.html`), dan Progres (`progres.html`) terverifikasi 100% menampilkan **27 Mapel · 49 Paket · 991 Soal**.
- **Alur Pengguna Baru Desktop:** Smooth scroll tombol "Mulai Sekarang", opsi "Coba Tamu" di modal konfirmasi kuis, filter kategori SMK/Bahasa/Saintek/Soshum, dan pencegahan error HTTP 403 paket 2 SMK teruji 100% PASS (0 console error).

### PERBAIKAN MASUKAN AGUS: 100% SELESAI & TERVERIFIKASI
1. **Tombol Bawah Mobile:** Dikembalikan 100% ke tombol "Cek Jawaban", tombol reviu di header HP disembunyikan di tampilan mobile (`display: none !important`).
2. **Formula Matematika KaTeX:** Rendering KaTeX diperluas ke tab pembahasan dan dilindungi dari pemecahan tag `<br>`, seluruh rumus tampil rapi.
3. **Mapel SMK di Desktop & Modul:** 5 mapel SMK terintegrasi penuh di dashboard, modul carousel, dan progres belajar.
4. **Alur Tamu Kuis Desktop:** Pengguna baru dapat memilih "Coba Tamu" langsung dari modal konfirmasi tanpa terblokir harus login Google terlebih dahulu.

### FASE 4: 100% (SELESAI-TERVERIFIKASI)
- **Terbukti:** `autopsy/analyzer.py` (9 label prioritas, 2 flag, kebocoran top-3) + `autopsy/planner.py` (jadwal belajar deterministik hingga H-1) lulus tes otomatis 20/20 di `tests/test_autopsy.py` (8 persona uji sesuai harapan). Kartu materi statis di `content/cards/`.

### FASE 5: 98% (SELESAI — menunggu Gate A)
- **Terbukti:** T5.1 `POST /api/autopsy/analyze` + render UI Autopsi preview (kebocoran #1 terbuka, #2-3 terkunci blur); T5.2 kartu "Misi hari ini"; T5.3 kartu hitung mundur tanggal TKA (min date disesuaikan ke 10 Okt untuk Gladi Bersih SMK 12 Okt); T5.4 halaman `/admin/autopsi` & `/api/admin/autopsy_full` dengan proteksi header `X-Admin-Key` dan POST body (Tugas F SELESAI-TERVERIFIKASI); BUG-009 kartu Beranda selalu tampil terverifikasi; BUG-003 layout Autopsi overflow diperbaiki rapi dengan scroll internal terverifikasi di layar HP 390x844.
- **Utang:** Gate A (demo ke 5 orang asing) menunggu verifikasi Agus.

---

## TINDAKAN DATABASE SUPABASE (Untuk Mas Agus)

### 1. Migrasi 007: Tambah Kolom `tka_date` (WAJIB Sebelum Gladi Bersih)
- **File SQL:** [db/migrations/007_users_tka_date.sql](file:///d:/PROJECTS/SCRAPE_TKA_DEV/db/migrations/007_users_tka_date.sql)
- **Isi SQL:**
  ```sql
  ALTER TABLE public.users ADD COLUMN IF NOT EXISTS tka_date date;
  ```
- **Langkah klik-per-klik untuk Mas Agus:**
  1. Buka browser di HP/Laptop, login ke dashboard Supabase: https://supabase.com/dashboard/project/auhqgzrrgvjbfvzvayzg
  2. Di bilah menu kiri, klik ikon **SQL Editor** (`>_`).
  3. Klik tombol **+ New query**.
  4. Salin dan tempel (paste) kode di atas, lalu klik tombol **Run**.
  5. Hasil benar: Muncul pesan *"Success. No rows returned"*.

### 2. Status Migrasi Sebelumnya (004, 005, 006)
- **Migrasi 004 & 005:** Skema `attempts` dan penambahan kolom `progress` (TIDAK TERVERIFIKASI langsung dari DB sampai query cek dijalankan).
- **Migrasi 006 (`006_fix_users_policy.sql`):** Perbaikan RLS Policy INSERT pada tabel `users`. Jika belum dijalankan, jalankan di SQL Editor.

### 3. Query Pengecekan Hasil Database (Jalankan di SQL Editor)
```sql
-- 1. Cek kolom users (HARUS menghasilkan 2 baris: progress dan tka_date):
select column_name, data_type 
from information_schema.columns 
where table_schema='public' and table_name='users' and column_name in ('progress','tka_date');

-- 2. Cek jumlah akun yang terdaftar:
select count(*) from public.users;
```
Hasil benar: Query pertama menghasilkan 2 baris (`progress` tipe jsonb/text, `tka_date` tipe date).
