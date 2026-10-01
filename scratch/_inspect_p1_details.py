import json

with open('data/bahasa_arab_paket_1_learning.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

with open('scratch/p1_details_out.txt', 'w', encoding='utf-8') as out:
    for q in d['soal'][:10]:
        no = q['nomor']
        stim = q.get('stimulus')
        stim_html = stim.get('html', '') if isinstance(stim, dict) else str(stim or '')
        prompt = q.get('pertanyaan') or q.get('prompt')
        prompt_html = prompt.get('html', '') if isinstance(prompt, dict) else str(prompt or '')
        pilihan = q.get('pilihan_jawaban', [])
        out.write(f"\n=== NOMOR {no} (tipe: {q.get('tipe_soal')}) ===\n")
        out.write(f"stimulus html: {stim_html}\n")
        out.write(f"prompt html: {prompt_html}\n")
        for opt in pilihan:
            has_img = bool(opt.get('image') or ('<img' in (opt.get('html') or '')))
            txt = opt.get('text') or ''
            htm = opt.get('html') or ''
            out.write(f"  {opt.get('key')}: img={has_img} | text='{txt}' | html='{htm}'\n")

print("Done writing to scratch/p1_details_out.txt")
