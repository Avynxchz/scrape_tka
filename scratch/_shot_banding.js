/** Screenshot perbandingan 3 halaman dengan data sample di localStorage. */
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(2500);
  await page.evaluate(() => {
    localStorage.setItem('tka_progress', JSON.stringify({
      matematika: { "1": { "1": { kunci: "A", benar: true }, "2": { kunci: "B", benar: false }, "3": { kunci: "C", benar: true } } },
      fisika: { "1": { "1": { kunci: "B", benar: true } } },
      sejarah: { "1": { "1": { kunci: "A", benar: false } } },
    }));
  });
  await page.screenshot({ path: 'exports/banding_beranda.png' });

  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'modul' }, '*'));
  await page.waitForTimeout(1500);
  await page.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 6000))]));
  await page.screenshot({ path: 'exports/banding_modul.png' });

  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'progres' }, '*'));
  await page.waitForTimeout(1800);
  await page.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 6000))]));
  await page.screenshot({ path: 'exports/banding_progres.png' });
  await browser.close();
  console.log('OK 3 screenshot');
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
