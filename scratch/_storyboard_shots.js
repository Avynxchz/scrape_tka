/**
 * STORYBOARD SEQUENCE — screenshot app TKA Master (asli, localhost:8080).
 * Ambil rangkaian frame yang saling berkaitan untuk motion graphics AI.
 * Viewport konsisten: 390x844 @3x (iPhone-ish, 9:19.5).
 * Output: exports/storyboard/NN_label.png
 */
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const BASE = 'http://127.0.0.1:8080';
const OUT = path.join(__dirname, '..', 'exports', 'storyboard');
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true, hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  });
  const page = await ctx.newPage();
  let n = 0;
  const shot = async (label, wait = 900) => {
    await page.waitForTimeout(wait);
    n++;
    const name = `${String(n).padStart(2, '0')}_${label}.png`;
    await page.screenshot({ path: path.join(OUT, name) });
    console.log('OK', name);
  };
  const smoothScroll = async (to, step = 300, ms = 16) => {
    await page.evaluate(async ({ to, step, ms }) => {
      const start = window.scrollY;
      for (let y = start; y < to; y += step) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, ms)); }
      window.scrollTo(0, to);
    }, { to, step, ms });
  };

  // ===== A. LANDING =====
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(1800);
  await shot('landing_hero', 400);
  await smoothScroll(900); await shot('landing_fitur');
  const harga = await page.evaluate(() => document.getElementById('paket')?.offsetTop || 0);
  await smoothScroll(harga); await shot('landing_harga');
  await smoothScroll(0);

  // ===== B. APP: soal → opsi → jawab → feedback =====
  await page.goto(`${BASE}/app?subject=matematika&paket=1`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(2200);
  await shot('app_soal', 500);
  await smoothScroll(560); await shot('app_opsi', 600);

  // pilih jawaban C (kunci soal aktif kalau PG)
  const optC = await page.$('[data-key="C"], [onclick*=\'"C"\'], .option-item:nth-child(3)');
  if (optC) { await optC.click().catch(() => {}); await page.waitForTimeout(1300); }
  await shot('app_terjawab', 300);

  // tombol Cek Jawaban
  const cek = await page.$('#btnCekJawaban, [onclick*="cekJawaban"], .btn-cek');
  if (cek) { await cek.click().catch(() => {}); await page.waitForTimeout(1500); }
  await shot('app_feedback', 400);

  // ===== C. Pembahasan terbuka =====
  const exp = await page.$('#btnToggleExp, [onclick*="toggleExplanation"], #txtToggleExp');
  if (exp) { await exp.click().catch(() => {}); await page.waitForTimeout(1600); }
  await smoothScroll((await page.evaluate(() => document.body.scrollHeight)));
  await shot('app_pembahasan', 500);

  // ===== D. AI Tutor sheet dengan jawaban =====
  await page.evaluate(() => window.scrollTo(0, 0));
  const tutor = await page.$('#btnBarTutor');
  if (tutor) { await tutor.click().catch(() => {}); await page.waitForTimeout(1600); }
  const ci = await page.$('#chatInput, .tutor-input input, textarea');
  if (ci) {
    await ci.type('Kak, langkahnya gimana?', { delay: 25 }).catch(() => {});
    await page.keyboard.press('Enter');
    await page.waitForTimeout(4500);
  }
  await shot('app_tutor_jawab', 400);

  // ===== E. Daftar soal (grid) =====
  await page.keyboard.press('Escape').catch(() => {});
  await page.waitForTimeout(500);
  const grid = await page.$('.btn-daftar-soal, #btnDaftarSoal, [onclick*="Daftar"]');
  if (grid) { await grid.click({ force: true }).catch(() => {}); await page.waitForTimeout(1300); }
  await shot('app_daftar_soal', 300);

  // ===== F. kembali ke landing CTA =====
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(1500);
  const cta = await page.evaluate(() => document.querySelector('section.bg-pine')?.offsetTop || 0);
  await smoothScroll(cta); await shot('landing_cta', 400);

  await browser.close();
  console.log(`SELESAI: ${n} frame di exports/storyboard/`);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
