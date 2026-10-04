const { chromium } = require('./node_modules/playwright-core');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://127.0.0.1:8080/app?subject=matematika&paket=1';
const MODUL_DIRECT_URL = 'http://127.0.0.1:8080/workspace_modul/modul.html';
const SCREENSHOT_DIR = path.join(__dirname, 'screenshots_fase8');
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

    console.log('\n--- 1. Buka Modul Mobile ---');
    await page.goto(MODUL_DIRECT_URL, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(500);

    console.log('\n--- 2. Cek Carousel Modul & Animasi Robot Baca Buku ---');
    const hasCarousel = await page.evaluate(() => !!document.getElementById('modulCarousel'));
    const hasRobotReading = await page.evaluate(() => !!document.querySelector('.modul-robot-reading'));
    const hasDots = await page.evaluate(() => document.querySelectorAll('#modulDots i').length === 2);
    assert(hasCarousel, 'Carousel modul (#modulCarousel) tersedia');
    assert(hasRobotReading, 'Animasi robot sedang membaca buku (.modul-robot-reading) ada di Slide 1');
    assert(hasDots, 'Tersedia 2 dots navigasi carousel modul (#modulDots)');

    console.log('\n--- 3. Cek Warna Semua Teks Carousel Modul adalah PUTIH ---');
    const nonWhiteTexts = await page.evaluate(() => {
      const texts = Array.from(document.querySelectorAll('#modulCarousel h2, #modulCarousel p, #modulCarousel span, #modulCarousel b'));
      return texts.map(el => {
        const cs = window.getComputedStyle(el);
        return { text: el.textContent.trim().slice(0, 20), color: cs.color };
      }).filter(t => t.color !== 'rgb(255, 255, 255)' && t.color !== 'rgba(255, 255, 255, 1)');
    });
    assert(nonWhiteTexts.length === 0, `Semua teks di dalam carousel modul berwarna putih rgb(255, 255, 255) (non-putih: ${nonWhiteTexts.length})`);
    if (nonWhiteTexts.length > 0) {
      console.log('    Detail non-putih:', nonWhiteTexts.slice(0, 3));
    }

    console.log('\n--- 4. Cek Kelengkapan 22 Mapel & Kategori ---');
    const totalMapelCards = await page.evaluate(() => {
      return document.querySelectorAll('#modulMobile [data-card]').length;
    });
    const totalCategories = await page.evaluate(() => {
      return document.querySelectorAll('#modulMobile [data-cat-section]').length;
    });
    assert(totalMapelCards === 22, `Daftar tetap berisi SEMUA 22 mapel (actual: ${totalMapelCards})`);
    assert(totalCategories === 5, `Pengelompokan 5 kategori (Wajib, Saintek, Soshum, Lanjut, Bahasa) dipertahankan (actual: ${totalCategories})`);

    console.log('\n--- 5. Uji Perhitungan Progres Gabungan dengan Data Tiruan ---');
    // Tes baseline default (4 mapel pilihan: Mtk 71, B.Indo 45, B.Ing 45, Fisika 44 = 205 soal)
    const baseCalc = await page.evaluate(() => {
      localStorage.removeItem('tka_progress');
      localStorage.removeItem('tka_user_subjects');
      if (typeof readLocalProgress === 'function') readLocalProgress();
      return getCombinedProgress();
    });
    assert(baseCalc.totalSoal === 205, `Total soal default 4 mapel pilihan = 205 (actual: ${baseCalc.totalSoal})`);
    assert(baseCalc.totalDone === 0, `Total done awal = 0 (actual: ${baseCalc.totalDone})`);

    // Injeksi data tiruan: Matematika 10 soal, Fisika 5 soal
    const mockCalc = await page.evaluate(() => {
      const mockProg = {
        matematika: {
          '1': { '0': { a: 'A', c: true }, '1': { a: 'B', c: true }, '2': { a: 'C', c: true }, '3': { a: 'D', c: true }, '4': { a: 'E', c: true }, '5': { a: 'A', c: false }, '6': { a: 'B', c: false }, '7': { a: 'C', c: false }, '8': { a: 'D', c: false }, '9': { a: 'E', c: false } }
        },
        fisika: {
          '1': { '0': { a: 'A', c: true }, '1': { a: 'B', c: true }, '2': { a: 'C', c: true }, '3': { a: 'D', c: true }, '4': { a: 'E', c: true } }
        }
      };
      localStorage.setItem('tka_progress', JSON.stringify(mockProg));
      if (typeof readLocalProgress === 'function') readLocalProgress();
      if (typeof refreshProgress === 'function') refreshProgress();
      const res = getCombinedProgress();

      // Cek DOM multi-segmented bar & legend
      const barSegments = document.querySelectorAll('#modulCombinedBar > div');
      const legendChips = document.querySelectorAll('#modulCombinedLegend > div');
      const pctText = document.getElementById('modulCombinedPct')?.textContent;

      return {
        res,
        segmentCount: barSegments.length,
        legendCount: legendChips.length,
        pctText,
        firstSegWidth: barSegments[0]?.style.width
      };
    });

    assert(mockCalc.res.totalDone === 15, `Total soal selesai tiruan adalah 15 (actual: ${mockCalc.res.totalDone})`);
    assert(mockCalc.res.pct === 7, `Persentase progres gabungan 15/205 dibulatkan ke 7% (actual: ${mockCalc.res.pct}%)`);
    assert(mockCalc.pctText === '7%', `Teks persentase di DOM menunjukkan 7% (actual: ${mockCalc.pctText})`);
    assert(mockCalc.segmentCount >= 2, `Segmented bar memiliki segmen terisi (actual: ${mockCalc.segmentCount})`);
    assert(mockCalc.legendCount === 4, `Legenda menampilkan 4 mapel pilihan (actual: ${mockCalc.legendCount})`);

    // Tes dinamis: ganti mapel pilihan user ke 2 mapel (Matematika & Kimia = 71 + 44 = 115 soal)
    const customSubjectsCalc = await page.evaluate(() => {
      localStorage.setItem('tka_user_subjects', JSON.stringify(['matematika', 'kimia']));
      if (typeof refreshProgress === 'function') refreshProgress();
      return getCombinedProgress();
    });
    assert(customSubjectsCalc.mapels.length === 2, `Mapel pilihan terupdate jadi 2 mapel (actual: ${customSubjectsCalc.mapels.length})`);
    assert(customSubjectsCalc.totalSoal === 115, `Total soal 2 mapel (Mtk+Kimia) = 115 (actual: ${customSubjectsCalc.totalSoal})`);

    // Bersihkan data tiruan
    await page.evaluate(() => {
      localStorage.removeItem('tka_progress');
      localStorage.removeItem('tka_user_subjects');
      if (typeof readLocalProgress === 'function') readLocalProgress();
      if (typeof refreshProgress === 'function') refreshProgress();
    });

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
      await vpPage.goto(MODUL_DIRECT_URL, { waitUntil: 'domcontentloaded' });
      await vpPage.waitForTimeout(400);

      const shotPath = path.join(SCREENSHOT_DIR, `${vp.name}.png`);
      await vpPage.screenshot({ path: shotPath });
      console.log(`  Saved screenshot: ${shotPath}`);

      if (vp.name === 'mobile_390') {
        // Klik dot 2 untuk slide 2 progres gabungan
        const dts = await vpPage.$$('#modulDots i');
        if (dts.length >= 2) {
          await dts[1].click();
          await vpPage.waitForTimeout(600);
          await vpPage.screenshot({ path: path.join(SCREENSHOT_DIR, 'mobile_390_slide2_progres.png') });
          console.log('  Saved mobile_390 slide 2 (progres gabungan) screenshot');
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
  console.log(`FASE 8 RESULT: ${passCount}/${testCount} PASS (${totalErrors} errors)`);
  console.log(`========================================\n`);

  if (totalErrors > 0) {
    process.exit(1);
  }
}

runTest();
