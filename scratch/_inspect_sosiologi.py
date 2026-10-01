import json

with open('data/sosiologi_paket_1_learning.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for q in data.get('soal', []):
    if q.get('nomor') in [13, 14, 15]:
        print(f"=== NOMOR {q.get('nomor')} ===")
        print("stimulus:", repr(q.get('stimulus')))
        print("soal:", repr(q.get('soal')))
        print("images:", q.get('images'))
        print("options:")
        for opt in q.get('options', []):
            print("  ", opt.get('key'), repr(opt.get('text')), opt.get('image'))
