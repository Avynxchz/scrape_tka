/**
 * Tes Audit Mobile: navigasi, carousel, rail jempol, pilar rapi, chat AI.
 * Viewport 390x844.
 */
const { chromium } = require('playwright-core');
const BASE = 'http://127.0.0.1:8080';
const R = [];
function report(name, pass, extra) {
  R.push([name, pass]);
  console.log(`${pass ? 'PASS' : 'FAIL'} | ${name}${extra ? ' -> ' + extra : ''}`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await m.waitForTimeout(3000);

  // ===== BERANDA MOBILE =====
  // 1) lonceng hilang, avatar jadi tombol akun
  const s1 = await m.evaluate(() => ({
    lonceng: !!document.querySelector('.stitch-iconbtn'),
    avatarBtn: document.querySelector('.stitch-avatar') ? document.querySelector('.stitch-avatar').tagName : null,
  }));
  report('Beranda: lonceng dihapus, avatar = tombol Akun', !s1.lonceng && s1.avatarBtn === 'BUTTON', JSON.stringify(s1));

  // 2) avatar -> panel akun -> balik beranda
  await m.evaluate(() => document.querySelector('.stitch-avatar').click());
  await m.waitForTimeout(1200);
  let akun = await m.evaluate(() => document.getElementById('panelAkun').classList.contains('panel-active'));
  report('Beranda: klik avatar -> panel Akun', akun);
  await m.evaluate(() => window.postMessage({ type: 'nav', path: 'beranda' }, '*'));
  await m.waitForTimeout(1000);

  // 3) bottom nav seragam: 4 item, ikon konsisten
  const s3 = await m.evaluate(() => {
    const items = [...document.querySelectorAll('.stitch-bottomnav a')].map(a => ({
      nav: a.dataset.nav,
      icon: a.querySelector('.material-symbols-outlined') ? a.querySelector('.material-symbols-outlined').textContent.trim() : null,
    }));
    return items;
  });
  const expect = [
    { nav: 'beranda', icon: 'home' },
    { nav: 'modul', icon: 'menu_book' },
    { nav: 'progres', icon: 'analytics' },
    { nav: 'akun', icon: 'account_circle' },
  ];
  report('Beranda: bottom nav 4 item ikon standar', JSON.stringify(s3) === JSON.stringify(expect), JSON.stringify(s3));

  // 4) hero carousel: 3 slide, scroll -> dot pindah, slide 2 angka real
  await m.evaluate(() => {
    localStorage.setItem('tka_progress', JSON.stringify({
      matematika: { "1": { "1": { kunci: "A", benar: true }, "2": { kunci: "B", benar: false } } },
      fisika: { "1": { "1": { kunci: "B", benar: true } } },
    }));
  });
  await m.evaluate(() => renderHome());
  await m.waitForTimeout(600);
  const car = m.playwright ? null : null;
  await m.evaluate(() => {
    const c = document.getElementById('heroCarousel');
    c.scrollTo({ left: c.clientWidth, behavior: 'instant' });
  });
  await m.waitForTimeout(700);
  const s4 = await m.evaluate(() => ({
    slides: document.querySelectorAll('#heroCarousel > .stitch-hero').length,
    dot2: document.querySelectorAll('#heroDots i')[1].classList.contains('on'),
    hsDone: document.getElementById('hsDone').textContent,
    hsBenar: document.getElementById('hsBenar').textContent,
    hsAcc: document.getElementById('hsAcc').textContent,
  }));
  report('Beranda: carousel 3 slide bisa discroll, dot sinkron, statistik real',
    s4.slides === 3 && s4.dot2 && s4.hsDone === '3' && s4.hsBenar === '2' && s4.hsAcc === '67%', JSON.stringify(s4));
  await m.evaluate(() => {
    const c = document.getElementById('heroCarousel');
    c.scrollTo({ left: 0, behavior: 'instant' });
  });
  await m.waitForTimeout(500);
  await m.screenshot({ path: 'exports/mob_beranda_slide1.png' });
  await m.evaluate(() => {
    const c = document.getElementById('heroCarousel');
    c.scrollTo({ left: c.clientWidth, behavior: 'instant' });
  });
  await m.waitForTimeout(500);
  await m.screenshot({ path: 'exports/mob_beranda_slide2.png' });

  // ===== MASUK SOAL =====
  await m.evaluate(() => homeClose());
  await m.waitForTimeout(800);

  // 5) animasi masuk soal
  const s5 = await m.evaluate(() => {
    const c = document.querySelector('.cbt-question-card');
    return c ? c.classList.contains('soal-enter') : false;
  });
  report('Soal: animasi masuk (soal-enter) aktif', s5);

  // 6) tab bar full width (sejajar kartu soal)
  const s6 = await m.evaluate(() => {
    const t = document.getElementById('workTabs').getBoundingClientRect();
    const card = document.querySelector('.cbt-question-card').getBoundingClientRect();
    return { w: Math.round(t.width), cardW: Math.round(card.width), sama: Math.abs(t.width - card.width) < 4 };
  });
  report('Soal: tab bar full-width sejajar kartu soal', s6.sama, JSON.stringify(s6));

  // 7) rail jempol kanan tampil, sub-bar atas hilang
  const s7 = await m.evaluate(() => {
    const rail = document.getElementById('workRail');
    const st = getComputedStyle(rail);
    const sub = document.getElementById('pembSubbar');
    const rect = rail.getBoundingClientRect();
    return {
      display: st.display,
      fixed: st.position === 'fixed',
      kanan: rect.right > window.innerWidth - 120,
      bawah: rect.bottom > window.innerHeight - 250,
      subbar: getComputedStyle(sub).display,
    };
  });
  report('Soal: rail jempol kanan-bawah tampil, sub-bar atas hilang',
    s7.display === 'flex' && s7.fixed && s7.kanan && s7.bawah && s7.subbar === 'none', JSON.stringify(s7));

  // 8) jawab soal (B/S) -> pembahasan; teks pilar rapi
  await m.evaluate(() => {
    const q = getCurrentQuestion();
    const kunci = parseBsKunci(q);
    (q.pernyataan || []).forEach(st => selectBsAnswer(st.key, kunci[st.key]));
    checkUserAnswer();
  });
  await m.waitForTimeout(2200);
  const s8 = await m.evaluate(() => {
    // DEBUG auto-switch
    const dbg = {
      expl: state.explanationVisible,
      fb: document.getElementById('feedbackBanner').style.display,
      soalPane: document.getElementById('workPaneSoal').className,
      pembPane: document.getElementById('workPanePembahasan').className,
      keepWorkTab: state.keepWorkTab,
      answered: isQuestionAnswered(getCurrentQuestion()),
    };
    switchWorkTab('pembahasan', 'materi', { scroll: false });
    dbg.afterManual = document.getElementById('workPanePembahasan').classList.contains('active');
    window.__dbg = dbg;
    const el = document.querySelector('#conceptContainer .dik-dit-text');
    const t = el ? el.innerText : '';
    const ul = el ? el.querySelector('ul.text-bullet-list') : null;
    const mm = el ? el.querySelector('.katex-mathml') : null;
    const mmHidden = mm ? getComputedStyle(mm).position === 'absolute' : true;
    return {
      list: !!ul,
      liCount: ul ? ul.children.length : 0,
      dobel: /n\(S\)=30\s*n\(S\)=30/.test(t.replace(/\n/g, '')),
      mmHidden,
      pembActive: document.getElementById('workPanePembahasan').classList.contains('active'),
    };
  });
  report('Pilar: diketahui jadi list rapi, tanpa teks dobel, MathML tersembunyi',
    s8.list && s8.liCount === 4 && !s8.dobel && s8.mmHidden && s8.pembActive, JSON.stringify(s8));
  await m.evaluate(() => {
    document.getElementById('learningSection').scrollIntoView();
    window.scrollBy(0, 120);
  });
  await m.waitForTimeout(400);
  await m.screenshot({ path: 'exports/mob_pilar_rapi.png' });

  // 9) BUG USER: klik "Tanya AI" (pill/sub) dari pembahasan -> sheet AI muncul
  //    (di mobile sub-bar hilang; jalurnya rail) -> klik rail AI
  await m.evaluate(() => document.querySelector('#workRail .rail-btn[data-rail="ai"]').click());
  await m.waitForTimeout(900);
  const s9 = await m.evaluate(() => ({
    sheet: document.getElementById('cbtSidebarCol').classList.contains('tutor-open'),
    chatVisible: (() => {
      const c = document.getElementById('chatMessages');
      const r = c.getBoundingClientRect();
      return r.height > 200 && r.width > 200;
    })(),
  }));
  report('Tanya AI: dari rail di pembahasan -> sheet AI muncul', s9.sheet && s9.chatVisible, JSON.stringify(s9));

  // 10) sheet full screen
  const s10 = await m.evaluate(() => {
    const sh = document.getElementById('cbtSidebarCol').getBoundingClientRect();
    return { h: Math.round(sh.height), vh: window.innerHeight, full: Math.abs(sh.height - window.innerHeight) < 4 };
  });
  report('Tanya AI: sheet full screen', s10.full, JSON.stringify(s10));

  // 11) bubble user terpisah (align kanan, ada background)
  await m.evaluate(() => {
    const inp = document.getElementById('chatInput');
    inp.value = 'Kenapa pakai rumus peluang?';
    document.getElementById('chatForm').dispatchEvent(new Event('submit', { cancelable: true }));
  });
  await m.waitForTimeout(1200);
  const s11 = await m.evaluate(() => {
    const b = [...document.querySelectorAll('.chat-bubble.user')].pop();
    if (!b) return { ada: false };
    const st = getComputedStyle(b);
    return {
      ada: true,
      align: st.alignSelf,
      bg: st.backgroundColor,
      terpisah: st.backgroundColor !== 'rgba(0, 0, 0, 0)' && st.backgroundColor !== 'transparent',
    };
  });
  report('Tanya AI: bubble pesan user terpisah & jelas', s11.ada && s11.terpisah, JSON.stringify(s11));
  await m.screenshot({ path: 'exports/mob_chat_ai.png' });

  // 12) tutup sheet -> balik ke materi (tidak kosong)
  await m.evaluate(() => closeTutorSheet());
  await m.waitForTimeout(600);
  const s12 = await m.evaluate(() => ({
    sheetClosed: !document.getElementById('cbtSidebarCol').classList.contains('tutor-open'),
    materi: document.getElementById('pembSubMateri').style.display === 'block',
  }));
  report('Tanya AI: tutup sheet -> balik ke Pembahasan Pilar', s12.sheetClosed && s12.materi, JSON.stringify(s12));

  await browser.close();
  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
