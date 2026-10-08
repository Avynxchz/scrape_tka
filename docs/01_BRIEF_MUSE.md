# BRIEF KERJA MUSE — Proyek TKA Master

Versi 1.1 · disusun oleh Claude untuk Agus · 8 Okt 2026 (diperbarui setelah membaca halaman repo)

> **Perintah pertama.** Baca Bagian 1–4 sampai habis. Lalu kerjakan **FASE 0 saja**, tulis laporannya, dan **berhenti sampai Agus bilang "lanjut"**. Bagian 5 dikerjakan satu fase per giliran. File `02_LAMPIRAN_MUSE.md` dibaca hanya saat sebuah tugas merujuknya (mis. "Lampiran C").

---

## 1. Peran

| Siapa | Peran |
|---|---|
| **Agus** | Pemilik proyek. Bukan programmer (membangun dengan bantuan AI). Memutuskan hal bisnis dan memverifikasi di HP. Butuh langkah klik-demi-klik, file jadi (bukan potongan kode untuk disalin), dan bahasa Indonesia santai tanpa jargon. |
| **Claude** | Arsitek dan reviewer di chat terpisah. Agus mengunggah laporan fasemu ke Claude; Claude memberi go/no-go dan koreksi. Karena itu laporan harus bisa dipahami tanpa konteks tambahan. |
| **Muse (kamu)** | Eksekutor di repo: menulis kode, migrasi, tes, dokumentasi, dan laporan. |

**Ritme kerja: satu fase → laporan → STOP → "lanjut" dari Agus.** Satu-satunya pengecualian: hotfix severity A.

---

## 2. Tujuan dan definisi sukses

**Tujuan.** Dalam ±7 hari (target live 15 Okt 2026; ujian TKA SMA mulai 26 Okt) ubah TKA Master dari "latihan soal + kuota AI Tutor" menjadi "latihan soal + **Autopsi Tryout**": perilaku mengerjakan (waktu, ganti jawaban, tanda Ragu-ragu) dianalisis menjadi *kebocoran* dan *rencana belajar harian sampai hari ujian*. Fitur penuhnya dijual sebagai **Paket Sprint TKA** (sekali bayar, aktif sampai hari ujian, bukan langganan) lewat QRIS manual + panel admin. Semuanya harus stabil di HP murah.

**Definisi sukses saat rilis:**
1. Mulus di dua HP lemot milik teman Agus (yang sebelumnya lag): tidak crash dan tidak tersendat sampai soal terakhir.
2. Tryout merekam waktu, jawaban, ganti jawaban, dan Ragu-ragu per soal dengan akurat, tahan crash/refresh/offline.
3. Setelah tryout, user yang login melihat Autopsi preview (gratis); pemegang pass melihat Autopsi penuh + rencana harian sampai tanggal TKA-nya.
4. Alur beli jalan: order → QRIS + nominal unik → konfirmasi WA → admin tandai lunas → pass aktif. Semua pengecekan hak akses di server.
5. AI dipanggil (untuk narasi Autopsi) hanya bagi pemegang pass, dengan batas biaya harian dan fallback template.
6. Funnel 7 angka terlihat di `/admin/funnel`.
7. Setiap fitur baru bisa dimatikan lewat flag; ada runbook dan rencana rollback.
8. Tidak ada rahasia di kode/klien; user tidak bisa membaca atau mengubah data user lain, dan tidak bisa memberi dirinya sendiri pass.

---

## 3. Fakta dan keputusan

### 3.1 Format TKA SMA 2026 (simpan di `config/exam.json`; jangan tanam angka di kode)

| Mapel | Soal | Durasi | Jatah per soal |
|---|---|---|---|
| Matematika (wajib) | 25 | 75 mnt | 3,0 mnt |
| Bahasa Indonesia (wajib) | 30 | 75 mnt | 2,5 mnt |
| Bahasa Inggris (wajib) | 30 | 75 mnt | 2,5 mnt |
| Mapel pilihan 1 dan 2 | 25 | 60 mnt | 2,4 mnt |

- Ujian utama 26 Okt–8 Nov 2026 (tergantung gelombang sekolah), **satu mapel per hari**. Susulan pertengahan–akhir Nov. Hasil diumumkan 23 Des 2026. Gladi bersih (±5–18 Okt) hanya latihan teknis; tidak dimodelkan.
- **Asumsi urutan hari:** Bahasa Indonesia → Bahasa Inggris → Matematika → pilihan (Matematika di hari ke-3). Simpan sebagai `EXAM_DAY_OFFSET = {bin:0, big:1, matematika:2, pilihan:3}` dan tandai "perlu konfirmasi jadwal sekolah".
- Sumber: pemberitaan Medcom dan Metro TV, dicek 8 Okt 2026. Agus akan mengonfirmasi ke sekolah/situs resmi. Jika konfigurasi paket di aplikasi berbeda dari tabel ini, itu **temuan severity A** di Fase 1.

### 3.2 Keputusan bisnis dan default

Default dipakai kalau Agus belum menjawab. Tandai di kode dan laporan dengan `TODO-AGUS`.

