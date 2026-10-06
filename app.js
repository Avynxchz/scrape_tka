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
      1: 'data/matematika/paket_1/',
      2: 'data/matematika/paket_2/'
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
  },
  geografi: {
    name: 'Geografi',
    json: {
      1: 'data/geografi_paket_1_learning.json',
      2: 'data/geografi_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/geografi/paket_1/',
      2: 'data/geografi/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Geografi</strong>. Masih bingung dengan analisis peta, citra penginderaan jauh, fenomena geosfer, atau prinsip geografi pada soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  },
  fisika: {
    name: 'Fisika',
    json: {
      1: 'data/fisika_paket_1_learning.json',
      2: 'data/fisika_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/fisika/paket_1/',
      2: 'data/fisika/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Fisika</strong>. Masih bingung dengan penurunan rumus, diagram benda bebas, vektor, atau hukum fisika pada soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  },
  kimia: {
    name: 'Kimia',
    json: {
      1: 'data/kimia_paket_1_learning.json',
      2: 'data/kimia_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/kimia/paket_1/',
      2: 'data/kimia/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Kimia</strong>. Masih bingung dengan reaksi kimia, struktur molekul, hukum kesetimbangan, atau stoikiometri pada soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  },
  biologi: {
    name: 'Biologi',
    json: {
      1: 'data/biologi_paket_1_learning.json',
      2: 'data/biologi_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/biologi/paket_1/',
      2: 'data/biologi/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Biologi</strong>. Masih bingung dengan diagram organ, proses metabolisme sel, genetika, atau analisis eksperimen pada soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  },
  bahasa_indonesia: {
    name: 'Bahasa Indonesia',
    json: {
      1: 'data/bahasa_indonesia_paket_1_learning.json',
      2: 'data/bahasa_indonesia_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_indonesia/paket_1/',
      2: 'data/bahasa_indonesia/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Indonesia</strong>. Masih bingung dengan makna istilah, gagasan pokok wacana, atau kaidah kebahasaan pada soal ini? Tanyakan langsung di bawah ya!`
  },
  sosiologi: {
    name: 'Sosiologi',
    json: {
      1: 'data/sosiologi_paket_1_learning.json',
      2: 'data/sosiologi_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/sosiologi/paket_1/',
      2: 'data/sosiologi/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Sosiologi</strong>. Masih bingung dengan konsep teori sosiologi, fenomena sosial, atau dinamika kelompok pada soal ini? Tanyakan langsung di bawah ya!`
  },
  sejarah: {
    name: 'Sejarah',
    json: {
      1: 'data/sejarah_paket_1_learning.json',
      2: 'data/sejarah_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/sejarah/paket_1/',
      2: 'data/sejarah/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Sejarah</strong>. Masih bingung dengan kronologi, konteks peristiwa, atau analisis sumber sejarah pada soal ini? Tanyakan langsung di bawah ya!`
  },
  matematika_lanjut: {
    name: 'Matematika Tingkat Lanjut',
    json: {
      1: 'data/matematika_lanjut_paket_1_learning.json',
      2: 'data/matematika_lanjut_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/matematika_lanjut/paket_1/',
      2: 'data/matematika_lanjut/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Matematika Lanjut</strong>. Masih bingung dengan matriks, polinomial, trigonometri analitik, atau kalkulus lanjut pada soal ini? Tanyakan langsung di bawah ya!`
  },
  bahasa_indonesia_lanjut: {
    name: 'Bahasa Indonesia Tingkat Lanjut',
    json: {
      1: 'data/bahasa_indonesia_lanjut_paket_1_learning.json',
      2: 'data/bahasa_indonesia_lanjut_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_indonesia_lanjut/paket_1/',
      2: 'data/bahasa_indonesia_lanjut/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Indonesia Lanjut</strong>. Masih bingung dengan struktur teks sastra, telaah kritis karya, atau kaidah bahasa tingkat lanjut? Tanyakan langsung di bawah ya!`
  },
  bahasa_inggris_lanjut: {
    name: 'Bahasa Inggris Tingkat Lanjut',
    json: {
      1: 'data/bahasa_inggris_lanjut_paket_1_learning.json',
      2: 'data/bahasa_inggris_lanjut_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_inggris_lanjut/paket_1/',
      2: 'data/bahasa_inggris_lanjut/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Inggris Lanjut</strong>. Need help understanding the text, rhetorical devices, synthesis of arguments, or advanced vocabulary? Feel free to ask below!`
  },
  antropologi: {
    name: 'Antropologi',
    json: {
      1: 'data/antropologi_paket_1_learning.json',
      2: 'data/antropologi_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/antropologi/paket_1/',
      2: 'data/antropologi/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Antropologi</strong>. Masih bingung dengan konsep kebudayaan, etnografi, sistem kekerabatan, atau analisis dinamika budaya pada soal ini? Tanyakan langsung di bawah ya!`
  },
  ppkn: {
    name: 'Pendidikan Pancasila & Kewarganegaraan (PPKn)',
    json: {
      1: 'data/ppkn_paket_1_learning.json',
      2: 'data/ppkn_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/ppkn/paket_1/',
      2: 'data/ppkn/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA PPKn</strong>. Masih bingung dengan pasal-pasal konstitusi, sistem ketatanegaraan, hak asasi manusia, atau nilai-nilai Pancasila pada soal ini? Tanyakan langsung di bawah ya!`
  },
  bahasa_arab: {
    name: 'Bahasa Arab',
    json: {
      1: 'data/bahasa_arab_paket_1_learning.json',
      2: 'data/bahasa_arab_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_arab/paket_1/',
      2: 'data/bahasa_arab/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Arab</strong>. Masih bingung dengan qawaid (nahwu/sharaf), mufradat, atau pemahaman teks bahasa Arab pada soal ini? Tanyakan langsung di bawah ya!`
  },
  bahasa_jepang: {
    name: 'Bahasa Jepang',
    json: {
      1: 'data/bahasa_jepang_paket_1_learning.json',
      2: 'data/bahasa_jepang_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_jepang/paket_1/',
      2: 'data/bahasa_jepang/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Jepang</strong>. Masih bingung dengan kanji, pola kalimat (bunpou), kosakata, atau pemahaman teks (dokkai) pada soal ini? Tanyakan langsung di bawah ya!`
  },
  bahasa_jerman: {
    name: 'Bahasa Jerman',
    json: {
      1: 'data/bahasa_jerman_paket_1_learning.json',
      2: 'data/bahasa_jerman_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_jerman/paket_1/',
      2: 'data/bahasa_jerman/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Jerman</strong>. Masih bingung dengan gramatika (Kasus/Grammatik), kosakata (Wortschatz), atau pemahaman teks (Leseverstehen) pada soal ini? Tanyakan langsung di bawah ya!`
  },
  bahasa_prancis: {
    name: 'Bahasa Prancis',
    json: {
      1: 'data/bahasa_prancis_paket_1_learning.json',
      2: 'data/bahasa_prancis_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_prancis/paket_1/',
      2: 'data/bahasa_prancis/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Prancis</strong>. Masih bingung dengan tata bahasa (grammaire/conjugaison), kosakata (vocabulaire), atau pemahaman bacaan pada soal ini? Tanyakan langsung di bawah ya!`
  },
  bahasa_mandarin: {
    name: 'Bahasa Mandarin',
    json: {
      1: 'data/bahasa_mandarin_paket_1_learning.json',
      2: 'data/bahasa_mandarin_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_mandarin/paket_1/',
      2: 'data/bahasa_mandarin/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Mandarin</strong>. Masih bingung dengan hanzi, pinyin, tata bahasa (yufa), atau pemahaman wacana pada soal ini? Tanyakan langsung di bawah ya!`
  },
  bahasa_korea: {
    name: 'Bahasa Korea',
    json: {
      1: 'data/bahasa_korea_paket_1_learning.json',
      2: 'data/bahasa_korea_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/bahasa_korea/paket_1/',
      2: 'data/bahasa_korea/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Bahasa Korea</strong>. Masih bingung dengan hangeul, partikel, tata bahasa (munbeop), atau pemahaman bacaan pada soal ini? Tanyakan langsung di bawah ya!`
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
  selectedTutorModel: localStorage.getItem('tka_tutor_model') || 'qwen-groq',
  explanationVisible: false
};

function pkgKey(pkg = state.currentPkg) {
  return `${state.currentSubject}:${pkg}`;
}

// Dynamic synchronization of all subjects and packages from server catalog
async function syncDynamicCatalog() {
  try {
    const res = await fetch('/api/swarm/subjects');
    if (!res.ok) return;
    const data = await res.json();
    const subjects = data.subjects || {};

    const mapelGroups = {};
    for (const [slug, item] of Object.entries(subjects)) {
      const mk = item.mapel_key;
      const kat = item.kategori || 'Pilihan';
      if (!mapelGroups[kat]) mapelGroups[kat] = {};
      if (!mapelGroups[kat][mk]) {
        mapelGroups[kat][mk] = {
          name: item.name.replace(/\s*\(Paket\s*\d+\)/i, '').trim(),
          packages: {}
        };
      }
      mapelGroups[kat][mk].packages[item.paket] = item.status === 'live';

      if (!SUBJECT_CATALOG[mk]) {
        SUBJECT_CATALOG[mk] = {
          name: mapelGroups[kat][mk].name,
          json: {
            1: `data/${mk}_paket_1_learning.json`,
            2: `data/${mk}_paket_2_learning.json`
          },
          imgBase: {
            1: `data/${mk}/paket_1/`,
            2: `data/${mk}/paket_2/`
          },
          welcome: `Halo! Saya <strong>AI Tutor TKA ${mapelGroups[kat][mk].name}</strong>. Masih bingung dengan konsep atau langkah pengerjaan pada soal ini? Tanyakan langsung di bawah ya!`
        };
      }
    }

    const select = document.getElementById('subjectSelect');
    if (select) {
      const currVal = state.currentSubject;
      let html = '';
      for (const [kat, mapels] of Object.entries(mapelGroups)) {
        html += `<optgroup label="${kat}">`;
        for (const [mk, info] of Object.entries(mapels)) {
          const liveCount = Object.values(info.packages).filter(Boolean).length;
          const liveTag = liveCount > 0 ? ` [${liveCount} Paket Live]` : ' (Belum Scrape)';
          html += `<option value="${mk}">${info.name}${liveTag}</option>`;
        }
        html += `</optgroup>`;
      }
      select.innerHTML = html;
      select.value = currVal;
    }
  } catch (err) {
    console.warn("syncDynamicCatalog error:", err);
  }
}

// Initialize Application on Page Load
document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const paramSub = urlParams.get('subject');
  const paramPkg = parseInt(urlParams.get('paket') || '1', 10);
  // Home overlay tampil pertama kecuali user langsung menuju soal tertentu (#soal-N)
  window.__homeFirst = !window.location.hash.startsWith('#soal-');

  await syncDynamicCatalog();

  if (paramSub && SUBJECT_CATALOG[paramSub]) {
    state.currentSubject = paramSub;
    state.currentPkg = paramPkg === 2 ? 2 : 1;
    const select = document.getElementById('subjectSelect');
    if (select) select.value = paramSub;
  }

  await loadPackageData(state.currentPkg);
  loadPackageData(state.currentPkg === 1 ? 2 : 1);
  updateSubjectUI();
  renderQuestion();
  updateModelPickerUI();
  renderGridModal();

  // Layar pertama: Home dashboard (kecuali langsung diarahkan ke soal via #soal-N)
  if (window.__homeFirst) homeOpen();
});
// 22 Mata Pelajaran TKA Master — Meta UI, Ikon Unik Material Symbols, & Tema Warna Harmonis
const SUBJECT_UI_META = {
  matematika: {
    name: 'Matematika (Wajib)', shortName: 'Matematika', chip: 'MATEMATIKA',
    icon: 'calculate', theme: 'blue', category: 'Wajib'
  },
  bahasa_indonesia: {
    name: 'Bahasa Indonesia (Wajib)', shortName: 'B. Indonesia', chip: 'B. INDONESIA',
    icon: 'menu_book', theme: 'emerald', category: 'Wajib'
  },
  bahasa_inggris: {
    name: 'Bahasa Inggris (Wajib)', shortName: 'B. Inggris', chip: 'B. INGGRIS',
    icon: 'language', theme: 'indigo', category: 'Wajib'
  },
  fisika: {
    name: 'Fisika (Peminatan)', shortName: 'Fisika', chip: 'FISIKA',
    icon: 'bolt', theme: 'amber', category: 'Saintek'
  },
  kimia: {
    name: 'Kimia (Peminatan)', shortName: 'Kimia', chip: 'KIMIA',
    icon: 'science', theme: 'teal', category: 'Saintek'
  },
  biologi: {
    name: 'Biologi (Peminatan)', shortName: 'Biologi', chip: 'BIOLOGI',
    icon: 'biotech', theme: 'green', category: 'Saintek'
  },
  ekonomi: {
    name: 'Ekonomi (Peminatan)', shortName: 'Ekonomi', chip: 'EKONOMI',
    icon: 'payments', theme: 'orange', category: 'Soshum'
  },
  geografi: {
    name: 'Geografi (Peminatan)', shortName: 'Geografi', chip: 'GEOGRAFI',
    icon: 'public', theme: 'cyan', category: 'Soshum'
  },
  sosiologi: {
    name: 'Sosiologi (Peminatan)', shortName: 'Sosiologi', chip: 'SOSIOLOGI',
    icon: 'groups', theme: 'rose', category: 'Soshum'
  },
  sejarah: {
    name: 'Sejarah (Peminatan)', shortName: 'Sejarah', chip: 'SEJARAH',
    icon: 'landmark', theme: 'purple', category: 'Soshum'
  },
  antropologi: {
    name: 'Antropologi (Peminatan)', shortName: 'Antropologi', chip: 'ANTROPOLOGI',
    icon: 'diversity_3', theme: 'amber', category: 'Soshum'
  },
  kewirausahaan: {
    name: 'Kewirausahaan (PKWU)', shortName: 'PKWU', chip: 'PKWU',
    icon: 'storefront', theme: 'lime', category: 'Soshum'
  },
  matematika_lanjut: {
    name: 'Matematika Lanjut', shortName: 'Matematika Lanjut', chip: 'MTK LANJUT',
    icon: 'functions', theme: 'blue', category: 'Lanjut'
  },
  bahasa_indonesia_lanjut: {
    name: 'Bahasa Indonesia Lanjut', shortName: 'B. Indo Lanjut', chip: 'INDO LANJUT',
    icon: 'auto_stories', theme: 'teal', category: 'Lanjut'
  },
  bahasa_inggris_lanjut: {
    name: 'Bahasa Inggris Lanjut', shortName: 'B. Inggris Lanjut', chip: 'INGGRIS LANJUT',
    icon: 'translate', theme: 'violet', category: 'Lanjut'
  },
  ppkn: {
    name: 'PPKn', shortName: 'PPKn', chip: 'PPKN',
    icon: 'gavel', theme: 'red', category: 'Lintas Minat'
  },
  bahasa_arab: {
    name: 'Bahasa Arab', shortName: 'B. Arab', chip: 'B. ARAB',
    icon: 'edit_note', theme: 'emerald', category: 'Bahasa Asing'
  },
  bahasa_jepang: {
    name: 'Bahasa Jepang', shortName: 'B. Jepang', chip: 'B. JEPANG',
    icon: 'wb_sunny', theme: 'rose', category: 'Bahasa Asing'
  },
  bahasa_jerman: {
    name: 'Bahasa Jerman', shortName: 'B. Jerman', chip: 'B. JERMAN',
    icon: 'castle', theme: 'yellow', category: 'Bahasa Asing'
  },
  bahasa_prancis: {
    name: 'Bahasa Prancis', shortName: 'B. Prancis', chip: 'B. PRANCIS',
    icon: 'architecture', theme: 'sky', category: 'Bahasa Asing'
  },
  bahasa_mandarin: {
    name: 'Bahasa Mandarin', shortName: 'B. Mandarin', chip: 'B. MANDARIN',
    icon: 'brush', theme: 'red', category: 'Bahasa Asing'
  },
  bahasa_korea: {
    name: 'Bahasa Korea', shortName: 'B. Korea', chip: 'B. KOREA',
    icon: 'stars', theme: 'pink', category: 'Bahasa Asing'
  }
};
window.SUBJECT_UI_META = SUBJECT_UI_META;

// Watermark geometris per rumpun mapel
const HOME_WATERMARKS = {
  matematika: '<path d="M25 25 L75 25 L45 50 L75 75 L25 75" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="5"/><circle cx="70" cy="50" fill="none" r="8" stroke="currentColor" stroke-width="2.5"/>',
  fisika: '<ellipse cx="50" cy="50" rx="38" ry="14" stroke-width="2.5" transform="rotate(30 50 50)"/><ellipse cx="50" cy="50" rx="38" ry="14" stroke-width="2.5" transform="rotate(90 50 50)"/><ellipse cx="50" cy="50" rx="38" ry="14" stroke-width="2.5" transform="rotate(150 50 50)"/><circle cx="50" cy="50" fill="currentColor" r="5"/>',
  kimia: '<path d="M40 20 L40 40 L20 75 L80 75 L60 40 L60 20" stroke="currentColor" stroke-width="4" stroke-linejoin="round" fill="none"/><line x1="32" y1="20" x2="68" y2="20" stroke="currentColor" stroke-width="4"/><circle cx="50" cy="62" r="5" fill="currentColor"/>',
  biologi: '<circle cx="50" cy="50" r="30" stroke="currentColor" stroke-width="3" fill="none"/><path d="M35 50 Q50 30 65 50 T95 50" stroke="currentColor" stroke-width="3" fill="none"/>',
  _default: '<path d="M10 80 L50 15 L90 80 Z" fill="none" stroke="currentColor" stroke-width="4"/><circle cx="50" cy="55" fill="none" r="16" stroke="currentColor" stroke-width="3"/><path d="M25 80 L75 80" stroke="currentColor" stroke-dasharray="4,4" stroke-width="3"/>',
};
const HOME_PKG_MINUTES = { 1: 45, 2: 50 };

// Progres nyata per paket dari jawaban user yang tersimpan (localStorage)
function homePkgProgress(subjectKey, pkgNum, total) {
  if (!total) return 0;
  try {
    const raw = localStorage.getItem('tka_progress');
    const store = raw ? JSON.parse(raw) : {};
    const answered = (store[subjectKey] && store[subjectKey][pkgNum]) || {};
    return Math.min(100, Math.round((Object.keys(answered).length / total) * 100));
  } catch (e) { return 0; }
}
const HOME_PKG_DESC = {
  1: 'Latihan + pembahasan + AI Tutor',
  2: 'Latihan lanjutan + AI Tutor',
};

// Data statis jumlah soal real dari KONTRAK_DATA.md — 0ms render & tanpa fetch berulang
const STATIC_SOAL_COUNTS = {
  matematika: { 1: 46, 2: 25 },
  bahasa_indonesia: { 1: 20, 2: 25 },
  bahasa_inggris: { 1: 20, 2: 25 },
  fisika: { 1: 20, 2: 24 },
  kimia: { 1: 20, 2: 24 },
  biologi: { 1: 20, 2: 29 },
  ekonomi: { 1: 20, 2: 29 },
  geografi: { 1: 10, 2: 29 },
  sosiologi: { 1: 20, 2: 30 },
  sejarah: { 1: 10, 2: 29 },
  antropologi: { 1: 10, 2: 30 },
  kewirausahaan: { 1: 10, 2: 30 },
  matematika_lanjut: { 1: 20, 2: 25 },
  bahasa_indonesia_lanjut: { 1: 10, 2: 29 },
  bahasa_inggris_lanjut: { 1: 10, 2: 29 },
  ppkn: { 1: 20, 2: 29 },
  bahasa_arab: { 1: 10, 2: 29 },
  bahasa_jepang: { 1: 10, 2: 29 },
  bahasa_jerman: { 1: 10, 2: 29 },
  bahasa_prancis: { 1: 10, 2: 29 },
  bahasa_mandarin: { 1: 10, 2: 29 },
  bahasa_korea: { 1: 10, 2: 29 }
};
const HOME_SOAL_COUNTS = Object.assign({}, STATIC_SOAL_COUNTS);

function homePkgCount(subjectKey, pkgNum) {
  const meta = SUBJECT_CATALOG[subjectKey];
  if (!meta) return null;
  if (subjectKey === state.currentSubject) {
    const cached = state.pkgData[pkgKey(pkgNum)];
    if (cached && cached.soal) return cached.soal.length;
  }
  return (HOME_SOAL_COUNTS[subjectKey] || {})[pkgNum] || (STATIC_SOAL_COUNTS[subjectKey] || {})[pkgNum] || 20;
}

// Pre-seeded: instan selesai tanpa 44 network fetch yang membebani Beranda
function homePrefetchCounts() {
  return Promise.resolve();
}

// Pengelolaan Mapel Pilihan User (localStorage: tka_user_subjects)
function getUserSelectedSubjects() {
  try {
    const raw = localStorage.getItem('tka_user_subjects');
    if (raw) {
      const arr = JSON.parse(raw);
      if (Array.isArray(arr) && arr.length > 0) {
        const valid = arr.filter(k => SUBJECT_CATALOG[k]);
        if (valid.length > 0) return valid;
      }
    }
  } catch (e) {}
  // Default mapel pilihan user: 4 mapel (Wajib + 1 Peminatan Saintek)
  return ['matematika', 'bahasa_indonesia', 'bahasa_inggris', 'fisika'];
}

function setUserSelectedSubjects(keys) {
  try {
    localStorage.setItem('tka_user_subjects', JSON.stringify(keys));
  } catch (e) {}
  renderHome();
}
window.getUserSelectedSubjects = getUserSelectedSubjects;
window.setUserSelectedSubjects = setUserSelectedSubjects;

// Modal Atur Mapel Pilihan
function openSubjectPickerModal() {
  let backdrop = document.getElementById('subjectModalBackdrop');
  if (!backdrop) {
    createSubjectPickerModalDOM();
    backdrop = document.getElementById('subjectModalBackdrop');
  }
  const list = document.getElementById('subjectPickerList');
  if (!backdrop || !list) return;
  const current = getUserSelectedSubjects();
  list.innerHTML = Object.keys(SUBJECT_UI_META).map(k => {
    const meta = SUBJECT_UI_META[k];
    const checked = current.includes(k) ? 'checked' : '';
    const selClass = current.includes(k) ? 'selected' : '';
    return `
      <label class="stitch-modal-item ${selClass}" data-key="${k}">
        <div class="stitch-modal-item-left">
          <span class="stitch-iconchip stitch-iconchip--${meta.theme}"><span class="ms-icon">${meta.icon}</span></span>
          <div>
            <div class="stitch-modal-item-name">${meta.shortName}</div>
            <div class="stitch-modal-item-cat">${meta.category}</div>
          </div>
        </div>
        <input type="checkbox" name="subject_pick" value="${k}" ${checked}>
      </label>
    `;
  }).join('');
  list.querySelectorAll('.stitch-modal-item').forEach(item => {
    const chk = item.querySelector('input');
    chk.addEventListener('change', () => {
      item.classList.toggle('selected', chk.checked);
    });
  });
  backdrop.style.display = 'flex';
}

function closeSubjectPickerModal() {
  const backdrop = document.getElementById('subjectModalBackdrop');
  if (backdrop) backdrop.style.display = 'none';
}

function saveSubjectPickerModal() {
  const list = document.getElementById('subjectPickerList');
  if (!list) return;
  const checked = Array.from(list.querySelectorAll('input[name="subject_pick"]:checked')).map(el => el.value);
  if (checked.length === 0) {
    alert('Pilih minimal 1 mata pelajaran.');
    return;
  }
  setUserSelectedSubjects(checked);
  closeSubjectPickerModal();
}

function createSubjectPickerModalDOM() {
  const div = document.createElement('div');
  div.id = 'subjectModalBackdrop';
  div.className = 'stitch-modal-backdrop';
  div.style.display = 'none';
  div.innerHTML = `
    <div class="stitch-modal-panel">
      <div class="stitch-modal-handle"></div>
      <div class="stitch-modal-header">
        <div>
          <h3 class="stitch-modal-title">Pilih Mapel Dashboard</h3>
          <p class="stitch-modal-desc">Pilih mapel yang ingin dipelajari dan ditampilkan di beranda.</p>
        </div>
        <button type="button" class="stitch-modal-close" onclick="closeSubjectPickerModal()" aria-label="Tutup"><span class="ms-icon">close</span></button>
      </div>
      <div class="stitch-modal-body" id="subjectPickerList"></div>
      <div class="stitch-modal-footer">
        <button type="button" class="stitch-btn-modal-cancel" onclick="closeSubjectPickerModal()">Batal</button>
        <button type="button" class="stitch-btn-modal-apply" onclick="saveSubjectPickerModal()">Terapkan Pilihan</button>
      </div>
    </div>
  `;
  document.body.appendChild(div);
  div.addEventListener('click', (e) => {
    if (e.target === div) closeSubjectPickerModal();
  });
}
window.openSubjectPickerModal = openSubjectPickerModal;
window.closeSubjectPickerModal = closeSubjectPickerModal;
window.saveSubjectPickerModal = saveSubjectPickerModal;

function renderHome() {
  const main = document.getElementById('hoMain');
  if (!main) return;
  const selectedKeys = getUserSelectedSubjects();

  const sectionsHtml = selectedKeys.map(k => {
    const meta = SUBJECT_UI_META[k] || {
      name: (SUBJECT_CATALOG[k] && SUBJECT_CATALOG[k].name) || k,
      shortName: k,
      chip: k.toUpperCase(),
      icon: 'school',
      theme: 'blue',
      category: 'Mapel'
    };
    const wm = HOME_WATERMARKS[k] || HOME_WATERMARKS._default;
    const cards = [1, 2].map(pkg => {
      const n = homePkgCount(k, pkg);
      const total = n || 20;
      const pct = homePkgProgress(k, pkg, total);
      const isNew = pct === 0;
      return `
      <button class="stitch-card stitch-theme-${meta.theme}" type="button" data-subject="${k}" data-pkg="${pkg}"
        aria-label="${meta.shortName} Paket ${pkg}">
        ${isNew ? '<span class="stitch-newwrap"><span>Baru</span></span>' : ''}
        <svg class="stitch-watermark" fill="none" stroke="currentColor" viewBox="0 0 100 100" aria-hidden="true">${wm}</svg>
        <div>
          <h3>Paket ${pkg}</h3>
          <p class="stitch-meta"><span class="ms-icon">schedule</span><span>${total} Soal • ${(HOME_PKG_MINUTES[pkg] || 45)} Menit</span></p>
          <span class="stitch-chip">${meta.chip}</span>
        </div>
        <div class="stitch-progress">
          <div class="stitch-progress-labels"><span>Progres Penyelesaian</span><b class="${pct > 0 ? 'on' : ''}">${pct}%</b></div>
          <div class="stitch-bar"><span class="${pct > 0 ? 'on' : ''}" style="width:${pct}%"></span></div>
        </div>
      </button>`;
    }).join('');

    return `
      <section class="stitch-section" data-subject="${k}">
        <div class="stitch-sec-head">
          <div class="stitch-sec-title">
            <span class="stitch-iconchip stitch-iconchip--${meta.theme}"><span class="ms-icon">${meta.icon}</span></span>
            <div>
              <h2>${meta.shortName}</h2>
              <span class="stitch-sec-sub">${meta.category}</span>
            </div>
          </div>
        </div>
        <div class="stitch-cards">${cards}</div>
      </section>`;
  }).join('');

  main.innerHTML = `
    <div class="stitch-mapel-header">
      <div class="stitch-mapel-header-left">
        <span class="stitch-mapel-header-title">Mapel Pilihanmu</span>
        <span class="stitch-mapel-header-count">(${selectedKeys.length} Mapel)</span>
      </div>
      <button type="button" class="stitch-btn-atur-mapel" id="btnAturMapel" onclick="openSubjectPickerModal()" aria-label="Atur Mapel Pilihan">
        <span class="ms-icon ms-16">tune</span><span>Atur Mapel</span>
      </button>
    </div>
    ${sectionsHtml}
  `;

  // klik card paket -> masuk soal via fungsi yang sudah ada
  main.querySelectorAll('.stitch-card').forEach(card => {
    card.addEventListener('click', async () => {
      const subject = card.dataset.subject, pkg = parseInt(card.dataset.pkg, 10);
      homeClose();
      if (state.currentSubject !== subject) await switchSubject(subject);
      await switchPackage(pkg);
    });
  });

  // CTA hero -> lanjut mapel aktif
  const heroCta = document.getElementById('heroCta');
  if (heroCta) heroCta.onclick = () => { homeClose(); window.scrollTo(0, 0); };

  // nav bawah mobile: switcher panel Beranda / Modul / Progres / Akun
  document.querySelectorAll('.stitch-bottomnav a').forEach(a => {
    a.onclick = (e) => {
      e.preventDefault();
      const nav = a.dataset.nav;
      if (nav === 'modul' || nav === 'progres' || nav === 'akun' || nav === 'beranda') homeShowPanel(nav);
    };
  });

  // slide 2 hero: ringkasan progres real
  try {
    const s = homeProgressSummary();
    const hsDone = document.getElementById('hsDone');
    if (hsDone) hsDone.textContent = s.dikerjakan;
    const hsBenar = document.getElementById('hsBenar');
    if (hsBenar) hsBenar.textContent = s.benar;
    const hsAcc = document.getElementById('hsAcc');
    if (hsAcc) hsAcc.textContent = s.dikerjakan ? s.tepat + '%' : '—';
  } catch (e) {}
  initHeroCarousel();
}

// Reusable Carousel Controller (dipakai di Beranda Fase 7 & Modul Fase 8)
function setupCarouselController(carEl, dotsElOrSelector) {
  if (!carEl) return null;
  const dots = typeof dotsElOrSelector === 'string' 
    ? document.querySelectorAll(dotsElOrSelector) 
    : (dotsElOrSelector || []);
  const sync = () => {
    if (!carEl.clientWidth) return;
    const idx = Math.max(0, Math.min(dots.length - 1, Math.round(carEl.scrollLeft / carEl.clientWidth)));
    dots.forEach((d, i) => d.classList.toggle('on', i === idx));
  };
  carEl.addEventListener('scroll', () => requestAnimationFrame(sync), { passive: true });
  dots.forEach((d, i) => {
    d.addEventListener('click', () => {
      carEl.scrollTo({ left: i * carEl.clientWidth, behavior: 'smooth' });
    });
  });
  sync();
  return { sync };
}
window.setupCarouselController = setupCarouselController;

let _heroCarouselBound = false;
function initHeroCarousel() {
  const car = document.getElementById('heroCarousel');
  const dots = document.querySelectorAll('#heroDots i');
  if (!car || !dots.length) return;
  if (!_heroCarouselBound) {
    _heroCarouselBound = true;
    setupCarouselController(car, dots);
  }
}

function homeOpen() {
  const ov = document.getElementById('homeOverlay');
  if (!ov) return;
  ov.classList.remove('home-hidden');
  document.body.style.overflow = 'hidden';
  // Kembali ke beranda: hapus tanda mode kuis
  delete document.body.dataset.quizMode;
  renderHome();
  homeShowPanel('beranda'); // default yang tampil: Beranda
  // prefetch jumlah soal semua mapel; render ulang saat selesai biar angka lengkap
  homePrefetchCounts().then(() => { if (homeIsOpen()) { renderHome(); homeSendDesktopData(); } });
  homeSendDesktopData();
}

// Ringkasan progres nyata dari localStorage tka_progress
function homeProgressSummary() {
  try {
    const raw = localStorage.getItem('tka_progress');
    const store = raw ? JSON.parse(raw) : {};
    let dikerjakan = 0, benar = 0;
    Object.values(store || {}).forEach(pkgs => {
      Object.values(pkgs || {}).forEach(soal => {
        Object.values(soal || {}).forEach(ans => {
          dikerjakan++;
          if (ans && ans.benar) benar++;
        });
      });
    });
    return { dikerjakan, benar, tepat: dikerjakan ? Math.round((benar / dikerjakan) * 100) : 0 };
  } catch (e) { return { dikerjakan: 0, benar: 0, tepat: 0 }; }
}

// Kirim data nyata ke iframe desktop (home_desktop.html).
// Panel lain (Modul/Progres) memakai helper yang sama lewat postToFrameReliable().
function homeSendDesktopData() {
  const frame = document.getElementById('homeDesktopFrame');
  postToFrameReliable(frame, () => ({
    type: 'home-desktop-data',
    subjects: buildSubjectsPayload(['matematika', 'fisika', 'ekonomi']),
    progress: homeProgressSummary(),
  }));
}

// Urutan 22 mapel sesuai daftar KONTRAK_DATA.md (dipakai panel Modul & Progres)
const PANEL_MODULE_ORDER = ['matematika', 'bahasa_indonesia', 'bahasa_inggris', 'fisika', 'kimia', 'biologi', 'ekonomi', 'geografi', 'sosiologi', 'sejarah', 'antropologi', 'kewirausahaan', 'matematika_lanjut', 'bahasa_indonesia_lanjut', 'bahasa_inggris_lanjut', 'ppkn', 'bahasa_arab', 'bahasa_jepang', 'bahasa_jerman', 'bahasa_prancis', 'bahasa_mandarin', 'bahasa_korea'];

// Raw store tka_progress (bentuk persis kontrak, bukan ringkasan)
function homeProgressStore() {
  try {
    const r = JSON.parse(localStorage.getItem('tka_progress') || '{}');
    return (r && typeof r === 'object' && !Array.isArray(r)) ? r : {};
  } catch (e) { return {}; }
}

function buildSubjectsPayload(keyOrder) {
  const subjects = [];
  keyOrder.forEach(k => {
    const meta = SUBJECT_CATALOG[k] || {};
    [1, 2].forEach(pkg => {
      subjects.push({
        subject: k, pkg,
        label: meta.name || k,
        count: homePkgCount(k, pkg),
        minutes: pkg === 1 ? 45 : 50,
        progress: homePkgProgress(k, pkg, homePkgCount(k, pkg) || 0),
      });
    });
  });
  return subjects;
}

// Daftar 22 mapel + jumlah soal real (untuk panel Progres)
function buildSubjectsSummary() {
  return PANEL_MODULE_ORDER.map(k => {
    const meta = SUBJECT_CATALOG[k] || {};
    return { key: k, label: meta.name || k, soal: { 1: homePkgCount(k, 1), 2: homePkgCount(k, 2) } };
  });
}

// Kirim payload ke frame dengan retry: iframe bisa saja belum load, dan data
// bisa berubah di antara retry (prefetch count selesai, jawaban baru).
function postToFrameReliable(frame, buildPayload) {
  if (!frame) return;
  let tries = 0;
  const maxTries = frame.dataset.loaded === '1' ? 1 : 3;
  const send = () => {
    tries++;
    try { frame.contentWindow.postMessage(buildPayload(), '*'); } catch (e) {}
    if (tries < maxTries) setTimeout(send, 400);
  };
  // Siap kirim? (1) pernah ditandai loaded, atau (2) dokumen iframe sudah keluar
  // dari state "loading". Cek langsung — kalau hanya mengandalkan event 'load',
  // kirim bisa bolong kalau iframe selesai load sebelum fungsi ini dipanggil.
  let ready = false;
  try {
    ready = frame.dataset.loaded === '1' ||
      (frame.contentWindow && frame.contentWindow.document && frame.contentWindow.document.readyState !== 'loading');
  } catch (e) { ready = false; }
  if (ready) {
    frame.dataset.loaded = '1';
    send();
  } else {
    frame.addEventListener('load', () => { frame.dataset.loaded = '1'; send(); }, { once: true });
  }
}

// Toast kecil mandiri (fase 3): dipakai untuk menu yang halamannya belum ada.
// Membuat elemen sendiri + inline style supaya tidak bergantung pada style.css.
function showMiniToast(msg) {
  try {
    let t = document.getElementById('miniToast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'miniToast';
      t.style.cssText = 'position:fixed;left:50%;bottom:84px;transform:translateX(-50%) translateY(20px);'
        + 'background:rgba(17,24,39,.94);color:#fff;font-size:13px;padding:10px 18px;border-radius:999px;'
        + 'z-index:99999;opacity:0;transition:opacity .25s,transform .25s;pointer-events:none;max-width:88vw;'
        + 'text-align:center;box-shadow:0 6px 24px rgba(0,0,0,.25);';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    requestAnimationFrame(() => { t.style.opacity = '1'; t.style.transform = 'translateX(-50%) translateY(0)'; });
    clearTimeout(showMiniToast._h);
    showMiniToast._h = setTimeout(() => {
      t.style.opacity = '0'; t.style.transform = 'translateX(-50%) translateY(20px)';
    }, 2200);
  } catch (e) { console.warn('toast gagal', e); }
}

// Terima event dari iframe panel (klik paket, nav, sinyal ready)
const panelReadyReplied = {}; // throttle balasan sinyal ready per panel
window.addEventListener('message', async (e) => {
  const d = e.data || {};
  if (d.type === 'open-package') {
    homeClose();
    try {
      if (state.currentSubject !== d.subject) await switchSubject(d.subject);
      await switchPackage(d.pkg);
    } catch (err) { console.error(err); }
  } else if (d.type === 'home-desktop-ready' || d.type === 'modul-ready' || d.type === 'request-data') {
    // Halaman panel baru saja siap -> kirim data terbaru ke frame yang bersangkutan.
    // Ini menutup race apapun urutan antara load iframe dan init app.
    // Throttle 1 detik per frame: jangan ikuti ping-pong kalau halaman spam ready.
    const pairs = [['homeDesktopFrame', 'beranda'], ['panelModulFrame', 'modul'], ['panelProgresFrame', 'progres'], ['panelAkunFrame', 'akun']];
    const hit = pairs.find(([id]) => {
      const el = document.getElementById(id);
      try { return el && el.contentWindow === e.source; } catch (err) { return false; }
    });
    if (hit) {
      const now = Date.now();
      if (now - (panelReadyReplied[hit[1]] || 0) > 1000) {
        panelReadyReplied[hit[1]] = now;
        sendPanelData(hit[1]);
      }
    
    } else if (d.type === 'login-google') {
  // Iframe (home_desktop) minta login Google — jalanin di window utama
  // (Google blokir OAuth dalam iframe). supabase_auth.js dimuat di parent.
  if (typeof loginWithGoogle === 'function') {
    loginWithGoogle();
  }

  } else if (d.type === 'nav' || d.type === 'nav-tab') {
    // Panel switcher: pesan dari iframe panel mana pun (Beranda/Modul/Progres).
    // Halaman untuk FAQ, Bank Soal dll. belum ada -> tampilkan toast "segera hadir",
    // tetap di overlay saat ini (jangan lempar ke layar soal; dulu homeClose() membingungkan).
    const p = String(d.path || d.tab || '').toLowerCase();
    if (p.includes('modul')) homeShowPanel('modul');
    else if (p.includes('progres') || p.includes('analitik')) homeShowPanel('progres');
    else if (p.includes('akun')) homeShowPanel('akun');
    else if (p.includes('beranda')) homeShowPanel('beranda');
    else showMiniToast('Halaman ini segera hadir 🙏');
  }
});

// ==================== PANEL SWITCHER (Beranda / Modul / Progres) ====================
let homeActivePanel = 'beranda';

function homeShowPanel(name) {
  const ov = document.getElementById('homeOverlay');
  if (!ov) return;
  if (name !== 'beranda' && name !== 'modul' && name !== 'progres' && name !== 'akun') return;
  homeActivePanel = name;

  ov.classList.remove('show-panel-modul', 'show-panel-progres', 'show-panel-akun');
  if (name !== 'beranda') ov.classList.add('show-panel-' + name);

  ['Beranda', 'Modul', 'Progres', 'Akun'].forEach(p => {
    const el = document.getElementById('panel' + p);
    if (el) el.classList.toggle('panel-active', p.toLowerCase() === name);
  });

  // highlight bottom nav mobile
  document.querySelectorAll('.stitch-bottomnav a[data-nav]').forEach(a => {
    a.classList.toggle('on', a.getAttribute('data-nav') === name);
  });

  // Setiap panel dibuka: kirim data terbaru (raw store tka_progress + summary + daftar mapel)
  if (name === 'beranda') {
    // iframe Beranda bisa saja ter-reload selama panelnya disembunyikan —
    // kirim ulang data supaya kartu tidak balik ke placeholder statis
    sendPanelData('beranda');
  }
  if (name === 'modul') {
    sendPanelData('modul');
  }
  if (name === 'progres') {
    sendPanelData('progres');
  }
  if (name === 'akun') {
    sendPanelData('akun');
  }
}

// Kirim data terkini ke satu panel. Dipakai homeShowPanel + handler sinyal ready.
function sendPanelData(panel) {
  if (panel === 'beranda') {
    homeSendDesktopData();
    return;
  }
  const frameId = panel === 'modul' ? 'panelModulFrame'
    : panel === 'akun' ? 'panelAkunFrame' : 'panelProgresFrame';
  const frame = document.getElementById(frameId);
  if (frame && frame.contentWindow && typeof currentTextScale !== 'undefined') {
    try {
      frame.contentWindow.postMessage({ type: 'set-font-scale', scale: currentTextScale }, '*');
    } catch (e) {}
  }
  if (panel === 'akun') {
    // profil: sistem login belum ada -> null (halaman tampil mode Tamu yang jujur).
    // kuota AI: data server-side via state.tutorQuota (null jika belum buka sesi tutor).
    postToFrameReliable(frame, () => ({
      type: 'akun-data',
      profile: state.akunProfile || null,
      quota: state.tutorQuota || null,
      summary: homeProgressSummary(),
      progress: homeProgressStore(),
    }));
    return;
  }
  postToFrameReliable(frame, () => ({
    type: 'progress-data',
    progress: homeProgressStore(),
    summary: homeProgressSummary(),
    subjects: buildSubjectsSummary(),
  }));
  if (panel === 'modul') {
    // format home-desktop-data juga dikirim (subjects 22 mapel × 2 paket, urut kontrak)
    postToFrameReliable(frame, () => ({
      type: 'home-desktop-data',
      subjects: buildSubjectsPayload(PANEL_MODULE_ORDER),
      progress: homeProgressSummary(),
    }));
  }
}

function homeClose() {
  const ov = document.getElementById('homeOverlay');
  if (!ov) return;
  ov.classList.add('home-hidden');
  document.body.style.overflow = '';
  // Tandai mode kuis: di desktop, pemilih mapel & paket disembunyikan
  // (user sudah memilih di beranda, tidak perlu ganti-ganti di tengah kuis)
  document.body.dataset.quizMode = '1';
}

function homeIsOpen() {
  const ov = document.getElementById('homeOverlay');
  return !!ov && !ov.classList.contains('home-hidden');
}
window.homeIsOpen = homeIsOpen;

// Tombol Home di header app: kembali ke dashboard
function homeToggle() { homeIsOpen() ? homeClose() : homeOpen(); }
window.homeToggle = homeToggle;

// Carousel dots hero
(function () {
  const track = document.getElementById('hoHeroTrack'), dots = document.getElementById('hoHeroDots');
  if (!track || !dots) return;
  track.addEventListener('scroll', () => {
    const i = Math.round(track.scrollLeft / (track.scrollWidth / track.children.length));
    [...dots.children].forEach((d, j) => d.classList.toggle('on', j === i));
  }, { passive: true });
})();

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
  // Audit Manus: brand tetap konsisten dengan landing, mapel jadi konteks sekunder
  document.getElementById('brandTitle').innerText = 'TKA Master';
  const brandSub = document.getElementById('brandSubtitle');
  if (brandSub) brandSub.innerText = `Simulasi ${meta.name} · Paket ${state.currentPkg}`;
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

  // Pasang class mapel pada body (misal .subject-bahasa_arab untuk arah RTL)
  document.body.className = `subject-${state.currentSubject}`;
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
  const key = pkgKey(pkgNum);
  if (!state.pkgData[key] || !state.pkgData[key].soal || state.pkgData[key].soal.length === 0) {
    alert(`Paket ${pkgNum} untuk ${SUBJECT_CATALOG[state.currentSubject]?.name || state.currentSubject} belum selesai di-scrape.`);
    return;
  }

  state.currentPkg = pkgNum;
  state.currentIndex = 0;
  state.explanationVisible = false;

  updateSubjectUI();
  renderQuestion();
  renderGridModal();
}

// ==================== FASE 3: Keluar ke beranda dengan konfirmasi ====================
// Jawaban tersimpan otomatis setiap pilihan (persistAnswerProgress).
// Jika tes belum selesai, tampilkan dialog konfirmasi untuk memastikan user tidak salah pencet.
// Jika tes sudah selesai (review/hasil), langsung kembali ke beranda tanpa konfirmasi.
function isTestFinished() {
  const overlay = document.getElementById('reviewHasilOverlay');
  if (overlay && overlay.classList.contains('open')) return true;
  return Boolean(state.testFinished && state.testFinished[pkgKey()]);
}

function askExitToBeranda() {
  if (isTestFinished()) {
    doExitToBeranda();
    return;
  }
  const modal = document.getElementById('exitConfirmModal');
  if (modal) modal.classList.add('open');
}

function closeExitConfirm(keepHere) {
  const modal = document.getElementById('exitConfirmModal');
  if (modal) modal.classList.remove('open');
  if (keepHere === true) return;
}

function doExitToBeranda() {
  closeExitConfirm();
  try {
    const q = getCurrentQuestion();
    if (q && typeof persistAnswerProgress === 'function') {
      persistAnswerProgress(q);
    }
  } catch (e) {}
  // jawaban sudah tersimpan otomatis; buka panel Beranda (overlay)
  if (!homeIsOpen()) homeOpen();
  else homeShowPanel('beranda');
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

  // soal baru tampil: selalu mulai di tab Lembar Soal (kecuali dipaksa review)
  if (!state.keepWorkTab) switchWorkTab('soal', null, { scroll: false });
  state.keepWorkTab = false;
  const strip = document.getElementById('pembResultStrip');
  if (strip) strip.style.display = 'none';

  // animasi masuk soal (re-trigger tiap soal baru)
  const qCard = document.querySelector('.cbt-question-card');
  if (qCard) {
    qCard.classList.remove('soal-enter');
    void qCard.offsetWidth;
    qCard.classList.add('soal-enter');
  }

  const total = state.pkgData[pkgKey()].soal.length;
  const subjectMeta = SUBJECT_CATALOG[state.currentSubject] || {};
  const pkgPath = (subjectMeta.imgBase && subjectMeta.imgBase[state.currentPkg]) || `data/${state.currentSubject}/paket_${state.currentPkg}/`;

  // 1. Metadata Bar & Dynamic Progress Bar
  const badgeNomor = document.getElementById('badgeSoalNomor');
  if (badgeNomor) badgeNomor.innerText = `Latihan Soal TKA · Nomor ${q.nomor}`;
  const badgeTopik = document.getElementById('badgeTopik');
  if (badgeTopik) badgeTopik.innerText = (q.topik || `${subjectMeta.name || state.currentSubject} SMA`).toUpperCase();
  const badgeTipe = document.getElementById('badgeTipe');
  if (badgeTipe) badgeTipe.innerText = q.tipe_soal || 'Pilihan Ganda';

  // v0 Header sync
  const currQNumEl = document.getElementById('currQNum');
  if (currQNumEl) currQNumEl.innerText = q.nomor;
  const totalQNumEl = document.getElementById('totalQNum');
  if (totalQNumEl) totalQNumEl.innerText = total;
  const progressFillEl = document.getElementById('progressBarFill');
  if (progressFillEl) progressFillEl.style.width = `${Math.round(((state.currentIndex + 1) / total) * 100)}%`;
  const qNumBadge = document.getElementById('qNumBadge');
  if (qNumBadge) qNumBadge.innerText = String(q.nomor).padStart(2, '0');
  const qLabelHeader = document.getElementById('qLabelHeader');
  if (qLabelHeader) qLabelHeader.innerText = `Soal Nomor ${q.nomor} dari ${total}`;

  // Fase 2: sinkron top bar mobile & progress line
  const mQNumEl = document.getElementById('mQNum');
  if (mQNumEl) {
    const fullSubj = subjectMeta.name || state.currentSubject;
    const shortSubj = (SUBJECT_UI_META[state.currentSubject] && SUBJECT_UI_META[state.currentSubject].shortName) || fullSubj;
    mQNumEl.innerHTML =
      '<b title="' + _escHtml(fullSubj) + '">' + _escHtml(shortSubj) + '</b>' +
      '<span>Paket ' + state.currentPkg + ' · Soal ' + q.nomor + '/' + total + '</span>';
  }
  const mProgressFill = document.getElementById('mProgressFill');
  if (mProgressFill) mProgressFill.style.width = `${Math.round(((state.currentIndex + 1) / total) * 100)}%`;

  // Sync cookie and URL for persistent subject/paket context across browser and server
  try {
    document.cookie = `active_subject=${state.currentSubject}; path=/; max-age=86400`;
    document.cookie = `active_paket=${state.currentPkg}; path=/; max-age=86400`;
    const targetUrl = `?subject=${encodeURIComponent(state.currentSubject)}&paket=${state.currentPkg}`;
    if (window.location.search !== targetUrl) {
      window.history.replaceState(null, '', `${targetUrl}#soal-${q.nomor}`);
    }
  } catch (e) {}

  // Set dataset attributes for scoped question styling
  const card = document.querySelector('.cbt-question-card');
  if (card) {
    card.dataset.subject = state.currentSubject;
    card.dataset.paket = String(state.currentPkg);
    card.dataset.nomor = String(q.nomor);
  }
  const examGridEl = document.getElementById('cbtExamGrid');
  if (examGridEl) {
    examGridEl.dataset.subject = state.currentSubject;
    examGridEl.dataset.paket = String(state.currentPkg);
    examGridEl.dataset.nomor = String(q.nomor);
  }
  document.body.dataset.activeSubject = state.currentSubject;
  document.body.dataset.activePaket = String(state.currentPkg);
  document.body.dataset.activeNomor = String(q.nomor);

/**
 * Format dan bersihkan HTML resmi CBT Pusmendik agar aman, responsif,
 * dan terintegrasi rapi dengan sistem layout kartu modern kita.
 */
function formatPusmendikHtml(rawHtml, pkgPath) {
  if (!rawHtml) return '';
  let html = rawHtml;

  // 1. Bersihkan penanda XML dan komentar CBT internal Pusmendik
  html = html.replace(/<!--[\s\S]*?-->/g, '').trim();

  // 1c. Netralkan tinggi tetap & scrollbar warisan Pusmendik di mana pun posisinya
  //     (wrapper height:520px/340px + overflow:auto bikin area scroll kosong panjang)
  html = html.replace(/style="([^"]*)"/gi, (m, s) => {
    const cleaned = s
      .replace(/(?:^|;)\s*(height|overflow)\s*:[^;"]*/gi, '')
      .replace(/^;+|;+$/g, '');
    return 'style="' + cleaned + '"';
  });

  // 1b. Normalisasi simbol ilmiah: derajat Celsius, derajat sudut, plus-minus, dan eksponen
  html = html.replace(/<sup>o<\/sup>\s*C\b/gi, '°C');
  html = html.replace(/<sup>o<\/sup>/gi, '°');
  html = html.replace(/<u>\+<\/u>/gi, '±');
  html = html.replace(/\b110\s*[-–]\s*6\s*M\b/gi, '1 × 10⁻⁶ M');
  html = html.replace(/\b10\s*[-–]\s*6\s*M\b/gi, '10⁻⁶ M');

  // 2. Lepaskan pembungkus div col-lg-6 cont-soal / isi-soal bawaan Pusmendik
  // (agar tidak memaksakan height kaku 340px atau scrollbar ganda)
  const wrapperMatch = html.match(/^<div\s+class=["']col-lg-6[^"']*["'][^>]*>([\s\S]*)<\/div>$/i);
  if (wrapperMatch) {
    html = wrapperMatch[1].trim();
  }

  // 3. Normalisasi UNIVERSAL path gambar: tangkap SEMUA format src
  //    termasuk /tka/cbt_images/..., images/..., ./images/..., URL lengkap, dll.
  //    Hasilnya selalu: src="${pkgPath}images/${namafile}"
  html = html.replace(/src=["']([^"']+\.(?:png|jpe?g|gif|webp|svg))(?:\?[^"']*)?["']/gi, (match, p1) => {
    // Ekstrak nama file murni dari path apa pun
    const parts = p1.split('/');
    const fname = parts[parts.length - 1].split('?')[0];
    let base = pkgPath.endsWith('/') ? pkgPath : `${pkgPath}/`;
    return `src="${base}images/${fname}?v=41"`;
  });

  // 4. Buat parser DOM lokal agar aman, responsif, dan presisi
  try {
    const temp = document.createElement('div');
    temp.innerHTML = html;

    // 4a. Perbaiki tabel: bersihkan width kaku (Mat P1 Q13, B. Jerman P1 Q10, B. Jerman P2 Q13-15)
    temp.querySelectorAll('table').forEach(tbl => {
      tbl.removeAttribute('width');
      if (tbl.style.width) tbl.style.removeProperty('width');
      const rows = tbl.querySelectorAll('tr');

      // Deteksi tabel kartu 1 sel pembungkus artikel (B. Jerman P2 Q13, Q14, Q15)
      if (rows.length === 1 && rows[0].children.length === 1) {
        tbl.classList.add('table-layout-single-cell');
      } else if (rows.length === 1 && tbl.querySelector('img')) {
        tbl.classList.add('table-layout-card');
      }

      tbl.querySelectorAll('th, td').forEach(cell => {
        cell.removeAttribute('width');
        if (cell.style.width) cell.style.removeProperty('width');
        // Hanya beri td-has-img jika ini kolom gambar khusus di baris multi-kolom
        if (cell.parentElement.children.length > 1 && cell.querySelector('img') && !cell.textContent.trim()) {
          cell.classList.add('td-has-img');
        }
      });

      const parent = tbl.parentElement;
      if (!parent || !parent.classList.contains('table-responsive')) {
        const wrap = document.createElement('div');
        wrap.className = 'table-responsive';
        tbl.parentNode.insertBefore(wrap, tbl);
        wrap.appendChild(tbl);
      }
    });

    // 4b. Klasifikasi gambar: inline-symbol-img vs diagram-img
    temp.querySelectorAll('p').forEach(p => {
      const imgs = p.querySelectorAll('img');
      if (imgs.length === 0) return;

      const clone = p.cloneNode(true);
      clone.querySelectorAll('img').forEach(im => im.remove());
      const realText = (clone.textContent || '').replace(/\u00a0/g, ' ').trim();

      if (!realText && imgs.length === 1) {
        p.classList.add('diagram-paragraph');
        imgs[0].classList.add('diagram-img');
      } else {
        imgs.forEach(im => {
          const w = parseInt(im.getAttribute('width') || '0', 10);
          const h = parseInt(im.getAttribute('height') || '0', 10);

          // Diagram tegas jika dimensi gambar besar (rak buku, grafik pertidaksamaan, peta, organ)
          const isDefiniteDiagram = (h > 65) || (w > 220 && h > 50) || (w > 260);
          // Simbol atau formula inline jika kecil atau membawa atribut formula
          const isInlineFormula = im.hasAttribute('data-latex') || (h > 0 && h <= 55 && w <= 250) || (w > 0 && w <= 95);

          if (isDefiniteDiagram) {
            im.classList.add('diagram-img');
            p.classList.add('diagram-paragraph');
          } else if (isInlineFormula) {
            im.classList.add('inline-symbol-img');
          } else if (realText.length === 0) {
            im.classList.add('diagram-img');
          } else {
            // Cek jika gambar dipisahkan oleh BR atau berdiri sendiri di baris paragraf
            const hasBrAdjacent = (im.nextElementSibling && im.nextElementSibling.tagName === 'BR') ||
                                  (im.previousElementSibling && im.previousElementSibling.tagName === 'BR');
            if (hasBrAdjacent && !im.hasAttribute('data-latex')) {
              im.classList.add('diagram-img');
              p.classList.add('diagram-paragraph');
            } else {
              im.classList.add('inline-symbol-img');
            }
          }
        });
      }
    });

    // 4c. Deteksi bahasa & arah skrip presisi (Bahasa Arab vs Bahasa Indonesia)
    temp.querySelectorAll('p, div, li, h1, h2, h3, h4, h5, h6').forEach(el => {
      // Abaikan jika hanya kontainer pembungkus yang memiliki elemen blok anak
      const hasBlockChildren = Array.from(el.children).some(c => ['P', 'DIV', 'TABLE', 'OL', 'UL'].includes(c.tagName));
      if (hasBlockChildren) return;

      const txt = (el.textContent || '').trim();
      if (!txt) return;

      const arMatches = txt.match(/[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/g);
      const latMatches = txt.match(/[a-zA-Z]/g);
      const arCount = arMatches ? arMatches.length : 0;
      const latCount = latMatches ? latMatches.length : 0;

      if (arCount > latCount) {
        el.classList.add('text-arabic');
        el.setAttribute('dir', 'rtl');
      } else if (latCount >= 2) {
        el.classList.add('text-indonesian');
        el.setAttribute('dir', 'ltr');
        if (el.style.textAlign === 'right') {
          el.style.textAlign = 'left';
        }
      }
    });

    return temp.innerHTML;
  } catch (err) {
    console.warn('DOM parse notice in formatPusmendikHtml:', err);
    return html;
  }
}

/**
 * Cek apakah HTML stimulus memiliki konten nyata (gambar atau teks)
 * dan bukan sekadar tag kosong atau spasi (&nbsp;)
 */
function hasVisibleStimulusContent(htmlStr) {
  if (!htmlStr) return false;
  if (/<img\b/i.test(htmlStr)) return true;
  let text = htmlStr.replace(/<!--[\s\S]*?-->/g, '');
  text = text.replace(/<[^>]+>/g, '');
  text = text.replace(/&nbsp;/gi, ' ').replace(/\u00a0/g, ' ').trim();
  return text.length > 0;
}

/**
 * Sanitasi teks stimulus untuk tampilan UI (fallback bila HTML tidak ada):
 * - Hapus penanda teknis AI/LLM ([Diagram — ...], [VISUAL_INFORMATION_UNRESOLVED: ...], dll.)
 */
function cleanUiStimulusText(stimText, stimImages) {
  if (!stimText) return '';
  const lines = stimText.split('\n');
  const clean = [];

  for (let line of lines) {
    const t = line.trim();
    if (!t) continue;

    // Saring tag transkripsi AI vision / OCR
    if (/^\[(Diagram|VISUAL_INFORMATION_UNRESOLVED|Formula|Table|Graph|Others)[\s\S]*\]/i.test(t)) {
      continue;
    }

    if (stimImages && stimImages.length > 0) {
      const withoutMath = t.replace(/\$[^$]+\$/g, '').trim();
      if (withoutMath === '') continue;
      if (t.startsWith('$') && /\[(Formula|Diagram|Table)/i.test(t)) continue;
    }

    clean.push(t);
  }

  return clean.join('\n');
}

  // 2. Stimulus Context (Rendering persis 100% CBT Pusmendik resmi)
  const stimCol = document.getElementById('stimulusCol');
  const stimContainer = document.getElementById('stimulusContainer');
  stimContainer.innerHTML = '';

  let hasStimulus = false;
  const stimHtml = (q.stimulus && q.stimulus.html) ? q.stimulus.html : '';
  const stimFormatted = hasVisibleStimulusContent(stimHtml) ? formatPusmendikHtml(stimHtml, pkgPath) : '';

  if (stimFormatted && hasVisibleStimulusContent(stimFormatted)) {
    hasStimulus = true;
    const stimDiv = document.createElement('div');
    stimDiv.className = 'stimulus-body-content';
    stimDiv.innerHTML = stimFormatted;

    // Lightbox click handler & responsive size validator untuk seluruh gambar stimulus
    stimDiv.querySelectorAll('img').forEach(img => {
      img.title = 'Klik untuk memperbesar gambar stimulus';
      img.style.cursor = 'zoom-in';
      img.onclick = () => openImageLightbox(img.src, 'Gambar Stimulus');

      const checkStimImgSize = () => {
        const nw = img.naturalWidth || parseInt(img.getAttribute('width') || '0', 10);
        const nh = img.naturalHeight || parseInt(img.getAttribute('height') || '0', 10);
        const hasLatex = img.hasAttribute('data-latex');
        // Hormati atribut HTML sumber: bila sudah menandakan simbol inline (kecil),
        // jangan demosikan ke diagram hanya karena pixel asli filenya tinggi.
        const ah = parseInt(img.getAttribute('height') || '0', 10);
        const aw = parseInt(img.getAttribute('width') || '0', 10);
        const attrSaysInline = ah > 0 && ah <= 55 && aw <= 95;
        if (!hasLatex && !attrSaysInline && (nh > 65 || (nw > 180 && nh > 45))) {
          img.classList.remove('inline-symbol-img');
          img.classList.add('diagram-img');
          const p = img.closest('p');
          if (p) p.classList.add('diagram-paragraph');
        }
      };
      if (img.complete && img.naturalWidth > 0) {
        checkStimImgSize();
      } else {
        img.onload = checkStimImgSize;
      }
    });

    stimContainer.appendChild(stimDiv);
  } else if (q.stimulus && (q.stimulus.text || (q.stimulus.images && q.stimulus.images.length > 0))) {
    // Fallback bila HTML tidak tersedia
    const rawStimText = q.stimulus.text ? q.stimulus.text.trim() : '';
    const stimImages = q.stimulus.images || [];
    const cleanStimText = cleanUiStimulusText(rawStimText, stimImages);

    if (cleanStimText || stimImages.length > 0) {
      hasStimulus = true;
      const stimDiv = document.createElement('div');
      stimDiv.className = 'stimulus-body-content';

      if (cleanStimText) {
        cleanStimText.split('\n').filter(p => p.trim()).forEach(pText => {
          const p = document.createElement('p');
          p.innerHTML = pText.replace(/\*(.*?)\*/g, '<em>$1</em>');
          stimDiv.appendChild(p);
        });
      }

      if (stimImages.length > 0) {
        const imgStack = document.createElement('div');
        imgStack.className = stimImages.length > 1 ? 'stimulus-images-stack' : 'stimulus-images-single';
        stimImages.forEach(imgObj => {
          const imgWrap = document.createElement('div');
          imgWrap.className = 'stimulus-img-container';
          const img = document.createElement('img');
          img.src = `${pkgPath}${imgObj.rel_path || 'images/' + imgObj.filename}?v=41`;
          img.className = 'stimulus-img';
          img.title = 'Klik untuk memperbesar gambar stimulus';
          img.style.cursor = 'zoom-in';
          img.onclick = () => openImageLightbox(img.src, 'Gambar Stimulus');
          imgWrap.appendChild(img);
          imgStack.appendChild(imgWrap);
        });
        stimDiv.appendChild(imgStack);
      }
      stimContainer.appendChild(stimDiv);
    }
  }

  // Tampilkan/sembunyikan kontainer stimulus
  const divider = document.getElementById('cbtPanelDivider');
  const examGrid = document.getElementById('cbtExamGrid');

  if (stimCol) stimCol.style.display = hasStimulus ? 'block' : 'none';
  if (divider) divider.style.display = 'none';
  if (examGrid) {
    if (hasStimulus) {
      examGrid.classList.add('has-stimulus');
    } else {
      examGrid.classList.remove('has-stimulus');
    }
  }

  // 3. Question Prompt (Rendering persis 100% CBT Pusmendik resmi)
  const promptContainer = document.getElementById('promptContainer');
  promptContainer.innerHTML = '';
  const pertHtml = (q.pertanyaan && q.pertanyaan.html) ? q.pertanyaan.html : '';

  if (pertHtml) {
    const promptDiv = document.createElement('div');
    promptDiv.className = 'prompt-html-wrap';
    promptDiv.innerHTML = formatPusmendikHtml(pertHtml, pkgPath);

    // Lightbox click handler & responsive size validator untuk seluruh gambar pertanyaan/prompt
    promptDiv.querySelectorAll('img').forEach(img => {
      img.title = 'Klik untuk memperbesar gambar soal';
      img.style.cursor = 'zoom-in';
      img.onclick = () => openImageLightbox(img.src, 'Gambar Soal');

      const checkPromptImgSize = () => {
        const nw = img.naturalWidth || parseInt(img.getAttribute('width') || '0', 10);
        const nh = img.naturalHeight || parseInt(img.getAttribute('height') || '0', 10);
        const hasLatex = img.hasAttribute('data-latex');
        // Hormati atribut HTML sumber: bila sudah menandakan simbol inline (kecil),
        // jangan demosikan ke diagram hanya karena pixel asli filenya tinggi.
        const ah = parseInt(img.getAttribute('height') || '0', 10);
        const aw = parseInt(img.getAttribute('width') || '0', 10);
        const attrSaysInline = ah > 0 && ah <= 55 && aw <= 95;
        if (!hasLatex && !attrSaysInline && (nh > 65 || (nw > 180 && nh > 45))) {
          img.classList.remove('inline-symbol-img');
          img.classList.add('diagram-img');
          const p = img.closest('p');
          if (p) p.classList.add('diagram-paragraph');
        }
      };
      if (img.complete && img.naturalWidth > 0) {
        checkPromptImgSize();
      } else {
        img.onload = checkPromptImgSize;
      }
    });

    promptContainer.appendChild(promptDiv);
  } else {
    // Fallback bila HTML pertanyaan tidak tersedia
    const promptRaw = (q.pertanyaan && q.pertanyaan.text) ? q.pertanyaan.text.trim() : '';
    if (promptRaw) {
      const promptLines = promptRaw.split('\n').filter(l => l.trim());
      promptLines.forEach(line => {
        const p = document.createElement('p');
        p.className = 'prompt-paragraph';
        p.innerHTML = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
        promptContainer.appendChild(p);
      });
    }

    if (q.pertanyaan && q.pertanyaan.images && q.pertanyaan.images.length > 0) {
      q.pertanyaan.images.forEach(pImg => {
        const imgWrap = document.createElement('div');
        imgWrap.className = 'stimulus-img-container prompt-img-wrap';
        const img = document.createElement('img');
        img.src = `${pkgPath}${pImg.rel_path || 'images/' + pImg.filename}`;
        img.className = 'stimulus-img';
        img.title = 'Klik untuk memperbesar gambar soal';
        img.style.cursor = 'zoom-in';
        img.onclick = () => openImageLightbox(img.src, 'Gambar Soal');
        imgWrap.appendChild(img);
        promptContainer.appendChild(imgWrap);
      });
    }
  }

  // 4. Options List (PG) atau Tabel Pernyataan Benar/Salah
  const optionsContainer = document.getElementById('optionsContainer');
  optionsContainer.innerHTML = '';

  const currentSelection = (state.userAnswers[pkgKey()] || {})[q.nomor];
  const isComplex = (q.tipe_soal === 'Pilihan Ganda Kompleks' || q.tipe === 'Pilihan Ganda Kompleks' || (Array.isArray(q.kunci_jawaban) && !statementType(q)));
  const stmtType = statementType(q);

  if (stmtType) {
    renderBsStatements(q, currentSelection || {}, optionsContainer);
  } else {
    const opts = q.pilihan_jawaban || [];
    if (opts.length === 0 && q.pernyataan && q.pernyataan.length > 0) {
      renderBsStatements(q, currentSelection || {}, optionsContainer);
    } else {
      opts.forEach(opt => {
      const isSelected = isComplex
        ? (Array.isArray(currentSelection) && currentSelection.includes(opt.key))
        : (currentSelection === opt.key);

      const optItem = document.createElement('div');
      optItem.className = `option-item ${isSelected ? 'selected' : ''}`;
      optItem.dataset.key = opt.key;
      optItem.dataset.optKey = opt.key;
      // Aksesibilitas (audit Kimi/Qwen): opsi sebagai kontrol semantik radio/checkbox
      optItem.setAttribute('role', isComplex ? 'checkbox' : 'radio');
      optItem.setAttribute('aria-checked', String(!!isSelected));
      optItem.setAttribute('tabindex', '0');
      optItem.setAttribute('aria-label', `Opsi ${opt.key}`);
      optItem.onclick = () => selectOption(opt.key, isComplex);
      optItem.onkeydown = (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          selectOption(opt.key, isComplex);
        }
      };

      // Key indicator
      const indicator = document.createElement('div');
      indicator.className = 'opt-indicator';
      indicator.innerText = opt.key;
      if (isComplex) {
        indicator.style.borderRadius = '6px';
      }
      optItem.appendChild(indicator);

      // Option body
      const body = document.createElement('div');
      body.className = 'opt-body';

      if (opt.html) {
        // 1. Prioritaskan HTML resmi CBT Pusmendik dengan superskrip, subskrip, dan simbol utuh
        let rawOptHtml = (opt.html || '').trim();
        // Bersihkan prefiks huruf pilihan duplikat "A. " / "<p>A. "
        // Lookahead: label hanya dibuang bila diikuti digit/huruf kapital/(
        // atau $ (math) — agar teks seperti "E. coli" tidak ikut terpotong.
        rawOptHtml = rawOptHtml.replace(/^(<p[^>]*>)?\s*[A-E][.\)]\s+(?=[0-9A-Z($])/i, '$1');
        body.innerHTML = formatPusmendikHtml(rawOptHtml, pkgPath);

        // Pasang event lightbox dan klasifikasi ukuran gambar pilihan
        body.querySelectorAll('img').forEach(img => {
          const checkSize = () => {
            const nw = img.naturalWidth || parseInt(img.getAttribute('width') || '0', 10);
            const nh = img.naturalHeight || parseInt(img.getAttribute('height') || '0', 10);
            // Hanya anggap diagram jika benar-benar tinggi / bukan strip formula horizontal
            const isFormula = img.hasAttribute('data-latex') || (nh > 0 && nh <= 65);
            if (!isFormula && (nh > 75 || (nw > 280 && nh > 60))) {
              img.classList.remove('opt-math-img');
              img.classList.add('opt-diagram-img');
            } else {
              img.classList.remove('opt-diagram-img');
              img.classList.add('opt-math-img');
            }
          };

          if (img.complete && img.naturalWidth > 0) {
            checkSize();
          } else {
            img.onload = checkSize;
          }

          img.title = 'Klik untuk memilih opsi';
          img.onclick = (e) => {
            // Audit Kimi: tap gambar dulu = zoom -> seleksi tak sengaja.
            // Sekarang: tap gambar = MEMILIH; zoom lewat tombol kaca terpisah.
            e.stopPropagation();
            selectOption(opt.key, isComplex);
          };
          const zoomBtn = document.createElement('button');
          zoomBtn.type = 'button';
          zoomBtn.className = 'opt-zoom-btn';
          zoomBtn.setAttribute('aria-label', `Perbesar gambar opsi ${opt.key}`);
          zoomBtn.title = 'Perbesar gambar';
          zoomBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass-plus"></i>';
          zoomBtn.onclick = (e) => {
            e.stopPropagation();
            openImageLightbox(img.src, `Pilihan Jawaban ${opt.key}`);
          };
          img.insertAdjacentElement('afterend', zoomBtn);
        });
      } else if (opt.image) {
        // 2. Tampilkan gambar opsi jika tersedia (grafik atau formula matematika)
        const mathImg = document.createElement('img');
        let base = pkgPath.endsWith('/') ? pkgPath : `${pkgPath}/`;
        let rel = (opt.image.rel_path || `images/${opt.image.filename}`).replace(/^\.?\//, '');
        if (base.endsWith('images/') && rel.startsWith('images/')) {
          rel = rel.substring(7);
        }
        mathImg.src = `${base}${rel}?v=41`;
        mathImg.alt = `Pilihan ${opt.key}`;
        mathImg.title = 'Klik untuk memilih opsi';
        mathImg.onclick = (e) => {
          e.stopPropagation();
          selectOption(opt.key, isComplex);
        };
        const zoomBtn2 = document.createElement('button');
        zoomBtn2.type = 'button';
        zoomBtn2.className = 'opt-zoom-btn';
        zoomBtn2.setAttribute('aria-label', `Perbesar gambar opsi ${opt.key}`);
        zoomBtn2.title = 'Perbesar gambar';
        zoomBtn2.innerHTML = '<i class="fa-solid fa-magnifying-glass-plus"></i>';
        zoomBtn2.onclick = (e) => {
          e.stopPropagation();
          openImageLightbox(mathImg.src, `Pilihan Jawaban ${opt.key}`);
        };
        mathImg.insertAdjacentElement('afterend', zoomBtn2);

        // Klasifikasi visual diagram vs rumus inline
        mathImg.onload = () => {
          if (mathImg.naturalHeight > 75 || (mathImg.naturalWidth > 280 && mathImg.naturalHeight > 60)) {
            mathImg.classList.add('opt-diagram-img');
          } else {
            mathImg.classList.add('opt-math-img');
          }
        };

        let rawText = (opt.text || '').trim();
        let textWithoutMath = rawText.replace(/\$[^$]+\$/g, '').trim();
        let isPureFormulaText = (opt.latex && (rawText === `$${opt.latex}$` || rawText === opt.latex)) ||
                                (rawText.startsWith('$') && rawText.endsWith('$') && !textWithoutMath);

        const hasRealAccompanyingText = Boolean(rawText && !isPureFormulaText);
        const txtSpan = hasRealAccompanyingText ? document.createElement('span') : null;
        if (txtSpan) {
          txtSpan.innerText = rawText;
        }

        const isImgFirst = opt.image_first || opt.image_position === 'before' || (hasRealAccompanyingText && /^(dan|atau|dengan|,)\s+/i.test(rawText));

        if (isImgFirst) {
          body.appendChild(mathImg);
          if (txtSpan) {
            txtSpan.style.marginLeft = '8px';
            body.appendChild(txtSpan);
          }
        } else {
          if (txtSpan) {
            txtSpan.style.marginRight = '8px';
            body.appendChild(txtSpan);
          }
          body.appendChild(mathImg);
        }
      } else {
        // 3. Fallback teks bersih dengan simbol yang telah diperbaiki
        let strippedDisplay = (opt.full_display || '').replace(/^[A-E][.\)]\s+(?=[0-9A-Z($])/i, '').trim();
        let fullContent = '';
        if (strippedDisplay) {
          fullContent = strippedDisplay;
        } else if (opt.latex) {
          fullContent = `$${opt.latex}$`;
        } else {
          fullContent = opt.text || '';
        }
        body.innerHTML = fullContent;
      }

      // Deteksi bahasa teks opsi (Arab vs Indonesia)
      const optRawText = (body.textContent || '').trim();
      const arMatches = optRawText.match(/[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/g);
      const latMatches = optRawText.match(/[a-zA-Z]/g);
      const arCount = arMatches ? arMatches.length : 0;
      const latCount = latMatches ? latMatches.length : 0;
      if (arCount > latCount) {
        optItem.classList.add('opt-arabic');
        body.classList.add('opt-arabic');
      } else {
        optItem.classList.add('opt-indonesian');
        body.classList.add('opt-indonesian');
      }

      optItem.appendChild(body);
      optionsContainer.appendChild(optItem);
      });
    }
  }

  // Reset feedback banner
  const feedback = document.getElementById('feedbackBanner');
  feedback.style.display = 'none';

  // 5. Navigation Buttons State
  const totalQuestions = (state.pkgData[pkgKey()] && state.pkgData[pkgKey()].soal) ? state.pkgData[pkgKey()].soal.length : 1;
  const isLastQuestion = state.currentIndex >= totalQuestions - 1;
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');

  btnPrev.disabled = state.currentIndex === 0;
  btnNext.disabled = false;

  if (isLastQuestion) {
    btnNext.innerHTML = '<i class="fa-solid fa-flag-checkered"></i> <span>Selesai Tes</span>';
    btnNext.classList.add('btn-nav-finish');
  } else {
    btnNext.innerHTML = '<span>Selanjutnya</span> <i class="fa-solid fa-arrow-right"></i>';
    btnNext.classList.remove('btn-nav-finish');
  }

  document.getElementById('chkRagu').checked = !!((state.raguStatus[pkgKey()] || {})[q.nomor]);

  // 6. Learning Section (Explanation, AI Tutor & Similar Question)
  renderExplanation(q);
  renderAiTutor(q);
  renderSimilarQuestion(q);

  // Toggle explanation visibility
  // Audit Kimi T-08: kunci resmi tidak boleh tampil otomatis di soal yang BELUM
  // dijawab — pembahasan tutup saat berpindah ke soal yang belum dijawab, sehingga
  // kunci seluruh paket tidak bisa "dipanen" hanya dengan membuka pembahasan sekali.
  if (!isQuestionAnswered(q)) state.explanationVisible = false;
  const learnSec = document.getElementById('learningSection');
  learnSec.style.display = state.explanationVisible ? 'flex' : 'none';
  document.getElementById('txtToggleExp').innerText = state.explanationVisible
    ? 'Tutup Tata Cara & Pembahasan'
    : 'Buka Tata Cara & Pembahasan';

  // Floating AI button di desktop dihilangkan (hanya aktif di mobile via CSS)

  // Sinkronkan status ciut/tampil Tata Cara
  setExplanationCollapsed(state.explanationCollapsed);

  // Trigger KaTeX render
  renderMath();
  prepareQuestionImages();
  updateGridModalActive();
}

// Fase 2: lazy-load + async decode semua gambar soal untuk mengurangi layout shift.
// Aspect-ratio per gambar tidak bisa dipasang karena dimensi asli tidak ada di data.
function prepareQuestionImages() {
  try {
    document.querySelectorAll(
      '.cbt-question-card img, .practice-card img, #stimulusContainer img, #promptContainer img'
    ).forEach(img => {
      if (!img.hasAttribute('loading')) img.setAttribute('loading', 'lazy');
      img.setAttribute('decoding', 'async');
    });
  } catch (e) {}
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

  // Update UI selection classes + aria (audit aksesibilitas)
  const selected = state.userAnswers[pkgKey()][q.nomor];
  document.querySelectorAll('.option-item').forEach(el => {
    const k = el.dataset.key;
    const isSel = isComplex ? (selected && selected.includes(k)) : (selected === k);
    el.classList.toggle('selected', !!isSel);
    el.setAttribute('aria-checked', String(!!isSel));
  });

  // Update modal grid
  renderGridModal();

  // Persist progres nyata ke localStorage (kontrak KONTRAK_DATA.md):
  // tka_progress[subjectKey][pkgNumber][nomorSoal] = { kunci, benar }
  persistAnswerProgress(q);
}

// Tulis jawaban yang barusan dipilih ke tka_progress. Dipanggil dari selectOption.
function persistAnswerProgress(q) {
  try {
    const subject = state.currentSubject;
    const pkg = Number(state.currentPkg) || 1;
    const ans = (state.userAnswers[subject + ':' + pkg] || {})[q.nomor];
    if (ans === undefined || ans === null || ans === '') return;

    const stmt = statementType(q);
    let benar = false;
    if (stmt) {
      // Soal pernyataan: simpan setelah semua pernyataan dijawab; benar = semua cocok kunci
      if (typeof ans !== 'object' || Array.isArray(ans)) return;
      const stmts = q.pernyataan || [];
      if (!stmts.every(st => ans[st.key])) return;
      const kunci = parseBsKunci(q);
      benar = stmts.every(st => ans[st.key] === kunci[st.key]);
    } else if (Array.isArray(q.kunci_jawaban)) {
      // Pilihan Ganda Kompleks: himpunan jawaban == himpunan kunci
      if (!Array.isArray(ans) || ans.length === 0) return;
      const k = q.kunci_jawaban.map(String);
      benar = ans.length === k.length && ans.every(x => k.includes(String(x)));
    } else {
      benar = String(ans) === String(q.kunci_jawaban);
    }

    const store = JSON.parse(localStorage.getItem('tka_progress') || '{}');
    store[subject] = store[subject] || {};
    store[subject][pkg] = store[subject][pkg] || {};
    store[subject][pkg][q.nomor] = { kunci: q.kunci_jawaban, benar };
    localStorage.setItem('tka_progress', JSON.stringify(store));
  } catch (e) { /* localStorage gagal: jangan ganggu UI */ }
}

// ==================== SOAL PERNYATAAN (Benar/Salah & Pernyataan-Label) ====================

// Tipe soal berbasis pernyataan: 'Benar-Salah', 'Pernyataan-Label', atau null
function statementType(q) {
  if (!q) return null;
  const t = q.tipe_soal || q.tipe;
  if (t === 'Benar-Salah') return 'Benar-Salah';
  if (t === 'Pernyataan-Label') return 'Pernyataan-Label';
  if (t === 'Matriks' || (q.pernyataan && q.pernyataan.length > 0)) {
    return 'Benar-Salah';
  }
  return null;
}

// Nilai kolom pilihan untuk soal pernyataan.
function statementValues(q) {
  if (Array.isArray(q.table_headers) && q.table_headers.length >= 2) {
    return q.table_headers;
  }
  const vals = [];
  if (Array.isArray(q.kunci_jawaban)) {
    q.kunci_jawaban.forEach(entry => {
      const v = String(entry).split(':')[1];
      if (v && !vals.includes(v)) vals.push(v);
    });
  }
  if (vals.length >= 2) return vals;
  return ['Benar', 'Salah'];
}

// Render tabel pernyataan (meniru UI resmi Pusmendik)
function renderBsStatements(q, selection, container) {
  const subjectMeta = SUBJECT_CATALOG[state.currentSubject] || {};
  const pkgPath = (subjectMeta.imgBase && subjectMeta.imgBase[state.currentPkg]) || `data/${state.currentSubject}/paket_${state.currentPkg}/`;
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

    // Isi pernyataan (teks + gambar asli resmi + latex)
    const body = document.createElement('div');
    body.className = 'bs-cell bs-cell-stmt';
    const stmtText = (stmt.text || '').trim();

    if (stmt.image) {
      const img = document.createElement('img');
      img.src = `${pkgPath}${stmt.image.rel_path}`;
      img.alt = `Pernyataan ${stmt.key}`;
      img.className = 'bs-stmt-img';
      img.title = 'Klik untuk memperbesar gambar';
      img.style.cursor = 'zoom-in';
      img.onclick = (e) => {
        e.stopPropagation();
        openImageLightbox(img.src, `Pernyataan ${stmt.key}`);
      };

      if (!stmtText) {
        body.appendChild(img);
      } else if (/^(merupakan|adalah|sama dengan|lebih|kurang|termasuk)/i.test(stmtText)) {
        // Contoh Soal 3: [gambar a] merupakan kelipatan dari 3.
        body.appendChild(img);
        const span = document.createElement('span');
        span.innerHTML = ` ${stmtText}`;
        body.appendChild(span);
      } else {
        const span = document.createElement('span');
        span.innerHTML = `${stmtText} `;
        body.appendChild(span);
        body.appendChild(img);
      }
    } else if (stmt.latex) {
      let contentHtml = '';
      if (!stmtText) {
        contentHtml = `<span class="bs-latex">$${stmt.latex}$</span>`;
      } else if (/^(merupakan|adalah|sama dengan|lebih|kurang|termasuk)/i.test(stmtText)) {
        contentHtml = `<span class="bs-latex">$${stmt.latex}$</span> ${stmtText}`;
      } else {
        contentHtml = `${stmtText} <span class="bs-latex">$${stmt.latex}$</span>`;
      }
      body.innerHTML = contentHtml;
    } else {
      body.innerHTML = stmtText;
    }

    // Deteksi bahasa teks pernyataan (Arab vs Indonesia)
    const stmtRaw = (body.textContent || '').trim();
    const arMatches = stmtRaw.match(/[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/g);
    const latMatches = stmtRaw.match(/[a-zA-Z]/g);
    if ((arMatches ? arMatches.length : 0) > (latMatches ? latMatches.length : 0)) {
      body.classList.add('stmt-arabic');
    } else {
      body.classList.add('stmt-indonesian');
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

  // Persist progres nyata (kontrak tka_progress) — simpan saat semua pernyataan terjawab
  persistAnswerProgress(q);
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
  if (item.tipe_soal === 'Pilihan Ganda Kompleks' || item.tipe === 'Pilihan Ganda Kompleks') {
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
  const isComplex = (q.tipe_soal === 'Pilihan Ganda Kompleks' || q.tipe === 'Pilihan Ganda Kompleks' || (Array.isArray(q.kunci_jawaban) && !statementType(q)));
  const stmtType = statementType(q);

  // ---- Soal pernyataan (Benar/Salah & Label): validasi & evaluasi per pernyataan ----
  if (stmtType) {
    const sel = (currentSelection && typeof currentSelection === 'object' && !Array.isArray(currentSelection))
      ? currentSelection : {};
    const stmts = q.pernyataan || [];
    const unanswered = stmts.filter(st => !sel[st.key]);

    if (unanswered.length > 0) {
      const valName = statementValues(q).join('/');
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
    showPembahasanAfterCheck();
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

  const targetArr = Array.isArray(correctKey) ? correctKey : (correctKey ? [correctKey] : []);
  if (isComplex) {
    const sortedUser = [...currentSelection].sort().join(',');
    const sortedTarget = [...targetArr].sort().join(',');
    isCorrect = sortedUser === sortedTarget;
  } else {
    isCorrect = currentSelection === correctKey;
  }

  // Highlight options
  document.querySelectorAll('.option-item').forEach(el => {
    const k = el.dataset.key;
    const isTarget = isComplex ? targetArr.includes(k) : (k === correctKey);
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
  showPembahasanAfterCheck();
}

// ==================== WORK TABS: Lembar Soal vs Pembahasan & AI (Arah 2) ====================
// Konteks dipisah supaya user tidak scroll maraton: soal di tab sendiri,
// pembahasan pilar + AI Tutor jadi full-pane dengan sub-switch + rail kanan.
function switchWorkTab(tab, sub, opts) {
  const o = opts || {};
  const paneSoal = document.getElementById('workPaneSoal');
  const panePemb = document.getElementById('workPanePembahasan');
  if (!paneSoal || !panePemb) return;
  if (tab !== 'soal' && tab !== 'pembahasan') return;

  paneSoal.classList.toggle('active', tab === 'soal');
  panePemb.classList.toggle('active', tab === 'pembahasan');
  paneSoal.style.display = tab === 'soal' ? 'block' : 'none';
  panePemb.style.display = tab === 'pembahasan' ? 'block' : 'none';

  const tSoal = document.getElementById('wtab-soal');
  const tPemb = document.getElementById('wtab-pemb');
  if (tSoal && tPemb) {
    tSoal.classList.toggle('active', tab === 'soal');
    tPemb.classList.toggle('active', tab === 'pembahasan');
    tSoal.setAttribute('aria-selected', String(tab === 'soal'));
    tPemb.setAttribute('aria-selected', String(tab === 'pembahasan'));
  }

  if (tab === 'pembahasan') {
    // pembahasan selalu tampil penuh di tab ini
    if (!state.explanationVisible) {
      state.explanationVisible = true;
      const ls = document.getElementById('learningSection');
      if (ls) ls.style.display = 'flex';
      const t = document.getElementById('txtToggleExp');
      if (t) t.innerText = 'Tutup Tata Cara & Pembahasan';
      const arr = document.getElementById('accordionArrow');
      if (arr) arr.classList.add('rotated');
      setExplanationCollapsed(false);
    }
    switchPembSub(sub || state.pembSub || 'materi', o);
  }
  syncRail(tab === 'soal' ? 'soal' : (sub || state.pembSub || 'materi'));
  if (o.scroll !== false) window.scrollTo({ top: 0, behavior: 'smooth' });
}

function switchPembSub(sub, opts) {
  const o = opts || {};
  if (sub !== 'materi' && sub !== 'ai') sub = 'materi';
  state.pembSub = sub;
  const mSub = document.getElementById('pembSubMateri');
  const aSub = document.getElementById('pembSubAI');
  if (mSub) mSub.style.display = sub === 'materi' ? 'block' : 'none';
  if (aSub) aSub.style.display = sub === 'ai' ? 'block' : 'none';
  const bM = document.getElementById('psub-materi');
  const bA = document.getElementById('psub-ai');
  if (bM && bA) {
    bM.classList.toggle('active', sub === 'materi');
    bA.classList.toggle('active', sub === 'ai');
  }
  syncRail(sub);
  if (sub === 'ai' && isTutorSheetMode()) {
    // mobile: AI Tutor = bottom sheet — buka sheet yang tinggal di sub-pane ini
    const sheet = document.getElementById('cbtSidebarCol');
    const backdrop = document.getElementById('tutorBackdrop');
    if (sheet) { sheet.style.transform = ''; sheet.classList.add('tutor-open'); }
    if (backdrop) backdrop.classList.add('open');
    return;
  }
  if (sub === 'ai') {
    const inp = document.getElementById('chatInput');
    if (inp) { try { inp.focus({ preventScroll: true }); } catch (e) {} }
  }
}

function syncRail(active) {
  document.querySelectorAll('#workRail .rail-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-rail') === active);
  });
}

// Setelah cek jawaban: salin hasil ke tab Pembahasan lalu pindah otomatis
// (hanya jika user masih di soal yang sama dan soalnya sudah dijawab).
function showPembahasanAfterCheck() {
  const fb = document.getElementById('feedbackBanner');
  const strip = document.getElementById('pembResultStrip');
  if (fb && strip) {
    strip.className = fb.className.replace('feedback-banner', 'feedback-banner pemb-strip');
    strip.innerHTML = fb.innerHTML;
    strip.style.display = fb.style.display;
  }
  const q = getCurrentQuestion();
  const nomor = q ? q.nomor : null;
  setTimeout(() => {
    const cur = getCurrentQuestion();
    if (cur && cur.nomor === nomor && isQuestionAnswered(cur)) {
      switchWorkTab('pembahasan', 'materi', { scroll: false });
    }
  }, 1100);
}

// Toggle display of Explanation section
function toggleExplanation() {
  state.explanationVisible = !state.explanationVisible;
  const learnSec = document.getElementById('learningSection');
  learnSec.style.display = state.explanationVisible ? 'flex' : 'none';
  const txtToggle = document.getElementById('txtToggleExp');
  if (txtToggle) {
    txtToggle.innerText = state.explanationVisible
      ? 'Tutup Tata Cara & Pembahasan'
      : 'Tata Cara & Langkah Penyelesaian';
  }
  const arr = document.getElementById('accordionArrow');
  if (arr) {
    arr.classList.toggle('rotated', state.explanationVisible);
  }

  // Floating AI button di desktop dihilangkan (hanya aktif di mobile via CSS)

  if (state.explanationVisible) {
    // Saat dibuka via tombol Buka Tata Cara, tampilkan langkah penuh
    setExplanationCollapsed(false);
    learnSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// Set status ciut/tampil Tata Cara & Langkah Penyelesaian Soal
function setExplanationCollapsed(collapsed) {
  state.explanationCollapsed = !!collapsed;
  const expCard = document.getElementById('explanationCard');
  const expBody = document.getElementById('expBody');
  const notice = document.getElementById('expCollapsedNotice');
  const txtBtn = document.getElementById('txtExpCollapse');
  const iconBtn = document.getElementById('iconExpCollapse');
  const txtAiBtn = document.getElementById('txtToggleStepsFromAi');
  const iconAiBtn = document.getElementById('iconToggleStepsFromAi');

  if (state.explanationCollapsed) {
    if (expCard) expCard.classList.add('is-collapsed');
    if (expBody) expBody.style.display = 'none';
    if (notice) notice.style.display = 'flex';
    if (txtBtn) txtBtn.innerText = 'Tampilkan Tata Cara';
    if (iconBtn) iconBtn.className = 'fa-solid fa-eye';
    if (txtAiBtn) txtAiBtn.innerText = 'Tampilkan Tata Cara';
    if (iconAiBtn) iconAiBtn.className = 'fa-solid fa-eye';
  } else {
    if (expCard) expCard.classList.remove('is-collapsed');
    if (expBody) expBody.style.display = 'block';
    if (notice) notice.style.display = 'none';
    if (txtBtn) txtBtn.innerText = 'Sembunyikan Tata Cara';
    if (iconBtn) iconBtn.className = 'fa-solid fa-eye-slash';
    if (txtAiBtn) txtAiBtn.innerText = 'Sembunyikan Tata Cara';
    if (iconAiBtn) iconAiBtn.className = 'fa-solid fa-eye-slash';
  }
}

// Toggle ciut/tampil Tata Cara & Langkah
function toggleExplanationCollapse() {
  setExplanationCollapsed(!state.explanationCollapsed);
}

// Buka AI Tutor langsung di bawah soal (dengan tata cara diciutkan agar soal terlihat)
function openAiTutorDirect() {
  const learnSec = document.getElementById('learningSection');
  if (!state.explanationVisible) {
    state.explanationVisible = true;
    learnSec.style.display = 'flex';
    document.getElementById('txtToggleExp').innerText = 'Tutup Tata Cara & Pembahasan';
    const btnFloating = document.getElementById('btnFloatingAi');
    if (btnFloating) btnFloating.style.display = 'flex';
  }

  // Sembunyikan langkah penyelesaian agar user bisa melihat soal & chat AI berdampingan tanpa scrolling jauh!
  setExplanationCollapsed(true);

  const card = document.getElementById('aiTutorCard');
  if (card) {
    card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    const input = document.getElementById('chatInput');
    if (input) setTimeout(() => input.focus(), 350);
  }
}

// Smooth scroll to AI Tutor card
function scrollToAiTutor() {
  if (!state.explanationVisible) {
    state.explanationVisible = true;
    const learnSec = document.getElementById('learningSection');
    if (learnSec) learnSec.style.display = 'flex';
    const txtExp = document.getElementById('txtToggleExp');
    if (txtExp) txtExp.innerText = 'Tutup Tata Cara & Pembahasan';
  }
  // Sembunyikan rincian langkah agar posisi soal tetap dekat di atas saat chat AI
  setExplanationCollapsed(true);

  const card = document.getElementById('aiTutorCard');
  if (card) {
    card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    const input = document.getElementById('chatInput');
    if (input) setTimeout(() => input.focus(), 350);
  }
}

// Render the Step-by-Step Explanation, Symbols Glossary, and Why-Concept
// Sumber data panel = solusi spesifik soal (Layer 3, hasil Claude) via /api/solution.
// q.pembahasan (enrichment generik lama) TIDAK dipakai lagi di panel ini: konten
// generik tidak boleh menyamar sebagai pembahasan spesifik soal.
function renderExplanation(q) {
  // Audit Grok: jangan tampilkan pesan pesimis "belum tersedia" selagi fetch
  // berjalan — tampilkan state loading yang jujur, pesan "belum tersedia" hanya
  // muncul bila fetch SELESAI dan memang tidak ada solusi.
  _renderSolutionLoading();
  _applyCanonicalSolution(q);
}

// State loading: ditampilkan selama request /api/solution berjalan.
function _renderSolutionLoading() {
  const banner = document.getElementById('solutionSummaryBanner');
  if (banner) {
    banner.style.display = 'none';
    banner.innerHTML = '';
  }

  const conceptContainer = document.getElementById('conceptContainer');
  if (conceptContainer) {
    conceptContainer.innerHTML =
      '<div class="concept-card-item loading-state"><i class="fa-solid fa-circle-notch fa-spin"></i> <span>Memuat pembahasan…</span></div>';
  }

  const symBox = document.getElementById('symbolsBox');
  if (symBox) {
    symBox.style.display = 'none';
    const symContainer = document.getElementById('symbolsContainer');
    if (symContainer) symContainer.innerHTML = '';
  }

  const whyBox = document.getElementById('whyConceptBox');
  if (whyBox) {
    whyBox.style.display = 'none';
    const whyContainer = document.getElementById('whyConceptContainer');
    if (whyContainer) whyContainer.innerHTML = '';
  }

  const stepsContainer = document.getElementById('stepsContainer');
  if (stepsContainer) {
    stepsContainer.innerHTML =
      '<div class="step-timeline-card"><div class="step-timeline-indicator"><div class="step-num-badge empty"><i class="fa-solid fa-circle-notch fa-spin"></i></div></div>' +
      '<div class="step-timeline-body"><div class="step-main-text" style="color: var(--text-2);">Memuat langkah penyelesaian…</div></div></div>';
  }

  const tipsContainer = document.getElementById('tipsContainer');
  if (tipsContainer) {
    tipsContainer.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Memuat tips & jebakan…';
  }

  const visBox = document.getElementById('canonicalVisualBox');
  if (visBox) {
    visBox.style.display = 'none';
    const visList = document.getElementById('canonicalVisualList');
    if (visList) visList.innerHTML = '';
  }
}

// State jujur: semua kartu menandai pembahasan spesifik belum tersedia.
function _renderSolutionUnavailable(note) {
  const banner = document.getElementById('solutionSummaryBanner');
  if (banner) {
    banner.style.display = 'none';
    banner.innerHTML = '';
  }

  const conceptContainer = document.getElementById('conceptContainer');
  if (conceptContainer) {
    conceptContainer.innerHTML =
      '<div class="concept-card-item empty-state"><i class="fa-solid fa-hourglass-half"></i> <span><strong>Pembahasan untuk soal ini belum tersedia.</strong> Kamu tetap bisa bertanya lewat AI Tutor di samping.</span></div>';
  }

  const symBox = document.getElementById('symbolsBox');
  if (symBox) {
    symBox.style.display = 'none';
    const symContainer = document.getElementById('symbolsContainer');
    if (symContainer) symContainer.innerHTML = '';
  }

  const whyBox = document.getElementById('whyConceptBox');
  if (whyBox) {
    whyBox.style.display = 'none';
    const whyContainer = document.getElementById('whyConceptContainer');
    if (whyContainer) whyContainer.innerHTML = '';
  }

  const stepsContainer = document.getElementById('stepsContainer');
  if (stepsContainer) {
    stepsContainer.innerHTML = '';
    const noteDiv = document.createElement('div');
    noteDiv.className = 'step-timeline-card empty-card';
    noteDiv.innerHTML =
      '<div class="step-timeline-indicator"><div class="step-num-badge empty"><i class="fa-solid fa-hourglass-half"></i></div></div>' +
      '<div class="step-timeline-body"><div class="step-card-inner"><div class="step-card-header"><span class="step-tag">STATUS</span><h4 class="step-title">Langkah Penyelesaian Belum Tersedia</h4></div>' +
      '<div class="step-card-content"><div class="step-main-text">' + _escHtml(note || 'Pembahasan langkah demi langkah untuk soal ini belum tersedia. Kamu tetap bisa bertanya lewat AI Tutor.') + '</div></div></div></div>';
    stepsContainer.appendChild(noteDiv);
  }

  const tipsContainer = document.getElementById('tipsContainer');
  if (tipsContainer) {
    tipsContainer.innerHTML =
      '<i class="fa-solid fa-hourglass-half"></i> Tips & jebakan spesifik soal ini menyusul dari solusi Claude.';
  }

  const visBox = document.getElementById('canonicalVisualBox');
  if (visBox) {
    visBox.style.display = 'none';
    const visList = document.getElementById('canonicalVisualList');
    if (visList) visList.innerHTML = '';
  }
}

function _escHtml(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function _fmtText(s) {
  let text = _escHtml(s);
  // Bersihkan sisa header markdown (### Judul)
  text = text.replace(/(?:^|\n)#{2,6}\s+\*\*([^*]+)\*\*/g, '\n<strong>$1:</strong>\n');
  text = text.replace(/(?:^|\n)#{2,6}\s+([^\n]+)/g, '\n<strong>$1:</strong>\n');
  // Format bold markdown (**teks**)
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Newline menjadi <br>
  text = text.replace(/\n/g, '<br>');
  // Rapikan <br> yang beruntun berlebih (>2)
  text = text.replace(/(?:<br>\s*){3,}/g, '<br><br>');
  return text;
}

// Teks yang berisi daftar ber-pemisah " • " dirender sebagai list blok
// (satu <li> per poin) — bukan menyatu horisontal. Aman untuk teks tanpa bullet.
function _bulletListHtml(s) {
  let raw = String(s || '').trim();
  // Normalisasi: dash yang dipakai sebagai pemisah item list (pola ":- " atau "$- "
  // diikuti huruf kapital) diubah jadi bullet • agar terpecah rapi.
  // Contoh data: "matematika:- Kelas 58 - 60: $f=2$- Kelas 61..." -> tiap "- Kelas" jadi item sendiri.
  // Aman: "58 - 60" tidak tersentuh karena dash-nya tidak didahului ":" atau "$".
  raw = raw.replace(/([:$])- (?=[A-ZÀ-Þ\u0600-\u06FF0-9])/g, '$1• ');
  if (!raw.includes('•')) return _fmtText(raw);
  const items = raw.split(/\s*•\s*/).map(x => x.trim()).filter(Boolean);
  if (items.length < 2) return _fmtText(raw);
  return '<ul class="text-bullet-list">' + items.map(it => '<li>' + _fmtText(it) + '</li>').join('') + '</ul>';
}

// Helper to render an elevated, structured pedagogical step card
function _renderStepTimelineCard(stepText, index, totalSteps) {
  let stepNum = index + 1;
  let rawText = String(stepText || '').trim();

  // 1. Extract Step Number
  const numMatch = rawText.match(/^(\d+)[\.\:\)]\s*(.*)$/s);
  if (numMatch) {
    stepNum = numMatch[1];
    rawText = numMatch[2];
  } else {
    const stepMatch = rawText.match(/^(?:Langkah|Step)\s*(\d+)[\:\.\-]?\s*(.*)$/is);
    if (stepMatch) {
      stepNum = stepMatch[1];
      rawText = stepMatch[2];
    }
  }

  // 2. Extract Title (separated by " — " or " : " or " - ")
  let title = '';
  let body = rawText;
  const splitDash = rawText.match(/^([^\n—\-:]{3,65})\s*(?:—|:\s|\s-\s)(.*)$/s);
  if (splitDash && !splitDash[1].includes('$') && !splitDash[1].includes('\\')) {
    title = splitDash[1].trim();
    body = splitDash[2].trim();
  }

  // 3. Detect and extract parenthetical note if at the end, e.g. "(bilangan asli dimulai dari 1, bukan 0)"
  let mainBody = body;
  let noteText = '';
  const noteMatch = body.match(/^(.*?)\s*\(([^)]+)\)\.?\s*$/s);
  if (noteMatch && !noteMatch[2].includes('\\') && !noteMatch[2].includes('{') && noteMatch[2].length > 10) {
    mainBody = noteMatch[1].trim();
    noteText = noteMatch[2].trim();
  }

  const card = document.createElement('div');
  card.className = 'step-timeline-card';
  card.innerHTML = `
    <div class="step-timeline-indicator">
      <div class="step-num-badge">${stepNum}</div>
      ${index < totalSteps - 1 ? '<div class="step-timeline-line"></div>' : ''}
    </div>
    <div class="step-timeline-body">
      <div class="step-card-inner">
        <div class="step-card-header">
          <span class="step-tag">LANGKAH ${String(stepNum).padStart(2, '0')}</span>
          ${title ? `<h4 class="step-title">${_fmtText(title)}</h4>` : ''}
        </div>
        <div class="step-card-content">
          <div class="step-main-text">${_fmtText(mainBody)}</div>
          ${noteText ? `
            <div class="step-note-callout">
              <i class="fa-solid fa-circle-info"></i>
              <span><strong>Catatan Penting:</strong> ${_fmtText(noteText)}</span>
            </div>
          ` : ''}
        </div>
      </div>
    </div>
  `;
  return card;
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

    // Konteks visual soal (Layer 2 — transkripsi teks gambar asli)
    const visBox = document.getElementById('canonicalVisualBox');
    const visList = document.getElementById('canonicalVisualList');
    if (visList) {
      visList.innerHTML = '';
      (data.formulas || []).forEach(f => {
        const li = document.createElement('div');
        li.className = 'visual-context-item';
        const src = f.source === 'official data-latex' ? 'data-latex resmi' : 'transkripsi vision';
        li.innerHTML = `<i class="fa-solid fa-square-root-variable"></i> <div class="vc-body"><strong>Formula</strong> <em>(${src})</em>: $${_escHtml(f.latex)}$</div>`;
        visList.appendChild(li);
      });
      (data.visual_items || []).forEach(v => {
        const li = document.createElement('div');
        li.className = 'visual-context-item';
        li.innerHTML = `<i class="fa-solid fa-chart-simple"></i> <div class="vc-body"><strong>${_escHtml(v.kind)}:</strong> ${_fmtText(v.description)}</div>`;
        visList.appendChild(li);
      });
    }
    if (visBox) {
      visBox.style.display = 'none'; // Sembunyikan konteks visual teknis dari pandangan siswa
    }

    if (data.status !== 'success' || !data.solution) {
      _renderSolutionUnavailable(data.message);
      renderMath();
      return;
    }

    const p = data.solution.pembahasan || {};
    const review = data.solution.review || {};
    const answerDisplay = data.solution.answer_display || '-';
    const canonicalId = data.solution.canonical_id || q.nomor;

    // 1. Solution Summary & Official Answer Banner (Elevated Certificate Seal)
    const banner = document.getElementById('solutionSummaryBanner');
    if (banner) {
      // Format statement answers nicely if multi-part
      let keyMarkup = '';
      if (answerDisplay.includes(',')) {
        const parts = answerDisplay.split(',').map(s => s.trim());
        keyMarkup = `
          <div class="key-pills-wrap">
            ${parts.map(pt => {
              const isBenar = pt.toLowerCase().includes('benar');
              const isSalah = pt.toLowerCase().includes('salah');
              const cls = isBenar ? 'key-pill-green' : (isSalah ? 'key-pill-red' : 'key-pill-blue');
              return `<span class="key-statement-pill ${cls}">${_escHtml(pt)}</span>`;
            }).join('')}
          </div>
        `;
      } else {
        keyMarkup = `<div class="key-badge-large">${_escHtml(answerDisplay)}</div>`;
      }

      banner.innerHTML = `
        <div class="summary-seal-row">
          <div class="summary-seal-left">
            <div class="summary-seal-icon"><i class="fa-solid fa-circle-check"></i></div>
            <div class="summary-seal-text">
              <div class="seal-heading">Kunci Jawaban Resmi</div>
              <div class="seal-subheading">Kunci dari publikasi resmi TKA Pusmendik · Pembahasan disusun otomatis (AI) dan masih perlu ditinjau</div>
            </div>
          </div>
          <div class="summary-seal-right">
            <span class="key-badge-caption">KUNCI RESMI</span>
            ${keyMarkup}
          </div>
        </div>
        <div class="summary-meta-bar">
          <span class="meta-tag"><i class="fa-solid fa-book"></i> Sumber kunci: TKA Pusmendik Kemendikdasmen</span>
          <span class="meta-tag"><i class="fa-solid fa-robot"></i> Pembahasan: disusun AI · belum direview manusia</span>
        </div>
      `;
      banner.style.display = 'block';
    }

    // 2. Pilar 1: Identifikasi Masalah (Dik & Dit) + Konsep Kunci
    const konsepList = Array.isArray(p.konsep_kunci) ? p.konsep_kunci : [];
    const conceptContainer = document.getElementById('conceptContainer');
    const conceptBox = document.getElementById('conceptBox');
    if (conceptContainer) {
      let dikDitHtml = '';
      if (p.diketahui || p.ditanyakan) {
        dikDitHtml = `
          <div class="dik-dit-grid">
            <div class="dik-dit-card dik">
              <div class="dik-dit-badge-tag"><i class="fa-solid fa-clipboard-list"></i> DIKETAHUI (DIK)</div>
              <div class="dik-dit-text">${_bulletListHtml(p.diketahui || '-')}</div>
            </div>
            <div class="dik-dit-card dit">
              <div class="dik-dit-badge-tag"><i class="fa-solid fa-circle-question"></i> DITANYAKAN (DIT)</div>
              <div class="dik-dit-text">${_bulletListHtml(p.ditanyakan || '-')}</div>
            </div>
          </div>
        `;
      }

      let konsepItemsHtml = '';
      if (konsepList.length) {
        konsepItemsHtml = `
          <div class="pillar-sub-section-title">
            <i class="fa-solid fa-key"></i> Konsep & Rumus Utama yang Menghubungkan:
          </div>
          <div class="concept-items-wrap">
            ${konsepList.map(k => `
              <div class="concept-card-item">
                <div class="concept-card-icon"><i class="fa-solid fa-check"></i></div>
                <div class="concept-card-text">${_fmtText(k)}</div>
              </div>
            `).join('')}
          </div>
        `;
      }

      conceptContainer.innerHTML = dikDitHtml + konsepItemsHtml;
      if (conceptBox) conceptBox.style.display = 'block';
    }

    // 3. Pilar 2: Glosarium Simbol & Notasi
    const symBox = document.getElementById('symbolsBox');
    const symList = document.getElementById('symbolsContainer');
    const glos = p.glosarium_simbol || [];
    if (glos.length && symList && symBox) {
      symList.innerHTML = '';
      glos.forEach(sym => {
        const card = document.createElement('div');
        card.className = 'symbol-card';
        const isMath = sym.simbol.includes('\\') || sym.simbol.includes('∩') || sym.simbol.includes('∪') || sym.simbol.includes('^');
        const badgeContent = isMath
          ? (sym.simbol.startsWith('$') ? sym.simbol : `$${sym.simbol}$`)
          : _escHtml(sym.simbol);
        card.innerHTML = `
          <div class="symbol-card-top">
            <span class="symbol-badge">${badgeContent}</span>
            ${sym.nama ? `<span class="symbol-name">${_escHtml(sym.nama)}</span>` : ''}
          </div>
          <div class="symbol-desc">${_fmtText(sym.arti)}</div>
        `;
        symList.appendChild(card);
      });
      symBox.style.display = 'block';
    } else if (symBox) {
      symBox.style.display = 'none';
    }

    // 4. Pilar 3: Memahami Logika Konsep (Mengapa Rumus Ini Dipakai?)
    const whyBox = document.getElementById('whyConceptBox');
    const whyTextEl = document.getElementById('whyConceptContainer');
    if (whyBox && whyTextEl) {
      if (p.mengapa_begini) {
        whyBox.style.display = 'block';
        whyTextEl.innerHTML = _bulletListHtml(p.mengapa_begini);
      } else {
        whyBox.style.display = 'none';
      }
    }

    // 5. Pilar 4: Langkah-Langkah Pengerjaan Rinci
    const stepsContainer = document.getElementById('stepsContainer');
    if (stepsContainer) {
      stepsContainer.innerHTML = '';
      const langkahList = p.langkah_penyelesaian || [];
      const totalSteps = langkahList.length;

      // Peringatan jika perlu verifikasi manual
      if (review.needs_manual_review) {
        const revAlert = document.createElement('div');
        revAlert.id = 'solutionReviewBadge';
        revAlert.className = 'solution-review-alert';
        revAlert.innerHTML = `
          <div class="alert-icon"><i class="fa-solid fa-triangle-exclamation"></i></div>
          <div class="alert-content">
            <div class="alert-title">Perlu Verifikasi Manual</div>
            <div class="alert-msg">Sebagian informasi sumber soal ini masih menunggu peninjauan dan belum final.</div>
            ${review.review_reason ? `
              <details class="alert-details">
                <summary>Lihat catatan peninjauan</summary>
                <div class="details-body">${_fmtText(review.review_reason)}</div>
              </details>
            ` : ''}
          </div>
        `;
        stepsContainer.appendChild(revAlert);
      }

      langkahList.forEach((stepText, idx) => {
        const card = _renderStepTimelineCard(stepText, idx, totalSteps);
        stepsContainer.appendChild(card);
      });
    }

    // 6. Pilar 5: Tips Cepat & Antisipasi Jebakan Soal (Permantap Dual Cards)
    const tipsContainer = document.getElementById('tipsContainer');
    if (tipsContainer) {
      const tipsList = Array.isArray(p.tips_list) ? p.tips_list : [];
      const mistakesList = Array.isArray(p.mistakes_list) ? p.mistakes_list : [];

      if (tipsList.length || mistakesList.length) {
        tipsContainer.innerHTML = `
          <div class="tips-dual-grid">
            ${tipsList.length ? `
              <div class="tips-subcard shortcut">
                <div class="tips-subcard-header">
                  <i class="fa-solid fa-bolt"></i>
                  <span>Trik Cepat & Efisiensi Ujian</span>
                </div>
                <ul class="tips-bullet-list">
                  ${tipsList.map(t => `<li>${_fmtText(t)}</li>`).join('')}
                </ul>
              </div>
            ` : ''}
            ${mistakesList.length ? `
              <div class="tips-subcard trap">
                <div class="tips-subcard-header">
                  <i class="fa-solid fa-triangle-exclamation"></i>
                  <span>Jebakan Umum yang Harus Dihindari</span>
                </div>
                <ul class="tips-bullet-list trap-list">
                  ${mistakesList.map(m => `<li>${_fmtText(m)}</li>`).join('')}
                </ul>
              </div>
            ` : ''}
          </div>
        `;
      } else if (p.tips_trik) {
        tipsContainer.innerHTML = `<div class="tips-text-legacy">${_bulletListHtml(p.tips_trik)}</div>`;
      } else {
        tipsContainer.innerHTML = '<span class="empty-hint">Lakukan pengecekan teliti pada setiap tahap penurunan rumus di atas.</span>';
      }
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
  let inCode = false;
  let codeLang = '';
  let codeLines = [];
  let inTable = false;
  let tableRows = [];

  function inline(text) {
    // Lindungi token matematika agar tidak terpotong oleh html-escape atau markdown italic
    const mathTokens = [];
    let t = text.replace(/(\$\$[\s\S]*?\$\$|\$[^\$]+?\$)/g, (match) => {
      mathTokens.push(match);
      return `___MATH_TOKEN_${mathTokens.length - 1}___`;
    });

    t = _escHtml(t);
    t = t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/\*([^\*]+)\*/g, '<em>$1</em>');
    t = t.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Kembalikan token matematika apa adanya untuk KaTeX
    t = t.replace(/___MATH_TOKEN_(\d+)___/g, (_, idx) => {
      return mathTokens[parseInt(idx, 10)] || '';
    });
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

  function flushTable() {
    if (inTable && tableRows.length > 0) {
      let tableHtml = '<div class="ai-table-wrap"><table>';
      const hasHeader = tableRows.length >= 2 && tableRows[1].some(c => /^:?-+:?$/.test(c.trim()));
      if (hasHeader) {
        tableHtml += '<thead><tr>';
        tableRows[0].forEach(cell => {
          tableHtml += `<th>${inline(cell.trim())}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';
        for (let r = 2; r < tableRows.length; r++) {
          tableHtml += '<tr>';
          tableRows[r].forEach(cell => {
            tableHtml += `<td>${inline(cell.trim())}</td>`;
          });
          tableHtml += '</tr>';
        }
        tableHtml += '</tbody>';
      } else {
        tableHtml += '<tbody>';
        tableRows.forEach(row => {
          tableHtml += '<tr>';
          row.forEach(cell => {
            tableHtml += `<td>${inline(cell.trim())}</td>`;
          });
          tableHtml += '</tr>';
        });
        tableHtml += '</tbody>';
      }
      tableHtml += '</table></div>';
      html += tableHtml;
      inTable = false;
      tableRows = [];
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Fenced Code Block handling (```)
    if (trimmed.startsWith('```')) {
      flushList();
      flushCallout();
      flushTable();
      if (!inCode) {
        inCode = true;
        codeLang = trimmed.slice(3).trim();
        codeLines = [];
      } else {
        inCode = false;
        html += `<pre><code class="${codeLang ? 'language-' + _escHtml(codeLang) : ''}">${_escHtml(codeLines.join('\n'))}</code></pre>`;
        codeLines = [];
        codeLang = '';
      }
      continue;
    }

    if (inCode) {
      codeLines.push(line);
      continue;
    }

    // Markdown Table handling (| col | col |)
    if (trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.length > 2) {
      flushList();
      flushCallout();
      inTable = true;
      const cells = trimmed.split('|').slice(1, -1);
      tableRows.push(cells);
      continue;
    } else if (inTable) {
      flushTable();
    }

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
      const content = inline(line.replace(/^###\s+/, ''));
      html += `<div class="ai-h3"><i class="fa-solid fa-diamond-turn-right"></i> <span>${content}</span></div>`;
      continue;
    } else if (line.startsWith('## ')) {
      flushList();
      const content = inline(line.replace(/^##\s+/, ''));
      html += `<div class="ai-h2">${content}</div>`;
      continue;
    }

    // Block display math ($$...$$) on its own line
    const blockMathMatch = trimmed.match(/^\$\$(.+)\$\$$/);
    if (blockMathMatch) {
      flushList();
      html += `<div class="ai-block-math">$$${_escHtml(blockMathMatch[1])}$$</div>`;
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

  if (inCode && codeLines.length > 0) {
    html += `<pre><code>${_escHtml(codeLines.join('\n'))}</code></pre>`;
  }
  flushTable();
  flushList();
  flushCallout();

  return html;
}

// Cooldown & Quota Management State
let _cooldownTimer = null;
let _cooldownSecondsRemaining = 0;

function updateTutorQuotaUI(quota) {
  if (!quota) return;
  state.tutorQuota = quota;
  // panel Akun terbuka? perbarui kuota di sana juga secara live
  if (homeIsOpen() && homeActivePanel === 'akun') {
    try { sendPanelData('akun'); } catch (e) {}
  }
  const badge = document.getElementById('tutorQuotaBadge');
  const text = document.getElementById('tutorQuotaText');
  if (!badge || !text) return;

  const isSub = quota.is_subscriber || quota.tier === 'subscriber';
  const rem = quota.remaining !== undefined ? quota.remaining : 5;
  const limit = quota.daily_limit || (isSub ? 100 : 5);

  text.innerText = `${rem}/${limit} Tanya`;
  badge.className = `tutor-quota-badge ${isSub ? 'subscriber' : 'free'}`;
  badge.title = isSub
    ? `Akun Langganan: ${rem} dari ${limit} pertanyaan tersisa hari ini`
    : `Akun Gratis: ${rem} dari ${limit} pertanyaan tersisa hari ini. Jeda 10 detik per pertanyaan.`;

  // Disable input bila kuota harian habis
  const chatInput = document.getElementById('chatInput');
  const btnSend = document.getElementById('btnSendChat');
  if (rem <= 0) {
    if (chatInput) {
      chatInput.placeholder = `Kuota harianmu habis (${limit}/${limit}). Reset tiap 00:00 WIB — Pro mendapat 100x/hari!`;
      chatInput.disabled = true;
    }
    if (btnSend) btnSend.disabled = true;
  }
}

// Reset / Refresh Kuota (Mode Testing Admin)
async function refreshTutorQuota() {
  const btn = document.getElementById('btnRefreshQuota');
  if (btn) btn.classList.add('rotating');
  try {
    const res = await fetch('/api/tutor/reset_quota', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success' && data.quota) {
      if (_cooldownTimer) {
        clearInterval(_cooldownTimer);
        _cooldownTimer = null;
      }
      _cooldownSecondsRemaining = 0;
      updateTutorQuotaUI(data.quota);
      const btnSend = document.getElementById('btnSendChat');
      const chatInput = document.getElementById('chatInput');
      if (btnSend) {
        btnSend.disabled = false;
        btnSend.innerHTML = '<i class="fa-solid fa-paper-plane"></i>';
      }
      if (chatInput) {
        chatInput.disabled = false;
        chatInput.placeholder = 'Tanyakan langkah atau rumus...';
      }
    }
  } catch (err) {
    console.error('Gagal reset kuota:', err);
  } finally {
    if (btn) {
      setTimeout(() => btn.classList.remove('rotating'), 400);
    }
  }
}

function startTutorCooldown(seconds = 10) {
  if (_cooldownTimer) clearInterval(_cooldownTimer);
  _cooldownSecondsRemaining = Math.max(1, Math.ceil(seconds));

  const btnSend = document.getElementById('btnSendChat');
  const chatInput = document.getElementById('chatInput');

  function tick() {
    if (_cooldownSecondsRemaining <= 0) {
      clearInterval(_cooldownTimer);
      _cooldownTimer = null;
      if (btnSend && (!state.tutorQuota || state.tutorQuota.remaining > 0)) {
        btnSend.disabled = false;
        btnSend.innerHTML = '<i class="fa-solid fa-paper-plane"></i>';
      }
      if (chatInput && (!state.tutorQuota || state.tutorQuota.remaining > 0)) {
        chatInput.disabled = false;
        chatInput.placeholder = 'Tanyakan langkah atau rumus...';
      }
      return;
    }

    if (btnSend) {
      btnSend.disabled = true;
      btnSend.innerHTML = `<span style="font-size:11px;font-weight:700;">${_cooldownSecondsRemaining}s</span>`;
    }
    if (chatInput) {
      chatInput.disabled = true;
      chatInput.placeholder = `Tunggu ${_cooldownSecondsRemaining} detik sebelum bertanya lagi...`;
    }
    _cooldownSecondsRemaining--;
  }

  tick();
  _cooldownTimer = setInterval(tick, 1000);
}

// Render Chat Conversation History
// Helper pembersih nama model AI (tanpa emoji, nama rapi konsisten)
function cleanModelName(raw) {
  if (!raw) return 'Gemini 3 Flash';
  const str = String(raw).trim();
  const noEmoji = str.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F1E0}-\u{1F1FF}]/gu, '').trim();
  const lower = noEmoji.toLowerCase();
  if (lower.includes('flash') || lower === 'gemini-flash') return 'Gemini 3 Flash';
  if (lower.includes('pro') || lower === 'gemini-pro') return 'Gemini Pro';
  if (lower.includes('qwen') || lower === 'qwen-groq') return 'Qwen 2.5 27B';
  return noEmoji || 'Gemini 3 Flash';
}

// Render Chat Conversation History
// Sumber data = percakapan tersimpan di server (tutor_store, per user+soal).
// state.tutorMsgs adalah cache tampilan; sinkronisasi dari /api/tutor/state.
function renderChatHistory(q) {
  const chatMessages = document.getElementById('chatMessages');
  if (!chatMessages) return;
  chatMessages.innerHTML = '';

  const history = state.tutorMsgs || [];
  const subjectName = (SUBJECT_CATALOG[state.currentSubject] && SUBJECT_CATALOG[state.currentSubject].name) || 'TKA';
  const activeModelDisplay = cleanModelName(state.selectedTutorModel);

  if (history.length === 0) {
    // Default welcome message (per subject)
    const defaultWelcome = document.createElement('div');
    defaultWelcome.className = 'chat-bubble ai';
    const modelBadge = `<span class="tutor-model-badge" title="Model AI Aktif"><i class="fa-solid fa-microchip"></i> ${_escHtml(activeModelDisplay)}</span>`;
    defaultWelcome.innerHTML = `
      <div class="bubble-sender-bar">
        <div class="sender-left">
          <span class="sender-avatar"><i class="fa-solid fa-robot"></i></span>
          <span class="sender-name">AI Tutor ${subjectName}</span>
        </div>
        ${modelBadge}
      </div>
      <div class="bubble-content">
        <p class="ai-p">${(SUBJECT_CATALOG[state.currentSubject] && SUBJECT_CATALOG[state.currentSubject].welcome) || 'Halo! Masih bingung dengan konsep atau langkah pengerjaan pada soal ini? Tanyakan langsung di bawah ya!'}</p>
      </div>
    `;
    chatMessages.appendChild(defaultWelcome);
  } else {
    history.forEach(item => {
      const isUser = item.role === 'user';
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble ${isUser ? 'user' : 'ai'}`;

      if (isUser) {
        const userText = item.content.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
        bubble.innerHTML = `<div class="bubble-content"><p class="ai-p">${userText}</p></div>`;
      } else {
        const contentHtml = formatAiMessage(item.content);
        const answeringModel = cleanModelName(item.model || activeModelDisplay);
        const modelBadge = `<span class="tutor-model-badge" title="Model AI Penjawab: ${_escHtml(answeringModel)}"><i class="fa-solid fa-microchip"></i> ${_escHtml(answeringModel)}</span>`;
        bubble.innerHTML = `
          <div class="bubble-sender-bar">
            <div class="sender-left">
              <span class="sender-avatar"><i class="fa-solid fa-robot"></i></span>
              <span class="sender-name">AI Tutor ${subjectName}</span>
            </div>
            ${modelBadge}
          </div>
          <div class="bubble-content">${contentHtml}</div>
        `;
      }
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
      if (data.provider) {
        syncModelSelectorUI(data.provider);
      }
      if (data.quota) {
        updateTutorQuotaUI(data.quota);
        if (data.quota.cooldown_remaining > 0) {
          startTutorCooldown(data.quota.cooldown_remaining);
        }
      }
      renderChatHistory(q);
      const chatMessages = document.getElementById('chatMessages');
      if (chatMessages) renderMath(chatMessages);
    }
  } catch (err) {
    console.warn('Sync percakapan tutor gagal (server tidak dijangkau):', err);
  }
}

// Model Selector UI Helpers (tanpa emoji, sinkronisasi instan)
function changeTutorModel(val) {
  state.selectedTutorModel = val;
  try {
    localStorage.setItem('tka_tutor_model', val);
  } catch (e) {}
  const sel = document.getElementById('aiTutorModelSelect');
  if (sel && sel.value !== val) sel.value = val;
  updateModelPickerUI(val);
  const q = getCurrentQuestion();
  if (q) {
    renderChatHistory(q);
  }
}

// Fase 12: Model Picker Popover UI Handlers
function updateModelPickerUI(modelId) {
  if (!modelId) modelId = state.selectedTutorModel || 'qwen-groq';
  const btn = document.getElementById('btnModelPicker');
  const icon = document.getElementById('modelPickerIcon');
  
  let iconClass = 'fa-solid fa-bolt';
  let modelName = 'Qwen 2.5 27B';
  if (modelId === 'gemini-flash') {
    iconClass = 'fa-solid fa-wand-magic-sparkles';
    modelName = 'Gemini 3.8 Flash';
  } else if (modelId === 'gemini-pro') {
    iconClass = 'fa-solid fa-brain';
    modelName = 'Gemini Pro';
  } else {
    iconClass = 'fa-solid fa-bolt';
    modelName = 'Qwen 2.5 27B';
  }

  if (icon) {
    icon.className = iconClass;
  }
  if (btn) {
    btn.setAttribute('aria-label', `Model AI: ${modelName}`);
    btn.setAttribute('title', `Model AI: ${modelName}`);
  }

  const items = document.querySelectorAll('.model-popover-item');
  items.forEach(it => {
    const m = it.getAttribute('data-model');
    if (m === modelId) {
      it.classList.add('active');
      it.setAttribute('aria-selected', 'true');
    } else {
      it.classList.remove('active');
      it.removeAttribute('aria-selected');
    }
  });
}

function toggleModelPicker(e) {
  if (e) e.stopPropagation();
  const pop = document.getElementById('modelPopover');
  if (!pop) return;
  const isHidden = pop.style.display === 'none' || !pop.style.display;
  pop.style.display = isHidden ? 'block' : 'none';
  if (isHidden) {
    updateModelPickerUI(state.selectedTutorModel);
  }
}

function closeModelPopover(e) {
  if (e) e.stopPropagation();
  const pop = document.getElementById('modelPopover');
  if (pop) pop.style.display = 'none';
}

function selectModelFromPopover(modelId) {
  changeTutorModel(modelId);
  closeModelPopover();
}

// Global click-outside listener untuk menutup model popover
document.addEventListener('click', function(e) {
  const pop = document.getElementById('modelPopover');
  const btn = document.getElementById('btnModelPicker');
  if (pop && pop.style.display !== 'none') {
    if (!pop.contains(e.target) && (!btn || !btn.contains(e.target))) {
      pop.style.display = 'none';
    }
  }
});

function syncModelSelectorUI(provider) {
  const sel = document.getElementById('aiTutorModelSelect');
  if (!sel) return;
  if (provider && provider.model_options && provider.model_options.length > 0) {
    const currentVal = state.selectedTutorModel || 'qwen-groq';
    sel.innerHTML = provider.model_options.map(opt =>
      `<option value="${opt.id}" ${opt.id === currentVal ? 'selected' : ''}>${_escHtml(cleanModelName(opt.name))}</option>`
    ).join('');
  }
  let saved = localStorage.getItem('tka_tutor_model');
  // Migrasi: 'gemini-flash' adalah default lama sebelum Groq menjadi rute utama
  // tutor — dianggap bukan pilihan sadar agar default baru berlaku.
  if (saved === 'gemini-flash') {
    try { localStorage.removeItem('tka_tutor_model'); } catch (e) {}
    saved = null;
  }
  if (saved && Array.from(sel.options).some(o => o.value === saved)) {
    state.selectedTutorModel = saved;
    sel.value = saved;
  } else if (sel.options.length > 0) {
    state.selectedTutorModel = sel.value;
  }
  updateModelPickerUI(state.selectedTutorModel);
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

  if (_cooldownTimer) {
    return; // Abaikan saat masih dalam cooldown 10 detik
  }
  if (state.tutorQuota && state.tutorQuota.remaining <= 0) {
    alert("Kuota harian bertanya kamu telah habis. Berlangganan untuk mendapatkan 100 pertanyaan per hari!");
    return;
  }

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
  const subjectName = (SUBJECT_CATALOG[state.currentSubject] && SUBJECT_CATALOG[state.currentSubject].name) || 'TKA';
  typingBubble.className = 'chat-bubble ai typing-indicator';
  typingBubble.id = 'aiTypingBubble';
  typingBubble.innerHTML = `
    <div class="bubble-sender-bar">
      <div class="sender-left">
        <span class="sender-avatar"><i class="fa-solid fa-robot"></i></span>
        <span class="sender-name">AI Tutor ${subjectName}</span>
      </div>
      <span class="tutor-model-badge" title="Model Sedang Menjawab"><i class="fa-solid fa-microchip"></i> ${_escHtml(cleanModelName(state.selectedTutorModel))}</span>
    </div>
    <div class="bubble-content" style="color: var(--text-muted); font-style: italic;">
      <i class="fa-solid fa-circle-notch fa-spin"></i> Sedang menyusun penjelasan...
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
        model: state.selectedTutorModel || 'gemini-flash',
        request_id: clientRequestId
      })
    });

    const data = await res.json();
    const typingEl = document.getElementById('aiTypingBubble');
    if (typingEl) typingEl.remove();

    if (data.quota) {
      updateTutorQuotaUI(data.quota);
    }

    if (res.status === 429) {
      if (data.reason === 'cooldown' && data.wait_seconds) {
        startTutorCooldown(data.wait_seconds);
      }
      state.tutorMsgs.push({
        role: 'assistant',
        content: data.message || 'Harap tunggu beberapa detik sebelum mengirim pertanyaan berikutnya.',
        error: true
      });
      renderChatHistory(q);
      return;
    }

    if (data.status === 'success' && data.reply) {
      state.tutorMsgs.push({
        role: 'assistant',
        content: data.reply,
        model: cleanModelName(data.model || state.selectedTutorModel)
      });
      renderChatHistory(q);
      const chatMessages = document.getElementById('chatMessages');
      if (chatMessages) renderMath(chatMessages);

      // Mulai cooldown 10 detik antar pertanyaan
      startTutorCooldown(10);
    } else {
      state.tutorMsgs.push({
        role: 'assistant',
        content: data.message || 'Terjadi kendala saat menghubungi AI.',
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
    if (!_cooldownTimer && (!state.tutorQuota || state.tutorQuota.remaining > 0)) {
      btnSend.disabled = false;
      btnSend.innerHTML = '<i class="fa-solid fa-paper-plane"></i>';
    }
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

  promptEl.innerHTML = _fmtText(sim.pertanyaan || '');
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
    txt.innerHTML = _fmtText(opt.text);
    item.appendChild(txt);

    optsEl.appendChild(item);
  });

  // Render rumus KaTeX pada prompt & opsi soal serupa (teks di-escape via _fmtText).
  renderMath(promptEl);
  renderMath(optsEl);

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
      <div>${_fmtText(sim.pembahasan || sim.pembahasan_singkat || '')}</div>
    `;
  } else {
    fb.className = 'sim-feedback danger';
    fb.innerHTML = `
      <div style="font-weight: 700; margin-bottom: 4px;"><i class="fa-solid fa-circle-xmark"></i> Jawaban Latihan Belum Tepat. Kunci: Opsi ${sim.kunci}</div>
      <div>${_fmtText(sim.pembahasan || sim.pembahasan_singkat || '')}</div>
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
  const pkg = state.pkgData[pkgKey()];
  if (!pkg || !pkg.soal) return;
  const total = pkg.soal.length;
  const answered = pkg.soal.filter(isQuestionAnswered).length;
  const ragu = Object.values(state.raguStatus[pkgKey()] || {}).filter(Boolean).length;
  const belum = total - answered;

  let msg = `Kamu telah menjawab <strong>${answered}</strong> dari <strong>${total}</strong> soal.`;
  if (ragu > 0) {
    msg += `<br><span style="color:var(--warn);"><i class="fa-solid fa-triangle-exclamation"></i> Masih ada <strong>${ragu}</strong> soal ditandai ragu-ragu.</span>`;
  }
  if (belum > 0) {
    msg += `<br><span style="color:var(--wrong);"><i class="fa-solid fa-circle-exclamation"></i> Ada <strong>${belum}</strong> soal yang belum dijawab.</span>`;
  }
  msg += `<br><br>Apakah kamu yakin ingin menyelesaikan tes ini dan melihat reviu hasil nilai beserta seluruh kunci jawaban resmi TKA?`;

  document.getElementById('finishSummaryText').innerHTML = msg;
  document.getElementById('modalKonfirmasiSelesai').classList.add('open');
}

function closeFinishModal() {
  document.getElementById('modalKonfirmasiSelesai').classList.remove('open');
}

// Evaluasi satu soal -> { type: 'bs'|'pg', status: 'benar'|'salah'|'kosong', perStatement? }
function evaluateQuestion(item) {
  const ans = (state.userAnswers[pkgKey()] || {})[item.nomor];

  if (statementType(item)) {
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
  const isComplex = (item.tipe_soal === 'Pilihan Ganda Kompleks' || item.tipe === 'Pilihan Ganda Kompleks' || (Array.isArray(item.kunci_jawaban) && !statementType(item)));
  let isCorrect;
  if (isComplex) {
    const target = Array.isArray(correctKey) ? [...correctKey].sort().join(',') : String(correctKey || '');
    const user = Array.isArray(ans) ? [...ans].sort().join(',') : String(ans || '');
    isCorrect = user === target;
  } else {
    isCorrect = ans === correctKey;
  }
  return { type: 'pg', status: isCorrect ? 'benar' : 'salah' };
}

function selesaiTes() {
  if (!state.testFinished) state.testFinished = {};
  state.testFinished[pkgKey()] = true;
  closeFinishModal();
  renderReviewHasil();
}

function renderReviewHasil() {
  const pkg = state.pkgData[pkgKey()];
  if (!pkg || !pkg.soal) return;
  const soalList = pkg.soal;
  const subjectMeta = SUBJECT_CATALOG[state.currentSubject] || {};
  const pkgPath = (subjectMeta.imgBase && subjectMeta.imgBase[state.currentPkg]) || `data/${state.currentSubject}/paket_${state.currentPkg}/`;
  let benar = 0, salah = 0, kosong = 0;
  const rows = [];

  soalList.forEach((item, idx) => {
    const res = evaluateQuestion(item);
    const ans = (state.userAnswers[pkgKey()] || {})[item.nomor];

    let statusHtml = '';
    let andaHtml = '<span class="review-empty">Belum dijawab</span>';
    let kunciHtml = '';

    // Ambil cuplikan opsi teks/latex/image jika ada
    const getOptSnippet = (k) => {
      const opt = (item.pilihan_jawaban || []).find(o => o.key === k);
      if (!opt) return '';
      if (opt.text && opt.text.trim()) return opt.text.trim();
      if (opt.latex) return `$${opt.latex}$`;
      if (opt.image) {
        let base = pkgPath.endsWith('/') ? pkgPath : `${pkgPath}/`;
        let rel = (opt.image.rel_path || `images/${opt.image.filename}`).replace(/^\.?\//, '');
        if (base.endsWith('images/') && rel.startsWith('images/')) {
          rel = rel.substring(7);
        }
        return `<img src="${base}${rel}" alt="Opsi ${k}" style="max-height:48px; max-width:140px; vertical-align:middle; border-radius:4px; border:1px solid var(--border); background:#fff; padding:2px; display:inline-block;" />`;
      }
      return '';
    };

    if (res.type === 'bs') {
      const kunciMap = parseBsKunci(item);
      const stmts = item.pernyataan || [];
      const hasAnyAnswer = stmts.some(st => ans && typeof ans === 'object' && !Array.isArray(ans) && ans[st.key]);
      const allCorrect = res.perStatement.length > 0 && res.perStatement.every(s => s === 'benar');

      if (!hasAnyAnswer) {
        kosong++;
        statusHtml = '<span class="review-status-badge badge-kosong"><i class="fa-regular fa-circle"></i> Kosong</span>';
      } else if (allCorrect) {
        benar++;
        statusHtml = '<span class="review-status-badge badge-benar"><i class="fa-solid fa-check"></i> Benar</span>';
      } else {
        salah++;
        statusHtml = '<span class="review-status-badge badge-salah"><i class="fa-solid fa-xmark"></i> Salah</span>';
      }

      const partsAnda = stmts.map(st => {
        const picked = (ans && typeof ans === 'object' && !Array.isArray(ans)) ? ans[st.key] : null;
        if (!picked) {
          return `<strong>${st.key}</strong> (&mdash;)`;
        }
        const isRight = picked === kunciMap[st.key];
        const color = isRight ? 'var(--accent)' : 'var(--wrong)';
        return `<strong>${st.key}</strong> (<span style="color:${color}; font-weight:600;">${picked}</span>)`;
      });

      const partsKunci = stmts.map(st => {
        return `<strong>${st.key}</strong> (<span style="color:var(--accent); font-weight:600;">${kunciMap[st.key] || '&mdash;'}</span>)`;
      });

      andaHtml = `<div class="review-ans-multiline">${partsAnda.join('<br>')}</div>`;
      kunciHtml = `<div class="review-key-multiline">${partsKunci.join('<br>')}</div>`;
    } else {
      // Pilihan Ganda Biasa & Kompleks
      if (res.status === 'kosong') {
        kosong++;
        statusHtml = '<span class="review-status-badge badge-kosong"><i class="fa-regular fa-circle"></i> Kosong</span>';
      } else if (res.status === 'benar') {
        benar++;
        statusHtml = '<span class="review-status-badge badge-benar"><i class="fa-solid fa-check"></i> Benar</span>';
      } else {
        salah++;
        statusHtml = '<span class="review-status-badge badge-salah"><i class="fa-solid fa-xmark"></i> Salah</span>';
      }

      if (Array.isArray(ans) && ans.length > 0) {
        const itemsAnda = ans.map(k => {
          const snip = getOptSnippet(k);
          return `<strong>(${k})</strong>${snip ? ` ${snip}` : ''}`;
        });
        andaHtml = `<span class="review-ans">${itemsAnda.join('<br>')}</span>`;
      } else if (typeof ans === 'string' && ans) {
        const snip = getOptSnippet(ans);
        andaHtml = `<span class="review-ans"><strong>(${ans})</strong>${snip ? ` ${snip}` : ''}</span>`;
      } else {
        andaHtml = '<span class="review-empty">Belum dijawab</span>';
      }

      const correctKey = item.kunci_jawaban;
      if (Array.isArray(correctKey)) {
        const itemsKunci = correctKey.map(k => {
          const snip = getOptSnippet(k);
          return `<strong>(${k})</strong>${snip ? ` ${snip}` : ''}`;
        });
        kunciHtml = `<span class="review-key">${itemsKunci.join('<br>')}</span>`;
      } else if (typeof correctKey === 'string' && correctKey) {
        const snip = getOptSnippet(correctKey);
        kunciHtml = `<span class="review-key"><strong>(${correctKey})</strong>${snip ? ` ${snip}` : ''}</span>`;
      } else {
        kunciHtml = '<span class="review-key">&mdash;</span>';
      }
    }

    rows.push(`
      <tr onclick="reviewJumpTo(${idx})" title="Klik untuk membuka pembahasan soal nomor ${item.nomor}">
        <td class="review-no">${item.nomor}</td>
        <td>${statusHtml}</td>
        <td>${andaHtml}</td>
        <td>${kunciHtml}</td>
      </tr>
    `);
  });

  const totalQuestions = soalList.length;
  const persen = totalQuestions ? Math.round((benar / totalQuestions) * 100) : 0;

  const subjName = (SUBJECT_CATALOG[state.currentSubject] && SUBJECT_CATALOG[state.currentSubject].name) || state.currentSubject;
  const reviewMetaEl = document.getElementById('reviewMetaText');
  if (reviewMetaEl) {
    reviewMetaEl.innerText = `${subjName} — Paket ${state.currentPkg} (${totalQuestions} Soal)`;
    reviewMetaEl.title = `${subjName} — Paket ${state.currentPkg}`;
  }
  document.getElementById('reviewScoreBenar').innerText = benar;
  document.getElementById('reviewScoreSalah').innerText = salah;
  document.getElementById('reviewScoreKosong').innerText = kosong;
  document.getElementById('reviewScorePersen').innerText = `${persen}%`;
  document.getElementById('reviewScorePersen').className =
    'review-persen ' + (persen >= 70 ? 'good' : persen >= 40 ? 'mid' : 'low');
  document.getElementById('reviewTableBody').innerHTML = rows.join('');

  document.getElementById('reviewHasilOverlay').classList.add('open');

  // Trigger KaTeX untuk render rumus matematika di tabel hasil
  renderMath(document.getElementById('reviewTableBody'));
}

// Klik baris reviu -> lompat ke soal terkait (pembahasan terbuka)
function reviewJumpTo(idx) {
  document.getElementById('reviewHasilOverlay').classList.remove('open');
  state.currentIndex = idx;
  state.explanationVisible = true;
  state.keepWorkTab = true; // renderQuestion jangan memaksa balik ke tab soal
  renderQuestion();
  switchWorkTab('pembahasan', 'materi', { scroll: false });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function closeReviewHasil() {
  document.getElementById('reviewHasilOverlay').classList.remove('open');
}

// Ulangi simulasi: reset jawaban & status ragu paket aktif
function resetSimulasi() {
  const key = pkgKey();
  if (state.testFinished) state.testFinished[key] = false;
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
    // Audit Kimi: jawab + ragu bisa berlaku bersamaan — tampilkan dua-duanya
    if (isRagu) btn.classList.add('ragu');
    if (isAnswered) btn.classList.add('answered');
    let gridAria = `Soal ${no}`;
    if (isAnswered) gridAria += ', sudah dijawab';
    if (isRagu) gridAria += ', ditandai ragu-ragu';
    btn.setAttribute('aria-label', gridAria);

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

// Trigger KaTeX math formula rendering (Targeted for fast 60fps rendering)
function renderMath(targetEl) {
  if (window.renderMathInElement) {
    try {
      const container = targetEl || document.querySelector('.main-container') || document.body;
      renderMathInElement(container, {
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


// Image Lightbox Zoom Modal (Pinch & Button Zoom Support)
let currentLightboxScale = 1;

function openImageLightbox(src, caption) {
  const modal = document.getElementById('imageLightboxModal');
  const img = document.getElementById('lightboxImg');
  const cap = document.getElementById('lightboxCaption');
  if (!modal || !img) return;
  img.src = src;
  currentLightboxScale = 1;
  img.style.transform = 'scale(1)';
  if (cap) cap.innerText = caption || 'Pratinjau Gambar';
  modal.classList.add('open');
}

function closeImageLightbox(e) {
  if (e && e.target && (e.target.id === 'lightboxImg' || e.target.closest('.lightbox-toolbar'))) return;
  const modal = document.getElementById('imageLightboxModal');
  if (modal) {
    modal.classList.remove('open');
    resetLightboxZoom();
  }
}

function zoomLightbox(delta) {
  const img = document.getElementById('lightboxImg');
  if (!img) return;
  currentLightboxScale = Math.min(Math.max(0.5, currentLightboxScale + delta), 3.5);
  img.style.transform = `scale(${currentLightboxScale})`;
}

function resetLightboxZoom() {
  const img = document.getElementById('lightboxImg');
  if (!img) return;
  currentLightboxScale = 1;
  img.style.transform = 'scale(1)';
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const modal = document.getElementById('imageLightboxModal');
    if (modal && modal.classList.contains('open')) {
      closeImageLightbox();
    }
  }
});

// ===== Fase 2: Mobile UX =====
// Top bar (menu mapel/paket + overflow), sticky bottom bar, tutor bottom sheet.
const MOBILE_MQ = window.matchMedia('(max-width: 1024px)');

function openTutorSheet() {
  if (!isTutorSheetMode()) {
    // desktop / layar lebar: AI Tutor = full pane di tab Pembahasan & AI
    switchWorkTab('pembahasan', 'ai');
    return;
  }
  // mobile: tetap bottom sheet — aktifkan sub-pane AI tempat sheet tinggal
  switchWorkTab('pembahasan', 'ai', { scroll: false });
  const sheet = document.getElementById('cbtSidebarCol');
  const backdrop = document.getElementById('tutorBackdrop');
  if (!sheet) return;
  sheet.style.transform = '';
  sheet.classList.add('tutor-open');
  if (backdrop) backdrop.classList.add('open');
}

function closeTutorSheet() {
  const sheet = document.getElementById('cbtSidebarCol');
  const backdrop = document.getElementById('tutorBackdrop');
  if (sheet) {
    sheet.classList.remove('tutor-open');
    sheet.style.transform = '';
  }
  if (backdrop) backdrop.classList.remove('open');
  // pane sub "Tanya AI" di mobile isinya sheet fixed — balik ke materi biar tidak kosong
  if (isTutorSheetMode() && state.pembSub === 'ai') switchPembSub('materi', { scroll: false });
}

// Deteksi nyata apakah AI Tutor tampil sebagai bottom sheet: ikuti CSS aktif
// (media <=1024px), bukan hanya lebar layar — mencegah pane AI kosong di
// rentang ukuran tertentu.
function isTutorSheetMode() {
  const sheet = document.getElementById('cbtSidebarCol');
  if (!sheet) return false;
  try { return getComputedStyle(sheet).position === 'fixed'; } catch (e) { return false; }
}

function closeMobilePanels() {
  const menu = document.getElementById('mobileMenuPanel');
  const overflow = document.getElementById('mOverflowPanel');
  if (menu) menu.classList.remove('open');
  if (overflow) overflow.classList.remove('open');
}

function toggleMobilePanel(panelId) {
  const panel = document.getElementById(panelId);
  if (!panel) return;
  const willOpen = !panel.classList.contains('open');
  closeMobilePanels();
  panel.classList.toggle('open', willOpen);
}

function initTutorSheetDrag() {
  const sheet = document.getElementById('cbtSidebarCol');
  const handle = document.getElementById('tutorSheetHandle');
  if (!sheet || !handle) return;

  let dragging = false;
  let startY = 0;
  let dy = 0;

  handle.addEventListener('pointerdown', (e) => {
    if (!MOBILE_MQ.matches) return;
    dragging = true;
    startY = e.clientY;
    dy = 0;
    sheet.classList.add('dragging');
    try { handle.setPointerCapture(e.pointerId); } catch (err) {}
  });

  handle.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    dy = Math.max(0, e.clientY - startY);
    sheet.style.transform = `translateY(${dy}px)`;
  });

  const endDrag = () => {
    if (!dragging) return;
    dragging = false;
    sheet.classList.remove('dragging');
    sheet.style.transform = '';
    if (dy > 110) closeTutorSheet();
  };
  handle.addEventListener('pointerup', endDrag);
  handle.addEventListener('pointercancel', endDrag);
}

// ==================== FASE 4: Navigasi Mengambang (work-rail) Bisa Dipindah ====================
// Fitur: Long-press 400ms -> Mode geser (outline & haptic) -> Drag -> Snap (kiri/kanan x atas/tengah/bawah)
// Posisi disimpan di localStorage, aman dari tap biasa, tetap tampil di atas AI chat (z-index 75)
function initDraggableWorkRail() {
  const rail = document.getElementById('workRail');
  if (!rail) return;

  const POSITIONS = [
    'snap-top-left', 'snap-top-right',
    'snap-mid-left', 'snap-mid-right',
    'snap-bottom-left', 'snap-bottom-right'
  ];

  // Default snap class if not present
  if (!POSITIONS.some(c => rail.classList.contains(c))) {
    rail.classList.add('snap-bottom-right');
  }

  // Restore saved position
  try {
    const saved = localStorage.getItem('tka_work_rail_snap');
    if (saved && POSITIONS.includes(saved)) {
      POSITIONS.forEach(c => rail.classList.remove(c));
      rail.classList.add(saved);
    }
  } catch (e) {}

  // Pastikan ada active tab
  if (!rail.querySelector('.rail-btn.active')) {
    const soalBtn = rail.querySelector('[data-rail="soal"]');
    if (soalBtn) soalBtn.classList.add('active');
  }

  // FASE 13: Auto-Minimize State (Mobile only <= 899px)
  let autoCollapseTimer = null;
  let longPressTimer = null;
  let isDragging = false;
  let startX = 0;
  let startY = 0;
  let initialLeft = 0;
  let initialTop = 0;
  let moved = false;

  function clearLongPress() {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    }
  }

  function clearAutoCollapse() {
    if (autoCollapseTimer) {
      clearTimeout(autoCollapseTimer);
      autoCollapseTimer = null;
    }
  }

  function collapseRail() {
    if (window.innerWidth > 899) return;
    clearAutoCollapse();
    rail.classList.remove('is-expanded');
    rail.classList.add('is-minimized');
  }

  function expandRail() {
    if (window.innerWidth > 899) return;
    clearAutoCollapse();
    rail.classList.remove('is-minimized');
    rail.classList.add('is-expanded');
    // Diam 4 detik tanpa interaksi -> otomatis mengecil lagi
    autoCollapseTimer = setTimeout(collapseRail, 4000);
  }

  function resetAutoCollapse() {
    if (rail.classList.contains('is-expanded')) {
      clearAutoCollapse();
      autoCollapseTimer = setTimeout(collapseRail, 4000);
    }
  }

  // Expose global methods for testing/programmatic control
  window._collapseWorkRail = collapseRail;
  window._expandWorkRail = expandRail;

  // Initial state mobile: minimized
  if (window.innerWidth <= 899) {
    collapseRail();
  }

  function snapToNearest(clientX, clientY) {
    const winW = window.innerWidth;
    const winH = window.innerHeight;

    const snapX = clientX < winW / 2 ? 'left' : 'right';
    let snapY = 'bottom';
    if (clientY < winH * 0.35) snapY = 'top';
    else if (clientY > winH * 0.68) snapY = 'bottom';
    else snapY = 'mid';

    const snapClass = `snap-${snapY}-${snapX}`;
    POSITIONS.forEach(c => rail.classList.remove(c));
    rail.classList.add(snapClass);

    // Reset inline styles so CSS snap class with safe-area rules takes over
    rail.style.left = '';
    rail.style.right = '';
    rail.style.top = '';
    rail.style.bottom = '';
    rail.style.transform = '';

    try {
      localStorage.setItem('tka_work_rail_snap', snapClass);
    } catch (e) {}
  }

  rail.addEventListener('pointerdown', (e) => {
    // Hanya primary pointer (klik kiri / touch tunggal)
    if (e.button && e.button !== 0) return;
    startX = e.clientX;
    startY = e.clientY;
    moved = false;

    const rect = rail.getBoundingClientRect();
    initialLeft = rect.left;
    initialTop = rect.top;

    clearLongPress();
    longPressTimer = setTimeout(() => {
      isDragging = true;
      clearAutoCollapse(); // jangan auto collapse saat dragging
      rail.classList.add('rail-dragging');
      rail.style.left = initialLeft + 'px';
      rail.style.top = initialTop + 'px';
      rail.style.right = 'auto';
      rail.style.bottom = 'auto';
      rail.style.transform = 'scale(1.08)';

      if (navigator.vibrate) {
        try { navigator.vibrate(40); } catch (_) {}
      }
    }, 400);
  });

  window.addEventListener('pointermove', (e) => {
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;

    if (!isDragging) {
      // Jika digeser sebelum 400ms tercapai, batalkan long-press agar tidak bentrok dengan scroll
      if (Math.hypot(dx, dy) > 10) {
        clearLongPress();
      }
      return;
    }

    // Sedang dragging aktif
    if (e.cancelable) e.preventDefault();
    moved = true;

    const newLeft = initialLeft + dx;
    const newTop = initialTop + dy;

    // Batas layar agar tidak terlempar keluar
    const pad = 6;
    const maxLeft = window.innerWidth - rail.offsetWidth - pad;
    const maxTop = window.innerHeight - rail.offsetHeight - pad;

    rail.style.left = Math.max(pad, Math.min(maxLeft, newLeft)) + 'px';
    rail.style.top = Math.max(pad, Math.min(maxTop, newTop)) + 'px';
  }, { passive: false });

  const endDrag = (e) => {
    clearLongPress();
    if (!isDragging) return;

    isDragging = false;
    rail.classList.remove('rail-dragging');
    snapToNearest(e.clientX, e.clientY);

    // Jika tadinya expanded, restart timer 4s
    if (rail.classList.contains('is-expanded')) {
      resetAutoCollapse();
    }
  };

  window.addEventListener('pointerup', endDrag);
  window.addEventListener('pointercancel', endDrag);

  // Click & Tap handling (Capture phase)
  rail.addEventListener('click', (e) => {
    if (moved) {
      e.stopPropagation();
      e.preventDefault();
      moved = false;
      return;
    }

    if (window.innerWidth <= 899) {
      // 1. Jika dalam kondisi minimized: Tap berfungsi untuk EXPAND
      if (rail.classList.contains('is-minimized') || !rail.classList.contains('is-expanded')) {
        e.stopPropagation();
        e.preventDefault();
        expandRail();
        return;
      }

      // 2. Jika dalam kondisi expanded:
      resetAutoCollapse();
      const btn = e.target.closest('.rail-btn');
      if (btn) {
        // Biarkan onclick button terpanggil (switchWorkTab), lalu collapse rail
        setTimeout(collapseRail, 250);
      }
    }
  }, true);

  // Tap di luar rail -> collapse rail jika sedang expanded
  document.addEventListener('pointerdown', (e) => {
    if (window.innerWidth <= 899 && rail.classList.contains('is-expanded')) {
      if (!e.target.closest('#workRail')) {
        collapseRail();
      }
    }
  });

  // Interaksi kursor di dalam rail me-reset timer 4 detik
  rail.addEventListener('pointerenter', resetAutoCollapse);
}

function initMobileChrome() {
  const btnMenu = document.getElementById('btnMobileMenu');
  const btnOverflow = document.getElementById('btnMobileOverflow');
  const backdrop = document.getElementById('tutorBackdrop');

  if (btnMenu) btnMenu.addEventListener('click', () => toggleMobilePanel('mobileMenuPanel'));
  if (btnOverflow) btnOverflow.addEventListener('click', () => toggleMobilePanel('mOverflowPanel'));
  if (backdrop) backdrop.addEventListener('click', closeTutorSheet);

  document.addEventListener('click', (e) => {
    if (!e.target.closest('#mobileMenuPanel, #btnMobileMenu')) {
      const menu = document.getElementById('mobileMenuPanel');
      if (menu) menu.classList.remove('open');
    }
    if (!e.target.closest('#mOverflowPanel, #btnMobileOverflow')) {
      const overflow = document.getElementById('mOverflowPanel');
      if (overflow) overflow.classList.remove('open');
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeTutorSheet();
      closeMobilePanels();
    }
  });

  initTutorSheetDrag();
  initDraggableWorkRail();

  // Tinggi sheet mengikuti visualViewport -> composer tetap terlihat saat keyboard naik
  if (window.visualViewport) {
    const vv = window.visualViewport;
    const syncVvh = () => {
      document.documentElement.style.setProperty('--vvh', Math.round(vv.height) + 'px');
    };
    vv.addEventListener('resize', syncVvh);
    syncVvh();
  }
}

document.addEventListener('DOMContentLoaded', initMobileChrome);

// Fase 2: label tombol Cek dipendekkan di mobile agar muat satu baris di bottom bar
function syncCheckLabel() {
  const btn = document.getElementById('btnCheckAnswer');
  if (!btn) return;
  const span = btn.querySelector('span');
  if (!span) return;
  if (!span.dataset.full) span.dataset.full = span.textContent;
  span.textContent = MOBILE_MQ.matches ? 'Cek Jawaban' : span.dataset.full;
}
try {
  if (MOBILE_MQ.addEventListener) MOBILE_MQ.addEventListener('change', syncCheckLabel);
  document.addEventListener('DOMContentLoaded', syncCheckLabel);
  syncCheckLabel();
} catch (e) {}

// ===== Fase 5: Feedback non-intrusif =====
// Timing di satu config. Aktif = tab visible + ada interaksi terbaru.
// Maks 2 tampil per sesi; setelah kirim, suppress via localStorage.
const FEEDBACK_CFG = {
  firstAfterMs: 3 * 60 * 1000,      // notif #1: 3 menit pemakaian aktif
  secondAfterMs: 5 * 60 * 1000,     // notif #2: 5 menit aktif berikutnya
  suppressDays: 14,                 // setelah kirim: jangan muncul lagi selama 14 hari
  minTimerSeconds: 5 * 60,          // jangan tampil saat timer ujian < 5 menit
  activeGapMs: 90 * 1000,           // 'aktif' = ada interaksi dalam 90 detik terakhir
};
const FB_KEY_SENT = 'tka_feedback_sent';
const FB_KEY_COUNT = 'tka_feedback_count';

const _fb = {
  activeMs: 0,
  lastInteraction: 0, // 0 = belum ada interaksi; waktu aktif mulai dihitung setelah interaksi pertama
  shownCount: 0,
  target: FEEDBACK_CFG.firstAfterMs,
  rating: 0,
  busy: false,
  visible: false, // widget sedang terbuka -> ticker tidak menampilkan lagi
};

function _fbMarkInteraction() {
  _fb.lastInteraction = Date.now();
}

function _fbSentAt() {
  try { return parseInt(localStorage.getItem(FB_KEY_SENT) || '0', 10); } catch (e) { return 0; }
}

function _fbSuppressed() {
  const sent = _fbSentAt();
  return sent && (Date.now() - sent) < FEEDBACK_CFG.suppressDays * 86400000;
}

function _fbTimerSeconds() {
  const el = document.getElementById('timerText');
  if (!el) return Infinity;
  const parts = (el.innerText || '').split(':').map(Number);
  if (parts.length !== 3 || parts.some(n => isNaN(n))) return Infinity;
  return parts[0] * 3600 + parts[1] * 60 + parts[2];
}

function _fbCanShow() {
  if (_fbSuppressed()) return false;
  try {
    if (parseInt(sessionStorage.getItem(FB_KEY_COUNT) || '0', 10) >= 2) return false;
  } catch (e) {}
  if (Date.now() - _fb.lastInteraction > FEEDBACK_CFG.activeGapMs) return false;
  const ae = document.activeElement;
  if (ae && ae.id === 'chatInput') return false;
  if (_fbTimerSeconds() < FEEDBACK_CFG.minTimerSeconds) return false;
  return true;
}

function _fbShow(stage) {
  const w = document.getElementById('fbWidget');
  if (!w) return;
  w.classList.remove('pos-top', 'pos-bottom');
  // Selalu pojok kanan bawah (desktop: kotak compact, mobile: persegi panjang via media query)
  w.classList.add('pos-bottom');
  w.style.display = 'block';
  try { sessionStorage.setItem(FB_KEY_COUNT, String(stage)); } catch (e) {}
  _fb.visible = true;
}

function _fbHide() {
  const w = document.getElementById('fbWidget');
  if (w) w.style.display = 'none';
  _fb.visible = false;
}

function _fbTicker() {
  if (document.visibilityState !== 'visible') return;
  if (_fb.visible || _fb.shownCount >= 2) return;
  if (_fb.lastInteraction && Date.now() - _fb.lastInteraction <= FEEDBACK_CFG.activeGapMs) {
    _fb.activeMs += 1000;
  }
  if (_fb.busy || _fb.activeMs < _fb.target) return;
  if (_fbCanShow()) {
    _fb.shownCount += 1;
    _fbShow(_fb.shownCount);
  }
}

function _fbDismiss() {
  _fbHide();
  if (_fb.shownCount === 1) {
    // ditutup tanpa kirim -> notif #2 setelah 5 menit aktif berikutnya
    _fb.activeMs = 0;
    _fb.target = FEEDBACK_CFG.secondAfterMs;
  }
}

async function _fbSubmitFeedback() {
  if (_fb.busy || !_fb.rating) return;
  const btn = document.getElementById('fbSubmit');
  const err = document.getElementById('fbError');
  _fb.busy = true;
  btn.disabled = true;
  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rating: _fb.rating,
        message: (document.getElementById('fbText').value || '').trim(),
        device: MOBILE_MQ.matches ? 'mobile' : 'desktop',
      }),
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.status === 'success') {
      try {
        localStorage.setItem(FB_KEY_SENT, String(Date.now()));
        sessionStorage.setItem(FB_KEY_COUNT, '2');
      } catch (e) {}
      _fbHide();
      _fb.shownCount = 2;
      _fb.target = Infinity;
    } else {
      err.textContent = data.message || 'Gagal mengirim. Coba lagi.';
      err.style.display = 'block';
      btn.disabled = false;
    }
  } catch (e) {
    err.textContent = 'Gagal mengirim — periksa koneksi.';
    err.style.display = 'block';
    btn.disabled = false;
  } finally {
    _fb.busy = false;
  }
}

function initFeedback() {
  const w = document.getElementById('fbWidget');
  if (!w) return;
  if (_fbSuppressed()) return;

  ['pointerdown', 'keydown', 'touchstart', 'wheel', 'scroll'].forEach(ev =>
    document.addEventListener(ev, _fbMarkInteraction, { passive: true }));

  const stars = document.getElementById('fbStars');
  for (let i = 1; i <= 5; i++) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'fb-star';
    b.textContent = i;
    b.setAttribute('aria-label', `Nilai ${i} dari 5`);
    b.addEventListener('click', () => {
      _fb.rating = i;
      stars.querySelectorAll('.fb-star').forEach(s =>
        s.classList.toggle('active', Number(s.textContent) === i));
      document.getElementById('fbSubmit').disabled = false;
    });
    stars.appendChild(b);
  }

  document.getElementById('fbClose').addEventListener('click', _fbDismiss);
  document.getElementById('fbLater').addEventListener('click', _fbDismiss);
  document.getElementById('fbSubmit').addEventListener('click', _fbSubmitFeedback);

  setInterval(_fbTicker, 1000);
}

document.addEventListener('DOMContentLoaded', initFeedback);

// ===== Mode bagikan online: sembunyikan tombol admin (Reset kuota) =====
// Muncul lagi bila akses dengan ?admin=1 atau localStorage.tka_admin = '1'.
(function hideAdminTools() {
  try {
    const isAdmin = localStorage.getItem('tka_admin') === '1' ||
                    window.location.search.includes('admin=1');
    if (!isAdmin) {
      const btn = document.getElementById('btnRefreshQuota');
      if (btn) btn.style.display = 'none';
    }
  } catch (e) {}
})();

// ===== Timer simulasi: hitung mundur nyata + persist per paket (audit Kimi P1) =====
const TIMER_TOTAL_SECONDS = 105 * 60; // 01:45:00
let _simTimerInterval = null;

function _timerStorageKey() {
  return 'tka_timer_remaining_' + pkgKey();
}

function _fmtTimer(sec) {
  sec = Math.max(0, sec);
  const h = String(Math.floor(sec / 3600)).padStart(2, '0');
  const m = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
  const s = String(sec % 60).padStart(2, '0');
  return `${h}:${m}:${s}`;
}

function _tickSimTimer() {
  const el = document.getElementById('timerText');
  if (!el) return;
  let rem = parseInt(localStorage.getItem(_timerStorageKey()), 10);
  if (isNaN(rem)) rem = TIMER_TOTAL_SECONDS;
  if (rem > 0) {
    rem -= 1;
    try { localStorage.setItem(_timerStorageKey(), String(rem)); } catch (e) {}
  }
  el.innerText = _fmtTimer(rem);
  const pill = document.getElementById('timerPill');
  if (pill) pill.classList.toggle('timer-habis', rem <= 300);
  if (rem <= 0 && _simTimerInterval) {
    clearInterval(_simTimerInterval);
    _simTimerInterval = null;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  _tickSimTimer();
  if (!_simTimerInterval) _simTimerInterval = setInterval(_tickSimTimer, 1000);
});

// ==========================================================================
// FASE 14: KONTROL UKURAN TEKS MOBILE (90%, 100%, 115%, 130%)
// ==========================================================================
const TEXT_SCALE_LEVELS = [90, 100, 115, 130];
let currentTextScale = 100;

function initTextScale() {
  try {
    const saved = localStorage.getItem('tka_font_scale');
    if (saved && TEXT_SCALE_LEVELS.includes(parseInt(saved, 10))) {
      currentTextScale = parseInt(saved, 10);
    }
  } catch (e) {}

  applyTextScale(currentTextScale);

  // Listener pesan dari iframe panel (misal dari menu Akun)
  window.addEventListener('message', (e) => {
    if (e.data && e.data.type === 'set-font-scale') {
      const s = parseInt(e.data.scale, 10);
      if (TEXT_SCALE_LEVELS.includes(s)) {
        setTextScale(s);
      }
    }
  });

  // Listener storage perubahan dari tab lain
  window.addEventListener('storage', (e) => {
    if (e.key === 'tka_font_scale') {
      const s = parseInt(e.newValue, 10);
      if (TEXT_SCALE_LEVELS.includes(s)) {
        applyTextScale(s);
      }
    }
  });
}

function applyTextScale(scale) {
  currentTextScale = scale;
  document.documentElement.setAttribute('data-text-scale', scale.toString());

  // Update indikator UI di overflow menu & popover AI
  document.querySelectorAll('.scale-indicator, #scaleIndicator, #tutorScaleIndicator').forEach(el => {
    el.textContent = scale + '%';
  });

  // Update disabled buttons
  document.querySelectorAll('.btn-scale-dec, #btnScaleDec, #btnTutorScaleDec').forEach(btn => {
    btn.disabled = scale <= TEXT_SCALE_LEVELS[0];
  });
  document.querySelectorAll('.btn-scale-inc, #btnScaleInc, #btnTutorScaleInc').forEach(btn => {
    btn.disabled = scale >= TEXT_SCALE_LEVELS[TEXT_SCALE_LEVELS.length - 1];
  });

  // Broadcast ke semua panel iframe (Modul, Progres, Akun)
  ['panelModulFrame', 'panelProgresFrame', 'panelAkunFrame'].forEach(id => {
    const iframe = document.getElementById(id);
    if (iframe && iframe.contentWindow) {
      try {
        iframe.contentWindow.postMessage({ type: 'set-font-scale', scale: scale }, '*');
      } catch (e) {}
    }
  });
}

function setTextScale(scale) {
  if (!TEXT_SCALE_LEVELS.includes(scale)) return;
  applyTextScale(scale);
  try {
    localStorage.setItem('tka_font_scale', scale.toString());
  } catch (e) {}
}

function stepTextScale(delta) {
  const currentIndex = TEXT_SCALE_LEVELS.indexOf(currentTextScale);
  const nextIndex = Math.max(0, Math.min(TEXT_SCALE_LEVELS.length - 1, (currentIndex === -1 ? 1 : currentIndex) + delta));
  setTextScale(TEXT_SCALE_LEVELS[nextIndex]);
}

function toggleTutorScaleMenu(e) {
  if (e) {
    e.stopPropagation();
    e.preventDefault();
  }
  const pop = document.getElementById('tutorScalePopover');
  if (pop) {
    pop.style.display = pop.style.display === 'none' ? 'flex' : 'none';
  }
}

// Tutup popover skala jika klik di luar
document.addEventListener('pointerdown', (e) => {
  const pop = document.getElementById('tutorScalePopover');
  if (pop && pop.style.display !== 'none') {
    if (!e.target.closest('#tutorScalePopover, #btnTutorScale')) {
      pop.style.display = 'none';
    }
  }
});

// Panggil saat DOM siap
document.addEventListener('DOMContentLoaded', initTextScale);

// Expose fungsi ke window untuk aksesibilitas & tes
window.initTextScale = initTextScale;
window.setTextScale = setTextScale;
window.stepTextScale = stepTextScale;
window.toggleTutorScaleMenu = toggleTutorScaleMenu;

