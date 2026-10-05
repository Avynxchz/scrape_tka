/**
 * Skrip Diagnosis Fase 11:
 * Mengukur posisi dan tinggi bottom nav di 4 menu (Beranda, Modul, Progres, Akun)
 * pada 3 resolusi: 360x640, 390x844, 412x915.
 */
const { chromium } = require('./node_modules/playwright-core');
const fs = require('fs');
const BASE = 'http://127.0.0.1:8080';

const VIEWPORTS = [
  { name: '360px', width: 360, height: 640 },
  { name: '390px', width: 390, height: 844 },
  { name: '412px', width: 412, height: 915 }
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = {};

  for (const vp of VIEWPORTS) {
    results[vp.name] = {};
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    
    await page.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(() => {});
    await page.waitForTimeout(2000);

    // Buka dashboard / homeOverlay
    await page.evaluate(() => {
      if (typeof homeOpen === 'function') homeOpen();
    });
    await page.waitForTimeout(600);

    const menus = ['beranda', 'modul', 'progres', 'akun'];

    for (const menu of menus) {
      await page.evaluate((m) => {
        if (typeof homeShowPanel === 'function') homeShowPanel(m);
      }, menu);
      await page.waitForTimeout(800);

      // Ambil screenshot
      const shotPath = `exports/f11_${menu}_${vp.name}.png`;
      await page.screenshot({ path: shotPath });

      // Ukur geometri nav
      let navMetrics = null;

      if (menu === 'beranda') {
        navMetrics = await page.evaluate(() => {
          const nav = document.querySelector('.stitch-bottomnav');
          if (!nav) return { error: 'nav not found' };
          const rect = nav.getBoundingClientRect();
          const cs = getComputedStyle(nav);
          const row = nav.querySelector('.stitch-bottomnav-row');
          const rowRect = row ? row.getBoundingClientRect() : null;

          // Check containing block triggers on parents
          let p = nav.parentElement;
          const ancestors = [];
          while (p && p !== document.documentElement) {
            const pcs = getComputedStyle(p);
            if (pcs.transform !== 'none' || pcs.filter !== 'none' || pcs.perspective !== 'none' || pcs.contain !== 'none') {
              ancestors.push({ tag: p.tagName, id: p.id, cls: p.className, transform: pcs.transform });
            }
            p = p.parentElement;
          }

          return {
            windowInnerHeight: window.innerHeight,
            windowInnerWidth: window.innerWidth,
            docHeight: document.documentElement.clientHeight,
            rect: { top: rect.top, bottom: rect.bottom, height: rect.height, width: rect.width },
            diffBottom: window.innerHeight - rect.bottom,
            computed: {
              position: cs.position,
              bottom: cs.bottom,
              height: cs.height,
              paddingBottom: cs.paddingBottom,
              boxSizing: cs.boxSizing
            },
            rowHeight: rowRect ? rowRect.height : 0,
            ancestorsWithTransform: ancestors
          };
        });
      } else {
        // Didalam iframe
        const frameTitle = menu === 'modul' ? 'Modul Belajar TKA Master'
          : menu === 'progres' ? 'Progres & Analitik TKA Master'
          : 'Akun & Preferensi TKA Master';
        
        // Ukur posisi iframe di parent
        const iframeMetrics = await page.evaluate((m) => {
          const frameId = m === 'modul' ? 'panelModulFrame'
            : m === 'progres' ? 'panelProgresFrame'
            : 'panelAkunFrame';
          const ifr = document.getElementById(frameId);
          if (!ifr) return null;
          const irect = ifr.getBoundingClientRect();
          const ics = getComputedStyle(ifr);
          return {
            top: irect.top,
            bottom: irect.bottom,
            height: irect.height,
            width: irect.width,
            position: ics.position,
            inset: { top: ics.top, bottom: ics.bottom, left: ics.left, right: ics.right }
          };
        }, menu);

        const frame = page.frame({ name: frameTitle }) || page.frame({ url: new RegExp(menu) });
        if (!frame) {
          navMetrics = { error: `frame not found for ${menu}` };
        } else {
          navMetrics = await frame.evaluate((args) => {
            const { ifrMet, menu } = args;
            const navSelector = menu === 'modul' ? '#modulMobile nav'
              : menu === 'progres' ? '#progresMobile nav'
              : '#akunMobile nav';
            const nav = document.querySelector(navSelector) || document.querySelector('nav');
            if (!nav) return { error: `nav not found for selector ${navSelector}` };
            const rect = nav.getBoundingClientRect();
            const cs = getComputedStyle(nav);
            const innerDiv = nav.querySelector('div');
            const rowRect = innerDiv ? innerDiv.getBoundingClientRect() : null;

            // Check ancestors
            let p = nav.parentElement;
            const ancestors = [];
            while (p && p !== document.documentElement) {
              const pcs = getComputedStyle(p);
              if (pcs.transform !== 'none' || pcs.filter !== 'none' || pcs.perspective !== 'none' || pcs.contain !== 'none') {
                ancestors.push({ tag: p.tagName, id: p.id, cls: p.className, transform: pcs.transform });
              }
              p = p.parentElement;
            }

            // HTML & body styles
            const htmlCs = getComputedStyle(document.documentElement);
            const bodyCs = getComputedStyle(document.body);

            return {
              windowInnerHeight: window.innerHeight,
              windowInnerWidth: window.innerWidth,
              docClientHeight: document.documentElement.clientHeight,
              docScrollHeight: document.documentElement.scrollHeight,
              rect: { top: rect.top, bottom: rect.bottom, height: rect.height, width: rect.width },
              diffBottomInFrame: window.innerHeight - rect.bottom,
              // Projected bottom in parent coordinates:
              projectedBottomInParent: ifrMet ? (ifrMet.top + rect.bottom) : null,
              computed: {
                position: cs.position,
                bottom: cs.bottom,
                height: cs.height,
                paddingBottom: cs.paddingBottom,
                boxSizing: cs.boxSizing
              },
              rowHeight: rowRect ? rowRect.height : 0,
              htmlHeight: htmlCs.height,
              bodyHeight: bodyCs.height,
              ancestorsWithTransform: ancestors
            };
          }, { ifrMet: iframeMetrics, menu });

          navMetrics.iframe = iframeMetrics;
        }
      }

      results[vp.name][menu] = navMetrics;
    }

    await page.close();
  }

  await browser.close();

  console.log('\n================ HASIL DIAGNOSIS FASE 11 ================');
  for (const [vpName, menuData] of Object.entries(results)) {
    console.log(`\n--- VIEWPORT ${vpName} ---`);
    for (const [mName, mInfo] of Object.entries(menuData)) {
      if (mInfo.error) {
        console.log(`  [${mName}]: ERROR -> ${mInfo.error}`);
        continue;
      }
      const btm = mInfo.projectedBottomInParent !== undefined && mInfo.projectedBottomInParent !== null
        ? mInfo.projectedBottomInParent
        : mInfo.rect.bottom;
      const navH = mInfo.rect.height;
      const diff = mInfo.diffBottom !== undefined ? mInfo.diffBottom : mInfo.diffBottomInFrame;
      console.log(`  [${mName}]: height = ${navH}px (row: ${mInfo.rowHeight}px), bottom = ${btm}px (diff to window.innerHeight: ${diff}px), pb: ${mInfo.computed.paddingBottom}`);
      if (mInfo.iframe) {
        console.log(`      iframe rect: top=${mInfo.iframe.top}, bottom=${mInfo.iframe.bottom}, height=${mInfo.iframe.height}, pos=${mInfo.iframe.position}`);
      }
      if (mInfo.ancestorsWithTransform && mInfo.ancestorsWithTransform.length > 0) {
        console.log(`      WARN: Ancestors with transform:`, JSON.stringify(mInfo.ancestorsWithTransform));
      }
    }
  }

  fs.writeFileSync('scratch/diagnosa_fase11.json', JSON.stringify(results, null, 2));
  console.log('\nDetail tersimpan di scratch/diagnosa_fase11.json');
})().catch(e => {
  console.error('DIAGNOSIS ERROR:', e);
  process.exit(1);
});
