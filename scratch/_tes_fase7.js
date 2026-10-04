const { chromium } = require('./node_modules/playwright-core');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://127.0.0.1:8080/app?subject=matematika&paket=1';
const SCREENSHOT_DIR = path.join(__dirname, 'screenshots_fase7');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function runTest() {
  const browser = await chromium.launch({ headless: true });
  let totalErrors = 0;
  let testCount = 0;
  let passCount = 0;

  function assert(cond, name) {
    testCount++;
    if (cond) {
      passCount++;
      console.log(`  [PASS] ${name}`);
    } else {
      totalErrors++;
      console.error(`  [FAIL] ${name}`);
    }
  }

  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();

    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('pageerror', err => consoleErrors.push(err.message));

    console.log('\n--- 1. Buka halaman dan buka Beranda ---');
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(500);

    // Buka Beranda
    await page.evaluate(() => {
      if (typeof homeOpen === 'function') homeOpen();
      if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
    });
    await page.waitForSelector('#homeOverlay:not(.home-hidden)', { timeout: 3000 });
    await page.waitForTimeout(500);

    console.log('\n--- 2. Cek elemen dekoratif dotrow dan cap dihapus ---');
    const dotrowCount = await page.evaluate(() => document.querySelectorAll('.stitch-dotrow').length);
    const capCount = await page.evaluate(() => document.querySelectorAll('.stitch-cap').length);
    assert(dotrowCount === 0, `Tidak ada elemen .stitch-dotrow (actual: ${dotrowCount})`);
    assert(capCount === 0, `Tidak ada elemen .stitch-cap (actual: ${capCount})`);

    console.log('\n--- 3. Cek warna semua teks dalam carousel adalah PUTIH (#FFFFFF) ---');
    const heroTextColors = await page.evaluate(() => {
      const texts = Array.from(document.querySelectorAll('.stitch-hero h3, .stitch-hero p, .stitch-hero span:not(.stitch-paper *):not(.st-slide-badge), .stitch-hero b:not(.stitch-paper *)'));
      return texts.map(el => {
        const cs = window.getComputedStyle(el);
        return { tag: el.tagName, text: el.textContent.trim().slice(0, 20), color: cs.color };
      });
    });

    const nonWhiteTexts = heroTextColors.filter(t => t.color !== 'rgb(255, 255, 255)');
    assert(nonWhiteTexts.length === 0, `Semua teks judul/deskripsi/label hero berwarna putih rgb(255, 255, 255) (non-putih: ${nonWhiteTexts.length})`);
    if (nonWhiteTexts.length > 0) {
      console.log('    Detail non-putih:', nonWhiteTexts.slice(0, 5));
    }

    console.log('\n--- 4. Cek Animasi Slide 2 (Pie Chart) & Slide 3 (Robot AI) ---');
    const hasPieSvg = await page.evaluate(() => !!document.querySelector('.hero-pie-card svg'));
    const hasRobotSvg = await page.evaluate(() => !!document.querySelector('.hero-robot-card svg'));
    assert(hasPieSvg, 'Slide 2 memiliki elemen SVG Pie Chart (.hero-pie-card svg)');
    assert(hasRobotSvg, 'Slide 3 memiliki elemen SVG Robot Mascot (.hero-robot-card svg)');

    console.log('\n--- 5. Cek Navigasi Dot Carousel ---');
    const dots = await page.$$('#heroDots i');
    assert(dots.length === 3, `Jumlah dots carousel adalah 3 (actual: ${dots.length})`);

    // Klik dot ke-2
    if (dots.length >= 2) {
      await dots[1].click();
      await page.waitForTimeout(600);
      const isDot2Active = await page.evaluate(() => {
        const ds = document.querySelectorAll('#heroDots i');
        return ds[1] && ds[1].classList.contains('on');
      });
      assert(isDot2Active, 'Dot ke-2 aktif setelah diklik');
    }

    // Klik dot ke-3
    if (dots.length >= 3) {
      await dots[2].click();
      await page.waitForTimeout(600);
      const isDot3Active = await page.evaluate(() => {
        const ds = document.querySelectorAll('#heroDots i');
        return ds[2] && ds[2].classList.contains('on');
      });
      assert(isDot3Active, 'Dot ke-3 aktif setelah diklik');
    }

    console.log('\n--- 6. Console Error Check ---');
    assert(consoleErrors.length === 0, `0 error di console (actual: ${consoleErrors.length})`);
    if (consoleErrors.length > 0) {
      console.error('Console errors:', consoleErrors);
    }

    await context.close();

    console.log('\n--- 7. Ambil Screenshot Berbagai Resolusi ---');
    const viewports = [
      { name: 'mobile_360', width: 360, height: 740 },
      { name: 'mobile_390', width: 390, height: 844 },
      { name: 'mobile_412', width: 412, height: 915 },
      { name: 'desktop_1280', width: 1280, height: 800 }
    ];

    for (const vp of viewports) {
      const vctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
      const vpPage = await vctx.newPage();
      await vpPage.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
      await vpPage.waitForTimeout(300);
      await vpPage.evaluate(() => {
        if (typeof homeOpen === 'function') homeOpen();
        if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
      });
      await vpPage.waitForSelector('#homeOverlay:not(.home-hidden)');
      await vpPage.waitForTimeout(500);

      const shotPath = path.join(SCREENSHOT_DIR, `${vp.name}.png`);
      await vpPage.screenshot({ path: shotPath });
      console.log(`  Saved screenshot: ${shotPath}`);

      // Ambil juga screenshot slide 2 & 3 di mobile_390
      if (vp.name === 'mobile_390') {
        const dts = await vpPage.$$('#heroDots i');
        if (dts.length >= 3) {
          await dts[1].click();
          await vpPage.waitForTimeout(600);
          await vpPage.screenshot({ path: path.join(SCREENSHOT_DIR, 'mobile_390_slide2.png') });
          await dts[2].click();
          await vpPage.waitForTimeout(600);
          await vpPage.screenshot({ path: path.join(SCREENSHOT_DIR, 'mobile_390_slide3.png') });
          console.log('  Saved slide 2 & slide 3 screenshots for mobile_390');
        }
      }

      await vctx.close();
    }

  } catch (err) {
    console.error('Test execution error:', err);
    totalErrors++;
  } finally {
    await browser.close();
  }

  console.log(`\n========================================`);
  console.log(`FASE 7 RESULT: ${passCount}/${testCount} PASS (${totalErrors} errors)`);
  console.log(`========================================\n`);

  if (totalErrors > 0) {
    process.exit(1);
  }
}

runTest();
