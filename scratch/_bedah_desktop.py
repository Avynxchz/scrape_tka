# -*- coding: utf-8 -*-
"""Bedah struktur kode desktop Stitch: layout, section, card, angka karangan."""
import re

kode = open('scratch/_stitch_desktop_raw.html', encoding='utf-8').read()

# 1. Struktur top-level
tops = re.findall(r'<(header|main|nav|aside|section)[^>]*class="([^"]{0,80})"', kode)
print('== TOP-LEVEL ==')
for t in tops[:14]:
    print(' ', t[0], '|', t[1][:70])

# 2. Judul & angka yang muncul (deteksi karangan)
print('\n== ANGKA/TEKS PENTING ==')
for pat in ['46 Soal', '20 Soal', '25 Soal', '45 Menit', '50 Menit', '35 Menit',
            'Skor', 'skor', '%', 'Modul', 'LATIHAN TKA', 'SIMULASI', 'Latihan TKA SIMULASI']:
    c = kode.count(pat)
    if c: print(f'  "{pat}": {c}x')

# 3. Ikon & font
print('\n== FONT/IKON ==')
for pat in ['Plus+Jakarta', 'Material+Symbols', 'tailwind.config', 'fonts.googleapis']:
    print(f'  {pat}:', pat in kode)

# 4. Hitung card
print('\n== CARD ==')
print('  snap-start:', kode.count('snap-start'))
print('  rounded-xl:', kode.count('rounded-xl'))

# 5. Lebar desain
m = re.search(r'width:\s*(\d+)px', kode)
print('\n lebar desain:', m.group(1) if m else '?')

# 6. Potongan hero
i = kode.find('Latihan TKA SIMULASI')
print('\n== HERO CONTOH ==')
print(kode[i-200:i+400].replace('\n',' ')[:500])
