# ARCHITECTURE — TKA Master

Inventaris Fase 0 (T0.3), main@`3605aab` (8 Okt 2026). Ringkasan aturan lama repo (T0.8) di bagian bawah.

## 1. Stack

| Lapisan | Teknologi |
|---|---|
| Frontend | HTML + CSS + vanilla JS statis, **tanpa build/bundler**. `index.html` (halaman `/app`), `landing.html` (`/`), `app.js` (~216 KB / 5783 baris — seluruh logika app), `style.css`, `mobile-improve.css`, `home_desktop.html`, `workspace_akun/akun.html`, `supabase_auth.js`. Cache-busting manual `?v=N` di `index.html`. |
| Backend | Python **stdlib murni** (`server.py`, 1741 baris): `ThreadingHTTPServer` [server HTTP multi-thread bawaan Python], tanpa framework. `requirements.txt` kosong. |
| Database | SQLite [database file lokal] `data/ai_tutor.db` (bisa dioverride via env `TUTOR_DB_PATH`). Tabel: `ai_tutor_conversations`, `ai_tutor_messages`, `ai_tutor_users` (kuota), `ai_tutor_devices` (anti-abuse tamu), `feedback` — dibuat idempoten [dibuat bila belum ada] di `tutor_store.init_db()` saat start. |
| Auth | Google OAuth via **Supabase Auth** (client-side, `supabase_auth.js` + CDN `supabase-js`). Supabase juga menyimpan `users`, `feedback`, `bug_reports` (+ RLS [aturan akses per baris]). **Server Python tidak memverifikasi JWT [token identitas] Supabase** — lihat T0.10. |
| AI Tutor | 100% server-side: `tutor_engine.py` → `tutor_llm.py` (multi-provider Groq/OpenRouter/Alibaba/Gemini, round-robin [rotasi bergantian] key per provider, cooldown saat 429 [jeda saat kena batas rate], semaphore maks 6 konkuren). Prompt dirakit **server** dari `soal_id` (`resolve_tutor_context`: teks soal, opsi, kunci, pembahasan, transkripsi gambar `visual_context`). Kuota: tamu 5/hari, login 25/hari, subscriber 100/hari; reset 00.00 WIB; enforcement di server. |
| Data soal | `data/` (~290 MB): `*_paket_N_learning.json` (soal + pembahasan 5 Pilar), `*_sidecar_transcriptions.json` (transkripsi gambar untuk AI), `*_text_only.json`, gambar lokal. Dimuat on-demand per paket (`/api/solution` + static serving dengan allowlist [daftar file yang diizinkan]). |
| Progres | `localStorage` [penyimpanan di browser] perangkat (`tka_progress`). Timer JS dihitung dari timestamp. |
| Deploy | Railway, **auto-deploy tiap merge ke `main`**. `railway.json`: builder NIXPACKS, `startCommand: python server.py`. **Tanpa Volume** → filesystem ephemeral [sementara; tulisan hilang tiap deploy/restart] → lihat T0.9. |

## 2. Alur (teks)

```
Browser ──▶ server.py (routing)
  ├─ / → landing.html · /app → index.html · /privacy · /terms
  ├─ /pengunjung (?key=VISITOR_ADMIN_KEY) · /audit[.txt] (snapshot reviewer AI)
  ├─ /api/tutor/chat|new|state|reset_quota|sync_user → tutor_engine → tutor_llm → provider AI
  ├─ /api/solution → data/*.json (soal, Pilar, transkripsi gambar)
  ├─ /api/feedback, /api/flags (baru, T0.7), /api/admin/flags (baru, T0.7)
  ├─ SQLite data/ai_tutor.db via tutor_store.py (kuota, chat, device, feedback, flags)
  └─ Supabase: HANYA login (JS klien) + tabel users/feedback/bug_reports
```

## 3. Env var (nama saja)

