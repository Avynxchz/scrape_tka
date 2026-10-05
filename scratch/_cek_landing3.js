const fs = require('fs');
const html = fs.readFileSync('landing.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
scripts.forEach((s, i) => { try { new Function(s); console.log(`script ${i+1}: OK`); } catch (e) { console.log(`script ${i+1}: ERROR -> ${e.message}`); } });
const checks = ['Tika', 'matchMedia', 'phoneCol', 'AI Tutor · Matematika', 'Paket 1'];
checks.forEach(c => console.log(`"${c}":`, html.includes(c) ? 'ada' : 'HILANG'));
console.log('ukuran:', (fs.statSync('landing.html').size/1024).toFixed(1)+'KB');
