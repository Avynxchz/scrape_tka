# Playbook: Bug Render Rumus Matematika → Deteksi & Solusi

> Tujuan: kalau bug yang sama muncul lagi, tinggal buka file ini — deteksi dan solusinya sudah tercetak. Pola: **ketemu bug > solve > catat > ketemu pola sama lagi > langsung solve pakai halaman ini.**

Terakhir diperbarui: 2026-09-29 (setelah sesi pembersihan menyeluruh).

---

## Prinsip dasar (kenapa bug ini terjadi)

Rumus matematika di project ini disimpan sebagai **LaTeX yang dibungkus delimiter** (`$...$` atau `$$...$$`), lalu dirender jadi simbol oleh **KaTeX** di browser (dipanggil lewat `renderMath()` di `app.js`). Bug tampilan muncul kalau salah satu dari rantai ini putus:

```
data (JSON) → dibersihkan saat serve (server.py) → dirender (app.js + KaTeX)
```

Punya user loh: `limxto3frac...`, `det(F)=(2)left(frac12 right)...`, `f(x)=x 3+3x2...` (dobel), `apit the t a theta`, `Matriks,, dan.` — semuanya varian dari 5 pola di bawah.

---

## Pola Bug #1 — LaTeX mentah tidak pernah dirender (penyebab utama contoh `limxto3frac...`)

**Gejala:** user melihat `lim_{x\to 3}\frac{x^3...}` atau `left(frac12 right)` sebagai teks polos.
**Akar:** teks berisi `$...$` tapi dimasukkan ke DOM pakai `.innerText`/`.textContent` (bukan `innerHTML`), atau dirender tanpa memanggil `renderMath(container)`.
**Lokasi pernah terjadi:** panel "soal serupa" `app.js` (prompt, opsi, feedback) — sudah difix 2026-09-29 (sekarang pakai `_fmtText()` + `innerHTML`, versi cache `app.js?v=28`).
**Solusi:**
1. Set teks via `element.innerHTML = _fmtText(teks)`.
2. Panggil `renderMath(container)` setelah render selesai.
**Deteksi:** grep `innerText =` / `textContent =` di `app.js` pada field yang bisa berisi rumus.

## Pola Bug #2 — Gema duplikat (`f(x)=x 3+3x2−10x−24f(x)=x3+3x2−10x−24`)

**Gejala:** rumus/teks tercetak 2× berdempetan; versi pertama pecah, versi kedua utuh (atau sebaliknya).
**Akar:** hasil ekstraksi DOM lama menangkap baik versi KaTeX internal (per karakter) maupun echo teks-nya.
**Solusi:** sudah ditangani `text_quality.py` (`dedupe_echo` + `_drop_token_echo`, idempoten). Kalau ada kasus baru: tambah di situ, jangan bikin normalizer baru.
**Deteksi:** `python _scan_render_garbage.py` (pola `[italic]/[frag]/[word]`).

## Pola Bug #3 — Fragmen pecah per karakter (`rigℎta r row`, `apit the t a theta`, `𝑑\n𝑒\nt`)

**Gejala:** kata LaTeX terpecah dengan karakter aneh (ℎ = U+210E) atau newline di tengah kata; angka/derajat terpisah (`30 O)` bukan `30°)`).
**Akar:** ekstraksi DOM pakai `get_text("\n", strip=True)` yang menyisipkan newline di setiap batas tag inline (`<em>`, `<sup>`), lalu model AI meniru gaya rusaknya.
**Solusi:** sudah ditangani `text_quality.py` (`map_math_unicode`, `merge_fragmented_lines`, `fix_word_symbols`, regex derajat). Varian spasi acak (`leftrigℎ t ar ow`) dibersihkan dengan replace literal — kalau muncul varian baru, tambahkan di `_scan_render_garbage.py` + cleaner.
**Deteksi:** `python _scan_render_garbage.py` + grep `igℎ|apit the|Matriks,,`.

## Pola Bug #4 — Teks ambigu/kosong (`Matriks,, dan.`)

**Gejala:** "diketahui" berisi `Matriks,, dan.` — tidak informatif, kadang konten mapel lain (trigonometri di soal Sejarah!).
**Akar:** (1) transkripsi sumber kosong/miskin sehingga AI mengarang kalimat kosong; (2) file solusi tertimpa hasil generator yang salah mapel (kontaminasi lintas-mapel).
**Solusi:** restore dari backup yang benar (kasus Sejarah P2 2026-09-29: backup `data/backup_solutions_20260929/` berisi 29 solusi benar, file aktif 20 solusi kontaminasi → di-restore). Kalau backup tidak ada → regenerate lewat swarm fase 4.
**Deteksi:** grep `"Matriks,,"` / cek jumlah solusi vs jumlah soal (`len(solutions)` harus sama dengan jumlah soal di learning JSON).

