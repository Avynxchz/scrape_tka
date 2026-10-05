// scratch/_tes_semua_kandidat.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  
  const viewports = [
    { name: '360px', width: 360, height: 740 },
    { name: '390px', width: 390, height: 844 },
    { name: '412px', width: 412, height: 915 },
    { name: '1280px', width: 1280, height: 800 }
  ];

  for (const vp of viewports) {
    console.log(`\n================ Testing ${vp.name} (${vp.width}x${vp.height}) ================`);
    const isMobile = vp.width < 900;
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      isMobile,
      hasTouch: isMobile
    });
    const page = await context.newPage();

    // 1. Tes Soal dengan mapel PPKn
    await page.goto(`http://127.0.0.1:8080/app?subject=ppkn&paket=1`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1000);

    // Close home overlay jika terbuka
    await page.evaluate(() => {
      const ov = document.getElementById('homeOverlay');
      if (ov) { ov.classList.add('home-hidden'); ov.style.display = 'none'; }
    });
    await page.waitForTimeout(400);

    // Cek Header Soal
    const headerInfo = await page.evaluate(() => {
      const qnum = document.querySelector('.m-qnum');
      const b = qnum ? qnum.querySelector('b') : null;
      const span = qnum ? qnum.querySelector('span') : null;
      const timer = document.querySelector('.timer-box');
      const header = document.querySelector('.app-header');
      return {
        headerW: header ? header.clientWidth : 0,
        qnumW: qnum ? qnum.clientWidth : 0,
        bText: b ? b.textContent : '',
        bW: b ? b.clientWidth : 0,
        bScrollW: b ? b.scrollWidth : 0,
        bH: b ? b.clientHeight : 0,
        spanText: span ? span.textContent : '',
        timerW: timer ? timer.clientWidth : 0
      };
    });
    console.log(`[${vp.name}] Header Soal:`, headerInfo);

    // Ambil screenshot header Soal
    await page.screenshot({ path: `scratch/header_soal_${vp.name}.png` });

    // Cek Modal Reviu Hasil Simulasi dengan jawaban panjang
    await page.evaluate(() => {
      // Buka langsung modal reviu dengan data simulasi yang memicu kolom panjang
      if (typeof handleOptionSelect === 'function') {
        handleOptionSelect('A');
      }
      if (typeof renderReviewHasil === 'function') {
        renderReviewHasil();
      }
    });
    await page.waitForTimeout(600);

    const reviewInfo = await page.evaluate(() => {
      const modal = document.getElementById('reviewHasilOverlay');
      if (!modal) return { open: false };
      const table = modal.querySelector('.review-table');
      const wrap = modal.querySelector('.review-table-wrap');
      const ths = Array.from(table ? table.querySelectorAll('thead th') : []).map(th => ({
        text: th.textContent.trim(),
        w: th.clientWidth,
        h: th.clientHeight
      }));
      const tds = Array.from(table ? table.querySelectorAll('tbody tr:first-child td') : []).map(td => ({
        text: td.textContent.trim().substring(0, 30),
        w: td.clientWidth,
        h: td.clientHeight
      }));
      return {
        open: modal.classList.contains('active') || modal.style.display === 'flex' || modal.clientHeight > 0,
        wrapW: wrap ? wrap.clientWidth : 0,
        wrapScrollW: wrap ? wrap.scrollWidth : 0,
        tableW: table ? table.clientWidth : 0,
        ths,
        tds
      };
    });
    console.log(`[${vp.name}] Review Modal:`, reviewInfo);
    await page.screenshot({ path: `scratch/review_modal_${vp.name}.png` });

    // Tutup review modal
    await page.evaluate(() => {
      const modal = document.getElementById('reviewHasilOverlay');
      if (modal) { modal.classList.remove('active'); modal.style.display = 'none'; }
    });

    // 2. Tes Beranda dengan Mapel Nama Panjang
    await page.evaluate(() => {
      localStorage.setItem('tka_user_subjects', JSON.stringify(['ppkn', 'kewirausahaan', 'bahasa_indonesia_lanjut', 'matematika_lanjut']));
      if (typeof homeOpen === 'function') homeOpen();
      if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
      const ov = document.getElementById('homeOverlay');
      if (ov) { ov.classList.remove('home-hidden'); ov.style.display = 'flex'; }
    });
    await page.waitForTimeout(600);

    const berandaInfo = await page.evaluate(() => {
      const titles = Array.from(document.querySelectorAll('.stitch-sec-title')).map(t => {
        const h2 = t.querySelector('h2');
        const sub = t.querySelector('.stitch-sec-sub');
        return {
          h2: h2 ? h2.textContent.trim() : '',
          h2W: h2 ? h2.clientWidth : 0,
          h2H: h2 ? h2.clientHeight : 0,
          sub: sub ? sub.textContent.trim() : ''
        };
      });
      const cards = Array.from(document.querySelectorAll('.stitch-card')).slice(0, 4).map(c => {
        const meta = c.querySelector('.stitch-meta');
        const chip = c.querySelector('.stitch-chip');
        const labels = c.querySelector('.stitch-progress-labels');
        return {
          w: c.clientWidth,
          meta: meta ? meta.textContent.trim() : '',
          chip: chip ? chip.textContent.trim() : '',
          labels: labels ? labels.textContent.trim() : ''
        };
      });
      return { titles, cards };
    });
    console.log(`[${vp.name}] Beranda Info:`, berandaInfo);
    await page.screenshot({ path: `scratch/beranda_${vp.name}.png` });

    // 3. Tes Carousel Slide 1, 2, 3
    const carouselInfo = await page.evaluate(() => {
      const slides = Array.from(document.querySelectorAll('.stitch-hero')).map((s, idx) => {
        const h2 = s.querySelector('h2');
        const p = s.querySelector('p');
        return {
          slide: idx + 1,
          h2: h2 ? h2.textContent.trim() : '',
          h2H: h2 ? h2.clientHeight : 0,
          p: p ? p.textContent.trim() : ''
        };
      });
      return slides;
    });
    console.log(`[${vp.name}] Carousel Slides:`, carouselInfo);

    await context.close();
  }

  await browser.close();
  console.log('\nSemua tes kandidat selesai dijalankan!');
})();
