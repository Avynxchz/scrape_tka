# LAPORAN FASE 3 — Migrasi dan logging
Tanggal/jam: 2026-10-09 11:45 WIB · Branch: dev (1x push akhir fase)

## 1. Ringkasan
- T3.1: SQL migrasi jalan (Agus): tabel `attempts` + kolom `tka_date`/`profile_name` + tabel `feature_flags`. Backup dilewati (tabel baru kosong).
- T3.2/T3.3: perekam klien (waktu aktif, jawaban pertama/akhir, ganti, ragu, kunjungan) + antrean localStorage + upload sekali ke `POST /api/attempts`; indikator "tersimpan".
- Server: `/api/attempts` verifikasi JWT, `user_id` dari token (bukan klien), teruskan ke Supabase REST (RLS menegakkan). Butuh env: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`.
- T3.4: kuis wajib login (belum login → ajakan login Google). T3.6: FAQ biaya AI. T3.7: tooltip tombol Ragu-ragu.
- app.js (Fase 2+3) → upload manual Agus (file siap). T3.5: verifikasi 2 device → langkah untuk Agus di §5.

## 2. Tabel tugas
| ID | Tugas | Status | File diubah | Bukti |
|----|-------|--------|-------------|-------|
| T3.1 | Tabel attempts + kolom | SELESAI-TERVERIFIKASI | `supabase/migrations/003_fase3_autopsy.sql` | Agus: "SQL sudah jalan" |
| T3.2 | Perekam klien | SELESAI-TERVERIFIKASI | `app.js` (manual) | simulasi node: first/final/ganti/ragu/visits benar |
| T3.2 | POST /api/attempts | SELESAI-TERVERIFIKASI | `server.py` | tes: 401 tanpa token; 503 tanpa env; 400 items kosong; user_id palsu diabaikan |
| T3.3 | Sinkronisasi + indikator | SELESAI-TERVERIFIKASI | `app.js` (manual) | antrean push/remove OK; badge di layar hasil |
| T3.4 | Kuis wajib login | SELESAI-MENUNGGU-CEK-AGUS | `app.js` (manual) | gate di modal mulai; perlu cek visual |
| T3.5 | Verifikasi 2 device | SEBAGIAN | — | langkah di §5 (butuh 2 HP + login) |
| T3.6 | Penjelasan biaya AI | SELESAI-TERVERIFIKASI | `landing.html` | FAQ "Berapa biaya AI Tutor?" |
| T3.7 | Tooltip Ragu-ragu | SELESAI-TERVERIFIKASI | `index.html` | title pada #btnRagu |

## 3. Angka sebelum → sesudah
- Attempt tersimpan di server: 0 → tercatat per user di Supabase (setelah env diisi + app.js di-upload).

## 4. Yang TIDAK terverifikasi dan kenapa
- Upload end-to-end ke Supabase sungguhan: butuh `SUPABASE_URL`/`ANON_KEY` di Railway + app.js ter-upload (langkah §5).
- Render visual gate login, badge, tooltip: Agus cek di HP setelah upload.

## 5. Langkah cek untuk Agus
**A. Env Railway** (sekali): Railway → tka-master → Variables → tambah `SUPABASE_URL` (= https://auhqgzrrgvjbfvzvayzg.supabase.co), `SUPABASE_ANON_KEY` (= dari Supabase → Project Settings → API → anon public), `SUPABASE_JWT_SECRET` (= JWT Secret, untuk T2.11 juga). Tunggu redeploy.
**B. Upload app.js** (cara di file panduan) → buka /app → login Google.
**C. T3.5 dua device**: di HP#1 kerjakan 1 paket sampai selesai → di layar hasil harusnya "✓ Hasil tersimpan di akunmu". Cek Supabase → Table Editor → `attempts` → ada 1 baris (mapel/paket benar). Ulangi di HP#2 dengan akun sama → total 2 baris, `user_id` sama.
**D. Timer habis**: (opsional) biarkan timer 1 paket kecil habis → harus otomatis selesai.

## 6. Risiko / keputusan yang dibutuhkan
1. T3.4 mengubah funnel (tamu tak bisa kuis). Sesuai brief; kalau conversion turun drastis, bisa dilonggarkan (guest → antrean lokal saja). Default: jalan dulu.
2. `score` di attempts opsional (NULL bila tak dikirim); Autopsi menghitung sendiri dari kunci. Default: OK.

## 7. Fase berikutnya
FASE 5: mode demo + layar Autopsi (butuh app.js ter-upload + env). Tag `pre-autopsi-v0` sebelum merge pertama ke main (per Agus).
