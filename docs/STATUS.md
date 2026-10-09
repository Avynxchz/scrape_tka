# STATUS — TKA Master (Autopsi + Sprint Pass)

Diperbarui: 2026-10-09 17:15 WIB · Branch: `dev` · `main` di `3605aab` (JANGAN SENTUH)

## Posisi sekarang
- FASE 0: SELESAI-TERVERIFIKASI (85%). Laporan: `reports/FASE-0.md`. Utang: T0.9 flag masih di SQLite ephemeral (B8); T0.5 backup belum dikonfirmasi Agus.
- FASE 1: SELESAI-TERVERIFIKASI (90%). Audit: `docs/AUDIT.md` (8A+6B+4C). Laporan: `reports/FASE-1.md`.
- FASE 2: SEBAGIAN (60%). Yang terbukti: T2.1 gzip (app.js 220→57KB), T2.7 copy jujur, T2.11 verifikasi JWT via `/auth/v1/user` (commit `859c7c3`). Belum: T2.2/T2.3 (AI Tutor), T2.4 skenario gagal-kirim, T2.5/T2.6/T2.8/T2.9/T2.10. `sync_user` masih HS256 lama.
- FASE 3: SEBAGIAN (70%). Terbukti: baris masuk Supabase (4 baris, 2026-10-09 16:49 WIB), RLS, perekam klien. Belum terbukti: T3.5 asli (refresh lanjut), waktu vs stopwatch, offline→online, idempotency (server siap commit `25d09b0`, migrasi `004` menunggu Agus jalankan SQL). T3.4 (tamu claim) BELUM. T3.8 (taksonomi) BELUM.
- FASE 4: SELESAI-TERVERIFIKASI (100%). 20/20 tes lulus (2026-10-09). 8 persona sesuai harapan.

## Commit terakhir di dev
- `7b9e440` test: regresi indentasi di _smoke_server.py
- `25d09b0` fix(2.2c): idempotency attempts via client_attempt_id
- `015c9b9` fix(2.1): getFreshToken + refreshTokenNow
- `74ae1e7` + `ec9c4e0` db: migrasi 004 (up/down)
- `859c7c3` fix(auth): indentasi _verify_supabase_token

## Menunggu Agus
1. **Upload 2 file** ke `dev` via GitHub web (Add files via upload): `app.js` dan `style.css` yang sudah diperbaiki (link di laporan). Alasan: file >100KB tidak bisa via API otomatis.
2. **Jalankan SQL migrasi 004** di Supabase SQL Editor (langkah di laporan).
3. **Tes login persistent**: login → tutup tab → buka lagi → harus tetap login.
4. **Screenshot popup** yang dimaksud "terlalu besar" (jika bukan modal review).

## Tugas berikutnya
- Setelah upload + migrasi: verifikasi idempotency (kirim 2x = 1 baris), T3.5 refresh, offline→online.
- Fase 5: MENUNGGU kata "lanjut Fase 5" dari Agus. JANGAN mulai duluan.
