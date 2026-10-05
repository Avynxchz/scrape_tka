import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { loadFont } from '@remotion/google-fonts/PlusJakartaSans';
import { C, Cam, camAt, CamKey, clamp, easeIn, easeOut, K, manifest, mbox, mnum, ramp, SW, toCanvas, W } from './lib';
import { Background, Burst, Caption, Confetti, Phone, ProgressBar, ScreenStack, Seg, Tap } from './parts';
import { AudioLayer } from './AudioLayer';

const { fontFamily } = loadFont('normal', { weights: ['600', '800'], subsets: ['latin'] });

// ------------------------------------------------------------------
// Tap targets from the capture manifest (CSS px in the 390x844 viewport)
// ------------------------------------------------------------------
const P = {
  card: mbox('home_card', 'tap', { cx: 135, cy: 422, x: 0, y: 342, w: 270, h: 160 }),
  wrong: mbox('q_options', 'wrong', { cx: 195, cy: 351 }),
  wrongFb: mbox('q_wrong_feedback', 'wrong', { cx: 195, cy: 251 }),
  check: mbox('q_wrong_feedback', 'tap', { cx: 168, cy: 819 }),
  rail: mbox('rail_open', 'tap', { cx: 359, cy: 727 }),
  ai: mbox('rail_open', 'ai', { cx: 352, cy: 718 }),
  send: mbox('tutor_typing2', 'send', { cx: 345, cy: 783 }),
  right: mbox('q_retry', 'right', { cx: 195, cy: 522 }),
  rightFb: mbox('q_right_feedback', 'right', { cx: 195, cy: 432 }),
  check2: mbox('q_right_feedback', 'tap', { cx: 168, cy: 819 }),
  persen: mbox('result', 'persen', { cx: 330, cy: 193 }),
};
const homeDelta = mnum('home_card', 'scrollDelta', 168);
const qDelta = mnum('q_options', 'scrollY', 618);
const wrongDelta = Math.round(P.wrong.cy - P.wrongFb.cy); // 100
const rightDelta = Math.round(P.right.cy - P.rightFb.cy); // 90

// ------------------------------------------------------------------
// Screen timeline (frame -> real screenshot + in-screen transition)
// ------------------------------------------------------------------
const stream = new Array(10).fill(0).map((_, i): Seg => ({ f: 382 + i * 4, shot: `tutor_stream_${String(i + 1).padStart(2, '0')}` }));
const SEGS: Seg[] = [
  { f: 0, shot: 'home_top' },
  { f: 68, shot: 'home_card', tr: 'scroll', d: 16, delta: homeDelta, bandTop: 64, bandBottom: 56 },
  { f: 165, shot: 'q_top', tr: 'zoomIn', d: 12 },
  { f: 190, shot: 'q_options', tr: 'scroll', d: 16, delta: qDelta, bandBottom: 51 },
  { f: 216, shot: 'q_wrong_selected' },
  { f: 232, shot: 'q_wrong_feedback', tr: 'scroll', d: 7, delta: wrongDelta, bandBottom: 51 },
  { f: 270, shot: 'pemb_top', tr: 'slideLeft', d: 11 },
  { f: 286, shot: 'pemb_mid', tr: 'scroll', d: 14, delta: 700 },
  { f: 308, shot: 'rail_open' },
  { f: 324, shot: 'tutor_open', tr: 'sheetUp', d: 11 },
  { f: 348, shot: 'tutor_typing1' },
  { f: 356, shot: 'tutor_typing2' },
  { f: 366, shot: 'tutor_thinking' },
  ...stream,
  { f: 480, shot: 'q_retry', tr: 'whip', d: 11 },
  { f: 504, shot: 'q_right_selected' },
  { f: 518, shot: 'q_right_feedback', tr: 'scroll', d: 7, delta: rightDelta, bandBottom: 51 },
  { f: 555, shot: 'result', tr: 'pushUp', d: 12 },
  { f: 630, shot: 'progres_top', tr: 'slideLeft', d: 11 },
  { f: 646, shot: 'progres_mid', tr: 'scroll', d: 14, delta: 560, bandTop: 57, bandBottom: 56 },
];

const TAPS = [
  { at: 132, ...P.card },
  { at: 216, ...P.wrong },
  { at: 230, ...P.check },
  { at: 308, ...P.rail },
  { at: 324, ...P.ai },
  { at: 366, ...P.send },
  { at: 504, ...P.right },
  { at: 517, ...P.check2 },
];

