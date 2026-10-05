# BRIEF UNTUK GUA (AutoClaw) — Dashboard Beranda versi Desktop

*(catatan kerja internal — bukan untuk AI lain)*

## Tugas
Versi desktop dari Home/Beranda: layout 2 kolom — kiri: hero + ringkasan
progres; kanan: section mapel (grid multi-kolom, bukan carousel horizontal).
Mobile tetap pakai `home_stitch.*` yang sudah jadi (tidak diubah).

## Wilayah file (isolasi, sesuai ATURAN_AI.md)
- Buat `home_desktop.css` + patch kecil di `index.html` (media query ≥900px)
  HANYA setelah Zcode & Antigravity selesai, saat integrasi akhir.
- Jangan sentuh `workspace_modul/`, `workspace_progres/`.

## Kontrak
- Data: KONTRAK_DATA.md (961 soal, 22 mapel, 44 paket).
- Progres: localStorage `tka_progress` (sudah dibaca oleh homePkgProgress).
- Event: postMessage open-package (sudah dipakai home_stitch).

## Urutan integrasi akhir (setelah semua AI selesai)
1. Verifikasi modul.html & progres.html terhadap kontrak (angka, postMessage).
2. Pasang keduanya sebagai panel di index.html, sambungkan bottom nav Stitch
   (Beranda/Modul/Progres) ke toggle panel — satu app, tiga panel.
3. Ganti bump cache `?v=` untuk style.css & script.
4. Uji end-to-end (Playwright): nav antar panel, klik paket, progres naik
   setelah menjawab soal, reduced-motion.
