/** Tes home_desktop.html: terima postMessage data, verifikasi angka ter-update, klik card kirim pesan balik. */
const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  const received = [];
  await page.goto('file:///D:/PROJECTS/SCRAPE_TKA/home_desktop.html');
  await page.waitForTimeout(1500);

  // kirim data nyata (6 slot: 3 section x 2 paket)
  await page.evaluate(() => {
    window.postMessage({ type: 'home-desktop-data', subjects: [
      { subject: 'matematika', pkg: 1, label: 'Matematika', count: 46, minutes: 45, progress: 13 },
      { subject: 'matematika', pkg: 2, label: 'Matematika', count: 25, minutes: 50, progress: 0 },
      { subject: 'fisika', pkg: 1, label: 'Fisika', count: 20, minutes: 45, progress: 0 },
      { subject: 'fisika', pkg: 2, label: 'Fisika', count: 24, minutes: 45, progress: 0 },
      { subject: 'ekonomi', pkg: 1, label: 'Ekonomi', count: 20, minutes: 45, progress: 0 },
      { subject: 'ekonomi', pkg: 2, label: 'Ekonomi', count: 29, minutes: 45, progress: 0 },
    ] }, '*');
  });
  await page.waitForTimeout(800);

  // listener balik
  await page.exposeFunction('onMsg', (p) => received.push(p));
  await page.evaluate(() => window.addEventListener('message', (e) => {
    if (e.data && e.data.type && window.onMsg) window.onMsg(JSON.stringify(e.data));
  }));

  // verifikasi angka di card
  const texts = await page.evaluate(() => {
    const cards = document.querySelectorAll('main section .grid.grid-cols-1.md\\:grid-cols-2 > div.relative');
    return [...cards].map(c => ({
      subject: c.dataset.subject || null,
      pkg: c.dataset.pkg || null,
      soal: [...c.querySelectorAll('span')].map(s => s.textContent.trim()).find(t => /Soal/.test(t)) || null,
      chip: c.querySelector('span.rounded-full.bg-brand-emerald-light')?.textContent.trim() || null,
    }));
  });

  console.log('cards:', cards_len(texts));
  texts.forEach((t, i) => console.log(`  [${i}] ${t.subject || '-'} p${t.pkg || '-'} | ${t.soal} | chip=${t.chip}`));

  // klik card pertama -> harus kirim open-package
  await page.evaluate(() => document.querySelector('main section .grid > div.relative').click());
  await page.waitForTimeout(400);

  const openMsgs = received.filter(r => r.includes('open-package'));
  console.log('open-package terkirim:', openMsgs.length, openMsgs[0] || '');

  function cards_len(t) { return t.length + ' (harusnya >=6)'; }
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
