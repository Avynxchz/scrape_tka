# ADR-1: Beranda Pakai Dua Template (Dual-Mode)

- **Status:** Diterima
- **Tanggal:** 2026-10-05
- **Konteks:** Beranda tampil di dua konteks yang sangat berbeda — mobile (panel overlay di dalam `index.html`) dan desktop (dashboard lebar penuh).

**Keputusan:** Beranda memakai dua template: versi mobile dibangun inline di `index.html` dengan class `.stitch-*` (terintegrasi langsung dengan `app.js`: carousel hero, kartu mapel pilihan, bottom nav 57px), sedangkan versi desktop dimuat lewat iframe dari `home_desktop.html` (template Stitch desktop dengan sistem token & CSS Tailwind-nya sendiri, `vendor/tw-home_desktop.css`), yang dipilih via media query `>=900px`. Satu template responsif tunggal ditolak karena desain desktop sudah menyimpang jauh (layout 12-kolom, gutter desktop, token `primary`/`surface-container` yang tidak ada padanannya di sistem mobile), dan memaksakan satu template berarti mengorbankan kecepatan render mobile (Fase 6 menurunkan render ke 12ms justru dengan memangkas DOM) atau merusak tampilan desktop. Konsekuensinya: perubahan konten Beranda harus dilakukan di dua tempat, dan sinkronisasi data antar-mode lewat `postMessage`/`localStorage`.

- **Terkait:** ADR-2 (iframe vs inline), DESIGN_SYSTEM_MAP.md
