# -*- coding: utf-8 -*-
import json
import re
from bs4 import BeautifulSoup

def clean_opt_html(raw):
    if not raw:
        return ''
    s = BeautifulSoup(raw, 'html.parser')
    res = str(s)
    res = re.sub(r'<\!--\?xml[^>]*\?-->', '', res)
    res = re.sub(r'<\!--[\s\S]*?-->', '', res)
    return res.strip()

soup = BeautifulSoup(open('data/raw_html/kimia_paket_1.html', encoding='utf-8'), 'html.parser')
lrn = json.load(open('data/kimia_paket_1_learning.json', encoding='utf-8'))
isi_list = soup.find_all(class_='isi-soal')

updated = 0
for idx, q in enumerate(lrn['soal']):
    if idx < len(isi_list):
        tbl = isi_list[idx].find('table')
        if tbl:
            rows = tbl.find_all('tr')
            opts = q.get('pilihan_jawaban', [])
            opt_idx = 0
            for r in rows:
                tds = r.find_all('td')
                if len(tds) > 1 and opt_idx < len(opts):
                    cell_html = clean_opt_html(tds[1].decode_contents())
                    if cell_html and ('<' in cell_html):
                        opts[opt_idx]['html'] = cell_html
                        opt_idx += 1
                        updated += 1

print(f'Extracted {updated} rich option htmls for Kimia P1')
for opt in lrn['soal'][5]['pilihan_jawaban']:
    print('  Q6 Opt', opt['key'], ':', opt.get('html'))
for opt in lrn['soal'][7]['pilihan_jawaban']:
    print('  Q8 Opt', opt['key'], ':', opt.get('html'))