| Item | Default | Catatan |
|---|---|---|
| Nama paket | Paket Sprint TKA | sekali bayar, tanpa perpanjangan otomatis |
| Harga dasar | Rp14.900 | env `PASS_PRICE` |
| Masa aktif | sampai (tanggal hari pertama TKA user + 4 hari) pukul 23.59 WIB | dihitung di server |
| Pembayaran | QRIS statis atas nama orang tua Agus + nominal unik + konfirmasi WhatsApp | env `QRIS_IMAGE_URL`, `WA_NUMBER` |
| Aktivasi | manual oleh admin, target ≤ 1 jam (07.00–22.00 WIB) | |
| Refund | 24 jam setelah aktif, manual | `TODO-AGUS` konfirmasi |
| Komisi referral | 25% dari harga dasar per order lunas | kode dibuat manual oleh admin |
| Batas biaya AI | Rp50.000/hari | env `AI_DAILY_BUDGET_IDR` |
| Mapel pertama Autopsi | Matematika saja | config `autopsy_mapel` |
| Bonus pass | kuota AI Tutor 100/hari | gratis: tamu 5, login 25 |

### 3.3 Konteks produk

- Situs live: https://tka-master.up.railway.app (landing `/`, aplikasi `/app`). 22 mapel, Paket 1 dan 2, soal bersumber dari simulasi Pusmendik. Fitur yang sudah ada: Pilar 1–5 (pembahasan bertahap), Soal Serupa, tombol **Ragu-ragu**, AI Tutor multi-provider (Groq, OpenRouter, Gemini, Alibaba; rotasi key), login Google.
- **Repo (PUBLIK):** https://github.com/Avynxchz/scrape_tka. Pengamatan Claude dari halaman repo (belum membaca `server.py`): backend Python (`Procfile`: `python server.py`), front-end HTML/CSS/JS statis (`app.js`, `index.html`, `modul.html`, `progres.html`, `landing.html`), data soal di `data/`, database SQLite `ai_tutor.db` yang **ter-commit di repo**, `.env.example` dengan `LLM_API_KEYS` (beberapa key Groq dari beberapa akun, diputar round-robin) dan `VISITOR_ADMIN_KEY`. Banyak skrip sekali-jalan di root (`_fix_*`, `_repair_*`, `_fill_*`, `repair_*`, `enrich_*`) dan dokumen aturan lama (`ATURAN_AI.md`, `AI_DESIGN_RULE.md`, `DESIGN.md`, `KONTRAK_DATA.md`, `PRD.md`, `PLAN.md`, `HANDOVER_PROMPT.md`). Karena repo publik, apa pun yang di-commit bisa dibaca siapa saja.
- Progres saat ini tersimpan **di perangkat** (belum ada rekaman per user di server). Kuota AI: tamu 5/hari, login 25/hari, "Pro" 100/hari (selama beta semua gratis).
- 90% pengguna di HP, banyak HP murah, jaringan tidak stabil.
- Landing masih menampilkan demo "45:00 · 40 soal" dan kartu harga "Pro Rp20.000/bulan"; FAQ menyebut kuota tetap terpotong saat jawaban gagal terkirim dan menyebut login "sedang dikembangkan" padahal tombol Login Google sudah ada. Daftar masalah dari Agus ada di Lampiran B.
- Soal bersumber dari Pusmendik: jangan mengklaim situs ini resmi; pertahankan disclaimer "bukan situs resmi" dan "pembahasan dibantu AI, bandingkan dengan kunci resmi".

---

## 4. Aturan main (WAJIB — melanggar berarti tugas dianggap gagal)

### 4.1 Bukti, bukan klaim
- Status tugas hanya boleh: `SELESAI-TERVERIFIKASI` (ada bukti otomatis: output tes, angka, diff), `SELESAI-MENUNGGU-CEK-AGUS` (perlu dicek manual; sertakan langkahnya), `SEBAGIAN`, `BELUM`, `DIBLOKIR`.
- Dilarang menulis "Fixed" atau "Selesai" tanpa salah satu dari dua status pertama. "Kodenya sudah ditulis" bukan bukti.
- Kalau kamu tidak bisa menjalankan atau mengetes sesuatu, tulis **TIDAK TERVERIFIKASI** dan beri Agus langkah cek manual. Jujur soal batas kemampuanmu lebih berharga daripada laporan yang rapi.
- Setiap angka performa harus punya "sebelum" dan "sesudah" dengan cara ukur yang sama.

### 4.2 Keselamatan repo
- Semua kerja di branch `dev`. **Jangan push/merge ke `main` tanpa kata "MERGE" dari Agus.**
- Satu tugas = satu commit kecil dengan pesan jelas (`T2.4: kuota dipotong hanya setelah AI sukses`). Jangan commit file acak atau format ulang file yang tidak kamu ubah.
- Migrasi database hanya **aditif** (tambah tabel/kolom/index). Tanpa DROP, tanpa penghapusan data. Setiap migrasi punya file `down`. Sebelum migrasi pertama, Agus harus mengonfirmasi backup sudah dibuat.
- **Repo ini PUBLIK.** Jangan commit data pengguna, key, isi `.env`, atau file database berisi data pengguna.
- Jangan menjalankan skrip pengubah data di root (`_fix_*`, `_repair_*`, `_fill_*`, `repair_*`, `enrich_*`, `build_canonical_questions.py`, `data_enricher.py`) kecuali tugas memintanya dan data sudah di-tag/backup.
- Dilarang: `git push --force`, menghapus branch/tag, mengganti versi framework/dependency besar, menambah library > 30 KB gzip tanpa alasan tertulis, menambah skrip pihak ketiga di `/app`.

