import json, glob

for f in glob.glob('data/*_learning.json'):
    d = json.load(open(f, encoding='utf-8'))
    for q in d.get('soal', []):
        for stmt in q.get('pernyataan') or []:
            if stmt.get('image'):
                print(f"{f} Q{q['nomor']} {stmt.get('key')}: text={repr(stmt.get('text'))}, latex={repr(stmt.get('latex'))}, img={stmt.get('image', {}).get('filename')}")
