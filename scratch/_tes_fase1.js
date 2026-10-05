/**
 * Tes FASE 1: opsi jawaban terakhir tidak tertutup bar aksi.
 * Mobile 360x640 & 390x844; desktop 1280 (bar dalam kartu, bukan fixed).
 */
const { chromium } = require('playwright-core');
const BASE = 'http://127.0.0.1:8080';
const R = [];
function report(name, pass, extra) {
  R.push([name, pass]);
  console.log(`${pass ? 'PASS' : 'FAIL'} | ${name}${extra ? ' -> ' + extra : ''}`);
}

async function cekOpsi(m, label, vpH) {
  // scroll konten ke paling bawah
  await m.evaluate(() => {
    const el = [...document.querySelectorAll('#optionsContainer .option-item')].pop();
    if (el) el.scrollIntoView({ block: 'end', behavior: 'instant' });
    window.scrollTo(0, document.body.scrollHeight);
  });
  await m.waitForTimeout(500);
  const r = await m.evaluate(() => {
    const opts = [...document.querySelectorAll('#optionsContainer .option-item')];
    const last = opts[opts.length - 1];
    const bar = document.querySelector('.qcard-actions');
    const lr = last.getBoundingClientRect();
    const br = bar.getBoundingClientRect();
    return {
      optBottom: Math.round(lr.bottom),
      barTop: Math.round(br.top),
      barBottom: Math.round(br.bottom),
      vh: window.innerHeight,
      tertutup: lr.bottom > br.top,
      nOpsi: opts.length,
    };
  });
  report(`${label}: opsi terakhir bebas dari bar (bottom ${r.optBottom} <= bar ${r.barTop})`,
    !r.tertutup, JSON.stringify(r));
  return r;
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  /* ===== MOBILE 360x640 ===== */
  let m = await browser.newPage({ viewport: { width: 360, height: 640 } });
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await m.waitForTimeout(2500);
  await m.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await m.waitForTimeout(600);

  // jawab dulu supaya semua elemen tampil, lalu ke tab soal
  await cekOpsi(m, '360x640 sebelum jawab', 640);
  await m.evaluate(() => {
    const q = getCurrentQuestion();
    selectOption(String(q.kunci_jawaban), false);
  });
  await cekOpsi(m, '360x640 setelah cek jawaban', 640);

  // tombol AI hilang dari bar aksi
  const noAiBtn = await m.evaluate(() => !document.querySelector('.qcard-actions #btnBarTutor'));
  report('360x640: tombol AI dihapus dari bar aksi', noAiBtn);

  // bar flush paling bawah
  const flush = await m.evaluate(() => {
    const br = document.querySelector('.qcard-actions').getBoundingClientRect();
    return Math.abs(br.bottom - window.innerHeight) < 2;
  });
  report('360x640: bar aksi nempel paling bawah layar', flush);
  await m.screenshot({ path: 'exports/f1_soal_360.png' });
  await m.close();

  /* ===== MOBILE 390x844 ===== */
  m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await m.waitForTimeout(2500);
  await m.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await m.waitForTimeout(600);
  await cekOpsi(m, '390x844', 844);
  await m.screenshot({ path: 'exports/f1_soal_390.png' });
  await m.close();

  /* ===== DESKTOP 1280 (tidak berubah) ===== */
  const d = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await d.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await d.waitForTimeout(2500);
  await d.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  await d.waitForTimeout(600);
  const dt = await d.evaluate(() => {
    const bar = document.querySelector('.qcard-actions');
    const st = getComputedStyle(bar);
    const card = document.querySelector('.cbt-question-card').getBoundingClientRect();
    const br = bar.getBoundingClientRect();
    const opts = [...document.querySelectorAll('#optionsContainer .option-item')];
    const lr = opts[opts.length - 1].getBoundingClientRect();
    return {
      posisi: st.position,                 // desktop: static (di dalam kartu)
      dalamKartu: br.top > card.top && br.bottom < card.bottom + 2,
      aiBtn: !!document.querySelector('.qcard-actions #btnBarTutor'),
      optVisible: lr.bottom > 0,
    };
  });
  report('Desktop: bar aksi tetap di dalam kartu (bukan fixed), layout tak berubah',
    dt.posisi === 'static' && dt.dalamKartu && dt.optVisible, JSON.stringify(dt));
  await d.screenshot({ path: 'exports/f1_soal_desktop.png' });
  await d.close();

  await browser.close();
  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
