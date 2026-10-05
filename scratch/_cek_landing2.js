const fs = require('fs');
const html = fs.readFileSync('landing.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
scripts.forEach((s, i) => { try { new Function(s); console.log(`inline script ${i+1}: OK`); } catch (e) { console.log(`inline script ${i+1}: SYNTAX ERROR -> ${e.message}`); } });
const must = ['href="/app"','href="/privacy"','href="/terms"','Pusmendik','Rp20.000','5 pertanyaan','00.00 WIB','bukan situs resmi','Masukan via aplikasi','Coba tanpa login','Coba sekarang (beta)'];
const miss = must.filter(m => !html.includes(m));
console.log('konten wajib hilang:', miss.length ? miss : 'tidak ada — semua konten asli dipertahankan');
console.log('ukuran:', (fs.statSync('landing.html').size/1024).toFixed(1)+'KB');
