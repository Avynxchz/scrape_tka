/**
 * Perekam demo TKA Master — Playwright + CDP screencast.
 * Output: exports/demo_scene<N>/frame_*.jpg + manifest.json (timestamp per frame).
 * Konversi ke video dilakukan langkah terpisah (frame -> webm/mp4).
 *
 * Pakai: node _record_demo.js <scene 1|2|3> <durasi_detik>
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SCENE = parseInt(process.argv[2] || '1', 10);
const DURATION = parseInt(process.argv[3] || '20', 10);
const OUT = path.join(__dirname, '..', 'exports', `demo_scene${SCENE}`);

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  // bersihkan frame lama
  for (const f of fs.readdirSync(OUT)) if (f.endsWith('.jpg')) fs.unlinkSync(path.join(OUT, f));

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });

  const cdp = await page.context().newCDPSession(page);
  const frames = [];
  let receiving = false;

  cdp.on('Page.screencastFrame', async (ev) => {
    const { data, metadata, sessionId } = ev;
    const ts = metadata.timestamp; // detik sejak epoch
    frames.push({ ts, data });
    receiving = true;
    try { await cdp.send('Page.screencastFrameAck', { sessionId }); } catch (e) {}
  });

  await cdp.send('Page.startScreencast', {
    format: 'jpeg', quality: 80,
    maxWidth: 1080, maxHeight: 1920, everyNthFrame: 1,
  });

  await page.goto(`file:///${__dirname.replace(/\\/g, '/')}/demo_studio.html?scene=${SCENE}&auto=1${process.argv[4] === 'reduced' ? '&reduced=1' : ''}`);
  await page.waitForFunction('window.__demoReady === true');

  // tunggu durasi penuh sambil frame mengalir
  await page.waitForTimeout(DURATION * 1000);

  await cdp.send('Page.stopScreencast');
  await browser.close();

  // normalisasi timestamp relatif
  const t0 = frames.length ? frames[0].ts : 0;
  let i = 0;
  const manifest = [];
  for (const f of frames) {
    const name = `frame_${String(i).padStart(5, '0')}.jpg`;
    fs.writeFileSync(path.join(OUT, name), Buffer.from(f.data, 'base64'));
    manifest.push({ file: name, t: +(f.ts - t0).toFixed(3) });
    i++;
  }
  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify({ scene: SCENE, fps: 'variable', frames: manifest }, null, 1));
  console.log(`scene ${SCENE}: ${frames.length} frame disimpan di ${OUT}`);
  console.log(`durasi efektif: ${(frames.length ? frames[frames.length - 1].ts - t0 : 0).toFixed(1)}s`);
  if (frames.length < 10) { console.log('PERINGATAN: frame terlalu sedikit — screencast mungkin tidak jalan.'); process.exit(2); }
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
