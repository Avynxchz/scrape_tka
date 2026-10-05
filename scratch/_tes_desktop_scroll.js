/** Tes scroll & layout desktop setelah fix: iframe harus bisa discroll penuh. */
const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });

  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(4000);

  const frame = page.frames().find(f => f.url().includes('home_desktop'));
  const info = await frame.evaluate(() => {
    const html = document.documentElement;
    const hero = document.querySelector('main section');
    hero.scrollIntoView();
    window.scrollTo(0, 1200);
    return {
      htmlStyle: html.getAttribute('style'),
      scrollHeight: html.scrollHeight,
      scrolledTo: window.scrollY,
      bodyOverflowX: getComputedStyle(document.body).overflowX,
    };
  });
  console.log('html style:', info.htmlStyle || '(tidak ada — bagus)');
  console.log('scrollHeight:', info.scrollHeight, '| scrollY setelah scrollTo(1200):', info.scrolledTo);
  console.log(info.scrolledTo > 0 ? 'PASS | iframe bisa discroll' : 'FAIL | masih terkunci');
  console.log(info.htmlStyle ? 'FAIL | inline style masih ada' : 'PASS | inline style 1280px sudah dihapus');

  await page.waitForTimeout(600);
  await page.screenshot({ path: '../exports/home_desktop_fixed.png' });
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
