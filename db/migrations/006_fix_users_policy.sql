-- ============================================================
-- PERBAIKAN: Izinkan INSERT di tabel public.users & Backfill
-- Masalah: Kode login di klien (supabase_auth.js) memanggil upsert,
-- tetapi tabel public.users tidak punya policy INSERT (hanya SELECT/UPDATE).
-- Akibatnya, user baru gagal disimpan dan tabel kosong (count = 0).
-- ============================================================

-- 1. Aktifkan RLS jika belum aktif
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- 2. Buat / perbarui policy INSERT agar user bisa menambahkan datanya sendiri
DROP POLICY IF EXISTS "users_insert" ON public.users;
CREATE POLICY "users_insert" ON public.users
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- 3. Buat / perbarui policy UPDATE agar user bisa mengupdate datanya sendiri
DROP POLICY IF EXISTS "users_update" ON public.users;
CREATE POLICY "users_update" ON public.users
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- 4. Buat / perbarui policy SELECT agar user bisa membaca datanya sendiri
DROP POLICY IF EXISTS "users_select" ON public.users;
CREATE POLICY "users_select" ON public.users
  FOR SELECT
  USING (auth.uid() = id);

-- 5. SINKRONISASI OTOMATIS (Backfill):
-- Masukkan user Google yang sudah terdaftar di auth.users ke public.users
INSERT INTO public.users (id, email, name, avatar_url, last_login_at)
SELECT
  au.id,
  au.email,
  COALESCE(au.raw_user_meta_data->>'full_name', au.email) AS name,
  au.raw_user_meta_data->>'avatar_url' AS avatar_url,
  COALESCE(au.last_sign_in_at, now()) AS last_login_at
FROM auth.users au
ON CONFLICT (id) DO UPDATE SET
  email = EXCLUDED.email,
  name = EXCLUDED.name,
  avatar_url = EXCLUDED.avatar_url,
  last_login_at = EXCLUDED.last_login_at;