### 4.3 Scope
- Kerjakan hanya tugas bernomor di fase aktif. Ide lain → `docs/BACKLOG.md` (satu baris), jangan dikerjakan. Daftar "JANGAN DIKERJAKAN" ada di akhir Bagian 5.
- Kalau tugas butuh lebih dari 2× estimasi, atau butuh keputusan bisnis/biaya: berhenti, tulis maksimal 3 opsi + rekomendasimu, tanya Agus.
- Jangan mengubah data soal/kunci/pembahasan Pusmendik kecuali tugas memintanya dan ada bukti.
- **Severity temuan:** **A** = bikin pembeli marah/refund, merugikan uang, atau membocorkan/merusak data. **B** = mengganggu tapi ada jalan keluar. **C** = kosmetik. Hanya A yang dikerjakan di Fase 2.

### 4.4 Rahasia dan data pribadi
- Jangan pernah mencetak atau meng-commit API key, token, atau password. Pakai environment variable dan sediakan `.env.example` (nama saja). Jangan minta Agus menempel key di chat; arahkan ke dashboard Railway/Supabase.
- Data yang dikirim ke AI: tanpa nama, email, atau ID akun. Log aplikasi: tanpa data pribadi.
- Semua keputusan akses (pass, admin, kepemilikan data) dicek di **server**. Backend sudah ada (`server.py`): semua logika baru (AI, order, admin, entitlement) lewat server itu, bukan dari browser.

### 4.5 Cara berkomunikasi dengan Agus
- Awali tiap giliran dengan 3 baris: `Fase/tugas sekarang • status • butuh apa dari Agus`.
- Instruksi untuk Agus = langkah bernomor yang bisa diikuti tanpa pengetahuan teknis (klik di mana, ketik apa, hasil yang benar seperti apa).
- Maksimal 3 pertanyaan per laporan, masing-masing dengan jawaban default yang akan kamu pakai kalau Agus tidak menjawab.

### 4.6 Memori antar sesi (sesi AI bisa terputus)
- Awal sesi: baca `docs/STATUS.md`, `docs/ARCHITECTURE.md`, `docs/BACKLOG.md`. Akhir sesi: perbarui `docs/STATUS.md` (fase, tugas selesai, tugas berikutnya, pertanyaan terbuka) dan `docs/CHANGELOG.md` (apa yang berubah + hash commit).
- Laporan fase disimpan di `reports/FASE-N.md` (format di Lampiran I).

### 4.7 Mode malam (jalan tanpa menunggu) — HANYA jika Agus mengaktifkannya
Default tetap: satu fase → laporan → STOP. Agus dapat mengetik `MODE MALAM: Fase X sampai Y`. Dalam mode itu kamu boleh lanjut antar fase tanpa menunggu, **asalkan**:
- Hanya fase yang diizinkan Agus. Rekomendasi: Fase 0, 1, 2, dan 4. **Tidak boleh tanpa Agus hadir:** perubahan/migrasi database (Fase 3, 6), pembayaran, menyalakan flag di produksi, merge ke `main`, rilis (Fase 10).
- Berhenti seketika dan tulis alasannya bila: ada tugas `DIBLOKIR`; butuh keputusan bisnis/biaya; butuh akses/rahasia yang belum ada; tes gagal setelah 2 kali perbaikan; kamu ragu perubahan itu aman.
- Tiap fase tetap menghasilkan `reports/FASE-N.md`; commit kecil dan sering; `docs/STATUS.md` diperbarui setelah setiap tugas (supaya bisa dilanjutkan bila sesimu terputus atau kena limit).
- Di akhir tulis `reports/PAGI.md` (maks 20 baris): yang selesai, yang menunggu cek Agus, yang diblokir, keputusan yang dibutuhkan.
- Jangan membangun fase berikutnya di atas perbaikan yang kamu sendiri belum yakin.

---

## 5. Fase

### Peta waktu (target; berlaku jika Agus punya 4–6 jam/hari untuk verifikasi)

| Fase | Isi | Target selesai |
|---|---|---|
| 0 | Orientasi dan pengaman | 8 Okt |
| 1 | Baseline dan audit jalur kritis | 8–9 Okt |
| 2 | Perbaikan blocker | 9–10 Okt |
| 3 | Rekam perilaku (logging) + konsen | 10 Okt |
| 4 | Analyzer dan penyusun jadwal | 11 Okt |
| 5 | Layar Autopsi (preview) + mode demo | 11 Okt → **Gate A** |
| 6 | Paket Sprint: order, bayar manual, admin, referral | 13 Okt |
| 7 | Lapisan AI (berbayar) | 14 Okt |
| 8 | Landing/FAQ + funnel | 14 Okt |
| 9 | Tes beban, ketahanan, keamanan | 14–15 Okt |
| 10 | Rilis bertahap + runbook | 15 Okt; **freeze 22 Okt** |

Kalau jadwal meleset: **potong scope (Bagian 4.3), jangan potong Fase 9.**

### Gerbang keputusan
- **Gate A (±11 Okt, oleh Agus):** tunjukkan Autopsi ke 5 orang asing. Jika ≥3 bilang "iya bener, gua emang gitu" → lanjut. Jika tidak, isi Autopsi diubah dulu (Agus + Claude). Fase 6–8 boleh jalan selama Gate A berlangsung, tetapi flag `paywall` tetap **OFF** sampai Gate A lolos.
- **Gate P (sebelum `paywall` ON):** tes alur bayar end-to-end lulus (Fase 6), backup terkonfirmasi, dan **order/pass tetap ada setelah redeploy**.
- **Gate B (setelah rilis, oleh Agus + Claude):** dari ±100 orang asing yang selesai tryout, ≥3 membeli → lanjut. Jika 0 → ubah satu variabel (harga/teks/posisi paywall), tes lagi. Muse tidak memutuskan ini.
- **Gate C:** code freeze 22 Okt 23.59 WIB.

