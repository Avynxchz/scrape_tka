/**
 * Screenshot halaman penting app TKA Master — viewport HP (390x844, DPR 3).
 * Menggunakan app ASLI yang jalan di localhost:8080 (bukan replikasi).
 *
 * Output: exports/app_shots/*.png
 */
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const BASE = 'http://127.0.0.1:8080';
const OUT = path.join(__dirname, '..', 'exports', 'app_shots');
fs.mkdirSync(OUT, { recursive: true });

const urlApp = `${BASE}/app?subject=matematika&paket=1`;

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,          // retina: tajam, cocok buat referensi AI
    isMobile: true, hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  });
  const page = await ctx.newPage();
  const shot = async (name, fullPage = false) => {
    await page.waitForTimeout(900);
    await page.screenshot({ path: path.join(OUT, name + '.png'), fullPage });
    console.log('OK:', name);
  };

  // ===== 1. Landing (hero) =====
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(1500);
  await shot('01_landing_hero');
  await page.evaluate(() => window.scrollTo(0, document.getElementById('fitur')?.offsetTop || 0));
  await page.waitForTimeout(1200);
  await shot('02_landing_fitur');

  // ===== 2. App: tampilan soal (atas) =====
  await page.goto(urlApp, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(2000);
  // soal 8: fungsi komposisi (soal tanpa gambar, paling bersih buat demo)
  await page.evaluate(() => { const el = document.getElementById('nomorInput'); if (el) { el.value = '8'; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); } });
  const goBtn = await page.$('#btnGoNomor, .btn-go, [onclick*="goToQuestion"]');
  if (goBtn) { await goBtn.click(); }
  await page.waitForTimeout(1500);
  await shot('03_app_soal');

  // scroll ke bawah: opsi jawaban
  await page.evaluate(() => window.scrollBy(0, 500));
  await shot('04_app_opsi');

  // ===== 3. Jawab soal → feedback benar =====
  const optC = await page.$('[data-key="C"], .option-item:nth-child(3), [onclick*="\'C\'"]');
  if (optC) { await optC.click(); await page.waitForTimeout(1200); }
  await page.evaluate(() => window.scrollBy(0, 400));
  await shot('05_app_feedback');

  // ===== 4. Panel pembahasan terbuka =====
  const expBtn = await page.$('#btnToggleExp, [onclick*="toggleExplanation"], #txtToggleExp');
  if (expBtn) { await expBtn.click(); await page.waitForTimeout(1500); }
  await page.evaluate(() => window.scrollBy(0, 600));
  await shot('06_app_pembahasan');

  // ===== 5. AI Tutor sheet =====
  const tutorBtn = await page.$('#btnBarTutor');
  if (tutorBtn) { await tutorBtn.click(); await page.waitForTimeout(1800); }
  await shot('07_app_tutor');
  // ketik pertanyaan dan kirim (kalau ada input)
  const chatInput = await page.$('#chatInput, .tutor-input input, textarea');
  if (chatInput) {
    await chatInput.type('Kak, kenapa f(x) = (x+1)^3 - 4(x+1)?', { delay: 30 });
    await page.keyboard.press('Enter');
    await page.waitForTimeout(4000);
    await shot('08_app_tutor_jawab');
  }

  // ===== 6. Simulasi: timer & grid daftar soal =====
  await page.keyboard.press('Escape');
  await page.evaluate(() => window.scrollTo(0, 0));
  const gridBtn = await page.$('#btnDaftarSoal, [onclick*="openDaftarModal"], .btn-daftar-soal');
  if (gridBtn) { await gridBtn.click(); await page.waitForTimeout(1200); }
  await shot('09_app_daftar_soal');

  await browser.close();
  console.log('SELESAI — cek exports/app_shots/');
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
