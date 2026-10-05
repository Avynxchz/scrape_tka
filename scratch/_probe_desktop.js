/** Probe: kenapa kartu 2-6 masih "— Soal"? Cek HOME_SOAL_COUNTS, list terakhir di bridge, dan kirim manual. */
const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  const errors = [];
  page.on('pageerror', e => errors.push('top: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 120)); });

  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(5000);

  const top = await page.evaluate(() => {
    let n = -1;
    try { n = Object.keys(HOME_SOAL_COUNTS).length; } catch (e) { n = 'err:' + e.message; }
    return {
      prefetchKeys: n,
      homeOpenVisible: !document.getElementById('homeOverlay').classList.contains('home-hidden'),
    };
  });

  const frame = page.frames().find(f => f.url().includes('home_desktop'));
  const fr = await frame.evaluate(() => {
    const B = window.__homeDesktopBridge;
    return {
      bridgeAda: !!B,
      listTerakhir: B && B._list ? B._list.map(d => d.subject + ':' + d.count).join(',') : '(null)',
    };
  });

  // kirim manual data lengkap -> kartu harus terisi semua
  await page.evaluate(() => {
    const f = document.getElementById('homeDesktopFrame');
    f.contentWindow.postMessage({
      type: 'home-desktop-data',
      subjects: [
        { subject: 'matematika', pkg: 1, label: 'Matematika (Wajib)', count: 46, minutes: 45, progress: 0 },
        { subject: 'matematika', pkg: 2, label: 'Matematika (Wajib)', count: 25, minutes: 50, progress: 0 },
        { subject: 'fisika', pkg: 1, label: 'Fisika (Peminatan)', count: 20, minutes: 45, progress: 0 },
        { subject: 'fisika', pkg: 2, label: 'Fisika (Peminatan)', count: 24, minutes: 50, progress: 0 },
        { subject: 'ekonomi', pkg: 1, label: 'Ekonomi', count: 20, minutes: 45, progress: 0 },
        { subject: 'ekonomi', pkg: 2, label: 'Ekonomi', count: 29, minutes: 50, progress: 0 },
      ],
      progress: { dikerjakan: 0, benar: 0, tepat: 0 },
    }, '*');
  });
  await page.waitForTimeout(600);
  const after = await frame.evaluate(() =>
    [...document.querySelectorAll('main section .grid > div.relative')].map(c =>
      [...c.querySelectorAll('span')].map(s => s.textContent.trim()).find(t => /Soal/.test(t))
    ).join(' | ')
  );

  console.log('TOP:', JSON.stringify(top));
  console.log('IFRAME:', JSON.stringify(fr));
  console.log('Setelah kirim manual:', after);
  console.log('JS errors:', errors.length ? errors.slice(0, 6).join(' ; ') : '(tidak ada)');
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
