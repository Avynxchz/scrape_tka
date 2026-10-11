# LAMPIRAN BRIEF MUSE — Proyek TKA Master

Pendamping `01_BRIEF_MUSE.md`. Baca hanya bagian yang dirujuk tugas aktif.

Daftar isi: A Skema database · B Daftar masalah dari Agus · C Aturan label (analyzer) + persona uji · D Aturan penyusun jadwal · E Kartu statis · F Prompt sistem AI + nada · G Skema JSON AI · H Copy landing/harga/FAQ · I Format laporan + tes manual untuk Agus

---

## A. Skema database

Dirancang untuk Postgres/Supabase. Jika stack berbeda, terjemahkan dengan prinsip yang sama: **klien hanya boleh membaca data miliknya; semua penulisan penting (attempt, order, pass, flag) lewat server.** Service role key hanya ada di server.

> **Stack nyata repo ini (lihat brief 3.3):** backend Python + kemungkinan SQLite (`ai_tutor.db`). Terjemahan ke SQLite: `uuid` → TEXT (buat dengan `uuid4()` di Python); `jsonb` → TEXT berisi JSON; `timestamptz` → TEXT ISO-8601 UTC; `bigserial` → `INTEGER PRIMARY KEY AUTOINCREMENT`; `gen_random_uuid()` dan `now()` → nilai dari aplikasi. Tidak ada RLS, jadi **otorisasi dilakukan di `server.py`** (setiap query difilter `user_id` hasil verifikasi token). Partial unique index didukung SQLite. Aktifkan `PRAGMA journal_mode=WAL` dan `PRAGMA foreign_keys=ON`. File database harus berada di penyimpanan persisten (Railway Volume) atau pindah ke Railway Postgres; keputusan setelah T0.9.

### A.1 `001_perilaku.sql` (aditif)

```sql
create table if not exists attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  client_attempt_id text not null,
  mapel text not null,
  paket text not null,
  mode text not null default 'simulasi',      -- simulasi | latihan
  started_at timestamptz not null,
  finished_at timestamptz,
  duration_limit_s int,                        -- batas waktu paket (detik)
  n_questions int,
  n_answered int,
  n_correct int,
  ended_by text,                               -- user | timer
  app_version text,
  device jsonb,
  created_at timestamptz not null default now(),
  unique (user_id, client_attempt_id)
);
create index if not exists attempts_user_idx on attempts (user_id, created_at desc);

create table if not exists attempt_items (
  id bigserial primary key,
  attempt_id uuid not null references attempts(id) on delete cascade,
  soal_id text not null,
  position int not null,
  topic_id text,
  first_answer text,
  final_answer text,
  is_correct boolean,                          -- dihitung SERVER dari kunci
  active_ms int not null default 0,
  first_answer_ms int,
  change_count int not null default 0,
  flagged_ragu boolean not null default false,
  visit_count int not null default 1,
  unique (attempt_id, soal_id)
);

create table if not exists autopsies (
  id uuid primary key default gen_random_uuid(),
  attempt_id uuid not null unique references attempts(id) on delete cascade,
  user_id uuid not null,
  analysis jsonb not null,                     -- hasil analyzer (aturan)
  plan jsonb,                                  -- hasil planner (aturan)
  narrative jsonb,                             -- hasil AI (hanya pemegang pass)
  config_version text,
  prompt_version text,
  created_at timestamptz not null default now()
);

create table if not exists plan_progress (
  user_id uuid not null,
  autopsy_id uuid not null references autopsies(id) on delete cascade,
  task_id text not null,
  done_at timestamptz not null default now(),
  primary key (user_id, autopsy_id, task_id)
);

create table if not exists events (
  id bigserial primary key,
  ts timestamptz not null default now(),
  anon_id text,
  user_id uuid,
  name text not null,
  props jsonb
);
create index if not exists events_name_ts on events (name, ts);

create table if not exists bug_reports (
  id bigserial primary key,
  ts timestamptz not null default now(),
  user_id uuid,
  page text,
  soal_id text,
  ua text,
  message text
);

create table if not exists feature_flags (
  name text primary key,
  enabled boolean not null default false,
  rollout_pct int not null default 100,
  updated_at timestamptz not null default now()
);
```