// ------------------------------------------------------------------
// Camera keyframes (zoom s, focus fx/fy in CSS px, ty = canvas y for focus)
// ------------------------------------------------------------------
const KEYS: CamKey[] = [
  { f: 0, s: 1, ry: -16, rx: 8 },
  { f: 50, s: 1, ry: 0, rx: 0, e: easeOut },
  { f: 60, s: 1 },
  { f: 88, s: 1.32, fx: 150, fy: 422, ty: 1120 },
  { f: 132, s: 1.42, fx: 140, fy: 422, ty: 1110 },
  { f: 165, s: 2.1, fx: 135, fy: 422, ty: 1100, e: easeIn },
  { f: 165.01, s: 1.12 },
  { f: 182, s: 1, e: easeOut },
  { f: 190, s: 1 },
  { f: 210, s: 1.28, fx: 195, fy: 430, ty: 1110 },
  { f: 228, s: 1.34, fx: 195, fy: 450, ty: 1110 },
  { f: 242, s: 1.14, fx: 195, fy: 470, ty: 1100, e: easeOut },
  { f: 268, s: 1.18, fx: 195, fy: 470, ty: 1100 },
  { f: 278, s: 1, ry: 9 },
  { f: 290, s: 1, ry: 0 },
  { f: 308, s: 1.5, fx: 300, fy: 660, ty: 1230 },
  { f: 324, s: 1.55, fx: 300, fy: 670, ty: 1230 },
  { f: 342, s: 1, e: easeOut },
  { f: 350, s: 1 },
  { f: 362, s: 1.42, fx: 195, fy: 720, ty: 1250 },
  { f: 372, s: 1.42, fx: 195, fy: 720, ty: 1250 },
  { f: 388, s: 1.2, fx: 195, fy: 400, ty: 1110 },
  { f: 472, s: 1.32, fx: 195, fy: 470, ty: 1110 },
  { f: 483, s: 1.04, ry: -24, e: easeIn },
  { f: 494, s: 1, ry: 0, e: easeOut },
  { f: 508, s: 1.28, fx: 195, fy: 480, ty: 1120 },
  { f: 526, s: 1.16, fx: 195, fy: 480, ty: 1100, e: easeOut },
  { f: 550, s: 1.18, fx: 195, fy: 480, ty: 1100 },
  { f: 560, s: 0.94 },
  { f: 572, s: 1, e: easeOut },
  { f: 590, s: 1.5, fx: 205, fy: 215, ty: 960 },
  { f: 625, s: 1.56, fx: 205, fy: 215, ty: 960 },
  { f: 636, s: 1 },
  { f: 652, s: 1.06, fy: 380 },
  { f: 678, s: 0.6, fy: 422, ty: 1420, e: easeOut },
  { f: 720, s: 0.6, fy: 422, ty: 1420 },
];

// ------------------------------------------------------------------
// Score overlay (count-up)
// ------------------------------------------------------------------
const ScoreOverlay: React.FC<{ font: string }> = ({ font }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < 556 || f > 632) return null;
  const inS = spring({ frame: f - 558, fps, config: { damping: 12, stiffness: 160 } });
  const out = ramp(f, 622, 630, easeIn);
  const n = Math.round(interpolate(f, [564, 598], [0, 80], { ...clamp, easing: easeOut }));
  const bump = f >= 598 ? 1 + 0.12 * Math.sin(Math.min(1, (f - 598) / 8) * Math.PI) : 1;
  const chip = (at: number, target: number, label: string, color: string, icon: string, x: number) => {
    const s = spring({ frame: f - at, fps, config: { damping: 11, stiffness: 180 } });
    const v = Math.round(interpolate(f, [at + 2, at + 14], [0, target], { ...clamp, easing: easeOut }));
    return (
      <div style={{ position: 'absolute', left: x, top: 1610, transform: `translate(-50%, ${(1 - s) * 140 + out * 160}px) scale(${0.6 + 0.4 * s})`, opacity: Math.min(1, s * 1.4) * (1 - out), display: 'flex', alignItems: 'center', gap: 22, padding: '22px 40px 22px 24px', borderRadius: 999, background: 'rgba(3,20,11,0.86)', border: `3px solid ${color}`, boxShadow: `0 20px 60px rgba(0,0,0,0.45), 0 0 40px ${color}55` }}>
        <div style={{ width: 74, height: 74, borderRadius: '50%', background: color, color: C.ink, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: font, fontWeight: 800, fontSize: 46 }}>{icon}</div>
        <div style={{ fontFamily: font, fontWeight: 800, fontSize: 76, color: C.white, letterSpacing: '-0.03em' }}>{v}</div>
        <div style={{ fontFamily: font, fontWeight: 600, fontSize: 44, color: C.white, opacity: 0.85 }}>{label}</div>
      </div>
    );
  };
  return (
    <>
      <div style={{ position: 'absolute', left: 0, right: 0, top: 70, display: 'flex', flexDirection: 'column', alignItems: 'center', transform: `translateY(${(1 - inS) * -120 - out * 140}px)`, opacity: Math.min(1, inS * 1.5) * (1 - out) }}>
        <div style={{ fontFamily: font, fontWeight: 800, fontSize: 40, letterSpacing: '0.45em', color: C.mint, marginBottom: -10, paddingLeft: '0.45em' }}>YOUR SCORE</div>
        <div style={{ display: 'flex', alignItems: 'flex-start', transform: `scale(${bump})` }}>
          <span style={{ fontFamily: font, fontWeight: 800, fontSize: 250, lineHeight: 1, color: C.white, letterSpacing: '-0.05em', textShadow: '0 16px 60px rgba(0,0,0,0.55)' }}>{n}</span>
          <span style={{ fontFamily: font, fontWeight: 800, fontSize: 110, lineHeight: 1.3, color: C.lime, marginLeft: 6 }}>%</span>
        </div>
      </div>
      {chip(574, 8, 'correct', C.mint, '\u2713', W * 0.29)}
      {chip(582, 2, 'wrong', C.red, '\u2715', W * 0.73)}
    </>
  );
};

