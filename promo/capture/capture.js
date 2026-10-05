/**
 * Promo showreel capture — drives the REAL app (http://127.0.0.1:8080) with Playwright
 * at 390x844 @3x and saves screenshots + a manifest of tap positions.
 *
 * - Demo data is seeded through localStorage (subjects, progress, streak).
 * - AI tutor endpoints are intercepted and return a pre-written answer (deterministic, no quota).
 * - Nothing in the app source is modified.
 *
 * Run:  node promo/capture/capture.js
 * Out:  promo/public/shots/*.png + promo/public/shots/manifest.json
 */
const path = require('path');
const fs = require('fs');
const { chromium } = require(path.resolve(__dirname, '..', '..', 'scratch', 'node_modules', 'playwright'));

const BASE = 'http://127.0.0.1:8080';
const OUT = path.resolve(__dirname, '..', 'public', 'shots');
fs.mkdirSync(OUT, { recursive: true });

const SUBJECT = 'geografi';
const PKG = 1;
const Q_INDEX = 8;          // soal nomor 9
const WRONG = 'A';
const RIGHT = 'C';

const USER_MSG = 'Kak, kenapa jawabanku A salah?';
const AI_REPLY = [
  'Oke, kita bedah pelan-pelan ya!',
  '',
  '**Langkah 1 — Cari penyebabnya.** Curah hujan tinggi adalah faktor **fisik**, sedangkan drainase buruk, alih fungsi lahan, dan sampah adalah faktor **manusia**.',
  '',
  '**Langkah 2 — Cocokkan konsep.** Banjir terjadi karena kedua faktor itu saling memengaruhi, jadi konsepnya adalah **keterkaitan**.',
  '',
  '**Langkah 3 — Eliminasi.** Opsi A membahas hubungan antarwilayah, bukan penyebab fisik + manusia.',
  '',
  'Jadi jawabannya **C. Keterkaitan antara faktor fisik dan manusia**.',
].join('\n');

// ---------- demo seed ----------
function buildProgress() {
  const mk = (n, benarN, kunci = 'A') => {
    const o = {};
    for (let i = 1; i <= n; i++) o[i] = { kunci, benar: i <= benarN };
    return o;
  };
  return {
    matematika: { 1: mk(30, 24), 2: mk(10, 7) },
    bahasa_inggris: { 1: mk(16, 13) },
    bahasa_indonesia: { 1: mk(12, 10) },
    fisika: { 1: mk(12, 8) },
  };
}
const SEED = {
  tka_user_subjects: JSON.stringify(['geografi', 'matematika', 'bahasa_inggris', 'fisika']),
  tka_progress: JSON.stringify(buildProgress()),
  tka_study_streak: '12',
};

