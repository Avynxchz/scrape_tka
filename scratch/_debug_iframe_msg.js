/** Debug: lacak postMessage antara iframe desktop dan parent saat card diklik. */
const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });

  page.on('console', m => { if (m.type() === 'error' || m.text().includes('home')) console.log('[console]', m.text().slice(0, 160)); });
  page.on('pageerror', e => console.log('[pageerror]', String(e).slice(0, 200)));

  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(3500);

  // pasang logger di parent
  await page.evaluate(() => {
    window.__msgs = [];
    window.addEventListener('message', (e) => {
      if (e.data && e.data.type) window.__msgs.push(e.data.type + ':' + (e.data.subject || '') + ':' + (e.data.pkg ?? ''));
    });
  });

  const frame = page.frames().find(f => f.url().includes('home_desktop'));
  console.log('iframe ditemukan:', !!frame);

  await frame.evaluate(() => document.querySelector('main section .grid > div.relative').click());
  await page.waitForTimeout(1500);

  const msgs = await page.evaluate(() => window.__msgs);
  console.log('pesan masuk parent:', msgs);

  const state = await page.evaluate(() => ({
    homeHidden: document.getElementById('homeOverlay').classList.contains('home-hidden'),
    bodyOverflow: document.body.style.overflow,
    soal: document.getElementById('qLabelHeader')?.textContent,
  }));
  console.log('state:', state);

  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
