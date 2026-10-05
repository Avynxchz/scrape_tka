# PROMPT UNTUK ZCODE (GLM 5.3 Flash) — Halaman MODUL

Copy-paste seluruh teks ini ke Zcode, beserta isi file `ATURAN_AI.md` dan
`KONTRAK_DATA.md` dari project SCRAPE_TKA (root: D:\PROJECTS\SCRAPE_TKA).

---

Kamu mengerjakan halaman "Modul" untuk app TKA Master (platform latihan soal
TKA Pusmendik Indonesia). Project sudah berjalan; kamu HANYA membuat satu file
baru. Baca dulu dua file ini di root project dan patuhi isinya sepenuhnya:

1. `ATURAN_AI.md`  — aturan wilayah file, kontrak postMessage, disiplin teknis
2. `KONTRAK_DATA.md` — data mapel & jumlah soal REAL (jangan mengarang angka)

## Tugasmu

Buat SATU file: `workspace_modul/modul.html` — halaman "Modul Belajar",
mobile-first (390px) dengan versi desktop (konten max-width 480px di tengah).

## Struktur halaman

1. **Header**: judul "Modul Belajar" + subjudul kecil "22 Mapel · 44 Paket ·
   961 Soal" (angka dari KONTRAK_DATA.md).
2. **Tab filter kategori** (sticky di bawah header): Semua · Wajib · Saintek ·
   Soshum · Lanjut · Bahasa & Lintas Minat. Tab aktif menyaring section.
3. **Search bar**: filter nama mapel secara live (client-side).
4. **Daftar mapel** (grouped per kategori): tiap mapel = satu baris card
   berisi ikon Material Symbols, nama mapel PERSIS dari kontrak, jumlah soal
   Paket 1 & Paket 2 PERSIS dari kontrak, dan dua tombol kecil "Paket 1" /
   "Paket 2". Klik tombol paket kirim:
   `parent.postMessage({type:'open-package', subject:key, pkg:N}, '*')`
5. **Keadaan kosong** saat search tidak menemukan mapel.

## Interaksi

- Tab & search berfungsi nyata (client-side, tanpa fetch).
- Klik kartu/paket = postMessage (lihat ATURAN_AI.md §3).
- Tidak perlu fetch apa pun; semua angka dari KONTRAK_DATA.md.

## Batasan

- HANYA buat `workspace_modul/modul.html`. JANGAN menyentuh file lain apa pun
  (index.html, app.js, style.css, dll. sedang dikerjakan AI lain).
- CSS+JS inline di file itu. Ikut semua aturan disiplin teknis di
  ATURAN_AI.md §4 (tokens warna, font, animasi, reduced-motion).
- Bahasa UI Indonesia, singkat & lugas.

## Definition of done

- File bisa dibuka langsung di browser dan tampil benar tanpa error console.
- Semua 22 mapel tampil dengan angka soal yang benar sesuai kontrak.
- Tab filter & search berfungsi. Klik paket mengirim postMessage yang benar.