### A.2 `002_paket.sql` (aditif)

```sql
-- tka_date boleh diubah user; letakkan di tabel profil yang sudah ada (mis. profiles)
alter table profiles add column if not exists tka_date date default '2026-10-26';

-- Pass disimpan di tabel terpisah yang HANYA bisa ditulis server
create table if not exists entitlements (
  user_id uuid primary key,
  pass_expires_at timestamptz,
  source_order text,
  updated_at timestamptz not null default now()
);

create table if not exists admins (user_id uuid primary key);

create table if not exists orders (
  id text primary key,                         -- mis. TKA-0001
  public_token text not null unique,           -- acak, >= 24 karakter
  user_id uuid not null,
  amount_base int not null,
  unique_code int not null,
  amount_total int not null,
  tka_date date not null,
  status text not null default 'pending',      -- pending|paid|expired|cancelled|refunded
  ref_code text,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  paid_at timestamptz,
  paid_by uuid,
  note text
);
create unique index if not exists orders_pending_amount
  on orders (amount_total) where status = 'pending';

create table if not exists referrals (
  code text primary key,
  owner_name text,
  owner_contact text,
  commission_pct int not null default 25,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists audit_log (
  id bigserial primary key,
  ts timestamptz not null default now(),
  actor uuid,
  action text not null,
  target text,
  detail jsonb
);
```

### A.3 Aturan akses (RLS)

```sql
alter table attempts enable row level security;
create policy attempts_select_own on attempts for select using (user_id = auth.uid());

alter table attempt_items enable row level security;
create policy items_select_own on attempt_items for select
  using (exists (select 1 from attempts a where a.id = attempt_id and a.user_id = auth.uid()));

alter table plan_progress enable row level security;
create policy progress_select_own on plan_progress for select using (user_id = auth.uid());

alter table entitlements enable row level security;
create policy ent_select_own on entitlements for select using (user_id = auth.uid());

alter table orders enable row level security;
create policy orders_select_own on orders for select using (user_id = auth.uid());

-- Tanpa policy klien (deny-all; akses hanya lewat server/service role):
alter table autopsies enable row level security;       -- baca lewat API yang menyaring bagian berbayar
alter table admins enable row level security;
alter table referrals enable row level security;
alter table audit_log enable row level security;
alter table events enable row level security;
alter table bug_reports enable row level security;
alter table feature_flags enable row level security;   -- baca lewat /api/flags
```

Catatan wajib:
- `is_correct` dihitung **server** dari kunci; klien tidak boleh menulis ke `attempts`/`attempt_items`/`plan_progress`/`entitlements`/`orders` secara langsung.
- Setiap migrasi punya `NNN_*_down.sql` yang membatalkannya.
- Pass kedaluwarsa dibaca dari waktu server (`now()`), bukan jam klien.

---

## B. Daftar masalah dari Agus (petakan ke ID temuan di Fase 1)

1. **Lag di HP lemot.** Dua HP teman Agus lag; HP Agus dan satu iPhone lancar. Targetnya mulus di HP murah. → Fase 2 (A).
2. **AI Tutor lambat**, dan ada bug saat mengganti model ketika model sebelumnya masih loading. → Fase 2 (A).
3. Di menu modul, saat scroll, tab (Wajib/Saintek/Soshum/Bahasa) dan navbar atas seharusnya tersembunyi, tetapi tetap tampil. → backlog.
4. Teman bingung dengan layout pembahasan/Pilar dan tombol navigasi; tidak ada notifikasi; banyak yang tidak tahu AI Tutor sudah paham konteks soal. → backlog (kecuali T3.7).
5. Tombol navigasi kanan kadang tidak langsung pindah (mis. dari chat AI ke soal). → cek ulang setelah perbaikan performa.
6. AI Tutor kadang salah konteks; untuk sebagian soal tidak melihat gambar dan menjawab soal lain. → Fase 2 (A).
7. Lapor Bug dan chat customer service belum benar-benar aktif. → Fase 2 (versi minimal).
8. Layar login menampilkan teks Supabase dengan karakter acak sebelum `.supabase`. → Fase 2 (A, ajukan opsi).
9. Ingin chat AI Tutor menampilkan soal sekaligus (hemat layar di mobile). → backlog.

