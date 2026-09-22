# Laporan Validasi — Canonical Question Transcription v1.1

Tanggal: 2026-09-20 · Builder: `build_canonical_questions.py` (deterministik, idempoten)
Status: **setelah pass transkripsi vision penuh** (batch 100 visual → 96 terwakili, 10 jujur unresolved)
Tes: `tests/test_canonical_extraction.py` — **19/19 PASS** · Gerbang otoritatif: `validate_data.py` — **SEMUA LOLOS**

## Dataset

| Paket | Soal | Formula (resmi + vision) | Tabel | Diagram | Lainnya | Unresolved | AI-ready |
|---|---|---|---|---|---|---|---|
| matematika_paket_1 | 46 | 30 (12+18) | 2 | 28 | 0 | 2 | 44 |
| matematika_paket_2 | 25 | 21 (16+5) | 0 | 21 | 2 | 7 | 23 |
| bahasa_inggris_paket_1 | 20 | 0 | 0 | 5 | 0 | 5 | 15 |
| bahasa_inggris_paket_2 | 25 | 0 | 5 | 11 | 0 | 0 | 25 |
| ekonomi_paket_1 | 20 | 0 | 2 | 2 | 0 | 0 | 20 |
| ekonomi_paket_2 | 29 | 0 | 0 | 5 | 5 | 0 | 29 |
| kewirausahaan_paket_1 | 10 | 0 | 0 | 1 | 0 | 0 | 10 |
| kewirausahaan_paket_2 | 30 | 0 | 0 | 5 | 2 | 0 | 30 |
| **TOTAL** | **205** | **51 (28+23)** | **9** | **78** | **9** | **14** | **196** |

Rekonsiliasi: soal sumber == soal kanonis == 205 (46/25/20/25/20/29/10/30).
Tipe terjaga: **PG 117, PGK 61, BS 22, LABEL 5** → **259 item dinilai** (178 pilihan
+ 27 pernyataan × 3) — identik dengan gerbang `validate_data.py`.

## Pass transkripsi vision (batch terkonsolidasi)

- Input: `data/canonical_questions/_vision_batch/` — 119 referensi unresolved
  terdeduplikasi sha256 menjadi **100 visual unik** (V001…V100), manifest +
  contact-sheet PDF berlabel `visual_id`.
- Hasil Claude (`VISION_TRANSCRIPTION_RESULT.json`): 96 visual terwakili
  (latex/deskripsi faktual, confidence tinggi; nilai grafik yang hanya bisa
  dibaca dari gridline **sengaja tidak ditebak**), 10 visual ditandai
  `unresolved: true` oleh Claude sendiri.
- `convert` → validasi kontrak (ID, enum, konsistensi, coverage): **0 masalah**;
  → hasil per-slug → `_vision_packet.py ingest` (diterima 105 pemetaan referensi,
  0 ditolak) → rebuild kanonis penuh.
- Efek: unresolved **119 → 14 referensi**; AI-ready **110 → 196 soal**.

## 14 unresolved tersisa (9 soal) — jujur, tanpa tebakan

Semua persis merupakan visual yang Claude sendiri tandai `unresolved: true`:
- **mtk1 q4** (V001) & **mtk1 q31** (V032): diagram batang tanpa label nilai
  (nilai hanya bisa dibaca dari posisi gridline → tidak ditranskripsi).
- **mtk2 q14** (V059–V064, 6 opsi grafik): titik koordinat tidak tercetak di grid
  (posisi relatif saja yang terdeskripsi).
- **mtk2 q21** (V071): line chart 3 seri tanpa label nilai titik.
- **bing1 q6–q10** (V075, 1 file untuk 5 soal): infografis terpotong di tepi
  bawah gambar (1 baris teks tak terbaca).
Keputusan konsisten: nilai yang hanya tersirat pada gridline tidak dibaca/diambil
kesimpulan — preserve ambiguity, sesuai aturan pass.

## Integritas jawaban resmi & data otoritatif

- `official_answer` tetap diturunkan **hanya** dari bukti `data/kunci/` dengan
  cross-check learning (raise bila beda) — **identik 205/205**; kunci multi PGK
  dan pernyataan BS/Label utuh.
- `validate_data.py`: **SEMUA LOLOS** (205 soal, 259 item, 203 referensi gambar).
- Tidak ada perubahan pada raw scrape, learning JSON, `data/kunci/`, frontend.

## Integriti gambar & determinisme

- 221 referensi `source_images` — semua ada di disk; setiap referensi terwakili
  (formula/`data-latex`, transkripsi vision, `represented_by`, deskripsi, atau
  penanda eksplisit) — tidak ada gambar "diam" (tes).
- Rebuild berulang dengan side-car tetap deterministik (sha256 identik).

## Perbaikan pipeline saat pass ini

- Bug nyata (ditemukan rebuild penuh): deskripsi vision pada gambar berklasifikasi
  'formula' menabrak bucket tidak ada (`visuals["formulas"]`) → diperbaiki dengan
  bucket `others` untuk visual berdeskripsi di luar table/graph/diagram.
- Tes diperluas mencakup bucket `others` (tetap 19/19 PASS).

## Keterbatasan tersisa

1. **14 referensi visual / 9 soal** menunggu keputusan lanjutan (lihat daftar
   di atas): opsi jujur adalah membiarkan `manual_review`, atau memperoleh nilai
   resmi dari sumber lain bila tersedia — bukan menebak dari gridline.
2. Transkripsi vision 96 visual lain adalah deskripsi faktual per elemen
   (confidence tercatat di hasil; soal tidak pernah "diselesaikan" oleh pass ini).
3. `data/canonical_questions/_vision_batch/results/` menyimpan hasil per-slug
   sebagai jejak audit ingest.
