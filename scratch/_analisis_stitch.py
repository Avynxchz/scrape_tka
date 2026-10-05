# -*- coding: utf-8 -*-
"""Analisis struktur kode Stitch sebelum integrasi."""
import re

h = open('home_stitch_source.html', encoding='utf-8').read()
print('panjang:', len(h))
print('tailwind config:', 'tailwind.config' in h)
print('sections:', h.count('SUBJECT SECTION'))
print('cards (snap-start):', h.count('snap-start'))
print('modal:', 'subject-modal-backdrop' in h)
print('nav:', 'data-path' in h)
print('"20 Soal" (karangan):', h.count('20 Soal'))
print('"Skor 92" (karangan):', 'Skor 92' in h)

# daftar mapel yang disebut
for m in ['Matematika', 'Fisika', 'Ekonomi', 'Kimia', 'Biologi', 'Geografi']:
    print(f'mapel {m}:', h.count(m))

# body section boundaries
b = h.find('<body')
print('body mulai:', b)
