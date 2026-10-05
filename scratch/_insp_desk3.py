# -*- coding: utf-8 -*-
# Inspeksi sidebar: widget kuota AI + scan angka fiktif lain
import io, re

BODY = io.open('scratch/_desk_body.html', encoding='utf-8').read()

a = BODY.find('<aside')
b = BODY.find('</aside>')
print('aside:', a, '->', b, 'len:', b - a)
aside = BODY[a:b]

# print struktur aside: semua teks visible + style width:
txt = re.sub(r'<span class="material-symbols-outlined[^"]*">[a-z_]+</span>', '[ikon]', aside)
txt = re.sub(r'\s+', ' ', txt)
print(txt[:4200])
print()
print('== bar width di aside ==')
for m in re.finditer(r'style="width: ?(\d+)%?"', aside):
    print('width:', m.group(1), 'ctx:', re.sub(r'\s+', ' ', aside[max(0, m.start()-100):m.end()+40]))
print()
print('== semua angka % di body luar aside (scan kasar) ==')
rest = BODY[:a] + BODY[b:]
for m in re.finditer(r'>(\d+(?:[.,]\d+)?)%?<', rest):
    s = re.sub(r'\s+', ' ', rest[max(0, m.start()-90):m.end()+30])
    print(m.group(0), '::', s)
