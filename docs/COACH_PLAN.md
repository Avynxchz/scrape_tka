# RENCANA KERJA & ARSITEKTUR GURU AUTOPSI (FASE A)

Versi 1.0 · 10 Okt 2026 · Target siap uji sebelum gladi bersih 12 Okt 2026 pukul 08.00 WIB

---

## 1. Bentuk Data Attempt yang Sebenarnya

### Di Klien (`app.js` -> `AttemptRecorder`)
Saat ini `AttemptRecorder.finish()` menghasilkan payload:
- `client_id`: string unik (mis. `att_m3...`)
- `subject` / `mapel`: nama mapel (mis. `matematika`)
- `paket`: nomor paket (integer)
- `n_questions`: total soal (mis. 25)
- `duration_limit_s`: batas waktu (detik)
- `ended_by`: `user` atau `timer`
- `started_at` & `finished_at`: timestamp ISO UTC
- `items`: array of object per soal:
  - `soal_id`: string (format `subject:paket:nomor`, mis. `matematika:1:9`)
  - `position`: nomor urut soal (1..n)
  - `topic_id`: nama topik / null
  - `first_answer`: jawaban pertama (string/null)
  - `final_answer`: jawaban akhir (string/null)
  - `active_ms`: total milidetik aktif di soal
  - `first_answer_ms`: milidetik saat jawaban pertama dipilih
  - `change_count`: jumlah penggantian jawaban
  - `flagged_ragu`: boolean penanda ragu-ragu
  - `visit_count`: frekuensi kunjungan ke soal

### Di Server (`server.py` & Supabase `attempts`)
- Endpoint `POST /api/attempts` memvalidasi JWT user via Supabase, membaca payload, dan memfilter `items` ke `clean_items`.
- Data disimpan di Supabase tabel `attempts` pada kolom JSONB `items`.
- **Akar masalah error "Items tidak valid":**
  1. Validasi saat ini: `if not isinstance(items, list) or not (1 <= len(items) <= 200): return 400`. Jika `items` dikirim sebagai dictionary bertingkat `{ "1": {...} }` (struktur internal `AttemptRecorder.active.items`), atau jika array kosong `[]`, server langsung menolak dengan 400 tanpa penjelasan detail.
  2. Server tidak mencatat log diagnostik (`logging.warning`) mengenai tipe data atau panjang payload yang ditolak, sehingga sulit di-debug di HP.
  3. **Solusi A1:** Normalisasi di server: jika `items` adalah `dict`, ekstrak `list(items.values())`. Jika `items` berupa string JSON, parse kembali. Berikan pesan log rinci di server jika payload benar-benar rusak.

---

## 2. Status Perekaman Data & Kebutuhan `jejak`

| Data Field | Status Saat Ini | Kebutuhan untuk Guru AI (`coach_input_v1`) |
|---|---|---|
| `first_answer`, `final_answer` | Sudah direkam di `AttemptRecorder` | Diperlukan untuk mendeteksi `overthinking` |
| `active_ms` | Sudah direkam (ms) | Tambahkan `waktu_detik = round(active_ms / 1000)` |
| `change_count` | Sudah direkam | Normalisasi ke `ganti_jawaban` |
| `flagged_ragu` | Sudah direkam | Normalisasi ke `ragu` (boolean) |
| **`jejak`** (kronologi aksi) | **BELUM ADA** | **Wajib ditambah di A1:** array maks 5 event `[{"t_detik": N, "aksi": "pilih"|"ganti"|"ragu", "opsi": "..."}]` |

Perekaman `jejak` ditambahkan pada `AttemptRecorder.onAnswer` dan `AttemptRecorder.onRagu` di `app.js` secara ringan, tanpa overhead memori, dan dikirim sekali saat `finish()` dipanggil di `selesaiTes`.

---

## 3. Pre-Mortem: 6 Skenario Gagal & Mitigasi

1. **AI Timeout (>25s saat jaringan/provider macet):**
   - *Risiko:* UI gantung menunggu respon AI, murid di HP menutup halaman.
   - *Mitigasi:* Timeout ketat 25 detik (`COACH_TIMEOUT_S`), 1x retry instan ke provider/key lain. Jika tetap timeout, otomatis jatuh ke `autopsy/coach_template.py` (template deterministik dengan struktur sama persis).
