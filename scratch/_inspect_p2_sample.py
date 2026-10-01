import json

data = json.load(open('data/bahasa_arab_paket_2_learning.json', encoding='utf-8'))
with open('scratch/p2_sample_out.txt', 'w', encoding='utf-8') as out:
    for q in data['soal']:
        if q['nomor'] in [1, 2, 3, 4, 5, 6, 9, 10, 11, 27, 28, 29]:
            out.write(f"\n=== P2 NO {q['nomor']} ===\n")
            out.write("stim: " + repr((q.get('stimulus') or {}).get('text') or '') + "\n")
            out.write("pert: " + repr((q.get('pertanyaan') or {}).get('text') or '') + "\n")
            out.write("opts: " + repr([(o.get('key'), o.get('text')) for o in q.get('pilihan_jawaban', [])]) + "\n")
            out.write("pern: " + repr([(p.get('key'), p.get('text')) for p in q.get('pernyataan', [])]) + "\n")
            out.write("stim html: " + repr((q.get('stimulus') or {}).get('html') or '') + "\n")
            out.write("pert html: " + repr((q.get('pertanyaan') or {}).get('html') or '') + "\n")

print("Done writing scratch/p2_sample_out.txt")
