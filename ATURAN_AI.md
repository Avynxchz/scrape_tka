# ATURAN WAJIB UNTUK SEMUA AI (Zcode / Antigravity / lainnya)

## 1. Wilayah file — SANGAT PENTING

Beberapa AI bekerja BERSAMAAN di project ini. Setiap AI HANYA boleh membuat
mengedit file di dalam folder kerjanya sendiri:

- AI halaman MODUL   -> hanya folder `workspace_modul/`
- AI halaman PROGRES -> hanya folder `workspace_progres/`

DILARANG KERAS membuat/mengedit/menyentuh file di luar folder kerja masing-
masing, khususnya file-file yang sedang dikerjakan pihak lain:
`index.html`, `app.js`, `style.css`, `server.py`, `landing.html`,
`home_stitch.*`, `tutor_*.py`, folder `data/`, folder `pipeline/`.

Melanggar aturan ini = merusak kerja AI lain yang berjalan bersamaan.

## 2. Bentuk deliverable

- Buat SATU file HTML mandiri: `workspace_modul/modul.html`
  (atau `workspace_progres/progres.html`) — CSS + JS inline di file itu.
- Boleh pakai CDN: Tailwind, Google Fonts (Plus Jakarta Sans), Material Symbols.
- Tidak boleh butuh build step / npm / server — file harus bisa dibuka langsung.
- Semua state halaman dibaca dari `localStorage` (format lihat KONTRAK_DATA.md)
  dan dikirim lewat `postMessage` ke parent. TIDAK boleh fetch file data/
  secara langsung; angka soal sudah disediakan di KONTRAK_DATA.md.

## 3. Kontrak integrasi dengan app utama

Halamanmu akan ditanam sebagai panel di dalam app utama (bukan situs terpisah).
Karena itu:

```js
// kirim event ke app utama (contoh: user klik kartu paket):
parent.postMessage({ type: 'open-package', subject: 'fisika', pkg: 1 }, '*');

// minta data terbaru (app akan balas dengan pesan 'home-data' / 'progress-data'):
parent.postMessage({ type: 'request-data' }, '*');

// terima data dari app utama:
window.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'progress-data') { /* render */ }
});
```

- Semua tombol navigasi antar-halaman HARUS lewat postMessage di atas,
  BUKAN `location.href` (halaman di-embed, bukan standalone).

## 4. Disain & disiplin teknis

- Design tokens (WAJIB, dari Stitch):
  primary #004a2a · primary-container #1b633e · accent-mint #22C55E ·
  tertiary-fixed #ffdcc3 · tertiary #643300 · surface #f6fafe ·
  surface-card #FFFFFF · border-subtle #E2E8F0 · text-primary #0F172A ·
  text-muted #64748B · secondary #56615c
- Font: 'Plus Jakarta Sans' (400–800), ikon 'Material Symbols Outlined'.
- Radius 12–20px; shadow lembut; light mode saja.
- Mobile-first 390px, responsif sampai desktop (max-width konten 480px,
  di desktop ditengah dengan latar abu hangat).
- Hanya animasikan `transform` & `opacity`. Durasi 0.3–0.6 detik.
- Hormati `prefers-reduced-motion`: tampilkan frame akhir tanpa animasi.
- Tombol: `:active { transform: scale(.97) }`.
- Bahasa UI: Indonesia yang singkat & lugas. Tanpa emoji sebagai ikon.

## 5. Kejujuran data

- Jangan pernah menampilkan angka yang tidak berasal dari KONTRAK_DATA.md
  atau localStorage. Contoh dilarang: "Skor rata-rata 88", "Akurasi 62%",
  "12 dari 28 modul selesai" — itu data fiktif.
- Keadaan kosong diperbolehkan dan harus jelas.
