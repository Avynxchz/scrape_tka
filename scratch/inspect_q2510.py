import json

d = json.load(open('data/bahasa_indonesia_paket_2_learning.json', encoding='utf-8'))
for q in d['soal']:
    if q['nomor'] in [2, 5, 10]:
        print(f"=== NOMOR {q['nomor']} ===")
        print("tipe:", q.get('tipe'))
        print("stimulus text len:", len(q.get('stimulus', {}).get('text', '')))
        print("pertanyaan text:", q.get('pertanyaan', {}).get('text', ''))
        print("pilihan_jawaban len:", len(q.get('pilihan_jawaban', [])))
        print("pernyataan len:", len(q.get('pernyataan', [])))
        print("kunci:", q.get('kunci_jawaban'))
