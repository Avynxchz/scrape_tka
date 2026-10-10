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
  },
  teknik_mesin: {
    name: 'SMK - Teknik Mesin',
    json: {
      1: 'data/teknik_mesin_paket_1_learning.json'
    },
    imgBase: {
      1: 'data/teknik_mesin/paket_1/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Teknik Mesin</strong>. Ada kendala dalam memahami prinsip pemesinan, K3 bengkel, toleransi suaian, atau material teknik di soal ini? Tanyakan langsung di bawah ya!`
  },
  teknik_otomotif: {
    name: 'SMK - Teknik Otomotif (TKR)',
    json: {
      1: 'data/teknik_otomotif_paket_1_learning.json'
    },
    imgBase: {
      1: 'data/teknik_otomotif/paket_1/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Teknik Otomotif</strong>. Butuh penjelasan mengenai sistem kelistrikan bodi, mesin kendaraan ringan, chasis, atau perawatan otomotif? Tanyakan langsung di bawah ya!`
  },
  teknik_jaringan: {
    name: 'SMK - Teknik Jaringan & Telekomunikasi (TKJ)',
    json: {
      1: 'data/teknik_jaringan_paket_1_learning.json'
    },
    imgBase: {
      1: 'data/teknik_jaringan/paket_1/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Teknik Jaringan Komputer & Telekomunikasi (TKJ)</strong>. Bingung dengan subnetting, routing, konfigurasi mikrotik/cisco, atau transmisi fiber optik? Tanyakan langsung di bawah ya!`
  },
  akuntansi: {
    name: 'SMK - Akuntansi & Keuangan Lembaga',
    json: {
      1: 'data/akuntansi_paket_1_learning.json'
    },
    imgBase: {
      1: 'data/akuntansi/paket_1/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Akuntansi & Keuangan Lembaga</strong>. Ada pertanyaan seputar jurnal penyesuaian, buku besar, neraca lajur, atau laporan keuangan? Tanyakan langsung di bawah ya!`
  },
  manajemen_perkantoran: {
    name: 'SMK - Manajemen Perkantoran & Layanan Bisnis (MPLB)',
    json: {
      1: 'data/manajemen_perkantoran_paket_1_learning.json'
    },
    imgBase: {
      1: 'data/manajemen_perkantoran/paket_1/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Manajemen Perkantoran & Layanan Bisnis (MPLB)</strong>. Butuh bantuan memahami tata kelola administrasi surat, kearsipan elektronik, atau etika pelayanan kantor? Tanyakan langsung di bawah ya!`
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
  
  // Tampilkan beranda hanya jika tidak ada parameter mapel di URL
  const isDirectQuiz = Boolean(paramSub || (window.location.hash && window.location.hash.includes('soal-')));
  window.__homeFirst = !isDirectQuiz;

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

  window.__appInitialized = true;

  // Layar pertama: Home dashboard jika bukan direct kuis; jika direct kuis pastikan homeClose()
  if (window.__homeFirst) {
    homeOpen();
  } else {
    homeClose();
  }
  try { syncProgressWithServer(); } catch (e) {}
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
    icon: 'history_edu', theme: 'purple', category: 'Soshum'
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
  },
  teknik_mesin: {
    name: 'SMK - Teknik Mesin', shortName: 'Teknik Mesin', chip: 'MESIN',
    icon: 'build', theme: 'slate', category: 'Kejuruan SMK'
  },
  teknik_otomotif: {
    name: 'SMK - Teknik Otomotif (TKR)', shortName: 'Teknik Otomotif', chip: 'OTOMOTIF',
    icon: 'directions_car', theme: 'amber', category: 'Kejuruan SMK'
  },
  teknik_jaringan: {
    name: 'SMK - Teknik Jaringan & Telekomunikasi (TKJ)', shortName: 'TKJ', chip: 'TKJ',
    icon: 'router', theme: 'cyan', category: 'Kejuruan SMK'
  },
  akuntansi: {
    name: 'SMK - Akuntansi & Keuangan Lembaga', shortName: 'Akuntansi (AKL)', chip: 'AKUNTANSI',
    icon: 'account_balance', theme: 'teal', category: 'Kejuruan SMK'
  },
  manajemen_perkantoran: {
    name: 'SMK - Manajemen Perkantoran & Layanan Bisnis (MPLB)', shortName: 'MPLB', chip: 'MPLB',
    icon: 'business_center', theme: 'indigo', category: 'Kejuruan SMK'
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
  bahasa_korea: { 1: 10, 2: 29 },
  teknik_mesin: { 1: 6 },
  teknik_otomotif: { 1: 6 },
  teknik_jaringan: { 1: 6 },
  akuntansi: { 1: 6 },
  manajemen_perkantoran: { 1: 6 }
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


// FASE 5 (T5.2, T5.3): HTML kartu countdown + misi (return string, bukan prepend).
function getTkaCardsHtml() {
  try {
    const tka = getTkaDate();
    const today = new Date(); today.setHours(0,0,0,0);
    const tkaD = new Date(tka + 'T00:00:00');
    const diff = Math.round((tkaD - today) / 86400000);
    const label = diff > 0 ? 'H-' + diff : (diff === 0 ? 'Hari H!' : 'Lewat ' + (-diff) + ' hari');
    let h = '<div style="margin:0 0 12px">';
    h += '<div style="background:linear-gradient(135deg,#004a2a,#006b3f);color:#fff;border-radius:12px;padding:14px 16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">'
      + '<div><div style="font-size:12px;opacity:0.9">Tanggal TKA kamu</div>'
      + '<div style="font-size:22px;font-weight:800">' + label + '</div></div>'
      + '<label style="font-size:12px;display:flex;align-items:center;gap:8px">Ubah: '
      + '<input type="date" min="2026-10-10" max="2026-11-29" value="' + tka + '" '
      + 'style="padding:6px 8px;border-radius:8px;border:0;font-size:13px" onchange="setTkaDate(this.value);renderHome()">'
      + '</label></div></div>';
    // Misi hari ini
    let misi = null;
    try {
      const last = JSON.parse(localStorage.getItem('tka_last_autopsy') || 'null');
      if (last && last.kebocoran_1) misi = last.kebocoran_1;
    } catch (e) {}
    const labelNama = {'terburu':'Terburu-buru','overthinking':'Overthinking','macet':'Macet','yakin_salah':'Yakin tapi salah','ragu_salah':'Ragu-ragu dan salah','waktu_habis':'Kehabisan waktu','kosong':'Dikosongkan'};
    if (misi) {
      const cthRef = (misi.contoh && misi.contoh[0]) ? String(misi.contoh[0]) : '';
      h += '<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:12px;padding:14px 16px;margin:0 0 12px">'
        + '<div style="font-size:12px;font-weight:700;color:#b45309;text-transform:uppercase;margin-bottom:6px">🎯 Misi hari ini</div>'
        + '<div style="font-size:15px;font-weight:700;margin-bottom:4px;color:#92400e">Perbaiki: ' + (labelNama[misi.label] || misi.label) + '</div>'
        + '<div style="font-size:13px;color:#6b7280;margin-bottom:10px">' + (misi.bukti || '') + '</div>'
        + `<button type="button" onclick="bukaKartuStrategi('${misi.label}', '${cthRef}')" style="background:#b45309;color:#fff;border:none;border-radius:6px;padding:6px 14px;font-size:11.5px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:6px;">📖 Pelajari Strategi Misi</button>`
        + '</div>';
    } else {
      h += '<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:12px;padding:14px 16px;margin:0 0 12px">'
        + '<div style="font-size:12px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:6px">🎯 Misi hari ini</div>'
        + '<div style="font-size:13px;color:#6b7280;margin-bottom:10px">Selesaikan 1 tryout untuk mengidentifikasi kebocoran skor dan membuka misi belajarmu.</div>'
        + '<button type="button" onclick="homeClose();" style="background:#004a2a;color:#fff;border:none;border-radius:6px;padding:6px 14px;font-size:11.5px;font-weight:700;cursor:pointer;">🚀 Mulai Latihan Tryout</button>'
        + '</div>';
    }
    return h;
  } catch (e) { return ''; }
}

// FASE 5 (T5.3): Date picker "Tanggal TKA kamu?" + hitung mundur H-n.
function getTkaDate() {
  try {
    const d = localStorage.getItem('tka_date');
    if (d && /^\d{4}-\d{2}-\d{2}$/.test(d)) return d;
  } catch (e) {}
  return '2026-10-26';
}
function setTkaDate(v) {
  try { localStorage.setItem('tka_date', v); } catch (e) {}
  // Sync ke server (best effort)
  try {
    if (typeof _attemptAuthHeader === 'function') {
      _attemptAuthHeader().then(hdr => {
        if (hdr.Authorization) {
          fetch('/api/user/tka_date', {
            method: 'POST',
            headers: Object.assign({'Content-Type': 'application/json'}, hdr),
            body: JSON.stringify({tka_date: v})
          }).catch(()=>{});
        }
      });
    }
  } catch (e) {}
}
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
    const availablePkgs = SUBJECT_CATALOG[k] && SUBJECT_CATALOG[k].json ? Object.keys(SUBJECT_CATALOG[k].json).map(Number) : [1, 2];
    const cards = availablePkgs.map(pkg => {
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

  // FASE 5 (T5.2, T5.3): kartu countdown + misi di atas daftar mapel
  const tkaCardsHtml = getTkaCardsHtml();
  main.innerHTML = tkaCardsHtml + `
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
      // FASE 3 (T3.2): mulai perekaman attempt (jalur kartu langsung / mobile)
      try {
        const _pkg = state.pkgData[pkgKey()];
        const _n = (_pkg && _pkg.soal) ? _pkg.soal.length : 0;
        AttemptRecorder.start(subject, pkg, _n, getTimerTotalSeconds());
      } catch (e) {}
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
  ov.style.display = '';
  ov.style.pointerEvents = '';
  document.body.style.overflow = 'hidden';
  // Kembali ke beranda: hapus tanda mode kuis
  delete document.body.dataset.quizMode;
  try {
    const hasOAuthHash = window.location.hash && (window.location.hash.includes('access_token=') || window.location.hash.includes('refresh_token=') || window.location.hash.includes('error_description='));
    const hasOAuthSearch = window.location.search && (window.location.search.includes('code=') || window.location.search.includes('error='));
    if (!hasOAuthHash && !hasOAuthSearch && (window.location.search || window.location.hash)) {
      window.history.replaceState(null, '', window.location.pathname);
    }
  } catch (e) {}
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
  let user = null;
  if (typeof getTKAUser === 'function') user = getTKAUser();
  else if (window.TKA_USER) user = window.TKA_USER;
  const isLogin = !!(user && user.loggedIn);
  const quota = state.tutorQuota || {
    remaining: isLogin ? 25 : 5,
    daily_limit: isLogin ? 25 : 5,
    tier: 'free',
    is_logged_in: isLogin
  };
  postToFrameReliable(frame, () => ({
    type: 'home-desktop-data',
    subjects: buildSubjectsPayload(['matematika', 'fisika', 'ekonomi']),
    progress: homeProgressSummary(),
    user: user,
    quota: quota,
  }));
}

// Urutan 22 mapel umum + 5 mapel SMK sesuai kurikulum Pusmendik (dipakai panel Modul & Progres)
const PANEL_MODULE_ORDER = [
  'matematika', 'bahasa_indonesia', 'bahasa_inggris', 'fisika', 'kimia', 'biologi',
  'ekonomi', 'geografi', 'sosiologi', 'sejarah', 'antropologi', 'kewirausahaan',
  'matematika_lanjut', 'bahasa_indonesia_lanjut', 'bahasa_inggris_lanjut',
  'ppkn', 'bahasa_arab', 'bahasa_jepang', 'bahasa_jerman', 'bahasa_prancis', 'bahasa_mandarin', 'bahasa_korea',
  'teknik_mesin', 'teknik_otomotif', 'teknik_jaringan', 'akuntansi', 'manajemen_perkantoran'
];

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

// Handler konfirmasi mulai belajar mapel (Desktop & Mobile)
let _pendingStartPackage = null;

function showStartPackageConfirmModal(subject, pkg) {
  _pendingStartPackage = { subject, pkg: parseInt(pkg || 1, 10) };
  const meta = SUBJECT_CATALOG[subject] || {};
  const subjName = meta.name || subject;
  const count = (typeof homePkgCount === 'function' ? homePkgCount(subject, _pendingStartPackage.pkg) : 20) || 20;
  // FASE 3 (T3.4): kuis direkomendasikan login — hasil tryout tersimpan di akun untuk Autopsi.
  let _bguest = document.getElementById('btnConfirmStartGuest');
  if (typeof _isLoggedIn === 'function' && !_isLoggedIn()) {
    _pendingStartPackage = { subject, pkg: parseInt(pkg || 1, 10) };
    const _t = document.getElementById('startMapelTitle');
    const _d = document.getElementById('startMapelDesc');
    const _b = document.getElementById('btnConfirmStartMapel');
    const _m = document.getElementById('modalKonfirmasiMulaiMapel');
    if (_t) _t.innerText = 'Login dulu yuk';
    if (_d) _d.innerHTML = 'Hasil tryout dapat tersimpan di akunmu untuk dianalisis (<strong>Autopsi Belajar</strong>).<br><br>Login dengan Google — gratis &amp; cepat.<br><span style="display:inline-block;margin-top:6px;font-size:12px;color:#6b7280;">Atau coba dulu sebagai Tamu (dapat diklaim setelah selesai kuis).</span>';
    if (_b) { 
      _b.innerHTML = '<i class="fa-brands fa-google"></i> Login Google'; 
      _b.onclick = function() { try { closeStartPackageModal(); if (typeof loginWithGoogle === 'function') loginWithGoogle(); } catch (e) {} }; 
    }
    if (!_bguest && _m) {
      const actions = _m.querySelector('.finish-actions');
      if (actions) {
        _bguest = document.createElement('button');
        _bguest.id = 'btnConfirmStartGuest';
        _bguest.className = 'btn-finish';
        _bguest.type = 'button';
        _bguest.style.cssText = 'flex: 1; background: #f3f4f6; color: #374151; font-size: 13px; font-weight: 600; border: 1px solid #d1d5db; border-radius: 10px; cursor: pointer; padding: 10px 14px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;';
        _bguest.innerHTML = '<i class="fa-solid fa-user"></i> Coba Tamu';
        actions.appendChild(_bguest);
      }
    }
    if (_bguest) {
      _bguest.style.display = 'inline-flex';
      _bguest.onclick = function() { executeStartPackage(); };
    }
    if (_m) { _m.classList.add('open'); if (window.TKAHistory) TKAHistory.push('modal-start'); }
    return;
  }
  if (_bguest) _bguest.style.display = 'none';
  // Kembalikan tombol ke fungsi semula (setelah pernah jadi tombol login)
  const _b0 = document.getElementById('btnConfirmStartMapel');
  if (_b0) { _b0.innerHTML = '<i class="fa-solid fa-play"></i> Mulai Sekarang'; _b0.onclick = function() { executeStartPackage(); }; }
  // T2.7: estimasi menit mengikuti timer per paket (bukan 45/50 basi)
  const _jh3 = { matematika: 3.0, bahasa_indonesia: 2.5, bahasa_inggris: 2.5 };
  const minutes = Math.round(count * (_jh3[subject] || 2.4));
  
  const titleEl = document.getElementById('startMapelTitle');
  const descEl = document.getElementById('startMapelDesc');
  const modal = document.getElementById('modalKonfirmasiMulaiMapel');
  
  if (titleEl) {
    titleEl.innerText = `Mulai Belajar ${subjName}?`;
  }
  if (descEl) {
    descEl.innerHTML = `Kamu akan memulai pengerjaan latihan <strong>${subjName} &middot; Paket ${_pendingStartPackage.pkg}</strong>.<br>`
      + `Terdiri dari <strong>${count} Soal</strong> dengan estimasi waktu <strong>${minutes} Menit</strong>.<br><br>`
      + `Jawaban dan nilai kamu otomatis tersimpan di dalam progres belajar.`;
  }
  if (modal) {
    modal.classList.add('open');
    if (window.TKAHistory) TKAHistory.push('modal-start');
  }
}

function closeStartPackageModal() {
  const modal = document.getElementById('modalKonfirmasiMulaiMapel');
  if (modal) modal.classList.remove('open');
  _pendingStartPackage = null;
}

async function executeStartPackage() {
  if (!_pendingStartPackage) return;
  const target = { ..._pendingStartPackage };
  closeStartPackageModal();
  // Beranda ditutup setelah konfirmasi mulai belajar
  if (typeof homeClose === 'function') homeClose();
  try {
    if (state.currentSubject !== target.subject) await switchSubject(target.subject);
    await switchPackage(target.pkg);
    // FASE 3 (T3.2): mulai perekaman attempt
    try {
      const _pkg = state.pkgData[pkgKey()];
      const _n = (_pkg && _pkg.soal) ? _pkg.soal.length : 0;
      AttemptRecorder.start(target.subject, target.pkg, _n, getTimerTotalSeconds());
    } catch (e) {}
  } catch (err) {
    console.error('Gagal membuka paket mapel:', err);
  }
}

// Terima event dari iframe panel (klik paket, nav, sinyal ready)
const panelReadyReplied = {}; // throttle balasan sinyal ready per panel
window.addEventListener('message', async (e) => {
  const d = e.data || {};
  if (d.type === 'open-package') {
    showStartPackageConfirmModal(d.subject, d.pkg);
  } else if (d.type === 'home-desktop-ready' || d.type === 'modul-ready' || d.type === 'request-data' || d.type === 'akun-ready') {
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
    }
  } else if (d.type === 'login-google') {
    // Iframe (home_desktop/akun) minta login Google — jalankan di window utama
    // (Google blokir OAuth dalam iframe). supabase_auth.js dimuat di parent.
    if (typeof loginWithGoogle === 'function') {
      loginWithGoogle();
    }
  } else if (d.type === 'modul-scroll') {
    // Iframe Modul kasih tau arah scroll -> navbar parent ngumpet/muncul
    var header = document.querySelector('.stitch-fixed-top, header.stitch-fixed-top');
    if (header) {
      header.style.transition = 'transform 0.3s ease';
      header.style.transform = d.direction === 'down' ? 'translateY(-100%)' : 'translateY(0)';
    }
  } else if (d.type === 'logout' || d.type === 'request-logout') {
    // Iframe minta logout — tampilkan modal konfirmasi keluar yang estetik
    if (typeof showLogoutConfirmationModal === 'function') {
      showLogoutConfirmationModal();
    } else if (typeof logout === 'function') {
      logout();
    }
  } else if (d.type === 'nav' || d.type === 'nav-tab') {
    // Panel switcher: pesan dari iframe panel mana pun (Beranda/Modul/Progres/Akun).
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
  window.homeActivePanel = name;

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
    let profile = state.akunProfile || null;
    if (!profile && typeof getTKAUser === 'function') {
      const u = getTKAUser();
      if (u && u.loggedIn) {
        profile = {
          name: u.name,
          nama: u.name,
          email: u.email,
          avatar: u.avatar,
          avatar_url: u.avatar,
          login: true,
          loggedIn: true,
          tier: 'Gratis',
          sub: u.email
        };
        state.akunProfile = profile;
      }
    }
    const isLogin = !!(profile && profile.loggedIn);
    const quota = state.tutorQuota || {
      remaining: isLogin ? 25 : 5,
      daily_limit: isLogin ? 25 : 5,
      tier: 'free',
      is_logged_in: isLogin
    };
    postToFrameReliable(frame, () => ({
      type: 'akun-data',
      profile: profile,
      quota: quota,
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

// Helper pengenal unik perangkat (Device Tracking & Fingerprinting untuk kuota tamu)
function getOrCreateDeviceId() {
  let did = null;
  try {
    did = localStorage.getItem('tka_device_id');
  } catch (e) {}
  if (!did) {
    did = 'did_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 10);
    try {
      localStorage.setItem('tka_device_id', did);
    } catch (e) {}
  }
  return did;
}

function getDeviceFingerprint() {
  try {
    const nav = window.navigator || {};
    const scr = window.screen || {};
    const parts = [
      nav.userAgent || '',
      nav.language || '',
      (scr.width || 0) + 'x' + (scr.height || 0) + 'x' + (scr.colorDepth || 0),
      new Date().getTimezoneOffset(),
      nav.hardwareConcurrency || '',
      nav.deviceMemory || '',
      nav.platform || ''
    ];
    const str = parts.join('|');
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return 'dfp_' + Math.abs(hash).toString(36);
  } catch (e) {
    return 'dfp_unknown';
  }
}

// Helper otentikasi AI Tutor ke backend server.py
function getTutorAuthHeaders() {
  const user = typeof getTKAUser === 'function' ? getTKAUser() : (window.TKA_USER || null);
  const headers = {};
  headers['X-Device-Id'] = getOrCreateDeviceId();
  headers['X-Device-Fingerprint'] = getDeviceFingerprint();
  if (user && user.loggedIn) {
    headers['X-User-Email'] = user.email || '';
    headers['X-User-Logged-In'] = 'true';
    if (user.name) headers['X-User-Name'] = encodeURIComponent(user.name);
  }
  return headers;
}

// Sinkronkan tier kuota (guest=5 vs free=25) langsung ke server.py
async function syncTutorUserToServer(user) {
  try {
    const isLogin = !!(user && user.loggedIn);
    // T2.11: sertakan Supabase access token agar server bisa memverifikasi
    // login bila AUTH_VERIFY=1. Tanpa token, server menganggap tamu (aman).
    let authHeader = {};
    try {
      const sessRaw = localStorage.getItem('tka_supabase_auth_token');
      if (sessRaw) {
        const sess = JSON.parse(sessRaw);
        if (sess && sess.access_token) authHeader = { 'Authorization': 'Bearer ' + sess.access_token };
      }
    } catch (e) {}
    const res = await fetch('/api/tutor/sync_user', {
      method: 'POST',
      headers: Object.assign({ 'Content-Type': 'application/json' }, authHeader),
      body: JSON.stringify({
        logged_in: isLogin,
        is_logged_in: isLogin,
        email: isLogin ? (user.email || '') : null
      })
    });
    const data = await res.json();
    if (data && data.quota) {
      updateTutorQuotaUI(data.quota);
    }
  } catch (e) {
    // Offline / fallback lokal
  }
}

// Cek simpanan user saat pertama kali app dimuat
try {
  const initSavedUser = localStorage.getItem('tka_user');
  if (initSavedUser) {
    const parsedUser = JSON.parse(initSavedUser);
    if (parsedUser && parsedUser.loggedIn) {
      window.TKA_USER = parsedUser;
      syncTutorUserToServer(parsedUser);
    }
  }
} catch (e) {}

// Listener sinkronisasi status login & kuota dari supabase_auth.js
window.addEventListener('tka-login', (e) => {
  const user = e.detail || (typeof getTKAUser === 'function' ? getTKAUser() : null);
  if (user && user.loggedIn) {
    state.akunProfile = {
      name: user.name,
      nama: user.name,
      email: user.email,
      avatar: user.avatar,
      avatar_url: user.avatar,
      login: true,
      loggedIn: true,
      tier: 'Gratis',
      sub: user.email
    };
    state.tutorQuota = { remaining: 25, daily_limit: 25, tier: 'free', is_logged_in: true };
    if (typeof updateTutorQuotaUI === 'function') {
      updateTutorQuotaUI(state.tutorQuota);
    }
    syncTutorUserToServer(user);
    sendPanelData('akun');
    sendPanelData('beranda');
    // FASE 3 (T3.4): Tamu-claim — klaim antrean hasil tryout yang dikerjakan saat mode tamu
    try {
      setTimeout(syncAttempts, 500);
    } catch (e) {}
  }
});

window.addEventListener('tka-logout', () => {
  _progressServerSynced = false;
  window._progressServerSynced = false;
  state.akunProfile = null;
  state.tutorQuota = { remaining: 5, daily_limit: 5, tier: 'guest', is_logged_in: false };
  if (typeof updateTutorQuotaUI === 'function') {
    updateTutorQuotaUI(state.tutorQuota);
  }
  syncTutorUserToServer({ loggedIn: false });
  sendPanelData('akun');
  sendPanelData('beranda');
});

// BUGFIX (10 Okt 2026 - T2/BUG-009): Sinkronisasi URL kuis hanya saat kuis sedang aktif
function syncQuizUrl() {
  try {
    if (!window.__appInitialized) return;
    const pkg = state.pkgData && state.pkgData[pkgKey()];
    const q = (pkg && pkg.soal && pkg.soal[state.currentIndex]) || { nomor: state.currentIndex + 1 };
    document.cookie = `active_subject=${state.currentSubject}; path=/; max-age=86400`;
    document.cookie = `active_paket=${state.currentPkg}; path=/; max-age=86400`;
    const targetUrl = `?subject=${encodeURIComponent(state.currentSubject)}&paket=${state.currentPkg}`;
    const hasOAuthHash = window.location.hash && (window.location.hash.includes('access_token=') || window.location.hash.includes('refresh_token=') || window.location.hash.includes('error_description='));
    const hasOAuthSearch = window.location.search && (window.location.search.includes('code=') || window.location.search.includes('error='));
    if (!hasOAuthHash && !hasOAuthSearch) {
      const currentTarget = `${targetUrl}#soal-${q.nomor}`;
      if (window.location.search !== targetUrl || window.location.hash !== `#soal-${q.nomor}`) {
        window.history.replaceState(null, '', currentTarget);
      }
    }
  } catch (e) {}
}
window.syncQuizUrl = syncQuizUrl;

function homeClose() {
  const ov = document.getElementById('homeOverlay');
  if (!ov) return;
  ov.classList.add('home-hidden');
  ov.style.display = 'none';
  ov.style.pointerEvents = 'none';
  document.body.style.overflow = '';
  // Tandai mode kuis: di desktop, pemilih mapel & paket disembunyikan
  // (user sudah memilih di beranda, tidak perlu ganti-ganti di tengah kuis)
  document.body.dataset.quizMode = '1';
  syncQuizUrl();
}

// BUGFIX (9 Okt 2026): overlay beranda tidak menutupi kuis saat akses via URL langsung atau dalam kuis
(function() {
  try {
    var q = new URLSearchParams(window.location.search);
    if (q.get('subject')) {
      homeClose();
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', homeClose);
      }
    }
  } catch (e) {}
})();

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
  if (!subject || !subject.json || !subject.json[pkgNum]) return;
  try {
    const res = await fetch(`${subject.json[pkgNum]}?t=${Date.now()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    state.pkgData[key] = await res.json();

    // Initialize per-key state maps lazily so access never hits undefined
    if (!state.userAnswers[key]) state.userAnswers[key] = {};
    if (!state.raguStatus[key]) state.raguStatus[key] = {};
    if (!state.simAnswers[key]) state.simAnswers[key] = {};
    if (!state.chatHistory[key]) state.chatHistory[key] = {};
    // FASE 3 (T3.5): Pulihkan jawaban & status ragu tersimpan jika user me-refresh tab
    try {
      const savedAns = localStorage.getItem('tka_answers_' + key);
      if (savedAns) state.userAnswers[key] = Object.assign({}, JSON.parse(savedAns), state.userAnswers[key]);
      const savedRagu = localStorage.getItem('tka_ragu_' + key);
      if (savedRagu) state.raguStatus[key] = Object.assign({}, JSON.parse(savedRagu), state.raguStatus[key]);
      if (localStorage.getItem('tka_finished_' + key) === 'true') {
        if (!state.testFinished) state.testFinished = {};
        state.testFinished[key] = true;
      }
      const savedChecked = localStorage.getItem('tka_checked_' + key);
      if (savedChecked) {
        const parsed = JSON.parse(savedChecked);
        if (parsed && typeof parsed === 'object') {
          if (!window._answerChecked) window._answerChecked = {};
          Object.keys(parsed).forEach(nomor => {
            if (parsed[nomor]) window._answerChecked[key + ':' + nomor] = true;
          });
        }
      }
    } catch (e) {}
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

  const loads = [loadPackageData(1)];
  if (SUBJECT_CATALOG[subjectKey]?.json?.[2]) {
    loads.push(loadPackageData(2));
  }
  await Promise.all(loads);

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
  // FASE 3 (T3.2): rekam kunjungan + waktu aktif per soal
  try { AttemptRecorder.onVisit(q.nomor, q.topik || null); } catch (e) {}

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
  if (typeof homeIsOpen === 'function' && !homeIsOpen() && !window.__homeFirst) {
    syncQuizUrl();
  }

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
      if (isComplex) {
        const complexNotice = document.createElement('div');
        complexNotice.className = 'complex-notice-pill';
        const numKeys = Array.isArray(q.kunci_jawaban) ? q.kunci_jawaban.length : 2;
        complexNotice.style.cssText = 'background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;padding:8px 14px;margin-bottom:12px;display:flex;align-items:center;gap:10px;font-size:12.5px;color:#0369a1;font-weight:700;';
        complexNotice.innerHTML = `<i class="fa-solid fa-square-check" style="font-size:16px;color:#0284c7;"></i> <span>Pilihan Ganda Kompleks · Jawaban benar lebih dari satu (Pilih ${numKeys} Opsi)</span>`;
        optionsContainer.appendChild(complexNotice);
      }
      opts.forEach(opt => {
      const isSelected = isComplex
        ? (Array.isArray(currentSelection) && currentSelection.includes(opt.key))
        : (currentSelection === opt.key);

      const optItem = document.createElement('div');
      optItem.className = `option-item ${isComplex ? 'complex-opt' : ''} ${isSelected ? 'selected' : ''}`;
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

      // Key indicator (Kotak untuk PG Kompleks, Bulat untuk PG Biasa)
      const indicator = document.createElement('div');
      indicator.className = `opt-indicator ${isComplex ? 'is-checkbox' : ''}`;
      if (isComplex) {
        indicator.style.borderRadius = '6px';
        indicator.innerHTML = isSelected ? '<i class="fa-solid fa-check" style="font-size:11px;"></i>' : opt.key;
      } else {
        indicator.innerText = opt.key;
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

  // Sinkronkan status Tes Selesai / Mode Reviu (Pengecekan Nilai & Kunci Jawaban)
  const isFinished = isTestFinished();
  const btnFinishHeader = document.getElementById('btnFinishHeader');
  const btnFinishModal = document.querySelector('.btn-finish-from-modal');

  if (isFinished) {
    if (btnFinishHeader) {
      btnFinishHeader.innerHTML = '<i class="fa-solid fa-clipboard-check"></i> <span>Reviu Hasil</span>';
      btnFinishHeader.title = 'Buka Reviu Nilai & Kunci Jawaban';
      btnFinishHeader.onclick = () => renderReviewHasil();
      btnFinishHeader.classList.add('btn-reviu-active');
    }
    if (btnFinishModal) {
      btnFinishModal.innerHTML = '<i class="fa-solid fa-clipboard-check"></i> Buka Reviu Hasil & Kunci Jawaban';
      btnFinishModal.onclick = () => { closeDaftarModal(); renderReviewHasil(); };
    }
  } else {
    if (btnFinishHeader) {
      btnFinishHeader.innerHTML = '<i class="fa-solid fa-flag-checkered"></i> <span>Selesai Tes</span>';
      btnFinishHeader.title = 'Selesai dan lihat hasil tes';
      btnFinishHeader.onclick = () => openFinishModal();
      btnFinishHeader.classList.remove('btn-reviu-active');
    }
    if (btnFinishModal) {
      btnFinishModal.innerHTML = '<i class="fa-solid fa-flag-checkered"></i> Selesai Tes';
      btnFinishModal.onclick = () => { closeDaftarModal(); openFinishModal(); };
    }
  }

  // Tombol Cek Jawaban di bilah bawah selalu bertindak sebagai Cek Jawaban (standar)
  const btnCheck = document.getElementById('btnCheckAnswer');
  if (btnCheck) {
    btnCheck.onclick = () => checkUserAnswer();
    btnCheck.style.background = '';
    btnCheck.style.color = '';
    if (typeof syncCheckLabel === 'function') syncCheckLabel();
  }

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
  // BUGFIX (10 Okt 2026): kunci opsi setelah jawaban dicek (tidak bisa diubah lagi)
  try {
    if (window._answerChecked && window._answerChecked[pkgKey() + ':' + q.nomor]) return;
  } catch (e) {}

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

  // FASE 3 (T3.2): rekam jawaban untuk Autopsi
  try { AttemptRecorder.onAnswer(q.nomor, key); } catch (e) {}
  // FASE 3 (T3.5): simpan jawaban ke localStorage agar tahan refresh
  try { localStorage.setItem('tka_answers_' + pkgKey(), JSON.stringify(state.userAnswers[pkgKey()])); } catch (e) {}

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
    scheduleSyncProgressToServer();
  } catch (e) { /* localStorage gagal: jangan ganggu UI */ }
}

window._progressServerSynced = false;

let _progressSyncTimer = null;
function scheduleSyncProgressToServer() {
  if (_progressSyncTimer) clearTimeout(_progressSyncTimer);
  _progressSyncTimer = setTimeout(() => {
    saveProgressToServer();
  }, 1200);
}

async function saveProgressToServer() {
  try {
    // T3c: hanya boleh POST jika GET sudah sukses (window._progressServerSynced = true)
    if (!window._progressServerSynced) {
      await syncProgressWithServer();
      if (!window._progressServerSynced) return;
    }
    if (typeof _attemptAuthHeader !== 'function') return;
    const hdr = await _attemptAuthHeader();
    if (!hdr.Authorization) return;
    const store = JSON.parse(localStorage.getItem('tka_progress') || '{}');
    await fetch('/api/user/progress', {
      method: 'POST',
      headers: Object.assign({ 'Content-Type': 'application/json' }, hdr),
      body: JSON.stringify({ progress: store })
    });
  } catch (e) {}
}
window.saveProgressToServer = saveProgressToServer;

async function syncProgressWithServer() {
  try {
    if (typeof _attemptAuthHeader !== 'function') return;
    const hdr = await _attemptAuthHeader();
    if (!hdr.Authorization) return;

    // T3a: Identifikasi akun yang sedang login
    const u = (typeof getTKAUser === 'function' ? getTKAUser() : null) || window.TKA_USER || {};
    const currentOwner = u.email || u.id || (typeof currentUser !== 'undefined' && currentUser && currentUser.email) || 'user';
    const savedOwner = localStorage.getItem('tka_progress_owner');

    const res = await fetch('/api/user/progress', {
      headers: hdr
    });
    if (!res.ok) return;
    const data = await res.json();
    if (data.status === 'success') {
      _progressServerSynced = true;
      window._progressServerSynced = true;
      const serverProgress = data.progress || {};
      let finalProgress = {};

      if (savedOwner && savedOwner !== currentOwner) {
        // T3a: Akun berbeda di perangkat yang sama (misal komputer lab)!
        // Buang data lokal akun sebelumnya, gunakan data bersih milik akun ini dari server.
        finalProgress = serverProgress;
      } else if (!savedOwner) {
        // Data dari tamu yang baru pertama kali login: gabungkan (merge) ke server
        const localProgress = JSON.parse(localStorage.getItem('tka_progress') || '{}');
        finalProgress = Object.assign({}, localProgress);
        for (const [sub, pkgs] of Object.entries(serverProgress)) {
          if (!finalProgress[sub]) finalProgress[sub] = {};
          for (const [pkgNo, questions] of Object.entries(pkgs)) {
            if (!finalProgress[sub][pkgNo]) finalProgress[sub][pkgNo] = {};
            for (const [qNo, qVal] of Object.entries(questions)) {
              if (!finalProgress[sub][pkgNo][qNo]) {
                finalProgress[sub][pkgNo][qNo] = qVal;
              }
            }
          }
        }
      } else {
        // Akun yang sama: gabungkan local dan server
        const localProgress = JSON.parse(localStorage.getItem('tka_progress') || '{}');
        finalProgress = Object.assign({}, localProgress);
        for (const [sub, pkgs] of Object.entries(serverProgress)) {
          if (!finalProgress[sub]) finalProgress[sub] = {};
          for (const [pkgNo, questions] of Object.entries(pkgs)) {
            if (!finalProgress[sub][pkgNo]) finalProgress[sub][pkgNo] = {};
            for (const [qNo, qVal] of Object.entries(questions)) {
              if (!finalProgress[sub][pkgNo][qNo]) {
                finalProgress[sub][pkgNo][qNo] = qVal;
              }
            }
          }
        }
      }

      localStorage.setItem('tka_progress', JSON.stringify(finalProgress));
      localStorage.setItem('tka_progress_owner', currentOwner);

      if (data.tka_date && !localStorage.getItem('tka_date')) {
        localStorage.setItem('tka_date', data.tka_date);
      }

      if (typeof renderHome === 'function') renderHome();
      saveProgressToServer();
    }
  } catch (e) {
    console.warn("syncProgressWithServer failed:", e);
  }
}
window.syncProgressWithServer = syncProgressWithServer;
window.addEventListener('tka-login', () => { syncProgressWithServer(); });

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
  // FASE 3 (T3.5): simpan jawaban BS ke localStorage
  try { localStorage.setItem('tka_answers_' + pkgKey(), JSON.stringify(state.userAnswers[pkgKey()])); } catch (e) {}

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
    let tableRowsHtml = '';

    stmts.forEach(st => {
      const userVal = sel[st.key] || '-';
      const targetVal = kunci[st.key] || '-';
      const isRight = (userVal === targetVal);
      if (isRight) benar++;

      const row = document.querySelector(`.bs-row[data-stmt="${st.key}"]`);
      if (row) {
        row.classList.toggle('correct', isRight);
        row.classList.toggle('incorrect', !isRight);
      }

      tableRowsHtml += `
        <tr style="border-bottom:1px solid #e2e8f0;">
          <td style="padding:6px 8px;font-weight:700;color:#1e293b;text-align:center;">${st.key}</td>
          <td style="padding:6px 8px;color:#334155;text-align:center;">${userVal}</td>
          <td style="padding:6px 8px;font-weight:700;color:#0f172a;text-align:center;">${targetVal}</td>
          <td style="padding:6px 8px;text-align:center;">
            ${isRight 
              ? '<span style="color:#15803d;font-weight:700;background:#dcfce7;padding:3px 8px;border-radius:6px;font-size:11px;">✅ Tepat</span>'
              : '<span style="color:#b91c1c;font-weight:700;background:#fee2e2;padding:3px 8px;border-radius:6px;font-size:11px;">❌ Berbeda</span>'}
          </td>
        </tr>
      `;
    });

    feedback.style.display = 'flex';
    const isAllRight = (benar === stmts.length);
    feedback.className = `feedback-banner ${isAllRight ? 'success' : 'danger'}`;
    feedback.innerHTML = `
      <div class="fb-card-inner">
        <div class="fb-main-info" style="width:100%;">
          <div class="fb-status-badge ${isAllRight ? 'correct' : 'incorrect'}">
            <i class="fa-solid ${isAllRight ? 'fa-circle-check' : 'fa-circle-info'}"></i>
            <span>${isAllRight ? 'Sempurna! Semua Pernyataan Sesuai Kunci' : `${benar} dari ${stmts.length} Pernyataan Tepat`}</span>
          </div>
          <div class="fb-text-msg" style="margin-bottom:8px;">
            ${isAllRight 
              ? 'Analisis logikamu untuk setiap pernyataan tepat sekali!' 
              : 'Berikut perbandingan pilihan jawabanmu dengan kunci resmi TKA Pusmendik:'}
          </div>
          <div style="overflow-x:auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:6px;margin:8px 0 12px;">
            <table style="width:100%;border-collapse:collapse;font-size:12px;">
              <thead>
                <tr style="background:#f8fafc;border-bottom:1px solid #cbd5e1;color:#475569;font-size:11px;text-transform:uppercase;">
                  <th style="padding:6px;text-align:center;">Baris</th>
                  <th style="padding:6px;text-align:center;">Pilihan Kamu</th>
                  <th style="padding:6px;text-align:center;">Kunci Resmi</th>
                  <th style="padding:6px;text-align:center;">Hasil</th>
                </tr>
              </thead>
              <tbody>${tableRowsHtml}</tbody>
            </table>
          </div>
        </div>
        <div class="fb-action-buttons">
          <button type="button" class="btn-fb-action btn-fb-pembahasan" onclick="kePembahasanDariCheck()">
            <i class="fa-solid fa-lightbulb"></i>
            <span>Lihat Pembahasan</span>
          </button>
          <button type="button" class="btn-fb-action btn-fb-next" onclick="navigateQuestion(1)">
            <span>Soal Berikutnya</span>
            <i class="fa-solid fa-arrow-right"></i>
          </button>
        </div>
      </div>
    `;

    state.explanationVisible = true;
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
  const userArr = Array.isArray(currentSelection) ? currentSelection : (currentSelection ? [currentSelection] : []);

  if (isComplex) {
    const sortedUser = [...userArr].sort().join(',');
    const sortedTarget = [...targetArr].sort().join(',');
    isCorrect = (sortedUser === sortedTarget);

    const benarDipilih = userArr.filter(k => targetArr.includes(k));
    const salahDipilih = userArr.filter(k => !targetArr.includes(k));
    const belumDipilih = targetArr.filter(k => !userArr.includes(k));
    const totalOpts = (q.pilihan_jawaban || []).length || 5;

    // Highlight options di layar
    document.querySelectorAll('.option-item').forEach(el => {
      const k = el.dataset.key;
      const isTarget = targetArr.includes(k);
      const isUserPick = userArr.includes(k);
      el.classList.toggle('correct', isTarget);
      if (isUserPick && !isTarget) {
        el.classList.add('incorrect');
      }
    });

    feedback.style.display = 'flex';
    if (isCorrect) {
      feedback.className = 'feedback-banner success';
      feedback.innerHTML = `
        <div class="fb-card-inner">
          <div class="fb-main-info">
            <div class="fb-status-badge correct">
              <i class="fa-solid fa-circle-check"></i>
              <span>Luar Biasa! Jawabanmu Benar Sempurna!</span>
            </div>
            <div class="fb-text-msg">
              Kamu berhasil memilih seluruh kunci jawaban yang tepat: <strong>(${targetArr.join(', ')})</strong>.
            </div>
          </div>
          <div class="fb-action-buttons">
            <button type="button" class="btn-fb-action btn-fb-pembahasan" onclick="kePembahasanDariCheck()">
              <i class="fa-solid fa-lightbulb"></i>
              <span>Lihat Pembahasan</span>
            </button>
            <button type="button" class="btn-fb-action btn-fb-next" onclick="navigateQuestion(1)">
              <span>Soal Berikutnya</span>
              <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>
        </div>
      `;
    } else if (userArr.length >= totalOpts && salahDipilih.length > 0) {
      // Siswa mencentang semua opsi tanpa membaca
      feedback.className = 'feedback-banner danger';
      feedback.innerHTML = `
        <div class="fb-card-inner">
          <div class="fb-main-info">
            <div class="fb-status-badge incorrect">
              <i class="fa-solid fa-triangle-exclamation"></i>
              <span>Semua Opsi Terpilih</span>
            </div>
            <div class="fb-text-msg">
              Kamu mencentang seluruh opsi. Kunci jawaban resmi hanya <strong>(${targetArr.join(', ')})</strong>. Skor proporsional: 0%.
            </div>
          </div>
          <div class="fb-action-buttons">
            <button type="button" class="btn-fb-action btn-fb-pembahasan" onclick="kePembahasanDariCheck()">
              <i class="fa-solid fa-lightbulb"></i>
              <span>Lihat Pembahasan</span>
            </button>
            <button type="button" class="btn-fb-action btn-fb-next" onclick="navigateQuestion(1)">
              <span>Soal Berikutnya</span>
              <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>
        </div>
      `;
    } else if (benarDipilih.length > 0 && salahDipilih.length === 0) {
      // Siswa tepat memilih 1 dari 2 (seperti kasus Agus memilih E pada soal A & E)
      const pct = Math.round((benarDipilih.length / targetArr.length) * 100);
      feedback.className = 'feedback-banner warn';
      feedback.innerHTML = `
        <div class="fb-card-inner">
          <div class="fb-main-info">
            <div class="fb-status-badge warn" style="background:#fef3c7;color:#b45309;">
              <i class="fa-solid fa-circle-half-stroke"></i>
              <span>Sebagian Benar (${benarDipilih.length} dari ${targetArr.length} Jawaban — ${pct}%)</span>
            </div>
            <div class="fb-text-msg">
              Pilihan kamu <strong>(${benarDipilih.join(', ')})</strong> tepat! Namun soal ini memiliki lebih dari satu jawaban benar. Kunci resmi lengkapnya adalah <strong>(${targetArr.join(', ')})</strong>. Opsi <strong>(${belumDipilih.join(', ')})</strong> belum kamu pilih.
            </div>
          </div>
          <div class="fb-action-buttons">
            <button type="button" class="btn-fb-action btn-fb-pembahasan" onclick="kePembahasanDariCheck()">
              <i class="fa-solid fa-lightbulb"></i>
              <span>Lihat Pembahasan</span>
            </button>
            <button type="button" class="btn-fb-action btn-fb-next" onclick="navigateQuestion(1)">
              <span>Soal Berikutnya</span>
              <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>
        </div>
      `;
    } else {
      // Ada opsi yang keliru
      feedback.className = 'feedback-banner danger';
      feedback.innerHTML = `
        <div class="fb-card-inner">
          <div class="fb-main-info">
            <div class="fb-status-badge incorrect">
              <i class="fa-solid fa-circle-xmark"></i>
              <span>Jawaban Belum Tepat</span>
            </div>
            <div class="fb-text-msg">
              Pilihanmu: <strong>(${userArr.join(', ')})</strong>.<br>
              ${benarDipilih.length ? `Opsi tepat: <strong>(${benarDipilih.join(', ')})</strong>. ` : ''}
              Kunci jawaban resmi yang benar adalah <strong>(${targetArr.join(', ')})</strong>.
            </div>
          </div>
          <div class="fb-action-buttons">
            <button type="button" class="btn-fb-action btn-fb-pembahasan" onclick="kePembahasanDariCheck()">
              <i class="fa-solid fa-lightbulb"></i>
              <span>Lihat Pembahasan</span>
            </button>
            <button type="button" class="btn-fb-action btn-fb-next" onclick="navigateQuestion(1)">
              <span>Soal Berikutnya</span>
              <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>
        </div>
      `;
    }
  } else {
    // Pilihan Ganda Biasa (Single Option)
    isCorrect = (currentSelection === correctKey);

    document.querySelectorAll('.option-item').forEach(el => {
      const k = el.dataset.key;
      const isTarget = (k === correctKey);
      el.classList.toggle('correct', isTarget);
      if (!isTarget && el.classList.contains('selected')) {
        el.classList.add('incorrect');
      }
    });

    feedback.style.display = 'flex';
    feedback.className = `feedback-banner ${isCorrect ? 'success' : 'danger'}`;
    feedback.innerHTML = `
      <div class="fb-card-inner">
        <div class="fb-main-info">
          <div class="fb-status-badge ${isCorrect ? 'correct' : 'incorrect'}">
            <i class="fa-solid ${isCorrect ? 'fa-circle-check' : 'fa-circle-xmark'}"></i>
            <span>${isCorrect ? 'Jawaban Kamu Benar!' : 'Jawaban Belum Tepat'}</span>
          </div>
          <div class="fb-text-msg">
            ${isCorrect 
              ? 'Pilihan jawabanmu tepat sekali! Ingin memperdalam rumus atau materi pada soal ini?' 
              : `Kunci jawaban yang benar adalah <strong>${correctKey || '-'}</strong>. Mau mengecek pembahasan langkahnya?`}
          </div>
        </div>
        <div class="fb-action-buttons">
          <button type="button" class="btn-fb-action btn-fb-pembahasan" onclick="kePembahasanDariCheck()">
            <i class="fa-solid fa-lightbulb"></i>
            <span>Lihat Pembahasan</span>
          </button>
          <button type="button" class="btn-fb-action btn-fb-next" onclick="navigateQuestion(1)">
            <span>Soal Berikutnya</span>
            <i class="fa-solid fa-arrow-right"></i>
          </button>
        </div>
      </div>
    `;
  }

  state.explanationVisible = true;
  // BUGFIX (10 Okt 2026): tandai sudah dicek agar opsi terkunci spesifik per mapel dan paket (tahan refresh via localStorage)
  try {
    if (!window._answerChecked) window._answerChecked = {};
    window._answerChecked[pkgKey() + ':' + q.nomor] = true;
    const curChecked = JSON.parse(localStorage.getItem('tka_checked_' + pkgKey()) || '{}');
    curChecked[q.nomor] = true;
    localStorage.setItem('tka_checked_' + pkgKey(), JSON.stringify(curChecked));
  } catch (e) {}
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
    if (!o.fromBack && window.TKAHistory) {
      TKAHistory.push('tab-pembahasan');
    }
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
    renderMath(panePemb);
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

// Setelah cek jawaban: salin hasil ke strip tab Pembahasan
// TIDAK ADA auto-redirect paksa — user bebas memilih apakah ingin klik "Lihat Pembahasan"
// atau tetap di lembar soal / lanjut ke nomor berikutnya.
function showPembahasanAfterCheck() {
  const fb = document.getElementById('feedbackBanner');
  const strip = document.getElementById('pembResultStrip');
  if (fb && strip) {
    strip.className = fb.className.replace('feedback-banner', 'feedback-banner pemb-strip');
    strip.innerHTML = fb.innerHTML;
    strip.style.display = fb.style.display;
  }
}

function kePembahasanDariCheck() {
  state.explanationVisible = true;
  const learnSec = document.getElementById('learningSection');
  if (learnSec) learnSec.style.display = 'flex';
  const txtToggle = document.getElementById('txtToggleExp');
  if (txtToggle) txtToggle.innerText = 'Tutup Tata Cara & Pembahasan';
  switchWorkTab('pembahasan', 'materi', { scroll: true });
}
window.kePembahasanDariCheck = kePembahasanDariCheck;

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
  if (!s) return '';
  let str = String(s);
  // Lindungi display math $$...$$ agar baris baru di dalamnya tidak diubah jadi <br>
  str = str.replace(/\$\$([\s\S]*?)\$\$/g, (m, inner) => {
    return '$$' + inner.replace(/\n+/g, ' ') + '$$';
  });
  let text = _escHtml(str);
  // Decode kembali karakter math khusus yang di-escape agar KaTeX tidak gagal me-render
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, (m, inner) => {
    return '$$' + inner.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"') + '$$';
  });
  text = text.replace(/\$([^\$\n]+?)\$/g, (m, inner) => {
    return '$' + inner.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"') + '$';
  });
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
    try { setupPillarAccordions(); } catch (e) {}
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
  const tkaUser = typeof getTKAUser === 'function' ? getTKAUser() : (window.TKA_USER || null);
  const isLogin = tkaUser ? !!tkaUser.loggedIn : !!quota.is_logged_in;
  const isSub = quota.is_subscriber || quota.tier === 'subscriber';
  // Aturan pasti Founder: Pro=100, Login Google=25, Tamu=5
  const limit = isSub ? 100 : (isLogin ? 25 : 5);

  let used = 0;
  if (typeof quota.daily_count === 'number') {
    used = quota.daily_count;
  } else if (typeof quota.daily_limit === 'number' && typeof quota.remaining === 'number') {
    used = Math.max(0, quota.daily_limit - quota.remaining);
  }
  const rem = Math.max(0, limit - used);

  state.tutorQuota = {
    daily_limit: limit,
    remaining: rem,
    daily_count: used,
    is_logged_in: isLogin,
    tier: isSub ? 'subscriber' : (isLogin ? 'free' : 'guest')
  };

  // panel Akun terbuka? perbarui kuota di sana juga secara live
  if (homeIsOpen() && homeActivePanel === 'akun') {
    try { sendPanelData('akun'); } catch (e) {}
  }

  const badge = document.getElementById('tutorQuotaBadge');
  const text = document.getElementById('tutorQuotaText');
  if (badge && text) {
    text.innerText = `${rem}/${limit} Tanya`;
    badge.className = `tutor-quota-badge ${isSub ? 'subscriber' : (isLogin ? 'user-login' : 'free')}`;
    badge.title = isSub
      ? `Akun Langganan: ${rem} dari ${limit} pertanyaan tersisa hari ini`
      : (isLogin 
          ? `Akun Google: ${rem} dari ${limit} pertanyaan tersisa hari ini` 
          : `Akun Tamu: ${rem} dari ${limit} pertanyaan tersisa hari ini. Login untuk 25 tanya/hari!`);
  }

  // Update hero slide 3 info bila ada
  const heroSlideInfo = document.getElementById('heroSlideInfo');
  if (heroSlideInfo) {
    const p = heroSlideInfo.querySelector('p');
    if (p) {
      p.textContent = isLogin
        ? `Bingung di tengah soal? Konsultasikan pembahasannya — ${limit} tanya/hari untuk akunmu.`
        : 'Bingung di tengah soal? Konsultasikan pembahasannya — 5 tanya/hari gratis.';
    }
  }

  // Disable input bila kuota harian habis
  const chatInput = document.getElementById('chatInput');
  const btnSend = document.getElementById('btnSendChat');
  if (rem <= 0) {
    if (chatInput) {
      chatInput.placeholder = `Kuota harianmu habis (${limit}/${limit}). Reset tiap 00:00 WIB — Pro mendapat 100x/hari!`;
      chatInput.disabled = true;
    }
    if (btnSend) btnSend.disabled = true;
  } else {
    if (chatInput && chatInput.disabled) {
      chatInput.placeholder = 'Tanyakan langkah atau rumus...';
      chatInput.disabled = false;
    }
    if (btnSend && btnSend.disabled) {
      btnSend.disabled = false;
    }
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
  if (!raw) return 'Qwen 2.5 27B';
  const str = String(raw).trim();
  const noEmoji = str.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F1E0}-\u{1F1FF}]/gu, '').trim();
  const lower = noEmoji.toLowerCase();
  if (lower.includes('openrouter') || lower.includes('qwen-openrouter')) return 'Qwen 7B (OpenRouter)';
  if (lower.includes('flash') || lower === 'gemini-flash') return 'Gemini 3 Flash';
  if (lower.includes('pro') || lower === 'gemini-pro') return 'Gemini Pro';
  if (lower.includes('qwen') || lower === 'qwen-groq') return 'Qwen 2.5 27B';
  return noEmoji || 'AI Tutor';
}

// Render Chat Conversation History
// Sumber data = percakapan tersimpan di server (tutor_store, per user+soal).
// state.tutorMsgs adalah cache tampilan; sinkronisasi dari /api/tutor/state.
// C9: Kartu soal collapsible di atas chat AI (Soal & Opsi Lengkap termasuk Gambar/Rumus)
function updateChatQuestionCard(q) {
  const card = document.getElementById('chatQuestionCard');
  const title = document.getElementById('chatQuestionTitle');
  const body = document.getElementById('chatQuestionBody');
  if (!card || !q) {
    if (card) card.style.display = 'none';
    return;
  }
  card.style.display = 'block';
  if (title) title.textContent = `Soal No. ${q.nomor} — Pratinjau Soal`;

  if (body) {
    const subjectMeta = (typeof SUBJECT_CATALOG !== 'undefined' && SUBJECT_CATALOG[state.currentSubject]) || {};
    const pkgPath = (subjectMeta.imgBase && subjectMeta.imgBase[state.currentPkg]) || `data/${state.currentSubject}/paket_${state.currentPkg}/`;

    let html = '';

    // 1. Stimulus (bila tersedia)
    if (q.stimulus) {
      if (q.stimulus.html && typeof formatPusmendikHtml === 'function') {
        html += `<div class="chat-qcard-stimulus" style="font-size:13px;color:#374151;margin-bottom:8px;padding-bottom:8px;border-bottom:1px dashed #e5e7eb">${formatPusmendikHtml(q.stimulus.html, pkgPath)}</div>`;
      } else if (q.stimulus.text) {
        html += `<div class="chat-qcard-stimulus" style="font-size:13px;color:#374151;margin-bottom:8px;padding-bottom:8px;border-bottom:1px dashed #e5e7eb">${_fmtText(q.stimulus.text)}</div>`;
      }
      if (Array.isArray(q.stimulus.images) && q.stimulus.images.length > 0) {
        html += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">';
        q.stimulus.images.forEach(sImg => {
          const sRel = (sImg.rel_path || `images/${sImg.filename}`).replace(/^\.?\//, '');
          const sSrc = `${pkgPath}${sRel}?v=41`;
          html += `<img loading="lazy" src="${sSrc}" alt="Stimulus" style="max-width:100%;max-height:120px;border-radius:6px;border:1px solid #e5e7eb;cursor:zoom-in" onclick="openImageLightbox('${sSrc}', 'Gambar Stimulus')" />`;
        });
        html += '</div>';
      }
    }

    // 2. Pertanyaan
    let pertContent = '';
    if (q.pertanyaan) {
      if (q.pertanyaan.html && typeof formatPusmendikHtml === 'function') {
        pertContent = formatPusmendikHtml(q.pertanyaan.html, pkgPath);
      } else if (q.pertanyaan.text) {
        pertContent = _fmtText(q.pertanyaan.text);
      } else if (typeof q.pertanyaan === 'string') {
        pertContent = _fmtText(q.pertanyaan);
      }
    } else if (q.teks) {
      pertContent = _fmtText(q.teks);
    }

    html += `<div class="chat-qcard-prompt" style="font-weight:600;font-size:13.5px;color:#111827;margin-bottom:10px;line-height:1.45">${pertContent || 'Pertanyaan tidak dapat dimuat.'}</div>`;

    if (q.pertanyaan && Array.isArray(q.pertanyaan.images) && q.pertanyaan.images.length > 0) {
      html += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px">';
      q.pertanyaan.images.forEach(pImg => {
        const pRel = (pImg.rel_path || `images/${pImg.filename}`).replace(/^\.?\//, '');
        const pSrc = `${pkgPath}${pRel}?v=41`;
        html += `<img loading="lazy" src="${pSrc}" alt="Gambar Soal" style="max-width:100%;max-height:120px;border-radius:6px;border:1px solid #e5e7eb;cursor:zoom-in" onclick="openImageLightbox('${pSrc}', 'Gambar Soal')" />`;
      });
      html += '</div>';
    }

    // 3. Pilihan Jawaban / Pernyataan
    const opts = q.pilihan_jawaban || [];
    if (opts.length > 0) {
      html += '<div class="chat-qcard-options" style="display:flex;flex-direction:column;gap:6px">';
      opts.forEach(o => {
        let optBody = '';
        if (o.html && typeof formatPusmendikHtml === 'function') {
          // Bersihkan prefiks huruf duplikat jika ada di HTML
          let cleanHtml = (o.html || '').replace(/^(<p[^>]*>)?\s*[A-E][.\)]\s+(?=[0-9A-Z($])/i, '$1');
          optBody = formatPusmendikHtml(cleanHtml, pkgPath);
        } else if (o.image) {
          let base = pkgPath.endsWith('/') ? pkgPath : `${pkgPath}/`;
          let rel = (o.image.rel_path || `images/${o.image.filename}`).replace(/^\.?\//, '');
          if (base.endsWith('images/') && rel.startsWith('images/')) rel = rel.substring(7);
          const imgSrc = `${base}${rel}?v=41`;
          optBody = `<div style="display:flex;align-items:center;gap:6px"><img loading="lazy" src="${imgSrc}" alt="Opsi ${o.key}" style="max-height:48px;max-width:240px;border-radius:4px" />${o.text ? `<span>${_fmtText(o.text)}</span>` : ''}</div>`;
        } else if (o.latex) {
          optBody = `$${o.latex}$`;
        } else if (o.text) {
          optBody = _fmtText(o.text);
        } else if (o.full_display) {
          optBody = _fmtText(o.full_display);
        }

        html += `
          <div style="display:flex;align-items:flex-start;gap:8px;padding:6px 10px;background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;font-size:13px;line-height:1.4">
            <span style="font-weight:700;color:#004a2a;min-width:18px">${o.key}.</span>
            <div style="flex:1;overflow-x:auto">${optBody}</div>
          </div>
        `;
      });
      html += '</div>';
    } else if (Array.isArray(q.pernyataan) && q.pernyataan.length > 0) {
      // Tabel pernyataan Benar/Salah
      html += '<div style="display:flex;flex-direction:column;gap:4px">';
      q.pernyataan.forEach(st => {
        html += `
          <div style="padding:6px 10px;background:#fff;border:1px solid #e5e7eb;border-radius:8px;font-size:12.5px">
            <b>${st.key || ''}.</b> ${st.teks || st.text || ''}
          </div>
        `;
      });
      html += '</div>';
    }

    body.innerHTML = html;

    // Render KaTeX pada konten kartu soal di chat
    if (typeof renderMath === 'function') {
      renderMath(body);
    }
  }
}

function toggleChatQuestion() {
  const body = document.getElementById('chatQuestionBody');
  const chevron = document.getElementById('chatQuestionChevron');
  if (!body) return;
  const isHidden = body.style.display === 'none';
  body.style.display = isHidden ? 'block' : 'none';
  if (chevron) chevron.className = isHidden ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down';
}

// Otomatis kecilkan kartu saat keyboard muncul (mobile)
if (typeof window !== 'undefined') {
  window.addEventListener('resize', () => {
    const card = document.getElementById('chatQuestionCard');
    const body = document.getElementById('chatQuestionBody');
    if (!card || card.style.display === 'none') return;
    // Jika viewport mengecil drastis (keyboard muncul), sembunyikan body kartu
    if (window.innerHeight < 500 && body && body.style.display !== 'none') {
      body.style.display = 'none';
      const chevron = document.getElementById('chatQuestionChevron');
      if (chevron) chevron.className = 'fa-solid fa-chevron-down';
    }
  });
}

function renderChatHistory(q) {
  const chatMessages = document.getElementById('chatMessages');
  if (!chatMessages) return;
  chatMessages.innerHTML = '';

  // C9: Update kartu soal collapsible
  updateChatQuestionCard(q);

  const history = state.tutorMsgs || [];
  const subjectName = (SUBJECT_CATALOG[state.currentSubject] && SUBJECT_CATALOG[state.currentSubject].name) || 'TKA';
  const activeModelDisplay = cleanModelName(state.selectedTutorModel);

  if (history.length === 0) {
    // Default welcome message (per subject)
    const defaultWelcome = document.createElement('div');
    defaultWelcome.className = 'chat-bubble ai';
    const modelBadge = `<span class="tutor-model-badge" title="Model AI Aktif"><i class="fa-solid fa-microchip"></i> ${_escHtml(activeModelDisplay)}</span>`;
    // Sapaan personal dengan nama user jika sudah login (Aturan Founder)
    let greetingText = '';
    const tkaUser = typeof getTKAUser === 'function' ? getTKAUser() : (window.TKA_USER || null);
    if (tkaUser && tkaUser.loggedIn && tkaUser.name && tkaUser.name !== 'Tamu') {
      greetingText = `Halo ${tkaUser.name}! Ada yang bisa saya bantu?`;
    } else {
      greetingText = (SUBJECT_CATALOG[state.currentSubject] && SUBJECT_CATALOG[state.currentSubject].welcome) || 'Halo! Masih bingung dengan konsep atau langkah pengerjaan pada soal ini? Tanyakan langsung di bawah ya!';
    }

    defaultWelcome.innerHTML = `
      <div class="bubble-sender-bar">
        <div class="sender-left">
          <span class="sender-avatar"><i class="fa-solid fa-robot"></i></span>
          <span class="sender-name">AI Tutor ${subjectName}</span>
        </div>
        ${modelBadge}
      </div>
      <div class="bubble-content">
        <p class="ai-p">${greetingText}</p>
        <div style="margin-top:8px;padding:6px 10px;background:#e8f5e9;border-radius:8px;font-size:12px;color:#2e7d32;display:flex;align-items:center;gap:6px">
          <i class="fa-solid fa-check-circle"></i>
          <span>AI sudah membaca soal nomor ${q ? q.nomor : ''} ini</span>
        </div>
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
    const user = typeof getTKAUser === 'function' ? getTKAUser() : (window.TKA_USER || null);
    const isLogin = !!(user && user.loggedIn);
    const userQuery = isLogin ? `&user_email=${encodeURIComponent(user.email || '')}&is_logged_in=true` : '';
    const didQuery = `&device_id=${encodeURIComponent(getOrCreateDeviceId())}&device_fp=${encodeURIComponent(getDeviceFingerprint())}`;
    const res = await fetch(`/api/tutor/state?subject=${encodeURIComponent(state.currentSubject)}&paket=${state.currentPkg}&nomor=${q.nomor}${userQuery}${didQuery}`, {
      headers: getTutorAuthHeaders()
    });
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
  // B4: Jika ada request yang masih loading, batalkan dulu biar tidak bug
  if (window._tutorAbortController) {
    window._tutorAbortController.abort();
    window._tutorAbortController = null;
    const typingEl = document.getElementById('aiTypingBubble');
    if (typingEl) {
      if (typingEl._timerInt) clearInterval(typingEl._timerInt);
      typingEl.remove();
    }
  }
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
  } else if (modelId === 'openrouter-qwen') {
    iconClass = 'fa-solid fa-network-wired';
    modelName = 'Qwen 7B (OpenRouter)';
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

  // Show typing indicator dengan timer + tombol batal
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
      <i class="fa-solid fa-circle-notch fa-spin"></i> <span id="aiTypingStage">Menghubungi AI...</span>
      <span id="aiTypingTimer" style="margin-left:8px;font-size:12px;opacity:0.7">0s</span>
    </div>
    <button id="aiCancelBtn" style="margin-top:8px;padding:6px 16px;background:#fee;border:1px solid #fcc;border-radius:8px;color:#c00;font-size:13px;cursor:pointer">Batalkan</button>
  `;
  chatMessages.appendChild(typingBubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Timer + stage messages
  const startTime = Date.now();
  const stageEl = document.getElementById('aiTypingStage');
  const timerEl = document.getElementById('aiTypingTimer');
  const stages = ['Menghubungi AI...', 'AI sedang berpikir...', 'Menyusun penjelasan...', 'Hampir selesai...'];
  let stageIdx = 0;
  const timerInt = setInterval(() => {
    const el = document.getElementById('aiTypingBubble');
    if (!el) { clearInterval(timerInt); return; }
    const secs = Math.floor((Date.now() - startTime) / 1000);
    if (timerEl) timerEl.textContent = secs + 's';
    const newIdx = Math.min(Math.floor(secs / 8), stages.length - 1);
    if (newIdx !== stageIdx && stageEl) {
      stageIdx = newIdx;
      stageEl.textContent = stages[stageIdx];
    }
  }, 500);
  // Simpan untuk dibersihkan nanti
  typingBubble._timerInt = timerInt;

  // Tombol batal -> abort request (juga untuk B4)
  const cancelBtn = document.getElementById('aiCancelBtn');
  if (cancelBtn) {
    cancelBtn.onclick = () => {
      if (window._tutorAbortController) {
        window._tutorAbortController.abort();
      }
    };
  }

  const btnSend = document.getElementById('btnSendChat');
  btnSend.disabled = true;

  // AbortController untuk tombol Batal + ganti model saat loading (B3/B4)
  window._tutorAbortController = new AbortController();

  try {
    const user = typeof getTKAUser === 'function' ? getTKAUser() : (window.TKA_USER || null);
    const isLogin = !!(user && user.loggedIn);
    const headers = Object.assign({ 'Content-Type': 'application/json' }, getTutorAuthHeaders());
    const res = await fetch('/api/tutor/chat', {
      signal: window._tutorAbortController.signal,
      method: 'POST',
      headers,
      body: JSON.stringify({
        subject: state.currentSubject,
        paket: state.currentPkg,
        nomor: q.nomor,
        // B5: Kirim konteks soal lengkap biar AI tidak salah konteks
        question_id: `${state.currentSubject}_p${state.currentPkg}_n${q.nomor}`,
        question_text: q.pertanyaan || q.teks || '',
        question_options: (q.pilihan_jawaban || []).map(o => ({ key: o.key, text: o.text || '' })),
        has_image: !!(q.gambar || q.image),
        message: msg,
        model: state.selectedTutorModel || 'gemini-flash',
        request_id: clientRequestId,
        user_email: isLogin ? (user.email || '') : null,
        is_logged_in: isLogin,
        device_id: getOrCreateDeviceId(),
        device_fp: getDeviceFingerprint()
      })
    });

    const data = await res.json();
    const typingEl = document.getElementById('aiTypingBubble');
    if (typingEl) {
      if (typingEl._timerInt) clearInterval(typingEl._timerInt);
      typingEl.remove();
    }
    window._tutorAbortController = null;

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
    if (typingEl) {
      if (typingEl._timerInt) clearInterval(typingEl._timerInt);
      typingEl.remove();
    }
    window._tutorAbortController = null;

    // Jika user yang membatalkan, jangan tampilkan error
    if (err.name === 'AbortError') {
      state.tutorMsgs.push({
        role: 'assistant',
        content: '⏹️ Permintaan dibatalkan.',
        error: true
      });
    } else {
      state.tutorMsgs.push({
        role: 'assistant',
        content: '⚠️ Koneksi ke server AI Tutor terputus. Pesanmu sudah masuk — coba kirim ulang pesanmu.',
        error: true
      });
    }
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

// Toggle Tampilkan / Sembunyikan Soal Serupa
function togglePracticeCard() {
  const card = document.getElementById('practiceCard');
  const icon = document.getElementById('iconTogglePractice');
  const txt = document.getElementById('txtTogglePractice');
  if (!card) return;
  const isCollapsed = card.classList.toggle('is-collapsed');
  if (icon) icon.className = isCollapsed ? 'fa-solid fa-chevron-down' : 'fa-solid fa-chevron-up';
  if (txt) txt.textContent = isCollapsed ? 'Tampilkan' : 'Ciutkan';
  try {
    localStorage.setItem('tka_practice_collapsed', isCollapsed ? '1' : '0');
  } catch (e) {}
}
window.togglePracticeCard = togglePracticeCard;

// Format pembahasan soal serupa agar rumus dan langkah terstruktur rapi
function formatSimilarPembahasan(rawText) {
  if (!rawText) return '';
  let str = String(rawText).trim();

  // Ubah pecahan a/b menjadi \frac{a}{b} agar KaTeX me-render pecahan bertingkat
  str = str.replace(/(\b\d+)\/(\d+\b)/g, (match, n, d) => {
    return `\\frac{${n}}{${d}}`;
  });

  // Pecah berdasarkan titik setelah rumus atau akhir kalimat
  const sentences = str
    .split(/(?<=\.)\s+(?=[A-Z0-9\$\(])/g)
    .map(s => s.trim())
    .filter(Boolean);

  if (sentences.length <= 1) {
    return `<div style="font-size:13.5px;line-height:1.5">${_fmtText(str)}</div>`;
  }

  let html = '<div class="sim-pemb-steps">';
  sentences.forEach((s, idx) => {
    const isConclusion = /opsi\s+[A-E]|jawaban\s*(?:yang\s*benar)?/i.test(s);
    if (isConclusion) {
      html += `
        <div class="sim-pemb-step conclusion">
          <i class="fa-solid fa-flag-checkered" style="margin-right:4px"></i>
          <span class="step-text"><strong>Kesimpulan:</strong> ${_fmtText(s)}</span>
        </div>`;
    } else {
      html += `
        <div class="sim-pemb-step">
          <span class="step-badge">Tahap ${idx + 1}</span>
          <span class="step-text">${_fmtText(s)}</span>
        </div>`;
    }
  });
  html += '</div>';
  return html;
}

function renderSimilarQuestion(q) {
  const sim = q.soal_serupa;
  const promptEl = document.getElementById('simPromptContainer');
  const optsEl = document.getElementById('simOptionsContainer');
  const feedbackEl = document.getElementById('simFeedback');
  const card = document.getElementById('practiceCard');
  const icon = document.getElementById('iconTogglePractice');
  const txt = document.getElementById('txtTogglePractice');

  // Pulihkan status ciutkan/tampilkan dari localStorage
  if (card) {
    const savedCollapsed = localStorage.getItem('tka_practice_collapsed') === '1';
    card.classList.toggle('is-collapsed', savedCollapsed);
    if (icon) icon.className = savedCollapsed ? 'fa-solid fa-chevron-down' : 'fa-solid fa-chevron-up';
    if (txt) txt.textContent = savedCollapsed ? 'Tampilkan' : 'Ciutkan';
  }

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

    const txtSpan = document.createElement('span');
    let optText = opt.text || '';
    // Format pecahan angka murni seperti "2/5", "3/5", "4/5" menjadi pecahan KaTeX
    if (/^\d+\/\d+$/.test(optText.trim())) {
      const parts = optText.trim().split('/');
      optText = `$\\frac{${parts[0]}}{${parts[1]}}$`;
    }
    txtSpan.innerHTML = _fmtText(optText);
    item.appendChild(txtSpan);

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

  const formattedPemb = formatSimilarPembahasan(sim.pembahasan || sim.pembahasan_singkat || '');

  if (isCorrect) {
    fb.className = 'sim-feedback success';
    fb.innerHTML = `
      <div style="font-weight: 700; display:flex; align-items:center; gap:6px;">
        <i class="fa-solid fa-circle-check"></i>
        <span>Jawaban Latihan Benar! (Opsi ${sim.kunci})</span>
      </div>
      <div>${formattedPemb}</div>
    `;
  } else {
    fb.className = 'sim-feedback danger';
    fb.innerHTML = `
      <div style="font-weight: 700; display:flex; align-items:center; gap:6px;">
        <i class="fa-solid fa-circle-xmark"></i>
        <span>Jawaban Latihan Belum Tepat. Kunci: Opsi ${sim.kunci}</span>
      </div>
      <div>${formattedPemb}</div>
    `;
  }
  renderMath(fb);
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
  if (window.TKAHistory) TKAHistory.push('modal-finish');
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
  // FASE 3 (T3.2/T3.3): simpan attempt ke antrean lalu upload sekali.
  try {
    const _att = AttemptRecorder.finish(window._finishByTimer ? 'timer' : 'user');
    window._finishByTimer = false;
    if (_att) { window._lastFinishedAttempt = _att; AttemptQueue.push(_att); syncAttempts(); }
  } catch (e) {}
  if (!state.testFinished) state.testFinished = {};
  state.testFinished[pkgKey()] = true;
  // FASE 3 (T3.5): simpan status finished ke localStorage
  try { localStorage.setItem('tka_finished_' + pkgKey(), 'true'); } catch (e) {}
  closeFinishModal();
  renderReviewHasil();
}

function renderReviewHasil() {
  if (typeof homeClose === 'function') homeClose();
  const pkg = state.pkgData[pkgKey()];
  if (!pkg || !pkg.soal) return;
  // FASE 3 (T3.3): indikator status simpan hasil
  try {
    if (!document.getElementById('attemptSyncBadge')) {
      const _b = document.createElement('div');
      _b.id = 'attemptSyncBadge';
      _b.setAttribute('data-fase3', '1');
      const _rh = document.querySelector('#reviewHasilOverlay .review-header');
      if (_rh) { _rh.after(_b); }
      else { const _ov = document.getElementById('reviewHasilOverlay'); if (_ov) _ov.prepend(_b); }
    }
    updateAttemptBadge();
    // Retry otomatis: janji ke user — buka halaman review = coba kirim lagi.
    try { syncAttempts(); } catch (e2) {}
  } catch (e) {}
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
        return `<img loading="lazy" src="${base}${rel}" alt="Opsi ${k}" style="max-height:48px; max-width:140px; vertical-align:middle; border-radius:4px; border:1px solid var(--border); background:#fff; padding:2px; display:inline-block;" />`;
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
          return `<strong>${st.key}:</strong> <span style="color:#94a3b8;">&mdash;</span>`;
        }
        const isRight = picked === kunciMap[st.key];
        const badge = isRight 
          ? `<span style="color:#15803d;font-weight:700;">✅ ${picked}</span>`
          : `<span style="color:#dc2626;font-weight:700;">❌ ${picked}</span>`;
        return `<strong>${st.key}:</strong> ${badge}`;
      });

      const partsKunci = stmts.map(st => {
        return `<strong>${st.key}:</strong> <span style="font-weight:700;color:#004a2a;">${kunciMap[st.key] || '&mdash;'}</span>`;
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

  // Render bertahap untuk HP kentang: 10 soal per batch biar tidak lag
  const tbody = document.getElementById('reviewTableBody');
  const isLowEnd = document.documentElement.classList.contains('mode-ringan');
  const batchSize = isLowEnd ? 10 : rows.length;

  if (isLowEnd && rows.length > batchSize) {
    tbody.innerHTML = rows.slice(0, batchSize).join('');
    let rendered = batchSize;
    const loadMore = () => {
      const next = rows.slice(rendered, rendered + batchSize).join('');
      tbody.insertAdjacentHTML('beforeend', next);
      rendered += batchSize;
      renderMath(tbody);
      if (rendered >= rows.length) {
        window.removeEventListener('scroll', onScroll);
      }
    };
    const onScroll = () => {
      const nearBottom = window.innerHeight + window.scrollY >= document.body.scrollHeight - 500;
      if (nearBottom) loadMore();
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    // Tombol "Muat lebih banyak" sebagai fallback
    const moreBtn = document.createElement('button');
    moreBtn.textContent = `Muat ${Math.min(batchSize, rows.length - rendered)} soal lagi`;
    moreBtn.className = 'btn-load-more';
    moreBtn.style.cssText = 'display:block;margin:16px auto;padding:10px 24px;background:#1b633e;color:#fff;border:none;border-radius:12px;font-weight:600';
    moreBtn.onclick = () => {
      loadMore();
      if (rendered >= rows.length) moreBtn.remove();
      else moreBtn.textContent = `Muat ${Math.min(batchSize, rows.length - rendered)} soal lagi`;
    };
    tbody.parentElement.appendChild(moreBtn);
  } else {
    tbody.innerHTML = rows.join('');
  }

  document.getElementById('reviewHasilOverlay').classList.add('open');
  if (window.TKAHistory) TKAHistory.push('review-overlay');

  // Trigger KaTeX untuk render rumus matematika di tabel hasil
  renderMath(document.getElementById('reviewTableBody'));

  // FASE 5 (T5.1): tampilkan Autopsi setelah review dirender
  try { renderAutopsiSection(); } catch (e) { console.warn('Autopsi:', e); }
}

// FASE 5 (T5.1): Ambil analisis Autopsi dari server dan tampilkan.
// Kebocoran #1 terbuka lengkap; #2-3 terkunci (blur) untuk non-pass.
async function renderAutopsiSection() {
  // Cari container atau buat baru (diletakkan DI BAWAH tabel agar nomor & kunci tidak tertutup)
  let cont = document.getElementById('autopsiSection');
  if (!cont) {
    cont = document.createElement('div');
    cont.id = 'autopsiSection';
    const overlay = document.getElementById('reviewHasilOverlay');
    const tableWrap = overlay.querySelector('.review-table-wrap') || overlay.querySelector('table');
    if (tableWrap) {
      tableWrap.after(cont);
    } else {
      overlay.appendChild(cont);
    }
  }
  cont.innerHTML = '';
  cont.style.display = 'none';

  try {
    // Ambil attempt terakhir dari antrean atau yang baru selesai
    const q = (typeof AttemptQueue !== 'undefined') ? AttemptQueue.all() : [];
    // Cari attempt yang baru saja selesai (atau pakai data dari state)
    let payload = null;
    if (window._lastFinishedAttempt) {
      payload = window._lastFinishedAttempt;
    } else if (q.length > 0) {
      payload = q[q.length - 1];
    }
    if (!payload || !payload.items || !payload.items.length) {
      cont.innerHTML = '';
      cont.style.display = 'none';
      return;
    }
    // Dapatkan token
    let hdr = {};
    if (typeof _attemptAuthHeader === 'function') {
      try { hdr = await _attemptAuthHeader(); } catch (e) {}
    }
    const isFounder = (localStorage.getItem('tka_founder_mode') === '1');
    const isGuest = !hdr.Authorization;

    cont.style.display = 'block';
    cont.innerHTML = '<div style="text-align:center;padding:12px;color:#6b7280;font-size:12px"><i class="fa-solid fa-spinner fa-spin"></i> Memuat analisis Autopsi...</div>';
    
    const reqBody = {
      items: payload.items,
      n_questions: payload.n_questions,
      duration_limit_s: payload.duration_limit_s,
      ended_by: payload.ended_by,
      mapel: payload.subject || payload.mapel,
      is_guest: isGuest,
      founder_mode: isFounder
    };

    const res = await fetch('/api/autopsy/analyze', {
      method: 'POST',
      headers: Object.assign({'Content-Type': 'application/json'}, hdr),
      body: JSON.stringify(reqBody)
    });
    if (!res.ok) {
      cont.innerHTML = '';
      return;
    }
    const d = await res.json();
    if (d.status !== 'success') {
      cont.innerHTML = '';
      return;
    }
    // Simpan untuk "Misi hari ini" (T5.2)
    try { localStorage.setItem('tka_last_autopsy', JSON.stringify(d)); } catch (e) {}
    // Render Autopsi
    const labelNama = {
      'terburu': 'Terburu-buru',
      'overthinking': 'Overthinking (plin-plan)',
      'macet': 'Macet (terlalu lama)',
      'yakin_salah': 'Yakin tapi salah',
      'ragu_salah': 'Ragu-ragu dan salah',
      'ragu_benar': 'Ragu tapi benar (rapuh)',
      'waktu_habis': 'Kehabisan waktu',
      'kosong': 'Dikosongkan'
    };
    let h = '<div class="autopsy-widget" style="margin:16px 0;padding:14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px">';
    h += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;flex-wrap:wrap;gap:6px">'
      + '<div style="display:flex;align-items:center;gap:8px;">'
      + '<h3 style="font-size:15px;font-weight:800;margin:0;color:#0f172a">🔍 Autopsi Tryout</h3>'
      + (d.is_founder ? '<span style="font-size:10.5px;background:#fef3c7;color:#92400e;border:1px solid #fde68a;padding:2px 8px;border-radius:6px;font-weight:700">👑 Founder Mode</span>' : '')
      + '</div>'
      + '<span style="font-size:11px;background:#e2e8f0;color:#475569;padding:3px 8px;border-radius:6px;font-weight:700">Pola Pengerjaan Siswa</span>'
      + '</div>';
    h += '<p style="font-size:12px;color:#64748b;margin:0 0 10px;line-height:1.4">Pola perilaku ini yang membuat nilaimu bocor, bukan sekadar angka akhir.</p>';
    if (d.data_tipis) {
      h += '<div style="background:#fef3c7;border:1px solid #fde68a;border-radius:8px;padding:8px 10px;font-size:12px;margin-bottom:8px">ℹ️ Jumlah soal yang dikerjakan masih sedikit, jadi anggap ini gambaran awal.</div>';
    }
    // Container scroll internal agar tidak overflow di layar HP
    h += '<div class="autopsy-scroll-wrap" style="max-height:300px;overflow-y:auto;padding-right:4px;-webkit-overflow-scrolling:touch">';
    // Kebocoran #1 (terbuka)
    const k1 = d.kebocoran_1;
    if (k1) {
      const cthId = (k1.contoh && k1.contoh[0]) ? String(k1.contoh[0]) : '';
      h += '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 14px;margin-bottom:10px">';
      h += '<div style="font-size:11px;font-weight:800;color:#15803d;text-transform:uppercase;margin-bottom:4px;letter-spacing:0.04em">Kebocoran #1 (Terbuka Lengkap)</div>';
      h += '<div style="font-size:14.5px;font-weight:800;margin-bottom:4px;color:#14532d">' + (labelNama[k1.label] || k1.label) + '</div>';
      h += '<div style="font-size:12.5px;color:#374151;margin-bottom:8px;line-height:1.45">' + (k1.bukti || '') + '</div>';
      if (k1.contoh && k1.contoh.length) {
        h += '<div style="font-size:11.5px;color:#6b7280;margin-bottom:10px">Contoh soal: <strong>' + k1.contoh.slice(0,3).join(', ') + '</strong></div>';
      }
      h += `<button type="button" onclick="bukaKartuStrategi('${k1.label}', '${cthId}')" style="background:#004a2a;color:#fff;border:0;border-radius:8px;padding:7px 14px;font-size:12px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:6px;">📚 Pelajari Strategi</button>`;
      h += '</div>';
    }

    // Jika Mode Founder: Tampilkan seluruh kebocoran yang terbuka
    if (d.is_founder && Array.isArray(d.kebocoran_all) && d.kebocoran_all.length > 1) {
      d.kebocoran_all.slice(1).forEach((k, idx) => {
        const cthId = (k.contoh && k.contoh[0]) ? String(k.contoh[0]) : '';
        h += '<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:12px 14px;margin-bottom:10px">';
        h += '<div style="font-size:11px;font-weight:800;color:#1d4ed8;text-transform:uppercase;margin-bottom:4px">Kebocoran #' + (idx+2) + ' (Founder Mode)</div>';
        h += '<div style="font-size:14px;font-weight:800;margin-bottom:4px;color:#1e40af">' + (labelNama[k.label] || k.label) + '</div>';
        h += '<div style="font-size:12px;color:#374151;margin-bottom:6px">' + (k.bukti || (k.soal_hilang + ' soal terpengaruh')) + '</div>';
        h += `<button type="button" onclick="bukaKartuStrategi('${k.label}', '${cthId}')" style="background:#1d4ed8;color:#fff;border:0;border-radius:6px;padding:5px 12px;font-size:11px;font-weight:700;cursor:pointer">📚 Pelajari</button>`;
        h += '</div>';
      });
    } else {
      // Kebocoran #2-3 (terkunci dengan blur ringan)
      (d.kebocoran_locked || []).forEach((k, idx) => {
        h += '<div style="background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:12px 14px;margin-bottom:10px;position:relative;overflow:hidden">';
        h += '<div style="filter:blur(4px);user-select:none;pointer-events:none">';
        h += '<div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:3px">Kebocoran #' + (idx+2) + '</div>';
        h += '<div style="font-size:13px;font-weight:700;margin-bottom:3px">' + (labelNama[k.label] || k.label) + '</div>';
        h += '<div style="font-size:12px;color:#374151">' + k.soal_hilang + ' soal terpengaruh</div>';
        h += '</div>';
        h += '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.78);">';
        h += '<span style="font-size:12px;font-weight:700;color:#004a2a;background:#e8f5e9;padding:6px 14px;border-radius:20px;border:1px solid #c8e6c9;">🔒 Buka dengan Paket Sprint</span>';
        h += '</div></div>';
      });
    }

    h += '</div>'; // Tutup autopsy-scroll-wrap
    if (d.rapuh_count > 0) {
      h += '<div style="font-size:11.5px;color:#64748b;text-align:center;margin-top:8px">💡 <strong>' + d.rapuh_count + ' soal</strong> kamu jawab benar tapi ditandai ragu-ragu (perlu pemantapan).</div>';
    }

    // Ajakan jika akun tamu (Funnel pendaftaran gratis)
    if (d.is_guest) {
      h += '<div style="margin-top:12px;padding:10px 14px;background:#fff7ed;border:1px solid #ffedd5;border-radius:10px;display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;">'
        + '<div style="font-size:11.5px;color:#9a3412;line-height:1.4"><strong>Mode Tamu:</strong> Masuk dengan Google untuk menyimpan hasil ini dan mengunci progres belajar harianmu!</div>'
        + '<button type="button" onclick="loginWithGoogle()" style="background:#c2410c;color:#fff;border:none;border-radius:6px;padding:6px 12px;font-size:11.5px;font-weight:700;cursor:pointer;white-space:nowrap;">Masuk Sekarang</button>'
        + '</div>';
    }

    h += '</div>';
    cont.innerHTML = h;
  } catch (e) {
    cont.innerHTML = '';
  }
}

// Buka Modal Kartu Strategi Belajar
function bukaKartuStrategi(label, contohSoalRef) {
  const modal = document.getElementById('modalKartuStrategi');
  const titleEl = document.getElementById('kartuStrategiTitle');
  const badgeEl = document.getElementById('kartuStrategiBadge');
  const iconEl = document.getElementById('kartuStrategiIcon');
  const iconWrap = document.getElementById('kartuStrategiIconWrap');
  const contentEl = document.getElementById('kartuStrategiContent');
  const btnLatih = document.getElementById('btnAksiLatihSoal');
  if (!modal || !contentEl) return;

  const STRATEGI = {
    'terburu': {
      title: 'Strategi Anti-Ceroboh & Cek Ulang',
      badge: 'PANDUAN ANTI-CEROBOH',
      icon: 'fa-bolt',
      theme: '#b45309',
      bg: '#fef3c7',
      points: [
        '<strong>1. Tunjuk yang ditanyakan:</strong> Sebelum klik jawaban, baca sekali lagi kalimat terakhir: apakah mencari <em>nilai x</em>, <em>pernyataan yang salah</em>, atau <em>simpulan utama</em>?',
        '<strong>2. Cek tanda (+/−) dan satuan:</strong> Pada langkah akhir pengerjaan, luangkan 5 detik untuk memeriksa kembali simbol minus/positif.',
        '<strong>3. Jangan ganti jawaban karena ragu sesaat:</strong> Jawaban pertama yang sudah dihitung matang biasanya 80% lebih akurat daripada hasil tebakan mendadak.',
        '<strong>4. Beri tanda Ragu-ragu:</strong> Jika masih bimbang, tandai Ragu-ragu lalu lanjutkan dulu ke soal lain yang lebih mudah.',
        '<strong>5. Evaluasi sisa waktu:</strong> Gunakan 5 menit terakhir khusus meninjau nomor bertanda ragu-ragu.'
      ]
    },
    'overthinking': {
      title: 'Strategi Keyakinan & Konsistensi Logika',
      badge: 'KONTROL OVERTHINKING',
      icon: 'fa-brain',
      theme: '#7c3aed',
      bg: '#ede9fe',
      points: [
        '<strong>1. Percayai analisis pertamamu:</strong> Data rekaman menunjukkan pilihan awalmu sebenarnya sudah benar sebelum kamu ganti.',
        '<strong>2. Aturan pergantian jawaban:</strong> Hanya ganti pilihan jika kamu menemukan bukti konkret salah membaca teks atau salah rumus matematika.',
        '<strong>3. Abaikan distractor rumit:</strong> Opsi pengecoh sering sengaja memakai kata-kata ilmiah panjang untuk menggoyahkan keyakinanmu.',
        '<strong>4. Selesaikan sekali tuntas:</strong> Jika logika langkahmu sudah terbukti di kertas buram, kunci dan pindah ke nomor berikutnya.'
      ]
    },
    'macet': {
      title: 'Strategi Manajemen Waktu (Anti-Macet)',
      badge: 'MANAJEMEN WAKTU',
      icon: 'fa-stopwatch',
      theme: '#b91c1c',
      bg: '#fee2e2',
      points: [
        '<strong>1. Aturan maksimal 2 menit:</strong> Jika dalam 2 menit kamu belum menemukan arah rumus/ide pokok, segera beri tanda Ragu-ragu dan tinggalkan.',
        '<strong>2. Semua soal punya bobot sama:</strong> Menghabiskan 8 menit untuk 1 soal sulit akan mengorbankan 3 soal mudah di nomor akhir.',
        '<strong>3. Checkpoint waktu ujian:</strong> Pastikan pada menit ke-30 kamu sudah menyelesaikan minimal sepertiga total soal.',
        '<strong>4. Kerjakan soal yang kamu kuasai lebih dulu:</strong> Mengamankan poin mudah membangun rasa percaya diri di ruang ujian.'
      ]
    },
    'waktu_habis': {
      title: 'Strategi Pencegahan Waktu Habis',
      badge: 'SPEED & TIMING',
      icon: 'fa-hourglass-end',
      theme: '#c2410c',
      bg: '#ffedd5',
      points: [
        '<strong>1. Ketahui jatah per soal:</strong> Rata-rata kamu punya waktu 2.5 hingga 3 menit per nomor.',
        '<strong>2. Pantau sisa waktu:</strong> Tengok indikator timer setiap selesai 5 nomor soal.',
        '<strong>3. Menit terakhir:</strong> Di sisa waktu 3 menit, pastikan tidak ada nomor yang tertinggal kosong tanpa jawaban.'
      ]
    },
    'yakin_salah': {
      title: 'Strategi Fondasi Teori & Konsep Kunci',
      badge: 'PENGUATAN TEORI',
      icon: 'fa-compass',
      theme: '#047857',
      bg: '#d1fae5',
      points: [
        '<strong>1. Buka kembali Pilar 1 & Pilar 3:</strong> Pelajari definisi dasar dan mengapa konsep rumus tersebut diterapkan pada soal ini.',
        '<strong>2. Waspadai jebakan opsi:</strong> Jawaban yang terasa familiar sering kali merupakan hasil jebakan salah tafsir.',
        '<strong>3. Latih Soal Serupa:</strong> Selesaikan 2-3 latihan soal pemantapan dengan tipe yang sama.'
      ]
    }
  };

  const st = STRATEGI[label] || STRATEGI['terburu'];
  titleEl.innerText = st.title;
  badgeEl.innerText = st.badge;
  badgeEl.style.color = st.theme;
  iconEl.className = 'fa-solid ' + st.icon;
  iconWrap.style.background = st.bg;
  iconWrap.style.color = st.theme;

  contentEl.innerHTML = '<ul style="margin:0;padding-left:0;list-style:none;display:flex;flex-direction:column;gap:8px;">'
    + st.points.map(p => `<li style="padding-left:14px;position:relative;line-height:1.5;">${p}</li>`).join('')
    + '</ul>';

  if (contohSoalRef && btnLatih) {
    btnLatih.style.display = 'inline-flex';
    btnLatih.onclick = () => pelajariSoalBocor(contohSoalRef);
  } else if (btnLatih) {
    btnLatih.style.display = 'none';
  }

  modal.classList.add('open');
  if (window.TKAHistory) TKAHistory.push('modal-kartu-strategi');
}

function tutupKartuStrategi() {
  const modal = document.getElementById('modalKartuStrategi');
  if (modal) modal.classList.remove('open');
}

// Buka pembahasan dari soal yang teridentifikasi bocor
function pelajariSoalBocor(contohSoalRef) {
  tutupKartuStrategi();
  closeReviewHasil();
  const pkg = state.pkgData[pkgKey()];
  if (!pkg || !pkg.soal) return;

  let targetIdx = 0;
  // Ekstrak nomor dari format id atau string
  const m = String(contohSoalRef).match(/\d+$/);
  const targetNo = m ? parseInt(m[0], 10) : null;

  if (targetNo) {
    const idx = pkg.soal.findIndex(s => s.nomor === targetNo);
    if (idx !== -1) targetIdx = idx;
  }

  state.currentIndex = targetIdx;
  state.explanationVisible = true;
  state.keepWorkTab = true;
  renderQuestion();
  switchWorkTab('pembahasan', 'materi', { scroll: true });
  window.scrollTo({ top: 0, behavior: 'smooth' });
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
  if (typeof homeClose === 'function') homeClose();
  if (typeof renderQuestion === 'function') renderQuestion();
}

// Kembali ke beranda dari modal konfirmasi selesai tes
function selesaiDanKeBeranda() {
  const key = pkgKey();
  if (!state.testFinished) state.testFinished = {};
  state.testFinished[key] = true;
  closeFinishModal();
  if (typeof homeOpen === 'function') {
    homeOpen();
    if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
  }
}

// Kembali ke beranda dari overlay reviu hasil
function reviewKeBeranda() {
  closeReviewHasil();
  if (typeof homeOpen === 'function') {
    homeOpen();
    if (typeof homeShowPanel === 'function') homeShowPanel('beranda');
  }
}

// Ulangi simulasi: reset jawaban & status ragu paket aktif
function resetSimulasi() {
  const key = pkgKey();
  if (state.testFinished) state.testFinished[key] = false;
  // FASE 3 (T3.2): reset perekam saat ulangi
  try { AttemptRecorder.reset(); } catch (e) {}
  // FASE 3 (T3.5): bersihkan data tersimpan paket ini di localStorage
  try {
    localStorage.removeItem('tka_answers_' + key);
    localStorage.removeItem('tka_ragu_' + key);
    localStorage.removeItem('tka_finished_' + key);
    localStorage.removeItem('tka_timer_remaining_' + key);
    localStorage.removeItem('tka_checked_' + key);
    if (window._answerChecked) {
      Object.keys(window._answerChecked).forEach(k => {
        if (k.startsWith(key + ':')) delete window._answerChecked[k];
      });
    }
  } catch (e) {}
  state.userAnswers[key] = {};
  state.raguStatus[key] = {};
  state.simAnswers[key] = {};
  state.currentIndex = 0;
  state.explanationVisible = false;
  closeReviewHasil();
  // FASE 3: ulangi = rekaman attempt baru
  try {
    const _pkg = state.pkgData[pkgKey()];
    const _n = (_pkg && _pkg.soal) ? _pkg.soal.length : 0;
    AttemptRecorder.start(state.currentSubject, state.currentPkg, _n, getTimerTotalSeconds());
  } catch (e) {}
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
  // FASE 3 (T3.2): rekam flag ragu-ragu
  try { AttemptRecorder.onRagu(q.nomor, !current); } catch (e) {}
  // FASE 3 (T3.5): simpan status ragu ke localStorage agar tahan refresh
  try { localStorage.setItem('tka_ragu_' + pkgKey(), JSON.stringify(state.raguStatus[pkgKey()])); } catch (e) {}
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
  if (window.TKAHistory) TKAHistory.push('daftar-soal');
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

// Trigger KaTeX math formula rendering (Targeted 60fps untuk HP Kentang & Mobile)
function renderMath(targetEl) {
  if (typeof window.renderMathInElement !== 'function') return;
  try {
    const targets = targetEl
      ? [targetEl]
      : [
          document.getElementById('cbtExamGrid'),
          document.getElementById('workPanePembahasan'),
          document.getElementById('practiceCard')
        ].filter(Boolean);

    targets.forEach(container => {
      // Fast bail-out: Jika tidak ada token matematika sama sekali, lewati parsing KaTeX untuk hemat CPU
      const text = container.textContent || '';
      if (!text.includes('$') && !text.includes('\\(') && !text.includes('\\[') && !container.innerHTML.includes('data-latex')) {
        return;
      }

      renderMathInElement(container, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true }
        ],
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option', 'iframe', 'svg'],
        throwOnError: false
      });
    });
  } catch (e) {
    console.warn('KaTeX rendering notice:', e);
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
  if (window.TKAHistory) TKAHistory.push('lightbox');
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

function closeTutorSheet(force) {
  const sheet = document.getElementById('cbtSidebarCol');
  const backdrop = document.getElementById('tutorBackdrop');
  if (sheet) {
    sheet.classList.remove('tutor-open');
    sheet.style.transform = '';
    // B6: Force-close untuk pastikan sheet benar-benar tertutup
    if (force) {
      sheet.style.display = 'none';
      setTimeout(() => { sheet.style.display = ''; }, 50);
    }
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
// T2.7: timer mengikuti format resmi TKA 2026 (brief §3.1): jatah per soal
// matematika 3,0 mnt · B.Indonesia/B.Inggris 2,5 mnt · mapel pilihan 2,4 mnt.
// Timer per paket = jumlah soal x jatah (MTK P2: 25x3 = 75 mnt = pas resmi).
const TIMER_TOTAL_SECONDS = 105 * 60; // fallback bila data paket belum dimuat
const _JATAH_MENIT_PER_SOAL = { matematika: 3.0, bahasa_indonesia: 2.5, bahasa_inggris: 2.5 };
function _jatahMenit(subject) { return _JATAH_MENIT_PER_SOAL[subject] || 2.4; }
function getTimerTotalSeconds() {
  try {
    const pkg = state.pkgData[pkgKey()];
    const n = (pkg && pkg.soal) ? pkg.soal.length : 0;
    if (n > 0) return Math.round(n * _jatahMenit(state.currentSubject) * 60);
  } catch (e) {}
  return TIMER_TOTAL_SECONDS;
}

// ============================================================================
// FASE 3 (T3.2/T3.3): Perekam attempt untuk Autopsi
// Per soal: waktu aktif, jawaban pertama vs akhir, jumlah ganti, flag ragu,
// kunjungan ulang. Buffer di localStorage; upload sekali saat "Selesai Tes"
// (atau saat online kembali). Tanpa login -> tidak direkam (T3.4).
// ============================================================================
const AttemptRecorder = {
  active: null, _lastQ: null, _lastT: 0,
  reset() {
    this.active = null; this._lastQ = null; this._lastT = 0;
  },
  start(subject, paket, n, duration_s) {
    this.active = { subject, paket, n, duration_s, started_at: Date.now(), items: {} };
    this._lastQ = null; this._lastT = Date.now();
  },
  _ensure(nomor) {
    const a = this.active; if (!a) return null;
    if (!a.items[nomor]) a.items[nomor] = {
      soal_id: a.subject + ':' + a.paket + ':' + nomor,
      position: nomor, topic_id: null,
      first_answer: null, final_answer: null,
      active_ms: 0, first_answer_ms: null,
      change_count: 0, flagged_ragu: false, visit_count: 0, _firstVisitT: 0,
      jejak: []
    };
    return a.items[nomor];
  },
  onVisit(nomor, topic_id) {
    const a = this.active; if (!a) return;
    const now = Date.now();
    if (this._lastQ != null && a.items[this._lastQ])
      a.items[this._lastQ].active_ms += now - this._lastT;
    const it = this._ensure(nomor);
    if (!it._firstVisitT) it._firstVisitT = now;
    if (topic_id) it.topic_id = topic_id;
    it.visit_count += 1;
    this._lastQ = nomor; this._lastT = now;
  },
  onAnswer(nomor, answer) {
    const it = this._ensure(nomor); if (!it) return;
    const now = Date.now();
    const curActiveMs = (it.active_ms || 0) + (this._lastQ === nomor ? (now - this._lastT) : 0);
    const t_detik = Math.max(1, Math.round(curActiveMs / 1000));
    const ans = Array.isArray(answer) ? answer.join(',') : String(answer);
    if (!it.jejak) it.jejak = [];
    if (it.first_answer == null) {
      it.first_answer = ans;
      it.first_answer_ms = now - (it._firstVisitT || now);
      if (it.jejak.length < 5) {
        it.jejak.push({ t_detik: t_detik, aksi: 'pilih', opsi: ans });
      }
    } else if (it.final_answer !== ans) {
      it.change_count += 1;
      if (it.jejak.length < 5) {
        it.jejak.push({ t_detik: t_detik, aksi: 'ganti', opsi: ans });
      }
    }
    it.final_answer = ans;
  },
  onRagu(nomor, flagged) {
    const it = this._ensure(nomor); if (!it) return;
    const now = Date.now();
    const curActiveMs = (it.active_ms || 0) + (this._lastQ === nomor ? (now - this._lastT) : 0);
    const t_detik = Math.max(1, Math.round(curActiveMs / 1000));
    it.flagged_ragu = !!flagged;
    if (!it.jejak) it.jejak = [];
    if (it.jejak.length < 5) {
      it.jejak.push({ t_detik: t_detik, aksi: 'ragu', opsi: flagged ? 'ragu' : 'batal_ragu' });
    }
  },
  finish(ended_by) {
    const a = this.active; if (!a) return null;
    const now = Date.now();
    if (this._lastQ != null && a.items[this._lastQ])
      a.items[this._lastQ].active_ms += now - this._lastT;
    // Isi item untuk SEMUA soal (1..n); yang tak dikunjungi dapat nilai nol.
    // Ini mencegah "Items tidak valid" saat user selesai tanpa buka semua soal.
    const items = [];
    for (let nomor = 1; nomor <= a.n; nomor++) {
      const it = a.items[nomor] || {
        soal_id: a.subject + ':' + a.paket + ':' + nomor,
        position: nomor, topic_id: null,
        first_answer: null, final_answer: null,
        active_ms: 0, first_answer_ms: null,
        change_count: 0, flagged_ragu: false, visit_count: 0,
        jejak: []
      };
      const activeMs = it.active_ms || 0;
      const c = Object.assign({}, it, {
        waktu_detik: Math.round(activeMs / 1000),
        ganti_jawaban: it.change_count || 0,
        ragu: !!it.flagged_ragu,
        jejak: (it.jejak || []).slice(0, 5)
      });
      delete c._firstVisitT;
      items.push(c);
    }
    const payload = {
      client_id: 'att_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
      subject: a.subject, paket: a.paket,
      n_questions: a.n, duration_limit_s: a.duration_s,
      ended_by: ended_by === 'timer' ? 'timer' : 'user',
      started_at: new Date(a.started_at).toISOString(),
      finished_at: new Date(now).toISOString(),
      items
    };
    this.active = null; this._lastQ = null;
    return payload;
  }
};

const AttemptQueue = {
  KEY: 'tka_attempt_queue',
  all() { try { return JSON.parse(localStorage.getItem(this.KEY) || '[]'); } catch (e) { return []; } },
  _save(q) { try { localStorage.setItem(this.KEY, JSON.stringify(q)); } catch (e) {} try { updateAttemptBadge(); } catch (e2) {} },
  push(att) { if (!att) return; const q = this.all(); q.push(att); this._save(q); },
  remove(client_id) { this._save(this.all().filter(x => x.client_id !== client_id)); },
  clear() { this._save([]); },
  count() { return this.all().length; }
};

async function _attemptAuthHeader() {
  // Ambil token segar via getSession() (otomatis refresh jika kedaluwarsa).
  try {
    if (typeof getFreshToken === 'function') {
      const t = await getFreshToken();
      if (t) return { 'Authorization': 'Bearer ' + t };
    }
  } catch (e) {}
  // Fallback: baca mentah dari localStorage
  try {
    const s = localStorage.getItem('tka_supabase_auth_token');
    if (s) { const sess = JSON.parse(s); if (sess && sess.access_token) return { 'Authorization': 'Bearer ' + sess.access_token }; }
  } catch (e) {}
  return {};
}

let _syncAttemptsInFlight = false;
async function syncAttempts() {
  if (_syncAttemptsInFlight) return; // cegah kirim ganda bersamaan
  _syncAttemptsInFlight = true;
  try {
  const q = AttemptQueue.all();
  if (!q.length) { try { updateAttemptBadge(); } catch (e) {} return; }
  for (const att of q) {
    try {
      const sendOnce = async (hdr) => await fetch('/api/attempts', {
        method: 'POST',
        headers: Object.assign({ 'Content-Type': 'application/json' }, hdr),
        body: JSON.stringify(att)
      });
      let res = await sendOnce(await _attemptAuthHeader());
      // Jika 401, coba refresh token sekali lalu kirim ulang.
      if (res.status === 401 && typeof refreshTokenNow === 'function') {
        try {
          const t = await refreshTokenNow();
          if (t) res = await sendOnce({ 'Authorization': 'Bearer ' + t });
        } catch (e) {}
      }
      if (res.ok) { AttemptQueue.remove(att.client_id); }
      else if (res.status === 400) {
        // 400 = data rusak permanen -> karantina (hapus dari antrean) agar tidak macet.
        try { const _ej = await res.json(); if (_ej && _ej.message) syncAttempts._lastErr = String(_ej.message).slice(0, 90); }
        catch (e) { syncAttempts._lastErr = 'HTTP 400'; }
        AttemptQueue.remove(att.client_id);
        continue;
      }
      else {
        try { const _ej = await res.json(); if (_ej && _ej.message) syncAttempts._lastErr = String(_ej.message).slice(0, 90); }
        catch (e) { syncAttempts._lastErr = 'HTTP ' + res.status; }
        break;
      }
    } catch (e) { break; }
  }
  try { updateAttemptBadge(); } catch (e) {}
  } finally { _syncAttemptsInFlight = false; }
}

function updateAttemptBadge() {
  try {
    const el = document.getElementById('attemptSyncBadge');
    if (!el) return;
    const n = AttemptQueue.count();
    const logged = _isLoggedIn();
    if (!logged && n > 0) {
      el.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:11.5px;font-weight:600;margin:6px 0 10px;padding:7px 12px;border-radius:10px;border:1px solid #fed7aa;background:#fff7ed;color:#c2410c;';
      el.innerHTML = '<span style="display:flex;align-items:center;gap:6px;">&#9888; <strong>Mode Tamu</strong> (' + n + ' hasil di HP)</span>' +
        '<button type="button" onclick="loginWithGoogle()" style="background:#004a2a;color:#fff;border:none;padding:5px 12px;border-radius:6px;font-size:11px;font-weight:700;cursor:pointer;white-space:nowrap;">Klaim ke Google</button>';
      return;
    }
    const ok = n === 0;
    el.style.cssText = 'text-align:center;font-size:12px;font-weight:700;margin:6px 0 8px;padding:6px 12px;border-radius:8px;border:1px solid;' +
      (ok ? 'background:#f0fdf4;color:#15803d;border-color:#bbf7d0;'
          : 'background:#fffbeb;color:#b45309;border-color:#fde68a;');
    el.innerHTML = ok ? '&#10003; Hasil tersimpan di akunmu'
      : '&#9203; ' + n + ' hasil menunggu upload' +
        (syncAttempts._lastErr ? ' <small style="font-weight:400">(' + syncAttempts._lastErr + ')</small>'
                              : ' <small style="font-weight:400">(akan dikirim otomatis)</small>');
  } catch (e) {}
}

window.addEventListener('online', () => { try { syncAttempts(); } catch (e) {} });
document.addEventListener('DOMContentLoaded', () => { try { setTimeout(syncAttempts, 3000); } catch (e) {} });

// FASE 3 (T3.4): status login
function _isLoggedIn() {
  try {
    const u = JSON.parse(localStorage.getItem('tka_user') || 'null');
    if (u && u.loggedIn) return true;
    const s = JSON.parse(localStorage.getItem('tka_supabase_auth_token') || 'null');
    return !!(s && s.access_token);
  } catch (e) { return false; }
}
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
  if (isNaN(rem)) rem = getTimerTotalSeconds();
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
    // FASE 3: waktu habis -> arahkan selesai (ended_by=timer untuk Autopsi)
    try {
      if (!((state.testFinished || {})[pkgKey()])) {
        window._finishByTimer = true;
        if (typeof openFinishModal === 'function') openFinishModal();
        else if (typeof selesaiTes === 'function') selesaiTes();
      }
    } catch (e) {}
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

// ==========================================================================
// MOBILE NATIVE BACK BUTTON & NAVIGATION HISTORY MANAGER
// Standar Industri Web App Mobile (Android Back Button & iOS Swipe Back):
// - Menutup modal/lightbox/sheet satu per satu saat tombol Back HP ditekan.
// - Menghindari reload atau keluar web secara tidak sengaja saat ujian berlangsung.
// - Jika di tab Pembahasan, tombol Back HP membawa kembali ke Lembar Soal.
// ==========================================================================
const TKAHistory = {
  _isHandlingPop: false,

  push(type, data) {
    if (this._isHandlingPop) return;
    try {
      const stateObj = { tka_type: type, tka_data: data || null, tka_ts: Date.now() };
      window.history.pushState(stateObj, '');
    } catch (e) {}
  },

  init() {
    try {
      if (!window.history.state || !window.history.state.tka_init) {
        window.history.replaceState({ tka_init: true }, '');
      }
    } catch (e) {}

    window.addEventListener('popstate', (e) => {
      this._isHandlingPop = true;
      try {
        const handled = this.handleBack();
        if (handled) {
          // Jaga guard state agar tombol back berikutnya tetap bisa ditangkap
          try {
            window.history.pushState({ tka_active: true }, '');
          } catch (err) {}
        }
      } finally {
        setTimeout(() => {
          this._isHandlingPop = false;
        }, 100);
      }
    });
  },

  handleBack() {
    // 0. Modal Lapor Bug
    const bugModal = document.getElementById('modalLaporBug');
    if (bugModal && bugModal.classList.contains('open')) {
      if (typeof closeBugReportModal === 'function') closeBugReportModal();
      return true;
    }

    // 1. Lightbox Gambar Zoom
    const lbModal = document.getElementById('imageLightboxModal');
    if (lbModal && lbModal.classList.contains('open')) {
      if (typeof closeImageLightbox === 'function') closeImageLightbox();
      return true;
    }

    // 2. Modal Grid Nomor Soal
    const gridModal = document.getElementById('modalDaftarSoal');
    if (gridModal && gridModal.classList.contains('open')) {
      if (typeof closeDaftarModal === 'function') closeDaftarModal();
      return true;
    }

    // 3. Modal Konfirmasi Selesai Tes
    const finModal = document.getElementById('modalKonfirmasiSelesai');
    if (finModal && finModal.classList.contains('open')) {
      if (typeof closeFinishModal === 'function') closeFinishModal();
      return true;
    }

    // 4. Modal Konfirmasi Mulai Mapel
    const startModal = document.getElementById('modalKonfirmasiMulaiMapel');
    if (startModal && startModal.classList.contains('open')) {
      if (typeof closeStartPackageModal === 'function') closeStartPackageModal();
      return true;
    }

    // 5. Overlay Reviu Hasil
    const revOverlay = document.getElementById('reviewHasilOverlay');
    if (revOverlay && revOverlay.classList.contains('open')) {
      if (typeof closeReviewHasil === 'function') closeReviewHasil();
      return true;
    }

    // 6. Modal Logout (jika ada)
    const logoutModal = document.getElementById('modalKonfirmasiLogout');
    if (logoutModal && logoutModal.classList.contains('open')) {
      if (typeof closeLogoutModal === 'function') closeLogoutModal();
      return true;
    }

    // 7. Modal Exit Confirm (jika ada)
    const exitModal = document.getElementById('exitConfirmModal');
    if (exitModal && exitModal.classList.contains('open')) {
      if (typeof closeExitConfirm === 'function') closeExitConfirm();
      return true;
    }

    // 8. Bottom Sheet AI Tutor di Mobile
    const tutorCol = document.getElementById('cbtSidebarCol');
    if (tutorCol && tutorCol.classList.contains('tutor-open')) {
      if (typeof closeTutorSheet === 'function') closeTutorSheet();
      return true;
    }

    // 9. Tab Pembahasan -> Kembali ke Lembar Soal
    const pPemb = document.getElementById('workPanePembahasan');
    if (pPemb && pPemb.classList.contains('active')) {
      if (typeof switchWorkTab === 'function') {
        switchWorkTab('soal', null, { scroll: false, fromBack: true });
      }
      return true;
    }

    // 10. Jika mode kuis aktif & Beranda terbuka -> tutup Beranda
    if (document.body.dataset.quizMode === '1' && typeof homeIsOpen === 'function' && homeIsOpen()) {
      if (typeof homeClose === 'function') homeClose();
      return true;
    }

    // 11. Jika sedang mengerjakan kuis di Lembar Soal:
    // Cegah keluar web tiba-tiba saat tombol Back HP ditekan. Tampilkan konfirmasi selesai tes.
    if (document.body.dataset.quizMode === '1') {
      if (typeof openFinishModal === 'function') {
        openFinishModal();
      }
      return true;
    }

    // 12. Jika di Beranda Mobile dan panel bukan 'beranda' (misal di Modul/Progres/Akun)
    if (typeof homeActivePanel !== 'undefined' && homeActivePanel !== 'beranda') {
      if (typeof homeShowPanel === 'function') {
        homeShowPanel('beranda');
      }
      return true;
    }

    // Jika tidak ada modal atau kuis aktif, biarkan browser bertindak normal
    return false;
  }
};

window.TKAHistory = TKAHistory;
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => TKAHistory.init());
} else {
  TKAHistory.init();
}

// ==================== FASE 2 / T2.6: Modal Lapor Bug Soal & Sistem ====================
function openBugReportModal() {
  const modal = document.getElementById('modalLaporBug');
  if (!modal) return;
  const desc = document.getElementById('bugDescription');
  const msg = document.getElementById('bugReportMsg');
  if (desc) desc.value = '';
  if (msg) {
    msg.style.display = 'none';
    msg.innerText = '';
  }
  const btn = document.getElementById('btnSubmitBug');
  if (btn) {
    btn.disabled = false;
    btn.innerText = 'Kirim Laporan';
  }
  modal.classList.add('open');
  if (window.TKAHistory) {
    window.TKAHistory.push('modal-lapor-bug');
  }
}

function closeBugReportModal(e) {
  if (e && e.target && e.target !== e.currentTarget) return;
  const modal = document.getElementById('modalLaporBug');
  if (modal) modal.classList.remove('open');
}

async function sendBugReport() {
  const cat = document.getElementById('bugCategory') ? document.getElementById('bugCategory').value : 'Umum';
  const descEl = document.getElementById('bugDescription');
  const desc = descEl ? descEl.value.trim() : '';
  const msg = document.getElementById('bugReportMsg');
  const btn = document.getElementById('btnSubmitBug');
  if (!desc) {
    if (msg) {
      msg.style.display = 'block';
      msg.style.background = '#fef2f2';
      msg.style.color = '#dc2626';
      msg.innerText = 'Mohon tuliskan penjelasan kendala terlebih dahulu.';
    }
    return;
  }
  const q = (typeof getCurrentQuestion === 'function') ? getCurrentQuestion() : null;
  const subj = state.currentSubject || 'unknown';
  const pkg = state.currentPkg || '1';
  const qNo = q ? q.nomor : '-';
  const title = `[${cat}] Mapel ${subj} Paket ${pkg} Soal #${qNo}`;
  const fullDesc = `Mapel: ${subj}\nPaket: ${pkg}\nNomor: ${qNo}\nKategori: ${cat}\nKendala: ${desc}\nURL: ${window.location.href}`;

  if (btn) {
    btn.disabled = true;
    btn.innerText = 'Mengirim...';
  }
  try {
    let ok = false;
    if (typeof submitBugReport === 'function') {
      try {
        const timeoutPromise = new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 2000));
        ok = await Promise.race([submitBugReport(title, fullDesc), timeoutPromise]);
      } catch (e) {
        ok = false;
      }
    }
    // Jika belum berhasil atau tanpa Supabase, kirim ke server local fallback
    if (!ok) {
      const res = await fetch('/api/bug-reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description: fullDesc })
      });
      ok = res.ok;
    }

    if (msg) {
      msg.style.display = 'block';
      msg.style.background = '#f0fdf4';
      msg.style.color = '#15803d';
      msg.innerText = 'Terima kasih! Laporan kendala berhasil dikirim.';
    }
    setTimeout(() => {
      closeBugReportModal();
    }, 1200);
  } catch (err) {
    if (msg) {
      msg.style.display = 'block';
      msg.style.background = '#fef2f2';
      msg.style.color = '#dc2626';
      msg.innerText = 'Gagal mengirim laporan: ' + (err.message || 'Error koneksi');
    }
    if (btn) {
      btn.disabled = false;
      btn.innerText = 'Kirim Laporan';
    }
  }
}

// ==========================================================================
// ACCORDION PEMBAHASAN 5 PILAR & MOBILE KEYBOARD HANDLER & DAILY STREAK
// ==========================================================================

function setupPillarAccordions() {
  try {
    const pilarConfigs = [
      { id: 'symbolsBox', bodyId: 'symbolsContainer' },
      { id: 'whyConceptBox', bodyId: 'whyConceptContainer' },
      { cls: 'steps-section-card', bodyId: 'stepsContainer' },
      { cls: 'tips-box', bodyId: 'tipsContainer' }
    ];

    pilarConfigs.forEach(cfg => {
      let card = null;
      if (cfg.id) card = document.getElementById(cfg.id);
      else if (cfg.cls) card = document.querySelector('.' + cfg.cls);
      if (!card) return;

      const header = card.querySelector('.pillar-header-row');
      if (!header || header.dataset.accordionInit) return;
      header.dataset.accordionInit = '1';

      header.style.cursor = 'pointer';
      header.style.display = 'flex';
      header.style.alignItems = 'center';
      header.style.justifyContent = 'space-between';
      header.title = 'Klik untuk membuka / menutup rincian pilar ini';

      let chevron = header.querySelector('.pillar-chevron');
      if (!chevron) {
        chevron = document.createElement('i');
        chevron.className = 'fa-solid fa-chevron-down pillar-chevron';
        chevron.style.marginLeft = 'auto';
        chevron.style.padding = '6px';
        chevron.style.color = '#64748b';
        chevron.style.transition = 'transform 0.2s ease';
        header.appendChild(chevron);
      }

      const bodyEl = card.querySelector('.symbols-grid, .why-text-body, .timeline-steps, .tips-text, #' + cfg.bodyId);
      if (!bodyEl) return;

      // Di mobile (<= 899px): ciutkan default pilar 2-5 agar tidak banjir teks (Pilar 1 tetap terbuka)
      const isMobile = (window.innerWidth <= 899);
      if (isMobile) {
        bodyEl.style.display = 'none';
        chevron.style.transform = 'rotate(0deg)';
        card.classList.remove('is-open');
      } else {
        bodyEl.style.display = 'block';
        chevron.style.transform = 'rotate(180deg)';
        card.classList.add('is-open');
      }

      header.onclick = (e) => {
        e.stopPropagation();
        const isOpen = (bodyEl.style.display !== 'none');
        if (isOpen) {
          bodyEl.style.display = 'none';
          chevron.style.transform = 'rotate(0deg)';
          card.classList.remove('is-open');
        } else {
          bodyEl.style.display = 'block';
          chevron.style.transform = 'rotate(180deg)';
          card.classList.add('is-open');
          if (typeof renderMath === 'function') renderMath(bodyEl);
        }
      };
    });
  } catch (e) {
    console.warn('setupPillarAccordions error:', e);
  }
}
window.setupPillarAccordions = setupPillarAccordions;

function initMobileKeyboardTutorHandler() {
  const inp = document.getElementById('chatInput');
  if (!inp) return;
  inp.addEventListener('focus', () => {
    document.body.classList.add('keyboard-active');
    setTimeout(() => {
      const msgBox = document.getElementById('chatMessages');
      if (msgBox) msgBox.scrollTop = msgBox.scrollHeight;
    }, 200);
  });
  inp.addEventListener('blur', () => {
    document.body.classList.remove('keyboard-active');
  });
}

function recordDailyStudyActivity() {
  try {
    const today = new Date().toISOString().slice(0, 10);
    const lastActive = localStorage.getItem('tka_last_active_date');
    let streak = parseInt(localStorage.getItem('tka_study_streak') || '0', 10);

    if (lastActive) {
      if (lastActive === today) {
        // Sudah aktif hari ini
      } else {
        const lastDate = new Date(lastActive);
        const curDate = new Date(today);
        const diffDays = Math.round((curDate - lastDate) / (1000 * 60 * 60 * 24));
        if (diffDays === 1) {
          streak += 1;
        } else {
          streak = 1;
        }
      }
    } else {
      streak = 1;
    }

    localStorage.setItem('tka_last_active_date', today);
    localStorage.setItem('tka_study_streak', String(streak));
  } catch (e) {}
}
window.recordDailyStudyActivity = recordDailyStudyActivity;

document.addEventListener('DOMContentLoaded', () => {
  initMobileKeyboardTutorHandler();
  recordDailyStudyActivity();
  setTimeout(setupPillarAccordions, 1500);
});


