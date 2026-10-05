/** Verifikasi visual home_desktop.html: 1280x860, tunggu 5 detik, screenshot ke exports/. */
const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });

  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(5000); // prefetch count + kirim ulang data 5x

  const frame = page.frames().find(f => f.url().includes('home_desktop'));
  if (!frame) { console.error('FAIL: iframe home_desktop tidak ditemukan'); process.exit(1); }

  // kondisi kartu SETELAH 5 detik (semua harus terisi angka real, bukan "—")
  const cards = await frame.evaluate(() => {
    return [...document.querySelectorAll('main section .grid > div.relative')].map(c => ({
      subject: c.dataset.subject, pkg: c.dataset.pkg,
      soal: [...c.querySelectorAll('span')].map(s => s.textContent.trim()).find(t => /Soal/.test(t)) || '?',
      menit: [...c.querySelectorAll('span')].map(s => s.textContent.trim()).find(t => /Menit/.test(t)) || '?',
      pct: [...c.querySelectorAll('span')].map(s => s.textContent.trim()).find(t => /^\d+%$/.test(t)) || '?',
    }));
  });
  console.log('Kartu setelah 5 detik:');
  cards.forEach(c => console.log(`  [${c.subject} p${c.pkg}] ${c.soal} | ${c.menit} | progres ${c.pct}`));

  const angkaKasar = await frame.evaluate(() => {
    const t = document.body.innerText;
    return ['Skor Komposit', 'Rian Pratama', '84/100', 'Persentil', 'Peluang Lolos', 'STEI-R']
      .filter(s => t.includes(s));
  });
  console.log(angkaKasar.length ? 'MASIH ADA ANGKA KARANGAN: ' + angkaKasar.join(', ') : 'Bersih: tidak ada angka karangan');

  await page.screenshot({ path: 'exports/home_desktop_verifikasi_20261004.png' });
  console.log('Screenshot: exports/home_desktop_verifikasi_20261004.png');
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
