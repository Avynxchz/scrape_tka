/** Probe: kondisi iframe Beranda sebelum/sesudah toggle panel. */
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(4000);

  const readFrame = () => page.evaluate(() => {
    const f = document.getElementById('homeDesktopFrame');
    let b = '(no access)';
    try {
      const w = f.contentWindow;
      b = {
        bridge: !!w.__homeDesktopBridge,
        list: w.__homeDesktopBridge && w.__homeDesktopBridge._list ? w.__homeDesktopBridge._list.map(x => x.subject + ':' + x.count).join(',') : null,
        kartu: w.document.body.innerText.includes('46 Soal'),
      };
    } catch (e) { b = 'ERR ' + e.message; }
    return { loaded: f.dataset.loaded || null, frame: b };
  });

  console.log('AWAL:', JSON.stringify(await readFrame()));
  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Modul' }, '*'));
  await page.waitForTimeout(1200);
  console.log('SETELAH nav Modul:', JSON.stringify(await readFrame()));
  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Beranda' }, '*'));
  await page.waitForTimeout(2500);
  console.log('SETELAH nav Beranda:', JSON.stringify(await readFrame()));
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
