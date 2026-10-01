const fs = require('fs');
const path = require('path');

const data = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/matematika_paket_2_learning.json'), 'utf-8'));
const soalList = data.soal;

function parseBsKunci(q) {
  const map = {};
  (Array.isArray(q.kunci_jawaban) ? q.kunci_jawaban : []).forEach(entry => {
    const [k, v] = String(entry).split(':');
    if (k && v) map[k] = v;
  });
  return map;
}

console.log(`Loaded ${soalList.length} questions from Matematika Paket 2.`);

// Scenario 1: All questions unanswered
console.log('\n--- Scenario 1: All Unanswered ---');
let emptyCount = 0;
soalList.forEach(q => {
  if (q.tipe_soal === 'Benar-Salah') {
    const stmts = q.pernyataan || [];
    const hasAny = false;
    if (!hasAny) emptyCount++;
  } else {
    emptyCount++;
  }
});
console.log(`Unanswered count: ${emptyCount}/${soalList.length}`);

// Scenario 2: Simulate 10 correct answers, 5 wrong, 10 unanswered
console.log('\n--- Scenario 2: Sample Test Run ---');
const userAnswers = {};

// Q1 (PG, key: C): user chooses C (correct)
userAnswers[1] = 'C';
// Q2 (PG, key: C): user chooses A (wrong)
userAnswers[2] = 'A';
// Q3 (BS, key: A:Benar, B:Salah, C:Benar): user answers correctly
userAnswers[3] = { 'A': 'Benar', 'B': 'Salah', 'C': 'Benar' };
// Q4 (PG, key: D): user chooses D (correct)
userAnswers[4] = 'D';
// Q7 (PG Kompleks, key: ['C', 'D']): user chooses ['C', 'D'] (correct)
userAnswers[7] = ['C', 'D'];
// Q10 (PG Kompleks, key: ['C', 'D', 'E']): user chooses ['C'] (wrong)
userAnswers[10] = ['C'];
// Q13 (BS, key: A:Salah, B:Benar, C:Salah): user answers A:Benar (wrong)
userAnswers[13] = { 'A': 'Benar', 'B': 'Benar', 'C': 'Salah' };

let benar = 0, salah = 0, kosong = 0;
const reviewRows = [];

soalList.forEach(item => {
  const ans = userAnswers[item.nomor];
  const correctKey = item.kunci_jawaban;

  let status = 'kosong';
  let andaText = 'Belum dijawab';
  let kunciText = '';

  const getOptSnippet = (k) => {
    const opt = (item.pilihan_jawaban || []).find(o => o.key === k);
    if (!opt) return '';
    return opt.text || opt.latex || '';
  };

  if (item.tipe_soal === 'Benar-Salah') {
    const kunciMap = parseBsKunci(item);
    const stmts = item.pernyataan || [];
    const hasAny = stmts.some(st => ans && typeof ans === 'object' && ans[st.key]);
    const allRight = hasAny && stmts.every(st => ans[st.key] === kunciMap[st.key]);

    if (!hasAny) {
      status = 'kosong';
      kosong++;
    } else if (allRight) {
      status = 'benar';
      benar++;
    } else {
      status = 'salah';
      salah++;
    }

    andaText = stmts.map(st => `${st.key}: ${(ans && ans[st.key]) || '-'}`).join(', ');
    kunciText = stmts.map(st => `${st.key}: ${kunciMap[st.key]}`).join(', ');
  } else {
    const isComplex = item.tipe_soal === 'Pilihan Ganda Kompleks';
    let isCorrect = false;

    if (!ans || (Array.isArray(ans) && ans.length === 0)) {
      status = 'kosong';
      kosong++;
    } else {
      if (isComplex) {
        const target = Array.isArray(correctKey) ? [...correctKey].sort().join(',') : String(correctKey);
        const user = Array.isArray(ans) ? [...ans].sort().join(',') : String(ans);
        isCorrect = user === target;
      } else {
        isCorrect = ans === correctKey;
      }
      if (isCorrect) {
        status = 'benar';
        benar++;
      } else {
        status = 'salah';
        salah++;
      }
      andaText = Array.isArray(ans) ? ans.join(', ') : ans;
    }

    kunciText = Array.isArray(correctKey) ? correctKey.join(', ') : correctKey;
  }

  reviewRows.push({ no: item.nomor, status, anda: andaText, kunci: kunciText });
});

console.log(`Result: Benar=${benar}, Salah=${salah}, Kosong=${kosong}, Total=${soalList.length}`);
const percent = Math.round((benar / soalList.length) * 100);
console.log(`Skor: ${percent}%`);
console.log('\nFirst 10 review rows:');
console.table(reviewRows.slice(0, 10));
