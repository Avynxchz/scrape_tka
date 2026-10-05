/**
 * Tes panel Akun: desktop 1280 & mobile 390.
 * - nav Akun -> panel tampil (iframe akun)
 * - statistik real dari tka_progress (sample), reset riwayat berfungsi (confirm di-accept)
 * - item Akun tampil lagi di bottom nav mobile; bottomnav Beranda hilang saat panel akun aktif
 * Jalankan dari root: node scratch/_tes_akun.js (server 8080 harus jalan)
 */
const { chromium } = require('playwright-core');

const BASE = 'http://127.0.0.1:8080';
const R = [];
function report(name, pass, extra) {
  R.push([name, pass]);
  console.log(`${pass ? 'PASS' : 'FAIL'} | ${name}${extra ? ' -> ' + extra : ''}`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  /* ================= DESKTOP 1280 ================= */
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.evaluate(() => localStorage.removeItem('tka_progress'));
  await page.reload();
  await page.waitForTimeout(2500);

  // 1) nav 'Akun' dari postMessage -> panel akun tampil
  await page.evaluate(() => {
    localStorage.setItem('tka_progress', JSON.stringify({
      matematika: { "1": { "1": { kunci: "A", benar: true }, "2": { kunci: "B", benar: false } } },
      fisika: { "1": { "1": { kunci: "B", benar: true } } },
    }));
    window.postMessage({ type: 'nav', path: 'Akun' }, '*');
  });
  await page.waitForTimeout(1800);
  const s1 = await page.evaluate(() => ({
    akun: document.getElementById('panelAkun') && document.getElementById('panelAkun').classList.contains('panel-active'),
    frame: document.getElementById('panelAkunFrame') ? document.getElementById('panelAkunFrame').getBoundingClientRect().width > 0 : false,
  }));
  report('Desktop: nav Akun -> panel akun tampil', s1.akun && s1.frame, JSON.stringify(s1));

  // 2) statistik real: 3 dikerjakan, 2 benar, 67%, 2 mapel
  const af = page.frames().find(f => f.url().includes('workspace_akun'));
  if (!af) { report('Desktop: iframe akun ditemukan', false); }
  else {
    const s2 = await af.evaluate(() => ({
      done: [...document.querySelectorAll('[data-d-stat-done]')].map(e => e.textContent.trim()),
      benar: document.querySelector('[data-d-stat-benar]').textContent.trim(),
      acc: document.querySelector('[data-d-stat-acc]').textContent.trim(),
      mapel: document.querySelector('[data-d-stat-mapel]').textContent.trim(),
      nama: document.querySelector('[data-d-name]').textContent.trim(),
    }));
    const ok = s2.done.every(v => v === '3') && s2.benar === '2' && s2.acc === '67%' && s2.mapel === '2' && s2.nama === 'Tamu';
    report('Desktop: statistik real + mode Tamu', ok, JSON.stringify(s2));
    try { await page.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 8000))])); } catch (e) {}
    try { await af.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 8000))])); } catch (e) {}
    await page.screenshot({ path: 'exports/panel_akun_desktop.png' });
  }

  // 3) reset riwayat: confirm di-accept -> localStorage kosong -> statistik 0
  page.on('dialog', d => d.accept());
  await af.evaluate(() => document.getElementById('d-btn-reset').click());
  await page.waitForTimeout(800);
  const s3 = await page.evaluate(() => localStorage.getItem('tka_progress'));
  const s3b = await af.evaluate(() => document.querySelector('[data-d-stat-done]').textContent.trim());
  report('Desktop: reset riwayat menghapus tka_progress', s3 === null && s3b === '0', `store=${s3}, done=${s3b}`);

  // 4) klik chip user di iframe Beranda -> nav Akun
  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Beranda' }, '*'));
  await page.waitForTimeout(1800);
  const hd = page.frames().find(f => f.url().includes('home_desktop'));
  if (!hd) { report('Desktop: iframe beranda ditemukan', false); }
  else {
    await hd.evaluate(() => document.querySelector('[data-nav-akun]').click());
    await page.waitForTimeout(1200);
    const s4 = await page.evaluate(() => document.getElementById('panelAkun').classList.contains('panel-active'));
    report('Desktop: klik chip user di Beranda -> panel Akun', s4);
  }
  await page.close();

  /* ================= MOBILE 390 ================= */
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(() => {});
  await m.waitForTimeout(3000);

  const s5 = await m.evaluate(() => ({
    akunItem: getComputedStyle(document.querySelector('.stitch-bottomnav a[data-nav="akun"]')).display,
    nav: getComputedStyle(document.querySelector('.stitch-bottomnav')).display,
  }));
  report('Mobile: item Akun tampil di bottom nav', s5.akunItem !== 'none' && s5.nav !== 'none', JSON.stringify(s5));

  await m.evaluate(() => window.postMessage({ type: 'nav', path: 'akun' }, '*'));
  await m.waitForTimeout(1500);
  try { await m.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 8000))])); } catch (e) {}
  try { const af2 = m.frames().find(f => f.url().includes('workspace_akun')); if (af2) await af2.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 8000))])); } catch (e) {}
  const s6 = await m.evaluate(() => ({
    akun: document.getElementById('panelAkun').classList.contains('panel-active'),
    frame: document.getElementById('panelAkunFrame').getBoundingClientRect().width > 0,
    navHidden: getComputedStyle(document.querySelector('.stitch-bottomnav')).display === 'none',
  }));
  report('Mobile: panel akun tampil, bottomnav Beranda hilang', s6.akun && s6.frame && s6.navHidden, JSON.stringify(s6));
  await m.screenshot({ path: 'exports/panel_akun_mobile.png' });

  await browser.close();
  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
