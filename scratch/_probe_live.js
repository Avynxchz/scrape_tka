/** Probe 3: alur persis _tes_desktop_live — dump kondisi bridge/iframe + error console. */
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  page.on('console', m => { if (m.type() === 'error') console.log('PAGE ERR:', m.text().slice(0, 200)); });
  page.on('pageerror', e => console.log('PAGE EXC:', String(e).slice(0, 200)));

  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(4500);

  const dump = await page.evaluate(() => {
    const f = document.getElementById('homeDesktopFrame');
    const w = f.contentWindow;
    return {
      loaded: f.dataset.loaded || null,
      readyState: w.document.readyState,
      bridge: !!w.__homeDesktopBridge,
      list: w.__homeDesktopBridge && w.__homeDesktopBridge._list ? w.__homeDesktopBridge._list.map(x => x.subject + ':' + x.count).join(',') : null,
      kartu: (w.document.body.innerText.match(/\d+ Soal/g) || []).slice(0, 6),
      soalDikerjakan: (w.document.getElementById('deskSoalDikerjakan') || {}).textContent,
    };
  });
  console.log(JSON.stringify(dump, null, 1));
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
