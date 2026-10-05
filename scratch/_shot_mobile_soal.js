const { chromium } = require('./node_modules/playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const viewports = [360, 390, 412];

  for (const w of viewports) {
    const page = await browser.newPage({ viewport: { width: w, height: 800 } });
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', err => errors.push(err.message));

    await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(2000);
    // Tutup overlay beranda
    await page.evaluate(() => {
      if (typeof homeClose === 'function') homeClose();
      const ov = document.getElementById('homeOverlay');
      if (ov) {
        ov.classList.add('home-hidden');
        ov.style.display = 'none';
      }
    });
    await page.waitForTimeout(600);

    await page.screenshot({ path: `exports/f3_mobile_soal_${w}.png` });
    console.log(`Mobile ${w}px captured. Console errors:`, errors.length ? errors : 'None');
    await page.close();
  }

  await browser.close();
  console.log('Mobile screenshots selesai!');
})();
