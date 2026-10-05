/**
 * Konversi frame sequence -> WebM (VP9) memakai Chromium + MediaRecorder.
 * Timing per frame diambil dari manifest.json (hasil CDP screencast).
 *
 * Pakai: node _frames_to_video.js <dir_demo_scene> [outFile.webm]
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const dir = process.argv[2];
const OUTFILE = process.argv[3] || path.join(dir, '..', `demo_${path.basename(dir)}.webm`);
if (!dir || !fs.existsSync(path.join(dir, 'manifest.json'))) {
  console.error('Pemakaian: node _frames_to_video.js <dir_demo_scene> [out.webm]'); process.exit(1);
}
const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'manifest.json'), 'utf8'));
const frames = manifest.frames;
if (frames.length < 5) { console.error('frame terlalu sedikit'); process.exit(1); }
const durasi = frames[frames.length - 1].t;
console.log(`frames: ${frames.length} | durasi: ${durasi.toFixed(1)}s | output: ${path.basename(OUTFILE)}`);

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 720, height: 720 } });

  await page.setContent('<canvas id="c" width="1080" height="1920"></canvas>');

  // injek gambar satu per satu (hindari limit argumen)
  const n = await page.evaluate(async (count) => {
    window.__imgs = [];
    return count;
  }, frames.length);

  for (let i = 0; i < frames.length; i++) {
    const b64 = fs.readFileSync(path.join(dir, frames[i].file)).toString('base64');
    const ok = await page.evaluate((d) => new Promise((res) => {
      const img = new Image();
      img.onload = () => { window.__imgs.push(img); res(true); };
      img.onerror = () => res(false);
      img.src = 'data:image/jpeg;base64,' + d;
    }), b64);
    if (!ok) { console.error(`frame ${i} gagal dimuat`); process.exit(1); }
  }

  // jalankan encoder: gambar frame sesuai timing -> MediaRecorder
  const b64out = await Promise.race([
    page.evaluate(({ times, dur }) => new Promise(async (resolve) => {
    const canvas = document.getElementById('c');
    const ctx = canvas.getContext('2d');
    const stream = canvas.captureStream(0);
    const track = stream.getVideoTracks()[0];
    const mime = ['video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm']
      .find(m => MediaRecorder.isTypeSupported(m));
    const rec = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 8_000_000 });
    const chunks = [];
    rec.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
    rec.onerror = () => resolve(null);

    const imgs = window.__imgs;
    let idx = 0;
    const t0 = performance.now();
    function pump() {
      const now = (performance.now() - t0) / 1000;
      while (idx < times.length - 1 && times[idx + 1] <= now) idx++;
      ctx.drawImage(imgs[idx], 0, 0, 1080, 1920);
      if (track.requestFrame) track.requestFrame();
      if (now < dur + 0.5) requestAnimationFrame(pump);
      else {
        setTimeout(() => {
          rec.stop();
          setTimeout(() => {
            if (!chunks.length) { resolve(null); return; }
            const blob = new Blob(chunks, { type: 'video/webm' });
            const fr = new FileReader();
            fr.onload = () => resolve(fr.result.split(',')[1]);
            fr.onerror = () => resolve(null);
            fr.readAsDataURL(blob);
          }, 500);
        }, 200);
      }
    }
    rec.start();
    requestAnimationFrame(pump);
  }), { times: frames.map(f => f.t), dur: durasi }),
    new Promise(res => setTimeout(() => res(null), (durasi + 15) * 1000)),
  ]);

  if (!b64out) { console.error('recorder tidak menghasilkan data'); await browser.close(); process.exit(1); }
  fs.writeFileSync(OUTFILE, Buffer.from(b64out, 'base64'));
  const kb = (fs.statSync(OUTFILE).size / 1024).toFixed(0);
  console.log(`OK: ${OUTFILE} (${kb} KB)`);
  await browser.close();
  process.exit(0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
