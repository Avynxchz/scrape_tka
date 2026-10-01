import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

for pkg in [1, 2]:
    with open(f'data/fisika_paket_{pkg}_learning.json', encoding='utf-8') as f:
        d = json.load(f)
    print(f"=== Exponents in Fisika P{pkg} ===")
    for q in d['soal']:
        no = q['nomor']
        opts = q.get('pilihan_jawaban') or q.get('opsi', [])
        found = False
        for o in opts:
            t = o.get('text', '') or ''
            if any(c in t for c in '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻·') or re.search(r'\b10\s*[-–]\s*\d+', t):
                print(f"  P{pkg} Q{no} Opt {o.get('key')}: text={repr(t)} latex={o.get('latex')}")
                found = True
                break
        if not found:
            # check stimulus & prompt
            st = q.get('stimulus', {}).get('text', '') or ''
            pt = q.get('pertanyaan', {}).get('text', '') or ''
            m = re.findall(r'(?:10\s*[-–]\s*\d+|10\s*[\^]\s*[-–]?\d+|\b\d+\s*°C|\b\d+\s*°)', st + ' ' + pt)
            if m:
                print(f"  P{pkg} Q{no} Prompt/Stim math: {m}")
