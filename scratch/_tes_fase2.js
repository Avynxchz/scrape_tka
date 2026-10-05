/**
 * Tes FASE 2: tab atas hilang di mobile (rail tetap menguasai navigasi),
 * chip saran AI satu baris horizontal, desktop tidak berubah.
 */
const { chromium } = require('playwright-core');
const BASE = 'http://127.0.0.1:8080';
const R = [];
function report(name, pass, extra) {
  R.push([name, pass]);
  console.log(`${pass ? 'PASS' : 'FAIL'} | ${name}${extra ? ' -> ' + extra : ''}`);
}

async function bukaAiPane(m) {
  // dari rail: klik Tanya AI (mobile = sheet, desktop = full pane)
  await m.evaluate(() => document.querySelector('#workRail .rail-btn[data-rail="ai"]').click());
  await m.waitForTimeout(900);
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  /* ===== MOBILE 390 ===== */
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await m.waitForTimeout(2500);
  await m.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await m.waitForTimeout(600);

  // 1) tab atas hilang di mobile
  const s1 = await m.evaluate(() => getComputedStyle(document.getElementById('workTabs')).display);
  report('Mobile: tab atas (Lembar Soal/Pembahasan & AI) dihapus', s1 === 'none', s1);

  // 2) rail AI tetap membuka tampilan AI (sheet full screen)
  await bukaAiPane(m);
  const s2 = await m.evaluate(() => ({
    sheet: document.getElementById('cbtSidebarCol').classList.contains('tutor-open'),
    chatH: Math.round(document.getElementById('chatMessages').getBoundingClientRect().height),
    sheetH: Math.round(document.getElementById('cbtSidebarCol').getBoundingClientRect().height),
    vh: window.innerHeight,
  }));
  report('Mobile: rail AI membuka tampilan AI (sheet full)', s2.sheet && s2.sheetH >= s2.vh - 4, JSON.stringify(s2));

  // 3) chip saran: satu baris horizontal (semua chip offsetTop sama + bisa scroll samping)
  const s3 = await m.evaluate(() => {
    const wrap = document.querySelector('#pembSubAI .quick-chips, .quick-chips');
    const chips = [...wrap.querySelectorAll('.chip-btn')];
    const tops = [...new Set(chips.map(c => Math.round(c.getBoundingClientRect().top)))];
    const wrapSt = getComputedStyle(wrap);
    return {
      n: chips.length,
      satuBaris: tops.length === 1,
      nowrap: wrapSt.flexWrap === 'nowrap',
      scrollX: wrap.scrollWidth > wrap.clientWidth,
      wrapper: wrap.id || wrap.className,
    };
  });
  report('Mobile: chip saran satu baris horizontal', s3.n >= 3 && s3.satuBaris && s3.nowrap, JSON.stringify(s3));
  await m.screenshot({ path: 'exports/f2_ai_mobile.png' });

  // 4) chat area lebih luas: tinggi chat >= 55% layar
  report('Mobile: area chat lebih luas (>=55% tinggi layar)', s2.chatH >= s2.vh * 0.55, `chatH=${s2.chatH}/${s2.vh}`);

  // 5) tutup sheet -> tetap konsisten (kembali ke pembahasan pilar)
  await m.evaluate(() => closeTutorSheet());
  await m.waitForTimeout(600);
  const s5 = await m.evaluate(() => ({
    materi: document.getElementById('pembSubMateri').style.display === 'block',
    tabMasihHilang: getComputedStyle(document.getElementById('workTabs')).display === 'none',
  }));
  report('Mobile: tutup AI -> kembali ke pembahasan, tab tetap hilang', s5.materi && s5.tabMasihHilang, JSON.stringify(s5));
  await m.close();

  /* ===== DESKTOP 1280 (tidak berubah) ===== */
  const d = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await d.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await d.waitForTimeout(2500);
  await d.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await d.waitForTimeout(600);
  const d1 = await d.evaluate(() => ({
    tabTampil: getComputedStyle(document.getElementById('workTabs')).display !== 'none',
    chipsWrap: getComputedStyle(document.querySelector('.quick-chips')).flexWrap,
  }));
  report('Desktop: tab atas TETAP tampil + chip tidak berubah', d1.tabTampil && d1.chipsWrap === 'wrap', JSON.stringify(d1));
  await d.close();

  await browser.close();
  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
