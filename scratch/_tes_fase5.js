/**
 * Tes FASE 5: Navbar atas & bawah konsisten di 4 menu (mobile).
 * - Beranda, Modul, Progres, Akun: top bar dan bottom nav IDENTIK.
 * - Tombol search TIDAK ada di top bar Modul.
 * - Bottom nav di ke-4 menu tingginya seragam 56px (h-14) & safe-area aware.
 * - Navbar halaman Soal tetap terjaga (Fase 3).
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
  const p = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const consoleErrors = [];
  p.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  p.on('pageerror', err => consoleErrors.push(err.message));

  await p.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
  await p.waitForTimeout(2000);

  // 1) Pastikan homeOverlay terbuka di Beranda
  await p.evaluate(() => {
    if (typeof homeOpen === 'function') homeOpen();
    if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
  });
  await p.waitForTimeout(500);

  // Periksa Beranda
  const berandaInfo = await p.evaluate(() => {
    const top = document.querySelector('.stitch-fixed-top');
    const btm = document.querySelector('.stitch-bottomnav');
    const row = document.querySelector('.stitch-bottomnav-row');
    const avatar = top ? top.querySelector('.stitch-avatar') : null;
    const title = top ? top.querySelector('.stitch-brand-title') : null;
    return {
      topHeight: top ? top.getBoundingClientRect().height : 0,
      btmRowHeight: row ? row.getBoundingClientRect().height : 0,
      hasAvatar: !!avatar,
      title: title ? title.innerText.trim() : ''
    };
  });
  report('Beranda: Top bar punya logo/title TKA Master & avatar',
    berandaInfo.hasAvatar && berandaInfo.title === 'TKA Master',
    JSON.stringify(berandaInfo)
  );
  report('Beranda: Bottom nav height 56px',
    Math.round(berandaInfo.btmRowHeight) === 56,
    `row height: ${berandaInfo.btmRowHeight}`
  );
  await p.screenshot({ path: 'exports/f5_beranda_mobile.png' });

  // 2) Buka Modul
  await p.evaluate(() => homeShowPanel('modul'));
  await p.waitForTimeout(1000);
  const modulFrame = p.frame({ name: 'Modul Belajar TKA Master' }) || p.frame({ url: /modul/ });
  const modulInfo = await modulFrame.evaluate(() => {
    const top = document.querySelector('#modulMobile header');
    const searchInTop = top ? top.querySelector('[data-focus-search], input[type="search"]') : null;
    const avatar = top ? top.querySelector('[data-nav="akun"]') : null;
    const nav = document.querySelector('#modulMobile nav');
    const navRow = nav ? nav.querySelector('div') : null;
    return {
      hasSearchInTop: !!searchInTop,
      hasAvatar: !!avatar,
      btmRowHeight: navRow ? navRow.getBoundingClientRect().height : 0
    };
  });
  report('Modul: Top bar TIDAK ada tombol search & punya avatar',
    !modulInfo.hasSearchInTop && modulInfo.hasAvatar,
    JSON.stringify(modulInfo)
  );
  report('Modul: Bottom nav height 56px',
    Math.round(modulInfo.btmRowHeight) === 56,
    `row height: ${modulInfo.btmRowHeight}`
  );
  await p.screenshot({ path: 'exports/f5_modul_mobile.png' });

  // 3) Buka Progres
  await p.evaluate(() => homeShowPanel('progres'));
  await p.waitForTimeout(1000);
  const progresFrame = p.frame({ name: 'Progres & Analitik TKA Master' }) || p.frame({ url: /progres/ });
  const progresInfo = await progresFrame.evaluate(() => {
    const top = document.querySelector('#progresMobile header');
    const searchInTop = top ? top.querySelector('input[type="search"], [data-focus-search]') : null;
    const avatar = top ? top.querySelector('button[aria-label="Buka Akun"]') : null;
    const nav = document.querySelector('#progresMobile nav');
    const navRow = nav ? nav.querySelector('div') : null;
    return {
      hasSearchInTop: !!searchInTop,
      hasAvatar: !!avatar,
      btmRowHeight: navRow ? navRow.getBoundingClientRect().height : 0
    };
  });
  report('Progres: Top bar punya avatar & tanpa elemen asing',
    !progresInfo.hasSearchInTop && progresInfo.hasAvatar,
    JSON.stringify(progresInfo)
  );
  report('Progres: Bottom nav height 56px (tidak menjulang)',
    Math.round(progresInfo.btmRowHeight) === 56,
    `row height: ${progresInfo.btmRowHeight}`
  );
  await p.screenshot({ path: 'exports/f5_progres_mobile.png' });

  // 4) Buka Akun
  await p.evaluate(() => homeShowPanel('akun'));
  await p.waitForTimeout(1000);
  const akunFrame = p.frame({ name: 'Akun & Preferensi TKA Master' }) || p.frame({ url: /akun/ });
  const akunInfo = await akunFrame.evaluate(() => {
    const top = document.querySelector('#akunMobile header');
    const avatar = top ? top.querySelector('.material-symbols-outlined') : null;
    const nav = document.querySelector('#akunMobile nav');
    const navRow = nav ? nav.querySelector('div') : null;
    return {
      hasAvatar: !!avatar,
      btmRowHeight: navRow ? navRow.getBoundingClientRect().height : 0
    };
  });
  report('Akun: Top bar punya avatar & Bottom nav height 56px',
    akunInfo.hasAvatar && Math.round(akunInfo.btmRowHeight) === 56,
    JSON.stringify(akunInfo)
  );
  await p.screenshot({ path: 'exports/f5_akun_mobile.png' });

  // 5) Tutup overlay -> Periksa navbar halaman Soal TIDAK rusak (Fase 3)
  await p.evaluate(() => homeClose());
  await p.waitForTimeout(600);
  const soalNavInfo = await p.evaluate(() => {
    const header = document.querySelector('.app-header');
    const st = getComputedStyle(header);
    const homeBtn = document.getElementById('btnHome');
    const qnum = document.getElementById('mQNum');
    return {
      bg: st.backgroundColor,
      homeVisible: homeBtn && getComputedStyle(homeBtn).display !== 'none',
      qnumVisible: qnum && getComputedStyle(qnum).display !== 'none'
    };
  });
  report('Halaman Soal: Navbar atas tetap hijau #004a2a dan utuh (Fase 3 tidak terganggu)',
    soalNavInfo.bg === 'rgb(0, 74, 42)' && soalNavInfo.homeVisible && soalNavInfo.qnumVisible,
    JSON.stringify(soalNavInfo)
  );

  await p.close();
  await browser.close();

  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== FASE 5: ${R.length - fail}/${R.length} PASS ===`);
  console.log('Console errors:', consoleErrors.length ? consoleErrors : 'None');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL FASE 5:', e); process.exit(1); });
