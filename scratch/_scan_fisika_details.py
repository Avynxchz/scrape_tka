import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

for pkg in [1, 2]:
    with open(f'data/fisika_paket_{pkg}_learning.json', encoding='utf-8') as f:
        d = json.load(f)
    print(f"=== Scanning Fisika P{pkg} ({len(d['soal'])} questions) ===")
    for q in d['soal']:
        no = q['nomor']
        stim_text = q.get('stimulus', {}).get('text', '') or ''
        pert_text = q.get('pertanyaan', {}).get('text', '') or ''
        
        # Check broken characters
        if '\ufffd' in stim_text or '\ufffd' in pert_text:
            print(f"  P{pkg} Q{no}: Contains replacement char in text: {repr(stim_text[:60])} | {repr(pert_text[:60])}")
        
        # Check flat exponents in options
        for o in q.get('pilihan_jawaban') or q.get('opsi', []):
            otext = o.get('text', '') or ''
            if '\ufffd' in otext:
                print(f"  P{pkg} Q{no} Opt {o.get('key')}: Contains replacement char: {repr(otext)}")
