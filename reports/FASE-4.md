# LAPORAN FASE 4 — Analyzer dan penyusun jadwal (tanpa AI)
Tanggal/jam: 2026-10-08 22:45 WIB · Commit terakhir: (menyusul) · Branch: dev

## 1. Ringkasan
- `autopsy/analyzer.py` (fungsi murni): 9 label prioritas + 2 flag + kebocoran top-3 + fatigue + data_tipis + topik. Ambang di `config/analyzer.json`.
- `autopsy/planner.py` (fungsi murni): jadwal harian deterministik sampai H-1; H-1 tanpa materi baru (≤15 mnt); H-3 simulasi ulang; H-2 tinjau 10 mnt.
- 20/20 tes lulus (`python3 tests/test_autopsy.py`): 8 persona sesuai harapan + 9 properti planner.
- `config/exam.json` (format §3.1) + 2 kartu statis. Kolom `tka_date` → Fase 3 (tanpa sentuh DB malam ini).

## 2. Tabel tugas
| ID | Tugas | Status | File diubah | Bukti |
|----|-------|--------|-------------|-------|
| T4.1 | Modul analyzer | SELESAI-TERVERIFIKASI | `autopsy/analyzer.py`, `config/analyzer.json` | 10/10 tes persona |
| T4.2 | Modul planner | SELESAI-TERVERIFIKASI | `autopsy/planner.py` | 9/9 properti (deterministik, H-1, ref valid, dsb) |
| T4.3 | Tes + 8 persona | SELESAI-TERVERIFIKASI | `tests/test_autopsy.py`, `tests/fixtures/personas.py` | `20 lulus, 0 gagal` |
| T4.4 | Kartu statis | SELESAI-TERVERIFIKASI | `content/cards/anti_ceroboh.md`, `strategi_waktu.md` | isi = Lampiran E verbatim |
| T4.5 | config exam.json | SELESAI-TERVERIFIKASI | `config/exam.json` | tabel §3.1; `tka_date` → Fase 3 |

## 3. Angka sebelum → sesudah
Tidak ada (modul baru, belum dipakai UI).

## 4. Yang TIDAK terverifikasi dan kenapa
- Integrasi ke `/api` dan layar hasil → Fase 5/6 (butuh DB + UI).
- `tka_date` per user → Fase 3 (dilarang sentuh DB malam ini).

## 5. Langkah cek untuk Agus
Tidak ada (modul backend murni). Validasi isi (Gate A, 11 Okt) memakai output modul ini via mode demo Fase 5.

## 6. Risiko / keputusan yang dibutuhkan
1. Bobot prioritas & ambang (mis. terburu 1,0) adalah default engineer — boleh di-tune setelah Gate A. Default: pakai dulu.
2. Planner butuh pustaka konten nyata (Pilar per soal, soal serupa) — dibangun Fase 5 dari data yang sudah ada.

## 7. Fase berikutnya
FASE 3 (besok, setelah backup+tag): migrasi Supabase (attempts, dst) + perekam klien + verifikasi JWT sudah siap (T2.11) + pindah flag ke Supabase.
STOP MODE MALAM sampai sini (Fase 1, 2, 4 selesai).
