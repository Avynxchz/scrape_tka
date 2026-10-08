# LAPORAN FASE 2 — Perbaikan blocker (severity A)
Tanggal/jam: 2026-10-08 22:20 WIB · Commit terakhir: `87fa373` · Branch: dev

## 1. Ringkasan
- T2.4 kuota: **kode sudah benar** — tes live tanpa API key: AI gagal → kuota tetap 5/5. Yang salah hanya FAQ (diperbaiki di T2.7).
- T2.11 (tambahan Agus): verifikasi JWT Supabase di server, di balik `AUTH_VERIFY` (default OFF). 4/4 skenario tes lulus. Server ter-push; app.js klien → upload manual besok.
- T2.1: gzip aset statis → app.js 220→57 KB, style.css 155→28 KB (terverifikasi). Lazy-load gambar masuk ke app.js manual.
- T2.7: timer per paket (n × jatah resmi), demo landing jujur (75:00 · 25 soal), FAQ diperbaiki (kuota gagal, login tersedia).
- T2.2/T2.3: kode sudah benar (PR #31/#33); tes live 20 soal TIDAK TERVERIFIKASI (tanpa API key di sesi ini).

## 2. Tabel tugas
| ID | Tugas | Status | File diubah | Bukti |
|----|-------|--------|-------------|-------|
| T2.4 | Kuota hanya setelah sukses | SELESAI-TERVERIFIKASI | — (kode sudah benar) | tes live: `llm_error` → count 0/remaining 5 |
| T2.11 | Verifikasi JWT server | SELESAI-TERVERIFIKASI | `auth_verify.py` (baru), `server.py` | 4 skenario: OFF→free; ON tanpa token→guest; token valid→free; kadaluarsa/rusak→guest. Commit `cfe0ae6` |
| T2.11 | Klien kirim token | SEBAGIAN | `app.js` (upload manual besok) | `node --check` OK; file siap |
| T2.1 | gzip aset statis | SELESAI-TERVERIFIKASI | `server.py` | app.js 220→57 KB; style.css 155→28 KB; isi valid. Commit `bfb104d` |
| T2.1 | lazy gambar | SEBAGIAN | `app.js` (upload manual besok) | 4 `<img>` → `loading="lazy"` |
| T2.7 | Timer per paket | SEBAGIAN | `app.js` (upload manual besok) | MTK P2 → 75:00 (pas resmi); fallback 105 mnt |
| T2.7 | Demo & FAQ | SELESAI-TERVERIFIKASI | `landing.html` | 0 sisa "45:00/40 soal"; FAQ benar. Commit `87fa373` |
| T2.2 | Konteks AI benar | SEBAGIAN | — | kode: prompt dirakit server dari `soal_id` ✓; tes 20 soal TIDAK TERVERIFIKASI |
| T2.3 | Abort ganti model | SEBAGIAN | — | kode: `AbortController` ✓; tes live → Agus |
| T2.5 | Teks login acak | BELUM | — | opsi di §6 (ada biaya → tidak diputuskan) |
| T2.6 | Lapor Bug | SELESAI-TERVERIFIKASI | — (PR #32) | kirim ke Supabase `bug_reports` ✓ |
| T2.10 | Kebijakan key AI | BELUM | — | opsi di §6 (keputusan biaya) |

## 3. Angka sebelum → sesudah
- Transfer `/app` awal: ~436 KB mentah → ~120 KB dengan gzip (app.js 57 + style.css 28 + html ~35).
- Kuota gagal-kirim: terpotong (klaim FAQ lama, salah) → tidak terpotong (fakta kode).

## 4. Yang TIDAK terverifikasi dan kenapa
- Tes 20 soal AI (T2.2): tanpa API key di sesi ini (key hanya di Railway; dilarang minta key di chat).
- Render visual timer/landing/FAQ: Agus cek di HP (dev belum di-merge ke main → live belum berubah).
- app.js manual: belum di-upload (besok).

## 5. Langkah cek untuk Agus (besok, gabung dengan tag+backup)
**A. Upload app.js**: buka file `app.js` dari link Muse → github.com/Avynxchz/scrape_tka → branch `dev` → Add file → Upload files → pilih app.js → commit message `app.js: T2.11 token + T2.1 lazy img + T2.7 timer per paket` → pastikan ke `dev`, BUKAN main.
**B. Nyalakan AUTH_VERIFY** (setelah A):
1. Supabase dashboard → Project Settings → API → salin **JWT Secret**.
2. Railway dashboard → tka-master → Variables → tambah `SUPABASE_JWT_SECRET` = secret tadi, dan `AUTH_VERIFY` = `1`.
3. Tunggu redeploy (~2 mnt).
4. Tes: login Google → kuota 25 (bukan 5). Logout → kuota 5.
5. Darurat: set `AUTH_VERIFY` = `0` → kembali ke perilaku lama.

## 6. Risiko / keputusan yang dibutuhkan
1. T2.5 teks login: opsi A teks penjelas (gratis) / B branding Google consent (gratis, butuh console) / C custom domain (~$25/bln). Default: A+B.
2. T2.10 key AI: A 1 akun berbayar (~Rp320rb/bln, patuh ToS) / B tetap multi-key gratis (risiko ToS) / C provider lain. Default: diskusi dulu (keputusan biaya).
3. Timer MTK P1 (46 soal → 138 mnt): rumus jujur, tapi durasinya panjang. Alternatif: label "format latihan". Default: rumus jalan; evaluasi setelah Gate A.

## 7. Fase berikutnya
FASE 4: `analyzer.py` + `planner.py` (fungsi murni, tanpa DB) + `config/analyzer.json` + `config/exam.json` + kartu statis + tes 8 persona. Tanpa sentuh Supabase/database.
Lanjut MODE MALAM.