`PORT`, `PUBLIC_DEMO`, `VISITOR_ADMIN_KEY`, `OPENAI_COMPATIBLE_BASE_URL`, `LLM_API_KEYS`, `LLM_MODEL`, `OPENROUTER_API_KEYS`, `ALIBABA_API_KEY`, `GEMINI_API_KEYS`, `OLLAMA_BASE_URL`, `RATE_LIMIT_COOLDOWN_SEC`, `RATE_LIMIT_MAX_PER_MIN`, `LLM_MAX_CONCURRENT`, `TUTOR_DB_PATH`. Direncanakan (TODO-AGUS): `PASS_PRICE`, `AI_DAILY_BUDGET_IDR`, `QRIS_IMAGE_URL`, `WA_NUMBER`.

## 4. Tes / CI

Tidak ada CI. Tes Playwright manual di `scratch/` (node_modules di `scratch/`).

## 5. Ringkasan aturan lama di repo (T0.8)

- **ATURAN_AI.md** — tata kerja multi-AI paralel: tiap AI hanya di folder kerjanya, dilarang sentuh file AI lain (`index.html`, `app.js`, `style.css`, `server.py`…); deliverable HTML mandiri; integrasi via `postMessage`; design token Stitch; **kejujuran data** (dilarang menampilkan angka karangan).
- **AI_DESIGN_RULE.md** — untuk AI yang mengerjakan UI: jangan ubah logika/data/rendering math/font soal; ikuti `DESIGN.md`.
- **DESIGN.md** — "Clean Editorial" (Vercel×Notion): 90% permukaan netral, satu aksen hijau (`#1F6F4A`/`#34D399`), radius 6/8px, Light+Dark, hierarki lewat tipografi, panel Tutor docked.
- **KONTRAK_DATA.md** — sumber kebenaran data: 22 mapel / 44 paket / 961 soal (per 4 Okt 2026); format progres `tka_progress` di localStorage; dilarang mengarang angka.
- **PRD.md** — dokumen master end-to-end (scraping Pusmendik → normalisasi → 5 Pilar → soal serupa → audit → runtime + AI Tutor). Historis, fokus pipeline data.
- **PLAN.md** — roadmap + status (5 fase selesai: design system, mobile, landing/legal, kuota, feedback); cara run lokal; daftar env; utang konten.
- **HANDOVER_PROMPT.md** — catatan serah terima antar-AI (peta file, status Home, jebakan teknis). Sebagian kedaluwarsa: menyebut Windows/PowerShell, sesi ini Linux.

**Konflik dengan brief baru (dilaporkan, tidak diputuskan sendiri):**
1. `PLAN.md` masih menargetkan "conversion ke Pro (Rp20.000/bulan)" — brief baru mengganti dengan **Paket Sprint TKA Rp14.900 sekali bayar** (keputusan Agus 7–8 Okt). Brief baru menang.
2. `PLAN.md` menyebut Google OAuth "TODO jika sempat" — **sudah jalan** (Okt 2026).
3. `ATURAN_AI.md` (wilayah folder per AI) dibuat untuk era multi-AI paralel; kini eksekutor tunggal per brief. Prinsipnya tetap dipakai: *satu tugas = satu perubahan kecil, jangan sentuh file di luar tugas.*

## 6. Temuan arsitektur untuk fase berikutnya

- **T0.9 (kritis):** `railway.json` tanpa Volume → SQLite ephemeral; tulisan runtime (kuota/chat/feedback/flag) **hilang tiap redeploy**. `data/ai_tutor.db` **tidak** ada di `main` (dicek via API 8 Okt 2026 — observasi lama di brief sudah kedaluwarsa; file ini di-`.gitignore`). Aturan keras: order & pass **wajib** di Supabase (persisten), bukan SQLite lokal.
- **T0.10 (kritis):** server tidak memverifikasi identitas Supabase — `/api/tutor/sync_user` percaya klaim `logged_in` dari klien. Sebelum Fase 3/6, server harus verifikasi JWT dan memetakan ke `user_id`.
- **T0.7:** flag via tabel `feature_flags` (ubah tanpa deploy lewat `/api/admin/flags`); konsekuensi: ikut hilang saat redeploy sampai DB pindah ke Supabase.
