import json

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for no in [4, 5, 8, 10, 13, 17, 18, 20, 23, 25]:
    q = d['soal'][no-1]
    print(f"=== SOAL {no} ===")
    print("STIMULUS HTML:")
    print(q.get('stimulus', {}).get('html'))
    print("PERTANYAAN HTML:")
    print(q.get('pertanyaan', {}).get('html'))
    print()
