# LAPORAN FASE 1 — Baseline dan audit jalur kritis
Tanggal/jam: 2026-10-08 21:35 WIB · Commit terakhir: (menyusul) · Branch: dev

## 1. Ringkasan
- Baseline statis: `/app` ~436 KB tanpa kompresi; gzip hanya untuk JSON; 3 font Google + KaTeX + (landing) Tailwind CDN; gambar tanpa lazy-load.
- 8 temuan A, 6 temuan B, 4 temuan C → `docs/AUDIT.md`. Lighthouse TIDAK TERVERIFIKASI (tanpa headless browser di sesi ini).
- Kabar baik: T2.2 (konteks AI server-side), T2.3 (abort ganti model), T2.4 (kuota setelah sukses) **sudah dikerjakan PR #31/#33** — Fase 2 tinggal verifikasi + copy.
- Cek .db (tambahan Agus): satu-satunya file `.db` yang pernah ter-commit = `ai_tutor.db` 0-byte di root (PR #35, tidak sengaja); `data/ai_tutor.db` TIDAK PERNAH di-commit.

## 2. Tabel tugas
| ID | Tugas | Status | File diubah | Bukti |
|----|-------|--------|-------------|-------|
| T1.1 | Baseline performa | SELESAI-TERVERIFIKASI | — | angka di `docs/AUDIT.md` (statis); Lighthouse TIDAK TERVERIFIKASI |
| T1.2 | Audit jalur kritis | SELESAI-TERVERIFIKASI | `docs/AUDIT.md` | 18 temuan dengan lokasi file:baris |
| T1.3 | docs/AUDIT.md | SELESAI-TERVERIFIKASI | `docs/AUDIT.md` | 8A+6B ≤ 25 |
| T1.4 | Petakan Lampiran B | SELESAI-TERVERIFIKASI | `docs/AUDIT.md` | 9/9 terpetakan |
| T1.5 | Cek format vs §3.1 | SELESAI-TERVERIFIKASI | `docs/AUDIT.md` | tabel per paket; A1+A2 |
| T1.x | Riwayat .db | SELESAI-TERVERIFIKASI | — | `git log --all -- '*.db'`: hanya `ai_tutor.db` root (0-byte, 3605aab) |

## 3. Angka sebelum → sesudah
Fase 1 tidak mengubah perilaku. Baseline untuk T2.1: transfer awal `/app` ~436 KB (mentah) → target setelah gzip ≈ 120–140 KB.

## 4. Yang TIDAK terverifikasi dan kenapa
- Lighthouse/LCP/TBT/CLS: tidak ada Chromium headless di VM ini. Pengganti: skrip stopwatch Lampiran I.2 untuk 2 HP lemot (Agus).
- Isi DB produksi & RLS Supabase: tanpa akses dashboard.

## 5. Langkah cek untuk Agus
Tidak ada (Fase 1 read-only). Opsional: jalankan skrip stopwatch I.2 di 2 HP lemot, kirim T1/J/C/T2 sebagai baseline "sebelum".

## 6. Risiko / keputusan yang dibutuhkan
1. Timer per paket (A1): usulan = `n_soal × jatah/soal` (MTK P2 pas 75 mnt; MTK P1 46×3=138 mnt). Mengubah pengalaman ujian — boleh jalan? Default: ya, sesuai T2.7 brief.
2. T2.5 (teks `.supabase.co` di login): opsi ada biaya (custom domain) — tidak diputuskan; diajukan sebagai opsi saja.
3. Format resmi 2026: Agus konfirmasi ke sekolah (A1/A2 mengasumsikan tabel §3.1 benar).

## 7. Fase berikutnya
FASE 2: hanya severity A — T2.4 (verifikasi kuota, kode sudah benar), T2.11 (verifikasi JWT, AUTH_VERIFY default OFF), T2.1 (gzip aset statis + lazy gambar), T2.7 (timer per paket + demo/FAQ jujur), T2.2/T2.3 (verifikasi 20 soal & skenario gagal).
Lanjut MODE MALAM.
