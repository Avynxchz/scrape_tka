import json, sys

def is_arabic(text):
    if not text: return False
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06ff' or '\u0750' <= c <= '\u077f' or '\ufb50' <= c <= '\ufdff' or '\ufe70' <= c <= '\ufeff')
    latin_chars = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    return arabic_chars > latin_chars

lines = []
for pkg in [1, 2]:
    with open(f'data/bahasa_arab_paket_{pkg}_learning.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    lines.append(f"\n==================== BAHASA ARAB PAKET {pkg} (Total: {len(data.get('soal', []))}) ====================")
    for q in data.get('soal', []):
        no = q.get('nomor')
        stim = q.get('stimulus') or {}
        pert = q.get('pertanyaan') or {}
        opts = q.get('pilihan_jawaban') or []
        pern = q.get('pernyataan') or []
        tipe = q.get('tipe')
        
        stim_text = (stim.get('text') or '').replace('\n', ' ').strip()
        pert_text = (pert.get('text') or '').replace('\n', ' ').strip()
        
        stim_ar = is_arabic(stim_text)
        pert_ar = is_arabic(pert_text)
        
        opt_info = []
        for o in opts:
            otxt = (o.get('text') or '').replace('\n', ' ').strip()
            o_img = bool(o.get('image'))
            o_ar = is_arabic(otxt)
            opt_info.append(f"{o.get('key')}({'AR' if o_ar else ('IMG' if o_img else 'ID')})")
            
        pern_info = []
        for p in pern:
            ptxt = (p.get('text') or '').replace('\n', ' ').strip()
            p_ar = is_arabic(ptxt)
            pern_info.append(f"{p.get('key')}({'AR' if p_ar else 'ID'})")

        has_stim_img = bool(stim.get('images') or '<img' in (stim.get('html') or ''))
        has_pert_img = bool(pert.get('images') or '<img' in (pert.get('html') or ''))
        
        lines.append(f"No {no:2d} | tipe: {str(tipe):12s} | stim({'AR' if stim_ar else 'ID'}): {len(stim_text)}c | pert({'AR' if pert_ar else 'ID'}): {pert_text[:35]} | img: S={has_stim_img} P={has_pert_img} | opts: {opt_info} | pern: {pern_info}")

with open('scratch/bahasa_arab_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Summary written to scratch/bahasa_arab_summary.txt")
