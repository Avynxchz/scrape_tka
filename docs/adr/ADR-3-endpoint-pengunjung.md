# ADR-3: Endpoint `/pengunjung` Terpisah dari API Publik

- **Status:** Diterima
- **Tanggal:** 2026-10-06
- **Konteks:** Server mencatat kunjungan (IP, user-agent, halaman) di `visitor_log.py` dan Agus butuh dashboard untuk melihatnya, tetapi data ini sensitif (bisa membocorkan pola trafik & identitas pengunjung) dan tidak boleh terekspos saat server dibagikan publik via tunnel (`bagikan_online.bat`, `PUBLIC_DEMO=1`).

**Keputusan:** Dashboard pengunjung disajikan di endpoint khusus `/pengunjung` (halaman `pengunjung.html`) + `/api/admin/visitors`, terpisah dari endpoint API publik, dengan tiga lapis proteksi: (1) wajib query `?key=` cocok dengan `ADMIN_KEY` dari env (fail-fast: server menolak start bila tidak diset), (2) seluruh path (`/pengunjung`, `/pengunjung.html`, `/api/admin/visitors`) otomatis 403 saat `PUBLIC_DEMO=1`, dan (3) respons memakai `Cache-Control: no-store`. Endpoint terpisah dipilih — bukan sekadar flag admin di API umum — agar aturannya eksplisit dan gampang diaudit: satu daftar `ADMIN_VISITOR_PATHS` di `server.py` yang bisa dicek sekilas, tanpa risiko aturan auth tercecer di tiap handler. Konsekuensinya: Agus harus menyimpan kunci admin di `.env` (tidak pernah di-commit), dan dashboard hanya bisa dibuka di server utama, bukan lewat link demo publik.

- **Terkait:** `server.py` (`ADMIN_VISITOR_PATHS`), `visitor_log.py`, PLAN.md §"Bagikan online"