2. **Respons AI JSON Rusak / Halusinasi Format:**
   - *Risiko:* JSON parse error atau field melenceng dari skema `coach_output_v1`.
   - *Mitigasi:* Pakai response_format JSON jika didukung provider. Server memvalidasi struktur, tipe data, dan batas karakter maksimal sebelum menyimpan/mengirim ke klien. Jika tidak valid, fallback ke template cadangan.
3. **Kuota Habis (429 Rate Limit / Budget Cap):**
   - *Risiko:* User gagal mendapat autopsi atau server error 500.
   - *Mitigasi:* Evaluasi kuota harian dari baris riwayat di database (`COACH_DAILY_PER_USER=3`, `COACH_DAILY_GLOBAL=150`). Rotasi key otomatis dengan cooldown 20s. Jika kuota habis, layani langsung via template cadangan tanpa pesan error mentah.
4. **HP Lemot (Device Freeze / Lag saat Render):**
   - *Risiko:* CSS blur berat dan re-render DOM berlebihan membuat browser HP murah lag.
   - *Mitigasi:* Paywall blur dihapus (sesuai Keputusan Agus). UI bersifat progresif: metrik aturan (skor, kebocoran) tampil seketika (<1 dtk), bagian Guru AI menampilkan skeleton ringan lalu menginjeksi HTML tanpa me-reload halaman.
5. **Attempt Gagal Tersimpan / Jaringan Putus:**
   - *Risiko:* Hasil tryout hilang saat klik Selesai Tes di koneksi buruk.
   - *Mitigasi:* `AttemptQueue` di `localStorage` menyimpan attempt secara lokal. Mengirim sekali saat selesai, dan jika gagal akan di-retry otomatis saat event `online` atau kunjungan berikutnya. Idempotency `client_attempt_id` mencegah data ganda.
6. **Klaim AI yang Salah / Mempermalukan Murid:**
   - *Risiko:* AI menyebut angka yang tidak ada di data, atau memakai kata merendahkan.
   - *Mitigasi:* Prompt persona ketat (`autopsy/coach_prompt_v1.txt`). Validator server memeriksa nomor soal ∈ `fokus_soal`, membatasi toleransi angka asing (maks 2 angka di luar evidence), serta memblokir kata terlarang (bodoh, malas, pasti lolos, dll). Jika melanggar, ganti dengan template cadangan.

---

## 4. Urutan Kerja Terarah

- **A0 (Aktif):** Peta dan rencana (`docs/COACH_PLAN.md`), audit kontrak data dan file panduan.
- **A1:** Perbaiki simpan attempt di `server.py` (toleransi bentuk data nyata + logging) dan rekam `jejak` di `app.js` (`selectOption`, `AttemptRecorder`, `selesaiTes`). Uji simpan & idempotency.
- **A2:** Implementasi Evidence Builder `autopsy/evidence.py` (fungsi murni: attempt + analyzer + planner -> `coach_input_v1`). Uji unit 3 persona.
- **A3:** Implementasi Layanan Guru AI `autopsy/coach.py` + endpoint `/api/autopsy/coach` (LLM call, timeout 25s, key rotator, validasi ketat 6.3, cache per attempt).
- **A4:** Implementasi Template Cadangan `autopsy/coach_template.py` (skema output identik, deterministik, berbasis data nyata).
- **A5:** Kuota & Biaya (perhitungan berbasis database, fallback template jika habis).
- **A6:** UI Layar Hasil (mobile-first 390px, progresif, hapus blur/paywall, input tanggal TKA).
- **A7:** Pengujian menyeluruh (3 persona end-to-end, uji gagal, uji bobol prompt, uji keamanan).
- **A8:** Laporan final `reports/COACH-A.md`.

---

## 5. Pertentangan Dokumen Lama vs Baru

1. **Akses Guru AI:** Dokumen lama (`01_BRIEF_MUSE.md`) membatasi AI narrative hanya untuk pemegang pass berbayar. *Aturan baru:* Guru AI gratis untuk semua user yang login dengan batas kuota harian.
2. **Paywall:** Dokumen lama menerapkan blur CSS dan paywall Paket Sprint pada kebocoran #2-3. *Aturan baru:* Paywall dan blur dimatikan total.
3. **Penyimpanan Autopsi:** Dokumen lama merencanakan tabel `autopsies` terpisah dengan kolom `analysis`, `plan`, `narrative`. *Aturan baru:* Simpan hasil coach aditif pada database per attempt dengan migrasi aman tanpa merusak skema yang ada.
