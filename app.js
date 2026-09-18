/**
 * SIMULASI TKA MATEMATIKA - INTERACTIVE LEARNING PLATFORM
 * Core Application Logic, KaTeX Math Engine, & 2-Way AI Tutor
 */

// Application State
const state = {
  currentPkg: 1,
  currentIndex: 0,
  pkgData: {
    1: null,
    2: null
  },
  userAnswers: {
    1: {}, // { [no]: 'A' or ['A', 'B'] }
    2: {}
  },
  raguStatus: {
    1: {}, // { [no]: true/false }
    2: {}
  },
  simAnswers: {
    1: {}, // { [no]: { selected: 'B', checked: true } }
    2: {}
  },
  chatHistory: {
    1: {}, // { [no]: [ { sender: 'ai'|'user', text: '...' } ] }
    2: {}
  },
  explanationVisible: false
};

// Initialize Application on Page Load
document.addEventListener('DOMContentLoaded', async () => {
  await loadPackageData(1);
  await loadPackageData(2);
  renderQuestion();
  renderGridModal();
});

// Load JSON data for package
async function loadPackageData(pkgNum) {
  try {
    const res = await fetch(`data/paket_${pkgNum}_learning.json?t=${Date.now()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    state.pkgData[pkgNum] = await res.json();
  } catch (err) {
    console.error(`Gagal memuat paket ${pkgNum}:`, err);
  }
}

// Switch between Paket 1 and Paket 2
function switchPackage(pkgNum) {
  if (state.currentPkg === pkgNum) return;
  state.currentPkg = pkgNum;
  state.currentIndex = 0;
  state.explanationVisible = false;

  // Update tabs UI
  document.getElementById('tabPkg1').classList.toggle('active', pkgNum === 1);
  document.getElementById('tabPkg2').classList.toggle('active', pkgNum === 2);
  
  // Update Modal title
  document.getElementById('modalTitle').innerText = `Daftar Soal - Matematika Paket ${pkgNum}`;

  renderQuestion();
  renderGridModal();
}

// Get current question object
function getCurrentQuestion() {
  const pkg = state.pkgData[state.currentPkg];
  if (!pkg || !pkg.soal || !pkg.soal[state.currentIndex]) return null;
  return pkg.soal[state.currentIndex];
}

// Render the active question into CBT UI & Learning section
function renderQuestion() {
  const q = getCurrentQuestion();
  if (!q) return;

  const total = state.pkgData[state.currentPkg].soal.length;
  const pkgPath = `data/paket_${state.currentPkg}/`;

  // 1. Metadata Bar
  document.getElementById('badgeSoalNomor').innerText = `Soal Nomor ${q.nomor} dari ${total}`;
  document.getElementById('badgeTopik').innerText = q.topik || 'Matematika TKA';
  document.getElementById('badgeTipe').innerText = q.tipe_soal || 'Pilihan Ganda';

  // 2. Stimulus Left Column (Preserve clean list formatting)
  const stimContainer = document.getElementById('stimulusContainer');
  stimContainer.innerHTML = '';
  
  let hasStimulus = false;
  if (q.stimulus && (q.stimulus.text || (q.stimulus.images && q.stimulus.images.length > 0))) {
    hasStimulus = true;
    const stimDiv = document.createElement('div');
    stimDiv.className = 'stimulus-text';

    // If raw HTML exists from Pusmendik, use it for 100% fidelity
    if (q.stimulus.html) {
      let cleanHtml = q.stimulus.html;
      cleanHtml = cleanHtml.replace(/<!--\?xml.*?\?-->/g, '');
      cleanHtml = cleanHtml.replace(/\uFFFD/g, ' ');
      // Fix image paths to local assets
      if (q.stimulus.images && q.stimulus.images.length > 0) {
        q.stimulus.images.forEach(imgObj => {
          const localSrc = `${pkgPath}${imgObj.rel_path}`;
          cleanHtml = cleanHtml.replace(imgObj.remote_url, localSrc);
          if (imgObj.remote_url.startsWith('https://pusmendik.kemendikdasmen.go.id')) {
            const relRemote = imgObj.remote_url.replace('https://pusmendik.kemendikdasmen.go.id', '');
            cleanHtml = cleanHtml.replace(relRemote, localSrc);
          }
        });
      }
      stimDiv.innerHTML = cleanHtml;
    } else {
      // Fallback: Format paragraphs and bullets cleanly
      const paragraphs = q.stimulus.text.split('\n').filter(p => p.trim());
      paragraphs.forEach(pText => {
        const p = document.createElement('p');
        p.innerHTML = pText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        stimDiv.appendChild(p);
      });
    }
    stimContainer.appendChild(stimDiv);
  }

  if (!hasStimulus) {
    stimContainer.innerHTML = `
      <div style="color: var(--text-light); text-align: center; margin-top: 60px;">
        <i class="fa-regular fa-file-lines" style="font-size: 32px; margin-bottom: 12px; display: block;"></i>
        <p>Soal ini tidak memiliki teks stimulus/bacaan terpisah.</p>
        <p style="font-size: 13px;">Silakan langsung cermati pertanyaan dan formula di sebelah kanan.</p>
      </div>
    `;
  }

  // 3. Question Prompt (Right Column)
  const promptContainer = document.getElementById('promptContainer');
  promptContainer.innerHTML = '';
  const promptLines = (q.pertanyaan.text || '').split('\n').filter(l => l.trim());
  promptLines.forEach((line, idx) => {
    const p = document.createElement('p');
    p.innerHTML = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
    if (idx > 0) {
      p.style.fontSize = '13.5px';
      p.style.color = '#475569';
      p.style.marginTop = '6px';
    }
    promptContainer.appendChild(p);
  });

  if (q.pertanyaan.images && q.pertanyaan.images.length > 0) {
    q.pertanyaan.images.forEach(pImg => {
      const imgWrap = document.createElement('div');
      imgWrap.className = 'stimulus-img-container';
      const img = document.createElement('img');
      img.src = `${pkgPath}${pImg.rel_path}`;
      img.className = 'stimulus-img';
      imgWrap.appendChild(img);
      promptContainer.appendChild(imgWrap);
    });
  }

  // 4. Options List
  const optionsContainer = document.getElementById('optionsContainer');
  optionsContainer.innerHTML = '';

  const currentSelection = state.userAnswers[state.currentPkg][q.nomor];
  const isComplex = q.tipe_soal === 'Pilihan Ganda Kompleks';

  q.pilihan_jawaban.forEach(opt => {
    const isSelected = isComplex
      ? (Array.isArray(currentSelection) && currentSelection.includes(opt.key))
      : (currentSelection === opt.key);

    const optItem = document.createElement('div');
    optItem.className = `option-item ${isSelected ? 'selected' : ''}`;
    optItem.dataset.key = opt.key;
    optItem.onclick = () => selectOption(opt.key, isComplex);

    // Key indicator
    const indicator = document.createElement('div');
    indicator.className = 'opt-indicator';
    indicator.innerText = opt.key;
    if (isComplex) {
      indicator.style.borderRadius = '6px'; // Checkbox style
    }
    optItem.appendChild(indicator);

    // Option body
    const body = document.createElement('div');
    body.className = 'opt-body';

    const fullContent = opt.full_display || (opt.latex ? `$${opt.latex}$` : opt.text);
    body.innerHTML = fullContent;

    if (!opt.latex && opt.image) {
      const mathImg = document.createElement('img');
      mathImg.src = `${pkgPath}${opt.image.rel_path}`;
      mathImg.alt = `Opsi ${opt.key}`;
      mathImg.className = 'opt-math-img';
      body.appendChild(mathImg);
    }

    optItem.appendChild(body);
    optionsContainer.appendChild(optItem);
  });

  // Reset feedback banner
  const feedback = document.getElementById('feedbackBanner');
  feedback.style.display = 'none';

  // 5. Navigation Buttons State
  document.getElementById('btnPrev').disabled = state.currentIndex === 0;
  document.getElementById('btnNext').disabled = state.currentIndex === total - 1;
  document.getElementById('chkRagu').checked = !!state.raguStatus[state.currentPkg][q.nomor];

  // 6. Learning Section (Explanation, AI Tutor & Similar Question)
  renderExplanation(q);
  renderAiTutor(q);
  renderSimilarQuestion(q);

  // Toggle explanation visibility
  const learnSec = document.getElementById('learningSection');
  learnSec.style.display = state.explanationVisible ? 'flex' : 'none';
  document.getElementById('txtToggleExp').innerText = state.explanationVisible
    ? 'Tutup Tata Cara & Pembahasan'
    : 'Buka Tata Cara & Pembahasan';

  // Trigger KaTeX render
  renderMath();
  updateGridModalActive();
}

// Select an option
function selectOption(key, isComplex) {
  const q = getCurrentQuestion();
  if (!q) return;

  if (isComplex) {
    let arr = state.userAnswers[state.currentPkg][q.nomor] || [];
    if (!Array.isArray(arr)) arr = [arr];
    if (arr.includes(key)) {
      arr = arr.filter(k => k !== key);
    } else {
      arr.push(key);
    }
    state.userAnswers[state.currentPkg][q.nomor] = arr;
  } else {
    state.userAnswers[state.currentPkg][q.nomor] = key;
  }

  // Update UI selection classes
  const selected = state.userAnswers[state.currentPkg][q.nomor];
  document.querySelectorAll('.option-item').forEach(el => {
    const k = el.dataset.key;
    const isSel = isComplex ? (selected && selected.includes(k)) : (selected === k);
    el.classList.toggle('selected', !!isSel);
  });

  // Update modal grid
  renderGridModal();
}

// Check User's Answer to Main Question
function checkUserAnswer() {
  const q = getCurrentQuestion();
  if (!q) return;

  const currentSelection = state.userAnswers[state.currentPkg][q.nomor];
  const feedback = document.getElementById('feedbackBanner');
  const isComplex = q.tipe_soal === 'Pilihan Ganda Kompleks';

  if (!currentSelection || (Array.isArray(currentSelection) && currentSelection.length === 0)) {
    feedback.className = 'feedback-banner danger';
    feedback.style.display = 'flex';
    feedback.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Silakan pilih salah satu jawaban terlebih dahulu!';
    return;
  }

  const correctKey = q.kunci_jawaban;
  let isCorrect = false;

  if (isComplex) {
    const targetArr = Array.isArray(correctKey) ? correctKey : [correctKey];
    const sortedUser = [...currentSelection].sort().join(',');
    const sortedTarget = [...targetArr].sort().join(',');
    isCorrect = sortedUser === sortedTarget;
  } else {
    isCorrect = currentSelection === correctKey;
  }

  // Highlight options
  document.querySelectorAll('.option-item').forEach(el => {
    const k = el.dataset.key;
    const isTarget = isComplex ? (Array.isArray(correctKey) && correctKey.includes(k)) : (k === correctKey);
    el.classList.toggle('correct', isTarget);
    if (!isTarget && el.classList.contains('selected')) {
      el.classList.add('incorrect');
    }
  });

  feedback.style.display = 'flex';
  if (isCorrect) {
    feedback.className = 'feedback-banner success';
    feedback.innerHTML = '<i class="fa-solid fa-circle-check"></i> <strong>Luar Biasa! Jawabanmu Tepat Sekali!</strong> Cermati pembahasan di bawah untuk memperdalam teori.';
  } else {
    feedback.className = 'feedback-banner danger';
    feedback.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> <strong>Jawaban Belum Tepat.</strong> Kunci yang benar adalah <strong>${Array.isArray(correctKey) ? correctKey.join(', ') : correctKey}</strong>. Silakan pelajari tata cara pengerjaannya di bawah.`;
  }

  // Auto-open explanation so student can immediately learn
  if (!state.explanationVisible) {
    toggleExplanation();
  }
}

// Toggle display of Explanation section
function toggleExplanation() {
  state.explanationVisible = !state.explanationVisible;
  const learnSec = document.getElementById('learningSection');
  learnSec.style.display = state.explanationVisible ? 'flex' : 'none';
  document.getElementById('txtToggleExp').innerText = state.explanationVisible
    ? 'Tutup Tata Cara & Pembahasan'
    : 'Buka Tata Cara & Pembahasan';

  if (state.explanationVisible) {
    learnSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// Render the Step-by-Step Explanation, Symbols Glossary, and Why-Concept
function renderExplanation(q) {
  const p = q.pembahasan || {};
  document.getElementById('conceptContainer').innerText = p.konsep_kunci || '-';

  // 1. Symbols Glossary
  const symbolsBox = document.getElementById('symbolsBox');
  const symbolsContainer = document.getElementById('symbolsContainer');
  symbolsContainer.innerHTML = '';
  
  if (p.glosarium_simbol && p.glosarium_simbol.length > 0) {
    symbolsBox.style.display = 'block';
    p.glosarium_simbol.forEach(sym => {
      const card = document.createElement('div');
      card.className = 'symbol-card';
      card.innerHTML = `
        <div class="symbol-top">
          <span class="symbol-badge">$${sym.simbol}$</span>
          <span class="symbol-name">${sym.nama}</span>
        </div>
        <div class="symbol-desc">${sym.arti.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>
      `;
      symbolsContainer.appendChild(card);
    });
  } else {
    symbolsBox.style.display = 'none';
  }

  // 2. Why Concept Box
  const whyBox = document.getElementById('whyConceptBox');
  const whyTextEl = document.getElementById('whyConceptContainer');
  if (p.mengapa_begini) {
    whyBox.style.display = 'flex';
    whyTextEl.innerHTML = p.mengapa_begini
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
  } else {
    whyBox.style.display = 'none';
  }
  
  // 3. Ordered Steps
  const stepsContainer = document.getElementById('stepsContainer');
  stepsContainer.innerHTML = '';
  
  if (p.langkah_penyelesaian && Array.isArray(p.langkah_penyelesaian)) {
    p.langkah_penyelesaian.forEach(stepText => {
      const stepDiv = document.createElement('div');
      stepDiv.className = 'step-item';
      stepDiv.innerHTML = stepText
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
      stepsContainer.appendChild(stepDiv);
    });
  }

  // 4. Pro Tips
  document.getElementById('tipsContainer').innerText = p.tips_trik || '-';
}

// Render the Interactive AI Tutor Section
function renderAiTutor(q) {
  // Quick Prompt Chips
  const chipsContainer = document.getElementById('quickChipsContainer');
  chipsContainer.innerHTML = '';

  const prompts = q.quick_prompts || [
    "Apa arti simbol matematika di soal ini?",
    "Kenapa langkah pengerjaannya seperti ini?",
    "Bisa jelaskan dengan analogi yang lebih gampang?",
    "Bagaimana trik cepat mengerjakan saat ujian?"
  ];

  prompts.forEach(pText => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'chip-btn';
    chip.innerText = pText;
    chip.onclick = () => sendQuickPrompt(pText);
    chipsContainer.appendChild(chip);
  });

  // Render conversation history for this question
  renderChatHistory(q);
}

// Format AI Tutor responses into clean, beautiful typography & structured HTML
function formatAiMessage(rawText) {
  if (!rawText) return '';

  const lines = rawText.split('\n');
  let html = '';
  let inList = false;
  let listType = null;
  let inCallout = false;
  let calloutType = '';
  let calloutLines = [];

  function flushList() {
    if (inList) {
      html += listType === 'ul' ? '</ul>' : '</ol>';
      inList = false;
      listType = null;
    }
  }

  function flushCallout() {
    if (inCallout) {
      const inner = calloutLines.map(l => {
        let formatted = l.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*([^\*]+)\*/g, '<em>$1</em>');
        return formatted;
      }).join('<br>');
      html += `<div class="ai-callout ${calloutType}">${inner}</div>`;
      inCallout = false;
      calloutType = '';
      calloutLines = [];
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Check if line triggers a Callout Box
    if (trimmed.startsWith('📌') || trimmed.includes('Catatan Tutor:')) {
      flushList();
      flushCallout();
      inCallout = true;
      calloutType = 'ai-callout-tutor';
      calloutLines.push(line);
      continue;
    } else if (trimmed.startsWith('⚡') || trimmed.includes('Tips Cepat') || trimmed.includes('Trik Cepat')) {
      flushList();
      flushCallout();
      inCallout = true;
      calloutType = 'ai-callout-tip';
      calloutLines.push(line);
      continue;
    } else if (trimmed.startsWith('⚠️') || (trimmed.includes('Maaf ya') && i <= 2)) {
      flushList();
      flushCallout();
      inCallout = true;
      calloutType = 'ai-callout-refusal';
      calloutLines.push(line);
      continue;
    }

    if (inCallout) {
      if (trimmed === '') {
        flushCallout();
      } else {
        calloutLines.push(line);
      }
      continue;
    }

    // Headings
    if (line.startsWith('### ')) {
      flushList();
      const content = line.replace(/^###\s+/, '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      html += `<div class="ai-h3"><i class="fa-solid fa-diamond-turn-right"></i> <span>${content}</span></div>`;
      continue;
    } else if (line.startsWith('## ')) {
      flushList();
      const content = line.replace(/^##\s+/, '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      html += `<div class="ai-h2">${content}</div>`;
      continue;
    }

    // Unordered list (bullet •, -, *)
    const bulletMatch = line.match(/^(\s*)([•\-\*])\s+(.*)/);
    if (bulletMatch) {
      if (!inList || listType !== 'ul') {
        flushList();
        html += '<ul class="ai-list">';
        inList = true;
        listType = 'ul';
      }
      let itemContent = bulletMatch[3];
      itemContent = itemContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      itemContent = itemContent.replace(/\*([^\*]+)\*/g, '<em>$1</em>');
      html += `<li>${itemContent}</li>`;
      continue;
    }

    // Numbered list (1., 2.)
    const numMatch = line.match(/^(\s*)(\d+)\.\s+(.*)/);
    if (numMatch) {
      if (!inList || listType !== 'ol') {
        flushList();
        html += '<ol class="ai-num-list">';
        inList = true;
        listType = 'ol';
      }
      let itemContent = numMatch[3];
      itemContent = itemContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      itemContent = itemContent.replace(/\*([^\*]+)\*/g, '<em>$1</em>');
      html += `<li>${itemContent}</li>`;
      continue;
    }

    // Regular line
    flushList();
    if (trimmed === '') {
      html += '<div class="ai-space"></div>';
    } else {
      let pContent = line;
      pContent = pContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      pContent = pContent.replace(/\*([^\*]+)\*/g, '<em>$1</em>');
      html += `<p class="ai-p">${pContent}</p>`;
    }
  }

  flushList();
  flushCallout();

  return html;
}

// Render Chat Conversation History
function renderChatHistory(q) {
  const chatMessages = document.getElementById('chatMessages');
  chatMessages.innerHTML = '';

  const history = state.chatHistory[state.currentPkg][q.nomor] || [];

  if (history.length === 0) {
    // Default welcome message
    const defaultWelcome = document.createElement('div');
    defaultWelcome.className = 'chat-bubble ai';
    defaultWelcome.innerHTML = `
      <div class="bubble-avatar"><i class="fa-solid fa-robot"></i></div>
      <div class="bubble-content">
        <p class="ai-p">Halo! Saya <strong>AI Tutor TKA</strong>. Masih bingung dengan arti simbol $\\cup$ atau $\\cap$, atau kenapa angka irisan harus dikurangi? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!</p>
      </div>
    `;
    chatMessages.appendChild(defaultWelcome);
  } else {
    history.forEach(item => {
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble ${item.sender}`;
      const icon = item.sender === 'ai' ? 'fa-robot' : 'fa-user';
      
      const contentHtml = item.sender === 'ai' 
        ? formatAiMessage(item.text) 
        : `<p class="ai-p">${item.text.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')}</p>`;

      bubble.innerHTML = `
        <div class="bubble-avatar"><i class="fa-solid ${icon}"></i></div>
        <div class="bubble-content">${contentHtml}</div>
      `;
      chatMessages.appendChild(bubble);
    });
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Quick Prompt Handler
function sendQuickPrompt(promptText) {
  const input = document.getElementById('chatInput');
  input.value = promptText;
  sendChatMessage(new Event('submit'));
}

// Send Chat Message to Backend AI Tutor
async function sendChatMessage(e) {
  if (e && e.preventDefault) e.preventDefault();

  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;

  const q = getCurrentQuestion();
  if (!q) return;

  // Clear input
  input.value = '';

  // Initialize history if needed
  if (!state.chatHistory[state.currentPkg][q.nomor]) {
    state.chatHistory[state.currentPkg][q.nomor] = [];
  }

  // Add user message to history & DOM
  state.chatHistory[state.currentPkg][q.nomor].push({
    sender: 'user',
    text: msg
  });
  renderChatHistory(q);

  // Show typing indicator
  const chatMessages = document.getElementById('chatMessages');
  const typingBubble = document.createElement('div');
  typingBubble.className = 'chat-bubble ai typing-indicator';
  typingBubble.id = 'aiTypingBubble';
  typingBubble.innerHTML = `
    <div class="bubble-avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="bubble-content" style="color: var(--text-muted); font-style: italic;">
      <i class="fa-solid fa-circle-notch fa-spin"></i> AI Tutor sedang menyusun penjelasan...
    </div>
  `;
  chatMessages.appendChild(typingBubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  const btnSend = document.getElementById('btnSendChat');
  btnSend.disabled = true;

  try {
    const res = await fetch('/api/ai-tutor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        paket: state.currentPkg,
        nomor: q.nomor,
        message: msg,
        question_data: q
      })
    });

    const data = await res.json();
    const replyText = data.reply || "Maaf, terjadi kendala saat memproses penjelasan.";

    // Remove typing indicator
    const typingEl = document.getElementById('aiTypingBubble');
    if (typingEl) typingEl.remove();

    // Add AI response to history & DOM
    state.chatHistory[state.currentPkg][q.nomor].push({
      sender: 'ai',
      text: replyText
    });
    renderChatHistory(q);
    renderMath();
  } catch (err) {
    console.error("AI Tutor error:", err);
    const typingEl = document.getElementById('aiTypingBubble');
    if (typingEl) typingEl.remove();

    state.chatHistory[state.currentPkg][q.nomor].push({
      sender: 'ai',
      text: "Maaf, koneksi ke server AI Tutor terputus. Pastikan server lokal berjalan."
    });
    renderChatHistory(q);
  } finally {
    btnSend.disabled = false;
  }
}

// Render the Similar Practice Question (Soal Serupa)
function renderSimilarQuestion(q) {
  const sim = q.soal_serupa;
  const promptEl = document.getElementById('simPromptContainer');
  const optsEl = document.getElementById('simOptionsContainer');
  const feedbackEl = document.getElementById('simFeedback');
  
  feedbackEl.style.display = 'none';

  if (!sim) {
    promptEl.innerText = 'Soal pemantapan belum tersedia untuk nomor ini.';
    optsEl.innerHTML = '';
    return;
  }

  promptEl.innerText = sim.pertanyaan || '';
  optsEl.innerHTML = '';

  const savedSim = state.simAnswers[state.currentPkg][q.nomor];

  sim.pilihan.forEach(opt => {
    const isSel = savedSim && savedSim.selected === opt.key;
    const item = document.createElement('div');
    item.className = `sim-opt-item ${isSel ? 'selected' : ''}`;
    item.dataset.key = opt.key;
    item.onclick = () => selectSimOption(opt.key);

    const ind = document.createElement('div');
    ind.className = 'sim-indicator';
    ind.innerText = opt.key;
    item.appendChild(ind);

    const txt = document.createElement('span');
    txt.innerText = opt.text;
    item.appendChild(txt);

    optsEl.appendChild(item);
  });

  if (savedSim && savedSim.checked) {
    evaluateSimilarDisplay(sim, savedSim.selected);
  }
}

// Select option in similar question
function selectSimOption(key) {
  const q = getCurrentQuestion();
  if (!q) return;

  state.simAnswers[state.currentPkg][q.nomor] = {
    selected: key,
    checked: false
  };

  document.querySelectorAll('.sim-opt-item').forEach(el => {
    el.classList.toggle('selected', el.dataset.key === key);
    el.classList.remove('correct', 'incorrect');
  });

  document.getElementById('simFeedback').style.display = 'none';
}

// Check similar question answer
function checkSimilarAnswer() {
  const q = getCurrentQuestion();
  if (!q || !q.soal_serupa) return;

  const sim = q.soal_serupa;
  const saved = state.simAnswers[state.currentPkg][q.nomor];

  if (!saved || !saved.selected) {
    const fb = document.getElementById('simFeedback');
    fb.className = 'sim-feedback danger';
    fb.style.display = 'block';
    fb.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Pilih jawaban latihan terlebih dahulu!';
    return;
  }

  saved.checked = true;
  evaluateSimilarDisplay(sim, saved.selected);
}

// Display similar question feedback
function evaluateSimilarDisplay(sim, selectedKey) {
  const isCorrect = selectedKey === sim.kunci;
  const fb = document.getElementById('simFeedback');
  fb.style.display = 'block';

  document.querySelectorAll('.sim-opt-item').forEach(el => {
    const k = el.dataset.key;
    if (k === sim.kunci) {
      el.classList.add('correct');
    } else if (k === selectedKey && !isCorrect) {
      el.classList.add('incorrect');
    }
  });

  if (isCorrect) {
    fb.className = 'sim-feedback success';
    fb.innerHTML = `
      <div style="font-weight: 700; margin-bottom: 4px;"><i class="fa-solid fa-circle-check"></i> Jawaban Latihan Benar! (Opsi ${sim.kunci})</div>
      <div>${sim.pembahasan}</div>
    `;
  } else {
    fb.className = 'sim-feedback danger';
    fb.innerHTML = `
      <div style="font-weight: 700; margin-bottom: 4px;"><i class="fa-solid fa-circle-xmark"></i> Jawaban Latihan Belum Tepat. Kunci: Opsi ${sim.kunci}</div>
      <div>${sim.pembahasan}</div>
    `;
  }
  renderMath();
}

// Navigate Next / Previous
function navigateQuestion(delta) {
  const total = state.pkgData[state.currentPkg].soal.length;
  const newIndex = state.currentIndex + delta;
  if (newIndex >= 0 && newIndex < total) {
    state.currentIndex = newIndex;
    renderQuestion();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// Toggle Ragu-ragu
function toggleRagu() {
  const q = getCurrentQuestion();
  if (!q) return;
  const current = !!state.raguStatus[state.currentPkg][q.nomor];
  state.raguStatus[state.currentPkg][q.nomor] = !current;
  document.getElementById('chkRagu').checked = !current;
  renderGridModal();
}

// Render numbers in modal "Daftar Soal"
function renderGridModal() {
  const pkg = state.pkgData[state.currentPkg];
  if (!pkg || !pkg.soal) return;

  const grid = document.getElementById('soalGrid');
  grid.innerHTML = '';

  pkg.soal.forEach((item, idx) => {
    const no = item.nomor;
    const btn = document.createElement('button');
    btn.className = 'grid-item';
    btn.innerText = no;

    const isCurrent = idx === state.currentIndex;
    const isAnswered = !!state.userAnswers[state.currentPkg][no];
    const isRagu = !!state.raguStatus[state.currentPkg][no];

    if (isCurrent) btn.classList.add('current');
    else if (isRagu) btn.classList.add('ragu');
    else if (isAnswered) btn.classList.add('answered');

    btn.onclick = () => {
      state.currentIndex = idx;
      renderQuestion();
      closeDaftarModal();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    grid.appendChild(btn);
  });
}

function updateGridModalActive() {
  const items = document.querySelectorAll('.grid-item');
  items.forEach((item, idx) => {
    item.classList.toggle('current', idx === state.currentIndex);
  });
}

// Modal open / close
function openDaftarModal() {
  renderGridModal();
  document.getElementById('modalDaftarSoal').classList.add('open');
}

function closeDaftarModal(event) {
  if (event && event.target !== event.currentTarget) return;
  document.getElementById('modalDaftarSoal').classList.remove('open');
}

// Adjust font size
function setFontSize(size) {
  document.body.className = `font-${size}`;
  document.querySelectorAll('.btn-font').forEach(btn => {
    btn.classList.toggle('active', btn.innerText.toLowerCase() === (size === 'sm' ? 'a' : size === 'lg' ? 'a' : 'a'));
  });
}

// Trigger KaTeX math formula rendering
function renderMath() {
  if (window.renderMathInElement) {
    try {
      renderMathInElement(document.body, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true }
        ],
        throwOnError: false
      });
    } catch (e) {
      console.warn('KaTeX rendering notice:', e);
    }
  }
}
