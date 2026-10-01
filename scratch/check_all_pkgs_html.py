import json, glob, os

files = glob.glob('data/*_learning.json')
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    soal = d.get('soal', [])
    stim_html_cnt = sum(1 for q in soal if q.get('stimulus', {}).get('html'))
    pert_html_cnt = sum(1 for q in soal if q.get('pertanyaan', {}).get('html'))
    print(f"{os.path.basename(f)}: total={len(soal)}, stim_html={stim_html_cnt}, pert_html={pert_html_cnt}")
