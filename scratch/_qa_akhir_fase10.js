const { chromium } = require('./node_modules/playwright-core');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://127.0.0.1:8080/app?subject=matematika&paket=1';
const QA_SCREENSHOTS = path.join(__dirname, 'screenshots_qa_akhir');
if (!fs.existsSync(QA_SCREENSHOTS)) {
  fs.mkdirSync(QA_SCREENSHOTS, { recursive: true });
}

async function runQA() {
  const browser = await chromium.launch({ headless: true });
  let totalErrors = 0;
  let checksCount = 0;
  let passCount = 0;

  function assert(cond, name) {
    checksCount++;
    if (cond) {
      passCount++;
      console.log(`  [PASS] ${name}`);
    } else {
      totalErrors++;
      console.error(`  [FAIL] ${name}`);
    }
  }

  try {
    const viewports = [
      { name: 'mobile_360', width: 360, height: 740 },
      { name: 'mobile_390', width: 390, height: 844 },
      { name: 'mobile_412', width: 412, height: 915 },
      { name: 'desktop_1280', width: 1280, height: 800 }
    ];

    for (const vp of viewports) {
      console.log(`\n==============================================`);
      console.log(`PENGUJIAN VIEWPORT: ${vp.name} (${vp.width}x${vp.height})`);
      console.log(`==============================================`);

      const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
      const page = await context.newPage();

      const consoleErrors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') consoleErrors.push(msg.text());
      });
      page.on('pageerror', err => consoleErrors.push(err.message));

      // 1. HALAMAN SOAL
      await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 12000 });
      await page.waitForTimeout(600);

      // Verifikasi navbar atas halaman soal
      const soalNavbar = await page.evaluate(() => {
        const top = document.querySelector('header, .top-nav, #topNav') || document.body.firstElementChild;
        const bg = window.getComputedStyle(top).backgroundColor;
        const rail = document.getElementById('workRail');
        const railVisible = rail ? window.getComputedStyle(rail).display !== 'none' : false;
        return { bg, railVisible };
      });
      assert(soalNavbar.railVisible, `[${vp.name}] Tombol navigasi floating (#workRail) tampil`);

      // Screenshot Halaman Soal
      await page.screenshot({ path: path.join(QA_SCREENSHOTS, `${vp.name}_1_soal.png`) });

      // 2. BUKA BERANDA
      await page.evaluate(() => {
        if (typeof homeOpen === 'function') homeOpen();
        if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
      });
      await page.waitForSelector('#homeOverlay:not(.home-hidden)', { timeout: 3000 });
      await page.waitForTimeout(500);

      // Screenshot Beranda
      await page.screenshot({ path: path.join(QA_SCREENSHOTS, `${vp.name}_2_beranda.png`) });

      // 3. BUKA MODUL
      await page.evaluate(() => {
        if (typeof homeShowPanel === 'function') homeShowPanel('modul');
      });
      await page.waitForTimeout(600);

      // Screenshot Modul
      await page.screenshot({ path: path.join(QA_SCREENSHOTS, `${vp.name}_3_modul.png`) });

      // 4. BUKA PROGRES
      await page.evaluate(() => {
        if (typeof homeShowPanel === 'function') homeShowPanel('progres');
      });
      await page.waitForTimeout(600);

      // Screenshot Progres
      await page.screenshot({ path: path.join(QA_SCREENSHOTS, `${vp.name}_4_progres.png`) });

      // 5. BUKA AKUN (MODE TAMU CEK)
      await page.evaluate(() => {
        if (typeof homeShowPanel === 'function') homeShowPanel('akun');
      });
      await page.waitForTimeout(600);

      const akunFrame = page.frame({ url: /akun/ }) || page.frame({ name: 'Akun & Preferensi TKA Master' });
      let isGuestPresent = false;
      if (akunFrame) {
        isGuestPresent = await akunFrame.evaluate(() => {
          const bodyText = document.body ? document.body.textContent : '';
          return bodyText.includes('Tamu') || bodyText.includes('Mode Tamu');
        });
      } else {
        // Fallback cek di top-level
        isGuestPresent = await page.evaluate(() => {
          const frameEl = document.getElementById('panelAkunFrame');
          const doc = frameEl?.contentDocument || frameEl?.contentWindow?.document;
          return doc ? doc.body.textContent.includes('Tamu') : false;
        });
      }
      assert(isGuestPresent, `[${vp.name}] Mode Tamu tetap utuh dan terdeteksi di panel Akun`);

      // Screenshot Akun
      await page.screenshot({ path: path.join(QA_SCREENSHOTS, `${vp.name}_5_akun.png`) });

      // Cek Horizontal Overflow pada Body (khusus mobile)
      if (vp.width < 900) {
        const hasHorizScroll = await page.evaluate(() => {
          return document.documentElement.scrollWidth > window.innerWidth;
        });
        assert(!hasHorizScroll, `[${vp.name}] Tidak ada horizontal scroll/overflow tak sengaja pada mobile`);
      }

      // Cek console error
      assert(consoleErrors.length === 0, `[${vp.name}] 0 console errors (actual: ${consoleErrors.length})`);
      if (consoleErrors.length > 0) {
        console.error('Console errors:', consoleErrors);
      }

      await context.close();
    }

  } catch (err) {
    console.error('QA Execution error:', err);
    totalErrors++;
  } finally {
    await browser.close();
  }

  console.log(`\n========================================`);
  console.log(`QA FASE 10 RESULT: ${passCount}/${checksCount} CHECKS PASS (${totalErrors} errors)`);
  console.log(`========================================\n`);

  if (totalErrors > 0) {
    process.exit(1);
  }
}

runQA();
