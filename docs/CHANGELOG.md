# CHANGELOG — TKA Master

## 2026-10-08 — FASE 0 (branch `dev`)
- docs: tambah `01_BRIEF_MUSE.md`, `02_LAMPIRAN_MUSE.md` (salinan brief kerja), `ARCHITECTURE.md` (inventaris stack + ringkasan aturan lama + temuan T0.9/T0.10), `STATUS.md`, `BACKLOG.md`.
- feat (T0.7): tabel `feature_flags` (7 flag, semua OFF) + `GET /api/flags` + `POST /api/admin/flags` (proteksi `VISITOR_ADMIN_KEY`); file baru `feature_flags.py`, edit surgical `server.py`.
- reports: `reports/FASE-0.md`.
- Commit: `b2f9450` (T0.6) · `d06381c` (T0.3+T0.8) · `2ef4551` (T0.7).

## 2026-10-10 — FASE 5 & Perbaikan Tryout (branch `dev`)
- feat(tryout): evaluasi proporsional Pilihan Ganda Kompleks (pilih 1 dari 2 kunci resmi menghasilkan skor 50% dan rincian opsi yang belum dipilih).
- feat(tryout): badge biru toska `[Pilihan Ganda Kompleks · Pilih N Jawaban]` dan indikator checkbox kotak pada opsi soal multi-jawaban.
- feat(tryout): perbaikan soal Benar/Salah — tabel evaluasi komparatif per baris (`✅ Tepat` / `❌ Berbeda`) tanpa pewarnaan merah ambigu pada pilihan "Salah" yang bernilai tepat.
- feat(autopsy): integrasi penuh alur Autopsi Belajar di server (`/api/autopsy/analyze`) dan UI (`renderAutopsiSection`). Kebocoran #1 terbuka lengkap dengan bukti berbasis angka; kebocoran #2-3 terkunci blur CSS + ajakan Paket Sprint TKA; Mode Founder tanpa blur untuk demo.
- feat(autopsy): tombol "📚 Pelajari Strategi" membuka modal Kartu Strategi Belajar (`modalKartuStrategi`, z-index 200) berisi kartu Anti-Ceroboh dan Manajemen Waktu sesuai Lampiran E Claude Sonnet.
- feat(mobile): keyboard mode adaptif untuk AI Tutor di HP, accordion 5 pilar (Pilar 1 terbuka default), auto-hide navbar dan tabs modul saat scroll di HP, perbaikan ikon Sejarah `history_edu`.
