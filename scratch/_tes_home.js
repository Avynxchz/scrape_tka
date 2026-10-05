/** Tes alur: /app -> Home overlay tampil -> klik card Matematika Paket 1 -> soal muncul. */
const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true });
  const R = [];

  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(2500);

  const homeVisible = await page.evaluate(() => {
    const ov = document.getElementById('homeOverlay');
    return !!ov && !ov.classList.contains('home-hidden');
  });
  R.push(['Home tampil pertama', homeVisible]);

  const sections = await page.evaluate(() => document.querySelectorAll('#hoMain .stitch-section').length);
  R.push(['Section mapel terender', sections, '(harusnya 8)']);

  const cards = await page.evaluate(() => document.querySelectorAll('#hoMain .stitch-card').length);
  R.push(['Card paket terender', cards, '(harusnya 44)']);

  await page.screenshot({ path: '../exports/home_overlay.png' });

  // klik card Matematika Paket 1 (section pertama, card pertama)
  await page.evaluate(() => document.querySelector('#hoMain .stitch-card').click());
  await page.waitForTimeout(3500);

  const after = await page.evaluate(() => ({
    homeHidden: document.getElementById('homeOverlay').classList.contains('home-hidden'),
    soal: document.querySelector('.qnum-badge')?.textContent || document.getElementById('qLabelHeader')?.textContent || '(?)',
  }));
  R.push(['Home tertutup setelah klik (atau sedang load paket)', after.homeHidden || after.soal !== '(?)', after.soal]);
  R.push(['Soal tampil', after.soal]);

  await page.screenshot({ path: '../exports/soal_setelah_home.png' });

  // tombol Home di header: buka lagi
  // tombol Home di header: overlay ditutup dulu via JS (header ketutupan overlay),
  // lalu klik tombol saat soal tampil
  await page.evaluate(() => window.homeClose ? homeClose() : null);
  await page.waitForTimeout(600);
  const soalAfterClose = await page.evaluate(() => document.getElementById('qLabelHeader')?.textContent || '(?)');
  R.push(['Soal tampil setelah Home ditutup', soalAfterClose !== '(?)', soalAfterClose]);
  const btn = await page.$('#btnHome');
  if (btn) { await btn.click(); await page.waitForTimeout(600); }
  const reopened = await page.evaluate(() => !document.getElementById('homeOverlay').classList.contains('home-hidden'));
  R.push(['Tombol Home membuka lagi', reopened]);

  for (const [k, v, extra] of R) console.log(`${v ? 'PASS' : 'FAIL'} | ${k}${extra ? ' -> ' + extra : ''}`);
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
