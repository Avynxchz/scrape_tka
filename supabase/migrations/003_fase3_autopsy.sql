-- ============================================================
-- TKA Master — FASE 3 migrasi Autopsi (T3.1)
-- Jalankan SEKALI di Supabase Dashboard → SQL Editor → New query → Run.
-- Idempoten [aman dijalankan ulang]: tidak akan merusak data yang ada.
-- Estimasi: < 1 menit.
-- ============================================================

-- T3.1.1: tabel attempts (Lampiran A) — riwayat tryout per user.
-- Ditulis oleh server via service_role (melewati RLS otomatis).
CREATE TABLE IF NOT EXISTS attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  mapel TEXT NOT NULL,
  paket INT NOT NULL,
  n_questions INT NOT NULL,
  duration_limit_s INT NOT NULL,
  ended_by TEXT NOT NULL DEFAULT 'user' CHECK (ended_by IN ('user','timer')),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  score INT,
  items JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_attempts_user ON attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_attempts_user_mapel ON attempts(user_id, mapel);
ALTER TABLE attempts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS attempts_owner ON attempts;
CREATE POLICY attempts_owner ON attempts
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- T3.1.2: kolom tka_date — tanggal TKA per user (untuk hitung mundur).
ALTER TABLE users ADD COLUMN IF NOT EXISTS tka_date DATE;

-- T3.1.3: kolom profile_name — nama tampilan (diisi otomatis saat login berikutnya).
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_name TEXT;

-- Tabel feature_flags — pindah dari SQLite ke Supabase (keputusan Agus:
-- data tulis pindah di Fase 3/6). Kode server menyusul di Fase 3;
-- sampai saat itu yang dipakai tetap SQLite (tidak ada perubahan perilaku).
CREATE TABLE IF NOT EXISTS feature_flags (
  name TEXT PRIMARY KEY,
  enabled BOOLEAN NOT NULL DEFAULT FALSE,
  rollout_pct INT NOT NULL DEFAULT 100 CHECK (rollout_pct BETWEEN 0 AND 100),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE feature_flags ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS flags_read ON feature_flags;
CREATE POLICY flags_read ON feature_flags FOR SELECT USING (true);
INSERT INTO feature_flags (name, enabled) VALUES
  ('autopsy_logging', FALSE),
  ('autopsy_preview', FALSE),
  ('autopsy_full', FALSE),
  ('paywall', FALSE),
  ('ai_narrative', FALSE),
  ('referral', FALSE),
  ('wa_notify', FALSE)
ON CONFLICT (name) DO NOTHING;
