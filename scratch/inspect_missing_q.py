import json

with open('data/bahasa_indonesia_paket_2_learning.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

soal_map = {q['nomor']: q for q in d['soal']}
for n in [2, 5, 10]:
    if n in soal_map:
        q = soal_map[n]
        print(f"Soal {n}: tipe={q.get('tipe')}, kunci={q.get('kunci')}, tanya={q.get('pertanyaan')[:80]}")