---

### FASE 0 — Orientasi dan pengaman (≤ 3 jam; tidak mengubah perilaku aplikasi)

- **T0.1 Lapor kapabilitas.** Jawab ya/tidak: bisa menjalankan aplikasi secara lokal? menjalankan tes/perintah terminal? membuka commit/PR dan push ke `dev`? mengakses database (Supabase) dan Railway (env, deploy)? membuka URL publik? membuat screenshot? Untuk setiap "tidak", tulis cara verifikasi pengganti. Jika kamu **tidak bisa menjalankan kode sama sekali**, katakan; Agus akan memakai eksekutor lain untuk menjalankan, dan kamu menulis perubahan + satu perintah tes yang bisa dijalankan Agus.
- **T0.2 Pengaman.** Buat tag `pre-autopsi-v0` pada commit produksi saat ini. Buat branch `dev` dari `main`. Jika Railway otomatis deploy dari `main`, catat itu di laporan.
- **T0.3 Inventaris → `docs/ARCHITECTURE.md` (maks 2 halaman).** Jawab: stack (frontend, bundler, backend, database, auth); struktur folder; bagaimana soal/pembahasan/Pilar/Soal Serupa disimpan dan dimuat; di mana AI Tutor dipanggil (rute, provider, rotasi key, siapa yang merakit prompt: server atau klien); bagaimana progres disimpan; bagaimana timer jalan; daftar halaman/rute; daftar env var (NAMA saja); skema database saat ini; cara deploy; apakah ada tes/CI. Tambahkan diagram alur dalam teks.
- **T0.4 Pindai rahasia.** Cari API key/token/password di kode **dan riwayat git**. Laporkan jumlah dan lokasi (jangan cetak nilainya). Jika ada yang bocor: minta Agus merotasi key, lalu buat `.env.example`.
- **T0.5 Backup.** Tulis langkah backup database untuk Agus (klik demi klik di dashboard) dan minta konfirmasi "sudah backup" sebelum migrasi pertama.
- **T0.6 Dokumen hidup.** Simpan dua file brief ini di `docs/`. Buat `docs/STATUS.md`, `docs/CHANGELOG.md`, `docs/BACKLOG.md`.
- **T0.7 Feature flag.** Buat mekanisme flag yang bisa diubah **tanpa deploy ulang** (idealnya tabel `feature_flags` di database; jika hanya env var, jelaskan konsekuensinya). Flag awal, semua OFF: `autopsy_logging`, `autopsy_preview`, `autopsy_full`, `paywall`, `ai_narrative`, `referral`, `wa_notify`. Klien membaca flag lewat satu endpoint `/api/flags` (nilai sudah dihitung untuk user itu).
- **T0.8 Baca aturan lama di repo** sebelum mengubah apa pun: `ATURAN_AI.md`, `AI_DESIGN_RULE.md`, `DESIGN.md`, `KONTRAK_DATA.md`, `PRD.md`, `PLAN.md`, `HANDOVER_PROMPT.md`. Ringkas di `ARCHITECTURE.md`. Jika ada yang bertentangan dengan brief ini, **laporkan dan tanya Agus**; jangan pilih sendiri.
- **T0.9 Persistensi dan isi database (kritis untuk pembayaran).** Di mana `ai_tutor.db` dan data pengguna disimpan di produksi? Apakah Railway memakai Volume atau penyimpanan sementara (data hilang tiap deploy/restart)? Apa isi `ai_tutor.db` (tabel/kolom; apakah ada chat, IP, atau data pengguna)? File itu ter-commit di repo **publik**: laporkan dan usulkan pemindahan ke luar git; pembersihan riwayat git hanya atas izin Agus. Aturan keras: **order dan pass tidak boleh disimpan di penyimpanan yang bisa hilang saat redeploy.**
- **T0.10 Peta autentikasi.** Jelaskan cara kerja login Google (apakah Supabase hanya untuk login? bagaimana `server.py` memverifikasi identitas user?).

**Bukti wajib:** `ARCHITECTURE.md`; hasil T0.1; jumlah temuan T0.4; daftar flag. **Laporan:** `reports/FASE-0.md`.

---

### FASE 1 — Baseline dan audit jalur kritis (4–6 jam; hanya membaca/mengukur)

Jalur kritis = jalur yang dilewati pembeli: buka → login → pilih mapel → kerjakan → selesai → hasil → tanya AI → (nanti) beli.

- **T1.1 Baseline performa.** Jika bisa menjalankan: Lighthouse mode Mobile (throttling default) untuk `/`, `/app`, dan satu halaman soal; catat total transfer (MB), jumlah request, 5 file terbesar, LCP, TBT, CLS. Jika tidak bisa: analisis statis ukuran aset/bundle, lalu berikan Agus skrip ukur stopwatch (Lampiran I.2) untuk dua HP lemot.
- **T1.2 Audit jalur kritis (baca kode).**
  - Muat awal: apakah semua 22 mapel dimuat sekaligus? gambar sudah WebP/lazy-load? Halaman `/app` menampilkan nama ikon sebagai teks (school, smart_toy, arrow_forward) → kemungkinan font ikon (Material Symbols): berat dan jadi teks di jaringan lambat.
  - Ruang ujian: timer (menggambar ulang seluruh layar tiap detik?), grid nomor, render rumus (MathJax/KaTeX?), ukuran gambar soal, jumlah elemen DOM.
  - Simpan progres: tulis penyimpanan lokal tiap klik secara sinkron? Bisa lanjut persis setelah tab dimatikan Android?
  - AI Tutor: siapa merakit prompt (server/klien)? dari mana konteks soal dan isi gambar? kuota dipotong kapan? ganti model saat request jalan? timeout, fallback, rotasi key?
  - Keamanan: ada key di bundle klien? endpoint tanpa autentikasi? aturan akses database (RLS)?
  - Database: index, koneksi, kebutuhan tabel baru.
  - Penanganan error dan logging.
