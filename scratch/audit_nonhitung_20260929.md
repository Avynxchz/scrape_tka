# Audit Pola Teks Rusak — Slice Non-Hitungan

Tanggal: 2026-09-29 · Scope: 11 file learning + 11 file solusi (bahasa Indonesia, bahasa Inggris, biologi, geografi, sosiologi, sejarah) · READ-ONLY: tidak ada file data yang diubah.

Metode: script `scratch/_audit_slice_nonhitung.py` (self-test 16 asersi OK) menelusuri SEMUA string user-visible secara rekursif, kecuali kunci non-teks (id, kunci_jawaban, latex, image, official_answer, dst.). Mencakup juga field yang mudah terlewat: `soal[].pembahasan.*` pada learning (diketahui, mengapa_begini, langkah_penyelesaian, tips_trik, glosarium_simbol, dst.) dan `solutions[].soal_serupa.*` pada file solusi. Field HTML dibersihkan tag dulu (tag blok → newline). Deteksi di luar segmen `$...$` untuk LaTeX; `$...$` dianggap legitim.

Klasifikasi pola: ECHO-VERTIKAL = >=6 baris pendek (<=4 char) + versi utuhnya ada / run muncul 2x · LATEX-KORUP = ±atrix, p/b matrix, \b egin, \fr ac, command terpecah spasi · LATEX-MENTAH = command LaTeX di luar $...$ · ECHO-GANDA = token/frasa/baris diulang langsung 2x · ECHO-GANDA-FP-JUDUL = judul diikuti kalimat pembuka kata yang sama (benign, struktur dokumen normal — TIDAK dihitung korupsi) · UNICODE-MATH = U+1D400-1D7FF / U+210E · AMBIGU = koma ganda / kalimat buntu · LATEX-ANOMALI-KARAKTER = karakter mencurigakan (°, fullwidth, U+FFFD) di dalam $...$.

## Ringkasan per file

| file | ECHO-VERT | LATEX-KORUP | LATEX-MENTAH | ECHO-GANDA | FP-JUDUL | UNI-MATH | AMBIGU-KOMA | AMBIGU-KAL | ANOMALI-$ | MISSING | total temuan |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bahasa_inggris_paket_2_learning.json | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| geografi_paket_1_learning.json | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| geografi_paket_2_learning.json | 0 | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 1 |
| BIOLOGI_PAKET_1_SOL.json | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| GEO_PAKET_2_SOL.json | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 2 |

Kolom FP-JUDUL = false positive struktur judul+kalimat pembuka (benign); tidak dihitung dalam total temuan korupsi.

## Tabel temuan lengkap

| file | nomor | field | pola | cuplikan (≤80 char) |
|---|---|---|---|---|
| BIOLOGI_PAKET_1_SOL.json | 5 | sol.reasoning | LATEX-ANOMALI-KARAKTER | lui respirasi seluler dengan persamaan: $C_6H_{12}O_6 + 6O_2 \rightarrow 6CO_2 + |
| GEO_PAKET_2_SOL.json | 5 | sol.reasoning | ECHO-GANDA | ena keduanya merupakan destinasi bahari/pesisir pesisir, bukan dataran tinggi. O |
| GEO_PAKET_2_SOL.json | 23 | sol.steps[1].explanation | LATEX-ANOMALI-KARAKTER | Formula pembentukan hujan asam: $2NO_2 + H_2° \rightarrow HNO_2 + HNO_3$. Asam n |
| bahasa_inggris_paket_2_learning.json | 11 | soal.stimulus.text | ECHO-GANDA-FP-JUDUL | The Great Barrier Reef⏎The Great Barrier Reef is one of the  |
| bahasa_inggris_paket_2_learning.json | 11 | soal.stimulus.html | ECHO-GANDA-FP-JUDUL | ⏎The Great Barrier Reef⏎The Great Barrier Reef is one of the |
| bahasa_inggris_paket_2_learning.json | 12 | soal.stimulus.text | ECHO-GANDA-FP-JUDUL | The Great Barrier Reef⏎The Great Barrier Reef is one of the  |
| bahasa_inggris_paket_2_learning.json | 12 | soal.stimulus.html | ECHO-GANDA-FP-JUDUL | ⏎The Great Barrier Reef⏎The Great Barrier Reef is one of the |
| bahasa_inggris_paket_2_learning.json | 13 | soal.stimulus.text | ECHO-GANDA-FP-JUDUL | The Great Barrier Reef⏎The Great Barrier Reef is one of the  |
| bahasa_inggris_paket_2_learning.json | 13 | soal.stimulus.html | ECHO-GANDA-FP-JUDUL | ⏎The Great Barrier Reef⏎The Great Barrier Reef is one of the |
| bahasa_inggris_paket_2_learning.json | 14 | soal.stimulus.text | ECHO-GANDA-FP-JUDUL | The Great Barrier Reef⏎The Great Barrier Reef is one of the  |
| bahasa_inggris_paket_2_learning.json | 14 | soal.stimulus.html | ECHO-GANDA-FP-JUDUL | ⏎The Great Barrier Reef⏎The Great Barrier Reef is one of the |
| bahasa_inggris_paket_2_learning.json | 15 | soal.stimulus.text | ECHO-GANDA-FP-JUDUL | The Great Barrier Reef⏎The Great Barrier Reef is one of the  |
| bahasa_inggris_paket_2_learning.json | 15 | soal.stimulus.html | ECHO-GANDA-FP-JUDUL | ⏎The Great Barrier Reef⏎The Great Barrier Reef is one of the |
| geografi_paket_1_learning.json | 2 | soal.stimulus.text | ECHO-GANDA-FP-JUDUL | Danau Bandung Purba⏎Danau Bandung purba terbentuk sekitar 12 |
| geografi_paket_1_learning.json | 2 | soal.stimulus.html | ECHO-GANDA-FP-JUDUL | ⏎Danau Bandung Purba⏎Danau Bandung purba terbentuk sekitar 1 |
| geografi_paket_2_learning.json | 5 | soal.pembahasan.mengapa_begini | ECHO-GANDA | ena keduanya merupakan destinasi bahari/pesisir pesisir, bukan dataran tinggi. O |
| geografi_paket_2_learning.json | 10 | soal.stimulus.text | ECHO-GANDA-FP-JUDUL | Fenomena Penuaan Penduduk di Indonesia⏎Indonesia dan negara-negara ASEAN sedang  |
| geografi_paket_2_learning.json | 10 | soal.stimulus.html | ECHO-GANDA-FP-JUDUL | ⏎Fenomena Penuaan Penduduk di Indonesia⏎Indonesia dan negara-negara ASEAN sedang |

