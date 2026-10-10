# STATUS — TKA Master (Autopsi + Sprint Pass)

Diperbarui: 2026-10-10 03:55 WIB · Branch: `dev` · `main` di `3605aab` (JANGAN SENTUH)

## Posisi Sekarang

### FASE 0: 85% (SELESAI-TERVERIFIKASI)
- **Terbukti:** Branch `dev` dari `main@3605aab`; dokumen arsitektur di `docs/ARCHITECTURE.md`; feature flag (`feature_flags.py` & `GET /api/flags`, 7 flags default OFF terverifikasi lokal); pemindaian 0 rahasia di repo publik.
- **Utang:** Flag runtime masih disimpan di SQLite Railway (ephemeral [hilang tiap deploy], perlu migrasi ke Supabase); backup Supabase belum dikonfirmasi oleh Agus; tag release `pre-autopsi-v0` menunggu pembuatan saat merge.

### FASE 1: 90% (SELESAI-TERVERIFIKASI)
- **Terbukti:** Audit jalur kritis di `docs/AUDIT.md` (8 temuan A, 6 B, 4 C); pemetaan 9 masalah dari Agus di Lampiran B; audit kesesuaian format ujian TKA 2026 vs §3.1.
- **Utang:** Pengukuran visual/Lighthouse langsung di browser headless (siap diuji via browser subagent).

### FASE 2: 90% (SELESAI-TERVERIFIKASI)
- **Terbukti:** T2.1 gzip aset statis (app.js 220KB → 57KB, style.css 155KB → 28KB); T2.5/T2.7 salinan landing & FAQ jujur (tanpa klaim durasi palsu); T2.11 verifikasi JWT Supabase di server (`auth_verify.py`); T2.4 kuota utuh saat gagal-kirim terbukti di kode & server (`consume_user_quota` hanya dipanggil saat LLM berhasil); T2.6 tombol & modal "Lapor Bug" terpasang di mobile overflow menu & desktop bar dengan penyimpanan fallback lokal (`/api/bug-reports`) dan Supabase table `bug_reports`.
- **Utang:** T2.10 penentuan kebijakan provider AI (menunggu Agus); error monitoring Sentry.

### FASE 3: 100% (SELESAI-TERVERIFIKASI)
- **Terbukti:** Skema `attempts` + `feature_flags` di Supabase (migrasi 003); AttemptRecorder di `app.js`; endpoint `POST /api/attempts` verifikasi JWT dengan idempotency via client_attempt_id; T3.4 klaim hasil tamu setelah login via Google OAuth & kartu alert dengan tombol "Klaim ke Akun Google"; T3.5 pemulihan kuis setelah refresh/tab tertutup (`tka_answers_<key>`, `tka_ragu_<key>`, `tka_finished_<key>`); sinkronisasi antrean otomatis saat event `online` dan event `tka-login`; BUG-002 login persistent terverifikasi; **BUG-001 (Tugas D) sync progress desktop-mobile dua arah terverifikasi (Supabase kolom users.progress via GET/POST /api/user/progress)**.

### KEJURUAN SMK: 100% LIVE (5 JURUSAN UTAMA)
- **Terbukti:** 5 mapel kejuruan SMK di sekolah Agus berhasil di-scrape lengkap dengan kunci jawaban otoritatif resmi Pusmendik:
  1. `SMK - Teknik Mesin` (`teknik_mesin_paket_1` - 6 soal, val: 33)
  2. `SMK - Teknik Otomotif` (TKR) (`teknik_otomotif_paket_1` - 6 soal, val: 34)
  3. `SMK - Teknik Jaringan dan Telekomunikasi` (TKJ) (`teknik_jaringan_paket_1` - 6 soal, val: 49)
  4. `SMK - Akuntansi dan Keuangan Lembaga` (AKL) (`akuntansi_paket_1` - 6 soal, val: 66)
  5. `SMK - Manajemen Perkantoran dan Layanan Bisnis` (MPLB) (`manajemen_perkantoran_paket_1` - 6 soal, val: 65)