- **T1.3 `docs/AUDIT.md`.** Tabel: `ID | severity (A/B/C) | lokasi (file:baris) | gejala | dampak | perbaikan minimal | cara verifikasi`. Maksimal 25 temuan A+B; sisanya C diringkas.
- **T1.4 Petakan daftar masalah Agus (Lampiran B)** ke ID temuan.
- **T1.5 Cek format paket vs Bagian 3.1.** Untuk tiap paket mapel wajib: jumlah soal dan timer yang dikonfigurasi vs tabel. Laporkan yang tidak cocok, termasuk copy landing/FAQ yang bertentangan.

**Jangan:** mengubah perilaku aplikasi. **Laporan:** `reports/FASE-1.md` + `docs/AUDIT.md`.

---

### FASE 2 — Perbaikan blocker (maks 2 hari; HANYA severity A)

Kerjakan berurutan, tiap item satu commit. Untuk performa, **kerjakan hanya yang terbukti berpengaruh di baseline**.

- **T2.1 Performa HP lemot.** Kandidat: ikon → SVG inline (±10 ikon yang dipakai); font sistem atau `font-display: swap`/subset; gambar → WebP + `width/height` + lazy-load + ukuran responsif (tetap bisa di-zoom, terutama Geografi); pecah data soal per paket dan muat pembahasan/Pilar saat dibutuhkan; timer hanya memperbarui elemen timer dan menghitung dari `Date.now()` (bukan penghitung interval); tidak menggambar ulang grid tiap detik; kurangi DOM (lepas soal sebelumnya); rumus pre-render atau KaTeX bila MathJax; hapus library tak terpakai; header cache + kompresi; matikan blur/bayangan berat dan animasi landing di `/app`; hormati `prefers-reduced-motion`. **Target awal (negosiasikan setelah baseline):** LCP < 4 dtk di jaringan lambat + CPU 4×, TBT < 600 ms, CLS < 0.1, pindah soal terasa instan, tidak crash sampai soal ke-40.
- **T2.2 AI Tutor: konteks yang benar.** Server merakit prompt dari `soal_id` (teks soal, opsi, kunci, pembahasan, **teks isi gambar**); klien hanya mengirim `soal_id` + pesan. Pakai transkripsi gambar yang sudah ada di repo (mis. `VISION_TRANSCRIPTION_RESULT.json` bila ada); laporkan soal bergambar yang belum punya transkripsi. **Uji:** 20 soal (10 tanpa gambar, 10 bergambar); AI harus mengutip kata kunci soal yang benar.
- **T2.3 AI Tutor: ketahanan.** Batalkan request lama saat ganti model (`AbortController`) dan abaikan respons basi via `request_id`; tombol kirim nonaktif saat loading; timeout 20 dtk; fallback ke provider berikutnya; cooldown per-key saat 429; streaming jika didukung; pesan error ramah.
- **T2.4 Kuota.** Dipotong hanya setelah sukses (atau dikembalikan otomatis saat gagal), idempotent per `request_id`. Tampilkan sisa kuota. Perbarui FAQ ("kuota tidak terpotong jika gagal terkirim").
- **T2.5 Layar login.** Teks `...supabase.co` dengan karakter acak membuat login tampak seperti phishing. Ajukan opsi ke Agus (branding di consent screen Google, custom domain auth, atau teks penjelas) dengan biaya masing-masing; jangan memilih sendiri jika ada biaya.
- **T2.6 Lapor masalah + support minimal.** Tombol "Lapor masalah" (kirim halaman, `soal_id`, tipe HP/UA, pesan → tabel `bug_reports`) + tautan WhatsApp support. Tanpa chat realtime.
- **T2.7 Format paket dan copy.** Samakan jumlah soal/timer paket wajib dengan Bagian 3.1 (atau tandai "format lama" di UI), ganti demo "45:00 · 40 soal" di landing, dan perbaiki FAQ yang bertentangan.
- **T2.8 Pemantau error.** Pelaporan error klien dan server ke endpoint sendiri atau Sentry (paket gratis): `window.onerror`, `unhandledrejection`, `app_version`, rute, info perangkat; tanpa data pribadi.
- **T2.9 Konten Matematika.** Jika ada waktu sisa, perbaiki hanya yang menyesatkan di mapel Matematika (gambar salah mapel, simbol pangkat/derajat). Mapel lain → backlog.
- **T2.10 Kebijakan key AI.** `.env.example` menganjurkan membuat beberapa akun Groq untuk memutar key. Itu kemungkinan melanggar ketentuan provider dan rapuh saat ada yang membayar. Jangan memperluas pola itu. Laporkan opsi (mis. satu akun berbayar dengan batas biaya, atau provider lain) beserta perkiraan biaya; keputusan ada di Agus.

**Bukti wajib:** angka sebelum/sesudah (T2.1), tes 20 soal (T2.2), skenario gagal-kirim untuk kuota (T2.4), langkah cek untuk Agus di HP lemot. **Laporan:** `reports/FASE-2.md`.

