import { Easing, interpolate } from 'remotion';
import manifestJson from '../public/shots/manifest.json';

export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const DUR = 450; // 15s

// Real captures are 390x844 CSS px @3x (1170x2532)
export const VW = 390;
export const VH = 844;
export const SW = 700;
export const SH = Math.round((SW * 2532) / 1170); // 1515
export const K = SW / VW; // CSS px -> screen px
export const BEZEL = 16;
export const PW = SW + BEZEL * 2;
export const PH = SH + BEZEL * 2;
export const PCX = W / 2;
export const PCY = 1096;

export const C = {
  bg0: '#021009',
  bg1: '#06321d',
  bg2: '#0b4d2e',
  green: '#1f7a4d',
  mint: '#3ddc84',
  lime: '#c3f56b',
  red: '#ff4d5e',
  white: '#f2fff7',
  ink: '#04140b',
};

export const ease = Easing.bezier(0.65, 0, 0.35, 1);
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeIn = Easing.bezier(0.7, 0, 0.84, 0);
export const backOut = Easing.bezier(0.34, 1.56, 0.64, 1);

export const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export const ramp = (f: number, a: number, b: number, e: (t: number) => number = ease) =>
  e(interpolate(f, [a, b], [0, 1], clamp));

type Box = { x: number; y: number; w: number; h: number; cx: number; cy: number } | null;
type Manifest = { shots: Record<string, Record<string, unknown>>; result?: { p: string; b: string; s: string } };
export const manifest = manifestJson as unknown as Manifest;

export const mbox = (shot: string, key: string, fallback: { cx: number; cy: number; w?: number; h?: number; x?: number; y?: number }) => {
  const b = (manifest.shots[shot] || {})[key] as Box | undefined;
  if (b && typeof b === 'object' && 'cx' in b) return b as NonNullable<Box>;
  return { x: fallback.x ?? fallback.cx - 20, y: fallback.y ?? fallback.cy - 20, w: fallback.w ?? 40, h: fallback.h ?? 40, cx: fallback.cx, cy: fallback.cy };
};
export const mnum = (shot: string, key: string, fallback: number) => {
  const v = (manifest.shots[shot] || {})[key];
  return typeof v === 'number' ? v : fallback;
};

// ---------------- camera ----------------
export type CamKey = {
  f: number;
  s: number; // zoom
  fx?: number; // focus point in CSS px (390x844 space)
  fy?: number;
  ty?: number; // canvas y the focus point should land on
  ry?: number; // rotateY deg
  rx?: number; // rotateX deg
  rz?: number; // rotateZ deg
  oy?: number; // extra canvas y offset (e.g. slide-in)
  e?: (t: number) => number;
};
export type Cam = { s: number; tx: number; ty: number; ry: number; rx: number; rz: number };

const resolveKey = (k: CamKey): Cam => {
  const fx = k.fx ?? VW / 2;
  const fy = k.fy ?? VH / 2;
  const dx = (fx - VW / 2) * K;
  const dy = (fy - VH / 2) * K;
  const targetY = k.ty ?? PCY;
  const tx = PCX - (PCX + k.s * dx);
  const ty = targetY - (PCY + k.s * dy) + (k.oy ?? 0);
  return { s: k.s, tx, ty, ry: k.ry ?? 0, rx: k.rx ?? 0, rz: k.rz ?? 0 };
};

export const camAt = (keys: CamKey[], f: number): Cam => {
  if (f <= keys[0].f) return resolveKey(keys[0]);
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i];
    const b = keys[i + 1];
    if (f >= a.f && f < b.f) {
      const t = (b.e ?? ease)((f - a.f) / (b.f - a.f));
      const A = resolveKey(a);
      const B = resolveKey(b);
      return {
        s: lerp(A.s, B.s, t),
        tx: lerp(A.tx, B.tx, t),
        ty: lerp(A.ty, B.ty, t),
        ry: lerp(A.ry, B.ry, t),
        rx: lerp(A.rx, B.rx, t),
        rz: lerp(A.rz, B.rz, t),
      };
    }
  }
  return resolveKey(keys[keys.length - 1]);
};

// CSS point inside the phone screen -> canvas coords (ignores small rotations)
export const toCanvas = (cam: Cam, fx: number, fy: number) => ({
  x: PCX + cam.s * (fx - VW / 2) * K + cam.tx,
  y: PCY + cam.s * (fy - VH / 2) * K + cam.ty,
});
