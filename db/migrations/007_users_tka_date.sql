-- Migrasi 007: Tambah kolom tka_date di tabel public.users untuk menyimpan tanggal ujian siswa
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS tka_date date;
