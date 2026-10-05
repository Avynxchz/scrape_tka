/** Dump struktur dik-dit-text untuk cari sumber duplikasi/patah teks. */
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(2500);
  await page.evaluate(() => {
    document.getElementById('homeOverlay').classList.add('home-hidden');
    // jawab dulu agar pembahasan bisa dibuka
    const q = getCurrentQuestion();
    if (statementType(q)) {
      const kunci = parseBsKunci(q);
      (q.pernyataan || []).forEach(st => selectBsAnswer(st.key, kunci[st.key]));
    } else {
      selectOption(String(q.kunci_jawaban), Array.isArray(q.kunci_jawaban));
    }
  });
  await page.evaluate(() => checkUserAnswer());
  await page.waitForTimeout(2500); // tunggu fetch solusi + renderMath

  const dump = await page.evaluate(() => {
    const el = document.querySelector('#conceptContainer .dik-dit-text');
    if (!el) return { ada: false };
    return {
      innerText: el.innerText.slice(0, 400),
      innerHTML: el.innerHTML.slice(0, 900),
      katex: el.querySelectorAll('.katex').length,
    };
  });
  console.log(JSON.stringify(dump, null, 1));
  await page.screenshot({ path: 'exports/pilar_dik_mobile.png', fullPage: false });
  await browser.close();
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