---

### FASE 3 — Rekam perilaku (logging) + konsen (flag `autopsy_logging`)

- **T3.1 Migrasi aditif** (Lampiran A; ditulis untuk Postgres. Jika produksi memakai SQLite, terjemahkan sesuai catatan di Lampiran A dan pastikan penyimpanannya persisten sesuai T0.9): `attempts`, `attempt_items`, `events`, `feature_flags`, `bug_reports`, `plan_progress`. Tulis `db/migrations/NNN_*.sql` + `NNN_*_down.sql`. Jika kamu tidak punya akses database: tulis langkah klik-demi-klik untuk Agus (mis. SQL Editor Supabase) beserta query pengecekan hasilnya.
- **T3.2 Aturan akses (RLS)** sesuai Lampiran A: user hanya membaca/menulis datanya sendiri; `is_correct` dihitung **server** dari kunci.
- **T3.3 Perekam di klien** (modul kecil, tanpa library baru). Per soal: `first_view_ts`, akumulasi `active_ms` (hanya saat tab terlihat dan soal aktif), `first_answer_ms`, `first_answer`, `final_answer`, `change_count`, `flagged_ragu`, `visit_count`, `position`. Simpan di memori + salin ke penyimpanan lokal tiap 5 dtk dan saat `visibilitychange`; kirim **sekali** saat "Selesai Tes" via `POST /api/attempts` dengan `client_attempt_id` (idempotent). Jika gagal: antrean lokal + coba lagi (backoff). **Jangan** mengirim per klik.
- **T3.4 Tamu.** Attempt tamu disimpan lokal; setelah login di-*claim* otomatis (diunggah sekali). Autopsi butuh login.
- **T3.5 Pemulihan.** Refresh atau tab dimatikan → lanjut di nomor dan sisa waktu yang benar (hitung dari timestamp, bukan penghitung).
- **T3.6 Konsen dan privasi.** Teks singkat sebelum tryout pertama ("Waktu dan pola jawabanmu direkam untuk analisis belajar; tidak dijual."). Perbarui halaman Privasi/Syarat (draf: data apa, tujuan, retensi 12 bulan, kontak penghapusan data; kalimat persetujuan orang tua/wali untuk pengguna di bawah umur). Beri catatan: **draf, perlu ditinjau Agus/ahli hukum.**
- **T3.7 Nudge Ragu-ragu.** Tooltip sekali di soal 1: "Tandai Ragu-ragu kalau menebak — analisismu jadi lebih akurat."
- **T3.8 Taksonomi topik.** UI sudah menampilkan topik per soal (mis. "MATEMATIKA SMA · HIMPUNAN"). Cek apakah field itu ada di data; normalisasi ke ≤ 15 topik di `data/taxonomy/matematika.json`. Soal tanpa topik: isi lewat skrip sekali jalan (boleh pakai AI, bukan saat runtime), lalu Agus meninjau sampel 20 soal.

**Bukti wajib:** (1) selesaikan tryout di HP lemot → baris muncul di `attempts`/`attempt_items`; (2) waktu per soal cocok stopwatch ±2 dtk (skrip uji untuk Agus); (3) refresh di tengah tes → lanjut; (4) selesai saat offline → terkirim saat online; (5) tes unit idempotency (kirim dua kali → satu baris). **Laporan:** `reports/FASE-3.md`.

---

### FASE 4 — Analyzer dan penyusun jadwal (tanpa AI)

- **T4.1 Modul `analyzer`**: fungsi murni (input: attempt + items + konfigurasi; output: JSON). Aturan label di Lampiran C; semua ambang di `config/analyzer.json` (versinya dicatat).
- **T4.2 Modul `planner`**: fungsi murni; aturan di Lampiran D.
- **T4.3 Tes unit + 8 "user palsu"** (Lampiran C.4) di `tests/fixtures/personas/`. Label dan rencana harus sesuai harapan tertulis.
- **T4.4 Kartu statis** "Anti-Ceroboh" dan "Strategi Waktu" (Lampiran E) sebagai konten yang bisa dirujuk planner.
- **T4.5 Konfigurasi jadwal ujian** (`config/exam.json`, Bagian 3.1) dan kolom `tka_date` di profil (default 2026-10-26).

**Bukti wajib:** output tes (semua lulus), tabel 8 persona → label + rencana. **Laporan:** `reports/FASE-4.md`.

---

### FASE 5 — Layar Autopsi (preview gratis) + Misi hari ini + mode demo (flag `autopsy_preview`)

- **T5.1 Halaman hasil** setelah "Selesai Tes": skor ringkas; **Autopsi** — kebocoran #1 terbuka lengkap, #2–#3 dan rencana tampil terkunci (blur CSS ringan, bukan gambar); tombol "Pelajari" menuju Pilar/Soal Serupa yang relevan. Tabel jawaban vs kunci yang ada sekarang dipindah ke tab/akordeon "Kunci" (jangan dihapus).
- **T5.2 Tab "Rencana"** + kartu **"Misi hari ini"** di Beranda; tugas bisa dicentang (`plan_progress`). Saat `autopsy_full` OFF atau user belum punya pass, tampilkan versi terkunci.
- **T5.3 "Tanggal TKA kamu?"**: date picker 26 Okt–29 Nov 2026 (default 26 Okt; catatan "tanyakan jadwal ke sekolahmu") + hitung mundur "H-n" di Beranda.
- **T5.4 Mode demo/concierge (khusus admin):** `/admin/autopsi` → daftar attempt terbaru + tombol "Lihat Autopsi penuh" (mengabaikan pass) + "Salin teks untuk WA". Untuk Gate A.
- **T5.5 Ringan.** Tanpa animasi berat, tanpa library baru, gaya bahasa "perilaku, bukan sifat" (Lampiran F).

