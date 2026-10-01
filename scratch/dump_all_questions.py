import json

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
with open('scratch/all_questions_dump.txt', 'w', encoding='utf-8') as out:
    for q in d['soal']:
        no = q['nomor']
        stim_text = q.get('stimulus', {}).get('text', '')
        pert_text = q.get('pertanyaan', {}).get('text', '')
        tipe = q.get('tipe_soal', '')
        kunci = q.get('kunci_jawaban', '')
        opts = q.get('pilihan_jawaban', [])
        stmts = q.get('pernyataan', [])
        
        out.write(f"===== SOAL {no} ({tipe}) | Kunci: {kunci} =====\n")
        out.write(f"STIMULUS: {stim_text[:400]}\n")
        out.write(f"PERTANYAAN: {pert_text[:400]}\n")
        if opts:
            for o in opts:
                t = (o.get('text') or '')[:100]
                lx = (o.get('latex') or '')[:100]
                out.write(f"  {o['key']}: text={repr(t)} latex={repr(lx)}\n")
        if stmts:
            for s in stmts:
                t = (s.get('text') or '')[:100]
                lx = (s.get('latex') or '')[:100]
                out.write(f"  Pernyataan {s['key']}: text={repr(t)} latex={repr(lx)}\n")
        out.write("\n")

print("Done")