Keputusan lama Agus yang tetap berlaku: semua gambar Geografi (dan gambar padat teks) harus bisa di-zoom; gambar mengikuti alur teks seperti di Pusmendik; gambar berisi teks Arab rata kanan; tampilan tetap rapi di mobile; AI Tutor harus tahu teks di dalam gambar.

Bug konten dari audit manual Agus (kerjakan Matematika dulu): gambar salah (dari mapel lain), superscript/subscript/derajat tampil datar, gambar terlalu besar/kecil, teks terpotong.

---

## C. Aturan label (analyzer)

### C.1 Besaran dasar
- `jatah_ms = duration_limit_s × 1000 / n_questions` (jika paket tidak punya timer, pakai `config/exam.json`).
- Kunci dan `is_correct` dari server. "Jawaban pertama benar" = `first_answer` sama dengan kunci.

### C.2 Label per soal (urutan prioritas; satu `primary_label` + flags)

| # | Label | Syarat |
|---|---|---|
| 1 | `waktu_habis` | tidak dijawab, `ended_by = timer`, dan `position ≥ 0,8 × n_questions` |
| 2 | `kosong` | tidak dijawab (selain di atas) |
| 3 | `overthinking` | `first_answer` benar, `final_answer` salah |
| 4 | `terburu` | salah dan `active_ms < max(15.000, 0,2 × jatah_ms)` |
| 5 | `macet` | salah dan `active_ms > 2 × jatah_ms` |
| 6 | `yakin_salah` | salah dan tidak Ragu-ragu |
| 7 | `ragu_salah` | salah dan Ragu-ragu |
| 8 | `ragu_benar` | benar dan Ragu-ragu (**rapuh**, bukan kebocoran) |
| 9 | `aman` | benar dan tidak Ragu-ragu |

Flags tambahan (bukan label utama): `ganti_banyak` (`change_count ≥ 2`), `lambat_benar` (benar dan `active_ms > 1,5 × jatah_ms`).

### C.3 Tingkat attempt
- `data_tipis`: `n_answered < 15` atau total `active_ms` < 40% dari batas waktu.
- `fatigue`: akurasi sepertiga terakhir turun ≥ 25 poin persentase dibanding sepertiga pertama (hanya jika `n_answered ≥ 15`).
- **Kebocoran:** `soal_hilang` = jumlah soal salah/kosong dengan `primary_label` itu. `bobot_pulih`: `terburu 1,0 · overthinking 0,9 · waktu_habis 0,7 · kosong 0,7 · ragu_salah 0,6 · yakin_salah 0,5 · macet 0,5`. `prioritas = soal_hilang × bobot_pulih`. Urut menurun, ambil maksimal 3. Kebocoran #1 = preview gratis. Label dengan `soal_hilang = 0` tidak ditampilkan.
- `rapuh_ids` = soal `ragu_benar`; tampilkan sebagai catatan jika ≥ 3.
- **Per topik:** `n, benar, akurasi, rata_waktu_s, label_dominan`. `topik_prioritas` = topik dengan (`n ≥ 3` dan `akurasi < 50%`) atau `n_salah ≥ 2`, urut `n_salah` menurun.
- **Bukti** dibangkitkan dari angka, mis. "5 soal dijawab kurang dari 36 detik dan salah". Jangan menulis bukti yang tidak punya angka.
- Semua ambang ada di `config/analyzer.json` (nomor versinya disimpan di `autopsies.config_version`).

### C.4 Delapan persona uji (buat fixture JSON; harapan harus lulus tes)

| Persona | Pola data | Harapan |
|---|---|---|
| P1 Terburu | 25 soal; 8 soal dijawab < 30 dtk dan salah; 3 salah lain; sisanya benar | kebocoran #1 = `terburu` |
| P2 Plin-plan | 6 soal: jawaban pertama benar → akhir salah | #1 = `overthinking` |
| P3 Yakin tapi salah | 7 salah tanpa Ragu-ragu, waktu normal, topik Peluang dan Barisan | #1 = `yakin_salah`; `topik_prioritas` memuat dua topik itu |
| P4 Ragu tapi benar | 8 benar dengan Ragu-ragu; 2 salah | tidak ada kebocoran besar; `rapuh_ids` ≥ 3 |
| P5 Kehabisan waktu | soal 21–25 kosong, `ended_by = timer` | #1 = `waktu_habis` |
| P6 Macet | 4 soal > 7 menit dan salah | #1 = `macet` |
| P7 Capek di akhir | akurasi 90% di sepertiga awal, 40% di akhir | `fatigue = true` |
| P8 Data tipis | hanya 9 soal dijawab | `data_tipis = true`, tanpa kesimpulan kuat |

