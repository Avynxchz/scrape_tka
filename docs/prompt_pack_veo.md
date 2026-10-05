# 🎬 Prompt Pack — Veo (Gemini/Flow) × TKA Master

Cara pakai: buka Gemini (langganan Google Pro) atau Flow → pilih **Video** → untuk scene 1–3 pakai mode **image-to-video** (upload screenshot app sebagai frame pertama) → tempel prompt di bawah. Scene 4 cukup text-to-video.

---

## LANGKAH 0 — Ambil bahan dulu (5 menit)

Screenshot app kamu sendiri (ini kunci biar akurat, bukan clickbait):

| # | Layar | Cara ambil |
|---|---|---|
| A | Chat AI Tutor (ada pertanyaan + jawaban + kartu rumus) | Buka `/app` → Matematika Paket 1 → buka soal → tanya AI Tutor sampai ada jawaban → screenshot |
| B | Simulasi ujian (timer + grid nomor) | Jalankan simulasi → screenshot saat timer & grid terlihat |
| C | Pembahasan (langkah 1–5 + kunci) | Buka pembahasan satu soal → screenshot bagian langkah |
| D | (Opsional) Landing baru | `http://localhost:8080/` di HP → screenshot hero |

Tips rekaman: pakai HP (9:16), zoom browser 100%, sembunyikan notifikasi, mode gelap jangan diaktifkan (desain kita light).

---

## STORYBOARD (total ±24 detik, 9:16 vertikal)

| Scene | Durasi | Tipe | Isi |
|---|---|---|---|
| 1 | 8s | image-to-video (screenshot A) | Siswa bingung → nanya AI Tutor → jawaban muncul |
| 2 | 5s | image-to-video (screenshot B) | Timer jalan, nomor soal terisi |
| 3 | 6s | image-to-video (screenshot C) | Langkah pembahasan terbuka, kunci tersorot |
| 4 | 5s | text-to-video | Outro brand + CTA |

---

## SCENE 1 — AI Tutor (image-to-video)

```
Clean vertical UI demo video. Start exactly from the provided app screenshot
(an Indonesian math learning app, dark green #0B3D2E header, white chat panel).
Motion: a chat bubble slides in from the bottom right with a soft spring ease,
three typing dots pulse gently for one second, then an AI answer bubble fades in
word by word, and a yellow highlighter stroke draws itself left-to-right across
the final answer "(2, -1)". Camera: static, slight subtle zoom-in toward the
chat area. Style: crisp, modern, flat UI, soft shadows, no distortion of any
text, keep all UI text pixel-perfect and unchanged from the screenshot.
Lighting: bright, clean studio feel. No people, no hands, screen recording look.
```

**Negative / hindari:** teks berubah-ubah, huruf aneh, elemen UI tambahan yang tidak ada di screenshot, tangan/people, blur.

## SCENE 2 — Simulasi ujian (image-to-video)

```
Clean vertical UI demo video. Start exactly from the provided app screenshot
(exam screen with a circular timer ring and a grid of question numbers,
dark green and amber accents). Motion: the timer ring's green arc rotates
smoothly clockwise as if counting down, the remaining-time digits tick down
once, then question number squares fill with green one by one left to right,
fast rhythmic pacing. Camera: static with a very subtle push-in. Style: flat
modern UI, crisp edges, 60fps feel. All existing text must stay sharp and
unchanged. No people, no hands.
```

## SCENE 3 — Pembahasan (image-to-video)

```
Clean vertical UI demo video. Start exactly from the provided app screenshot
(step-by-step solution panel, numbered steps 1-5, dark green accents).
Motion: step 1 expands open, then step 2, step 3 open sequentially with a
smooth accordion ease, then a yellow highlight sweep draws across the final
answer line. Camera: slow subtle scroll down the panel, smooth and steady.
Style: flat UI, soft shadow, minimal. Keep every text label identical to the
screenshot, no invented text. No people.
```

## SCENE 4 — Outro brand (text-to-video, tanpa screenshot)

```
Minimal motion graphics, vertical 9:16. Deep emerald green background (#0B3D2E)
with a soft radial glow. Three small white rounded pill badges float upward
gently in 3D parallax, labeled exactly: "AI Tutor", "Simulasi", "Pembahasan".
They settle around a centered white graduation-cap icon inside a rounded square.
Below it, bold white headline fades up: "Latihan soal TKA, tanpa panik."
with "tanpa panik." in warm amber italic serif. Subtle grain, premium education
brand feel, smooth 60fps easing, 5 seconds, end on a held final frame.
```

> Kalau Veo merender teks headline dengan huruf salah (sering terjadi), split jadi 2 langkah: minta versi **tanpa teks dulu** (badge + logo saja), lalu tambahkan teks sendiri di CapCut/Canva — lebih rapi.

---

## SETTINGS YANG DISARANKAN
- Aspect ratio **9:16** (buat Reels/Shorts/TikTok) — kalau buat banner web, 16:9
- Resolution 1080p kalau tersedia
- Generate **2–3 take per scene**, pilih yang teksnya paling rapi
- Rakit di CapCut: scene 1→2→3→4, tambah musik lo-fi + caption kecil, tanpa transisi flashy (crossfade 0.2s cukup)

## CATATAN JUJUR
- Scene 1–3 wajib image-to-video; kalau text-to-video murni, UI-nya pasti rambutan
- Teks kecil di UI (angka grid, rumus) kadang tetap sedikit bergoyang — solusi: gerakan kamera statis + zoom pelan (sudah diminta di prompt), atau blur ringan saat transisi
- Simpan semua hasil generate; Veo tidak konsisten, kadang take ke-2 jauh lebih bagus
