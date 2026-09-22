/**
 * SIMULASI TKA - INTERACTIVE LEARNING PLATFORM (MULTI-SUBJECT)
 * Core Application Logic, KaTeX Math Engine, & 2-Way AI Tutor
 */

// ==========================================================================
// SUBJECT CATALOG - Multi-Subject Configuration
// ==========================================================================
const SUBJECT_CATALOG = {
  matematika: {
    name: 'Matematika',
    json: {
      1: 'data/matematika_paket_1_learning.json',
      2: 'data/matematika_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/paket_1/',
      2: 'data/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Matematika</strong>. Masih bingung dengan arti simbol, rumus, atau langkah pengerjaan di soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  },
  bahasa_inggris: {
    name: 'Bahasa Inggris',
    json: {
      1: 'data/bahasa_inggris_paket_1_learning.json',
      2: 'data/bahasa_inggris_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_inggris/paket_1/',
      2: 'data/bahasa_inggris/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Inggris</strong>. Masih bingung dengan kosakata, grammar, atau maksud teks pada soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  },
  ekonomi: {
    name: 'Ekonomi',
    json: {
      1: 'data/ekonomi_paket_1_learning.json',
      2: 'data/ekonomi_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/ekonomi/paket_1/',
      2: 'data/ekonomi/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Ekonomi</strong>. Masih bingung dengan konsep, istilah, atau alasan logis di balik jawaban soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  },
  kewirausahaan: {
    name: 'Kewirausahaan (PKWU)',
    json: {
      1: 'data/kewirausahaan_paket_1_learning.json',
      2: 'data/kewirausahaan_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/kewirausahaan/paket_1/',
      2: 'data/kewirausahaan/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Kewirausahaan (PKWU)</strong>. Masih bingung dengan konsep bisnis, istilah, atau langkah analisis pada soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  }
};

// Application State (keyed by "subject:pkg" so answers/history persist across switches)
const state = {
  currentSubject: 'matematika',
  currentPkg: 1,
  currentIndex: 0,
  pkgData: {},      // { [`${subject}:${pkg}`]: json }
  userAnswers: {},  // { [key]: { [no]: 'A' or ['A','B'] } }
  raguStatus: {},   // { [key]: { [no]: true/false } }
  simAnswers: {},   // { [key]: { [no]: { selected, checked } } }
  chatHistory: {},  // (usang — dipertahankan agar pemanggil lama tidak error)
  tutorMsgs: [],    // cache tampilan percakapan tutor soal aktif (sumber: server)
  tutorConvId: null,
  tutorProvider: null,
  explanationVisible: false
};

function pkgKey(pkg = state.currentPkg) {
  return `${state.currentSubject}:${pkg}`;
}

// Initialize Application on Page Load
document.addEventListener('DOMContentLoaded', async () => {
  await loadPackageData(1);
  await loadPackageData(2);
  updateSubjectUI();
  renderQuestion();
  renderGridModal();
});

// Load JSON data for current subject + package (cached)
async function loadPackageData(pkgNum) {
  const key = pkgKey(pkgNum);
  if (state.pkgData[key]) return;
  const subject = SUBJECT_CATALOG[state.currentSubject];
  try {
    const res = await fetch(`${subject.json[pkgNum]}?t=${Date.now()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    state.pkgData[key] = await res.json();

    // Initialize per-key state maps lazily so access never hits undefined
    if (!state.userAnswers[key]) state.userAnswers[key] = {};
    if (!state.raguStatus[key]) state.raguStatus[key] = {};
    if (!state.simAnswers[key]) state.simAnswers[key] = {};
    if (!state.chatHistory[key]) state.chatHistory[key] = {};
    // Riwayat percakapan tutor soal ini dimuat dari server (resume)
    syncTutorConversation();
  } catch (err) {
    console.error(`Gagal memuat ${subject.name} paket ${pkgNum}:`, err);
  }
}

// Update all dynamic subject-dependent texts in the UI
function updateSubjectUI() {
  const meta = SUBJECT_CATALOG[state.currentSubject];

  document.title = `Simulasi TKA ${meta.name} - Platform Belajar Interaktif`;
  document.getElementById('brandTitle').innerText = `SIMULASI TKA ${meta.name.toUpperCase()}`;
  document.getElementById('aiTutorTitle').innerText = `Tanya AI Tutor ${meta.name}`;
  document.getElementById('modalTitle').innerText = `Daftar Soal - ${meta.name} Paket ${state.currentPkg}`;

  // Package tabs: active state + dynamic question counts
  [1, 2].forEach(n => {
    const data = state.pkgData[pkgKey(n)];
    const count = data && data.soal ? ` (${data.soal.length} Soal)` : '';
    document.getElementById(`tabPkg${n}Label`).innerHTML = `Paket ${n}<small>${count}</small>`;
  });
  document.getElementById('tabPkg1').classList.toggle('active', state.currentPkg === 1);
  document.getElementById('tabPkg2').classList.toggle('active', state.currentPkg === 2);
}

// Switch active subject (from header dropdown)
async function switchSubject(subjectKey) {
  if (!SUBJECT_CATALOG[subjectKey] || state.currentSubject === subjectKey) return;

  state.currentSubject = subjectKey;
  state.currentPkg = 1;
  state.currentIndex = 0;
  state.explanationVisible = false;

  await Promise.all([loadPackageData(1), loadPackageData(2)]);

  document.getElementById('subjectSelect').value = subjectKey;
  updateSubjectUI();
  renderQuestion();
  renderGridModal();
}

// Switch between Paket 1 and Paket 2 (within active subject)
async function switchPackage(pkgNum) {
  if (state.currentPkg === pkgNum) return;

  await loadPackageData(pkgNum);

  state.currentPkg = pkgNum;
  state.currentIndex = 0;
  state.explanationVisible = false;

  updateSubjectUI();
  renderQuestion();
  renderGridModal();
}

// Get current question object
function getCurrentQuestion() {
  const pkg = state.pkgData[pkgKey()];
  if (!pkg || !pkg.soal || !pkg.soal[state.currentIndex]) return null;
  return pkg.soal[state.currentIndex];
}

// Render the active question into CBT UI & Learning section
function renderQuestion() {
  const q = getCurrentQuestion();
  if (!q) return;

  const total = state.pkgData[pkgKey()].soal.length;
  const subjectMeta = SUBJECT_CATALOG[state.currentSubject];
  const pkgPath = subjectMeta.imgBase[state.currentPkg];

  // 1. Metadata Bar
  document.getElementById('badgeSoalNomor').innerText = `Soal Nomor ${q.nomor} dari ${total}`;
  document.getElementById('badgeTopik').innerText = q.topik || `${subjectMeta.name} TKA`;
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
          // Global replace of the full remote URL
          cleanHtml = cleanHtml.split(imgObj.remote_url).join(localSrc);
          // Global replace of the relative remote path (without domain)
          if (imgObj.remote_url.startsWith('https://pusmendik.kemendikdasmen.go.id')) {
            const relRemote = imgObj.remote_url.replace('https://pusmendik.kemendikdasmen.go.id', '');
            cleanHtml = cleanHtml.split(relRemote).join(localSrc);
          }
          // Fallback: replace any src that ends with the same filename
          const fname = (imgObj.rel_path || '').split('/').pop();
          if (fname) {
            const escaped = fname.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            cleanHtml = cleanHtml.replace(
              new RegExp(`src="[^"]*${escaped}"`, 'g'),
              `src="${localSrc}"`
            );
          }
        });
      }
      // Final pass: rewrite any remaining relative images/... srcs to the local package path
      // (covers Pusmendik HTML that uses src="images/xxx.png" without a domain)
      cleanHtml = cleanHtml.replace(/src="(images\/[^"]+)"/g, `src="${pkgPath}$1"`);
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
        <p style="font-size: 13px;">Silakan langsung cermati pertanyaan dan pilihan jawaban di panel berikutnya.</p>
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

  // 4. Options List (PG) atau Tabel Pernyataan Benar/Salah
  const optionsContainer = document.getElementById('optionsContainer');
  optionsContainer.innerHTML = '';

  const currentSelection = (state.userAnswers[pkgKey()] || {})[q.nomor];
  const isComplex = q.tipe_soal === 'Pilihan Ganda Kompleks';
  const stmtType = statementType(q);

  if (stmtType) {
    renderBsStatements(q, currentSelection || {}, optionsContainer);
  } else {
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
  }

  // Reset feedback banner
  const feedback = document.getElementById('feedbackBanner');
  feedback.style.display = 'none';

  // 5. Navigation Buttons State
  document.getElementById('btnPrev').disabled = state.currentIndex === 0;
  // Next tetap aktif di soal terakhir: memicu popup Konfirmasi Selesai Tes (alur resmi)
  document.getElementById('btnNext').disabled = false;
  document.getElementById('chkRagu').checked = !!((state.raguStatus[pkgKey()] || {})[q.nomor]);

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
    let arr = (state.userAnswers[pkgKey()] || {})[q.nomor] || [];
    if (!Array.isArray(arr)) arr = [arr];
    if (arr.includes(key)) {
      arr = arr.filter(k => k !== key);
    } else {
      arr.push(key);
    }
    if (!state.userAnswers[pkgKey()]) state.userAnswers[pkgKey()] = {};
    state.userAnswers[pkgKey()][q.nomor] = arr;
  } else {
    if (!state.userAnswers[pkgKey()]) state.userAnswers[pkgKey()] = {};
    state.userAnswers[pkgKey()][q.nomor] = key;
  }

  // Update UI selection classes
  const selected = state.userAnswers[pkgKey()][q.nomor];
  document.querySelectorAll('.option-item').forEach(el => {
    const k = el.dataset.key;
    const isSel = isComplex ? (selected && selected.includes(k)) : (selected === k);
    el.classList.toggle('selected', !!isSel);
  });

  // Update modal grid
  renderGridModal();
}

// ==================== SOAL PERNYATAAN (Benar/Salah & Pernyataan-Label) ====================

// Tipe soal berbasis pernyataan: 'Benar-Salah', 'Pernyataan-Label', atau null
function statementType(q) {
  if (q.tipe_soal === 'Benar-Salah') return 'Benar-Salah';
  if (q.tipe_soal === 'Pernyataan-Label') return 'Pernyataan-Label';
  return null;
}

// Nilai kolom pilihan untuk soal pernyataan.
// Benar/Salah -> ['Benar','Salah']; Label -> label unik sesuai urutan kemunculan di kunci
function statementValues(q) {
  if (statementType(q) === 'Benar-Salah') return ['Benar', 'Salah'];
  const vals = [];
  (Array.isArray(q.kunci_jawaban) ? q.kunci_jawaban : []).forEach(entry => {
    const v = String(entry).split(':')[1];
    if (v && !vals.includes(v)) vals.push(v);
  });
  return vals;
}

// Render tabel pernyataan (meniru UI resmi Pusmendik)
function renderBsStatements(q, selection, container) {
  const pkgPath = SUBJECT_CATALOG[state.currentSubject].imgBase[state.currentPkg];
  const values = statementValues(q);
  const isBS = statementType(q) === 'Benar-Salah';

  const wrap = document.createElement('div');
  wrap.className = 'bs-table';
  // Lebar kolom nilai: label teks (mis. 'Long-term financial goals') butuh kolom lebih lebar
  wrap.style.setProperty('--bs-val-cols', `repeat(${values.length}, ${isBS ? '92px' : '116px'})`);

  // Header tabel: # | Pernyataan/Item | kolom nilai
  const header = document.createElement('div');
  header.className = 'bs-header';
  header.innerHTML = `
    <span class="bs-col-no">#</span>
    <span class="bs-col-stmt">${isBS ? 'Pernyataan' : 'Item'}</span>
    ${values.map(v => `<span class="bs-col-opt">${v}</span>`).join('')}
  `;
  wrap.appendChild(header);

  (q.pernyataan || []).forEach(stmt => {
    const row = document.createElement('div');
    row.className = 'bs-row';
    row.dataset.stmt = stmt.key;

    // Nomor/huruf pernyataan
    const no = document.createElement('div');
    no.className = 'bs-cell bs-cell-no';
    no.innerText = stmt.key;
    row.appendChild(no);

    // Isi pernyataan (teks + latex + gambar)
    const body = document.createElement('div');
    body.className = 'bs-cell bs-cell-stmt';
    const stmtText = stmt.text || '';
    body.innerHTML = stmt.latex
      ? `${stmtText} <span class="bs-latex">$${stmt.latex}$</span>`
      : stmtText;
    if (stmt.image) {
      const img = document.createElement('img');
      img.src = `${pkgPath}${stmt.image.rel_path}`;
      img.alt = `Pernyataan ${stmt.key}`;
      img.className = 'bs-stmt-img';
      body.appendChild(img);
    }
    row.appendChild(body);

    // Tombol nilai (Benar/Salah atau label) — toggle, touch-friendly
    values.forEach(val => {
      const cell = document.createElement('div');
      cell.className = 'bs-cell bs-cell-opt';
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.dataset.value = val;
      const valClass = isBS ? (val === 'Benar' ? 'bs-btn-benar' : 'bs-btn-salah') : 'bs-btn-opt';
      btn.className = `bs-btn ${valClass} ${selection[stmt.key] === val ? 'active' : ''}`;
      btn.innerText = val;
      btn.onclick = () => selectBsAnswer(stmt.key, val);
      cell.appendChild(btn);
      row.appendChild(cell);
    });

    wrap.appendChild(row);
  });

  container.appendChild(wrap);
}

// Pilih jawaban Benar/Salah untuk satu pernyataan
function selectBsAnswer(stmtKey, value) {
  const q = getCurrentQuestion();
  if (!q) return;

  if (!state.userAnswers[pkgKey()]) state.userAnswers[pkgKey()] = {};
  const cur = state.userAnswers[pkgKey()][q.nomor];
  const sel = (cur && typeof cur === 'object' && !Array.isArray(cur)) ? { ...cur } : {};
  sel[stmtKey] = value;
  state.userAnswers[pkgKey()][q.nomor] = sel;

  // Update tampilan tombol pada baris terkait
  const row = document.querySelector(`.bs-row[data-stmt="${stmtKey}"]`);
  if (row) {
    row.querySelectorAll('.bs-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.value === value);
    });
    row.classList.remove('correct', 'incorrect');
  }

  renderGridModal();
}

// Ambil kunci pernyataan B/S dari kunci_jawaban ["A:Benar", ...]
function parseBsKunci(q) {
  const map = {};
  (Array.isArray(q.kunci_jawaban) ? q.kunci_jawaban : []).forEach(entry => {
    const [k, v] = String(entry).split(':');
    if (k && v) map[k] = v;
  });
  return map;
}

// Apakah sebuah soal sudah dijawab lengkap (untuk grid daftar soal)
function isQuestionAnswered(item) {
  const ans = (state.userAnswers[pkgKey()] || {})[item.nomor];
  if (ans === undefined || ans === null || ans === '') return false;
  if (statementType(item)) {
    if (typeof ans !== 'object' || Array.isArray(ans)) return false;
    return (item.pernyataan || []).every(st => ans[st.key]);
  }
  if (item.tipe_soal === 'Pilihan Ganda Kompleks') {
    return Array.isArray(ans) && ans.length > 0;
  }
  return true;
}

// Check User's Answer to Main Question
function checkUserAnswer() {
  const q = getCurrentQuestion();
  if (!q) return;

  const currentSelection = (state.userAnswers[pkgKey()] || {})[q.nomor];
  const feedback = document.getElementById('feedbackBanner');
  const isComplex = q.tipe_soal === 'Pilihan Ganda Kompleks';
  const stmtType = statementType(q);

  // ---- Soal pernyataan (Benar/Salah & Label): validasi & evaluasi per pernyataan ----
  if (stmtType) {
    const sel = (currentSelection && typeof currentSelection === 'object' && !Array.isArray(currentSelection))
      ? currentSelection : {};
    const stmts = q.pernyataan || [];
    const unanswered = stmts.filter(st => !sel[st.key]);

    if (unanswered.length > 0) {
      const valName = stmtType === 'Benar-Salah' ? 'Benar/Salah' : 'label yang sesuai';
      feedback.className = 'feedback-banner danger';
      feedback.style.display = 'flex';
      feedback.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Silakan pilih ${valName} untuk <strong>semua pernyataan</strong> terlebih dahulu!`;
      return;
    }

    const kunci = parseBsKunci(q);
    let benar = 0;
    stmts.forEach(st => {
      const row = document.querySelector(`.bs-row[data-stmt="${st.key}"]`);
      if (!row) return;
      const isRight = sel[st.key] === kunci[st.key];
      if (isRight) benar++;
      row.classList.toggle('correct', isRight);
      row.classList.toggle('incorrect', !isRight);
    });

    feedback.style.display = 'flex';
    if (benar === stmts.length) {
      feedback.className = 'feedback-banner success';
      feedback.innerHTML = `<i class="fa-solid fa-circle-check"></i> <strong>Sempurna! Semua ${stmts.length} pernyataan benar!</strong> Cermati pembahasan di bawah untuk memperdalam teori.`;
    } else {
      feedback.className = 'feedback-banner danger';
      feedback.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> <strong>${benar} dari ${stmts.length} pernyataan benar.</strong> Baris bertanda merah belum tepat — perhatikan kunci pada baris hijau dan pelajari tata caranya di bawah.`;
    }

    if (!state.explanationVisible) toggleExplanation();
    return;
  }

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
// Sumber data panel = solusi spesifik soal (Layer 3, hasil Claude) via /api/solution.
// q.pembahasan (enrichment generik lama) TIDAK dipakai lagi di panel ini: konten
// generik tidak boleh menyamar sebagai pembahasan spesifik soal.
function renderExplanation(q) {
  _renderSolutionUnavailable();
  _applyCanonicalSolution(q);
}

// State jujur: semua kartu menandai pembahasan spesifik belum tersedia.
function _renderSolutionUnavailable(note) {
  document.getElementById('conceptContainer').innerHTML =
    '<i class="fa-solid fa-hourglass-half"></i> <strong>Pembahasan belum tersedia</strong> untuk soal ini — menunggu solusi spesifik hasil Claude (Layer 3).';

  document.getElementById('symbolsBox').style.display = 'none';
  document.getElementById('symbolsContainer').innerHTML = '';

  document.getElementById('whyConceptBox').style.display = 'none';
  document.getElementById('whyConceptContainer').innerHTML = '';

  const stepsContainer = document.getElementById('stepsContainer');
  stepsContainer.innerHTML = '';
  const noteDiv = document.createElement('div');
  noteDiv.className = 'step-item';
  noteDiv.innerHTML =
    '<i class="fa-solid fa-hourglass-half"></i> <strong>Langkah penyelesaian belum tersedia.</strong> ' +
    _escHtml(note || 'File solusi Claude untuk soal ini belum ada; konten generik lama sengaja tidak ditampilkan. Konteks soal (teks, visual, kunci) tetap bisa ditanyakan ke AI Tutor.');
  stepsContainer.appendChild(noteDiv);

  document.getElementById('tipsContainer').innerHTML =
    '<i class="fa-solid fa-hourglass-half"></i> Tips & jebakan spesifik soal ini menyusul dari solusi Claude.';

  document.getElementById('canonicalVisualBox').style.display = 'none';
  document.getElementById('canonicalVisualList').innerHTML = '';
}

function _escHtml(s) {
  return String(s || '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function _fmtText(s) {
  return _escHtml(s)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

// === Pembahasan panel: solusi spesifik hasil Claude (Layer 3) + konteks visual (Layer 2) ===
// status "pending" = file solusi belum ada -> state jujur, BUKAN fallback konten lama.
let _solutionReqSeq = 0;
async function _applyCanonicalSolution(q) {
  const seq = ++_solutionReqSeq;
  const token = pkgKey() + '#' + state.currentIndex;
  try {
    const res = await fetch('/api/solution', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subject: state.currentSubject,
        paket: state.currentPkg,
        nomor: q.nomor
      })
    });
    const data = await res.json();
    // Abaikan respons basi — pengguna sudah berpindah soal
    if (seq !== _solutionReqSeq || token !== pkgKey() + '#' + state.currentIndex) return;

    // Konteks visual soal (Layer 2 — transkripsi teks gambar asli, bukan pembahasan)
    const visBox = document.getElementById('canonicalVisualBox');
    const visList = document.getElementById('canonicalVisualList');
    visList.innerHTML = '';
    (data.formulas || []).forEach(f => {
      const li = document.createElement('div');
      li.className = 'step-item';
      const src = f.source === 'official data-latex' ? 'data-latex resmi' : 'transkripsi vision';
      li.innerHTML = `<i class="fa-solid fa-square-root-variable"></i> <strong>Formula</strong> <em>(${src})</em>: $${_escHtml(f.latex)}$`;
      visList.appendChild(li);
    });
    (data.visual_items || []).forEach(v => {
      const li = document.createElement('div');
      li.className = 'step-item';
      li.innerHTML = `<i class="fa-solid fa-chart-simple"></i> <strong>${_escHtml(v.kind)}:</strong> ${_fmtText(v.description)}`;
      visList.appendChild(li);
    });
    visBox.style.display = ((data.visual_items || []).length || (data.formulas || []).length) ? 'block' : 'none';

    if (data.status !== 'success' || !data.solution) {
      // Solusi spesifik belum ada -> status jujur (bukan konten learning lama)
      _renderSolutionUnavailable(data.message);
      renderMath();
      return;
    }

    const p = data.solution.pembahasan || {};

    // Konsep & tips: dari solusi spesifik soal (Layer 3 aktif)
    const konsepList = Array.isArray(p.konsep_kunci) ? p.konsep_kunci : [];
    document.getElementById('conceptContainer').innerHTML = konsepList.length
      ? konsepList.map(k => `<div class="step-item"><i class="fa-solid fa-lightbulb"></i> ${_fmtText(k)}</div>`).join('')
      : '-';
    document.getElementById('tipsContainer').innerHTML = p.tips_trik ? _fmtText(p.tips_trik) : '-';

    const review = data.solution.review || {};

    // Glosarium — hanya notasi yang benar-benar muncul di soal ini (kanonis)
    const symBox = document.getElementById('symbolsBox');
    const symList = document.getElementById('symbolsContainer');
    const glos = p.glosarium_simbol || [];
    if (glos.length) {
      symList.innerHTML = '';
      glos.forEach(sym => {
        const card = document.createElement('div');
        card.className = 'symbol-card';
        card.innerHTML = `
          <div class="symbol-top">
            <span class="symbol-badge">${sym.simbol.includes('\\') ? `$${_escHtml(sym.simbol)}$` : _escHtml(sym.simbol)}</span>
            <span class="symbol-name">${_escHtml(sym.nama)}</span>
          </div>
          <div class="symbol-desc">${_fmtText(sym.arti)}</div>
        `;
        symList.appendChild(card);
      });
      symBox.style.display = 'block';
    }

    // Alasan logis (Layer 3) — tampil hanya bila solusinya menyediakan
    const whyBox = document.getElementById('whyConceptBox');
    const whyTextEl = document.getElementById('whyConceptContainer');
    if (p.mengapa_begini) {
      whyBox.style.display = 'flex';
      whyTextEl.innerHTML = _fmtText(p.mengapa_begini);
    } else {
      whyBox.style.display = 'none';
    }

    // Langkah penyelesaian — hasil Claude
    const stepsContainer = document.getElementById('stepsContainer');
    stepsContainer.innerHTML = '';
    const badge = document.createElement('div');
    badge.className = 'step-item';
    badge.innerHTML =
      `<i class="fa-solid fa-robot"></i> <strong>Sumber:</strong> solusi spesifik soal hasil Claude ` +
      (data.solution.source && data.solution.source.file
        ? `(sumber aktif: <code>${_escHtml(data.solution.source.file)}</code>, ` +
          `soal <code>${_escHtml(data.solution.canonical_id)}</code>)`
        : `(soal <code>${_escHtml(data.solution.canonical_id)}</code>)`) +
      (data.visual_unresolved
        ? ` — <em>${data.visual_unresolved} elemen visual soal ini masih menunggu transkripsi</em>`
        : '') +
      `. <br><strong>Kunci resmi:</strong> ${_escHtml(data.solution.answer_display)}`;
    stepsContainer.appendChild(badge);
    (p.langkah_penyelesaian || []).forEach(stepText => {
      const stepDiv = document.createElement('div');
      stepDiv.className = 'step-item';
      stepDiv.innerHTML = _fmtText(stepText);
      stepsContainer.appendChild(stepDiv);
    });

    // Indikator review yang jujur (needs_manual_review dari file solusi) —
    // dibuat SETELAH langkah dibangun agar tidak ikut terhapus innerHTML=''.
    const oldReviewBadge = document.getElementById('solutionReviewBadge');
    if (oldReviewBadge) oldReviewBadge.remove();
    if (review.needs_manual_review) {
      const badge = document.createElement('div');
      badge.id = 'solutionReviewBadge';
      badge.className = 'step-item';
      badge.style.cssText = 'border-left:3px solid #f59e0b;background:rgba(245,158,11,.08);';
      badge.innerHTML =
        '<i class="fa-solid fa-triangle-exclamation"></i> <strong>Perlu verifikasi manual.</strong> ' +
        'Sebagian informasi sumber soal ini belum dapat dipastikan, sehingga penjelasan di atas ' +
        'memuat ketergantungan verifikasi dan belum final. ' +
        (review.review_reason ? `<details><summary style="cursor:pointer"><em>Lihat alasan verifikasi</em></summary>` +
          `<div style="margin-top:6px;font-size:.92em;">${_fmtText(review.review_reason)}</div></details>` : '');
      stepsContainer.insertBefore(badge, stepsContainer.children[1] || null);
    }

    renderMath();
  } catch (err) {
    if (seq !== _solutionReqSeq) return;
    console.warn('Solution (kanonis) tidak tersedia:', err);
    _renderSolutionUnavailable('Tidak dapat menghubungi server untuk memuat pembahasan.');
  }
}

// Render the Interactive AI Tutor Section
function renderAiTutor(q) {
  // Quick Prompt Chips
  const chipsContainer = document.getElementById('quickChipsContainer');
  chipsContainer.innerHTML = '';

  const prompts = q.quick_prompts || [
    "Apa arti istilah atau simbol di soal ini?",
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

  // Render conversation history for this question (muat dari server)
  renderChatHistory(q);
  syncTutorConversation();
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

  function inline(text) {
    let t = text;
    // Protect display math ($$...$$) from bold/em processing is unnecessary;
    // bold/italic patterns rarely clash with LaTeX in practice.
    t = t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/\*([^\*]+)\*/g, '<em>$1</em>');
    return t;
  }

  function flushList() {
    if (inList) {
      html += listType === 'ul' ? '</ul>' : '</ol>';
      inList = false;
      listType = null;
    }
  }

  function flushCallout() {
    if (inCallout) {
      const inner = calloutLines.map(l => inline(l)).join('<br>');
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

    // Block display math ($$...$$) on its own line
    const blockMathMatch = trimmed.match(/^\$\$(.+)\$\$$/);
    if (blockMathMatch) {
      flushList();
      html += `<div class="ai-block-math">$$${blockMathMatch[1]}$$</div>`;
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
      html += `<li>${inline(bulletMatch[3])}</li>`;
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
      html += `<li>${inline(numMatch[3])}</li>`;
      continue;
    }

    // Regular line
    flushList();
    if (trimmed === '') {
      html += '<div class="ai-space"></div>';
    } else {
      html += `<p class="ai-p">${inline(line)}</p>`;
    }
  }

  flushList();
  flushCallout();

  return html;
}

// Render Chat Conversation History
// Sumber data = percakapan tersimpan di server (tutor_store, per user+soal).
// state.tutorMsgs adalah cache tampilan; sinkronisasi dari /api/tutor/state.
function renderChatHistory(q) {
  const chatMessages = document.getElementById('chatMessages');
  chatMessages.innerHTML = '';

  const history = state.tutorMsgs || [];

  if (history.length === 0) {
    // Default welcome message (per subject)
    const defaultWelcome = document.createElement('div');
    defaultWelcome.className = 'chat-bubble ai';
    defaultWelcome.innerHTML = `
      <div class="bubble-avatar"><i class="fa-solid fa-robot"></i></div>
      <div class="bubble-content">
        <p class="ai-p">${SUBJECT_CATALOG[state.currentSubject].welcome}</p>
      </div>
    `;
    chatMessages.appendChild(defaultWelcome);
  } else {
    history.forEach(item => {
      const role = item.role === 'user' ? 'user' : 'ai';
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble ${role}`;
      const icon = role === 'ai' ? 'fa-robot' : 'fa-user';

      const contentHtml = role === 'ai'
        ? formatAiMessage(item.content)
        : `<p class="ai-p">${item.content.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')}</p>`;

      bubble.innerHTML = `
        <div class="bubble-avatar"><i class="fa-solid ${icon}"></i></div>
        <div class="bubble-content">${contentHtml}</div>
      `;
      chatMessages.appendChild(bubble);
    });
  }

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Sinkronkan cache chat dari server (resume percakapan tersimpan).
async function syncTutorConversation() {
  const q = getCurrentQuestion();
  if (!q) return;
  try {
    const res = await fetch(`/api/tutor/state?subject=${encodeURIComponent(state.currentSubject)}&paket=${state.currentPkg}&nomor=${q.nomor}`);
    const data = await res.json();
    if (data.status === 'success') {
      state.tutorMsgs = data.messages || [];
      state.tutorConvId = data.conversation_id || null;
      state.tutorProvider = data.provider || null;
      renderChatHistory(q);
    }
  } catch (err) {
    console.warn('Sync percakapan tutor gagal (server tidak dijangkau):', err);
  }
}

// Mulai percakapan BARU untuk soal ini (riwayat lama diarsipkan di server).
async function startNewTutorConversation() {
  const q = getCurrentQuestion();
  if (!q) return;
  try {
    const res = await fetch('/api/tutor/new', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subject: state.currentSubject, paket: state.currentPkg, nomor: q.nomor })
    });
    const data = await res.json();
    if (data.status === 'success') {
      state.tutorMsgs = [];
      state.tutorConvId = data.conversation_id;
      renderChatHistory(q);
    }
  } catch (err) {
    console.error('Gagal memulai percakapan baru:', err);
  }
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

  // Add user message to local cache & DOM (persistensi di server via API)
  const clientRequestId = 'r' + Date.now() + '-' + Math.random().toString(36).slice(2, 8);
  state.tutorMsgs = state.tutorMsgs || [];
  state.tutorMsgs.push({
    role: 'user',
    content: msg
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
    const res = await fetch('/api/tutor/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subject: state.currentSubject,
        paket: state.currentPkg,
        nomor: q.nomor,
        message: msg,
        request_id: clientRequestId
      })
    });

    const data = await res.json();
    const typingEl = document.getElementById('aiTypingBubble');
    if (typingEl) typingEl.remove();

    if (data.status === 'success' && data.reply) {
      state.tutorMsgs.push({ role: 'assistant', content: data.reply });
      renderChatHistory(q);
      renderMath();
    } else {
      // LLM gagal / error server: pesan user sudah tersimpan; tampilkan
      // error jujur + tombol coba lagi (TIDAK ada balasan palsu).
      state.tutorMsgs.push({
        role: 'assistant',
        content: '⚠️ ' + (data.message || 'Terjadi kendala saat menghubungi AI.'),
        error: true
      });
      renderChatHistory(q);
    }
  } catch (err) {
    console.error("AI Tutor error:", err);
    const typingEl = document.getElementById('aiTypingBubble');
    if (typingEl) typingEl.remove();

    state.tutorMsgs.push({
      role: 'assistant',
      content: '⚠️ Koneksi ke server AI Tutor terputus. Pesanmu sudah masuk — coba kirim ulang pesanmu.',
      error: true
    });
    renderChatHistory(q);
  } finally {
    btnSend.disabled = false;
  }
}