---

## D. Aturan penyusun jadwal (planner)

**Input:** `today` (WIB), `tka_date` (hari pertama TKA user), `mapel`, `daily_minutes` (default 25; pilihan 15/25/40), kebocoran top-3, `topik_prioritas`, `rapuh_ids`, pustaka konten (Pilar per soal, Soal Serupa per soal/topik, kartu, paket simulasi).

**D.1 Tanggal.** `exam_day = tka_date + EXAM_DAY_OFFSET[mapel]`; `last_study_day = exam_day − 1`; rentang = `today … last_study_day`. Jika rentang kosong → rencana "hanya hari ini" (ulang soal yang salah + kartu).

**D.2 Hari khusus.**
- **H-1 (`last_study_day`):** `tinjau_ragu` (soal `ragu_salah`/`ragu_benar`, maks 8) + satu kartu (sesuai label teratas). **Tanpa materi baru.** Total ≤ 15 menit.
- **H-3 sampai H-2** (jika rentang ≥ 5 hari): `simulasi_ulang` sebagai **sesi panjang** (`long: true`, opsional; paket yang belum dikerjakan, atau yang paling lama) + tinjau kebocoran 10 menit di hari lain.

**D.3 Hari biasa.** Bagi `daily_minutes` ke 3 kebocoran teratas proporsional `prioritas` (tiap kebocoran minimal 1 sesi per 3 hari). Satu sesi = (a) `pilar` sesuai pemetaan D.4, (b) `soal_serupa` 3–5 soal dari soal yang salah pada topik terkait, (c) `kartu` bila label ∈ {terburu, overthinking, waktu_habis, kosong, macet}; kartu yang sama maksimal 1× per 3 hari. Estimasi menit: pilar 6, soal serupa 3 per soal, kartu 2, tinjau ragu 8.

**D.4 Pemetaan kebocoran → konten**

| Kebocoran | Pilar | Tambahan |
|---|---|---|
| `terburu`, `overthinking` | Pilar 5 (Trik & Jebakan) → Pilar 4 (langkah, untuk cek ulang) | kartu `anti_ceroboh` |
| `yakin_salah`, `ragu_salah` | Pilar 1 (fondasi) → Pilar 3 (intuisi) | Soal Serupa |
| `ragu_benar` (rapuh) | Pilar 3 | Soal Serupa untuk mengunci |
| `macet`, `waktu_habis`, `kosong` | — | kartu `strategi_waktu` + Soal Serupa bertimer (pakai jatah) |

**D.5 Properti yang harus lulus tes:** deterministik (input sama → output sama); `task_id` stabil (`hash(date|type|ref)`); re-plan hanya saat attempt baru selesai dan mempertahankan tugas yang sudah dicentang bila `task_id` sama; menit per hari ≤ `daily_minutes` (kecuali sesi panjang); tidak ada tugas setelah H-1; H-1 tanpa materi baru; setiap `ref` ada di konten.

**D.6 Bentuk output:**
```json
{
  "tka_date": "2026-10-26",
  "exam_day": "2026-10-28",
  "days": [
    {
      "date": "2026-10-09",
      "hari_ke": 1,
      "label_h": "H-19",
      "minutes": 24,
      "tasks": [
        {"id": "d1-pilar-3fa9", "type": "pilar", "ref": "MTK-P1-04#5", "title": "Pilar 5: Trik & Jebakan", "minutes": 6, "reason": "terburu"},
        {"id": "d1-serupa-91c2", "type": "soal_serupa", "ref": ["MTK-P1-04-S1", "MTK-P1-04-S2", "MTK-P1-04-S3"], "title": "3 soal serupa", "minutes": 9, "reason": "terburu"},
        {"id": "d1-kartu-77aa", "type": "kartu", "ref": "anti_ceroboh", "title": "Kartu Anti-Ceroboh", "minutes": 2, "reason": "terburu"}
      ]
    }
  ]
}
```

