# PROMPT UNTUK ANTIGRAVITY (Gemini 3.8 Flash) — Halaman PROGRES

Copy-paste seluruh teks ini ke Antigravity, beserta isi file `ATURAN_AI.md`
dan `KONTRAK_DATA.md` dari project SCRAPE_TKA (root: D:\PROJECTS\SCRAPE_TKA).

---

Kamu mengerjakan halaman "Progres" untuk app TKA Master (platform latihan
soal TKA Pusmendik Indonesia). Project sudah berjalan; kamu HANYA membuat satu
file baru. Baca dulu dua file ini di root project dan patuhi isinya:

1. `ATURAN_AI.md`  — aturan wilayah file, kontrak postMessage, disiplin teknis
2. `KONTRAK_DATA.md` — data mapel REAL + format penyimpanan progres

## Tugasmu

Buat SATU file: `workspace_progres/progres.html` — halaman "Progres Belajar",
mobile-first (390px) dengan versi desktop (konten max-width 480px di tengah).

## Struktur halaman

1. **Header**: judul "Progres Belajar" + subjudul "Riwayat pengerjaanmu".
2. **Kartu ringkasan atas**: total soal dikerjakan (dihitung dari
   localStorage `tka_progress`), total jawaban benar, persentase ketepatan.
   Semua angka dihitung dari data NYATA. Jika kosong → tampilkan keadaan
   kosong: "Belum ada riwayat. Mulai satu paket dulu, yuk!" — JANGAN
   menampilkan angka nol besar palsu atau angka karangan.
3. **Daftar per mapel yang ADA datanya saja**: tiap baris menampilkan ikon
   Material Symbols, nama mapel (PERSIS dari kontrak), progres paket 1 &
   paket 2 (X dari N soal, N = angka REAL dari KONTRAK_DATA.md), progress
   bar, dan jumlah benar/salah.
4. **Mapel yang belum dikerjakan** dikelompokkan terpisah di bawah dengan
   tampilan redup + tombol "Mulai" yang mengirim:
   `parent.postMessage({type:'open-package', subject:key, pkg:1}, '*')`
5. **Tombol reset riwayat** kecil di bawah (dengan dialog konfirmasi) yang
   menghapus `tka_progress` dari localStorage lalu merender ulang.

## Interaksi & data

- Baca data dari `localStorage.getItem('tka_progress')` — format persis di
  KONTRAK_DATA.md (tka_progress[subject][pkg][nomor] = {kunci, benar}).
- Halaman harus tetap benar saat data kosong ATAU saat formatnya tidak valid
  (try/catch, tampilkan keadaan kosong).
- Perubahan data dari app utama datang via postMessage type
  'progress-data' — dengarkan dan render ulang.

## Batasan

- HANYA buat `workspace_progres/progres.html`. JANGAN menyentuh file lain
  apa pun (index.html, app.js, style.css, dll. sedang dikerjakan AI lain).
- CSS+JS inline. Ikut semua aturan disiplin teknis di ATURAN_AI.md §4
  (tokens warna Stitch, font Plus Jakarta Sans, Material Symbols, animasi
  transform/opacity saja, reduced-motion).
- Bahasa UI Indonesia, singkat & lugas.

## Definition of done

- File bisa dibuka langsung di browser tanpa error console.
- Dengan localStorage kosong → keadaan kosong yang jelas & jujur.
- Dengan localStorage berisi contoh data (buatkan tombol "Isi data contoh"
  yang disembunyikan di production, mis. lewat `?demo=1`) → kartu ringkasan
  dan daftar per mapel menampilkan angka yang benar.
- Klik "Mulai" mengirim postMessage yang benar.
