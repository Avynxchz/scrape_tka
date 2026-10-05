const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
['homeOverlay','hoHeroTrack','hoHeroDots','hoMain','btnHome'].forEach(id => console.log(id + ':', html.includes('id="' + id + '"') ? 'OK' : 'HILANG'));
const css = fs.readFileSync('style.css', 'utf8');
['.home-overlay','.ho-hero-card','.ho-card','.ho-section'].forEach(c => console.log(c + ':', css.includes(c) ? 'OK' : 'HILANG'));
