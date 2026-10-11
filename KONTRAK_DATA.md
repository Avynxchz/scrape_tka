# KONTRAK DATA — TKA Master (WAJIB dibaca semua AI)

File ini adalah sumber kebenaran data. Angka di bawah dihitung langsung dari
file JSON project (data/*_paket_*.json) per 10 Okt 2026. JANGAN MENGARANG ANGKA.

## Mata pelajaran & jumlah soal real (27 mapel, 49 paket, 991 soal total)

| Mapel | key | Paket 1 | Paket 2 | Keterangan |
|---|---|---|---|---|
| Matematika (Wajib) | matematika | 46 | 25 | Wajib |
| Bahasa Indonesia (Wajib) | bahasa_indonesia | 20 | 25 | Wajib |
| Bahasa Inggris (Wajib) | bahasa_inggris | 20 | 25 | Wajib |
| Fisika (Peminatan) | fisika | 20 | 24 | Saintek |
| Kimia (Peminatan) | kimia | 20 | 24 | Saintek |
| Biologi (Peminatan) | biologi | 20 | 29 | Saintek |
| Ekonomi | ekonomi | 20 | 29 | Soshum |
| Geografi | geografi | 10 | 29 | Soshum |
| Sosiologi | sosiologi | 20 | 30 | Soshum |
| Sejarah | sejarah | 10 | 29 | Soshum |
| Antropologi | antropologi | 10 | 30 | Soshum |
| Kewirausahaan (PKWU) | kewirausahaan | 10 | 30 | Soshum |
| Matematika Lanjut | matematika_lanjut | 20 | 25 | Tingkat Lanjut |
| B. Indonesia Lanjut | bahasa_indonesia_lanjut | 10 | 29 | Tingkat Lanjut |
| B. Inggris Lanjut | bahasa_inggris_lanjut | 10 | 29 | Tingkat Lanjut |
| PPKn | ppkn | 20 | 29 | Bahasa & Lintas Minat |
| Bahasa Arab | bahasa_arab | 10 | 29 | Bahasa & Lintas Minat |
| Bahasa Jepang | bahasa_jepang | 10 | 29 | Bahasa & Lintas Minat |
| Bahasa Jerman | bahasa_jerman | 10 | 29 | Bahasa & Lintas Minat |
| Bahasa Prancis | bahasa_prancis | 10 | 29 | Bahasa & Lintas Minat |
| Bahasa Mandarin | bahasa_mandarin | 10 | 29 | Bahasa & Lintas Minat |
| Bahasa Korea | bahasa_korea | 10 | 29 | Bahasa & Lintas Minat |
| Teknik Mesin (SMK) | teknik_mesin | 6 | - | Kejuruan SMK (Paket 1 resmi Pusmendik) |
| Teknik Otomotif (SMK) | teknik_otomotif | 6 | - | Kejuruan SMK (Paket 1 resmi Pusmendik) |
| Teknik Jaringan & Telekomunikasi (SMK) | teknik_jaringan | 6 | - | Kejuruan SMK (Paket 1 resmi Pusmendik) |
| Akuntansi & Keuangan Lembaga (SMK) | akuntansi | 6 | - | Kejuruan SMK (Paket 1 resmi Pusmendik) |
| Manajemen Perkantoran & Layanan Bisnis (SMK) | manajemen_perkantoran | 6 | - | Kejuruan SMK (Paket 1 resmi Pusmendik) |

*Catatan: Mapel Kejuruan SMK hanya memiliki Paket 1 (6 butir soal resmi Pusmendik).*

Estimasi durasi pengerjaan: ± 1 menit per soal (Paket 1 mtk = ±45 menit, Paket SMK = ±15 menit).

## Kategori mapel (untuk tab/group)

- WAJIB (3 mapel): matematika, bahasa_indonesia, bahasa_inggris
- SAINTEK (3 mapel): fisika, kimia, biologi
- SOSHUM (6 mapel): ekonomi, geografi, sosiologi, sejarah, antropologi, kewirausahaan
- TINGKAT LANJUT (3 mapel): matematika_lanjut, bahasa_indonesia_lanjut, bahasa_inggris_lanjut
- BAHASA ASING & LINTAS MINAT (7 mapel): ppkn, bahasa_arab, bahasa_jepang, bahasa_jerman, bahasa_prancis, bahasa_mandarin, bahasa_korea
- KEJURUAN SMK (5 mapel): teknik_mesin, teknik_otomotif, teknik_jaringan, akuntansi, manajemen_perkantoran

Total: 3 + 3 + 6 + 3 + 7 + 5 = 27 mapel.

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
- KEJURUAN SMK: precision_manufacturing (mesin), directions_car (otomotif), router (jaringan), account_balance (akuntansi), corporate_fare (perkantoran)

## Aturan konten

- Nama mapel HARUS persis tabel di atas.
- Jumlah soal HARUS persis tabel di atas.
- Angka progres/skor selain dari format localStorage = dilarang keras.
