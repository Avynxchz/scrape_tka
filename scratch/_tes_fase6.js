/**
 * Tes FASE 6: Beranda - Performa & Desain Ulang Kartu Mapel.
 * 1. Performa render cepat (< 30ms) dengan pre-seeded static counts.
 * 2. Hanya mapel pilihan user yang tampil (default 4 mapel = 8 kartu).
 * 3. Tombol "Lihat Semua" dihapus (0 elemen).
 * 4. Desain ulang kartu: kontras tinggi, kartu Matematika warna biru bersih (bukan oranye/cokelat).
 * 5. Ikon unik 22 mapel: tidak ada duplikat ikon antar-mapel (Set size == 22).
 * 6. Nama panjang ditangani dengan nama singkat/akronim & line-clamp.
 * 7. Integrasi: ubah pilihan mapel via localStorage/modal langsung tercermin di Beranda.
 * 8. Screenshot mobile (360, 390, 412 px) & desktop (1280 px).
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
  const p = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const consoleErrors = [];
  p.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  p.on('pageerror', err => consoleErrors.push(err.message));

  await p.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded', timeout: 10000 }).catch(() => {});
  await p.waitForTimeout(1000);

  // 1) Pastikan Beranda terbuka
  await p.evaluate(() => {
    localStorage.removeItem('tka_user_subjects'); // reset ke default
    if (typeof homeOpen === 'function') homeOpen();
    if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
  });
  await p.waitForTimeout(500);

  // 2) Uji Ikon Unik 22 Mapel (harus 0 duplikat)
  const iconCheck = await p.evaluate(() => {
    const meta = window.SUBJECT_UI_META || {};
    const keys = Object.keys(meta);
    const icons = keys.map(k => meta[k].icon);
    const uniqueIcons = new Set(icons);
    return {
      totalKeys: keys.length,
      totalIcons: icons.length,
      uniqueCount: uniqueIcons.size,
      duplicates: icons.filter((item, index) => icons.indexOf(item) !== index)
    };
  });
  report('Semua 22 mapel memiliki ikon Material Symbols UNIK tanpa duplikat',
    iconCheck.totalKeys === 22 && iconCheck.uniqueCount === 22,
    `Total: ${iconCheck.totalKeys}, Unik: ${iconCheck.uniqueCount}, Duplikat: ${iconCheck.duplicates.join(', ') || 'Nihil'}`
  );

  // 3) Uji Performa: waktu eksekusi renderHome() & jumlah kartu default
  const perfInfo = await p.evaluate(() => {
    const t0 = performance.now();
    renderHome();
    const t1 = performance.now();
    const cards = document.querySelectorAll('.stitch-card');
    const sections = document.querySelectorAll('.stitch-section');
    return {
      durationMs: t1 - t0,
      cardCount: cards.length,
      sectionCount: sections.length
    };
  });
  report('Performa render kartu instan (< 30ms)',
    perfInfo.durationMs < 30,
    `${perfInfo.durationMs.toFixed(2)} ms`
  );
  report('Hanya mapel pilihan user yang tampil (default 4 mapel = 8 kartu)',
    perfInfo.cardCount === 8 && perfInfo.sectionCount === 4,
    `Cards: ${perfInfo.cardCount}, Sections: ${perfInfo.sectionCount}`
  );

  // 4) Uji tombol "Lihat Semua" DIHAPUS
  const seeAllCount = await p.evaluate(() => {
    return document.querySelectorAll('.stitch-seeall').length;
  });
  report('Tombol "Lihat Semua" dihapus dari Beranda',
    seeAllCount === 0,
    `Jumlah .stitch-seeall: ${seeAllCount}`
  );

  // 5) Uji Desain & Kontras Kartu Matematika
  const mtkCardInfo = await p.evaluate(() => {
    const card = document.querySelector('.stitch-card[data-subject="matematika"]');
    if (!card) return null;
    const chip = card.querySelector('.stitch-chip');
    const title = card.querySelector('h3');
    const meta = card.querySelector('.stitch-meta');
    const cardStyle = window.getComputedStyle(card);
    const chipStyle = window.getComputedStyle(chip);
    return {
      cardBg: cardStyle.backgroundColor,
      cardBorderRadius: cardStyle.borderRadius,
      chipBg: chipStyle.backgroundColor,
      chipColor: chipStyle.color,
      chipText: chip ? chip.innerText : '',
      titleText: title ? title.innerText : '',
      metaText: meta ? meta.innerText : ''
    };
  });
  const mtkIsBlueChip = mtkCardInfo && mtkCardInfo.chipColor.includes('29, 78, 216'); // rgb(29, 78, 216) = #1D4ED8
  report('Kartu Matematika: teks chip biru berani #1D4ED8 di atas latar biru muda (bukan cokelat kusam)',
    mtkIsBlueChip && mtkCardInfo.cardBg === 'rgb(255, 255, 255)',
    JSON.stringify(mtkCardInfo)
  );

  // 6) Uji nama singkat (PPKn) & penanganan nama panjang
  const ppknTest = await p.evaluate(() => {
    // set pilihan user hanya PPKn
    setUserSelectedSubjects(['ppkn']);
    const sec = document.querySelector('.stitch-section[data-subject="ppkn"]');
    const h2 = sec ? sec.querySelector('h2') : null;
    const chip = sec ? sec.querySelector('.stitch-chip') : null;
    return {
      h2Text: h2 ? h2.innerText : '',
      chipText: chip ? chip.innerText : '',
      sectionCount: document.querySelectorAll('.stitch-section').length
    };
  });
  report('Mapel nama panjang (PPKn) tampil dengan nama singkat/akronim rapi',
    ppknTest.h2Text === 'PPKn' && ppknTest.chipText === 'PPKN' && ppknTest.sectionCount === 1,
    JSON.stringify(ppknTest)
  );

  // Kembalikan pilihan ke default 4 mapel
  await p.evaluate(() => {
    localStorage.removeItem('tka_user_subjects');
    renderHome();
  });
  await p.waitForTimeout(300);

  // 7) Ambil screenshot di berbagai viewport mobile dan desktop
  await p.setViewportSize({ width: 360, height: 740 });
  await p.screenshot({ path: 'exports/f6_beranda_360.png' });

  await p.setViewportSize({ width: 390, height: 844 });
  await p.screenshot({ path: 'exports/f6_beranda_390.png' });

  await p.setViewportSize({ width: 412, height: 915 });
  await p.screenshot({ path: 'exports/f6_beranda_412.png' });

  await p.setViewportSize({ width: 1280, height: 800 });
  await p.screenshot({ path: 'exports/f6_beranda_desktop.png' });

  // 8) Klik kartu masuk ke soal
  await p.setViewportSize({ width: 390, height: 844 });
  await p.evaluate(() => {
    const card = document.querySelector('.stitch-card[data-subject="matematika"][data-pkg="1"]');
    if (card) card.click();
  });
  await p.waitForTimeout(800);

  const soalOpened = await p.evaluate(() => {
    const ov = document.getElementById('homeOverlay');
    const ovHidden = ov ? ov.classList.contains('home-hidden') : false;
    const qnum = document.getElementById('mQNum');
    return {
      ovHidden,
      qnumVisible: qnum && getComputedStyle(qnum).display !== 'none',
      subject: state.currentSubject,
      pkg: state.currentPkg
    };
  });
  report('Klik kartu paket di Beranda membuka soal yang sesuai',
    soalOpened.ovHidden && soalOpened.subject === 'matematika' && soalOpened.pkg === 1,
    JSON.stringify(soalOpened)
  );

  await p.close();
  await browser.close();

  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== FASE 6: ${R.length - fail}/${R.length} PASS ===`);
  console.log('Console errors:', consoleErrors.length ? consoleErrors : 'None');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL FASE 6:', e); process.exit(1); });
