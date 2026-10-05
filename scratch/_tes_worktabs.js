/**
 * Tes Work Tabs (Arah 2): Lembar Soal vs Pembahasan & AI + rail kanan.
 * Desktop 1280 & mobile 390.
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

  /* ================= DESKTOP ================= */
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await page.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(3000);
  await page.evaluate(() => document.getElementById('btnHome').click()); // tutup home
  await page.waitForTimeout(1000);

  // 1) default: tab Lembar Soal aktif, pane pembahasan tertutup
  const s1 = await page.evaluate(() => ({
    soal: document.getElementById('workPaneSoal').classList.contains('active'),
    soalVisible: document.getElementById('workPaneSoal').style.display !== 'none',
    pembHidden: document.getElementById('workPanePembahasan').style.display === 'none',
    rail: !!document.querySelector('#workRail .rail-btn.active[data-rail="soal"]'),
  }));
  report('Desktop: default tab Lembar Soal + rail aktif soal', s1.soal && s1.soalVisible && s1.pembHidden && s1.rail, JSON.stringify(s1));
  await page.screenshot({ path: 'exports/worktab_soal_desktop.png' });

  // 2) klik tab Pembahasan & AI -> pane terbuka, pilar tampil, sub materi aktif
  await page.evaluate(() => switchWorkTab('pembahasan'));
  await page.waitForTimeout(800);
  const s2 = await page.evaluate(() => ({
    pane: document.getElementById('workPanePembahasan').classList.contains('active'),
    sub: document.getElementById('pembSubMateri').style.display === 'block',
    pilar1: document.getElementById('conceptContainer') !== null,
    learningOpen: document.getElementById('learningSection').style.display === 'flex',
    rail: !!document.querySelector('#workRail .rail-btn.active[data-rail="materi"]'),
  }));
  report('Desktop: tab Pembahasan -> pilar tampil (sub Pembahasan)', s2.pane && s2.sub && s2.pilar1 && s2.learningOpen && s2.rail, JSON.stringify(s2));

  // 3) rail AI -> full pane AI
  await page.evaluate(() => switchPembSub('ai'));
  await page.waitForTimeout(600);
  const s3 = await page.evaluate(() => ({
    ai: document.getElementById('pembSubAI').style.display === 'block',
    chat: document.getElementById('chatMessages') !== null,
    rail: !!document.querySelector('#workRail .rail-btn.active[data-rail="ai"]'),
  }));
  report('Desktop: rail AI -> full pane Tanya AI', s3.ai && s3.chat && s3.rail, JSON.stringify(s3));
  await page.screenshot({ path: 'exports/worktab_ai_desktop.png' });

  // 4) balik ke pembahasan lalu ke soal via rail
  await page.evaluate(() => switchWorkTab('soal'));
  await page.waitForTimeout(400);
  const s4 = await page.evaluate(() => document.getElementById('workPaneSoal').classList.contains('active'));
  report('Desktop: rail Soal -> kembali ke lembar soal', s4);

  // 5) cek jawaban -> strip di tab pembahasan + auto pindah tab
  await page.evaluate(() => {
    const q = getCurrentQuestion();
    selectOption(String(q.kunci_jawaban), false);
  });
  await page.evaluate(() => checkUserAnswer());
  await page.waitForTimeout(600);
  const s5a = await page.evaluate(() => ({
    strip: document.getElementById('pembResultStrip').style.display !== 'none',
    stillSoal: document.getElementById('workPaneSoal').classList.contains('active'),
  }));
  await page.waitForTimeout(1200);
  const s5b = await page.evaluate(() => ({
    moved: document.getElementById('workPanePembahasan').classList.contains('active'),
    stripVisible: document.getElementById('pembResultStrip').style.display !== 'none',
  }));
  report('Desktop: cek jawaban -> strip muncul lalu auto pindah ke Pembahasan', s5a.strip && s5a.stillSoal && s5b.moved && s5b.stripVisible, JSON.stringify({ s5a, s5b }));
  await page.screenshot({ path: 'exports/worktab_pembahasan_desktop.png' });
  await page.close();

  /* ================= MOBILE ================= */
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(() => {});
  await m.waitForTimeout(3000);
  await m.evaluate(() => document.getElementById('btnHome').click());
  await m.waitForTimeout(800);

  // tab soal default, tab bar tampil
  const s6 = await m.evaluate(() => ({
    soal: document.getElementById('workPaneSoal').classList.contains('active'),
    tabs: getComputedStyle(document.getElementById('workTabs')).display,
  }));
  report('Mobile: default tab Lembar Soal', s6.soal, JSON.stringify(s6));
  await m.screenshot({ path: 'exports/worktab_soal_mobile.png' });

  // buka AI via tombol bar -> bottom sheet tetap jalan + pane pembahasan di belakang
  await m.evaluate(() => openTutorSheet());
  await m.waitForTimeout(800);
  const s7 = await m.evaluate(() => ({
    sheet: document.getElementById('cbtSidebarCol').classList.contains('tutor-open'),
    pembActive: document.getElementById('workPanePembahasan').classList.contains('active'),
  }));
  report('Mobile: tombol AI -> bottom sheet terbuka', s7.sheet && s7.pembActive, JSON.stringify(s7));
  await m.screenshot({ path: 'exports/worktab_ai_mobile.png' });

  await browser.close();
  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