## Catatan verifikasi manual (klasifikasi benign vs korup)

1. **ECHO-GANDA-FP-JUDUL** — semua kasus terverifikasi adalah judul stimulus yang diikuti kalimat pertama memuat judul tersebut (mis. `The Great Barrier Reef⏎The Great Barrier Reef is one of...` pada B.INGGRIS paket 2 q11-15, `Danau Bandung Purba⏎Danau Bandung purba terbentuk...` pada GEO paket 1 q2, `Fenomena Penuaan Penduduk di Indonesia⏎Indonesia dan negara-negara ASEAN...` pada GEO paket 2 q10). Struktur judul+isi normal — bukan kerusakan.
2. **ECHO-GANDA korup terverifikasi** — GEO_PAKET_2_SOL q5 `reasoning`: `...destinasi bahari/pesisir pesisir, bukan dataran tinggi.` — token `pesisir` terduplikasi langsung. Satu-satunya duplikasi korup di slice ini.
3. **LATEX-ANOMALI-KARAKTER** — GEO_PAKET_2_SOL q? `steps[].explanation`: `$2NO_2 + H_2° \\rightarrow HNO_2 + HNO_3$` — `°` (U+00B0) menggantikan `O` pada H2O; kemungkinan besar korupsi OCR/ketik. Konten di dalam $...$ jadi perlu perbaikan terpisah dari pola LaTeX mentah.
4. **LaTeX dalam $...$ ditemukan legitim** — dipakai di pembahasan learning B.INGGRIS/GEOGRAFI dan beberapa file solusi (mis. `$2NO_2 + H_2O \\rightarrow HNO_2 + HNO_3$`, `$91{,}4\\%$`, `$\\rightarrow$` di tips SEJARAH paket 2). Renderer aplikasi harus mendukung math delimiter `$...$` untuk field-field ini.

## Statistik total

- String user-visible dipindai: 11660
- Field mengandung >=1 temuan (termasuk FP-JUDUL): 18
- Total temuan korupsi (di luar FP-JUDUL): 4
- Total temuan termasuk FP-JUDUL: 18
- ECHO-GANDA: 2
- ECHO-GANDA-FP-JUDUL: 14
- LATEX-ANOMALI-KARAKTER: 2
- Field data_latex / latex / image: tidak diaudit (legitim sesuai instruksi).

## File tanpa temuan

- bahasa_indonesia_paket_1_learning.json
- bahasa_indonesia_paket_2_learning.json
- bahasa_inggris_paket_1_learning.json
- biologi_paket_1_learning.json
- biologi_paket_2_learning.json
- sosiologi_paket_1_learning.json
- sejarah_paket_1_learning.json
- sejarah_paket_2_learning.json
- BAHASA_INDONESIA_PAKET_1_SOL.json
- BAHASA_INDONESIA_PAKET_2_SOL.json
- BING_PAKET_1_SOL.json
- BING_PAKET_2_SOL.json
- BIOLOGI_PAKET_2_SOL.json
- GEO_PAKET_1_SOL.json
- SOSIOLOGI_PAKET_1_SOL.json
- SEJARAH_PAKET_1_SOL.json
- SEJARAH_PAKET_2_SOL.json
