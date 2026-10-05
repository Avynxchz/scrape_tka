# -*- coding: utf-8 -*-
"""Hitung jumlah soal real per mapel per paket -> untuk brief AI lain."""
import glob, json

rows = []
for f in sorted(glob.glob('data/*_paket_1_learning.json')):
    key = f.replace('data\\', '').replace('data/', '').split('_paket_')[0]
    d = json.load(open(f, encoding='utf-8'))
    n1 = len(d.get('soal', []))
    n2 = None
    try:
        d2 = json.load(open(f.replace('_paket_1_', '_paket_2_'), encoding='utf-8'))
        n2 = len(d2.get('soal', []))
    except Exception:
        pass
    rows.append((key, n1, n2))

print('| Key | Paket 1 | Paket 2 |')
print('|---|---|---|')
t1 = t2 = 0
for k, a, b in rows:
    t1 += a or 0
    t2 += (b or 0)
    print(f'| {k} | {a} | {b if b is not None else "-"} |')
print(f'| TOTAL | {t1} | {t2} |')
