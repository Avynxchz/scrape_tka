import json

with open('data/matematika_lanjut_paket_1_learning.json', encoding='utf-8') as f:
    d = json.load(f)

for q in d['soal']:
    opts = []
    for opt in q.get('pilihan_jawaban', []):
        h = opt.get('html') or ''
        im = opt.get('image')
        if im or '<img' in h:
            opts.append((opt['key'], opt.get('text'), im, h[:60]))
    if opts:
        print(f"MTL P1 Q{q['nomor']}: {len(opts)} options with images")
        for k, t, im, h in opts:
            print(f"   Opt {k}: text={t}, img={im}, h={h}")
