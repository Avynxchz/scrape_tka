# PLAN.md — Roadmap & Keputusan Produk

Platform latihan soal TKA/UTBK + AI Tutor. Umur proyek pendek (~1 bulan s.d. TKA selesai):
**tidak ada migrasi framework, tidak ada rewrite besar.**

Prioritas: clean editorial (serius, rapi) → mobile experience enak → conversion ke Pro
(Rp20.000/bulan, awalnya beta gratis) → kumpulkan feedback.

## Konteks teknis (hasil audit)

- App live: pure HTML + CSS + vanilla JS di root (`index.html`, `app.js`, `style.css`).
- Backend: Python stdlib (`server.py`, ThreadingHTTPServer) + SQLite (`data/ai_tutor.db`).
- AI Tutor 100% server-side (`tutor_llm.py` → Groq/Qwen default, Gemini opsional, Ollama fallback).
  API key tidak pernah ke client. Rate limit berlapis: kuota harian per user, cooldown,
  semaphore konkurensi, rotasi multi-key.
- `tka-by-v0/` = ekspor desain Next.js, TIDAK dipakai — jangan disentuh.
- Tidak ada package.json / build step. Cache busting manual via `?v=N` di `index.html`.

## Fase

| # | Fase | Status |
|---|------|--------|
| 1 | Design system + Light theme | ✅ selesai (commit Fase 1) |
| 2 | Mobile experience polish | ⬜ menunggu spek detail |
| 3 | Conversion Pro (paywall, kuota Pro) | ⬜ menunggu spek detail |
| 4 | Feedback loop | ⬜ menunggu spek detail |

## Fase 1 — Design system + Light theme (SELESAI)

Token di `:root` sesuai spesifikasi: `--bg #FFFFFF`, `--surface #FAFAF9`, `--surface-2 #F5F5F4`,
`--border #E7E5E4`, `--border-strong #D6D3D1`, `--text/#1C1917 --text-2/#57534E --text-3/#78716C`,
`--accent #1F6F4A` (+hover/tint/border), `--wrong #B42318` (+tint), `--warn #B54708` (+tint),
`--navbar #09090B`. Radius 6px kontrol / 8px kartu, shadow nyaris nol, spacing skala 4/8.

Yang dikerjakan:

- Netralkan semua permukaan: tint pastel per section (mint/lavender/ungu/amber) dihapus;
  satu aksen hijau dewasa. Merah hanya untuk salah/destruktif, amber hanya jebakan/peringatan.
- **Area soal putih**: stimulus, prompt, opsi, blok KaTeX display, dan gambar di area soal
  berlatar `#FFFFFF`.
- **Gambar soal**: `max-width:100%; height:auto; mix-blend-mode: multiply`, container putih +
  border tipis (`.stimulus-img`, `img.diagram-img`, `.opt-diagram-img`).
- **Font**: `--font-ui` (Inter) hanya nav/label/tombol/heading chrome; `--font-content` = font
  soal & math saat ini (Inter stack), tidak diubah, tidak tersentuh chrome. Tidak ada font di
  `*`; body memakai `--font-content`.
- Badge bertumpuk, pill "LANGKAH x" berwarna, icon lingkaran tinted → heading teks + angka
  tipografi mono (`01`, `02`, tabular-nums). Timer & nomor soal `tabular-nums`.
- Tombol: primary solid gelap + secondary outline. Tanpa gradient.
- Halaman kunci jawaban: hero = kunci + status verifikasi, urutan jawaban → konsep → langkah →
  tips, kolom baca ~756px (wrapper 1180px), timeline langkah flatten tanpa kartu bersarang.
- Panel Tutor AI: sidebar docked full-height (border pemisah 1px, bukan floating card),
  chat gaya dokumen (label kecil + teks, tanpa bubble navy), input pinned.
- **Light-only**: tombol & script dark mode dilepas dari UI. CSS `[data-theme="dark"]` sengaja
  dibiarkan dorman (tanpa entry point) untuk fase dark berikutnya.

## Keputusan desain penting

1. **Dark mode ditunda.** Gambar soal berlatar putih terlihat aneh di dark. Sebelum dark
   diaktifkan lagi, perlu strategi per-gambar: formula PNG di-invert (sudah ada di CSS dorman),
   scan/diagram tetap frame putih, atau re-render formula asli.
2. **Alias token lama dipertahankan** (`--accent-blue`, `--bg-card`, dst. dipetakan ke token
   baru) supaya ~3.900 baris rule lama ikut ternetralkan tanpa rewrite — sisa teknis
   dipindahkan bertahap kalau ada waktu.
3. **Tanpa framework baru.** Semua perubahan UI lewat CSS + sedikit markup; logika soal,
   penilaian, dan AI Tutor tidak disentuh.

## Definition of Done per fase

- Verifikasi visual light di desktop + lebar mobile (375px) sebelum commit.
- Commit per fase, pesan commit menyebut nama fase.
- Tidak ada perubahan logika/data soal dalam commit UI.
