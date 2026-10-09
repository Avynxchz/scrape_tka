-- BUG-001: sync progress antar device
-- Jalankan SEKALI di Supabase SQL Editor → Run → Save query.

-- Tambah kolom progress (JSONB) ke tabel users
ALTER TABLE users ADD COLUMN IF NOT EXISTS progress JSONB DEFAULT '{}'::jsonb;

-- Pastikan RLS mengizinkan user update progress miliknya sendiri
-- (policy users_owner sudah ada dari migrasi sebelumnya)