---

## E. Kartu statis (konten tetap untuk semua pengguna)

**Kartu `anti_ceroboh`**
1. Sebelum klik, tunjuk apa yang ditanya: nilai x, nilai fungsi, atau selisih?
2. Cek tanda (+/−) dan satuan di langkah terakhir.
3. Jangan ganti jawaban karena "perasaan". Ganti hanya kalau kamu menemukan bukti konkret (salah hitung, salah baca).
4. Jawaban pertama yang sudah kamu cek sekali biasanya layak dipertahankan.
5. Sisakan waktu di akhir untuk meninjau soal yang kamu tandai Ragu-ragu, bukan semua soal.

**Kartu `strategi_waktu`** (angka dihitung dari `jatah_ms` mapel; contoh Matematika)
1. Jatah rata-rata ±3 menit per soal (25 soal dalam 75 menit).
2. Kalau setelah 2 menit belum ada arah, tandai Ragu-ragu dan lanjut.
3. Kerjakan dulu yang kamu yakin; kembali ke soal yang ditandai di sisa waktu.
4. Checkpoint: soal 5 sebelum menit 15, soal 10 sebelum menit 30, soal 15 sebelum menit 45, soal 20 sebelum menit 60.
5. Jangan biarkan kosong di menit terakhir; pilih jawaban terbaikmu (cek aturan penilaian resmi tentang jawaban salah).

---

## F. Prompt sistem AI Autopsi + nada

Simpan sebagai `prompts/autopsy_v1.txt` dan catat `prompt_version = "autopsy_v1"`.

```
Kamu adalah penulis "Autopsi Tryout" untuk aplikasi latihan TKA. Tugasmu: mengubah DATA ANALISIS (JSON) menjadi penjelasan singkat dan rencana yang jelas untuk seorang pelajar SMA.

ATURAN KERAS
1. Gunakan HANYA angka dan fakta dari JSON input. Jangan mengarang angka, soal, topik, atau tugas.
2. Untuk rencana harian, rujuk hanya `task_id` yang ada di input. Dilarang menambah, mengganti, atau menghapus tugas.
3. Bicara tentang PERILAKU yang terlihat di data, bukan sifat orang. Dilarang: "kamu ceroboh", "kamu malas", "kamu terlalu percaya diri". Pakai bentuk seperti: "pada soal X kamu menjawab dalam N detik dan salah; biasanya itu tanda terburu-buru".
4. Jangan menebak isi pikiran. Untuk dugaan, pakai kata "biasanya", "kemungkinan", atau "bisa jadi".
5. Jika data_tipis = true, awali dengan kalimat bahwa datanya masih sedikit dan kesimpulannya masih awal.
6. Sertakan SATU hal yang sudah bagus (dari data), dan akhiri setiap kebocoran dengan satu langkah kecil yang bisa dilakukan hari ini.
7. Nada: hangat, lugas, bahasa Indonesia santai-sopan dengan kata "kamu"; tanpa emoji; tanpa menghakimi; tanpa menakut-nakuti; tanpa janji hasil (jangan menjanjikan skor atau kelulusan).
8. Jangan memberi saran medis atau psikologis. Jangan menyebut nama model, AI, atau perusahaan.
9. Keluarkan HANYA JSON valid sesuai skema output. Tanpa teks lain, tanpa markdown.
```

**Contoh nada**
- Baik: "Pada 5 soal kamu menjawab kurang dari 36 detik dan salah. Biasanya itu tanda terburu-buru. Hari ini coba baca ulang kalimat tanya sebelum klik."
- Buruk: "Kamu terlalu ceroboh dan sombong, makanya salah terus."
- Baik: "Datanya masih sedikit (9 soal dijawab), jadi anggap ini gambaran awal."
- Buruk: "Dengan rencana ini kamu pasti lolos."

---

## G. Skema JSON AI

