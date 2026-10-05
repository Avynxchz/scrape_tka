# KONTRAK DATA — TKA Master (WAJIB dibaca semua AI)

File ini adalah sumber kebenaran data. Angka di bawah dihitung langsung dari
file JSON project (data/*_paket_*.json) per 4 Okt 2026. JANGAN MENGARANG ANGKA.

## Mata pelajaran & jumlah soal real (22 mapel, 44 paket, 961 soal total)

| Mapel | key | Paket 1 | Paket 2 |
|---|---|---|---|
| Matematika (Wajib) | matematika | 46 | 25 |
| Bahasa Indonesia (Wajib) | bahasa_indonesia | 20 | 25 |
| Bahasa Inggris (Wajib) | bahasa_inggris | 20 | 25 |
| Fisika (Peminatan) | fisika | 20 | 24 |
| Kimia (Peminatan) | kimia | 20 | 24 |
| Biologi (Peminatan) | biologi | 20 | 29 |
| Ekonomi | ekonomi | 20 | 29 |
| Geografi | geografi | 10 | 29 |
| Sosiologi | sosiologi | 20 | 30 |
| Sejarah | sejarah | 10 | 29 |
| Antropologi | antropologi | 10 | 30 |
| Kewirausahaan (PKWU) | kewirausahaan | 10 | 30 |
| Matematika Lanjut | matematika_lanjut | 20 | 25 |
| B. Indonesia Lanjut | bahasa_indonesia_lanjut | 10 | 29 |
| B. Inggris Lanjut | bahasa_inggris_lanjut | 10 | 29 |
| PPKn | ppkn | 20 | 29 |
| Bahasa Arab | bahasa_arab | 10 | 29 |
| Bahasa Jepang | bahasa_jepang | 10 | 29 |
| Bahasa Jerman | bahasa_jerman | 10 | 29 |
| Bahasa Prancis | bahasa_prancis | 10 | 29 |
| Bahasa Mandarin | bahasa_mandarin | 10 | 29 |
| Bahasa Korea | bahasa_korea | 10 | 29 |

Estimasi durasi pengerjaan: ± 1 menit per soal (Paket 1 mtk = ±45 menit).

## Kategori mapel (untuk tab/group)

- SAINTEK (Peminatan): fisika, kimia, biologi
- SOSHUM (Peminatan): ekonomi, geografi, sosiologi, sejarah, antropologi, kewirausahaan
- WAJIB: matematika, bahasa_indonesia, bahasa_inggris
- TINGKAT LANJUT: matematika_lanjut, bahasa_indonesia_lanjut, bahasa_inggris_lanjut
- BAHASA ASING & LINTAS MINAT: ppkn, bahasa_arab, bahasa_jepang, bahasa_jerman, bahasa_prancis, bahasa_mandarin, bahasa_korea

## Format progres pengerjaan (disimpan app utama di localStorage)

```json
{
  "tka_progress": {
    "matematika": { "1": { "1": {"kunci":"B","benar":true}, "2": {"kunci":"C","benar":false} } }
  }
}
```
Struktur: tka_progress[subjectKey][pkgNumber][nomorSoal] = { kunci, benar }.
Halaman progres HARUS membaca format ini (jangan mengarang format lain).
Saat data kosong: tampilkan keadaan kosong yang jelas ("Belum ada yang dikerjakan"),
JANGAN tampilkan angka palsu.

## Ikon Material Symbols per kategori

- WAJIB: calculate / menu_book / language
- SAINTEK: bolt (fisika), science (kimia), psychology (biologi)
- SOSHUM: query_stats, public, groups, landmark, diversity_3, storefront
- LANJUT: trending_up

## Aturan konten

- Nama mapel HARUS persis tabel di atas.
- Jumlah soal HARUS persis tabel di atas.
- Angka progres/skor selain dari format localStorage = dilarang keras.
