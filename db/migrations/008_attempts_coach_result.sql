-- Migrasi 008: Tambah kolom coach_result ke tabel attempts untuk menyimpan hasil Guru Autopsi AI (A3).
-- Aditif: tidak merusak data yang ada. Aman dijalankan berulang kali.

ALTER TABLE public.attempts ADD COLUMN IF NOT EXISTS coach_result JSONB;
