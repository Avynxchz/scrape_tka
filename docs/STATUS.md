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

### FASE 5: 100% (SELESAI-TERVERIFIKASI — Sesuai Arahan Claude Sonnet 5.5)
- **Terbukti:** 
  1. T5.1 `POST /api/autopsy/analyze` + render UI Autopsi preview (kebocoran #1 terbuka lengkap dengan bukti berbasis angka, #2-3 terkunci blur CSS halus + ajakan Paket Sprint).
  2. Mode Founder (`founder_mode: true` / admin bypass) membuka autopsi penuh tanpa blur untuk review/demo.
  3. Tombol "📚 Pelajari Strategi" aktif dan membuka Modal Kartu Strategi Belajar (`modalKartuStrategi`, z-index 200) berisi kartu Anti-Ceroboh, Manajemen Waktu, Overthinking, dll. sesuai Lampiran E Claude Sonnet.
  4. Tombol "Buka Pembahasan Soal Ini" langsung melompat ke nomor soal bocor dan membuka tab Pembahasan (Pilar).
  5. T5.2 Kartu "Misi Hari Ini" di Beranda desktop & mobile memiliki tombol aksi interaktif `📖 Pelajari Strategi Misi` dan `🚀 Mulai Latihan Tryout`.
  6. T5.3 Tanggal TKA & hitung mundur H-X di Beranda aktif.
  7. T5.4 Halaman `/admin/autopsi` & `/api/admin/autopsy_full` dengan proteksi `X-Admin-Key` terverifikasi.
  8. Evaluasi PG Kompleks: Skor proporsional (pilih E dari A & E -> 50% benar) + badge biru toska + checkbox kotak.
  9. Evaluasi Benar/Salah: Tabel per baris membandingkan pilihan siswa vs kunci resmi (`✅ Tepat` / `❌ Berbeda`) tanpa warna merah ambigu pada opsi "Salah" yang bernilai tepat.
  10. UI Mobile: Mode adaptif keyboard pada AI Tutor, accordion 5 pilar (Pilar 1 default terbuka), auto-hide navbar modul saat scroll, dan perbaikan ikon Sejarah `history_edu`.
  11. Seluruh 5 bukti visual viewport mobile 390x844 terverifikasi via Playwright audit (`scratch/run_audit_tryout.py` EXIT CODE 0).

### GURU AUTOPSI (FASE A0–A8): 100% (SELESAI-TERVERIFIKASI)
- **Terbukti:** 
  1. **A0:** Rencana kerja dan pre-mortem di `docs/COACH_PLAN.md`, prompt persona di `autopsy/coach_prompt_v1.txt`.
  2. **A1:** Normalisasi `clean_attempt_items()` toleran di `server.py`, perekaman riwayat `jejak` (pilih, ganti, ragu) di `app.js`.
  3. **A2:** Evidence Builder `autopsy/evidence.py` menghasilkan `coach_input_v1` terkompresi (~750 token).
  4. **A3:** Layanan Guru AI `autopsy/coach.py` + endpoint `/api/autopsy/coach` dengan validasi ketat skema 6.3 dan circuit breaker.
  5. **A4/A5:** Template deterministik `autopsy/coach_template.py` + kuota harian database Supabase `autopsy/quota.py` (bebas SQLite).
  6. **A6:** UI Layar Hasil Guru Autopsi mobile-first 390px di `app.js`, paywall & blur OFF, date picker H-n, misi 10 menit, tanya AI per soal.
  7. **A7:** Pengujian 3 persona, uji gagal 6 skenario, uji injeksi prompt, uji otorisasi di `docs/eval/coach_v1.md` dan `tests/test_eval_a7.py` (120/120 tes lulus).
  8. **A8:** Laporan final serah terima dan panduan uji HP mandiri untuk Mas Agus di `reports/COACH-A.md`.

---

## TINDAKAN DATABASE SUPABASE (Untuk Mas Agus)

### 1. Migrasi 008: Tambah Kolom `coach_result` pada tabel `attempts` (Direkomendasikan)
- **File SQL:** [db/migrations/008_attempts_coach_result.sql](file:///d:/PROJECTS/SCRAPE_TKA_DEV/db/migrations/008_attempts_coach_result.sql)
- **Isi SQL:**
  ```sql
  ALTER TABLE public.attempts ADD COLUMN IF NOT EXISTS coach_result jsonb;
  ```
- **Langkah di Supabase:** Buka SQL Editor, paste kode di atas, klik **Run**.

### 2. Migrasi 007: Tambah Kolom `tka_date` (WAJIB Sebelum Gladi Bersih)
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
