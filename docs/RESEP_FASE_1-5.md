# RESEP FASE 1–5 — Pipeline Scraping TKA "Perfect by Default"

> Revisa 2026-09-29. Acuan resmi menjalankan swarm untuk 1 mapel baru ATAU
> bulk banyak mapel sekaligus, tanpa perbaikan manual per mapel.

## Prinsip Desain (kenapa pipeline ini aman)

1. **Setiap fase punya checkpoint.** Proses yang selesai tidak diulang:
   - Fase 1: cache `data/raw_html/<slug>.html` + `data/kunci/<slug>_kunci.json` → skip.
   - Fase 3: sidecar `data/<slug>_sidecar_transcriptions.json` → hanya gambar
     yang BELUM ada entri-nya yang ditranskripsi. Gambar chrome (logo/loader/
     ikon < 2KB) otomatis dilewati.
   - Fase 4: solusi 5-Pilar checkpoint per nomor (`data/solution_sources/`), soal
     serupa hanya dibuat untuk nomor yang kosong.
2. **Kunci resmi = satu-satunya ground truth.** Fase 2 TIDAK mengarang kunci;
   kunci yang gagal terparse dibiarkan kosong dan ditandai auditor.
3. **Auditor fase 5 adalah gate release.** Registry hanya ditulis kalau audit
   LOLOS. Kalau merah, log-nya menyebut persis soal & jenis kerusakannya.

## Alur Fase (versi terkini)

| Fase | Tugas | Mesin | Catatan anti-bug |
|---|---|---|---|
| 1 Scout | Login Playwright → simpan HTML ujian + unduh gambar + panen kunci `review_hasil` | Playwright headless | Parser kunci punya guard anti-misfire (kunci PG multi-jawaban `(C) teks (D) teks` tidak lagi terbaca sebagai matriks Benar-Salah) |
| 2 Architect | Pisah artefak Tipe A (CBT/HTML+gambar) & Tipe B (teks JSON) | BeautifulSoup | Ekstraksi teks `text_quality`-aware: rumus TIDAK pecah per karakter lagi; tag inline (`em`,`sup`) aman |
| 3 Visionary | Transkripsi gambar → teks (sidecar) | **AI Studio Playground via Playwright (gratis, batch 8 gambar/turn)** → fallback API Gemini (rotasi kunci) | Checkpoint per batch; urutan dipetakan `urutan`+`filename`; filter gambar chrome |
| 4 Reasoner | Solusi 5-Pilar + Soal Serupa | **AI Studio Playground** (jika Chrome 9222 aktif) → fallback API Gemini → fallback Qwen/Groq (syarat: semua gambar batch sudah terwakili sidecar) | Continuation guard 3x untuk nomor terlewat; deteksi selesai = teks stabil 9 detik + tombol Stop hilang; ekstraksi anti-echo-prompt |
| 5 Auditor | 9+ checklist zero-trust | Lokal (deterministik) | Cek: gambar fisik, opsi bersih, kunci kosong/mismatch, soal kosong, langkah generik/copy-tempel, soal serupa unik & bukan jiplakan soal asli, konteks tutor |

## Resep Menjalankan (2 cara)

### Cara A — Lewat Dashboard (disarankan)
1. Buka `swarm.html` → **TARGET MATRIX** → centang semua paket yang mau di-scrape.
2. **LUNCURKAN SWARM** → pantau 5 pod divisi.
3. Divisi 4 & 3 otomatis pakai **AI Studio** kalau Chrome debugging aktif
   (lihat cara B langkah 1), kalau tidak → API Gemini → fallback Groq.
4. Cek hasil: pod Divisi 5 hijau = mapel live & lolos audit. Merah = baca log
   isunya (auditor menyebut nomor soal & jenis bug-nya).

