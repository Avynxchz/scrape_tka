import json, os
from PIL import Image

with open('data/matematika_lanjut_paket_2_learning.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

qs = d.get('soal', d) if isinstance(d, dict) else d
for q in qs:
    if q['nomor'] in [13, 14, 21, 22]:
        print(f"=== Q{q['nomor']} images ===")
        for part in [q.get('stimulus'), q.get('pertanyaan')]:
            if not part: continue
            for img in part.get('images', []):
                fn = img.get('filename')
                p = os.path.join('data/matematika_lanjut/paket_2/images', fn)
                if os.path.exists(p):
                    im = Image.open(p)
                    print(fn, "size:", im.size)
