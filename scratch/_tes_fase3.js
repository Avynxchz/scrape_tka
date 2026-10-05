/**
 * Tes FASE 3: navbar atas halaman soal.
 * Mobile: tanpa hamburger/paket-tabs/ikon hijau; ada info mapel+paket+timer;
 *         tombol home -> dialog konfirmasi (Ya -> beranda, Tidak -> tetap).
 * Desktop: bg navbar HIJAU, tombol Beranda dengan dialog yang sama,
 *          Daftar Soal & Selesai Tes tetap ada.
 */
const { chromium } = require('playwright-core');
const BASE = 'http://127.0.0.1:8080';
const R = [];
function report(name, pass, extra) {
  R.push([name, pass]);
  console.log(`${pass ? 'PASS' : 'FAIL'} | ${name}${extra ? ' -> ' + extra : ''}`);
}

async function bukaHeader(m) {
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await m.waitForTimeout(2500);
  await m.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await m.waitForTimeout(600);
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  /* ===== MOBILE 390 ===== */
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await bukaHeader(m);

  const s1 = await m.evaluate(() => {
    const header = document.querySelector('.app-header');
    const st = getComputedStyle(header);
    const vis = el => el && getComputedStyle(el).display !== 'none';
    return {
      bg: st.backgroundColor,
      hamburger: vis(document.getElementById('btnMobileMenu')),
      paketTabs: vis(document.querySelector('.package-tabs')),
      ikonBrand: vis(document.querySelector('.brand-logo')),
      infoText: (document.getElementById('mQNum') || {}).innerText || '',
      homeBtn: vis(document.getElementById('btnHome')),
      timer: vis(document.getElementById('timerPill')),
      overflow: vis(document.getElementById('btnMobileOverflow')),
      overflowIsi: (document.getElementById('mOverflowPanel') || {}).innerText || '',
    };
  });
  const hijau = s1.bg === 'rgb(0, 74, 42)';
  report('Mobile: bg navbar hijau tema', hijau, s1.bg);
  report('Mobile: hamburger/paket-tabs/ikon-brand dihapus',
    !s1.hamburger && !s1.paketTabs && !s1.ikonBrand, JSON.stringify(s1));
  report('Mobile: info mapel+paket tampil (2 baris)', /Matematika/.test(s1.infoText) && /Paket 1/.test(s1.infoText), s1.infoText.replace(/\n/g, ' | '));
  report('Mobile: home + timer + overflow (Daftar/Selesai) tetap ada',
    s1.homeBtn && s1.timer && s1.overflow && s1.overflowIsi.includes('Daftar Soal') && s1.overflowIsi.includes('Selesai Tes'), JSON.stringify(s1));

  // 2) klik home -> dialog muncul; Tidak -> tetap di soal
  await m.evaluate(() => document.getElementById('btnHome').click());
  await m.waitForTimeout(500);
  const s2 = await m.evaluate(() => ({
    dialog: document.getElementById('exitConfirmModal').classList.contains('open'),
    teks: document.querySelector('.exit-confirm-text').textContent.includes('disimpan'),
  }));
  report('Mobile: klik home -> dialog konfirmasi muncul', s2.dialog && s2.teks, JSON.stringify(s2));
  await m.screenshot({ path: 'exports/f3_dialog_mobile.png' });
  await m.evaluate(() => document.querySelector('.exit-btn-tidak').click());
  await m.waitForTimeout(400);
  const s3 = await m.evaluate(() => ({
    dialogTutup: !document.getElementById('exitConfirmModal').classList.contains('open'),
    masihSoal: !document.getElementById('homeOverlay').classList.contains('home-hidden') === false || document.getElementById('homeOverlay').classList.contains('home-hidden'),
  }));
  report('Mobile: Tidak -> tetap di halaman soal', s3.dialogTutup && s3.masihSoal, JSON.stringify(s3));

  // 3) klik home -> Ya -> panel Beranda tampil + jawaban tersimpan
  await m.evaluate(() => {
    const q = getCurrentQuestion();
    selectOption(String(q.kunci_jawaban), false); // jawab soal 1 (persist otomatis)
    document.getElementById('btnHome').click();
  });
  await m.waitForTimeout(400);
  await m.evaluate(() => document.querySelector('.exit-btn-ya').click());
  await m.waitForTimeout(1200);
  const s4 = await m.evaluate(() => ({
    beranda: document.getElementById('panelBeranda').classList.contains('panel-active'),
    overlayOpen: !document.getElementById('homeOverlay').classList.contains('home-hidden'),
    jawaban: JSON.parse(localStorage.getItem('tka_progress') || '{}'),
  }));
  report('Mobile: Ya -> panel Beranda tampil', s4.beranda && s4.overlayOpen, JSON.stringify(s4.beranda));
  // balik ke soal, cek jawaban tersimpan: localStorage tka_progress matematika p1 soal 1
  await m.evaluate(() => homeClose());
  await m.waitForTimeout(600);
  const tersimpan = await m.evaluate(() => {
    const raw = JSON.parse(localStorage.getItem('tka_progress') || '{}');
    return !!((raw.matematika || {})['1'] || {})['1'];
  });
  report('Mobile: jawaban tersimpan otomatis (tka_progress)', tersimpan);
  await m.close();

  /* ===== DESKTOP 1280 ===== */
  const d = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await d.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await d.waitForTimeout(2500);
  await d.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await d.waitForTimeout(600);
  const d1 = await d.evaluate(() => {
    const header = document.querySelector('.app-header');
    const st = getComputedStyle(header);
    return {
      bg: st.backgroundColor,
      beranda: !!document.getElementById('btnHome') && getComputedStyle(document.getElementById('btnHome')).display !== 'none',
      daftar: getComputedStyle(document.getElementById('btnOpenDaftarSoal')).display !== 'none',
      selesai: getComputedStyle(document.getElementById('btnFinishHeader')).display !== 'none',
      paketTabs: getComputedStyle(document.querySelector('.package-tabs')).display !== 'none',
      subjectSel: getComputedStyle(document.getElementById('mobileMenuPanel')).display !== 'none',
    };
  });
  report('Desktop: navbar hijau + Beranda/Daftar/Selesai/Paket-tabs/subject lengkap',
    d1.bg === 'rgb(0, 74, 42)' && d1.beranda && d1.daftar && d1.selesai && d1.paketTabs && d1.subjectSel, JSON.stringify(d1));

  // dialog di desktop
  await d.evaluate(() => document.getElementById('btnHome').click());
  await d.waitForTimeout(400);
  const d2 = await d.evaluate(() => document.getElementById('exitConfirmModal').classList.contains('open'));
  report('Desktop: tombol Beranda -> dialog konfirmasi', d2);
  await d.screenshot({ path: 'exports/f3_dialog_desktop.png' });
  await d.evaluate(() => document.querySelector('.exit-btn-ya').click());
  await d.waitForTimeout(1200);
  const d3 = await d.evaluate(() => document.getElementById('panelBeranda').classList.contains('panel-active'));
  report('Desktop: Ya -> panel Beranda tampil', d3);
  await d.close();

  await browser.close();
  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
