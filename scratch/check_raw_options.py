import json

d = json.load(open('data/paket_2/matematika_paket_2.json', encoding='utf-8'))
for no in [2, 8, 12, 14, 20, 24]:
    q = d['soal'][no-1]
    print(f"=== Q{no} ===")
    for o in q.get('pilihan_jawaban', []):
        print(o)
