const { chromium } = require('./node_modules/playwright-core');
const fs = require('fs');
const path = require('path');

const PROGRES_URL = 'http://127.0.0.1:8080/workspace_progres/progres.html';
const APP_URL = 'http://127.0.0.1:8080/app?subject=matematika&paket=1';
const SCREENSHOT_DIR = path.join(__dirname, 'screenshots_fase9');
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

    // Siapkan data dummy realistis di localStorage terlebih dahulu
    const sampleData = {
      matematika: {
        '1': {
          '0': { benar: true }, '1': { benar: true }, '2': { benar: true }, '3': { benar: false }, '4': { benar: true }
        }
      },
      fisika: {
        '1': {
          '0': { benar: true }, '1': { benar: false }, '2': { benar: true }
        }
      }
    };

    console.log('\n--- 1. Uji Anti-Blinking / Anti-Flicker Saat Membuka Progres ---');
    // Set data sebelum load
    await page.goto(PROGRES_URL, { waitUntil: 'commit' });
    await page.evaluate(data => {
      localStorage.setItem('tka_progress', JSON.stringify(data));
      localStorage.setItem('tka_study_streak', '3');
    }, sampleData);

    await page.goto(PROGRES_URL, { waitUntil: 'domcontentloaded' });

    // Sampling DOM #mobile-kpi-container setiap 250ms selama 2.5 detik untuk memastikan tidak ada flicker / innerHTML reset berulang
    const samples = [];
    for (let i = 0; i < 10; i++) {
      const sample = await page.evaluate(() => {
        const kpi = document.getElementById('mobile-kpi-container');
        if (!kpi) return null;
        return {
          childrenCount: kpi.children.length,
          textSnippet: kpi.textContent.replace(/\s+/g, ' ').trim().slice(0, 50),
          hasFadeIn: !!kpi.querySelector('.fade-in')
        };
      });
      samples.push(sample);
      await page.waitForTimeout(250);
    }

    // Periksa bahwa semua sampel konsisten (tidak kosong atau berkedip hilang di tengah sampling)
    const allValid = samples.every(s => s && s.childrenCount > 0 && s.textSnippet.length > 0);
    const noFlickerFadeIn = samples.every(s => s && !s.hasFadeIn);
    assert(allValid, 'DOM #mobile-kpi-container stabil selama 2.5 detik sampling (tidak pernah kosong/hilang)');
    assert(noFlickerFadeIn, 'Tidak ada class .fade-in yang memicu animasi berulang saat re-render');

    console.log('\n--- 2. Uji Dashboard Analitik Belajar (Streak, Waktu, & Kategori) ---');
    const analytics = await page.evaluate(() => {
      const text = document.getElementById('mobile-kpi-container')?.textContent || '';
      return {
        hasStreak: text.includes('Streak Belajar') && text.includes('Hari'),
        hasStudyTime: text.includes('Waktu Belajar') && text.includes('mnt'),
        hasCategoryDist: text.includes('Distribusi Rumpun Mapel') && text.includes('Wajib') && text.includes('Saintek')
      };
    });

    assert(analytics.hasStreak, 'Widget Streak Belajar (kehadiran) tampil dengan benar');
    assert(analytics.hasStudyTime, 'Widget Waktu Belajar (hari ini vs kemarin) tampil dengan benar');
    assert(analytics.hasCategoryDist, 'Widget Visualisasi Distribusi Rumpun Mapel (5 kategori) tampil');

    console.log('\n--- 3. Uji Empty State untuk User Baru (Data Kosong) ---');
    await page.evaluate(() => {
      localStorage.removeItem('tka_progress');
      if (typeof renderAll === 'function') renderAll(true);
    });
    await page.waitForTimeout(300);

    const emptyState = await page.evaluate(() => {
      const kpi = document.getElementById('mobile-kpi-container');
      const text = kpi ? kpi.textContent : '';
      const ctaBtn = kpi ? kpi.querySelector('button') : null;
      return {
        hasHeadline: text.includes('Belum Ada Riwayat Belajar'),
        hasCTA: !!ctaBtn && ctaBtn.textContent.includes('Mulai Latihan Paket 1')
      };
    });

    assert(emptyState.hasHeadline, 'Empty state menampilkan headline "Belum Ada Riwayat Belajar" saat data kosong');
    assert(emptyState.hasCTA, 'Empty state memiliki tombol CTA "Mulai Latihan Paket 1" yang jelas');

    console.log('\n--- 4. Uji Top Bar & Bottom Nav Konsistensi ---');
    const navCheck = await page.evaluate(() => {
      const topBar = document.querySelector('#progresMobile header');
      const btmNav = document.querySelector('#progresMobile nav');
      const btmRow = btmNav ? btmNav.querySelector('div') : null;
      return {
        hasTitle: topBar ? topBar.textContent.includes('TKA Master') : false,
        hasAvatar: topBar ? !!topBar.querySelector('button[aria-label="Buka Akun"]') : false,
        btmHeight: btmRow ? Math.round(btmRow.getBoundingClientRect().height) : 0
      };
    });

    assert(navCheck.hasTitle && navCheck.hasAvatar, 'Top bar memiliki brand TKA Master dan avatar');
    assert(navCheck.btmHeight === 56, `Bottom nav height terstandarisasi 56px (actual: ${navCheck.btmHeight}px)`);

    console.log('\n--- 5. Console Error Check ---');
    assert(consoleErrors.length === 0, `0 error di console (actual: ${consoleErrors.length})`);
    if (consoleErrors.length > 0) {
      console.error('Console errors:', consoleErrors);
    }

    await context.close();

    console.log('\n--- 6. Ambil Screenshot Berbagai Resolusi ---');
    const viewports = [
      { name: 'mobile_360', width: 360, height: 740 },
      { name: 'mobile_390', width: 390, height: 844 },
      { name: 'mobile_412', width: 412, height: 915 },
      { name: 'desktop_1280', width: 1280, height: 800 }
    ];

    for (const vp of viewports) {
      const vctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
      const vpPage = await vctx.newPage();

      // Isi kembali data contoh agar screenshot menampilkan dashboard penuh
      await vpPage.goto(PROGRES_URL, { waitUntil: 'commit' });
      await vpPage.evaluate(data => {
        localStorage.setItem('tka_progress', JSON.stringify(data));
        localStorage.setItem('tka_study_streak', '3');
      }, sampleData);

      await vpPage.goto(PROGRES_URL, { waitUntil: 'domcontentloaded' });
      await vpPage.waitForTimeout(500);

      const shotPath = path.join(SCREENSHOT_DIR, `${vp.name}.png`);
      await vpPage.screenshot({ path: shotPath });
      console.log(`  Saved screenshot: ${shotPath}`);

      if (vp.name === 'mobile_390') {
        // Screenshot juga tampilan empty state
        await vpPage.evaluate(() => {
          localStorage.removeItem('tka_progress');
          if (typeof renderAll === 'function') renderAll(true);
        });
        await vpPage.waitForTimeout(400);
        await vpPage.screenshot({ path: path.join(SCREENSHOT_DIR, 'mobile_390_empty_state.png') });
        console.log('  Saved mobile_390 empty state screenshot');
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
  console.log(`FASE 9 RESULT: ${passCount}/${testCount} PASS (${totalErrors} errors)`);
  console.log(`========================================\n`);

  if (totalErrors > 0) {
    process.exit(1);
  }
}

runTest();
