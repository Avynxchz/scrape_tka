# PLAN.md — Roadmap, Status & Keputusan Produk

Platform latihan soal TKA/UTBK + AI Tutor. Umur proyek pendek (~1 bulan s.d. TKA selesai):
**tidak ada migrasi framework, tidak ada rewrite besar.**

Prioritas: clean editorial (serius, rapi) → mobile experience enak → conversion ke Pro
(Rp20.000/bulan, awalnya beta gratis) → kumpulkan feedback.

## Konteks teknis (hasil audit)

- App live: pure HTML + CSS + vanilla JS di root (`index.html`, `app.js`, `style.css`).
- Backend: Python stdlib (`server.py`, ThreadingHTTPServer) + SQLite (`data/ai_tutor.db`).
- AI Tutor 100% server-side (`tutor_llm.py` → Groq/Qwen default, Gemini opsional, Ollama
  fallback). API key tidak pernah ke client. Enforcement kuota tetap di server.
- `tka-by-v0/` = ekspor desain Next.js, TIDAK dipakai — jangan disentuh.
- Tidak ada package.json / build step. Cache busting manual via `?v=N` di `index.html`
  (saat ini v=45) — bump setiap mengubah `style.css`/`app.js`.

## Status fase (SEMUA SELESAI)

| # | Fase | Commit | Status |
|---|------|--------|--------|
| 1 | Design system + Light theme | `4801b9b` | ✅ |
| 2 | Mobile experience | `a3c9f34` | ✅ |
| 3 | Landing + Pricing + Legal | `e5b35dd` | ✅ |
| 4 | Kuota & plan | `2924a78` | ✅ |
| 5 | Feedback non-intrusif | `8fd43fd` | ✅ |

### Fase 1 — Design system + Light theme
- Token `:root` (DESIGN.md): `--bg #FFFFFF`, `--surface #FAFAF9`, `--accent #1F6F4A`,
  `--wrong #B42318`, `--warn #B54708`, `--navbar #09090B`. Radius 6/8px, shadow nyaris nol.
- Semua tint pastel per section dihapus; satu aksen hijau. Merah = salah/destruktif,
  amber = jebakan/peringatan.
- Area soal putih; gambar soal `mix-blend-mode: multiply` + container putih border tipis.
- `--font-ui` (Inter) hanya chrome; `--font-content` = font soal/math (tidak diubah).
- Badge bertumpuk & pill "LANGKAH" dihapus → tipografi; tombol primary solid + secondary
  outline; timer & nomor `tabular-nums`.
- Kunci jawaban: hero kunci + status, urutan jawaban → konsep → langkah → tips.
- Panel Tutor docked (border pemisah), chat gaya dokumen.
- **Light-only**: CSS `data-theme="dark"` dibiarkan dorman tanpa entry point.

### Fase 2 — Mobile experience
- Top bar: menu (mapel & paket), "Soal x/n", timer, overflow (Daftar Soal / Selesai Tes).
- Progress line tipis di bawah top bar; progress utama tetap ada di header soal.
- Konten satu kolom; teks soal & opsi ≥16px; padding 16px; opsi min-height 56px.
- Sticky bottom bar + safe-area: Sebelumnya | Cek Jawaban (primary) | Selanjutnya | Ragu |
  Tutor. In-card action bar dipindah jadi fixed bar lewat CSS (ID/handler tidak berubah).
- Tutor AI = bottom sheet (drag handle, backdrop, Escape); tinggi via `visualViewport`
  (`--vvh`) + dvh agar composer tidak tertutup keyboard.
- Daftar Soal jadi bottom sheet; input ≥16px (anti zoom iOS); tanpa horizontal scroll
  di 360/390/430 (terverifikasi); lazy-load + async decode gambar soal.

### Fase 3 — Landing + Pricing + Legal
- `/` → `landing.html`; `/app` → `index.html` (deep link `?subject=&paket=` tetap jalan);
  `/privacy`, `/terms` → draf dengan banner "perlu ditinjau".
- Struktur landing: hero + CTA, cara kerja 3 langkah, 3 fitur, pricing 3 kolom
  (Tamu 5/hari · Terdaftar 20/hari "segera" · Pro Rp20.000/bln "gratis selama beta"),
  FAQ, footer. Tanpa social proof/k klaim yang dikarang.

### Fase 4 — Kuota & plan
- Kuota: **Guest 5 / Free(login) 20 / Pro 100** per hari; satuan = 1 pesan user.
- Reset pakai tanggal **WIB** (`_today_wib`) → tepat 00:00 WIB, bukan tengah malam server.
- Migrasi: user lama tier 'free' (belum pernah ada auth) → 'guest'; user baru default
  'guest'. `_daily_limit(tier)` satu sumber kebenaran; enforcement tetap server-side.
