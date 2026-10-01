import json

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for q in d['soal']:
    no = q['nomor']
    p = q.get('pembahasan', '')
    preview = (p[:300] + '...') if len(p) > 300 else p
    print(f"=== Q{no:02d} (len={len(p)}) ===")
    print(preview)
    print()
