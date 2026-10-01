import json

data = json.load(open('data/bahasa_arab_paket_1_learning.json', encoding='utf-8'))
with open('scratch/p1_q7_10_details.txt', 'w', encoding='utf-8') as out:
    for q in data['soal']:
        if q['nomor'] in [7, 8, 9, 10]:
            out.write(f"\n=== NOMOR {q['nomor']} ===\n")
            out.write("stim text: " + repr(q.get('stimulus', {}).get('text')) + "\n")
            out.write("stim html: " + repr(q.get('stimulus', {}).get('html')) + "\n")
            out.write("pert text: " + repr(q.get('pertanyaan', {}).get('text')) + "\n")
            out.write("pert html: " + repr(q.get('pertanyaan', {}).get('html')) + "\n")
            out.write("opts: " + repr([(o.get('key'), o.get('text'), bool(o.get('image')), o.get('image')) for o in q.get('pilihan_jawaban', [])]) + "\n")
            out.write("pern: " + repr([(p.get('key'), p.get('text')) for p in q.get('pernyataan', [])]) + "\n")

print("Done writing scratch/p1_q7_10_details.txt")
