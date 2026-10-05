// scratch/_tes_fase14.js
// Verifikasi Fase 14: Kontrol Ukuran Teks Mobile (90%, 100%, 115%, 130%)
// Titik akses: (1) Menu overflow (⋮) & AI header, (2) Baris pengaturan menu Akun

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
    await page.waitForTimeout(800);
    await page.evaluate(() => {
      try { localStorage.removeItem('tka_font_scale'); } catch (e) {}
      if (typeof setTextScale === 'function') setTextScale(100);
      if (typeof homeClose === 'function') homeClose();
      const ov = document.getElementById('homeOverlay');
      if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
    });
    await page.waitForTimeout(400);

    // 1. Verifikasi Default Scale: 100%
    const initialInfo = await page.evaluate(() => {
      const qText = document.querySelector('.question-text') || document.querySelector('.qcard-body');
      const optText = document.querySelector('.cbt-opt-text');
      const attr = document.documentElement.getAttribute('data-text-scale');
      const ind = document.getElementById('scaleIndicator')?.textContent;

      return {
        attr,
        indicator: ind,
        qFontSize: qText ? parseFloat(getComputedStyle(qText).fontSize) : null,
        optFontSize: optText ? parseFloat(getComputedStyle(optText).fontSize) : null
      };
    });

    report(`${vp.name}: Skala awal default 100% dengan font-size terkalibrasi`,
      initialInfo.attr === '100' && initialInfo.indicator === '100%' && initialInfo.qFontSize >= 14,
      JSON.stringify(initialInfo)
    );

    // 2. Akses Titik (1): Buka menu overflow (⋮) dan ubah ukuran teks ke 115% dan 130%
    await page.click('#btnMobileOverflow');
    await page.waitForTimeout(300);

    // Klik tombol A+ (100% -> 115%)
    await page.click('#btnScaleInc');
    await page.waitForTimeout(300);

    const scale115Info = await page.evaluate(() => {
      const qText = document.querySelector('.question-text') || document.querySelector('.qcard-body');
      const attr = document.documentElement.getAttribute('data-text-scale');
      const ind = document.getElementById('scaleIndicator')?.textContent;
      const saved = localStorage.getItem('tka_font_scale');
      return {
        attr,
        indicator: ind,
        saved,
        fontSize: qText ? parseFloat(getComputedStyle(qText).fontSize) : null
      };
    });

    report(`${vp.name}: Tombol A+ menaikkan skala ke 115% dan tersimpan di localStorage`,
      scale115Info.attr === '115' && scale115Info.indicator === '115%' && scale115Info.saved === '115' &&
      scale115Info.fontSize > initialInfo.qFontSize,
      JSON.stringify(scale115Info)
    );

    // Klik tombol A+ lagi (115% -> 130%)
    await page.click('#btnScaleInc');
    await page.waitForTimeout(300);

    const scale130Info = await page.evaluate(() => {
      const qText = document.querySelector('.question-text') || document.querySelector('.qcard-body');
      const optText = document.querySelector('.cbt-opt-text');
      const attr = document.documentElement.getAttribute('data-text-scale');
      const ind = document.getElementById('scaleIndicator')?.textContent;
      const saved = localStorage.getItem('tka_font_scale');
      const incDisabled = document.getElementById('btnScaleInc')?.disabled;

      // Cek overflow horizontal pada window
      const winW = window.innerWidth;
      const scrollW = document.documentElement.scrollWidth;
      const bodyScrollW = document.body.scrollWidth;
      const hasHorizontalOverflow = scrollW > winW + 1 || bodyScrollW > winW + 1;

      // Cek tinggi bar
      const header = document.querySelector('.app-header');
      const headerHeight = header ? header.getBoundingClientRect().height : 0;

      return {
        attr,
        indicator: ind,
        saved,
        incDisabled,
        fontSize: qText ? parseFloat(getComputedStyle(qText).fontSize) : null,
        optFontSize: optText ? parseFloat(getComputedStyle(optText).fontSize) : null,
        hasHorizontalOverflow,
        scrollW,
        winW,
        headerHeight: Math.round(headerHeight)
      };
    });

    report(`${vp.name}: Pada skala maksimal 130%: font membesar, A+ disabled, 0 horizontal overflow`,
      scale130Info.attr === '130' && scale130Info.indicator === '130%' &&
      scale130Info.incDisabled === true &&
      !scale130Info.hasHorizontalOverflow &&
      scale130Info.fontSize >= initialInfo.qFontSize * 1.25,
      JSON.stringify(scale130Info)
    );

    // Tangkap screenshot soal pada 130%
    await page.screenshot({ path: `exports/fase14_soal_130pct_${vp.name}.png` });

    // 3. Verifikasi Tampilan AI Tutor menerima skala teks dari menu overflow/global
    await page.evaluate(() => {
      if (typeof openTutorSheet === 'function') openTutorSheet();
      else if (typeof switchWorkTab === 'function') switchWorkTab('pembahasan', 'ai');
    });
    await page.waitForTimeout(400);

    const tutorCheck = await page.evaluate(() => {
      const bubble = document.querySelector('.chat-bubble .bubble-content') || document.querySelector('.chat-bubble .ai-p') || document.querySelector('.chat-bubble');
      const attr = document.documentElement.getAttribute('data-text-scale');
      const hasIntrusiveScaleBtn = !!document.getElementById('btnTutorScale');
      return {
        attr,
        hasIntrusiveScaleBtn,
        fontSize: bubble ? parseFloat(getComputedStyle(bubble).fontSize) : null
      };
    });

    report(`${vp.name}: Tampilan AI Tutor menerima skala teks 130% dan header AI bersih (tanpa tombol pengganggu)`,
      tutorCheck.attr === '130' && !tutorCheck.hasIntrusiveScaleBtn && tutorCheck.fontSize >= 15,
      JSON.stringify(tutorCheck)
    );

    // Tangkap screenshot AI pada 130%
    await page.screenshot({ path: `exports/fase14_ai_130pct_${vp.name}.png` });

    // Restorasi skala ke 100% via setTextScale
    await page.evaluate(() => {
      if (typeof setTextScale === 'function') setTextScale(100);
      if (typeof closeTutorSheet === 'function') closeTutorSheet();
    });
    await page.waitForTimeout(300);

    // 4. Verifikasi Persistensi setelah Reload Halaman
    await page.evaluate(() => {
      setTextScale(115);
    });
    await page.waitForTimeout(200);

    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1000);
    await page.evaluate(() => {
      if (typeof homeClose === 'function') homeClose();
      const ov = document.getElementById('homeOverlay');
      if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
    });
    await page.waitForTimeout(300);

    const restoredScale = await page.evaluate(() => {
      return {
        attr: document.documentElement.getAttribute('data-text-scale'),
        saved: localStorage.getItem('tka_font_scale'),
        indicator: document.getElementById('scaleIndicator')?.textContent
      };
    });

    report(`${vp.name}: Skala font persisten setelah reload halaman (115%)`,
      restoredScale.attr === '115' && restoredScale.saved === '115' && restoredScale.indicator === '115%',
      JSON.stringify(restoredScale)
    );

    // 5. Verifikasi Titik Akses (2): Menu Akun (buka panel Akun dan verifikasi row pengaturan)
    await page.evaluate(() => {
      if (typeof homeOpenPanel === 'function') homeOpenPanel('akun');
      else if (typeof homeShowPanel === 'function') homeShowPanel('akun');
      const ov = document.getElementById('homeOverlay');
      if (ov) { ov.classList.remove('home-hidden'); ov.style.display = 'flex'; }
    });
    await page.waitForTimeout(600);

    const akunFrameCheck = await page.evaluate(async () => {
      const iframe = document.getElementById('panelAkunFrame');
      if (!iframe || !iframe.contentDocument) return null;
      const iDoc = iframe.contentDocument;
      const indicator = iDoc.getElementById('akunScaleIndicator');
      const textScaleAttr = iDoc.documentElement.getAttribute('data-text-scale');

      // Cek apakah tombol stepper ada
      const btnDec = iDoc.getElementById('btnAkunScaleDec');
      const btnInc = iDoc.getElementById('btnAkunScaleInc');

      return {
        hasIframe: true,
        textScaleAttr,
        indicatorText: indicator ? indicator.textContent : null,
        hasBtns: !!(btnDec && btnInc)
      };
    });

    report(`${vp.name}: Menu Akun memiliki row pengaturan ukuran teks dan tersinkronisasi`,
      akunFrameCheck && akunFrameCheck.hasIframe &&
      akunFrameCheck.textScaleAttr === '115' &&
      akunFrameCheck.indicatorText === '115%' &&
      akunFrameCheck.hasBtns,
      JSON.stringify(akunFrameCheck)
    );

    // Screenshot panel akun
    await page.screenshot({ path: `exports/fase14_akun_${vp.name}.png` });

    await context.close();
  }

  // 6. Desktop 1280px: Verifikasi skala teks HANYA aktif di mobile, desktop tetap tidak terpengaruh
  const deskContext = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const deskPage = await deskContext.newPage();
  await deskPage.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  await deskPage.waitForTimeout(1000);
  await deskPage.evaluate(() => {
    if (typeof homeClose === 'function') homeClose();
    const ov = document.getElementById('homeOverlay');
    if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
    // Coba set skala 130% di root
    setTextScale(130);
  });
  await deskPage.waitForTimeout(400);

  const deskCheck = await deskPage.evaluate(() => {
    const qText = document.querySelector('.question-text') || document.querySelector('.qcard-body');
    const cs = getComputedStyle(document.documentElement);
    // Di desktop, font-size html harus 16px murni (karena rule @media max-width 899px tidak berlaku)
    const htmlFontSize = parseFloat(cs.fontSize);

    return {
      htmlFontSize,
      desktopUnchanged: htmlFontSize === 16
    };
  });

  report('Desktop 1280px: Pengaturan skala teks mobile tidak mengubah font-size root desktop (tetap 16px)',
    deskCheck && deskCheck.desktopUnchanged,
    JSON.stringify(deskCheck)
  );

  await deskPage.screenshot({ path: 'exports/fase14_desktop_1280.png' });
  await deskContext.close();

  await browser.close();

  console.log(`\n=== FASE 14: ${passedChecks}/${totalChecks} PASS ===`);
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
