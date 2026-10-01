import json, re

with open('scratch/p_tags_out.txt', 'w', encoding='utf-8') as out:
    for pkg in [1, 2]:
        data = json.load(open(f'data/bahasa_arab_paket_{pkg}_learning.json', encoding='utf-8'))
        out.write(f"\n=================== PAKET {pkg} ===================\n")
        for q in data['soal']:
            no = q['nomor']
            pert_h = (q.get('pertanyaan') or {}).get('html', '')
            stim_h = (q.get('stimulus') or {}).get('html', '')
            
            p_stim = re.findall(r'<p[^>]*>[\s\S]*?</p>', stim_h)
            p_pert = re.findall(r'<p[^>]*>[\s\S]*?</p>', pert_h)
            
            out.write(f"\nP{pkg} Q{no:2d}:\n")
            for i, p in enumerate(p_stim):
                out.write(f"  stim p[{i}]: {p}\n")
            for i, p in enumerate(p_pert):
                out.write(f"  pert p[{i}]: {p}\n")
            for o in q.get('pilihan_jawaban', []):
                out.write(f"  opt {o.get('key')}: text={repr(o.get('text'))}, img={bool(o.get('image'))}\n")
            for pr in q.get('pernyataan', []):
                out.write(f"  pern {pr.get('key')}: text={repr(pr.get('text'))}, img={bool(pr.get('image'))}\n")

print("Wrote scratch/p_tags_out.txt")
