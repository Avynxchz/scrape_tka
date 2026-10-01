import json

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for no in [2, 8, 12, 14, 24]:
    q = d['soal'][no-1]
    for o in q.get('pilihan_jawaban', []):
        if o.get('image'):
            print(f"Q{no} {o['key']}: latex={repr(o.get('latex'))}, text={repr(o.get('text'))}, img={o.get('image',{}).get('filename')}")
