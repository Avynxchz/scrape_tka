# -*- coding: utf-8 -*-
import json
import shutil

p = 'data/solution_sources/BAHASA_INGGRIS_LANJUT_PAKET_2_SOLUTIONS.json'
d = json.load(open(p, encoding='utf-8'))
for s in d['solutions']:
    if s.get('question_number') == 4:
        s['ditanyakan'] = 'Menganalisis hubungan sebab-akibat antara penyembunyian emosi sejati dan peningkatan level stres berdasarkan teks.'
        bad_keys = [k for k in s.keys() if 'losing our' in k or 'self-esteem' in k]
        for bk in bad_keys:
            s.pop(bk, None)
    elif s.get('question_number') == 13:
        s['ditanyakan'] = 'Mengidentifikasi alasan-alasan yang mendukung opini penulis mengenai peran positif finfluencer bagi generasi muda.'
        bad_keys = [k for k in s.keys() if 'broader' in k or 'ventures' in k]
        for bk in bad_keys:
            s.pop(bk, None)

with open(p, 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

shutil.copyfile(p, 'exports/bahasa_inggris_lanjut_paket_2_solutions.json')
print('Ingl 2 Q4 and Q13 successfully repaired and exported!')
