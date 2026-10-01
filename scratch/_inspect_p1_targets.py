import json

with open('data/matematika_paket_1_learning.json', encoding='utf-8') as f:
    d = json.load(f)

for no in [5, 7, 8, 12, 15, 43]:
    q = next(x for x in d['soal'] if x['nomor'] == no)
    print(f"=== SOAL {no} ===")
    print("STIMULUS HTML:", q.get('stimulus', {}).get('html'))
    print("PERTANYAAN HTML:", q.get('pertanyaan', {}).get('html'))
    for opt in q.get('pilihan_jawaban', []):
        print("  OPT:", opt.get('key'), opt.get('text'), opt.get('latex'), opt.get('html'), opt.get('image'))