const manifest = { viewport: { w: 390, h: 844, dsf: 3 }, shots: {} };

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true, hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
  });

  // ---- deterministic AI tutor (no real LLM call) ----
  const quota = { remaining: 4, daily_limit: 5, tier: 'free', cooldown_remaining: 0 };
  await ctx.route('**/api/tutor/state**', r => r.fulfill({ json: { status: 'success', messages: [], quota: { ...quota, remaining: 5 } } }));
  await ctx.route('**/api/tutor/new**', r => r.fulfill({ json: { status: 'success', messages: [], quota: { ...quota, remaining: 5 } } }));
  await ctx.route('**/api/tutor/chat**', async r => {
    await new Promise(res => setTimeout(res, 1500));
    await r.fulfill({ json: { status: 'success', reply: AI_REPLY, model: 'gemini-flash', quota } });
  });
  await ctx.route('**/api/feedback**', r => r.fulfill({ json: { status: 'success' } }));

  const page = await ctx.newPage();
  page.on('pageerror', e => console.log('[pageerror]', e.message));

  const box = async (sel) => {
    const el = await page.$(sel);
    if (!el) return null;
    const b = await el.boundingBox();
    return b ? { x: b.x, y: b.y, w: b.width, h: b.height, cx: b.x + b.width / 2, cy: b.y + b.height / 2 } : null;
  };
  const shot = async (name, extra = {}, wait = 350) => {
    await page.waitForTimeout(wait);
    await page.screenshot({ path: path.join(OUT, name + '.png') });
    manifest.shots[name] = extra;
    console.log('OK', name, JSON.stringify(extra));
  };

  // seed then reload so the app boots with demo data
  await page.goto(`${BASE}/app?subject=matematika&paket=1`, { waitUntil: 'domcontentloaded' });
  await page.evaluate(seed => { localStorage.clear(); for (const [k, v] of Object.entries(seed)) localStorage.setItem(k, v); }, SEED);
  await page.goto(`${BASE}/app?subject=matematika&paket=1`, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(2500);
  // hide any first-run toast/modal that is not part of the flow
  await page.keyboard.press('Escape').catch(() => {});

  // ===== 1. Dashboard =====
  await shot('home_top', {}, 600);

  const cardSel = `.stitch-card[data-subject="${SUBJECT}"][data-pkg="${PKG}"]`;
  await page.$eval(cardSel, el => el.scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(500);
  const scrollDelta = await page.evaluate(() => {
    const ov = document.getElementById('homeOverlay');
    const sc = [ov, ...ov.querySelectorAll('*')].find(e => e.scrollTop > 0);
    return sc ? sc.scrollTop : 0;
  });
  const cardBox = await box(cardSel);
  await shot('home_card', { tap: cardBox, scrollDelta });
  // element-only capture of the card for the "lift out" parallax
  await (await page.$(cardSel)).screenshot({ path: path.join(OUT, 'card.png') });
  manifest.shots.card = { box: cardBox };

  // tap the card (real click → real navigation into the package)
  await page.click(cardSel);
  await page.waitForTimeout(2200);
  await page.keyboard.press('Escape').catch(() => {});

  // jump to soal nomor 9 using the app's own state + renderer
  await page.evaluate(i => { state.currentIndex = i; state.explanationVisible = false; renderQuestion(); window.scrollTo(0, 0); }, Q_INDEX);
  await page.waitForTimeout(1200);
  await shot('q_top', {});

  // scroll so options are visible
  await page.$eval('#optionsContainer', el => el.scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(500);
  const wrongBox = await box(`.option-item[data-key="${WRONG}"]`);
  const rightBox = await box(`.option-item[data-key="${RIGHT}"]`);
  const optsBox = await box('#optionsContainer');
  const scrollYQ = await page.evaluate(() => window.scrollY);
  await shot('q_options', { wrong: wrongBox, right: rightBox, opts: optsBox, scrollY: scrollYQ });

  // ===== 2. Wrong answer =====
  await page.click(`.option-item[data-key="${WRONG}"]`);
  await shot('q_wrong_selected', { tap: wrongBox }, 300);
  const checkBox1 = await box('#btnCheckAnswer');
  await page.click('#btnCheckAnswer');
  await page.waitForTimeout(250);
  // keep the feedback in view
  await page.$eval('#optionsContainer', el => el.scrollIntoView({ block: 'center' }));
  const fbBox = await box('#feedbackBanner');
  await shot('q_wrong_feedback', { tap: checkBox1, wrong: await box(`.option-item[data-key="${WRONG}"]`), feedback: fbBox }, 150);

  // ===== 3. Pembahasan (auto-switch by the app after 1.1s) =====
  await page.waitForTimeout(1400);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(900);
  await shot('pemb_top', { rail: await box('#workRail') });
  await page.evaluate(() => window.scrollTo(0, 700));
  await shot('pemb_mid', { rail: await box('#workRail') }, 500);

  // ===== 4. AI tutor (mobile: floating work rail → "Tanya AI") =====
  const railBox = await box('#workRail');
  await page.click('#workRail');
  await page.waitForTimeout(600);
  const aiBtnSel = '#workRail .rail-btn[data-rail="ai"]';
  const aiBtnBox = await box(aiBtnSel);
  await shot('rail_open', { tap: railBox, ai: aiBtnBox }, 100);
  await page.click(aiBtnSel);
  await page.waitForTimeout(1200);
  await shot('tutor_open', { tap: aiBtnBox });

  await page.click('#chatInput');
  await page.type('#chatInput', USER_MSG.slice(0, 14), { delay: 15 });
  await shot('tutor_typing1', {}, 100);
  await page.type('#chatInput', USER_MSG.slice(14), { delay: 15 });
  const sendBox = await box('#btnSendChat');
  await shot('tutor_typing2', { send: sendBox }, 100);
  await page.click('#btnSendChat');
  await shot('tutor_thinking', { tap: sendBox }, 400);
  await page.waitForSelector('#aiTypingBubble', { state: 'detached', timeout: 10000 });
  await page.waitForTimeout(500);
  await shot('tutor_full', {});

  // streaming snapshots: re-render the app's own chat bubble with growing prefixes of the reply
  const words = AI_REPLY.split(/(\s+)/);
  const STEPS = 10;
  for (let s = 1; s <= STEPS; s++) {
    const n = Math.max(1, Math.round((words.length * s) / STEPS));
    let partial = words.slice(0, n).join('');
    // avoid an unclosed ** bold marker mid-stream
    if ((partial.match(/\*\*/g) || []).length % 2 === 1) partial += '**';
    await page.evaluate(txt => {
      const last = state.tutorMsgs[state.tutorMsgs.length - 1];
      last.content = txt;
      renderChatHistory(getCurrentQuestion());
      const cm = document.getElementById('chatMessages');
      if (cm) cm.scrollTop = cm.scrollHeight;
    }, partial);
    await shot(`tutor_stream_${String(s).padStart(2, '0')}`, {}, 120);
  }

  // ===== 5. Back to the question → correct answer =====
  await page.evaluate(() => { if (typeof closeTutorSheet === 'function') closeTutorSheet(); });
  await page.waitForTimeout(500);
  await page.evaluate(() => {
    // retry the question: clear the previous pick and re-render via the app
    const k = pkgKey();
    const q = getCurrentQuestion();
    if (state.userAnswers[k]) delete state.userAnswers[k][q.nomor];
    state.explanationVisible = false;
    state.keepWorkTab = false;
    switchWorkTab('soal', null, { scroll: false });
    renderQuestion();
  });
  await page.waitForTimeout(800);
  await page.$eval('#optionsContainer', el => el.scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(400);
  const rightBox2 = await box(`.option-item[data-key="${RIGHT}"]`);
  await shot('q_retry', { right: rightBox2 });
  await page.click(`.option-item[data-key="${RIGHT}"]`);
  await shot('q_right_selected', { tap: rightBox2 }, 300);
  const checkBox2 = await box('#btnCheckAnswer');
  await page.click('#btnCheckAnswer');
  await page.waitForTimeout(200);
  await page.$eval('#optionsContainer', el => el.scrollIntoView({ block: 'center' }));
  await shot('q_right_feedback', { tap: checkBox2, right: await box(`.option-item[data-key="${RIGHT}"]`), feedback: await box('#feedbackBanner') }, 150);
  await page.waitForTimeout(1500);

  // ===== 6. Result: 8 benar, 2 salah → 80% =====
  await page.evaluate(() => {
    const k = pkgKey();
    const pkg = state.pkgData[k];
    const wrongNos = [2, 6]; // these two answered wrongly
    state.userAnswers[k] = state.userAnswers[k] || {};
    pkg.soal.forEach(q => {
      const bad = wrongNos.includes(q.nomor);
      let ans;
      if (statementType(q)) {
        const kunci = parseBsKunci(q);
        ans = {};
        (q.pernyataan || []).forEach((st, i) => {
          const v = kunci[st.key];
          ans[st.key] = bad && i === 0 ? (v === 'Benar' ? 'Salah' : 'Benar') : v;
        });
      } else if (Array.isArray(q.kunci_jawaban)) {
        ans = bad ? q.kunci_jawaban.slice(0, 1) : q.kunci_jawaban.slice();
      } else {
        ans = bad ? (q.kunci_jawaban === 'A' ? 'B' : 'A') : q.kunci_jawaban;
      }
      state.userAnswers[k][q.nomor] = ans;
      persistAnswerProgress(q); // real progress write (tka_progress)
    });
    renderGridModal();
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(400);
  const finBox = await box('#btnFinishHeader');
  await page.click('#btnFinishHeader').catch(() => page.evaluate(() => openFinishModal()));
  await page.waitForTimeout(700);
  await shot('finish_modal', { tap: finBox });
  await page.evaluate(() => selesaiTes());
  await page.waitForTimeout(1200);
  await shot('result', {
    persen: await box('#reviewScorePersen'),
    benar: await box('#reviewScoreBenar'),
    salah: await box('#reviewScoreSalah'),
    kosong: await box('#reviewScoreKosong'),
  });
  const res = await page.evaluate(() => ({
    p: document.getElementById('reviewScorePersen').innerText,
    b: document.getElementById('reviewScoreBenar').innerText,
    s: document.getElementById('reviewScoreSalah').innerText,
  }));
  console.log('RESULT', res);
  manifest.result = res;

  // ===== 7. Progress analytics panel =====
  await page.evaluate(() => { closeReviewHasil(); homeOpen(); });
  await page.waitForTimeout(900);
  const navBox = await box('.stitch-bottomnav a[data-nav="progres"]');
  await page.evaluate(() => homeShowPanel('progres'));
  await page.waitForTimeout(2500);
  await shot('progres_top', { tap: navBox });
  const frame = page.frame({ url: /progres\.html/ });
  if (frame) {
    await frame.evaluate(() => {
      const sc = document.scrollingElement || document.body;
      sc.scrollTo(0, 520);
    });
    await shot('progres_mid', {}, 700);
  }

  fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 1));
  await browser.close();
  console.log('DONE');
})().catch(e => { console.error('FAILED:', e); process.exit(1); });
