# TKA Master — 15s Motion Showreel (promo/)

Status log + decisions. Everything lives in `promo/`; the app (index.html, app.js, style.css, …) is untouched.

## Status
- [x] Repo research (selectors, localStorage keys, AI endpoints)
- [x] `capture/capture.js` — real app driven by Playwright @ 390x844 (DSF 3 → 1170x2532 PNGs) → `public/shots/*.png` + `manifest.json` (tap coordinates)
- [x] `capture/capture_progres.js` — re-capture of Progress panel (first pass shot it before the Material Symbols icon font loaded in the iframe)
- [x] Remotion skeleton (package.json, tsconfig, index.ts, Root.tsx, lib.ts) — deps installed
- [x] Scenes in Remotion (`src/Showreel.tsx` timeline + camera, `src/parts.tsx` components)
- [ ] Low-res test render → fixes → final render `out/showreel.mp4`

## Scene map (30 fps, 450 frames)
| Frames | Time | Screen (real captures) | Motion |
|---|---|---|---|
| 0–45 | 0.0–1.5 | home_top | Phone flies in on a spring (rotX/rotZ settle), 3D yaw, glare sweep; caption "Ace the TKA." word-by-word springs + lime pill swipe |
| 45–110 | 1.5–3.7 | home_top → home_card | Real scroll (fixed header/bottom nav kept static), camera push to Geografi Paket 1, **card lifts out** (real element screenshot) with shadow, finger tap; "Pick a subject." |
| 110–196 | 3.7–6.5 | q_top → q_options → wrong selected → wrong feedback | Zoom-through + white flash into the question, scroll to options, tap A, tap Cek Jawaban → red vignette, red ring burst, decaying **shake**; "Test yourself." / "Wrong? No stress." |
| 196–245 | 6.5–8.2 | pemb_top → pemb_mid → rail_open → tutor_open | Slide-left tab push with yaw swing, scroll, zoom on the floating rail, tap "Tanya AI", bottom sheet slides up; "Learn why." |
| 245–316 | 8.2–10.5 | typing → thinking → 10 streaming frames | Zoom on input while typing, tap send, "Sedang menyusun…" then streamed answer (snapshot every 4 frames) with slow push-in; "Ask your AI tutor." |
| 316–361 | 10.5–12.0 | q_retry → right selected → right feedback | Whip-pan (yaw + motion blur), tap C, Cek Jawaban → green glow, ring burst, confetti; "Try again." / "Nailed it!" |
| 361–405 | 12.0–13.5 | result | Push-up transition, camera zooms onto the real score row, overlay counts **0→80%**, chips count **8 correct / 2 wrong** with springs |
| 405–450 | 13.5–15.0 | progres_top → progres_mid | Slide-left, scroll through analytics; "Watch it grow."; phone shrinks down, outro lockup: real app logo (cropped from capture) springs in, "TKA Master" letter stagger, "Practice smarter. Score higher." |

Global: parallax background (glow blobs, grid, giant outlined marquee type, depth particles all offset by the camera), ambient float on the phone, bottom progress bar.

## Decisions
- **Tool:** Remotion 4 (React, frame-accurate springs/easing, bundled ffmpeg — no system ffmpeg on this machine).
- **Subject:** Geografi Paket 1 (exactly 10 soal) so the real result screen naturally shows **80% / 8 benar / 2 salah**. The question shown is **Soal 9** (banjir Kota Bekasi): wrong pick **A**, correct **C**.
- **Demo data (localStorage):** `tka_user_subjects` = geografi, matematika, bahasa_inggris, fisika; `tka_progress` with ~80 answered questions across subjects; `tka_study_streak` = 12 → Progress panel shows 12 Hari streak, ~105 mnt study time, 78% accuracy.
- **AI tutor:** `/api/tutor/state|new|chat` intercepted in Playwright and answered with a pre-written 3-step Indonesian explanation (1.5s fake latency) — deterministic, zero quota. The app's chat is non-streaming, so the "streaming" effect uses 10 snapshots where the *app's own* `renderChatHistory()` renders growing prefixes of the reply (real UI rendering at every step).
- **Mobile AI entry point:** on mobile the "Tanya AI" tab is hidden; the real path is the floating work rail (tap → expand → "Tanya AI"). Captured that way.
- **Result scene:** answers for all 10 soal set through `state.userAnswers` + the app's `persistAnswerProgress()`, then the app's `selesaiTes()` renders the real review overlay.
- **Correct-answer scene:** the question is "retried" (previous pick cleared, `renderQuestion()`), then C is clicked + Cek Jawaban → real green feedback.
- **Captions:** short English phrases; app UI stays Indonesian.
- **Look:** deep green gradient background (#021009 → #0b4d2e), mint #3ddc84 / lime #c3f56b accents, red #ff4d5e for errors; Plus Jakarta Sans (same family as the app's dashboard).

## Known app-side observations (not fixed — out of scope)
- The red/green feedback banner on mobile lays its text out in columns (flex children), visible in the capture as-is.
- Progress panel bottom-nav tap coordinates are not available (nav lives inside the iframe) → tap position uses a fallback.