**Bukti wajib:** screenshot atau langkah cek untuk 3 persona; uji di HP lemot. **Laporan:** `reports/FASE-5.md`. Setelah laporan, **tunggu Gate A dari Agus** sebelum menyalakan paywall.

---

### FASE 6 — Paket Sprint: order, bayar manual, admin, referral (flag `paywall` OFF)

- **T6.1 Migrasi** (Lampiran A; **jangan mulai Fase 6 sebelum T0.9 terbukti aman: data harus bertahan setelah redeploy**): `entitlements`, `admins`, `orders`, `referrals`, `audit_log`. **Pass disimpan di tabel `entitlements` yang hanya bisa ditulis server**, bukan kolom di tabel yang bisa diubah user.
- **T6.2 Alur beli.** `/beli` (login wajib; pilih tanggal hari pertama TKA; tampilkan "tanpa perpanjangan otomatis") → buat order (pakai ulang order pending yang masih aktif) → `/bayar/<public_token>`: gambar QRIS (`QRIS_IMAGE_URL`), nominal total besar + tombol salin, batas bayar 60 menit (hitung mundur ringan), tombol **"Sudah bayar"** → `https://wa.me/<WA_NUMBER>?text=` berisi `Order <id> · Rp <nominal>`. Halaman `/bayar/<token>` bisa dibuka orang tua tanpa login (hanya info order, tanpa data pribadi).
- **T6.3 Nominal unik.** `amount_total = PASS_PRICE + unique_code` (1–99 acak yang belum dipakai order pending; jika habis, perlebar 1–999). Teks UI: "Bayar PERSIS sesuai nominal."
- **T6.4 Admin** `/admin/orders` (login + cek peran di server, rate limit): tabel pending (cari nominal/ID), **Tandai lunas** (set `paid`, `paid_at`, `entitlements.pass_expires_at = (tka_date + 4 hari) 23.59 WIB`, catat di `audit_log`), **Batalkan**, **Refund** (cabut pass + catatan), ubah masa aktif. Tombol "Salin pesan konfirmasi WA". Opsional di balik flag `wa_notify`: kirim "Pass aktif!" lewat gateway WhatsApp milik Agus (tanya Agus endpoint/format; jangan hardcode; kegagalan kirim tidak boleh membatalkan aktivasi).
- **T6.5 Entitlement di server.** `hasPass(user) = pass_expires_at > now()` (waktu server). `/api/autopsy/:attemptId` selalu mengembalikan bagian gratis; bagian penuh hanya jika pass. Klien tidak pernah jadi sumber kebenaran. Halaman Akun: "Paket Sprint aktif sampai <tanggal> (sisa n hari)".
- **T6.6 Referral.** Tangkap `?ref=KODE` (penyimpanan lokal 30 hari) → simpan di order. `/admin/referral`: per kode jumlah order lunas, total komisi (`commission_pct` × harga dasar), ekspor CSV; kode dibuat manual oleh admin.
- **T6.7 "Kirim ke ortu".** Tombol di halaman hasil → teks WhatsApp siap kirim (skor, 2 temuan, tautan `/bayar/<token>` bila order sudah dibuat, atau `/beli`).
- **T6.8 Kedaluwarsa.** Order pending > 60 menit → `expired` (cek saat dibaca); admin tetap bisa menandainya lunas.
- **T6.9 Saat `paywall` OFF**, semua fitur terbuka seperti beta dan tidak ada yang rusak.

**Bukti wajib (Gate P):** skenario end-to-end: tamu → login → tryout → lihat preview → beli → bayar (Agus membayar nominal asli ke dirinya/orang tuanya sekali) → admin lunas → penuh terbuka → ubah tanggal agar kedaluwarsa → terkunci lagi. Uji 2 akun: user A **tidak bisa** membaca attempt/order user B dan **tidak bisa** menulis `entitlements`. Uji batas waktu: aktif pada 23.58 WIB hari terakhir, nonaktif pukul 00.00. **Laporan:** `reports/FASE-6.md`.

---

### FASE 7 — Lapisan AI untuk narasi Autopsi (berbayar; flag `ai_narrative`)

- **T7.1 Modul `autopsyNarrative`**: input = ringkasan JSON (Lampiran G, tanpa nama/email); output JSON sesuai skema; validasi skema; retry sekali; jika gagal → **template cadangan** deterministik dari hasil analyzer.
- **T7.2 Prompt sistem** (Lampiran F), disimpan dengan `prompt_version`.
- **T7.3 Aturan panggilan.** Hanya jika `hasPass` dan flag ON; **satu kali per attempt**; hasil di-cache di `autopsies.narrative`; "Regenerasi" maksimal 1× per attempt.
- **T7.4 Kontrol biaya.** Env `AUTOPSY_MODEL` (model murah yang bisa keluarkan JSON), `AI_DAILY_BUDGET_IDR`; hitung biaya per panggilan dari token; lewat batas → fallback template + log; counter harian terlihat di admin.
- **T7.5 Evaluasi.** 20 kasus uji (8 persona × variasi) → `docs/eval/autopsi_v1.md`. Periksa: tidak ada tugas di luar daftar, tidak menghakimi sifat, tidak mengarang angka, bahasa Indonesia, panjang sesuai batas. Agus membaca 10.

