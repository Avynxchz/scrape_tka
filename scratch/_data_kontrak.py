# -*- coding: utf-8 -*-
"""Ambil jumlah soal real per mapel/paket -> kontrak data buat brief AI."""
import json, glob

rows = {}
for f in sorted(glob.glob('data/*_paket_1_learning.json')):
    key = f.replace('data\\', '').replace('data/', '').split('_paket_')[0]
    try:
        d = json.load(open(f, encoding='utf-8'))
        n1 = len(d.get('soal', []))
    except Exception:
        n1 = None
    rows[key] = {'p1': n1, 'p2': None}

for f in sorted(glob.glob('data/*_paket_2_learning.json')):
    key = f.replace('data\\', '').replace('data/', '').split('_paket_')[0]
    try:
        d = json.load(open(f, encoding='utf-8'))
        rows.setdefault(key, {'p1': None, 'p2': None})['p2'] = len(d.get('soal', []))
    except Exception:
        pass

names = {
    'matematika': 'Matematika (Wajib)', 'bahasa_indonesia': 'Bahasa Indonesia (Wajib)',
    'bahasa_inggris': 'Bahasa Inggris (Wajib)', 'fisika': 'Fisika (Peminatan)',
    'kimia': 'Kimia (Peminatan)', 'biologi': 'Biologi (Peminatan)',
    'ekonomi': 'Ekonomi', 'geografi': 'Geografi', 'sosiologi': 'Sosiologi',
    'sejarah': 'Sejarah', 'antropologi': 'Antropologi', 'kewirausahaan': 'Kewirausahaan (PKWU)',
    'matematika_lanjut': 'Matematika Lanjut', 'bahasa_indonesia_lanjut': 'B. Indonesia Lanjut',
    'bahasa_inggris_lanjut': 'B. Inggris Lanjut', 'ppkn': 'PPKn', 'bahasa_arab': 'Bahasa Arab',
    'bahasa_jepang': 'Bahasa Jepang', 'bahasa_jerman': 'Bahasa Jerman',
    'bahasa_prancis': 'Bahasa Prancis', 'bahasa_mandarin': 'Bahasa Mandarin',
    'bahasa_korea': 'Bahasa Korea',
}
total = 0
out = []
for k, v in rows.items():
    n1, n2 = v['p1'] or 0, v['p2'] or 0
    total += n1 + n2
    out.append(f"| {names.get(k, k)} | `{k}` | {n1} | {n2} |")
print('\n'.join(out))
print(f"TOTAL: {total} soal")