// ------------------------------------------------------------------
// Outro lockup (logo cropped from the real app header)
// ------------------------------------------------------------------
const Outro: React.FC<{ font: string }> = ({ font }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < 670) return null;
  const logoS = spring({ frame: f - 672, fps, config: { damping: 11, stiffness: 170 } });
  const LOGO = 190;
  const sc = LOGO / 96; // logo is 96x96 px in the @3x capture (CSS 16..48 x 12..44)
  const title = 'TKA Master';
  const tag = spring({ frame: f - 688, fps, config: { damping: 14, stiffness: 160 } });
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: 210, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ width: LOGO, height: LOGO, borderRadius: 52, overflow: 'hidden', position: 'relative', transform: `scale(${logoS}) rotate(${(1 - logoS) * -120}deg)`, boxShadow: `0 24px 70px rgba(0,0,0,0.5), 0 0 0 6px rgba(195,245,107,${0.35 * logoS})` }}>
        <Img src={staticFile('shots/progres_top.png')} style={{ position: 'absolute', width: 1170 * sc, height: 2532 * sc, left: -48 * sc, top: -36 * sc, maxWidth: 'none' }} />
      </div>
      <div style={{ display: 'flex', marginTop: 34 }}>
        {title.split('').map((ch, i) => {
          const s = spring({ frame: f - 676 - i * 1.2, fps, config: { damping: 12, stiffness: 210, mass: 0.6 } });
          return (
            <span key={i} style={{ display: 'inline-block', whiteSpace: 'pre', fontFamily: font, fontWeight: 800, fontSize: 138, lineHeight: 1.05, letterSpacing: '-0.04em', color: i >= 4 ? C.lime : C.white, transform: `translateY(${(1 - s) * 120}px) scale(${0.5 + 0.5 * s})`, opacity: Math.min(1, s * 1.6), textShadow: '0 14px 50px rgba(0,0,0,0.5)' }}>
              {ch}
            </span>
          );
        })}
      </div>
      <div style={{ marginTop: 18, fontFamily: font, fontWeight: 600, fontSize: 50, color: C.white, opacity: tag, transform: `translateY(${(1 - tag) * 50}px)`, letterSpacing: '-0.01em', textAlign: 'center', maxWidth: 960, whiteSpace: 'normal' }}>
        Practice smarter. <span style={{ color: C.mint }}>Score higher.</span>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------
// Card "lift out" (real element screenshot of the subject card)
// ------------------------------------------------------------------
const CardLift: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < 96 || f >= 165) return null;
  const l = spring({ frame: f - 98, fps, config: { damping: 12, stiffness: 150 } });
  const press = f >= 132 ? interpolate(f, [132, 136, 140], [1, 0.95, 1], clamp) : 1;
  const grow = ramp(f, 154, 165, easeIn);
  const b = P.card;
  const scale = (1 + 0.08 * l) * press * (1 + grow * 0.5);
  return (
    <>
      <div style={{ position: 'absolute', inset: 0, background: `rgba(2,16,9,${0.35 * l})` }} />
      <Img
        src={staticFile('shots/card.png')}
        style={{
          position: 'absolute', left: b.x * K, top: b.y * K, width: b.w * K, height: b.h * K,
          transform: `translateY(${-18 * l}px) scale(${scale})`, transformOrigin: '50% 50%',
          borderRadius: 24, boxShadow: `0 ${30 * l}px ${70 * l}px rgba(0,0,0,${0.4 * l}), 0 0 0 ${4 * l}px ${C.mint}`,
          opacity: 1 - grow * 0.3,
        }}
      />
    </>
  );
};

