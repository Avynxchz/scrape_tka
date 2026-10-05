/** Diagnostic: cari ancestor pembuat containing block untuk .qcard-actions fixed. */
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const m = await browser.newPage({ viewport: { width: 360, height: 640 } });
  await m.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await m.waitForTimeout(2500);
  await m.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await m.waitForTimeout(600);
  const out = await m.evaluate(() => {
    const bar = document.querySelector('.qcard-actions');
    const st = getComputedStyle(bar);
    const info = {
      posisi: st.position,
      bottom: st.bottom,
      rectBottom: bar.getBoundingClientRect().bottom,
      ancestors: [],
    };
    let el = bar.parentElement;
    while (el && el !== document.documentElement) {
      const cs = getComputedStyle(el);
      const suspicious = {};
      ['transform', 'filter', 'backdropFilter', 'perspective', 'willChange', 'contain', 'contentVisibility', 'containerType', 'position'].forEach(k => {
        const v = cs[k];
        if (v && v !== 'none' && v !== 'visible' && v !== 'normal' && v !== 'static' && v !== 'auto') suspicious[k] = v;
      });
      info.ancestors.push({ tag: el.tagName + '.' + String(el.className).split(' ').slice(0, 3).join('.'), ...suspicious });
      el = el.parentElement;
    }
    return info;
  });
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
