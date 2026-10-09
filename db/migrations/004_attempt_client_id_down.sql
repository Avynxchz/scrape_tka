-- Down untuk 004: batalkan idempotency (aditif, tidak hapus baris).
alter table attempts drop constraint if exists attempts_user_client_unique;
alter table attempts drop column if exists client_attempt_id;
