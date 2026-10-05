/**
 * Tes integrasi panel: Beranda / Modul / Progres dalam satu Home overlay.
 * - 1280px (desktop) dan 390px (mobile)
 * - postMessage nav antar panel, klik paket dari Modul, persist tka_progress,
 *   halaman Progres menampilkan angka real.
 * Jalankan dari root: node scratch/_tes_panel.js  (server 8080 harus jalan)
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

  /* ================= DESKTOP 1280 ================= */
  const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
  await page.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'networkidle' }).catch(() => {});
  await page.evaluate(() => localStorage.removeItem('tka_progress'));
  await page.reload();
  await page.waitForTimeout(2500);

  // 1) default panel = Beranda
  const s1 = await page.evaluate(() => ({
    beranda: document.getElementById('panelBeranda').classList.contains('panel-active'),
    modul: document.getElementById('panelModul').classList.contains('panel-active'),
    overlayOpen: !document.getElementById('homeOverlay').classList.contains('home-hidden'),
    desktopFrame: document.getElementById('homeDesktopFrame').getBoundingClientRect().width > 0,
  }));
  report('Desktop: default panel Beranda + iframe tampil', s1.beranda && !s1.modul && s1.overlayOpen && s1.desktopFrame, JSON.stringify(s1));

  // 2) nav 'Modul' -> panel modul
  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Modul' }, '*'));
  await page.waitForTimeout(1200);
  const s2 = await page.evaluate(() => ({
    modul: document.getElementById('panelModul').classList.contains('panel-active'),
    modulFrame: document.getElementById('panelModulFrame').getBoundingClientRect().width > 0,
    beranda: document.getElementById('panelBeranda').classList.contains('panel-active'),
  }));
  report('Desktop: nav Modul -> panel modul tampil', s2.modul && s2.modulFrame && !s2.beranda, JSON.stringify(s2));

  // 3) klik kartu paket di iframe Modul -> overlay tutup -> soal tampil
  //    (server stdlib single-thread: prefetch 44 JSON bisa bikin lambat -> klik + polling)
  const modulFrame = page.frames().find(f => f.url().includes('workspace_modul'));
  if (!modulFrame) { report('Desktop: iframe modul ditemukan di frames', false); }
  else {
    let soal3 = '';
    for (let attempt = 0; attempt < 3 && !/1 dari 20/.test(soal3); attempt++) {
      await modulFrame.evaluate(() => {
        const btn = document.querySelector('#modulDesktop [data-open][data-subject="fisika"][data-pkg="1"]')
          || document.querySelector('[data-open][data-subject="fisika"][data-pkg="1"]');
        btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      });
      for (let i = 0; i < 10 && !/1 dari 20/.test(soal3); i++) {
        await page.waitForTimeout(1000);
        soal3 = await page.evaluate(() => (document.getElementById('qLabelHeader') || {}).textContent || '');
      }
    }
    const s3 = await page.evaluate(() => ({
      hidden: document.getElementById('homeOverlay').classList.contains('home-hidden'),
      soal: document.getElementById('qLabelHeader') ? document.getElementById('qLabelHeader').textContent : '(?)',
    }));
    report('Desktop: klik paket fisika P1 di Modul -> soal tampil', s3.hidden && /1 dari 20/.test(s3.soal), s3.soal);
  }

  // 4) buka home lagi -> default Beranda -> nav 'Progres' dengan data contoh
  await page.evaluate(() => document.getElementById('btnHome').click());
  await page.waitForTimeout(800);
  const s4a = await page.evaluate(() => document.getElementById('panelBeranda').classList.contains('panel-active'));
  report('Desktop: home dibuka lagi -> default panel Beranda', s4a);

  await page.evaluate(() => {
    localStorage.setItem('tka_progress', JSON.stringify({
      matematika: { "1": {
        "2": { kunci: "B", benar: false },
        "3": { kunci: "C", benar: true },
      } },
    }));
    window.postMessage({ type: 'nav', path: 'Progres' }, '*');
  });
  await page.waitForTimeout(1500);
  const s4 = await page.evaluate(() => ({
    progres: document.getElementById('panelProgres').classList.contains('panel-active'),
    frame: document.getElementById('panelProgresFrame').getBoundingClientRect().width > 0,
  }));
  report('Desktop: nav Progres -> panel progres tampil', s4.progres && s4.frame, JSON.stringify(s4));

  // 5) angka real di halaman progres (3 dikerjakan, 2 benar)
  const progFrame = page.frames().find(f => f.url().includes('workspace_progres'));
  if (!progFrame) { report('Desktop: iframe progres ditemukan di frames', false); }
  else {
    const val = await progFrame.evaluate(() => {
      const el = document.querySelector('.text-3xl');
      return el ? el.textContent.trim() : '(kosong)';
    });
    report('Desktop: halaman Progres menampilkan 2 (dikerjakan)', val === '2', 'total=' + val);
    await page.screenshot({ path: 'exports/panel_progres_desktop.png' });
  }

  // 6) nav 'Beranda' -> kembali
  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Beranda' }, '*'));
  await page.waitForTimeout(1800);
  const s6 = await page.evaluate(() => {
    const f = document.getElementById('homeDesktopFrame');
    const w = f.contentWindow;
    return {
      beranda: document.getElementById('panelBeranda').classList.contains('panel-active'),
      progres: document.getElementById('panelProgres').classList.contains('panel-active'),
      loaded: f.dataset.loaded || null,
      bridge: !!w.__homeDesktopBridge,
      list: w.__homeDesktopBridge && w.__homeDesktopBridge._list ? w.__homeDesktopBridge._list.map(x => x.count).join(',') : null,
      kartuTerisi: w.document.body.innerText.includes('46 Soal'),
    };
  });
  report('Desktop: nav Beranda -> kembali + kartu beranda terisi data real',
    s6.beranda && !s6.progres && s6.kartuTerisi, JSON.stringify(s6));

  // 7) jawab 1 soal -> tka_progress bertambah (persist nyata)
  await page.evaluate(() => document.getElementById('btnHome').click()); // tutup overlay ke soal
  await page.waitForTimeout(800);
  const persisted = await page.evaluate(() => {
    const q = getCurrentQuestion();
    const subj = state.currentSubject, pkg = Number(state.currentPkg) || 1;
    // jawab soal AKTIF dengan benar, apa pun tipenya (PG / Kompleks / Benar-Salah)
    if (statementType(q)) {
      const kunci = parseBsKunci(q);
      (q.pernyataan || []).forEach(st => selectBsAnswer(st.key, kunci[st.key]));
    } else if (Array.isArray(q.kunci_jawaban)) {
      q.kunci_jawaban.forEach(k => selectOption(String(k), true));
    } else {
      selectOption(String(q.kunci_jawaban), false);
    }
    const raw = JSON.parse(localStorage.getItem('tka_progress') || '{}');
    const entry = ((raw[subj] || {})[String(pkg)] || {})[q.nomor];
    return { subj, nomor: q.nomor, entry: entry || null };
  });
  report('Desktop: jawab 1 soal -> tka_progress terisi', !!persisted.entry, JSON.stringify(persisted));

  // buka progres lagi -> angka bertambah (4 dikerjakan)
  await page.evaluate(() => {
    document.getElementById('btnHome').click();
    setTimeout(() => window.postMessage({ type: 'nav', path: 'Progres' }, '*'), 300);
  });
  await page.waitForTimeout(2200);
  const progFrame2 = page.frames().find(f => f.url().includes('workspace_progres'));
  const val2 = progFrame2 ? await progFrame2.evaluate(() => {
    const el = document.querySelector('.text-3xl');
    return el ? el.textContent.trim() : '(kosong)';
  }) : '(no frame)';
  report('Desktop: Progres menampilkan 3 setelah jawab soal', val2 === '3', 'total=' + val2);

  // 8) screenshot beranda desktop & modul desktop (overlay masih open di panel progres)
  //    tunggu document.fonts.ready di page + iframe: ikon Material Symbols baru jadi
  //    setelah webfont-nya selesai di-fetch (bukan soal jeda tetap)
  console.log('STEP: screenshot beranda+modul desktop');
  const waitFonts = async (frame) => {
    try { await frame.evaluate(() => Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 8000))])); } catch (e) {}
  };
  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Beranda' }, '*'));
  await page.waitForTimeout(1200);
  await waitFonts(page);
  await waitFonts(page.frames().find(f => f.url().includes('home_desktop')));
  await page.screenshot({ path: 'exports/panel_beranda_desktop.png' });
  console.log('STEP: beranda desktop tersimpan');
  await page.evaluate(() => window.postMessage({ type: 'nav', path: 'Modul' }, '*'));
  await page.waitForTimeout(1200);
  await waitFonts(page);
  await waitFonts(page.frames().find(f => f.url().includes('workspace_modul')));
  await page.screenshot({ path: 'exports/panel_modul_desktop.png' });
  console.log('STEP: modul desktop tersimpan');
  await page.close();

  /* ================= MOBILE 390 ================= */
  console.log('STEP: mobile mulai');
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(e => console.log('goto mobile:', e.message));
  await m.waitForTimeout(3500);
  console.log('STEP: mobile loaded');

  const s9 = await m.evaluate(() => ({
    beranda: document.getElementById('panelBeranda').classList.contains('panel-active'),
    nav: getComputedStyle(document.querySelector('.stitch-bottomnav')).display,
    akun: getComputedStyle(document.querySelector('.stitch-bottomnav a[data-nav="akun"]')).display,
    card: document.querySelectorAll('.stitch-card').length,
  }));
  report('Mobile: default Beranda, bottomnav tampil, item Akun tersedia', s9.beranda && s9.nav !== 'none' && s9.akun !== 'none' && s9.card > 0, JSON.stringify(s9));
  await m.screenshot({ path: 'exports/panel_beranda_mobile.png' });

  await m.evaluate(() => window.postMessage({ type: 'nav', path: 'Modul' }, '*'));
  await m.waitForTimeout(1200);
  const s10 = await m.evaluate(() => ({
    modul: document.getElementById('panelModul').classList.contains('panel-active'),
    frame: document.getElementById('panelModulFrame').getBoundingClientRect().width > 0,
    navHidden: getComputedStyle(document.querySelector('.stitch-bottomnav')).display === 'none',
  }));
  report('Mobile: nav Modul -> iframe tampil, bottomnav beranda hilang', s10.modul && s10.frame && s10.navHidden, JSON.stringify(s10));

  await m.evaluate(() => window.postMessage({ type: 'nav', path: 'beranda' }, '*'));
  await m.waitForTimeout(600);
  const s11 = await m.evaluate(() => ({
    beranda: document.getElementById('panelBeranda').classList.contains('panel-active'),
    nav: getComputedStyle(document.querySelector('.stitch-bottomnav')).display,
  }));
  report('Mobile: nav beranda -> kembali, bottomnav muncul lagi', s11.beranda && s11.nav !== 'none', JSON.stringify(s11));

  await browser.close();

  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== ${R.length - fail}/${R.length} PASS ===`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('GAGAL:', e.message); process.exit(1); });