- UI konsisten (badge 5/5, pesan habis menyebut reset 00.00 WIB + Pro 100/hari).
- Pro di fase beta = tier 'subscriber' yang diaktifkan manual di DB
  (`UPDATE ai_tutor_users SET tier='subscriber' WHERE user_key=...`).

### Fase 5 — Feedback non-intrusif
- Timing satu config (`FEEDBACK_CFG` di app.js): notif #1 setelah 3 menit pemakaian aktif
  (posisi atas), #2 setelah 5 menit aktif berikutnya (posisi bawah). Maks 2/sesi.
- "Aktif" = tab visible + interaksi <90 detik. Tidak muncul saat mengetik di Tutor,
  saat timer <5 menit, atau di landing. Setelah kirim: suppress 14 hari (localStorage).
- `POST /api/feedback`: validasi rating 1-5 + pesan ≤1000 char; rate limit per sesi
  (jeda 10 menit, maks 3/24 jam); tabel SQLite `feedback(rating, message, device, plan,
  created_at)`.

## Cara run

1. `start_server.bat` (meload `.env` lalu `python server.py`) atau `python server.py`.
2. Server jalan di `http://localhost:8080` (env `PORT` untuk ubah).
3. Landing di `/`, aplikasi di `/app`. Setelah mengubah `server.py`/`tutor_store.py`
   **wajib restart server**; setelah mengubah `style.css`/`app.js` bump `?v=N` di
   `index.html`.

## Env yang relevan

| Var | Fungsi |
|-----|--------|
| `PORT` | Port server (default 8080) |
| `OPENAI_COMPATIBLE_BASE_URL` + `LLM_API_KEYS` + `LLM_MODEL` | Provider AI utama (Groq/Qwen, multi-key round-robin) |
| `GEMINI_API_KEYS` | Provider Gemini opsional untuk Tutor |
| `OLLAMA_BASE_URL` | Fallback lokal |
| `RATE_LIMIT_COOLDOWN_SEC`, `RATE_LIMIT_MAX_PER_MIN` | Anti-spam per user |
| `LLM_MAX_CONCURRENT` | Antrean konkurensi LLM |
| `TUTOR_DB_PATH` | Lokasi SQLite (default `data/ai_tutor.db`) |
| `BILLING_MODE` | Belum diimplementasikan — label beta di-hardcode di landing.html |

Jangan pernah commit `.env`.

## Ditunda / TODO

- **Google OAuth** — TODO jika sempat; saat ini Pro diaktifkan manual via tier DB.
- **Billing nyata** (pembayaran Pro) — landing menandai "segera"; label beta hardcode.
- **Dark mode** — CSS dorman ada; butuh strategi gambar soal (formula PNG invert sudah
  disiapkan, scan/diagram perlu frame putih) sebelum diaktifkan lagi.
- **aspect-ratio gambar soal** — dimensi asli gambar tidak tersimpan di data; lazy-load
  sudah dipasang, CLS penuh menunggu metadata dimensi.
- **Halaman "Terdaftar"** — menunggu auth; pricing menampilkan badge "segera".
- Halaman privacy/terms masih draf — perlu ditinjau sebelum dipublikasikan luas.

## Bagikan online untuk demo/feedback

- **Nyalakan**: double-click `bagikan_online.bat` → otomatis menyalakan server demo
  (port 8081, `PUBLIC_DEMO=1`), tunnel cloudflared (fallback ngrok), lalu menampilkan
  link publik `https://xxx.trycloudflare.com` untuk dibagikan.
- **Matikan**: jalankan `matikan_bagikan.bat`, atau Ctrl+C di jendela skrip.
- Keamanan saat demo: endpoint admin dimatikan (`/api/tutor/reset_quota`, `/api/swarm/*`,
  `/api/ai-tutor` → 403), tombol Reset kuota disembunyikan di UI (muncul lagi dengan
  `?admin=1` atau `localStorage.tka_admin='1'`), kuota tamu 5/hari tetap berlaku.
- URL quick tunnel berubah setiap kali nyalakan. Mau link permanen → pakai ngrok
  (sudah terauth di mesin ini) atau domain sendiri.
- Feedback penguji terkumpul di tabel `feedback` SQLite:
  `python -c "import sqlite3; c=sqlite3.connect('data/ai_tutor.db'); print(c.execute('SELECT rating, message, device, created_at FROM feedback ORDER BY id DESC LIMIT 20').fetchall())"`

## Audit konten oleh AI (fetch-only model, mis. Claude)

- `/audit?subject=&paket=&dari=&sampai=` → HTML statis; `/audit.txt?...` → teks polos.
- Regenerate file paste untuk chat AI:
  `python -c "import server,io; io.open('exports/audit/matematika_paket1_soal1-15.txt','w',encoding='utf-8').write(server.render_audit_text('matematika',1,1,15))"`
- File siap-paste ada di `exports/audit/` (di-gitignore; regenerate kapan saja).
- Catatan host tunnel: `*.trycloudflare.com` robots.txt-nya milik Cloudflare (memblock
  crawler AI), ngrok free punya interstitial untuk browser-UA — keduanya tidak bisa
  dimatikan dari sisi kita. Jalur paling andal untuk model fetch-only: paste file teks.

