import React from 'react';
import { AbsoluteFill, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { BEZEL, C, Cam, clamp, DUR, easeIn, easeOut, H, K, PCX, PCY, PH, PW, ramp, SH, SW, W } from './lib';

// ============================================================
// Background: gradient + parallax grid + giant marquee type + particles
// ============================================================
export const Background: React.FC<{ cam: Cam; red: number; green: number; flash: number; font: string }> = ({ cam, red, green, flash, font }) => {
  const f = useCurrentFrame();
  const px = -cam.tx * 0.12;
  const py = -cam.ty * 0.08;
  const marquee = (dir: number, y: number, text: string, speed: number, depth: number) => {
    const span = 2600;
    const x = ((dir * f * speed) % span) - (dir > 0 ? span : 0) + -cam.tx * depth;
    return (
      <div
        style={{
          position: 'absolute', top: y + py * depth * 4, left: x, whiteSpace: 'nowrap',
          fontFamily: font, fontWeight: 800, fontSize: 250, letterSpacing: '-0.04em', lineHeight: 1,
          color: 'transparent', WebkitTextStroke: '2px rgba(195,245,107,0.10)',
        }}
      >
        {(text + ' ').repeat(6)}
      </div>
    );
  };
  return (
    <AbsoluteFill style={{ background: `linear-gradient(170deg, ${C.bg1} 0%, ${C.bg0} 55%, #010805 100%)`, overflow: 'hidden' }}>
      {/* moving glow blobs */}
      <div style={{ position: 'absolute', width: 1300, height: 1300, borderRadius: '50%', left: -300 + Math.sin(f / 45) * 120 + px * 2, top: 250 + Math.cos(f / 60) * 90 + py * 2, background: 'radial-gradient(circle, rgba(61,220,132,0.30), rgba(61,220,132,0) 62%)' }} />
      <div style={{ position: 'absolute', width: 1100, height: 1100, borderRadius: '50%', left: 380 + Math.cos(f / 50) * 140 + px * 3, top: 1050 + Math.sin(f / 38) * 100 + py * 3, background: 'radial-gradient(circle, rgba(195,245,107,0.16), rgba(195,245,107,0) 60%)' }} />
      {/* grid */}
      <svg width={W + 240} height={H + 240} style={{ position: 'absolute', left: -120 + ((px * 1.5) % 90), top: -120 + ((f * 0.6 + py) % 90), opacity: 0.09 }}>
        <defs>
          <pattern id="g" width="90" height="90" patternUnits="userSpaceOnUse">
            <path d="M 90 0 L 0 0 0 90" fill="none" stroke={C.lime} strokeWidth="1.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#g)" />
      </svg>
      {marquee(-1, 520, 'PRACTICE · LEARN · MASTER ·', 5, 0.25)}
      {marquee(1, 1420, 'AI TUTOR · TKA 2026 · SCORE ·', 4, 0.4)}
      {/* depth particles */}
      {new Array(26).fill(0).map((_, i) => {
        const z = 0.3 + random(`z${i}`) * 1.2;
        const x0 = random(`x${i}`) * W;
        const y0 = random(`y${i}`) * H;
        const y = ((y0 - f * (1.2 + z * 2.2)) % (H + 100) + H + 100) % (H + 100) - 50;
        const x = x0 + Math.sin(f / 30 + i) * 14 - cam.tx * z * 0.35;
        const sz = 3 + z * 6;
        return <div key={i} style={{ position: 'absolute', left: x, top: y, width: sz, height: sz, borderRadius: '50%', background: i % 3 === 0 ? C.lime : C.mint, opacity: 0.18 + z * 0.3, filter: `blur(${z > 1.1 ? 1.5 : 0}px)` }} />;
      })}
      {/* event tints */}
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 55%, rgba(255,77,94,0) 30%, rgba(255,40,60,${0.55 * red}) 100%)` }} />
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 55%, rgba(61,220,132,${0.35 * green}) 0%, rgba(61,220,132,0) 70%)` }} />
      <AbsoluteFill style={{ background: `rgba(220,255,230,${flash})` }} />
    </AbsoluteFill>
  );
};