// Render the Similar Practice Question (Soal Serupa)
// Kaidah: konten generik tidak boleh menyamar sebagai latihan spesifik soal.
// soal_serupa lama ternyata TEMPLATE SAMA untuk semua soal dalam paket
// (terverifikasi audit: 1 teks unik utk 25 soal). Bila teks soal_serupa
// terdeteksi dipakai bergantian di >1 soal (bukan spesifik), tampilkan state
// jujur — jangan pajang soal latihan palsu.
function _isGenericSim(sim) {
  if (!sim || !sim.pertanyaan) return true;
  const pkg = state.pkgData[pkgKey()];
  if (!pkg || !pkg.soal) return false;
  const sameCount = pkg.soal.filter(
    x => (x.soal_serupa || {}).pertanyaan === sim.pertanyaan
  ).length;
  return sameCount > 1;
}

function renderSimilarQuestion(q) {
  const sim = q.soal_serupa;
  const promptEl = document.getElementById('simPromptContainer');
  const optsEl = document.getElementById('simOptionsContainer');
  const feedbackEl = document.getElementById('simFeedback');

  feedbackEl.style.display = 'none';

  if (!sim || _isGenericSim(sim)) {
    promptEl.innerHTML =
      '<i class="fa-solid fa-hourglass-half"></i> <strong>Latihan pemantapan spesifik untuk soal ini belum tersedia.</strong> ' +
      'Konten latihan generik lama (sama untuk semua soal) sengaja tidak ditampilkan agar tidak menyesatkan.';
    optsEl.innerHTML = '';
    return;
  }

  promptEl.innerText = sim.pertanyaan || '';
  optsEl.innerHTML = '';

  const savedSim = (state.simAnswers[pkgKey()] || {})[q.nomor];

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

  if (!state.simAnswers[pkgKey()]) state.simAnswers[pkgKey()] = {};
  state.simAnswers[pkgKey()][q.nomor] = {
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
  const saved = (state.simAnswers[pkgKey()] || {})[q.nomor];

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

// Navigate Next / Previous (Next di soal terakhir = pemicu Konfirmasi Selesai Tes)
function navigateQuestion(delta) {
  const total = state.pkgData[pkgKey()].soal.length;
  const newIndex = state.currentIndex + delta;

  if (delta > 0 && state.currentIndex === total - 1) {
    openFinishModal();
    return;
  }

  if (newIndex >= 0 && newIndex < total) {
    state.currentIndex = newIndex;
    renderQuestion();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

// ==================== ALUR SELESAI TES & REVIU HASIL ====================

function openFinishModal() {
  const total = state.pkgData[pkgKey()].soal.length;
  const answered = state.pkgData[pkgKey()].soal.filter(isQuestionAnswered).length;
  document.getElementById('finishSummaryText').innerText =
    `Kamu sudah menjawab ${answered} dari ${total} soal. ` +
    `Terimakasih telah berpartisipasi dalam tes ini. Tekan SELESAI TES untuk melihat reviu hasil, ` +
    `atau KEMBALI untuk melanjutkan mengerjakan.`;
  document.getElementById('modalKonfirmasiSelesai').classList.add('open');
}

function closeFinishModal() {
  document.getElementById('modalKonfirmasiSelesai').classList.remove('open');
}

// Evaluasi satu soal -> { status: 'benar'|'salah'|'kosong' }
// B/S dinilai per pernyataan; PG per soal (sesuai mekanisme resmi)
function evaluateQuestion(item) {
  const ans = (state.userAnswers[pkgKey()] || {})[item.nomor];

  if (item.tipe_soal === 'Benar-Salah' || item.tipe_soal === 'Pernyataan-Label') {
    const stmts = item.pernyataan || [];
    const results = stmts.map(st => {
      const picked = (ans && typeof ans === 'object' && !Array.isArray(ans)) ? ans[st.key] : null;
      if (!picked) return 'kosong';
      const kunciMap = parseBsKunci(item);
      return picked === kunciMap[st.key] ? 'benar' : 'salah';
    });
    return { type: 'bs', perStatement: results };
  }

  if (!isQuestionAnswered(item)) return { type: 'pg', status: 'kosong' };

  const correctKey = item.kunci_jawaban;
  const isComplex = item.tipe_soal === 'Pilihan Ganda Kompleks';
  let isCorrect;
  if (isComplex) {
    const target = Array.isArray(correctKey) ? [...correctKey].sort().join(',') : String(correctKey);
    isCorrect = [...ans].sort().join(',') === target;
  } else {
    isCorrect = ans === correctKey;
  }
  return { type: 'pg', status: isCorrect ? 'benar' : 'salah' };
}

function selesaiTes() {
  closeFinishModal();
  renderReviewHasil();
}

function renderReviewHasil() {
  const soalList = state.pkgData[pkgKey()].soal;
  let benar = 0, salah = 0, kosong = 0;
  const rows = [];

  soalList.forEach(item => {
    const res = evaluateQuestion(item);
    const ans = (state.userAnswers[pkgKey()] || {})[item.nomor];

    let andaHtml = '<span class="review-empty">Belum dijawab</span>';
    let kunciHtml = '';
    let counts;

    if (res.type === 'bs') {
      const kunciMap = parseBsKunci(item);
      counts = { benar: 0, salah: 0, kosong: 0 };
      res.perStatement.forEach(st => counts[st === 'benar' ? 'benar' : st === 'salah' ? 'salah' : 'kosong']++);
      // untuk agregat: setiap pernyataan dihitung satu item
      const partsAnda = (item.pernyataan || []).map(st => {
        const picked = (ans && typeof ans === 'object' && !Array.isArray(ans)) ? ans[st.key] : null;
        return `${st.key} (${picked || '&mdash;'})`;
      });
      const partsKunci = (item.pernyataan || []).map(st => `${st.key} (${kunciMap[st.key] || '&mdash;'})`);
      andaHtml = partsAnda.join('<br>');
      kunciHtml = partsKunci.join('<br>');
      benar += counts.benar;
      salah += counts.salah;
      kosong += counts.kosong;
    } else {
      if (res.status === 'kosong') {
        kosong++;
      } else if (res.status === 'benar') {
        benar++;
      } else {
        salah++;
      }
      const label = Array.isArray(ans) ? ans.join(', ') : (ans || null);
      andaHtml = label ? `<span class="review-ans">${label}</span>` : '<span class="review-empty">Belum dijawab</span>';
      const kl = Array.isArray(item.kunci_jawaban) ? item.kunci_jawaban.join(', ') : item.kunci_jawaban;
      kunciHtml = `<span class="review-key">${kl}</span>`;
    }

    rows.push(`
      <tr onclick="reviewJumpTo(${item.nomor - 1})" title="Klik untuk review soal ini">
        <td class="review-no">${item.nomor}</td>
        <td>${andaHtml}</td>
        <td>${kunciHtml}</td>
      </tr>
    `);
  });

  const totalItems = benar + salah + kosong;
  const persen = totalItems ? Math.round((benar / totalItems) * 100) : 0;

  document.getElementById('reviewMetaText').innerText =
    `${SUBJECT_CATALOG[state.currentSubject].name} — Paket ${state.currentPkg}`;
  document.getElementById('reviewScoreBenar').innerText = benar;
  document.getElementById('reviewScoreSalah').innerText = salah;
  document.getElementById('reviewScoreKosong').innerText = kosong;
  document.getElementById('reviewScorePersen').innerText = `${persen}%`;
  document.getElementById('reviewScorePersen').className =
    'review-persen ' + (persen >= 70 ? 'good' : persen >= 40 ? 'mid' : 'low');
  document.getElementById('reviewTableBody').innerHTML = rows.join('');

  document.getElementById('reviewHasilOverlay').classList.add('open');
}

// Klik baris reviu -> lompat ke soal terkait (pembahasan terbuka)
function reviewJumpTo(idx) {
  document.getElementById('reviewHasilOverlay').classList.remove('open');
  state.currentIndex = idx;
  state.explanationVisible = true;
  renderQuestion();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function closeReviewHasil() {
  document.getElementById('reviewHasilOverlay').classList.remove('open');
}

// Ulangi simulasi: reset jawaban & status ragu paket aktif
function resetSimulasi() {
  const key = pkgKey();
  state.userAnswers[key] = {};
  state.raguStatus[key] = {};
  state.simAnswers[key] = {};
  state.currentIndex = 0;
  state.explanationVisible = false;
  closeReviewHasil();
  renderQuestion();
  renderGridModal();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Toggle Ragu-ragu
function toggleRagu() {
  const q = getCurrentQuestion();
  if (!q) return;
  if (!state.raguStatus[pkgKey()]) state.raguStatus[pkgKey()] = {};
  const current = !!state.raguStatus[pkgKey()][q.nomor];
  state.raguStatus[pkgKey()][q.nomor] = !current;
  document.getElementById('chkRagu').checked = !current;
  renderGridModal();
}

// Render numbers in modal "Daftar Soal"
function renderGridModal() {
  const pkg = state.pkgData[pkgKey()];
  if (!pkg || !pkg.soal) return;

  const grid = document.getElementById('soalGrid');
  grid.innerHTML = '';

  pkg.soal.forEach((item, idx) => {
    const no = item.nomor;
    const btn = document.createElement('button');
    btn.className = 'grid-item';
    btn.innerText = no;

    const isCurrent = idx === state.currentIndex;
    const isAnswered = isQuestionAnswered(item);
    const isRagu = !!((state.raguStatus[pkgKey()] || {})[no]);

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

// Guard: konfirmasi sebelum menutup tab saat masih ada jawaban tersimpan
window.addEventListener('beforeunload', (e) => {
  const hasAnswers = Object.values(state.userAnswers).some(pkg =>
    pkg && Object.keys(pkg).length > 0);
  if (hasAnswers) {
    e.preventDefault();
    e.returnValue = '';
  }
});

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
