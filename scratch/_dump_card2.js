/** Dump HTML kartu P2 pertama untuk cek struktur progres. */
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(4500);
  const frame = page.frames().find(f => f.url().includes('home_desktop'));
  const html = await frame.evaluate(() => {
    const c = document.querySelectorAll('main section .grid > div.relative')[1];
    return c.outerHTML.replace(/\s+/g, ' ').slice(0, 2000);
  });
  console.log(html);
  await browser.close();
})();