## Pola Bug #5 — Mojibake encoding (`Â°` bukan `°`)

**Gejala:** `Â°` / `Ã` muncul di teks (UTF-8 dibaca sebagai Latin-1 lalu disimpan ulang).
**Akar:** penyimpanan/penulisan file dengan encoding salah di salah satu langkah pipeline.
**Solusi:** replace `"Â°" → "°"` (sudah ada di cleaner data); `text_quality.py` sendiri sudah benar (telah diverifikasi byte U+00B0). Jangan pernah tulis file data tanpa `encoding="utf-8"`.
**Deteksi:** scan karakter U+00C2 (`Â`) di semua JSON aktif → harus 0.

---

## Pola Bug #6 — Kontaminasi lintas-target di fase 4 swarm (jawaban mapel lain dipakai untuk mapel ini)

**Gejala:** solusi mapel A berisi materi mapel lain (contoh nyata: solusi Sejarah P2 berisi "determinan matriks" dari MTK Lanjut), jumlah solusi = jumlah soal target LAIN, audit gagal "Solusi hanya mencakup 20/29 soal".
**Akar (fix 2026-09-29, bridge.py):** (1) `extract_latest_response` mengabaikan `turn_index_start` sehingga mengambil turn ber-JSON TERAKHIR dari seluruh chat; (2) fase 4 tidak membuka chat baru — 1 percakapan AI Studio dipakai ulang antar-target; (3) tidak ada guard keaslian output.
**Solusi (sudah diterapkan):** (1) `turn_index_start` diteruskan ke `page.evaluate`, pindai hanya turn >= indeks itu; (2) `run_phase_4_via_playwright` sekarang WAJIB `start_fresh_chat` (1 target = 1 chat baru, raise kalau gagal); (3) `_sanity_check_target_token` — raw output harus memuat token khas target dari learning JSON, kalau tidak → RuntimeError sebelum ditulis file.
**Deteksi:** bandingkan `data/raw_llm_outputs/<slug>_5pillar_raw.txt` antar-slug (similarity ~1.0 = kontaminasi); audit gagal "mencakup N/M soal" dengan N ≠ jumlah soal target.
**Pembersihan setelah insiden:** restore solusi dari backup bersih (atau re-run swarm), lalu hapus cache: `data/raw_llm_outputs/<slug>_5pillar_raw.txt` + `data/aistudio_playground_url.txt`.

---

## Pola Bug #7 — Korupsi on-the-fly saat serve (`pmatrix` → `±atrix` di UI, padahal file bersih)

**Gejala:** UI menampilkan `\begin{±atrix}` (rumus gagal dirender) padahal file data di disk berisi `\begin{pmatrix}` yang benar; `rg "±atrix" data/` = 0 hasil.
**Akar (fix 2026-09-29, `server.py` :: `clean_katex_artifacts`):** rule pembersih `(r'\\?pm', r'±')` TANPA batas kata menyambar substring "pm" di dalam command LaTeX `pmatrix` (juga risiko: `pm` lain, dsb.). Rule serupa (`times`, `leq`, `geq`, `cdot`, `circ`, ...) punya risiko sama (mis. "circus", "lequa").
**Solusi (sudah diterapkan):** semua 11 rule diberi batas huruf: `(?<![a-zA-Z])\\?pm(?![a-zA-Z])` — digit tetap lolos (`4times2 → 4×2`), command LaTeX utuh (`pmatrix` tidak tersentuh).
**Deteksi:** bandingkan field dari `/api/solution` dengan field file sumber di disk — kalau beda, ada korupsi on-the-fly; tes cepat: `python -c "from server import clean_katex_artifacts; print(clean_katex_artifacts('$T=\\\\begin{pmatrix}a\\\\end{pmatrix}$'))"` → harus tetap `pmatrix`.
**Pelajaran umum:** regex pembersih SEMBARI berbahaya untuk teks yang memuat LaTeX — selalu batasi dengan lookaround huruf; dan audit harus bandingkan OUTPUT SERVE vs FILE, bukan cuma scan file.