### Cara B — Lewat Terminal (kontrol penuh)
1. Siapkan AI Studio (vision & reasoning gratis):
   ```
   start_chrome_debug.bat   :: buka Chrome port 9222 dengan sesuai AI Studio
   ```
   Pastikan login akun Google di profil Chrome itu (sekali saja, tersimpan).
2. Jalankan swarm untuk target tertentu, mis. lewat dashboard atau:
   ```python
   from pipeline.swarm_manager import swarm_engine
   swarm_engine.start_swarm_pipeline(targets=["antropologi_paket_1", "antropologi_paket_2"])
   ```

## Anggaran & Kuota (kenapa jalur ini hemat)

- **AI Studio Playground = GRATIS** (pakai sesi web akun, tanpa API key).
  Dipakai untuk: vision batch (fase 3) + reasoning 5-Pilar & soal serupa (fase 4).
- **API Gemini** = cadangan. Vision free-tier dibatasi kuota HARIAN per kunci —
  jangan andalkan untuk bulk. Tambah kunci di `GEMINI_API_KEYS` (koma) untuk
  memperbesar rotasi.
- **Groq (Qwen)** = mesin tutor + fallback teks fase 4. 3 kunci round-robin,
  tidak bisa vision.
- **Aturan praktis**: selama Chrome AI Studio aktif, hampir tidak ada kuota API
  yang terpakai. Satu paket 25 soal ≈ 4 batch vision + 2-3 turn reasoning.

### Jebakan AI Studio yang sudah diatasi otomatis
1. **Mode Antigravity** — URL `new_chat` terkadang dialihkan ke "Antigravity
   Agent Preview" yang menuntut API key (Run tidak pernah jalan). Bridge
   mendeteksinya, melindungi tab playground standar dari cleanup, dan membuka
   ulang dari **URL tersimpan** (`data/aistudio_playground_url.txt`) yang
   mencatat percakapan standar terakhir yang sukses.
2. **Submit hantu** — Control+Enter tanpa fokus / Run disabled saat lampiran
   masih diproses. Sekarang: tunggu chip lampiran siap → submit → **verifikasi
   generasi mulai** (tombol Stop muncul) → fallback klik Run → retry.
3. **JSON rusak akibat kutip ganda tak ter-escape** (mis. judul bahasa asing di
   deskripsi) — instruksi melarang `"` di nilai string + ada recovery parser
   yang memotong record per marker `filename`.
4. **Echo prompt** — ekstraksi memilih turn TERAKHIR berisi JSON respons nyata
   (`"question_number": <angka>`), bukan turn prompt terpanjang.

## Re-scrape / Ulang Paket Lama — AMAN

Checkpoint membuat re-run tidak boros:
- Gambar yang sudah tertranskripsi **tidak** ditranskripsi ulang (sidecar).
- Solusi & soal serupa yang lengkap **tidak** dibuat ulang (fase 4 checkpoint).
- Yang diproses ulang hanya bagian yang bolong. Contoh kondisi 2026-09-29:
  5 gambar sisa transkripsi → cukup jalankan ulang swarm/fase 3.

⚠️ **JANGAN** jalankan ulang fase 2 secara manual pada paket yang sudah live:
fase 2 menulis ulang `*_learning.json` dari nol dan **menghapus soal_serupa** yang
sudah ada. Biarkan fase 2 hanya berjalan untuk paket BARU di dalam swarm.

## Gerbang Mutu (apa yang otomatis tertangkap)

Auditor menolak paket bila menemukan: gambar hilang/0-byte, opsi kosong/A-L,
kunci kosong atau tidak cocok `review_hasil`, soal tanpa isi, langkah solusi
generik/identik antar soal, `diketahui` copy-tempel, soal serupa hilang/duplikat/
jiplak soal asli, konteks tutor tidak lengkap.

Perbaikan tampilan (bukan data): huruf opsi "A. " dari `full_display` kini
dilepas di layer render (`app.js`) sehingga tidak dobel dengan indikator kunci.
