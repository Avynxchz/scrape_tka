/**
 * Tes navbar seragam desktop v2:
 * - Nav teks tepat 3: Beranda / Modul Belajar / Progres & Analitik (TANPA "Akun")
 * - Chip kuota + chip user (ikon profil) ada di semua header; klik profil -> panel Akun
 * - Tidak ada lagi: Bank Soal, FAQ, search header, notif
 * - Klik nav dari panel mana pun pindah panel dengan benar
 */
const { chromium } = require('playwright-core');
const BASE = 'http://127.0.0.1:8080';
const R = [];
function report(name, pass, extra) {
  R.push([name, pass]);
  console.log(`${pass ? 'PASS' : 'FAIL' } | ${name}${extra ? ' -> ' + extra : ''}`);
}

async function waitFonts(page, frame) {
  try { await page.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 8000))])); } catch (e) {}
  if (frame) { try { await frame.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 8000))])); } catch (e) {} }
}

async function headerInfo(page, frameSel) {
  return page.evaluate((sel) => {
    const root = sel ? document.querySelector(sel) : null;
    const doc = root ? root.contentWindow.document : document;
    const header = doc.querySelector('#modulDesktop header, #akunDesktop header, header');
    if (!header) return { ada: false };
    const navItems = [...header.querySelectorAll('nav a, nav button')].map(b => b.textContent.trim());
    const text = header.innerText;
    return {
      ada: true,
      navItems,
      kuota: text.includes('Kuota AI Tamu · 5/hari'),
      user: text.includes('Tamu'),
      akunDiNav: navItems.some(t => /akun/i.test(t)),
      tidakAda: ['Bank Soal', 'FAQ', 'Cari materi', 'Cari mapel'].filter(t => text.includes(t)),
      notif: text.includes('notifications'),
    };
  }, frameSel);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await page.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(3000);
  // overlay Home default TERBUKA; navbar hanya ada di dalam overlay

  // 1) Beranda
  const h1 = await headerInfo(page, '#homeDesktopFrame');
  report('Beranda: nav 3 item tanpa Akun + kuota + user, tanpa item mati',
    h1.ada && h1.navItems.length === 3 && !h1.akunDiNav && h1.kuota && h1.user && h1.tidakAda.length === 0 && !h1.notif,
    JSON.stringify(h1));
  await waitFonts(page, page.frames().find(f => f.url().includes('home_desktop')));
  await page.screenshot({ path: 'exports/nav_seragam_beranda.png' });

  // 2) Beranda -> klik Modul Belajar
  const hd = page.frames().find(f => f.url().includes('home_desktop'));
  await hd.evaluate(() => {
    [...document.querySelectorAll('header nav a, header nav button')]
      .find(b => b.textContent.trim() === 'Modul Belajar').click();
  });
  await page.waitForTimeout(1500);
  let active = await page.evaluate(() => document.getElementById('panelModul').classList.contains('panel-active'));
  report('Beranda -> Modul Belajar: panel Modul tampil', active);

  const hf = await headerInfo(page, '#panelModulFrame');
  report('Modul: struktur navbar sama (3 item, tanpa Akun)', hf.ada && hf.navItems.length === 3 && !hf.akunDiNav && hf.kuota && hf.user && hf.tidakAda.length === 0, JSON.stringify(hf));
  await waitFonts(page, page.frames().find(f => f.url().includes('workspace_modul')));
  await page.screenshot({ path: 'exports/nav_seragam_modul.png' });

  // 3) Modul -> klik ikon profil (chip user) -> panel Akun
  const mf = page.frames().find(f => f.url().includes('workspace_modul'));
  await mf.evaluate(() => document.querySelector('#modulDesktop header [data-nav="akun"]').click());
  await page.waitForTimeout(1500);
  active = await page.evaluate(() => document.getElementById('panelAkun').classList.contains('panel-active'));
  report('Modul -> klik ikon profil: panel Akun tampil', active);

  // 4) Akun -> klik Progres & Analitik
  const af = page.frames().find(f => f.url().includes('workspace_akun'));
  await af.evaluate(() => {
    [...document.querySelectorAll('#akunDesktop header nav a')]
      .find(b => b.textContent.trim() === 'Progres & Analitik').click();
  });
  await page.waitForTimeout(1500);
  active = await page.evaluate(() => document.getElementById('panelProgres').classList.contains('panel-active'));
  report('Akun -> Progres & Analitik: panel Progres tampil', active);

  const hp = await headerInfo(page, '#panelProgresFrame');
  report('Progres: struktur navbar sama (3 item, tanpa Akun)', hp.ada && hp.navItems.length === 3 && !hp.akunDiNav && hp.kuota && hp.user && hp.tidakAda.length === 0, JSON.stringify(hp));
  await waitFonts(page, page.frames().find(f => f.url().includes('workspace_progres')));
  await page.screenshot({ path: 'exports/nav_seragam_progres.png' });

  // 5) Progres -> klik ikon profil -> Akun, screenshot header akun
  const pf = page.frames().find(f => f.url().includes('workspace_progres'));
  await pf.evaluate(() => {
    const chip = [...document.querySelectorAll('header [onclick*="handleNavTab(\'akun\')"]')]
      .find(el => el.textContent.includes('Tamu'));
    chip.click();
  });
  await page.waitForTimeout(1500);
  active = await page.evaluate(() => document.getElementById('panelAkun').classList.contains('panel-active'));
  report('Progres -> klik ikon profil: panel Akun tampil', active);
  await waitFonts(page, page.frames().find(f => f.url().includes('workspace_akun')));
  await page.screenshot({ path: 'exports/nav_seragam_akun.png' });

  // 6) Akun -> klik Beranda
  await af.evaluate(() => {
    [...document.querySelectorAll('#akunDesktop header nav a')]
      .find(b => b.textContent.trim() === 'Beranda').click();
  });
  await page.waitForTimeout(1500);
  active = await page.evaluate(() => document.getElementById('panelBeranda').classList.contains('panel-active'));
  report('Akun -> Beranda: panel Beranda tampil', active);

  await browser.close();
  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