**Bukti wajib:** file evaluasi; tes unit validasi skema; simulasi AI mati → fallback jalan. **Laporan:** `reports/FASE-7.md`.

---

### FASE 8 — Landing, harga, FAQ, funnel

- **T8.1 Harga.** Ganti kartu "Pro (beta) Rp20.000/bulan" menjadi **Paket Sprint TKA** (teks di Lampiran H). Tampilkan Gratis vs Paket Sprint berdampingan. Hapus "Mendukung pengembangan berlanjut"; "100 tanya/hari" hanya boleh jadi bonus kecil.
- **T8.2 Hero + satu section "Autopsi Tryout"** berisi contoh hasil (dari persona demo; teks + CSS ringan; **tanpa animasi baru**). Jangan mengubah desain lain.
- **T8.3 FAQ baru** (Lampiran H), dan perbaiki FAQ lama yang bertentangan.
- **T8.4 Event funnel** (7 event): `landing_view`, `start_tryout`, `finish_tryout`, `view_autopsi` (props: `preview|full`), `click_buy`, `order_created`, `order_paid` (server-side). `POST /api/event` ringan, dibatch, anonim (`anon_id` acak), **tanpa SDK pihak ketiga** di `/app`.
- **T8.5 `/admin/funnel`**: 7 hari terakhir, jumlah tiap event per hari + rasio antar tahap + pecahan per kode `ref`.
- **T8.6 (opsional, hanya setelah Gate B)** Kartu Hasil untuk Story: gambar dibuat **hanya saat tombol diketuk**, ringan.

**Bukti wajib:** screenshot sebelum/sesudah; query contoh event masuk. **Laporan:** `reports/FASE-8.md`.

---

### FASE 9 — Tes beban, ketahanan, keamanan

- **T9.1 Skrip k6** di `tests/load/` + `README` langkah menjalankan untuk Agus (atau layanan web seperti loader.io; cek batas gratisnya). `MOCK_AI=1` agar tidak memakai kuota AI. Skenario: landing + aset (300 pengguna virtual), tryout tamu, login-user kirim attempt + ambil autopsi (100), burst `POST /api/orders` (30), AI mock (50). **Ambang:** 95% request non-AI < 1 dtk, error < 1%.
- **T9.2 Perbaiki bottleneck** satu per satu dan ukur ulang: index database, cache soal via CDN/header, pooling koneksi, batas ukuran payload.
- **T9.3 Tes gagal:** provider AI mati; timeout; kirim attempt saat offline; order dobel; jam server vs klien berbeda; database lambat. Sistem tidak boleh rusak diam-diam.
- **T9.4 Keamanan:** tiap endpoint dicek autentikasi + otorisasi; user A vs B (dua akun nyata); endpoint admin menolak non-admin; rate limit pada AI, order, event, lapor masalah; tidak ada key di bundle klien; header keamanan dasar; validasi input; log tanpa data pribadi.
- **T9.5 Simulasi biaya:** 1.000 attempt → perkiraan biaya AI per pengguna berbayar.

**Bukti wajib:** output k6 sebelum/sesudah; daftar temuan keamanan + status. **Laporan:** `reports/FASE-9.md`.

---

### FASE 10 — Rilis bertahap, runbook, code freeze

- **T10.1 Staging.** Deploy `dev` ke lingkungan terpisah (environment/preview Railway) atau, jika tidak ada, uji di produksi hanya di balik flag.
- **T10.2 `docs/RUNBOOK.md`:** cara mematikan AI dan paywall (kill switch), rollback (tag/deploy sebelumnya + migrasi `down`), restore backup, cek kesehatan (`/healthz`), batas biaya, kontak.
- **T10.3 Rilis.** Merge ke `main` **hanya atas kata "MERGE" dari Agus.** Urutan menyalakan flag: `autopsy_logging` → `autopsy_preview` (10% → 100%) → `paywall` setelah Gate A + Gate P → `ai_narrative` → `referral`.
- **T10.4 Laporan harian singkat** `reports/DAILY-<tanggal>.md` berisi 5 angka: error, p95 latency, kegagalan AI, biaya AI hari ini, jumlah order.
- **T10.5 Code freeze 22 Okt 23.59 WIB.** Setelah itu hanya hotfix severity A dan perubahan teks, masing-masing dengan laporan.

**Bukti wajib:** runbook diuji (matikan flag → perilaku berubah), latihan rollback di staging. **Laporan:** `reports/FASE-10.md`.

---

### JANGAN DIKERJAKAN (sebelum 26 Okt selesai dan Agus mengizinkan)

Pembersihan/restrukturisasi repo (folder arsip, backup, scratch, skrip lama) · Mapel pilihan SMK dan mapel/paket baru · bank soal UTBK · leaderboard · redesign UI · payment gateway otomatis (webhook) · bot WhatsApp · push notification · service worker/offline penuh · badge "Terverifikasi" · live chat · dark mode · multi-bahasa · analitik pihak ketiga · refactor besar · upgrade framework.

---

### Penutup setiap sesi (checklist)
1. `docs/STATUS.md` dan `docs/CHANGELOG.md` sudah diperbarui.
2. Semua perubahan ada di `dev`, tidak ada yang di `main`.
3. Tidak ada rahasia yang ter-commit.
4. Laporan fase memakai format Lampiran I dan tidak memuat status "Selesai" tanpa bukti.
5. Berhenti dan tunggu "lanjut".
