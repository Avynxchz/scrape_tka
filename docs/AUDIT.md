# AUDIT — Jalur kritis TKA Master

Fase 1 (T1.3), 2026-10-08 · main@`3605aab`. Jalur kritis: buka → login → pilih mapel → kerjakan → selesai → hasil → tanya AI → beli.

## Baseline performa (T1.1, analisis statis)

| Metrik | Nilai |
|---|---|
| Transfer awal `/app` (html+css+js, tanpa kompresi) | ~436 KB (`index.html` 53 KB + `app.js` 220 KB + `style.css` 155 KB + lain) |
| 5 file terbesar | `app.js` 220 KB · `style.css` 155 KB · `server.py` 86 KB · `swarm.html` 80 KB · `landing.html` 62 KB |
| Request eksternal awal | 3 font Google (Inter, Material Symbols Outlined variable penuh, Plus Jakarta Sans) + KaTeX (css+js+auto-render via jsDelivr) + (landing: Tailwind CDN) |
| Kompresi | **gzip hanya untuk JSON** (`server.py:1140`); html/css/js dikirim mentah |
| Data soal | per paket, on-demand (tidak sekaligus 22 mapel) — OK |
| Gambar soal | tanpa `loading="lazy"`, tanpa `width/height` (CLS) |
| Timer | hanya update elemen `#timerText` per detik — OK, tidak redraw layar |

Lighthouse mobile TIDAK TERVERIFIKASI (tidak ada browser headless di sesi ini); Agus ukur dengan skrip stopwatch (Lampiran I.2).

## Temuan

| ID | Sev | Lokasi | Gejala | Dampak | Perbaikan minimal | Cara verifikasi |
|---|---|---|---|---|---|---|
| A1 | A | `app.js:5493` | Timer flat 105 mnt untuk semua paket; format resmi: wajib 75 mnt, pilihan 60 mnt | Klaim "persis hari-H" salah; pacing latihan salah | Timer per kategori = `n_soal × jatah/soal` (3,0/2,5/2,4 mnt, §3.1) | timer MTK P2 = 75:00 |
| A2 | A | `data/*_learning.json` | Jml soal ≠ resmi: MTK P1 46 vs 25; B.Ind P1/P2 20/25 vs 30; B.Ing P1/P2 20/25 vs 30 | Ekspektasi hari-H salah | Data jangan diubah → tandai "format latihan" di UI (T2.7) | label tampil di modal paket |
| A3 | A | `server.py:1686` (`/api/tutor/sync_user`) | Tier `free` diberi berdasar klaim `logged_in` dari klien | Siapa saja bisa klaim login; fondasi Autopsi jebol | Verifikasi JWT Supabase di server (T2.11) | klaim palsu → tetap guest |
| A4 | A | `railway.json`, `tutor_store.py:35` | SQLite ephemeral: tulisan hilang tiap redeploy | Kuota/chat/flag/order bisa lenyap | Pindah tulis penting ke Supabase (Fase 3, disetujui) | tulis → redeploy → tetap ada |
| A5 | A | `landing.html` (FAQ) | FAQ: "kuota tetap terpotong saat jawaban gagal" — **kode sudah benar** (`server.py:1611`: potong setelah sukses) | Copy memfitnah fitur sendiri; trust | Perbaiki FAQ (T2.7) | baca FAQ |
| A6 | A | `landing.html` | Demo "45:00 · 40 soal" fiktif + klaim "persis hari-H" | Trust; melanggar larangan copy H.5 | Ganti demo jujur (T2.7) | baca landing |
| A7 | A | `landing.html` (FAQ) | "Fitur akun login sedang dikembangkan" — login Google sudah jalan | Membingungkan; menekan login (= menekan funnel) | Perbaiki FAQ (T2.7) | baca FAQ |
| A8 | A | `landing.html` | Kartu "Pro Rp20.000/bulan — gratis selama beta" usang (keputusan: Sprint Pass Rp14.900) | Menjual produk yang tidak jadi | Ganti kartu harga (Fase 8, T8.1) | — (Fase 8) |
| B1 | B | `app.js:3672,3699,3719` | `<img>` soal tanpa `loading="lazy"` | Semua gambar diunduh sekaligus; lag HP murah | Tambah `loading="lazy"` + dimensi | tab Network: gambar di bawah fold tidak diunduh |
| B2 | B | `index.html` | Material Symbols Outlined variable penuh; di jaringan lambat tampil sebagai teks ("school") | Ikon jadi teks; font berat | Subset/SVG inline (T2.1) | throttling: tidak ada teks ikon |
| B3 | B | `index.html`, `landing.html` | 3 font Google + Tailwind CDN (landing) + KaTeX selalu dimuat | Banyak request render-blocking | `font-display: swap`; KaTeX on-demand | jumlah request awal turun |
| B4 | B | `server.py:1140` | gzip hanya untuk JSON; html/css/js mentah (~436 KB) | Transfer 3–4× lebih besar dari perlu | gzip untuk html/css/js (T2.1) | header `Content-Encoding: gzip` |
| B5 | B | `app.js` (progres) | Progres hanya di `localStorage` (hilang ganti HP/hapus data) | — | Server-side attempts (Fase 3) | — (Fase 3) |
| B6 | B | — | Tidak ada error reporting klien/server (T2.8) | Bug diam-diam | Endpoint log ringan (ditunda; bukan A) | — |

**C (ringkas):** C1 `ai_tutor.db` 0-byte di root ter-commit di PR #35 (tidak sengaja; kosong, tidak berbahaya — hapus via web 1 ketuk). C2 skrip sekali-jalan `_fix_*`/`repair_*` di root jangan disentuh. C3 `Cache-Control: no-store` untuk semua aset (boros bandwidth, tapi update instan). C4 timer dari `localStorage` (bisa diubah user; tidak kritis untuk latihan).

## Pemetaan Lampiran B (T1.4)

| # | Masalah Agus | ID temuan |
|---|---|---|
| 1 | Lag di HP lemot | B1, B2, B3, B4 (A — dikerjakan Fase 2) |
| 2 | AI lambat + bug ganti model | Sudah diperbaiki PR #31 (AbortController `app.js:3894`); verifikasi di T2.3 |
| 3 | Tab modul tidak ngumpet saat scroll | Backlog B1 |
| 4 | Layout bingung | Backlog B2 (kecuali tooltip T3.7) |
| 5 | Navigasi kanan kadang macet | Cek ulang setelah perbaikan performa |
| 6 | AI salah konteks/gambar | Sudah diperbaiki PR #33 (prompt dirakit server); verifikasi di T2.2 |
| 7 | Lapor Bug belum aktif | Sudah ada PR #32 (kirim ke Supabase) |
| 8 | Teks acak `.supabase.co` di login | T2.5 — ajukan opsi (ada biaya → tidak diputuskan sendiri) |
| 9 | Chat tampilkan soal sekaligus | Backlog B3 |

## Cek format paket vs §3.1 (T1.5)

| Paket | Soal aktual | Target §3.1 | Timer aktual | Target §3.1 |
|---|---|---|---|---|
| MTK P1 | 46 | 25 ✗ | 105 mnt | 75 mnt ✗ |
| MTK P2 | 25 | 25 ✓ | 105 mnt | 75 mnt ✗ |
| B.Ind P1/P2 | 20/25 | 30 ✗ | 105 mnt | 75 mnt ✗ |
| B.Ing P1/P2 | 20/25 | 30 ✗ | 105 mnt | 75 mnt ✗ |

→ Temuan A1, A2. Agus perlu konfirmasi format ke sekolah (catatan §3.1).
