-- ============================================================
-- Migrasi 009: Tabel Payments & Kolom Pass_Expires_At (Sprint Pass)
-- Produk: Sprint Pass musse Rp14.900 (Akses sampai hari ujian TKA)
-- Catatan: Dijalankan oleh admin/Agus di Supabase SQL Editor.
-- Idempoten [aman dijalankan ulang tanpa merusak data].
-- ============================================================

-- 1. Tambah kolom pass_expires_at di tabel public.users
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS pass_expires_at TIMESTAMPTZ;

-- 2. Buat tabel public.payments untuk mencatat riwayat transaksi Midtrans
CREATE TABLE IF NOT EXISTS public.payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id TEXT UNIQUE NOT NULL,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  tka_date DATE NOT NULL,
  amount INT NOT NULL DEFAULT 14900,
  status TEXT NOT NULL DEFAULT 'pending',
  payment_url TEXT,
  paid_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Indeks untuk kecepatan pencarian transaksi
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON public.payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON public.payments(status);

-- 4. Keamanan Row Level Security (RLS)
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- User hanya dapat membaca transaksi miliknya sendiri
DROP POLICY IF EXISTS "payments_select_owner" ON public.payments;
CREATE POLICY "payments_select_owner" ON public.payments
  FOR SELECT
  USING (auth.uid() = user_id);

-- User dapat menyisipkan order pembayarannya sendiri
DROP POLICY IF EXISTS "payments_insert_owner" ON public.payments;
CREATE POLICY "payments_insert_owner" ON public.payments
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Service role Supabase (backend) otomatis memiliki akses penuh (bypass RLS)
-- untuk update status settlement dari webhook Midtrans.
