/**
 * Tes FASE 4: Navigasi Mengambang (work-rail / 3 tombol bawah) bisa dipindah
 * Fitur:
 * 1. 3 tombol Soal, Pembahasan, Tanya AI ada di #workRail.
 * 2. Long-press 400ms -> .rail-dragging -> drag -> snap.
 * 3. Tersimpan di localStorage ('tka_work_rail_snap') & restore saat reload.
 * 4. Tetap tampil saat AI chat dibuka (z-index 75 di atas sheet 70).
 * 5. Tap biasa tidak memicu drag.
 */
const { chromium } = require('./node_modules/playwright-core');
const BASE = 'http://127.0.0.1:8080';
const R = [];

function report(name, pass, extra) {
  R.push([name, pass]);
  console.log(`${pass ? 'PASS' : 'FAIL'} | ${name}${extra ? ' -> ' + extra : ''}`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });

  /* ===== MOBILE 390 ===== */
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
  await m.waitForTimeout(2000);
  await m.evaluate(() => {
    if (typeof homeClose === 'function') homeClose();
    const ov = document.getElementById('homeOverlay');
    if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
  });
  await m.waitForTimeout(500);

  // 1) Identifikasi 3 tombol mengambang
  const buttonsInfo = await m.evaluate(() => {
    const rail = document.getElementById('workRail');
    if (!rail) return null;
    const btns = Array.from(rail.querySelectorAll('.rail-btn')).map(b => b.textContent.trim());
    const cs = getComputedStyle(rail);
    return {
      visible: cs.display !== 'none',
      buttons: btns,
      zIndex: parseInt(cs.zIndex, 10),
      className: rail.className
    };
  });
  report('Mobile: 3 tombol mengambang (Soal, Pembahasan, Tanya AI) terdeteksi',
    buttonsInfo && buttonsInfo.visible && buttonsInfo.buttons.includes('Soal') && buttonsInfo.buttons.includes('Pembahasan') && buttonsInfo.buttons.includes('Tanya AI'),
    JSON.stringify(buttonsInfo)
  );
  report('Mobile: workRail z-index >= 75 (di atas sheet chat 70)',
    buttonsInfo && buttonsInfo.zIndex >= 75,
    `zIndex: ${buttonsInfo ? buttonsInfo.zIndex : 'null'}`
  );

  // 2) Tap cepat (< 200ms) tidak memicu dragging
  const railBox = await m.evaluate(() => {
    const r = document.getElementById('workRail').getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  await m.mouse.click(railBox.x, railBox.y);
  await m.waitForTimeout(200);
  const isDraggingAfterTap = await m.evaluate(() => document.getElementById('workRail').classList.contains('rail-dragging'));
  report('Mobile: Tap cepat tidak memicu drag mode', !isDraggingAfterTap);

  // 3) Long-press & Drag ke kiri tengah
  await m.mouse.move(railBox.x, railBox.y);
  await m.mouse.down();
  // Tunggu durasi long-press (> 400ms)
  await m.waitForTimeout(450);
  const isDraggingDuringHold = await m.evaluate(() => document.getElementById('workRail').classList.contains('rail-dragging'));
  report('Mobile: Long-press 400ms mengaktifkan mode geser (.rail-dragging)', isDraggingDuringHold);

  // Geser pointer ke area kiri-tengah (x=30, y=420)
  await m.mouse.move(30, 420, { steps: 5 });
  await m.waitForTimeout(100);
  await m.mouse.up();
  await m.waitForTimeout(400);

  const snappedPos = await m.evaluate(() => {
    const rail = document.getElementById('workRail');
    const classes = Array.from(rail.classList);
    const snapClass = classes.find(c => c.startsWith('snap-'));
    const saved = localStorage.getItem('tka_work_rail_snap');
    const rect = rail.getBoundingClientRect();
    return { snapClass, saved, left: rect.left, top: rect.top };
  });
  report('Mobile: Snap ke kiri terdekat dan tersimpan di localStorage',
    snappedPos.snapClass && snappedPos.snapClass.includes('left') && snappedPos.saved === snappedPos.snapClass,
    JSON.stringify(snappedPos)
  );

  // 4) Reload halaman dan verifikasi posisi dipulihkan
  await m.reload({ waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
  await m.waitForTimeout(2000);
  await m.evaluate(() => {
    if (typeof homeClose === 'function') homeClose();
    const ov = document.getElementById('homeOverlay');
    if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
  });
  await m.waitForTimeout(500);

  const restoredPos = await m.evaluate(() => {
    const rail = document.getElementById('workRail');
    const classes = Array.from(rail.classList);
    return classes.find(c => c.startsWith('snap-'));
  });
  report('Mobile: Posisi dipulihkan dari localStorage saat reload',
    restoredPos === snappedPos.snapClass,
    `restored: ${restoredPos}, expected: ${snappedPos.snapClass}`
  );

  // 5) Buka AI Chat -> workRail tetap tampil di atas sheet
  await m.evaluate(() => {
    if (typeof openTutorSheet === 'function') openTutorSheet();
  });
  await m.waitForTimeout(600);

  const aiChatState = await m.evaluate(() => {
    const sheet = document.getElementById('cbtSidebarCol');
    const rail = document.getElementById('workRail');
    const sRect = sheet.getBoundingClientRect();
    const rRect = rail.getBoundingClientRect();
    const sZ = parseInt(getComputedStyle(sheet).zIndex, 10);
    const rZ = parseInt(getComputedStyle(rail).zIndex, 10);
    return {
      sheetOpen: sheet.classList.contains('tutor-open'),
      railVisible: getComputedStyle(rail).display !== 'none',
      sheetZ: sZ,
      railZ: rZ,
      railHigher: rZ > sZ
    };
  });
  report('Mobile: workRail tetap tampil di atas AI Chat (railZ > sheetZ)',
    aiChatState.sheetOpen && aiChatState.railVisible && aiChatState.railHigher,
    JSON.stringify(aiChatState)
  );

  await m.screenshot({ path: 'exports/f4_mobile_chat_rail.png' });
  await m.close();

  /* ===== DESKTOP 1280 ===== */
  const d = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await d.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
  await d.waitForTimeout(2000);
  await d.evaluate(() => {
    if (typeof homeClose === 'function') homeClose();
    const ov = document.getElementById('homeOverlay');
    if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
  });
  await d.waitForTimeout(500);

  const dRailState = await d.evaluate(() => {
    const rail = document.getElementById('workRail');
    const cs = getComputedStyle(rail);
    return {
      display: cs.display,
      position: cs.position
    };
  });
  report('Desktop: workRail tampil aman di desktop (fixed / flex)',
    dRailState.display === 'flex' && dRailState.position === 'fixed',
    JSON.stringify(dRailState)
  );

  await d.screenshot({ path: 'exports/f4_desktop_rail.png' });
  await d.close();

  await browser.close();
  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== FASE 4: ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL FASE 4:', e); process.exit(1); });
