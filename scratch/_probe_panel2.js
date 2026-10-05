/** Probe 2: replikasi alur persis _tes_panel untuk cari kenapa kartu beranda kosong. */
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  page.on('console', m => { if (m.type() === 'error') console.log('PAGE ERR:', m.text().slice(0, 150)); });
  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(4000);

  const dump = (label) => page.evaluate((label) => {
    const f = document.getElementById('homeDesktopFrame');
    let b;
    try {
      const w = f.contentWindow;
      b = {
        bridge: !!w.__homeDesktopBridge,
        list: w.__homeDesktopBridge && w.__homeDesktopBridge._list ? w.__homeDesktopBridge._list.map(x => x.subject + ':' + x.count).join(',') : null,
        kartu46: w.document.body.innerText.includes('46 Soal'),
        soalDikerjakan: (w.document.getElementById('deskSoalDikerjakan') || {}).textContent,
      };
    } catch (e) { b = 'ERR ' + e.message; }
    return label + ' => ' + JSON.stringify({ loaded: f.dataset.loaded || null, ...b });
  }, label);

  // replikasi alur tes
  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Modul' }, '*'));
  await page.waitForTimeout(1200);
  console.log(await dump('setelah nav Modul'));

  const modulFrame = page.frames().find(f => f.url().includes('workspace_modul'));
  await modulFrame.evaluate(() => {
    const btn = document.querySelector('[data-open][data-subject="fisika"][data-pkg="1"]');
    btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  });
  await page.waitForTimeout(3500);
  console.log(await dump('setelah klik fisika (overlay closed)'));

  await page.evaluate(() => document.getElementById('btnHome').click());
  await page.waitForTimeout(1200);
  console.log(await dump('setelah homeOpen lagi'));

  await page.evaluate(() => {
    localStorage.setItem('tka_progress', JSON.stringify({ matematika: { "1": { "2": { kunci: "B", benar: false }, "3": { kunci: "C", benar: true } } } }));
    window.postMessage({ type: 'nav', path: 'Progres' }, '*');
  });
  await page.waitForTimeout(1500);
  console.log(await dump('setelah nav Progres'));

  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Beranda' }, '*'));
  await page.waitForTimeout(2500);
  console.log(await dump('setelah nav Beranda'));

  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