export const Showreel: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();

  // hook entry spring (phone flies in from below)
  const entry = spring({ frame: f - 3, fps, config: { damping: 15, stiffness: 95, mass: 0.9 } });
  let cam: Cam = camAt(KEYS, f);
  cam = {
    ...cam,
    ty: cam.ty + (1 - entry) * 1750 + Math.sin(f / 26) * 6,
    rx: cam.rx + (1 - entry) * 40,
    rz: cam.rz + (1 - entry) * -14 + Math.sin(f / 40) * 0.6,
    ry: cam.ry + Math.sin(f / 33) * 1.2,
  };

  // wrong-answer shake
  const ts = f - 234;
  const shakeX = ts >= 0 && ts < 22 ? 30 * Math.sin(ts * 2.3) * Math.exp(-ts / 6) : 0;
  const shakeR = ts >= 0 && ts < 22 ? 1.4 * Math.sin(ts * 2.3 + 1) * Math.exp(-ts / 6) : 0;
  const red = f >= 233 ? interpolate(f, [233, 236, 262], [0, 1, 0], clamp) : 0;
  const green = f >= 520 ? interpolate(f, [520, 524, 552], [0, 1, 0], clamp) : 0;
  const flash = Math.max(
    interpolate(f, [164, 166, 172], [0, 0.55, 0], clamp),
    interpolate(f, [669, 672, 682], [0, 0.35, 0], clamp),
  );
  const glare = f < 60 ? ramp(f, 8, 48) : f < 670 ? (f >= 555 && f < 595 ? ramp(f, 555, 595) : 0) : ramp(f, 670, 720);

  const wrongC = toCanvas(cam, P.wrongFb.cx, P.wrongFb.cy);
  const rightC = toCanvas(cam, P.rightFb.cx, P.rightFb.cy);

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg0, fontFamily }}>
      <Background cam={cam} red={red} green={green} flash={flash} font={fontFamily} />

      <Phone cam={cam} shakeX={shakeX} shakeR={shakeR} glare={glare}>
        <ScreenStack segs={SEGS} />
        <CardLift />
        {TAPS.map((t, i) => (
          <Tap key={i} at={t.at} x={t.cx} y={t.cy} />
        ))}
      </Phone>

      <Burst at={234} x={wrongC.x} y={wrongC.y} color={C.red} />
      <Burst at={522} x={rightC.x} y={rightC.y} color={C.mint} />
      <Confetti at={522} x={rightC.x} y={rightC.y} />

      {/* legibility band for captions */}
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(2,16,9,0.85) 0%, rgba(2,16,9,0.55) 15%, rgba(2,16,9,0) 27%)', pointerEvents: 'none' }} />

      <Caption font={fontFamily} from={6} to={54} y={150} size={138} lines={[[{ t: 'Ace' }, { t: 'the' }, { t: 'TKA.', hl: 'lime' }]]} />
      <Caption font={fontFamily} from={66} to={156} y={170} size={124} lines={[[{ t: 'Pick' }, { t: 'a' }, { t: 'subject.', hl: 'lime' }]]} />
      <Caption font={fontFamily} from={170} to={224} y={170} size={124} lines={[[{ t: 'Test' }, { t: 'yourself.', hl: 'mint' }]]} />
      <Caption font={fontFamily} from={232} to={266} y={170} size={124} lines={[[{ t: 'Wrong?', hl: 'red' }, { t: 'No' }, { t: 'stress.' }]]} />
      <Caption font={fontFamily} from={274} to={340} y={170} size={124} lines={[[{ t: 'Learn' }, { t: 'why.', hl: 'lime' }]]} />
      <Caption font={fontFamily} from={348} to={474} y={120} size={114} lines={[[{ t: 'Ask' }, { t: 'your' }], [{ t: 'AI tutor.', hl: 'lime' }]]} />
      <Caption font={fontFamily} from={484} to={516} y={170} size={124} lines={[[{ t: 'Try' }, { t: 'again.' }]]} />
      <Caption font={fontFamily} from={520} to={552} y={170} size={132} lines={[[{ t: 'Nailed' }, { t: 'it!', hl: 'mint' }]]} />
      <Caption font={fontFamily} from={632} to={666} y={170} size={124} lines={[[{ t: 'Watch' }, { t: 'it' }, { t: 'grow.', hl: 'lime' }]]} />

      <ScoreOverlay font={fontFamily} />
      <Outro font={fontFamily} />
      <ProgressBar />
      <AudioLayer />
    </AbsoluteFill>
  );
};

// keep TS happy about unused imports in some builds
void SW;
void manifest;
