# ADR-2: Template Desktop & Panel Dimuat via iframe (Bukan Inline)

- **Status:** Diterima
- **Tanggal:** 2026-10-05
- **Konteks:** Template desktop Beranda (`home_desktop.html`) dan panel Modul/Progres/Akun (`workspace_*/`) membawa CSS sendiri (Tailwind utilities + token Stitch), sementara app utama (`index.html`) memakai `style.css`/`home_stitch.css` dengan sistem Editorial.

**Keputusan:** Semua template/panel tersebut dimuat via `<iframe>`, bukan disisipkan inline. Alasannya tiga: (1) **isolasi CSS** — class utilitas Tailwind dan token Stitch (mis. `.bg-surface`, `.text-primary`) akan bertabrakan dengan class app utama bila digabung satu dokumen, dan iframe memberi batas gaya yang kedap; (2) **kemandirian kerja** — panel dikerjakan AI/worker terpisah di folder kerjanya masing-masing (`ATURAN_AI.md` §1 melarang menyentuh file di luar folder kerja), dan file HTML mandiri bisa dibuka/diuji langsung tanpa server app utama; (3) **keamanan perubahan** — perbaikan di satu panel tidak berisiko merusak layout panel lain atau halaman Soal. Konsekuensinya: komunikasi antar-panel harus lewat `postMessage` (`open-package`, `request-data`, `set-font-scale`, dsb.), state dibagi via `localStorage`, dan navigasi antar-panel wajib lewat pesan (bukan `location.href`).

- **Terkait:** ADR-1 (dual-mode beranda), `ATURAN_AI.md` §1–§3
