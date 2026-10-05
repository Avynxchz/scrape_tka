/**
 * Re-capture of the Progress analytics panel only (the first pass shot it before the
 * Material Symbols icon font had loaded inside the panel iframe).
 * Seeds the same demo data as capture.js PLUS the geografi paket 1 result (8 benar / 2 salah)
 * that the main flow produced, so the numbers are consistent with the story.
 *
 * Run: node promo/capture/capture_progres.js
 */
const path = require('path');
const fs = require('fs');
const { chromium } = require(path.resolve(__dirname, '..', '..', 'scratch', 'node_modules', 'playwright'));

const BASE = 'http://127.0.0.1:8080';
const OUT = path.resolve(__dirname, '..', 'public', 'shots');

const mk = (n, benarN, kunci = 'A') => {
  const o = {};
  for (let i = 1; i <= n; i++) o[i] = { kunci, benar: i <= benarN };
  return o;
};
const geo = {};
for (let i = 1; i <= 10; i++) geo[i] = { kunci: 'A', benar: ![2, 6].includes(i) };
const SEED = {
  tka_user_subjects: JSON.stringify(['geografi', 'matematika', 'bahasa_inggris', 'fisika']),
  tka_progress: JSON.stringify({
    matematika: { 1: mk(30, 24), 2: mk(10, 7) },
    bahasa_inggris: { 1: mk(16, 13) },
    bahasa_indonesia: { 1: mk(12, 10) },
    fisika: { 1: mk(12, 8) },
    geografi: { 1: geo },
  }),
  tka_study_streak: '12',
};

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  });
  await ctx.route('**/api/tutor/**', r => r.fulfill({ json: { status: 'success', messages: [], quota: { remaining: 4, daily_limit: 5 } } }));
  const page = await ctx.newPage();
  await page.goto(`${BASE}/app?subject=geografi&paket=1`, { waitUntil: 'domcontentloaded' });
  await page.evaluate(seed => { localStorage.clear(); for (const [k, v] of Object.entries(seed)) localStorage.setItem(k, v); }, SEED);
  await page.goto(`${BASE}/app?subject=geografi&paket=1`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(1500);

  await page.evaluate(() => homeShowPanel('progres'));
  const frame = await (async () => {
    for (let i = 0; i < 40; i++) {
      const f = page.frame({ url: /progres\.html/ });
      if (f) return f;
      await page.waitForTimeout(250);
    }
    return null;
  })();
  if (!frame) throw new Error('progres iframe not found');
  await frame.waitForLoadState('networkidle').catch(() => {});
  const fontOk = await frame.evaluate(async () => {
    try {
      await document.fonts.load('24px "Material Symbols Outlined"', 'home');
      await document.fonts.load('800 24px "Plus Jakarta Sans"');
      await document.fonts.ready;
    } catch (e) {}
    return document.fonts.check('24px "Material Symbols Outlined"', 'home');
  });
  console.log('icon font loaded:', fontOk);
  await page.evaluate(() => homeShowPanel('progres')); // re-send data after load
  await page.waitForTimeout(1500);

  const navBox = await page.evaluate(() => {
    const a = document.querySelector('.stitch-bottomnav a[data-nav="progres"]');
    if (!a) return null;
    const b = a.getBoundingClientRect();
    return b.width ? { x: b.x, y: b.y, w: b.width, h: b.height, cx: b.x + b.width / 2, cy: b.y + b.height / 2 } : null;
  });
  await page.screenshot({ path: path.join(OUT, 'progres_top.png') });
  console.log('OK progres_top', JSON.stringify(navBox));
  await frame.evaluate(() => (document.scrollingElement || document.body).scrollTo(0, 560));
  await page.waitForTimeout(700);
  await page.screenshot({ path: path.join(OUT, 'progres_mid.png') });
  console.log('OK progres_mid');

  const mPath = path.join(OUT, 'manifest.json');
  const m = JSON.parse(fs.readFileSync(mPath, 'utf8'));
  m.shots.progres_top = { tap: navBox || (m.shots.progres_top || {}).tap || null };
  m.shots.progres_mid = {};
  fs.writeFileSync(mPath, JSON.stringify(m, null, 1));
  await browser.close();
})().catch(e => { console.error('FAILED:', e); process.exit(1); });
