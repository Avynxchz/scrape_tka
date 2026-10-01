import json, re

for pkg in [1, 2]:
    data = json.load(open(f'data/bahasa_arab_paket_{pkg}_learning.json', encoding='utf-8'))
    for q in data['soal']:
        for field in ['pertanyaan', 'stimulus']:
            h = (q.get(field) or {}).get('html', '')
            txt = (q.get(field) or {}).get('text', '')
            for s in [h, txt]:
                m = re.findall(r'(!\s*[a-zA-Z]|\.\s*[a-zA-Z]|\(!\s*[a-zA-Z])', s)
                if m:
                    print(f"P{pkg} Q{q['nomor']} {field}: {m} in {repr(s[:80])}")