## Pola Bug #8 — Kebocoran Markdown Transkripsi & Kepadatan Rumus Inline (Bikin Mata Pusing)

**Gejala:** Panel "Tata Cara & Langkah Penyelesaian" (terutama Pilar 1 Diketahui & Steps) menampilkan karakter markdown mentah `###`, garis pemisah `---`, tabel pipa mentah `| kolom | kolom | |:---:|`, preamble teknis ("Berikut adalah ekstraksi data...", "Transkripsi Rumus:"), serta matriks besar dan rumus matematika beruntun yang menumpuk rapat dalam satu baris inline.
**Akar:**
1. AI Studio pada Fase 4 menyerap deskripsi transkripsi visual dari sidecar vision dan menyalin mentah-mentah header `###`, tabel pipa `|...|`, serta preamble prompt.
2. Template prompt 5-pilar lama belum melarang format markdown header/tabel pipa pada field `diketahui` dan belum mengatur keterbacaan baris persamaan matematika.
3. Rumus-rumus berurutan `$persamaan1$ $persamaan2$` tidak memiliki jeda newline sehingga menumpuk dalam satu baris.
4. Matriks ordo 2x1 atau 2x2 dirender inline `$ \begin{pmatrix} ... \end{pmatrix} $` sehingga tampak kecil dan terhimpit teks paragraf.
**Solusi:**
1. **Level Data (Idempoten):** Jalankan `python scratch/_fix_readability_pilar.py` — membuang preamble ekstraksi teknis, mengonversi tabel pipa markdown menjadi daftar poin terstruktur (`•`), memisahkan rumus-rumus beruntun dengan newline ganda, dan menaikkan matriks besar ke display math `$$...$$`. Backup tersimpan di `data/backup_readability_20260930/`.
2. **Level Prompt (Pencegahan Permanen):** Aturan 10 & 11 di `_build_5pillar_prompt` (`pipeline/swarm_manager.py`) secara eksplisit melarang header markdown (###), melarang tabel pipa (|...|), melarang preamble ekstraksi, mewajibkan format poin terstruktur, dan mewajibkan display math `$$...$$` untuk matriks/persamaan utama.
3. **Level Frontend & CSS:** Perkuat `_fmtText()` di `app.js` (`?v=29`) untuk membersihkan sisa header markdown, dan beri margin serta background khusus untuk `.katex-display` di `style.css`.
**Deteksi:** `python scratch/_audit_markdown_readability.py` (target: 0 header markdown, 0 tabel pipa mentah, 0 preamble ekstraksi).

---

## Rutinitas verifikasi (jalankan setelah scraping/regenerasi mana pun)

1. `python _scan_render_garbage.py` → target: hanya temuan LEGITIM (attribute `data-latex` gambar kimia boleh ada).
2. Scan kontaminasi: `"Matriks,,"` = 0; jumlah solusi tiap file = jumlah soal.
3. Scan mojibake: karakter `Â` = 0 di semua data aktif.
4. Kalau ubah `app.js`: `node --check app.js` + naikkan `?v=` di `index.html`.
5. Spot-check manual di UI: matematika (lim, frac), mtk lanjut (matriks, determinan), kimia (reaksi reversible), sejarah (tips panjang dengan panah →).
6. **Setelah swarm fase 1–5**: `python scratch/_fix_render_data_20260929.py` (cleaner idempoten — bersihkan unicode math italic dll. dari data segar) lalu `python _scan_render_garbage.py` sampai hanya tersisa temuan LEGITIM (data_latex kimia).
7. **Perhatian khusus kontaminasi**: kalau audit gagal dengan jumlah solusi tidak cocok, cek raw output lintas-slug dulu (Pola Bug #6) sebelum nebak-nebak regenerasi.

## File kunci

| File | Peran |
|---|---|
| `text_quality.py` | Normalizer teks rusak (idempoten) — satu-satunya tempat menambah rule pembersihan |
| `_scan_render_garbage.py` | Scanner pola sampah render |
| `app.js` → `renderMath()` | Mesin render KaTeX (delimiters `$`, `$$`, `\(`, `\[`) |
| `server.py` → `clean_katex_artifacts` | Bersihkan payload `/api/solution` + konteks tutor (learning JSON statis & soal_serupa TIDAK dibersihkan server → harus di level data) |
| `data/backup_render_fix_20260929_v2/` | Backup sebelum pembersihan 2026-09-29 |
| `data/backup_solutions_20260929/` | Sumber restore solusi yang benar (kasus Sejarah P2) |
