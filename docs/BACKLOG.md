# BACKLOG — TKA Master

Satu baris per ide; dikerjakan hanya bila brief/fase memintanya.

- B1 (Lampiran B #3): tab modul (Wajib/Saintek/Soshum/Bahasa) + navbar tetap tampil saat scroll di menu modul — kosmetik.
- B2 (Lampiran B #4): layout pembahasan/Pilar membingungkan + user tidak tahu AI Tutor paham konteks soal — kecuali tooltip Ragu-ragu (T3.7).
- B3 (Lampiran B #9): chat AI Tutor menampilkan soal sekaligus (hemat layar mobile).
- B4 (temuan T0.9): pindahkan penyimpanan tulis (kuota/chat/feedback/flag) ke Supabase/persisten — prasyarat Fase 3/6.
- B5 (temuan T0.10): verifikasi JWT Supabase di `server.py` — wajib sebelum Fase 3/6.
- B6: evaluasi opsi provider AI berbayar tunggal vs multi-key gratis (T2.10) — keputusan Agus.
- B7 (JANGAN sebelum 26 Okt + izin Agus): mapel/paket baru, model AI baru, leaderboard, bank soal UTBK, animasi landing, payment gateway otomatis (webhook), bot WA, push notification, service worker/offline penuh, badge "Terverifikasi", live chat, dark mode, multi-bahasa, analitik pihak ketiga, refactor besar, upgrade framework, bersih-bersih repo.
- B8 (keputusan Agus, MODE MALAM): `feature_flags` pindah dari SQLite ke Supabase di Fase 3 — saat ini perubahan flag via admin ikut hilang tiap redeploy Railway (ephemeral).

- URL routing yang jelas (/app/beranda, /app/kuis/:mapel/:paket, /app/hasil/:id) — SPA saat ini pakai query param + hash, bikin susah debug & share link. Refactor besar, setelah 26 Okt.

- Layout section Autopsi di halaman hasil terlalu besar (overflow di desktop & mobile). Perkecil + buat scroll internal yang rapi. (temuan 9 Okt 2026)
