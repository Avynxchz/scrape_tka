import json

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for q in d['soal']:
    no = q['nomor']
    p = q.get('pembahasan_ai', {})
    keys = list(p.keys()) if p else "NONE"
    length = len(json.dumps(p, ensure_ascii=False)) if p else 0
    print(f"Q{no:02d}: keys={keys}, len={length}")
