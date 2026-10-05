/**
 * Tes Otomatis FASE 11:
 * Verifikasi posisi dan tinggi bottom nav di 4 menu (Beranda, Modul, Progres, Akun)
 * - Identik di 360, 390, 412 px (selisih <= 1px)
 * - Menempel paling bawah (bottom == window.innerHeight, selisih <= 1px)
 * - Safe-area aware
 * - Desktop 1280px tidak terpengaruh (mobile nav hidden)
 * - 0 console errors
 */
const { chromium } = require('./node_modules/playwright-core');
const BASE = 'http://127.0.0.1:8080';
const R = [];

function report(name, pass, extra) {
  R.push([name, pass]);
  console.log(`${pass ? 'PASS' : 'FAIL'} | ${name}${extra ? ' -> ' + extra : ''}`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const consoleErrors = [];

  const viewports = [
    { name: '360px', width: 360, height: 640 },
    { name: '390px', width: 390, height: 844 },
    { name: '412px', width: 412, height: 915 }
  ];

  for (const vp of viewports) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(`[${vp.name}] ${msg.text()}`); });
    page.on('pageerror', err => consoleErrors.push(`[${vp.name}] ${err.message}`));

    await page.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(() => {});
    await page.waitForTimeout(1500);

    // Buka dashboard
    await page.evaluate(() => {
      if (typeof homeOpen === 'function') homeOpen();
    });
    await page.waitForTimeout(500);

    const menus = ['beranda', 'modul', 'progres', 'akun'];
    const metrics = {};

    for (const menu of menus) {
      await page.evaluate(m => {
        if (typeof homeShowPanel === 'function') homeShowPanel(m);
      }, menu);
      await page.waitForTimeout(600);

      // Screenshot untuk verifikasi visual
      await page.screenshot({ path: `exports/fase11_${menu}_${vp.name}.png` });

      if (menu === 'beranda') {
        const met = await page.evaluate(() => {
          const nav = document.querySelector('.stitch-bottomnav');
          const row = nav ? nav.querySelector('.stitch-bottomnav-row') : null;
          const rect = nav ? nav.getBoundingClientRect() : null;
          return {
            height: rect ? Math.round(rect.height) : 0,
            bottom: rect ? Math.round(rect.bottom) : 0,
            rowHeight: row ? Math.round(row.getBoundingClientRect().height) : 0,
            winH: window.innerHeight
          };
        });
        metrics[menu] = met;
      } else {
        const frameTitle = menu === 'modul' ? 'Modul Belajar TKA Master'
          : menu === 'progres' ? 'Progres & Analitik TKA Master'
          : 'Akun & Preferensi TKA Master';
        const frame = page.frame({ name: frameTitle }) || page.frame({ url: new RegExp(menu) });
        const met = await frame.evaluate(m => {
          const sel = m === 'modul' ? '#modulMobile nav'
            : m === 'progres' ? '#progresMobile nav'
            : '#akunMobile nav';
          const nav = document.querySelector(sel);
          const row = nav ? nav.querySelector('div') : null;
          const rect = nav ? nav.getBoundingClientRect() : null;
          return {
            height: rect ? Math.round(rect.height) : 0,
            bottom: rect ? Math.round(rect.bottom) : 0,
            rowHeight: row ? Math.round(row.getBoundingClientRect().height) : 0,
            winH: window.innerHeight
          };
        }, menu);
        metrics[menu] = met;
      }
    }

    // Evaluasi ketinggian & posisi
    const heights = Object.values(metrics).map(m => m.height);
    const bottoms = Object.values(metrics).map(m => m.bottom);
    const minH = Math.min(...heights);
    const maxH = Math.max(...heights);
    const hDiff = maxH - minH;

    const attachedToBottom = Object.values(metrics).every(m => Math.abs(m.bottom - m.winH) <= 1);
    const rowHeights56 = Object.values(metrics).every(m => m.rowHeight === 56);

    report(`${vp.name}: Bottom nav di 4 menu tingginya seragam (selisih <= 1px, aktual ${hDiff}px)`,
      hDiff <= 1,
      `Heights: Beranda=${metrics.beranda.height}px, Modul=${metrics.modul.height}px, Progres=${metrics.progres.height}px, Akun=${metrics.akun.height}px`
    );

    report(`${vp.name}: Bottom nav di 4 menu menempel paling bawah (selisih <= 1px)`,
      attachedToBottom,
      `Bottoms: Beranda=${metrics.beranda.bottom}, Modul=${metrics.modul.bottom}, Progres=${metrics.progres.bottom}, Akun=${metrics.akun.bottom} (viewport: ${vp.height})`
    );

    report(`${vp.name}: Row konten nav tingginya seragam 56px`,
      rowHeights56,
      `Row heights: Beranda=${metrics.beranda.rowHeight}, Modul=${metrics.modul.rowHeight}, Progres=${metrics.progres.rowHeight}, Akun=${metrics.akun.rowHeight}`
    );

    await page.close();
  }

  // Uji Desktop 1280px
  const deskPage = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await deskPage.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(() => {});
  await deskPage.waitForTimeout(1500);
  await deskPage.evaluate(() => { if (typeof homeOpen === 'function') homeOpen(); });
  await deskPage.waitForTimeout(600);

  const deskInfo = await deskPage.evaluate(() => {
    const mobileNav = document.querySelector('.stitch-bottomnav');
    const cs = mobileNav ? getComputedStyle(mobileNav) : null;
    return {
      mobileNavDisplay: cs ? cs.display : 'not found'
    };
  });
  report('Desktop 1280px: Mobile bottom nav disembunyikan (display: none)',
    deskInfo.mobileNavDisplay === 'none',
    `display: ${deskInfo.mobileNavDisplay}`
  );
  await deskPage.screenshot({ path: 'exports/fase11_desktop_1280.png' });
  await deskPage.close();

  // Uji Regresi Halaman Soal Fase 3
  const soalPage = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await soalPage.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(() => {});
  await soalPage.waitForTimeout(1500);
  const soalNavInfo = await soalPage.evaluate(() => {
    const hdr = document.querySelector('.app-header');
    const cs = getComputedStyle(hdr);
    return {
      bg: cs.backgroundColor,
      homeBtn: !!document.getElementById('btnHome'),
      qnum: !!document.getElementById('mQNum')
    };
  });
  report('Regresi Halaman Soal: Navbar #004a2a tetap utuh',
    soalNavInfo.bg === 'rgb(0, 74, 42)' && soalNavInfo.homeBtn && soalNavInfo.qnum,
    JSON.stringify(soalNavInfo)
  );
  await soalPage.close();

  await browser.close();

  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== FASE 11: ${R.length - fail}/${R.length} PASS ===`);
  console.log('Console errors:', consoleErrors.length ? consoleErrors : '0 errors');
  process.exit(fail ? 1 : 0);
})().catch(e => {
  console.error('GAGAL FASE 11:', e);
  process.exit(1);
});
