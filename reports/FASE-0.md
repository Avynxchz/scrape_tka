# LAPORAN FASE 0 — Orientasi dan pengaman
Tanggal/jam: 2026-10-08 19:25 WIB · Commit terakhir: `2ef4551` · Branch: dev

## 1. Ringkasan (maks 5 baris)
- FASE 0 selesai: branch `dev` dibuat dari `main@3605aab`; dokumen hidup + salinan brief di `docs/`; inventaris di `docs/ARCHITECTURE.md`.
- Mekanisme feature flag jadi dan **terverifikasi lokal** (7 flag, semua OFF; `GET /api/flags`; `POST /api/admin/flags` butuh kunci admin).
- 2 temuan kritis: (a) SQLite di Railway ephemeral — tulisan hilang tiap redeploy; (b) server tidak memverifikasi identitas login Supabase.
- Koreksi observasi lama: `data/ai_tutor.db` **tidak** ada di `main` (sudah di-`.gitignore`); 0 API key asli di kode + riwayat git.
- Tag `pre-autopsi-v0` BELUM dibuat (tidak ada tool); Railway auto-deploy dari `main` terkonfirmasi via `railway.json`.

## 2. Tabel tugas
| ID | Tugas | Status | File diubah | Bukti |
|----|-------|--------|-------------|-------|
| T0.1 | Lapor kapabilitas | SELESAI-TERVERIFIKASI | — | server lokal jalan (`/`,`/app` → 200); `github` CLI bisa commit/PR/push ke `dev`; URL publik terbaca (landing live). TIDAK: akses Supabase SQL & Railway dashboard (tanpa kredensial → Agus eksekusi via dashboard, langkah per fase). Screenshot: TIDAK TERVERIFIKASI. |
| T0.2 | Pengaman | SEBAGIAN | — | branch `dev` dibuat di `3605aab` (terverifikasi via API). Tag `pre-autopsi-v0` BELUM (tidak ada tool pembuat tag). Railway auto-deploy dari `main` tercatat. |
| T0.3 | Inventaris | SELESAI-TERVERIFIKASI | `docs/ARCHITECTURE.md` | file ada di `dev@d06381c` |
| T0.4 | Pindai rahasia | SELESAI-TERVERIFIKASI | — | 0 key asli (`gsk_`/`sk-or-v1_`/`AIza`/password) di working tree + 163 commit riwayat; `.env` tidak pernah di-commit. Catatan: Supabase anon key di `supabase_auth.js` publik by-design (dilindungi RLS). |
| T0.5 | Backup | SELESAI-MENUNGGU-CEK-AGUS | — | langkah klik-demi-klik di §5; butuh balasan "sudah backup" |
| T0.6 | Dokumen hidup | SELESAI-TERVERIFIKASI | `docs/01_BRIEF_MUSE.md`, `02_LAMPIRAN_MUSE.md`, `STATUS.md`, `CHANGELOG.md`, `BACKLOG.md` | commit `b2f9450` |
| T0.7 | Feature flag | SELESAI-TERVERIFIKASI | `feature_flags.py` (baru), `server.py` | tes lokal: GET → 7 flag OFF; POST tanpa key → 401; POST dengan key → ON & GET ikut berubah; flag ngawur → 400; dikembalikan OFF. Commit `2ef4551`. |
| T0.8 | Aturan lama | SELESAI-TERVERIFIKASI | `docs/ARCHITECTURE.md` §5 | 7 dokumen dibaca; 3 konflik dilaporkan (Pro Rp20rb vs Sprint Pass; OAuth "TODO" vs sudah jalan; Windows vs Linux) |
| T0.9 | Persistensi DB | SELESAI-TERVERIFIKASI | `docs/ARCHITECTURE.md` §6 | `railway.json` tanpa Volume → ephemeral; skema 5 tabel didokumentasi; aturan: order/pass wajib di Supabase |
| T0.10 | Peta autentikasi | SELESAI-TERVERIFIKASI | `docs/ARCHITECTURE.md` §6 | alur login dipetakan; temuan: server percaya klaim `logged_in` dari klien |

## 3. Angka sebelum → sesudah
Tidak ada (Fase 0 tidak mengubah perilaku aplikasi). `/` dan `/app` tetap 200 setelah perubahan T0.7 (cek lokal).

## 4. Yang TIDAK terverifikasi dan kenapa
- Isi database **produksi** (berapa baris chat/kuota di Railway): tidak ada akses Railway/Supabase service-role. Tidak memengaruhi Fase 0.
- Screenshot/pixel-check: belum diuji di sesi ini; verifikasi visual tetap via HP Agus.
- Tag `pre-autopsi-v0`: tidak bisa dibuat dengan tool yang tersedia (tidak ada API pembuat tag).

## 5. Langkah cek untuk Agus (bernomor, klik demi klik, hasil yang benar)
**A. Buat tag pengaman `pre-autopsi-v0`** (pengganti tombol yang tidak bisa gue tekan):
1. Di browser HP, buka `github.com/Avynxchz/scrape_tka`.
2. Ketuk tab **Releases** (kanan atas halaman repo).
3. Ketuk **Draft a new release**.
4. Di "Choose a tag", ketik `pre-autopsi-v0` → pilih **Create new tag: pre-autopsi-v0 on publish**.
5. Target: `main`. Judul: `pre-autopsi-v0`. Ketuk **Publish release**.
6. Hasil benar: tag muncul di daftar tags, menunjuk ke commit `3605aab`. Balas "tag jadi".

**B. Backup database Supabase** (wajib sebelum migrasi pertama):
1. Buka `supabase.com` → login → pilih project **tka-master**.
2. Menu kiri: **Table Editor** → tabel `users` → titik tiga (⋯) kanan atas → **Export as CSV** → simpan.
3. Ulangi untuk tabel `feedback` dan `bug_reports`.
4. Simpan 3 file CSV di tempat aman (mis. Google Drive).
5. Balas "sudah backup".
6. Catatan: data chat/kuota di Railway tidak bisa di-backup dari dashboard (hilang tiap deploy) — ini alasan migrasi ke Supabase di Fase 3.

## 6. Risiko / keputusan yang dibutuhkan (maks 3, masing-masing dengan default)
1. **Penyimpanan tulis pindah ke Supabase?** SQLite Railway ephemeral → flag/order/kuota bisa hilang tiap deploy. Default saya: pindahkan data tulis penting (attempt, order, pass, flag) ke Supabase Postgres di Fase 3/6 (tanpa biaya tambahan, Supabase sudah ada). Butuh persetujuan Agus sebelum Fase 3.
2. **Refund 24 jam** (TODO-AGUS di brief): default = ya, manual via WA sesuai brief. Butuh konfirmasi.
3. **`QRIS_IMAGE_URL` + `WA_NUMBER`** (env Railway): dibutuhkan Fase 6. Default: Agus siapkan sebelum 10 Okt; saya beri langkah dashboard saat itu.

## 7. Fase berikutnya (3 baris)
FASE 1: baseline performa (ukur ukuran aset/transfer; Lighthouse bila bisa) + audit jalur kritis (baca kode) → `docs/AUDIT.md` (maks 25 temuan A+B).
Hanya membaca/mengukur; tanpa mengubah perilaku aplikasi.
Menunggu kata "lanjut" dari Agus.
