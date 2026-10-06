# DESIGN_SYSTEM_MAP.md — Kapan Pakai Sistem Desain yang Mana

Proyek ini memakai **dua** sistem desain. Keduanya hijau, tapi untuk kebutuhan berbeda.
File ini peta singkatnya — baca sebelum mengubah tampilan.

## TL;DR

| | **Editorial** (`DESIGN.md`) | **Stitch** (`ATURAN_AI.md`) |
|---|---|---|
| Inspirasi | Vercel × Notion | Dashboard mobile modern |
| Kesan | Serius, tenang, akademik | Ramah, hidup, beranimasi |
| Font | Inter (UI) + font konten soal | Plus Jakarta Sans |
| Ikon | Minimalis | Material Symbols Outlined |
| Radius / shadow | Kecil (6/8px), shadow nyaris nol | Besar (12–20px), shadow lembut |
| Dipakai di | **Halaman Soal / CBT** (`index.html` area soal, `style.css`) | **Beranda, Modul, Progres, Akun** (`home_stitch.*`, `workspace_*/`) |

## Pakai Editorial kalau...

- Kamu mengerjakan **tampilan soal, opsi jawaban, pembahasan, atau chat AI Tutor**.
- Prioritasnya: teks enak dibaca lama, hierarki jelas, tidak ada distraksi.
- Aturan: 90% permukaan netral, warna hanya untuk status (hijau = benar/aktif,
  merah = salah/destruktif, amber = peringatan). Tipografi membawa hierarki, bukan warna.

## Pakai Stitch kalau...

- Kamu mengerjakan **Beranda, Modul, Progres, atau Akun** (dashboard).
- Prioritasnya: mobile-first, kartu berwarna, animasi halus, maskot robot.
- Aturan wajib (dari `ATURAN_AI.md`): primary `#004a2a`, teks putih di atas hijau,
  radius 12–20px, hanya animasikan `transform` & `opacity`, hormati
  `prefers-reduced-motion`, mobile-first 390px.
- Panel Modul/Progres/Akun hidup di **iframe terpisah** — CSS-nya tidak boleh bocor
  ke app utama (lihat ADR-2).

## Batas wilayah (jangan campur)

- Warna/token Editorial (`--bg`, `--accent` di `DESIGN.md`) ≠ token Stitch
  (`primary #004a2a`, `surface #f6fafe` di `ATURAN_AI.md`). Jangan pakai token
  satu sistem di wilayah sistem lain.
- Dark mode: Editorial mendukung penuh; Stitch **light-only** (CSS dark dibiarkan
  dorman tanpa entry point — keputusan PLAN.md Fase 1).
- Kalau ragu: lihat file-nya. `style.css` = Editorial. `home_stitch.css` dan
  `workspace_*/*.html` = Stitch.
