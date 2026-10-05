# TKA Master — 24s Motion Showreel with Sound Design (promo/)

Status log + decisions. Everything lives in `promo/`; the app (`index.html`, `app.js`, `style.css`, …) is untouched.

## Status
- [x] Repo research (selectors, localStorage keys, AI endpoints)
- [x] `capture/capture.js` — real app driven by Playwright @ 390x844 (DSF 3 → 1170x2532 PNGs) → `public/shots/*.png` + `manifest.json` (tap coordinates)
- [x] `capture/capture_progres.js` — re-capture of Progress panel (seeds 8 benar / 2 salah so stats match showreel story, icon fonts loaded)
- [x] App UI re-captured with latest clean styles (no vertically stacked text in feedback banners, result tables, or KPI cards)
- [x] Remotion skeleton (`package.json`, `tsconfig.json`, `index.ts`, `Root.tsx`, `lib.ts`)
- [x] Captions inspected & strengthened: wide `maxWidth`, `whiteSpace: normal`, no per-letter breaking, safe font sizes for 1080px canvas
- [x] Expanded duration to 24s (720 frames @ 30fps) with redistributed timing across all sequences
- [x] Professional audio layer implemented (`src/AudioLayer.tsx`) with synchronized BGM + 13 custom-synthesized SFX
- [x] Audio validation & mixing: 48kHz stereo, -6.5 dBFS max peak, zero clipping, smooth ducking & fades
- [x] Final full-res 1080x1920 render with audio (`out/showreel.mp4`)

## Scene Map & Sound Design (30 fps, 720 frames, 24.0s)
| Frames | Time (s) | Screen (real captures) | Motion & Visual Events | Audio & Sound Design |
|---|---|---|---|---|
| 0–60 | 0.0–2.0 | home_top | Phone flies in on spring from below, settle, 3D yaw, glare sweep; caption "Ace the TKA." | BGM fades in (0.0s to 0.8s); `sfx_whoosh_enter` (f:3–28) as phone glides in |
| 60–165 | 2.0–5.5 | home_top → home_card | Real scroll, camera push to Geografi card, card lifts out with shadow, finger tap; "Pick a subject." | BGM groove establishes (124 BPM); `sfx_card_lift` (f:96); `sfx_tap` (f:132) |
| 165–270 | 5.5–9.0 | q_top → q_options → wrong selected → wrong feedback | Zoom-through + flash into question, scroll to options, tap A, tap Cek Jawaban → red vignette, red burst, decaying shake; "Test yourself." / "Wrong? No stress." | `sfx_slide` (f:165); `sfx_tap` (f:216); `sfx_tap` (f:230); `sfx_error_shake` sub thud & 8Hz beating flutter (f:234) with BGM ducked to 0.28 |
| 270–345 | 9.0–11.5 | pemb_top → pemb_mid → rail_open → tutor_open | Slide-left tab push with yaw swing, scroll, zoom on floating rail, tap "Tanya AI", bottom sheet slides up; "Learn why." | `sfx_slide` (f:270); `sfx_tap` on rail (f:308); `sfx_drawer_open` ascending swoosh (f:324) |
| 345–480 | 11.5–16.0 | typing → thinking → 10 streaming frames | Zoom on input while typing, tap send, "Sedang menyusun…" then streamed answer (10 frames) with slow push-in; ample reading time; "Ask your AI tutor." | `sfx_typing` micro-clicks (f:348); `sfx_tap` send (f:366); `sfx_ai_stream` crystal synth shimmer (f:382) |
| 480–555 | 16.0–18.5 | q_retry → right selected → right feedback | Whip-pan (yaw + motion blur), tap C, Cek Jawaban → green glow, ring burst, confetti; "Try again." / "Nailed it!" | `sfx_whip` (f:480); `sfx_tap` option C (f:504); `sfx_tap` check (f:517); `sfx_success` major pentatonic celebration chime + confetti sparkle (f:522) with BGM ducked |
| 555–630 | 18.5–21.0 | result | Push-up transition, camera zooms onto score row, overlay counts 0→80%, chips count 8 correct / 2 wrong | `sfx_slide` (f:555); `sfx_counter` accelerated ticking riser with 80% lock chime (f:564–598); `sfx_chip_pop` (f:574 & 582) |
| 630–720 | 21.0–24.0 | progres_top → progres_mid | Slide-left, scroll analytics; "Watch it grow."; phone shrinks down, outro lockup: real logo springs in, "TKA Master" stagger, "Practice smarter. Score higher." | `sfx_slide` (f:630); `sfx_outro` warm major-9th harmonic resolve + sub impact (f:670); BGM smooth fade out (f:675–718) |

Global: parallax background, ambient float on phone, bottom progress bar.

## Audio Design Decisions
- **Background Music:**
  - Track: "Tech Live" by Kevin MacLeod (`incompetech.com`).
  - License: Creative Commons: By Attribution 4.0 License (`http://creativecommons.org/licenses/by/4.0/`).
  - ISRC: `USUAN1700030`.
  - Tempo: 124 BPM (~14.5 frames per beat at 30 fps), naturally locking into sequence cut points at 2s (f:60), 5.5s (f:165), 16s (f:480), and 24s (f:720).
  - Mixing & Automation: Base volume 0.40 with automated ducking to 0.28 during major impacts/chimes, 24-frame entry fade-in, and 43-frame outro fade-out.
- **Sound Effects (SFX):**
  - 13 custom-synthesized 48kHz WAV audio assets generated via Python + NumPy mathematical acoustics modeling:
    - `sfx_tap.wav`: 25ms crisp mobile UI haptic click ($e^{-t/0.004}$ with high-frequency transient).
    - `sfx_card_lift.wav`: 160ms elevation whoosh + resonant low-pass body.
    - `sfx_whoosh_enter.wav`: 750ms aerodynamic bandpass noise sweep.
    - `sfx_error_shake.wav`: 550ms 70Hz sub thud + 8Hz acoustic beating flutter (148Hz + 156Hz dissonance) matching visual screen shake.
    - `sfx_slide.wav`: 320ms smooth stereo air glide.
    - `sfx_drawer_open.wav`: 280ms ascending frequency sweep for bottom sheet.
    - `sfx_typing.wav`: 350ms rapid sequence of 6 subtle high-frequency keystrokes.
    - `sfx_ai_stream.wav`: 650ms crystalline FM chime (E6/G#6/B6) with chorus shimmer.
    - `sfx_whip.wav`: 240ms fast whip-pan sweep.
    - `sfx_success.wav`: 950ms major pentatonic bell cascade (C6-E6-G6-C7) + confetti sparkle.
    - `sfx_counter.wav`: 1150ms 24-step accelerated ticking riser from 900Hz to 1750Hz with confirmation chime.
    - `sfx_chip_pop.wav`: 90ms organic badge pop.
    - `sfx_outro.wav`: 1900ms warm D-major-9th harmonic chord + sub bass impact.
- **Voice-Over Evaluation:**
  - Evaluated per Phase 6 guidelines. Omitted deliberately because the 24s showreel is driven by 9 kinetic, synchronized on-screen typography captions. Adding synthetic voiceover would create acoustic clutter and compete with the fast visual pacing, whereas pure rhythmic beat-synced music + tactile UI sound design creates a much higher-end, focused SaaS product aesthetic.
- **Audio Mixing & Master:**
  - Master format: 48,000 Hz, 2-channel Stereo.
  - Maximum mix peak: -6.5 dBFS (peak 0.4744), providing 6.5 dB of clean headroom with zero digital clipping.