## Audit ronde 2 (Kimi K3, salinan beku) — 3 Okt 2026

Temuan & tindak lanjut (commit `0fbac08`..ini):
- **T-08 kunci bocor antar soal** (buka pembahasan sekali → kunci 46 soal tampil otomatis
  saat navigasi) → pembahasan kini tertutup otomatis di soal yang belum dijawab.
- **Halaman /audit.txt buta formula** → T-02/T-03/T-09–T-16 ternyata mayoritas ARTIFAK
  ekstraksi, bukan bug app (datanya lengkap: img & data-latex). Difix: data-latex
  direkonstruksi jadi $..$, tabel jadi baris teks, alt/filename gambar dipertahankan,
  field html diprioritaskan di atas text.
- **Karakter kontrol peninggalan escape LaTeX** (`\frac`→FF+rac, `\rightarrow`→CR+ightarrow;
  audit T-27/T-21) → direkonstruksi di `clean_katex_artifacts` (render fix untuk semua mapel).
- **T-32/T-19/T-01 label internal & pembahasan sirkular** ("Kunci Pusmendik [...]",
  "Sesuai penetapan kunci resmi…") → disanitasi di render layer, semua mapel.
- **T-07 Fisika #1**: kunci C:Salah bertentangan dengan pembahasan sendiri (v_B = 10 m/s
  mendukung C:Benar) → kunci diselaraskan ke C:Benar.
- **T-05 MTK P2 #9**: langkah ditulis ulang dengan solusi SPLTV hasil hitung ulang auditor
  (m=16.000, l=13.000, a=14.000 → 115.000 = kunci D) + flag review.
- **needs_manual_review** di-set untuk soal yang perlu sumber asli (gambar) sebelum bisa
  diperbaiki: MTK P2 #5 & #15, MTK P1 #31 & #35.
- **T-37/T-29**: FAQ landing tak lagi klaim "diverifikasi"; /privacy dapat bagian
  Pengendali Data (placeholder wajib diisi).
- **T-39**: chip AI Tutor kini wrap, tidak terpotong.
- **T-25** (LaTeX rusak di tabel reviu): renderMath sudah dipanggil — kasus #15 bermula
  dari latex kunci yang rusak di data; ditandai via review flag MTK P2 #15.

## Utang konten (status setelah membaca gambar sumber — 3 Okt 2026)

Gua (model) Membaca langsung gambar sumber (tabel siswa, fungsi diskon, diagram ruangan,
grafik wisatawan) dan menulis ulang 4 soal:

1. **MTK P2 #5 — SELESAI**: gambar fungsi terbaca (y=0,9x; g(y)=0,7y rapor>90; 0,8y
   85–90; tabel siswa Andi 90/285rb, Budi 92/286rb, Cici 89/280rb, Dini 95/287rb).
   Keempatnya mampu membayar → kunci resmi B salah, diganti **D** + pembahasan
   per-siswa. Flag review tetap (konfirmasi kunci resmi Pusmendik).
2. **MTK P2 #15 — SEBAGIAN**: diagram terbaca (4×6 m, tinggi 5 m) → tali = √40 ≈ 6,32 m
   (bukan ≈5), 2 tali = 12,65, sisa ≈ 7,35 m — **tidak ada di opsi** (6/10/11/13/15).
   Pembahasan ditulis ulang dengan hitungan benar + catatan mismatch; flag review tetap
   (butuh koreksi opsi/stimulus dari sumber resmi).
3. **MTK P1 #31 — SELESAI**: grafik (Australia 120, China 85, Malaysia 65, Jepang 40
   ribu) + tabel aktivitas terbaca. Pernyataan C terbukti BENAR (Belanja Jepang
   30%×40.000 = 12.000 < Belanja China 40%×85.000 = 34.000) → kunci resmi C:Salah
   salah, diganti **C:Benar** + pembahasan per-pernyataan dengan angka nyata. Flag
   review tetap (konfirmasi resmi).
4. **MTK P1 #35 — SELESAI**: soal pecahan ¼ + ¾ × ⁸⁄₂₁ = ¹¹⁄₁₂ (opsi C) — pembahasan
   generik ditulis ulang jadi langkah nyata; flag review dihapus.
5. **Fisika #1 — SELESAI**: diagram & pernyataan terbaca; C (v_B = 10 m/s) terbukti
   benar secara fisika (t_A = 0,4 s dari h = 0,8 m; v_B = 4/0,4). Kunci sudah
   diselaraskan sebelumnya; tidak perlu tindakan lanjutan.

Sisa utang konten: Bahasa Arab berbasis gambar (aksesibilitas, besar), Sosiologi #2
mismatch tipe soal, hygiene kecil (typo Kimia, notasi Geografi, duplikasi kata).
