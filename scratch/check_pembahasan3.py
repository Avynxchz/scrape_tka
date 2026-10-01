import json

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for q in d['soal']:
    no = q['nomor']
    p = q.get('pembahasan', '')
    if isinstance(p, dict):
        print(f"Q{no:02d} type=dict keys={list(p.keys())}")
    elif isinstance(p, str):
        print(f"Q{no:02d} type=str len={len(p)} preview={repr(p[:200])}")
    else:
        print(f"Q{no:02d} type={type(p).__name__}")