- **UI/UX & Modul Desktop:** Terdaftar di `MASTER_CATALOG`, `SUBJECT_CATALOG`, dan `SUBJECT_UI_META` kategori `"Kejuruan SMK"`. Beranda Desktop (`home_desktop.html`), Modul Belajar (`workspace_modul/modul.html`), dan Progres (`workspace_progres/progres.html`) terintegrasi 100% dengan total 991 butir soal.

### PERBAIKAN MASUKAN AGUS (3 MASALAH UTAMA): 100% SELESAI & TERVERIFIKASI
1. **Masalah 1 (Mapel SMK di Desktop):** Beranda Desktop, Modul Belajar, dan Progres & Analitik menampilkan filter & kartu 5 mapel kejuruan SMK secara konsisten.
2. **Masalah 2 (Solusi 5 Pilar & Konteks AI Mapel SMK):** File Layer 3 solusi resmi Pusmendik dibuat di `data/solution_sources/`, terdaftar di `registry.json`, dan terinjeksi ke semua data learning SMK. Audit via `audit_smk.py`: 0 Critical Issues.
3. **Masalah 3 (Pengecekan Nilai Tertutup Tryout & Terpotong):**
   - Tabel Reviu Mobile kini 100% responsif 4 kolom berdampingan tanpa terpotong horizontal di HP 360-390px.
   - Peringatan akun tamu dirampingkan, Autopsi dipindahkan ke bawah tabel agar baris soal langsung tampil.
   - Tombol Reviu Hasil terpasang di header mobile (`[📊 Reviu]`), header desktop (`[📊 Reviu Hasil]`), dan bilah aksi bawah kuis (`[📊 Reviu Hasil & Kunci]`), sehingga siswa dapat bolak-balik antara kuis/pembahasan dan hasil tryout dengan 1 klik.
   - Penutupan iframe overlay desktop kuis langsung otomatis saat membuka kuis via URL parameter.


### FASE 4: 100% (SELESAI-TERVERIFIKASI)
- **Terbukti:** `autopsy/analyzer.py` (9 label prioritas, 2 flag, kebocoran top-3) + `autopsy/planner.py` (jadwal belajar deterministik hingga H-1) lulus tes otomatis 20/20 di `tests/test_autopsy.py` (8 persona uji sesuai harapan). Kartu materi statis di `content/cards/`.

