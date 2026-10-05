// scratch/_tes_fase13.js
// Verifikasi Fase 13: Floating Navigation Rail Auto-Minimize, Expand on Tap, 4s Auto-Collapse, & Drag

const { chromium } = require('playwright');
const fs = require('fs');

const BASE_URL = 'http://127.0.0.1:8080/app?subject=matematika&paket=1';

const VIEWPORTS = [
  { name: '360px', width: 360, height: 640 },
  { name: '390px', width: 390, height: 844 },
  { name: '412px', width: 412, height: 915 }
];

async function runTests() {
  const browser = await chromium.launch({ headless: true });
  let totalChecks = 0;
  let passedChecks = 0;
  let allConsoleErrors = [];

  function report(name, pass, detail) {
    totalChecks++;
    if (pass) {
      passedChecks++;
      console.log(`PASS | ${name} -> ${detail}`);
    } else {
      console.error(`FAIL | ${name} -> ${detail}`);
    }
  }

  for (const vp of VIEWPORTS) {
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      isMobile: true,
      hasTouch: true
    });
    const page = await context.newPage();

    page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        if (!text.includes('Failed to load resource') && !text.includes('favicon')) {
          allConsoleErrors.push(`[${vp.name}] ${text}`);
        }
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1000);
    await page.evaluate(() => {
      if (typeof homeClose === 'function') homeClose();
      const ov = document.getElementById('homeOverlay');
      if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
    });
    await page.waitForTimeout(400);

    // 1. Kondisi Normal: Tombol Navigasi Mengambang Ter-minimize
    const normalState = await page.evaluate(() => {
      const rail = document.getElementById('workRail');
      if (!rail) return null;
      const rect = rail.getBoundingClientRect();
      const style = getComputedStyle(rail);
      const activeBtn = rail.querySelector('.rail-btn.active');
      const allBtns = Array.from(rail.querySelectorAll('.rail-btn'));
      const visibleBtns = allBtns.filter(b => getComputedStyle(b).display !== 'none');
      const activeBtnRect = activeBtn ? activeBtn.getBoundingClientRect() : null;
      const activeBtnSpan = activeBtn ? activeBtn.querySelector('span') : null;
      const spanDisplay = activeBtnSpan ? getComputedStyle(activeBtnSpan).display : null;

      return {
        hasRail: true,
        isMinimized: rail.classList.contains('is-minimized'),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        opacity: parseFloat(style.opacity),
        visibleBtnsCount: visibleBtns.length,
        spanHidden: spanDisplay === 'none',
        borderRadius: style.borderRadius,
        activeIcon: activeBtn ? (activeBtn.querySelector('i')?.className || '') : ''
      };
    });

    report(`${vp.name}: Kondisi normal rail berupa 1 tombol kecil (36-44px, transparan, teks tersembunyi)`,
      normalState && normalState.isMinimized &&
      normalState.width >= 36 && normalState.width <= 44 &&
      normalState.height >= 36 && normalState.height <= 44 &&
      normalState.visibleBtnsCount === 1 &&
      normalState.spanHidden &&
      normalState.opacity < 1.0,
      JSON.stringify(normalState)
    );

    await page.screenshot({ path: `exports/fase13_minimized_${vp.name}.png` });

    // 2. Tap Tombol Kecil -> Mengembang Menampilkan 3 Tombol (Soal, Pembahasan, Tanya AI)
    await page.tap('#workRail');
    await page.waitForTimeout(350);

    const expandedState = await page.evaluate(() => {
      const rail = document.getElementById('workRail');
      if (!rail) return null;
      const rect = rail.getBoundingClientRect();
      const style = getComputedStyle(rail);
      const allBtns = Array.from(rail.querySelectorAll('.rail-btn'));
      const visibleBtns = allBtns.filter(b => getComputedStyle(b).display !== 'none');
      const btnLabels = visibleBtns.map(b => b.querySelector('span')?.textContent?.trim());

      return {
        isExpanded: rail.classList.contains('is-expanded'),
        isNotMinimized: !rail.classList.contains('is-minimized'),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        opacity: parseFloat(style.opacity),
        visibleBtnsCount: visibleBtns.length,
        btnLabels
      };
    });

    report(`${vp.name}: Tap tombol mini mengembang menampilkan 3 tombol lengkap`,
      expandedState && expandedState.isExpanded &&
      expandedState.visibleBtnsCount === 3 &&
      expandedState.btnLabels.includes('Soal') &&
      expandedState.btnLabels.includes('Pembahasan') &&
      expandedState.btnLabels.includes('Tanya AI'),
      JSON.stringify(expandedState)
    );

    await page.screenshot({ path: `exports/fase13_expanded_${vp.name}.png` });

    // 3. Verifikasi Diam 4 Detik Tanpa Interaksi -> Otomatis Mengecil Lagi
    // Kita tunggu 4.3 detik
    await page.waitForTimeout(4300);

    const autoCollapsedState = await page.evaluate(() => {
      const rail = document.getElementById('workRail');
      if (!rail) return null;
      const rect = rail.getBoundingClientRect();
      const allBtns = Array.from(rail.querySelectorAll('.rail-btn'));
      const visibleBtns = allBtns.filter(b => getComputedStyle(b).display !== 'none');

      return {
        isMinimized: rail.classList.contains('is-minimized'),
        isNotExpanded: !rail.classList.contains('is-expanded'),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        visibleBtnsCount: visibleBtns.length
      };
    });

    report(`${vp.name}: Diam ~4 detik tanpa interaksi otomatis mengecil lagi`,
      autoCollapsedState && autoCollapsedState.isMinimized &&
      autoCollapsedState.visibleBtnsCount === 1 &&
      autoCollapsedState.width >= 36 && autoCollapsedState.width <= 44,
      JSON.stringify(autoCollapsedState)
    );

    // 4. Pilih Salah Satu Tombol Saat Mengembang -> Tab Berpindah & Langsung Mengecil
    await page.tap('#workRail'); // Expand lagi
    await page.waitForTimeout(300);

    // Tap tombol 'Pembahasan'
    await page.tap('#workRail .rail-btn[data-rail="materi"]');
    await page.waitForTimeout(400);

    const switchedTabState = await page.evaluate(() => {
      const rail = document.getElementById('workRail');
      const pembPane = document.getElementById('workPanePembahasan');
      const activeBtn = rail ? rail.querySelector('.rail-btn.active') : null;
      const rect = rail ? rail.getBoundingClientRect() : null;

      return {
        pembActive: pembPane ? pembPane.classList.contains('active') : false,
        activeRailData: activeBtn ? activeBtn.getAttribute('data-rail') : null,
        isMinimizedAfterSwitch: rail ? rail.classList.contains('is-minimized') : false,
        railWidth: rect ? Math.round(rect.width) : 0
      };
    });

    report(`${vp.name}: Memilih salah satu tombol berpindah tab dan otomatis mengecil`,
      switchedTabState && switchedTabState.pembActive &&
      switchedTabState.activeRailData === 'materi' &&
      switchedTabState.isMinimizedAfterSwitch,
      JSON.stringify(switchedTabState)
    );

    // Kembalikan ke tab Soal
    await page.tap('#workRail');
    await page.waitForTimeout(300);
    await page.tap('#workRail .rail-btn[data-rail="soal"]');
    await page.waitForTimeout(400);

    // 5. Cek di Semua 6 Snap Posisi Saat Mengembang: Tiga Tombol Tidak Pernah Keluar Layar
    const snapChecks = await page.evaluate(async () => {
      const rail = document.getElementById('workRail');
      const POSITIONS = [
        'snap-top-left', 'snap-top-right',
        'snap-mid-left', 'snap-mid-right',
        'snap-bottom-left', 'snap-bottom-right'
      ];
      const winW = window.innerWidth;
      const winH = window.innerHeight;
      const results = [];

      for (const pos of POSITIONS) {
        POSITIONS.forEach(c => rail.classList.remove(c));
        rail.classList.add(pos);
        rail.classList.remove('is-minimized');
        rail.classList.add('is-expanded');

        // Force reflow
        rail.offsetHeight;

        const rect = rail.getBoundingClientRect();
        const inScreen = (
          rect.top >= 0 &&
          rect.bottom <= winH + 1 &&
          rect.left >= 0 &&
          rect.right <= winW + 1
        );

        results.push({
          pos,
          inScreen,
          bounds: { top: Math.round(rect.top), bottom: Math.round(rect.bottom), left: Math.round(rect.left), right: Math.round(rect.right) }
        });
      }

      // Kembalikan ke snap-bottom-right & minimized
      POSITIONS.forEach(c => rail.classList.remove(c));
      rail.classList.add('snap-bottom-right', 'is-minimized');
      rail.classList.remove('is-expanded');

      return results;
    });

    const allSnapsInScreen = snapChecks.every(r => r.inScreen);
    report(`${vp.name}: Tiga tombol tidak pernah keluar layar di seluruh 6 posisi snap`,
      allSnapsInScreen,
      `All 6 in screen: ${allSnapsInScreen}`
    );

    // 6. Tombol Kecil Tetap Tampil di Chat AI & Tidak Menutupi Input / Tombol Kirim
    await page.evaluate(() => {
      if (typeof openTutorSheet === 'function') openTutorSheet();
      else if (typeof switchWorkTab === 'function') switchWorkTab('pembahasan', 'ai');
    });
    await page.waitForTimeout(400);

    const aiViewCheck = await page.evaluate(() => {
      const rail = document.getElementById('workRail');
      const chatInput = document.getElementById('chatInput');
      const btnSend = document.getElementById('btnSendChat') || document.querySelector('.btn-send-chat');
      const tutorSheet = document.getElementById('cbtSidebarCol');

      if (!rail || !chatInput || !btnSend) return null;

      const railRect = rail.getBoundingClientRect();
      const inputRect = chatInput.getBoundingClientRect();
      const sendRect = btnSend.getBoundingClientRect();

      // Apakah rail menutupi chat input atau tombol kirim?
      const overlapsInput = !(
        railRect.right < inputRect.left ||
        railRect.left > inputRect.right ||
        railRect.bottom < inputRect.top ||
        railRect.top > inputRect.bottom
      );

      const overlapsSend = !(
        railRect.right < sendRect.left ||
        railRect.left > sendRect.right ||
        railRect.bottom < sendRect.top ||
        railRect.top > sendRect.bottom
      );

      return {
        railVisible: rail.style.display !== 'none' && getComputedStyle(rail).display !== 'none',
        isMinimized: rail.classList.contains('is-minimized'),
        activeIcon: rail.querySelector('.rail-btn.active i')?.className,
        overlapsInput,
        overlapsSend,
        railBottom: Math.round(railRect.bottom),
        inputTop: Math.round(inputRect.top),
        zIndex: parseInt(getComputedStyle(rail).zIndex || '0')
      };
    });

    report(`${vp.name}: Tombol mini tetap tampil di AI Tutor dan tidak menutupi input atau tombol kirim`,
      aiViewCheck && aiViewCheck.railVisible &&
      !aiViewCheck.overlapsInput && !aiViewCheck.overlapsSend &&
      aiViewCheck.zIndex >= 70,
      JSON.stringify(aiViewCheck)
    );

    await page.screenshot({ path: `exports/fase13_in_ai_${vp.name}.png` });

    // Tutup AI sheet
    await page.evaluate(() => {
      if (typeof closeTutorSheet === 'function') closeTutorSheet();
    });
    await page.waitForTimeout(300);

    // 7. Long-press Gestur Drag Masih Berfungsi & Menggeser Rail
    const dragResult = await page.evaluate(async () => {
      const rail = document.getElementById('workRail');
      const rect = rail.getBoundingClientRect();
      const startX = rect.left + rect.width / 2;
      const startY = rect.top + rect.height / 2;

      // Simulasi pointerdown
      rail.dispatchEvent(new PointerEvent('pointerdown', {
        clientX: startX,
        clientY: startY,
        button: 0,
        bubbles: true
      }));

      // Tunggu 420ms agar long-press 400ms terpicu
      await new Promise(r => setTimeout(r, 420));

      const isDraggingActive = rail.classList.contains('rail-dragging');

      // Geser pointer
      window.dispatchEvent(new PointerEvent('pointermove', {
        clientX: 50,
        clientY: 100,
        bubbles: true
      }));

      // Pointerup
      window.dispatchEvent(new PointerEvent('pointerup', {
        clientX: 50,
        clientY: 100,
        bubbles: true
      }));

      const finalClass = Array.from(rail.classList).find(c => c.startsWith('snap-'));
      return { isDraggingActive, finalClass };
    });

    report(`${vp.name}: Long-press >=400ms memicu drag dan snapping ke posisi target`,
      dragResult && dragResult.isDraggingActive && dragResult.finalClass === 'snap-top-left',
      JSON.stringify(dragResult)
    );

    await context.close();
  }

  // 8. Desktop 1280px: Work rail tetap layout desktop 3 tombol biasa (bukan tombol mini bulat)
  const deskContext = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const deskPage = await deskContext.newPage();
  await deskPage.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  await deskPage.waitForTimeout(1000);
  await deskPage.evaluate(() => {
    if (typeof homeClose === 'function') homeClose();
    const ov = document.getElementById('homeOverlay');
    if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
  });
  await deskPage.waitForTimeout(400);

  const deskRail = await deskPage.evaluate(() => {
    const rail = document.getElementById('workRail');
    if (!rail) return null;
    const rect = rail.getBoundingClientRect();
    const allBtns = Array.from(rail.querySelectorAll('.rail-btn'));
    const visibleBtns = allBtns.filter(b => getComputedStyle(b).display !== 'none');
    const spanVisible = Array.from(rail.querySelectorAll('.rail-btn span')).every(s => getComputedStyle(s).display !== 'none');

    return {
      display: getComputedStyle(rail).display,
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      visibleBtnsCount: visibleBtns.length,
      spanVisible,
      isCircle: getComputedStyle(rail).borderRadius === '50%'
    };
  });

  report('Desktop 1280px: Work rail tetap format sidebar desktop lengkap (3 tombol penuh, bukan bulat mini)',
    deskRail && deskRail.visibleBtnsCount === 3 && deskRail.spanVisible && !deskRail.isCircle,
    JSON.stringify(deskRail)
  );

  await deskPage.screenshot({ path: 'exports/fase13_desktop_1280.png' });
  await deskContext.close();

  await browser.close();

  console.log(`\n=== FASE 13: ${passedChecks}/${totalChecks} PASS ===`);
  console.log(`Console errors: ${allConsoleErrors.length} errors`);
  if (allConsoleErrors.length > 0) {
    console.error(allConsoleErrors.join('\n'));
    process.exit(1);
  }
  if (passedChecks < totalChecks) {
    process.exit(1);
  }
}

runTests().catch(err => {
  console.error('Test execution error:', err);
  process.exit(1);
});
