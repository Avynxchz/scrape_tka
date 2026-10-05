const { chromium } = require('./node_modules/playwright-core');
const BASE = 'http://127.0.0.1:8080';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const p = await browser.newPage({ viewport: { width: 390, height: 844 } });
  
  const startTime = Date.now();
  await p.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded', timeout: 10000 });
  const dclTime = Date.now() - startTime;
  
  // Ukur waktu eksekusi renderHome() dan waktu kartu selesai tampil
  const timing = await p.evaluate(async () => {
    const t0 = performance.now();
    const countBefore = document.querySelectorAll('.stitch-card').length;
    // Ukur pemanggilan renderHome
    if (typeof renderHome === 'function') renderHome();
    const t1 = performance.now();
    const countAfter = document.querySelectorAll('.stitch-card').length;
    return {
      renderDurationMs: t1 - t0,
      cardsCount: countAfter,
      hasPrefetching: typeof _homePrefetching !== 'undefined'
    };
  });
  
  console.log('DOM Content Loaded:', dclTime + 'ms');
  console.log('Timing baseline:', JSON.stringify(timing));
  await browser.close();
})();