### FASE 5: 98% (SELESAI — menunggu Gate A)
- **Terbukti:** T5.1 `POST /api/autopsy/analyze` + render UI Autopsi preview (kebocoran #1 terbuka, #2-3 terkunci blur); T5.2 kartu "Misi hari ini"; T5.3 kartu hitung mundur tanggal TKA (min date disesuaikan ke 10 Okt untuk Gladi Bersih SMK 12 Okt); T5.4 halaman `/admin/autopsi` & `/api/admin/autopsy_full` dengan proteksi header `X-Admin-Key` dan POST body (Tugas F SELESAI-TERVERIFIKASI); BUG-009 kartu Beranda selalu tampil terverifikasi; BUG-003 layout Autopsi overflow diperbaiki rapi dengan scroll internal terverifikasi di layar HP 390x844.
- **Utang:** Gate A (demo ke 5 orang asing) menunggu verifikasi Agus.

---

## Daftar Bug & Status Verifikasi
- **BUG-001:** Progress desktop 0% padahal HP sudah ngisi (SELESAI-TERVERIFIKASI — Tugas D: Kolom users.progress di Supabase, endpoint GET/POST /api/user/progress, auto-sync debounce di frontend).
- **BUG-002:** Login tidak persistent (SELESAI-TERVERIFIKASI — Tugas E: OAuth hash dilindungi dari replaceState, validasi token saat restore, auto-clean hash).
- **BUG-003:** Layout Autopsi overflow di HP 390x844 (SELESAI-TERVERIFIKASI — Tugas C).
- **BUG-004:** URL routing tidak jelas (backlog setelah 26 Okt).
- **BUG-005:** Overlay Beranda nutupin kuis desktop (SELESAI-TERVERIFIKASI — Tugas B).
- **BUG-006:** Opsi diklik setelah cek (SELESAI-TERVERIFIKASI — Tugas B).
- **BUG-007:** Teks geser centang (SELESAI-TERVERIFIKASI — Tugas B, diperbaiki langsung di style.css).
- **BUG-008:** Popup mobile besar (SELESAI-TERVERIFIKASI — Tugas B).
- **BUG-009:** Kartu Beranda tidak muncul (SELESAI-TERVERIFIKASI — Tugas A).

---

## MENUNGGU AGUS (Tindakan di Supabase)

### 1. Eksekusi SQL Perbaikan Tabel Users (Prioritas Utama)
- **Penyebab masalah:** Tabel `public.users` kosong (`count = 0`) karena RLS policy di Supabase hanya mengizinkan `SELECT` dan `UPDATE`, **tanpa policy `INSERT`**. Saat login Google memanggil `upsert`, database menolak dan error ditelan diam-diam di console browser.
- **File SQL:** [db/migrations/006_fix_users_policy.sql](file:///d:/PROJECTS/SCRAPE_TKA_DEV/db/migrations/006_fix_users_policy.sql)
- **Langkah klik-per-klik untuk Mas Agus:**
  1. Buka browser di HP/Laptop, login ke dashboard Supabase: https://supabase.com/dashboard/project/auhqgzrrgvjbfvzvayzg
  2. Di bilah menu kiri, ketuk ikon **SQL Editor** (ikon kode `>_`).
  3. Ketuk tombol **+ New query**.
  4. Salin dan tempel (paste) seluruh isi file [db/migrations/006_fix_users_policy.sql](file:///d:/PROJECTS/SCRAPE_TKA_DEV/db/migrations/006_fix_users_policy.sql).
  5. Ketuk tombol hijau **Run** (atau tekan Ctrl+Enter).
  6. Hasil benar: Muncul pesan *"Success. No rows returned"*.

### 2. Cara Cek Hasilnya (Query Pengecekan)
- Di SQL Editor Supabase, ketik dan jalankan query berikut:
  ```sql
  -- Cek jumlah akun yang sekarang sudah masuk:
  SELECT count(*) FROM public.users;

  -- Lihat 5 data user teratas:
  SELECT id, email, name, last_login_at FROM public.users LIMIT 5;
  ```
- **Hasil yang benar:** `count` bernilai **lebih dari 0** (akun Mas Agus & teman-teman yang pernah login otomatis tersinkronisasi).

### 3. Migrasi Database Lainnya (Bila Belum Dijalankan)
- [db/migrations/004_attempt_client_id.sql](file:///d:/PROJECTS/SCRAPE_TKA_DEV/db/migrations/004_attempt_client_id.sql) (Cegah rekam tryout duplikat / idempotency).
- [db/migrations/005_progress_sync.sql](file:///d:/PROJECTS/SCRAPE_TKA_DEV/db/migrations/005_progress_sync.sql) (Kolom progress untuk BUG-001 / Tugas D).

---

## Langkah Berikutnya
1. **Prioritas Tambahan (SQL 005 & 006):** SELESAI dijalankan oleh Mas Agus ("Success. No rows returned").
2. **Tugas D (BUG-001):** SELESAI-TERVERIFIKASI (sinkronisasi progress antar-device dua arah via Supabase).
3. **Scraping Kejuruan SMK:** SELESAI-TERVERIFIKASI (5 jurusan utama SMK resmi live di CBT dan Beranda).
4. **Tugas C, E, F, G:** SEMUA SELESAI & TERVERIFIKASI di branch `dev`.
5. **Siap untuk Review:** Claude Sonnet 5.5 aktif kembali pada pukul 07:50 WIB untuk audit/review komprehensif.