**Input** (`autopsy_input_v1`; tanpa nama/email/ID akun):
```json
{
  "version": "autopsy_input_v1",
  "mapel": "matematika",
  "skor_pct": 56,
  "n_soal": 25,
  "n_dijawab": 24,
  "durasi_aktif_menit": 61,
  "hari_menuju_ujian": 17,
  "hari_ujian_mapel": "2026-10-28",
  "data_tipis": false,
  "kebocoran": [
    {"label": "terburu", "soal_hilang": 5, "bukti": "5 soal dijawab kurang dari 36 detik dan salah", "contoh": ["MTK-P1-04", "MTK-P1-09"]}
  ],
  "topik_prioritas": [{"topik": "Peluang", "akurasi_pct": 33, "n": 6}],
  "hal_bagus": "Akurasi 82% pada soal Aljabar",
  "tasks": [
    {"task_id": "d1-pilar-3fa9", "hari_ke": 1, "judul": "Pilar 5: Trik & Jebakan", "menit": 6, "alasan": "terburu"}
  ]
}
```

**Output** (`autopsy_output_v1`):
```json
{
  "version": "autopsy_output_v1",
  "ringkasan": "maks 350 karakter",
  "kebocoran": [
    {"label": "terburu", "judul": "maks 60 karakter", "penjelasan": "maks 280 karakter", "langkah_hari_ini": "maks 140 karakter"}
  ],
  "hal_bagus": "maks 140 karakter",
  "hari": [
    {"hari_ke": 1, "pembuka": "maks 120 karakter", "task_ids": ["d1-pilar-3fa9"]}
  ],
  "catatan_data": "opsional, maks 160 karakter"
}
```

**Validasi wajib:** maksimal 3 item `kebocoran`; semua `task_ids` ⊆ `task_id` di input; tidak ada key tak dikenal; panjang di bawah batas; teks tidak memuat angka yang tidak ada di input. Jika gagal: retry sekali, lalu template cadangan.

---

## H. Copy landing, harga, FAQ (bahasa Indonesia)

**H.1 Hero**
- Judul: **Tahu persis kenapa kamu salah — dan apa yang dikerjakan hari ini.**
- Sub: Kerjakan simulasi TKA. Autopsi membedah pola jawabanmu (waktu, ganti jawaban, keraguan), lalu menyusun rencana belajar harian sampai hari ujian.
- Tombol utama: "Mulai latihan gratis" · tombol kedua: "Lihat contoh Autopsi"

**H.2 Section "Autopsi Tryout"** (beri label kecil: "Contoh ilustrasi, bukan data pengguna")
> Dari 25 soal, kamu salah 11.
> • 5 soal dijawab kurang dari 36 detik dan salah — biasanya tanda terburu-buru.
> • 4 soal Peluang & Barisan: kamu yakin, tapi jawabannya keliru — kemungkinan ada konsep yang perlu diperbaiki.
> • 2 soal terakhir tidak sempat dikerjakan.
> Mulai dari yang pertama: hari ini 20 menit — Pilar 5 + 3 soal serupa.

