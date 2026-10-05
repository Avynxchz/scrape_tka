// scratch/_diagnosa_teks_vertikal.js
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true
  });
  const page = await context.newPage();

  console.log('--- 1. Buka App & Diagnosa Halaman Soal ---');
  await page.goto('http://127.0.0.1:8080/app?subject=geografi&paket=1', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // Close overlay jika ada
  await page.evaluate(() => {
    if (typeof homeClose === 'function') homeClose();
    const ov = document.getElementById('homeOverlay');
    if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
  });
  await page.waitForTimeout(500);

  // 1. Diagnosa Header Soal
  const headerDiag = await page.evaluate(() => {
    const header = document.querySelector('.app-header');
    const qnum = document.querySelector('.m-qnum');
    const qnumB = document.querySelector('.m-qnum b');
    const qnumSpan = document.querySelector('.m-qnum span');
    const timer = document.querySelector('.timer-box');
    return {
      headerW: header ? header.clientWidth : 0,
      qnumW: qnum ? qnum.clientWidth : 0,
      qnumBW: qnumB ? qnumB.clientWidth : 0,
      qnumText: qnumB ? qnumB.textContent : '',
      timerW: timer ? timer.clientWidth : 0
    };
  });
  console.log('Header Soal Diag:', headerDiag);

  // 2. Diagnosa Modal Reviu Hasil Simulasi
  console.log('\n--- 2. Diagnosa Reviu Hasil Simulasi Table ---');
  await page.evaluate(() => {
    // Isi jawaban tiruan dan buka finish modal lalu reviu
    if (typeof finishExam === 'function') {
      finishExam();
    } else if (typeof openReviewHasil === 'function') {
      openReviewHasil();
    }
  });
  await page.waitForTimeout(600);

  // Cek apakah #reviewHasilOverlay terbuka
  const reviewDiag = await page.evaluate(() => {
    const ov = document.getElementById('reviewHasilOverlay');
    if (!ov) return { found: false };
    const isOpen = ov.classList.contains('active') || ov.style.display !== 'none';
    const table = document.querySelector('.review-table');
    const wrap = document.querySelector('.review-table-wrap');
    if (!table) return { found: true, isOpen, table: false };

    const ths = Array.from(table.querySelectorAll('thead th')).map(th => ({
      text: th.textContent.trim(),
      width: Math.round(th.getBoundingClientRect().width)
    }));

    const firstRowTds = Array.from(table.querySelectorAll('tbody tr:first-child td')).map(td => ({
      text: td.textContent.trim().substring(0, 30),
      width: Math.round(td.getBoundingClientRect().width),
      height: Math.round(td.getBoundingClientRect().height)
    }));

    return {
      found: true,
      isOpen,
      wrapW: wrap ? wrap.clientWidth : 0,
      wrapScrollW: wrap ? wrap.scrollWidth : 0,
      tableW: table.clientWidth,
      ths,
      firstRowTds
    };
  });
  console.log('Review Table Diag:', JSON.stringify(reviewDiag, null, 2));

  // Ambil screenshot review modal
  await page.screenshot({ path: 'scratch/diag_review_modal_390.png' });

  // 3. Diagnosa Beranda Kartu Mapel (khususnya jika ada nama panjang)
  console.log('\n--- 3. Diagnosa Beranda Mapel Cards ---');
  await page.evaluate(() => {
    // Pilih mapel panjang: PPKn, Kewirausahaan, B. Indo Lanjut, Matematika Lanjut
    localStorage.setItem('tka_user_subjects', JSON.stringify(['ppkn', 'kewirausahaan', 'bahasa_indonesia_lanjut', 'matematika_lanjut']));
    if (typeof homeOpen === 'function') homeOpen();
    if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
    const ov = document.getElementById('homeOverlay');
    if (ov) { ov.classList.remove('home-hidden'); ov.style.display = 'flex'; }
  });
  await page.waitForTimeout(600);

  const berandaDiag = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('.stitch-card')).map(c => {
      const h3 = c.querySelector('h3');
      const meta = c.querySelector('.stitch-meta');
      const chip = c.querySelector('.stitch-chip');
      const prog = c.querySelector('.stitch-progress-labels');
      return {
        cardW: c.clientWidth,
        h3: h3 ? h3.textContent : '',
        meta: meta ? meta.textContent.trim() : '',
        chip: chip ? chip.textContent.trim() : '',
        chipW: chip ? Math.round(chip.getBoundingClientRect().width) : 0,
        progText: prog ? prog.textContent.trim() : ''
      };
    });

    const secTitles = Array.from(document.querySelectorAll('.stitch-sec-title')).map(s => {
      const h2 = s.querySelector('h2');
      const sub = s.querySelector('.stitch-sec-sub');
      return {
        h2: h2 ? h2.textContent.trim() : '',
        h2W: h2 ? Math.round(h2.getBoundingClientRect().width) : 0,
        h2H: h2 ? Math.round(h2.getBoundingClientRect().height) : 0,
        sub: sub ? sub.textContent.trim() : ''
      };
    });

    return { secTitles, cards: cards.slice(0, 4) };
  });
  console.log('Beranda Diag:', JSON.stringify(berandaDiag, null, 2));
  await page.screenshot({ path: 'scratch/diag_beranda_390.png' });

  // 4. Diagnosa Panel Modul
  console.log('\n--- 4. Diagnosa Panel Modul ---');
  await page.evaluate(() => {
    if (typeof homeShowPanel === 'function') homeShowPanel('modul');
  });
  await page.waitForTimeout(600);

  const modulDiag = await page.evaluate(async () => {
    const iframe = document.getElementById('panelModulFrame');
    if (!iframe || !iframe.contentDocument) return { err: 'no iframe' };
    const doc = iframe.contentDocument;

    const cards = Array.from(doc.querySelectorAll('[data-card]')).slice(0, 8).map(c => {
      const h3 = c.querySelector('h3');
      const badges = Array.from(c.querySelectorAll('span')).map(s => s.textContent.trim()).filter(Boolean);
      return {
        h3: h3 ? h3.textContent.trim() : '',
        h3W: h3 ? Math.round(h3.getBoundingClientRect().width) : 0,
        h3H: h3 ? Math.round(h3.getBoundingClientRect().height) : 0,
        badges
      };
    });

    const legend = Array.from(doc.querySelectorAll('#modulCombinedLegend > div')).map(el => ({
      text: el.textContent.trim(),
      w: Math.round(el.getBoundingClientRect().width),
      h: Math.round(el.getBoundingClientRect().height)
    }));

    return { cards, legend };
  });
  console.log('Modul Diag:', JSON.stringify(modulDiag, null, 2));
  await page.screenshot({ path: 'scratch/diag_modul_390.png' });

  // 5. Diagnosa Panel Progres
  console.log('\n--- 5. Diagnosa Panel Progres ---');
  await page.evaluate(() => {
    if (typeof homeShowPanel === 'function') homeShowPanel('progres');
  });
  await page.waitForTimeout(600);

  const progresDiag = await page.evaluate(() => {
    const iframe = document.getElementById('panelProgresFrame');
    if (!iframe || !iframe.contentDocument) return { err: 'no iframe' };
    const doc = iframe.contentDocument;

    const kpiItems = Array.from(doc.querySelectorAll('#mobile-kpi-container .flex, #mobile-kpi-container .grid > div')).map(el => ({
      text: el.textContent.trim().replace(/\s+/g, ' ').substring(0, 40),
      w: Math.round(el.getBoundingClientRect().width),
      h: Math.round(el.getBoundingClientRect().height)
    }));

    const activeCards = Array.from(doc.querySelectorAll('#mobile-active-subjects-list article, #mobile-unattempted-subjects-list > div')).slice(0, 6).map(el => {
      const h4 = el.querySelector('h4');
      const p = el.querySelector('p');
      return {
        h4: h4 ? h4.textContent.trim() : '',
        h4W: h4 ? Math.round(h4.getBoundingClientRect().width) : 0,
        p: p ? p.textContent.trim() : '',
        totalW: Math.round(el.getBoundingClientRect().width),
        totalH: Math.round(el.getBoundingClientRect().height)
      };
    });

    return { kpiItems: kpiItems.slice(0, 6), activeCards };
  });
  console.log('Progres Diag:', JSON.stringify(progresDiag, null, 2));
  await page.screenshot({ path: 'scratch/diag_progres_390.png' });

  await browser.close();
  console.log('\nDiagnosa selesai.');
})();
