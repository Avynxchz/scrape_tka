const fs = require('fs');
const html = fs.readFileSync('原型/index.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
scripts.forEach((s, i) => { try { new Function(s); console.log(`inline script ${i+1}: OK (${s.length} chars)`); } catch (e) { console.log(`inline script ${i+1}: SYNTAX ERROR -> ${e.message}`); } });
// sanity: semua id yang direferensikan JS ada di HTML
const ids = ['mStu','mAi','mDots','fCards','mHl','mChips','chatBody','scr1','scr2','scr3','examGrid','examProg','stepsWrap','scrub','panels','phone','heroFloat','tline','cwWrap','segInd','cardFree','cardPrem','tabFree','tabPrem','mnu','btnMenu','statistik','paket','faq','fitur','beranda'];
const missing = ids.filter(id => !html.includes(`id="${id}"`));
console.log('missing ids:', missing.length ? missing : 'tidak ada');
// hitung tag pembuka/penutup utama
for (const t of ['section','div','header','footer','main','nav']) {
  const open = (html.match(new RegExp(`<${t}[\\s>]`, 'g')) || []).length;
  const close = (html.match(new RegExp(`</${t}>`, 'g')) || []).length;
  if (open !== close) console.log(`TAG MISMATCH <${t}>: open=${open} close=${close}`);
}
console.log('tag balance check selesai');
console.log('ukuran file:', (fs.statSync('原型/index.html').size/1024).toFixed(1)+'KB');
