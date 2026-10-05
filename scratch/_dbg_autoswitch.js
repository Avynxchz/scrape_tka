/** Debug v2: skenario PG (selectOption) -> auto-switch. */
const { chromium } = require('playwright-core');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errs = [];
  m.on('pageerror', e => errs.push(String(e).slice(0, 250)));
  await m.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await m.waitForTimeout(2500);
  await m.evaluate(() => { document.getElementById('homeOverlay').classList.add('home-hidden'); });
  const imm = await m.evaluate(() => {
    const q = getCurrentQuestion();
    selectOption(String(q.kunci_jawaban), false);
    checkUserAnswer();
    return {
      ua: JSON.stringify(state.userAnswers),
      answered: isQuestionAnswered(getCurrentQuestion()),
      expl: state.explanationVisible,
      tipe: q.tipe_soal,
    };
  });
  console.log('SEGERA:', JSON.stringify(imm));
  await m.waitForTimeout(2200);
  const dbg = await m.evaluate(() => ({
    pembClass: document.getElementById('workPanePembahasan').className,
    soalClass: document.getElementById('workPaneSoal').className,
    answered: isQuestionAnswered(getCurrentQuestion()),
    nomor: getCurrentQuestion().nomor,
  }));
  console.log('SETelah 2.2s:', JSON.stringify(dbg));
  console.log('ERRORS:', errs.length ? errs.join(' | ') : '(tidak ada)');
  await browser.close();
})().catch(e => console.error('GAGAL:', e.message));
