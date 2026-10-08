# STATUS — TKA Master (Autopsi + Sprint Pass)

Diperbarui: 2026-10-08 19:30 WIB · Branch: `dev` · Fase aktif: **0 SELESAI** (menunggu "lanjut" untuk Fase 1)

## Posisi sekarang
- FASE 0 selesai dan di-push ke `dev` (`b2f9450` docs, `d06381c` arsitektur, `2ef4551` feature flag). Laporan: `reports/FASE-0.md`.
- `main` tetap di `3605aab` (merge PR #35). **Jangan merge ke `main` tanpa kata "MERGE" dari Agus.**
- Tag `pre-autopsi-v0` BELUM dibuat (tidak ada tool untuk membuat tag; Agus perlu buat manual — langkah di `reports/FASE-0.md` §5).

## Tugas berikutnya
- FASE 1: baseline performa + audit jalur kritis (hanya membaca/mengukur, tanpa ubah perilaku).

## Pertanyaan terbuka (butuh Agus)
1. Backup database: konfirmasi "sudah backup" (langkah di `reports/FASE-0.md` §5) — wajib sebelum migrasi pertama (Fase 3).
2. `QRIS_IMAGE_URL` + `WA_NUMBER` (env Railway) — TODO-AGUS, dibutuhkan Fase 6.
3. Refund 24 jam — TODO-AGUS konfirmasi.
4. Format TKA 2026 (tabel di `01_BRIEF_MUSE.md` §3.1) — Agus konfirmasi ke sekolah/situs resmi.

## Flag (semua OFF)
`autopsy_logging`, `autopsy_preview`, `autopsy_full`, `paywall`, `ai_narrative`, `referral`, `wa_notify` — via tabel `feature_flags`, endpoint `GET /api/flags`, ubah via `POST /api/admin/flags?key=VISITOR_ADMIN_KEY`.
