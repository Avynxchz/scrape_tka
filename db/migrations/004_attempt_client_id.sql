-- Migrasi 004: idempotency untuk attempts (kirim dua kali = satu baris).
-- Menambah client_attempt_id + UNIQUE(user_id, client_attempt_id).
-- Aditif: tidak menghapus data.

-- 1. Tambah kolom (nullable dulu untuk backfill)
alter table attempts add column if not exists client_attempt_id text;

-- 2. Backfill baris lama yang belum punya client_attempt_id
update attempts set client_attempt_id = 'legacy_' || id::text
where client_attempt_id is null;

-- 3. Jadikan NOT NULL setelah backfill
alter table attempts alter column client_attempt_id set not null;

-- 4. Unique constraint per user (idempotency)
do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'attempts_user_client_unique'
  ) then
    alter table attempts
      add constraint attempts_user_client_unique unique (user_id, client_attempt_id);
  end if;
end $$;
