/** Tes desktop: buka /app di 1280px -> iframe home_desktop tampil dengan data real. */
const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  const R = [];

  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(4000);

  const homeVisible = await page.evaluate(() => {
    const ov = document.getElementById('homeOverlay');
    return !!ov && !ov.classList.contains('home-hidden');
  });
  R.push(['Home overlay tampil (desktop)', homeVisible]);

  const frameInfo = await page.evaluate(() => {
    const f = document.getElementById('homeDesktopFrame');
    if (!f) return { ada: false };
    const style = getComputedStyle(f);
    return { ada: true, display: style.display, src: f.src };
  });
  R.push(['Iframe desktop ada & tampil', frameInfo.ada && frameInfo.display !== 'none', JSON.stringify(frameInfo)]);

  // cek angka DI DALAM iframe
  const frame = page.frames().find(f => f.url().includes('home_desktop'));
  if (frame) {
    const soal = await frame.evaluate(() => {
      const cards = document.querySelectorAll('main section .grid > div.relative');
      return [...cards].map(c => ({
        subject: c.dataset.subject, pkg: c.dataset.pkg,
        soal: [...c.querySelectorAll('span')].map(s => s.textContent.trim()).find(t => /Soal/.test(t)),
      }));
    });
    R.push(['Card desktop terisi data', soal.length >= 6, JSON.stringify(soal.slice(0, 3))]);
  } else {
    R.push(['Iframe ditemukan di frames', false]);
  }

  // klik card dalam iframe -> overlay harus tutup & soal tampil
  if (frame) {
    await frame.evaluate(() => document.querySelector('main section .grid > div.relative').click());
    await page.waitForTimeout(3000);
    const after = await page.evaluate(() => ({
      homeHidden: document.getElementById('homeOverlay').classList.contains('home-hidden'),
      soal: document.getElementById('qLabelHeader')?.textContent || '(?)',
    }));
    R.push(['Klik card -> masuk soal', after.homeHidden && after.soal !== '(?)', after.soal]);
  }

  for (const [k, v, extra] of R) console.log(`${v ? 'PASS' : 'FAIL'} | ${k}${extra ? ' -> ' + extra : ''}`);
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
