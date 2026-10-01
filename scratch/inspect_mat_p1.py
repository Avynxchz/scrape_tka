import json, os
from PIL import Image

with open('data/matematika_paket_1_learning.json', encoding='utf-8') as f:
    d = json.load(f)
qs = d.get('soal', d) if isinstance(d, dict) else d
for q in qs:
    if q['nomor'] in [5, 7, 8, 12, 13, 15, 43]:
        print(f"=== Q{q['nomor']} ===")
        print("STIM:", (q.get('stimulus') or {}).get('html'))
        print("PERT:", (q.get('pertanyaan') or {}).get('html'))
        for o in q.get('pilihan_jawaban', []):
            if o.get('image') or o.get('html'):
                print(f"  OPT {o['key']}: html={o.get('html')} img={o.get('image')}")
