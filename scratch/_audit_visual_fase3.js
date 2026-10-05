const { chromium } = require('./node_modules/playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });

  // 1. Audit Desktop
  const d = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await d.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
  await d.waitForTimeout(2000);
  await d.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await d.waitForTimeout(500);

  const dHomeStyle = await d.evaluate(() => {
    const el = document.getElementById('btnHome');
    const s = getComputedStyle(el);
    return {
      display: s.display,
      width: s.width,
      height: s.height,
      bg: s.backgroundColor,
      border: s.border,
      borderRadius: s.borderRadius,
      color: s.color,
      padding: s.padding
    };
  });
  console.log('DESKTOP btnHome computed style:', JSON.stringify(dHomeStyle, null, 2));
  await d.screenshot({ path: 'exports/f3_header_desktop.png' });
  await d.close();

  // 2. Audit Mobile: 360, 390, 412
  for (const w of [360, 390, 412]) {
    const p = await browser.newPage({ viewport: { width: w, height: 800 } });
    await p.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
    await p.waitForTimeout(2000);
    await p.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
    await p.waitForTimeout(500);

    const mInfo = await p.evaluate(() => {
      const q = document.getElementById('mQNum');
      const qs = getComputedStyle(q);
      const b = q.querySelector('b');
      const sp = q.querySelector('span');
      const home = document.getElementById('btnHome');
      const hs = getComputedStyle(home);
      const timer = document.getElementById('timerPill');
      const ts = getComputedStyle(timer);
      const ovf = document.getElementById('btnMobileOverflow');
      const os = getComputedStyle(ovf);
      return {
        qnumDisplay: qs.display,
        qnumFlexDir: qs.flexDirection,
        bText: b ? b.innerText : '',
        spText: sp ? sp.innerText : '',
        homeVis: hs.display !== 'none',
        homeSize: `${hs.width}x${hs.height}`,
        timerVis: ts.display !== 'none',
        ovfVis: os.display !== 'none',
      };
    });
    console.log(`MOBILE ${w}px header info:`, JSON.stringify(mInfo, null, 2));
    await p.screenshot({ path: `exports/f3_header_mobile_${w}.png` });
    await p.close();
  }

  await browser.close();
  console.log('AUDIT SELESAI');
})();