**H.3 Harga**
- **Gratis:** semua soal dan kunci · Pembahasan Pilar 1–5 · simulasi ber-timer · Autopsi tahap awal (temuan #1) · AI Tutor 25 tanya/hari setelah login.
- **Paket Sprint TKA — Rp14.900** · sekali bayar · aktif sampai hari TKA kamu · tanpa langganan: Autopsi lengkap setiap simulasi · rencana belajar harian sampai hari-H · soal serupa sesuai kelemahanmu · ringkasan untuk orang tua · AI Tutor 100 tanya/hari (bonus).
- Tombol: "Beli Paket Sprint". Teks kecil: "Bayar via QRIS. Aktif maksimal 1 jam (07.00–22.00 WIB)."

**H.4 FAQ**
- **Apa itu Paket Sprint TKA?** Tiket sekali bayar yang membuka Autopsi lengkap dan rencana belajar harian sampai hari TKA-mu. Tidak ada perpanjangan otomatis.
- **Apa yang tetap gratis?** Semua soal, kunci, pembahasan, simulasi ber-timer, dan Autopsi tahap awal.
- **Bagaimana cara bayar?** Bayar lewat QRIS dengan nominal yang tertera, lalu konfirmasi lewat WhatsApp. Biasanya aktif dalam 1 jam (07.00–22.00 WIB).
- **Sampai kapan aktif?** Sampai beberapa hari setelah tanggal TKA yang kamu pilih saat membeli.
- **Boleh dibayarkan orang tua?** Boleh. Bagikan tautan pembayaran dari halaman hasil.
- **Bagaimana kalau jadwal TKA-ku berubah?** Hubungi WhatsApp support; masa aktif bisa disesuaikan.
- **Refund?** Kalau dalam 24 jam setelah aktif kamu merasa tidak terbantu, hubungi WhatsApp support dan uang dikembalikan. `TODO-AGUS: konfirmasi`
- **Data saya dipakai untuk apa?** Waktu dan pola jawabanmu dipakai untuk analisis belajarmu. Tidak dijual ke pihak lain.
- Perbaiki FAQ lama: kuota AI tidak terpotong jika jawaban gagal terkirim; login Google sudah tersedia.

**H.5 Larangan copy:** tidak ada hitung mundur palsu, tidak ada ancaman ("kamu pasti gagal kalau tidak beli"), tidak ada janji skor/kelulusan ("pasti naik X poin"), tidak ada klaim "resmi", tidak ada testimoni tanpa izin tertulis. Pertahankan disclaimer "bukan situs resmi" dan "pembahasan dibantu AI, bandingkan dengan kunci resmi".

---

## I. Format laporan dan tes manual untuk Agus

### I.1 Format `reports/FASE-N.md`

```
# LAPORAN FASE N — <judul>
Tanggal/jam: ...   Commit terakhir: <hash>   Branch: dev

## 1. Ringkasan (maks 5 baris)

## 2. Tabel tugas
| ID | Tugas | Status | File diubah | Bukti |
|----|-------|--------|-------------|-------|
Status hanya: SELESAI-TERVERIFIKASI | SELESAI-MENUNGGU-CEK-AGUS | SEBAGIAN | BELUM | DIBLOKIR

## 3. Angka sebelum → sesudah (jika ada; cara ukur yang sama)

## 4. Yang TIDAK terverifikasi dan kenapa

## 5. Langkah cek untuk Agus (bernomor, klik demi klik, hasil yang benar)

## 6. Risiko / keputusan yang dibutuhkan (maks 3, masing-masing dengan default)

## 7. Fase berikutnya (3 baris)
```

### I.2 Skrip ukur stopwatch untuk Agus (dua HP lemot)

1. Pakai HP teman yang lag. Tutup semua aplikasi lain. Buka Chrome, tab baru kosong.
2. Siapkan stopwatch di HP lain. Ketik alamat `/app`; mulai stopwatch saat menekan Enter; berhenti saat soal pertama terlihat dan bisa diklik. Catat detiknya (**T1**).
3. Tekan "Selanjutnya" 10 kali berturut-turut. Hitung berapa kali ada jeda terasa lebih dari 1 detik (**J**).
4. Kerjakan simulasi sampai soal terakhir. Catat apakah halaman me-refresh/crash dan di soal ke berapa (**C**).
5. Buka AI Tutor, kirim 1 pertanyaan. Catat detik sampai balasan pertama muncul (**T2**).
6. Kirim ke Muse: merek/tipe HP, jaringan (WiFi/4G), T1, J, C, T2. Ulangi di HP kedua. Setelah perbaikan, ulangi dengan cara yang sama.

### I.3 Tes manual alur bayar (Fase 6, untuk Agus)

1. Buat akun uji (login Google kedua). Kerjakan satu tryout sampai selesai; pastikan Autopsi preview muncul dan sisanya terkunci.
2. Klik "Beli Paket Sprint", pilih tanggal TKA, lihat QRIS + nominal unik.
3. Bayar nominal persis tersebut ke QRIS (sekali, memakai uang asli), klik "Sudah bayar" → WhatsApp terbuka dengan pesan siap kirim.
4. Di `/admin/orders`, cari nominal itu → "Tandai lunas".
5. Kembali ke akun uji, muat ulang: Autopsi penuh dan Rencana terbuka; Akun menampilkan tanggal berakhir.
6. Ubah tanggal masa aktif ke kemarin lewat admin → muat ulang: terkunci lagi.
7. Login dengan akun lain: pastikan tidak bisa melihat order atau attempt akun uji.
