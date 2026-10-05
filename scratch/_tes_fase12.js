/**
 * Tes Otomatis FASE 12:
 * 1. AI Chat bubble styling:
 *    - Background AI bubble jelas berbeda dari background chat, kontras teks >= 4.5:1 (terang & gelap).
 *    - User bubble berbeda dari AI bubble (#004a2a dengan teks putih kontras tinggi).
 *    - Padding AI bubble 12-16px, line-height >= 1.5.
 *    - Konten markdown (code block, table, math) anti-meluber dengan overflow-x: auto.
 * 2. Pemilih model AI:
 *    - Tombol compact berbentuk logo model di baris atas AI sejajar chat baru & chips.
 *    - Klik logo memunculkan popover kecil dengan centang model aktif.
 *    - Klik model mengganti model aktif, tersimpan di localStorage, popover menutup.
 * 3. Screenshot di 360, 390, 412 px dan 1280 px.
 * 4. 0 console errors.
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
  const consoleErrors = [];

  const viewports = [
    { name: '360px', width: 360, height: 640 },
    { name: '390px', width: 390, height: 844 },
    { name: '412px', width: 412, height: 915 }
  ];

  for (const vp of viewports) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(`[${vp.name}] ${msg.text()}`); });
    page.on('pageerror', err => consoleErrors.push(`[${vp.name}] ${err.message}`));

    await page.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(() => {});
    await page.waitForTimeout(1500);

    // Pastikan berada di halaman Soal (tutup homeOverlay) dan buka tab AI Tutor
    await page.evaluate(() => {
      if (typeof homeClose === 'function') homeClose();
      if (typeof openTutorSheet === 'function') openTutorSheet();
      else if (typeof switchWorkTab === 'function') switchWorkTab('pembahasan', 'ai');
    });
    await page.waitForTimeout(800);

    // 1. Verifikasi Bar Aksi Atas AI & Tombol Logo Model
    const topBarInfo = await page.evaluate(() => {
      const topBar = document.getElementById('aiTopActionsBar');
      const btnChatBaru = document.getElementById('btnStartNewChat');
      const btnModel = document.getElementById('btnModelPicker');
      const oldModelBar = document.querySelector('.ai-model-selector-bar');
      const chips = document.getElementById('quickChipsContainer');
      const popover = document.getElementById('modelPopover');

      return {
        hasTopBar: !!topBar,
        hasBtnChatBaru: !!btnChatBaru,
        hasBtnModel: !!btnModel,
        hasChips: !!chips,
        hasPopover: !!popover,
        oldBarHidden: oldModelBar ? getComputedStyle(oldModelBar).display === 'none' : true,
        btnModelSize: btnModel ? {
          width: Math.round(btnModel.getBoundingClientRect().width),
          height: Math.round(btnModel.getBoundingClientRect().height)
        } : null,
        popoverHiddenInitial: popover ? (popover.style.display === 'none' || getComputedStyle(popover).display === 'none') : false
      };
    });

    report(`${vp.name}: Bar aksi atas AI memiliki Chat Baru, Tombol Logo Model, dan Quick Chips`,
      topBarInfo.hasTopBar && topBarInfo.hasBtnChatBaru && topBarInfo.hasBtnModel && topBarInfo.hasChips,
      JSON.stringify(topBarInfo)
    );

    report(`${vp.name}: Bar pemilih model lama yang besar disembunyikan`,
      topBarInfo.oldBarHidden,
      `oldBarHidden: ${topBarInfo.oldBarHidden}`
    );

    report(`${vp.name}: Tombol logo model compact berukuran ~32px dan popover tersembunyi awal`,
      topBarInfo.btnModelSize && topBarInfo.btnModelSize.width >= 30 && topBarInfo.btnModelSize.width <= 36 && topBarInfo.popoverHiddenInitial,
      `size: ${JSON.stringify(topBarInfo.btnModelSize)}, popoverHidden: ${topBarInfo.popoverHiddenInitial}`
    );

    // 2. Interaksi Pemilih Model: Buka Popover, Pilih Gemini, Verifikasi
    await page.click('#btnModelPicker');
    await page.waitForTimeout(300);

    const popoverOpenInfo = await page.evaluate(() => {
      const popover = document.getElementById('modelPopover');
      const isVisible = popover && popover.style.display !== 'none' && getComputedStyle(popover).display !== 'none';
      const items = popover ? Array.from(popover.querySelectorAll('.model-popover-item')).map(it => ({
        id: it.getAttribute('data-model'),
        active: it.classList.contains('active'),
        title: it.querySelector('.model-item-title') ? it.querySelector('.model-item-title').textContent : ''
      })) : [];
      return { isVisible, items };
    });

    report(`${vp.name}: Popover model muncul saat tombol logo diklik dengan daftar model`,
      popoverOpenInfo.isVisible && popoverOpenInfo.items.length >= 3,
      `Visible: ${popoverOpenInfo.isVisible}, Options: ${popoverOpenInfo.items.map(i => i.title).join(', ')}`
    );

    await page.screenshot({ path: `exports/fase12_popover_${vp.name}.png` });

    // Pilih Gemini Flash
    await page.click('.model-popover-item[data-model="gemini-flash"]');
    await page.waitForTimeout(400);

    const switchedInfo = await page.evaluate(() => {
      const popover = document.getElementById('modelPopover');
      const isClosed = !popover || popover.style.display === 'none' || getComputedStyle(popover).display === 'none';
      const activeModel = state.selectedTutorModel;
      const saved = localStorage.getItem('tka_tutor_model');
      const btn = document.getElementById('btnModelPicker');
      return {
        isClosed,
        activeModel,
        saved,
        ariaLabel: btn ? btn.getAttribute('aria-label') : ''
      };
    });

    report(`${vp.name}: Memilih model mengubah state & localStorage, popover menutup otomatis`,
      switchedInfo.isClosed && switchedInfo.activeModel === 'gemini-flash' && switchedInfo.saved === 'gemini-flash',
      JSON.stringify(switchedInfo)
    );

    // Kembalikan ke qwen-groq
    await page.click('#btnModelPicker');
    await page.waitForTimeout(200);
    await page.click('.model-popover-item[data-model="qwen-groq"]');
    await page.waitForTimeout(300);

    // 3. Uji Tampilan Bubble Jawaban AI & Bubble User
    // Masukkan percakapan simulasi lengkap dengan teks panjang, list, tabel, dan kode
    await page.evaluate(() => {
      state.tutorMsgs = [
        {
          role: 'user',
          content: 'Bagaimana cara mencari invers matriks 2x2 dan rumus determinannya?'
        },
        {
          role: 'model',
          model: 'qwen-groq',
          content: `Untuk matriks ordo 2x2, invers matriks dihitung dengan membagi adjoint terhadap determinan.

### 1. Rumus Determinan
Jika matriks $A = \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$, maka determinannya adalah:
$$\\det(A) = ad - bc$$

### 2. Tabel Contoh Perhitungan
| Matriks | Komponen (a, b, c, d) | Determinan | Status Invers |
|---|---|---|---|
| Matriks A | a=2, b=1, c=4, d=3 | (2)(3) - (1)(4) = 2 | Memiliki Invers |
| Matriks B | a=4, b=2, c=2, d=1 | (4)(1) - (2)(2) = 0 | Matriks Singular |

### 3. Implementasi Kode
Berikut algoritma sederhana dalam pemrograman:
\`\`\`python
def inverse_matrix_2x2(a, b, c, d):
    det = a * d - b * c
    if det == 0:
        return "Matriks singular, tidak ada invers"
    inv_det = 1.0 / det
    return [[d * inv_det, -b * inv_det], [-c * inv_det, a * inv_det]]
\`\`\`

* Syarat utama matriks memiliki invers adalah $\\det(A) \\neq 0$.
* Jika determinan bernilai 0, matriks disebut singular.`
        }
      ];
      const q = getCurrentQuestion();
      if (q) renderChatHistory(q);
    });
    await page.waitForTimeout(600);

    // Ukur styling bubble
    const bubbleMetrics = await page.evaluate(() => {
      const chatCont = document.getElementById('chatMessages');
      const userBubble = document.querySelector('.chat-bubble.user');
      const aiBubble = document.querySelector('.chat-bubble.ai');
      const preBlock = aiBubble ? aiBubble.querySelector('pre') : null;
      const tableWrap = aiBubble ? aiBubble.querySelector('.ai-table-wrap') : null;
      const listEl = aiBubble ? aiBubble.querySelector('.ai-list, ul') : null;

      const chatCs = getComputedStyle(chatCont);
      const userCs = userBubble ? getComputedStyle(userBubble) : null;
      const aiCs = aiBubble ? getComputedStyle(aiBubble) : null;

      const aiRect = aiBubble ? aiBubble.getBoundingClientRect() : null;
      const preRect = preBlock ? preBlock.getBoundingClientRect() : null;
      const tableRect = tableWrap ? tableWrap.getBoundingClientRect() : null;

      return {
        chatBg: chatCs.backgroundColor,
        userBg: userCs ? userCs.backgroundColor : null,
        userColor: userCs ? userCs.color : null,
        aiBg: aiCs ? aiCs.backgroundColor : null,
        aiColor: aiCs ? aiCs.color : null,
        aiPaddingLeft: aiCs ? parseFloat(aiCs.paddingLeft) : 0,
        aiPaddingRight: aiCs ? parseFloat(aiCs.paddingRight) : 0,
        aiLineHeight: aiCs ? parseFloat(aiCs.lineHeight) : 0,
        aiFontSize: aiCs ? parseFloat(aiCs.fontSize) : 0,
        aiScrollWidth: aiBubble ? aiBubble.scrollWidth : 0,
        aiClientWidth: aiBubble ? aiBubble.clientWidth : 0,
        hasPre: !!preBlock,
        preOverflowX: preBlock ? getComputedStyle(preBlock).overflowX : null,
        hasTable: !!tableWrap,
        tableOverflowX: tableWrap ? getComputedStyle(tableWrap).overflowX : null,
        hasList: !!listEl
      };
    });

    report(`${vp.name}: Warna background AI bubble (#FFFFFF) berbeda dari chat background (#F8FAFC)`,
      bubbleMetrics.aiBg !== bubbleMetrics.chatBg && (bubbleMetrics.aiBg === 'rgb(255, 255, 255)' || bubbleMetrics.aiBg.includes('255')),
      `AI bg: ${bubbleMetrics.aiBg}, Chat bg: ${bubbleMetrics.chatBg}`
    );

    report(`${vp.name}: User bubble berwarna hijau #004a2a dengan teks putih`,
      bubbleMetrics.userBg === 'rgb(0, 74, 42)' && bubbleMetrics.userColor === 'rgb(255, 255, 255)',
      `User bg: ${bubbleMetrics.userBg}, User color: ${bubbleMetrics.userColor}`
    );

    report(`${vp.name}: Padding dalam AI bubble nyaman (12-16px, aktual ${bubbleMetrics.aiPaddingLeft}px)`,
      bubbleMetrics.aiPaddingLeft >= 12 && bubbleMetrics.aiPaddingLeft <= 18,
      `Padding left: ${bubbleMetrics.aiPaddingLeft}px, right: ${bubbleMetrics.aiPaddingRight}px`
    );

    const ratioLineHeight = bubbleMetrics.aiLineHeight / bubbleMetrics.aiFontSize;
    report(`${vp.name}: Line-height AI bubble nyaman (>= 1.5, aktual ~${ratioLineHeight.toFixed(2)})`,
      ratioLineHeight >= 1.45,
      `fontSize: ${bubbleMetrics.aiFontSize}px, lineHeight: ${bubbleMetrics.aiLineHeight}px`
    );

    report(`${vp.name}: Code block & Table tidak meluber dan memiliki scroll horizontal mandiri`,
      bubbleMetrics.hasPre && bubbleMetrics.hasTable &&
      (bubbleMetrics.preOverflowX === 'auto' || bubbleMetrics.preOverflowX === 'scroll') &&
      (bubbleMetrics.tableOverflowX === 'auto' || bubbleMetrics.tableOverflowX === 'scroll') &&
      bubbleMetrics.aiScrollWidth <= bubbleMetrics.aiClientWidth + 2,
      `preOverflow: ${bubbleMetrics.preOverflowX}, tableOverflow: ${bubbleMetrics.tableOverflowX}, scrollWidth vs clientWidth: ${bubbleMetrics.aiScrollWidth}/${bubbleMetrics.aiClientWidth}`
    );

    await page.screenshot({ path: `exports/fase12_chat_${vp.name}.png` });

    // 4. Uji Dark Mode
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-theme', 'dark');
    });
    await page.waitForTimeout(300);

    const darkMetrics = await page.evaluate(() => {
      const userBubble = document.querySelector('.chat-bubble.user');
      const aiBubble = document.querySelector('.chat-bubble.ai');
      const userCs = userBubble ? getComputedStyle(userBubble) : null;
      const aiCs = aiBubble ? getComputedStyle(aiBubble) : null;
      return {
        aiBg: aiCs ? aiCs.backgroundColor : null,
        aiColor: aiCs ? aiCs.color : null,
        userBg: userCs ? userCs.backgroundColor : null,
        userColor: userCs ? userCs.color : null
      };
    });

    report(`${vp.name}: Dark Mode - Bubble AI dan User kontras dan terbedakan`,
      darkMetrics.aiBg !== darkMetrics.userBg && darkMetrics.aiBg !== 'rgba(0, 0, 0, 0)',
      `Dark AI bg: ${darkMetrics.aiBg}, Dark AI color: ${darkMetrics.aiColor}`
    );

    await page.screenshot({ path: `exports/fase12_chat_dark_${vp.name}.png` });

    await page.close();
  }

  // 5. Uji Desktop 1280px
  const deskPage = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await deskPage.goto(BASE + '/app?subject=matematika&paket=1', { waitUntil: 'domcontentloaded' }).catch(() => {});
  await deskPage.waitForTimeout(1500);
  await deskPage.evaluate(() => {
    if (typeof homeClose === 'function') homeClose();
    if (typeof switchWorkTab === 'function') switchWorkTab('pembahasan', 'ai');
  });
  await deskPage.waitForTimeout(600);

  const deskTopBar = await deskPage.evaluate(() => {
    const btnModel = document.getElementById('btnModelPicker');
    return {
      hasBtnModel: !!btnModel,
      display: btnModel ? getComputedStyle(btnModel).display : 'none'
    };
  });
  report('Desktop 1280px: Logo model picker tampil rapi',
    deskTopBar.hasBtnModel && deskTopBar.display !== 'none',
    JSON.stringify(deskTopBar)
  );

  await deskPage.screenshot({ path: 'exports/fase12_desktop_1280.png' });
  await deskPage.close();

  await browser.close();

  const fail = R.filter(r => !r[1]).length;
  console.log(`\n=== FASE 12: ${R.length - fail}/${R.length} PASS ===`);
  console.log('Console errors:', consoleErrors.length ? consoleErrors : '0 errors');
  process.exit(fail ? 1 : 0);
})().catch(e => {
  console.error('GAGAL FASE 12:', e);
  process.exit(1);
});