// ============================================================
// Phone frame (3D transform driven by the camera)
// ============================================================
export const Phone: React.FC<{ cam: Cam; shakeX: number; shakeR: number; glare: number; children: React.ReactNode }> = ({ cam, shakeX, shakeR, glare, children }) => {
  return (
    <AbsoluteFill style={{ perspective: 2600, perspectiveOrigin: `${PCX}px ${PCY}px` }}>
      <div
        style={{
          position: 'absolute', left: PCX - PW / 2, top: PCY - PH / 2, width: PW, height: PH,
          transformOrigin: '50% 50%',
          transform: `translate(${cam.tx + shakeX}px, ${cam.ty}px) scale(${cam.s}) rotateX(${cam.rx}deg) rotateY(${cam.ry}deg) rotateZ(${cam.rz + shakeR}deg)`,
        }}
      >
        {/* soft shadow + glow */}
        <div style={{ position: 'absolute', inset: 30, top: 90, borderRadius: 110, background: 'rgba(0,0,0,0.55)', filter: 'blur(60px)', transform: 'translateY(50px)' }} />
        <div style={{ position: 'absolute', inset: -40, borderRadius: 150, background: 'radial-gradient(closest-side, rgba(61,220,132,0.22), rgba(61,220,132,0))', filter: 'blur(20px)' }} />
        {/* side buttons */}
        <div style={{ position: 'absolute', left: -7, top: 300, width: 8, height: 90, borderRadius: 4, background: '#16211b' }} />
        <div style={{ position: 'absolute', left: -7, top: 420, width: 8, height: 150, borderRadius: 4, background: '#16211b' }} />
        <div style={{ position: 'absolute', right: -7, top: 380, width: 8, height: 190, borderRadius: 4, background: '#16211b' }} />
        {/* body */}
        <div style={{ position: 'absolute', inset: 0, borderRadius: 104, background: 'linear-gradient(145deg, #3c5446 0%, #0d1511 30%, #070b09 70%, #2b3d33 100%)', boxShadow: 'inset 0 0 0 2px rgba(195,245,107,0.18), inset 0 0 0 6px #050806' }} />
        {/* screen */}
        <div style={{ position: 'absolute', left: BEZEL, top: BEZEL, width: SW, height: SH, borderRadius: 88, overflow: 'hidden', background: '#f6f8f7' }}>
          {children}
          {/* glare sweep */}
          <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', background: `linear-gradient(115deg, rgba(255,255,255,0) ${glare * 140 - 40}%, rgba(255,255,255,0.28) ${glare * 140 - 25}%, rgba(255,255,255,0) ${glare * 140 - 10}%)` }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// Screen stack: real screenshots + in-screen transitions
// ============================================================
export type Tr = 'cut' | 'scroll' | 'slideLeft' | 'sheetUp' | 'zoomIn' | 'whip' | 'pushUp' | 'fade';
export type Seg = { f: number; shot: string; tr?: Tr; d?: number; delta?: number; bandTop?: number; bandBottom?: number };

const Shot: React.FC<{ name: string; style?: React.CSSProperties }> = ({ name, style }) => (
  <Img src={staticFile(`shots/${name}.png`)} style={{ position: 'absolute', left: 0, top: 0, width: SW, height: SH, ...style }} />
);

export const ScreenStack: React.FC<{ segs: Seg[] }> = ({ segs }) => {
  const f = useCurrentFrame();
  let i = 0;
  for (let k = 0; k < segs.length; k++) if (segs[k].f <= f) i = k;
  const cur = segs[i];
  const d = cur.d ?? 0;
  const p = d > 0 ? interpolate(f, [cur.f, cur.f + d], [0, 1], clamp) : 1;
  if (p >= 1 || i === 0 || !cur.tr || cur.tr === 'cut') return <Shot name={cur.shot} />;
  const prev = segs[i - 1];
  const e = easeInOut(p);
  const mid = Math.sin(Math.PI * p); // 0 → 1 → 0, for motion blur
  switch (cur.tr) {
    case 'scroll': {
      const dy = (cur.delta ?? 300) * K;
      const top = (cur.bandTop ?? 0) * K;
      const bot = (cur.bandBottom ?? 0) * K;
      const blur = `blur(${mid * 2.2}px)`;
      const clipBands = `inset(${top}px 0 ${bot}px 0)`;
      return (
        <>
          <div style={{ position: 'absolute', inset: 0, clipPath: clipBands }}>
            <Shot name={prev.shot} style={{ transform: `translateY(${-dy * e}px)`, filter: blur }} />
            <Shot name={cur.shot} style={{ transform: `translateY(${dy * (1 - e)}px)`, filter: blur, clipPath: `inset(${top}px 0 ${bot}px 0)` }} />
          </div>
          {top > 0 && <Shot name={cur.shot} style={{ clipPath: `inset(0 0 ${SH - top}px 0)` }} />}
          {bot > 0 && <Shot name={cur.shot} style={{ clipPath: `inset(${SH - bot}px 0 0 0)` }} />}
        </>
      );
    }
    case 'slideLeft':
      return (
        <>
          <Shot name={prev.shot} style={{ transform: `translateX(${-SW * 0.3 * e}px) scale(${1 - 0.05 * e})`, filter: `brightness(${1 - 0.45 * e})` }} />
          <Shot name={cur.shot} style={{ transform: `translateX(${SW * (1 - e)}px)`, boxShadow: '-30px 0 60px rgba(0,0,0,0.35)', filter: `blur(${mid * 2}px)` }} />
        </>
      );
    case 'sheetUp': {
      const e2 = easeOut(p);
      return (
        <>
          <Shot name={prev.shot} style={{ filter: `brightness(${1 - 0.5 * e2})` }} />
          <Shot name={cur.shot} style={{ transform: `translateY(${SH * 0.9 * (1 - e2)}px)`, boxShadow: '0 -30px 60px rgba(0,0,0,0.35)', borderRadius: 40 * (1 - e2) }} />
        </>
      );
    }
    case 'zoomIn':
      return (
        <>
          <Shot name={prev.shot} style={{ transform: `scale(${1 + 0.4 * e})`, opacity: 1 - e, filter: `blur(${e * 8}px)` }} />
          <Shot name={cur.shot} style={{ transform: `scale(${1.18 - 0.18 * easeOut(p)})`, opacity: Math.min(1, p * 2.2) }} />
        </>
      );
    case 'whip':
      return (
        <>
          <Shot name={prev.shot} style={{ transform: `translateX(${-SW * e}px)`, filter: `blur(${mid * 10}px)` }} />
          <Shot name={cur.shot} style={{ transform: `translateX(${SW * (1 - e)}px)`, filter: `blur(${mid * 10}px)` }} />
        </>
      );
    case 'pushUp':
      return (
        <>
          <Shot name={prev.shot} style={{ transform: `scale(${1 - 0.1 * e})`, opacity: 1 - e, filter: `blur(${e * 4}px)` }} />
          <Shot name={cur.shot} style={{ transform: `translateY(${SH * 0.22 * (1 - easeOut(p))}px) scale(${0.94 + 0.06 * easeOut(p)})`, opacity: Math.min(1, p * 1.8) }} />
        </>
      );
    case 'fade':
    default:
      return (
        <>
          <Shot name={prev.shot} />
          <Shot name={cur.shot} style={{ opacity: e }} />
        </>
      );
  }
};

const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

// ============================================================
// Finger tap (in screen space, CSS coords)
// ============================================================
export const Tap: React.FC<{ at: number; x: number; y: number }> = ({ at, x, y }) => {
  const f = useCurrentFrame();
  const t = f - at;
  if (t < -11 || t > 20) return null;
  const appear = ramp(f, at - 11, at - 2, easeOut);
  const press = t >= 0 ? interpolate(t, [0, 3, 8], [1, 0.72, 1], clamp) : 1;
  const out = ramp(f, at + 9, at + 18, easeIn);
  const sx = x * K;
  const sy = y * K;
  const ox = (1 - appear) * 70;
  const oy = (1 - appear) * 110;
  const ring = t >= 0 ? interpolate(t, [0, 16], [0, 1], clamp) : 0;
  return (
    <>
      {t >= 0 && (
        <div style={{ position: 'absolute', left: sx, top: sy, width: 0, height: 0 }}>
          <div style={{ position: 'absolute', left: -110 * ring - 30, top: -110 * ring - 30, width: 220 * ring + 60, height: 220 * ring + 60, borderRadius: '50%', border: `${6 * (1 - ring) + 1}px solid ${C.mint}`, opacity: 1 - ring }} />
          <div style={{ position: 'absolute', left: -60 * ring - 20, top: -60 * ring - 20, width: 120 * ring + 40, height: 120 * ring + 40, borderRadius: '50%', background: `rgba(61,220,132,${0.35 * (1 - ring)})` }} />
        </div>
      )}
      <div
        style={{
          position: 'absolute', left: sx - 36 + ox, top: sy - 36 + oy, width: 72, height: 72, borderRadius: '50%',
          background: 'rgba(255,255,255,0.88)', border: `5px solid ${C.mint}`,
          boxShadow: '0 12px 30px rgba(0,0,0,0.35)', transform: `scale(${press * (0.6 + 0.4 * appear)})`, opacity: appear * (1 - out),
        }}
      />
    </>
  );
};

// ============================================================
// Kinetic caption
// ============================================================
export type Word = { t: string; hl?: 'lime' | 'red' | 'mint' };
export const Caption: React.FC<{ from: number; to: number; lines: Word[][]; y: number; size: number; font: string }> = ({ from, to, lines, y, size, font }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < from - 1 || f > to + 6) return null;
  let idx = 0;
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: y, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: size * 0.02 }}>
      {lines.map((line, li) => (
        <div key={li} style={{ display: 'flex', justifyContent: 'center', gap: size * 0.22 }}>
          {line.map((w) => {
            const k = idx++;
            const sp = spring({ frame: f - from - k * 3, fps, config: { damping: 13, stiffness: 200, mass: 0.7 } });
            const out = ramp(f, to - 6 + k * 1.2, to + k * 1.2, easeIn);
            const ty = (1 - sp) * size * 1.15 - out * size * 1.15;
            const rot = (1 - sp) * 14 - out * 8;
            const pill = w.hl ? ramp(f, from + k * 3 + 5, from + k * 3 + 13, easeOut) : 0;
            const pillColor = w.hl === 'red' ? C.red : w.hl === 'mint' ? C.mint : C.lime;
            const txtColor = w.hl && w.hl !== 'red' && pill > 0.5 ? C.ink : C.white;
            return (
              <div key={k} style={{ position: 'relative', overflow: 'hidden', padding: `${size * 0.04}px ${size * 0.12}px ${size * 0.1}px` }}>
                {w.hl && (
                  <div style={{ position: 'absolute', left: size * 0.02, right: size * 0.02, top: size * 0.12, bottom: size * 0.08, borderRadius: size * 0.2, background: pillColor, transformOrigin: '0% 50%', transform: `scaleX(${pill * (1 - out)})` }} />
                )}
                <div
                  style={{
                    position: 'relative', fontFamily: font, fontWeight: 800, fontSize: size, lineHeight: 1.05, letterSpacing: '-0.035em',
                    color: txtColor, transform: `translateY(${ty}px) rotate(${rot}deg)`, transformOrigin: '0% 100%',
                    textShadow: w.hl ? 'none' : '0 10px 40px rgba(0,0,0,0.5)', whiteSpace: 'nowrap',
                  }}
                >
                  {w.t}
                </div>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
};

// ============================================================
// FX: ring burst + confetti (canvas space)
// ============================================================
export const Burst: React.FC<{ at: number; x: number; y: number; color: string }> = ({ at, x, y, color }) => {
  const f = useCurrentFrame();
  const t = f - at;
  if (t < 0 || t > 24) return null;
  return (
    <>
      {[0, 5].map((delay, i) => {
        const p = interpolate(t - delay, [0, 18], [0, 1], clamp);
        if (t < delay) return null;
        const r = 40 + easeOut(p) * (260 + i * 120);
        return <div key={i} style={{ position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', border: `${10 * (1 - p) + 1}px solid ${color}`, opacity: 1 - p }} />;
      })}
    </>
  );
};

export const Confetti: React.FC<{ at: number; x: number; y: number }> = ({ at, x, y }) => {
  const f = useCurrentFrame();
  const t = f - at;
  if (t < 0 || t > 40) return null;
  const cols = [C.lime, C.mint, '#ffffff', '#ffd166'];
  return (
    <>
      {new Array(34).fill(0).map((_, i) => {
        const a = random(`a${i}`) * Math.PI * 2;
        const v = 14 + random(`v${i}`) * 26;
        const px = x + Math.cos(a) * v * t * 0.9;
        const py = y + Math.sin(a) * v * t * 0.9 + 0.9 * t * t;
        const rot = t * (8 + random(`r${i}`) * 20);
        const o = interpolate(t, [26, 40], [1, 0], clamp);
        const w = 12 + random(`w${i}`) * 12;
        return <div key={i} style={{ position: 'absolute', left: px, top: py, width: w, height: w * 0.45, borderRadius: 3, background: cols[i % cols.length], transform: `rotate(${rot}deg)`, opacity: o }} />;
      })}
    </>
  );
};

// thin showreel progress bar at the bottom
export const ProgressBar: React.FC = () => {
  const f = useCurrentFrame();
  return <div style={{ position: 'absolute', left: 0, bottom: 0, height: 8, width: (f / (DUR - 1)) * W, background: `linear-gradient(90deg, ${C.mint}, ${C.lime})` }} />;
};
