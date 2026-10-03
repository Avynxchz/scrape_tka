# -*- coding: utf-8 -*-
"""Pembersih wrapper Pusmendik di semua data/*_paket_*_learning.json (one-off).

Aksi per field html (stimulus, pertanyaan, tiap pilihan):
1. Lepaskan komentar <!--...--> (termasuk sisa <?xml encoding ... ?>).
2. Lepaskan wrapper terluar <div class="col-lg-6 cont-soal|isi-soal" ...> ... </div>
   secara berulang selama polanya cocok (wrapper di awal + penutup di akhir).
3. Buang properti height/overflow dari inline style mana pun.
4. Bila hasil akhir tidak punya konten terlihat (hanya tag/spasi) DAN tidak ada <img>,
   field html dihapus agar app memakai fallback text (stimulus kosong tidak dirender).
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RE_COMMENT = re.compile(r'<!--[\s\S]*?-->')
RE_WRAP = re.compile(r'^<div\s+class=["\']col-lg-6[^"\']*["\'][^>]*>([\s\S]*)</div>\s*$', re.I)
RE_STYLE = re.compile(r'style="([^"]*)"', re.I)
RE_TAG = re.compile(r'<[^>]+>')


def clean_style(m):
    s = m.group(1)
    s2 = re.sub(r'(?:^|;)\s*(height|overflow)\s*:[^;"]*', '', s, flags=re.I)
    s2 = s2.strip().strip(';').strip()
    return 'style="%s"' % s2


def visible_len(h):
    t = RE_TAG.sub('', h or '')
    t = t.replace('&nbsp;', ' ').replace('\u00a0', ' ')
    return len(t.strip())


def clean_html(h):
    changed = False
    orig = h
    h2 = RE_COMMENT.sub('', h).strip()
    if h2 != h:
        changed = True
    h = h2
    # unwrap berulang
    while True:
        m = RE_WRAP.match(h)
        if not m:
            break
        h = m.group(1).strip()
        changed = True
    h3 = RE_STYLE.sub(clean_style, h)
    if h3 != h:
        changed = True
    h = h3.strip()
    return h, changed


def main():
    stats = {'file': 0, 'field_bersih': 0, 'field_dihapus': 0, 'wrap_dilepas': 0}
    for fp in sorted(glob.glob(os.path.join(ROOT, 'data', '*_paket_*_learning.json'))):
        with open(fp, 'r', encoding='utf-8') as f:
            doc = json.load(f)
        soal_list = doc.get('soal') or []
        dirty = False
        for q in soal_list:
            for sec in ('stimulus', 'pertanyaan'):
                sec_obj = q.get(sec)
                if not isinstance(sec_obj, dict) or 'html' not in sec_obj:
                    continue
                h = sec_obj['html'] or ''
                if not h.strip():
                    continue
                before_wraps = len(RE_WRAP.findall(h))
                nh, changed = clean_html(h)
                if changed:
                    stats['field_bersih'] += 1
                    stats['wrap_dilepas'] += before_wraps
                # hapus bila tak ada konten nyata & tak ada gambar
                if '<img' not in nh.lower() and visible_len(nh) == 0:
                    del sec_obj['html']
                    stats['field_dihapus'] += 1
                    dirty = True
                    continue
                if changed:
                    sec_obj['html'] = nh
                    dirty = True
            for pil in (q.get('pilihan') or []):
                if isinstance(pil, dict) and pil.get('html'):
                    h = pil['html']
                    if not h.strip():
                        continue
                    nh, changed = clean_html(h)
                    if changed:
                        pil['html'] = nh
                        stats['field_bersih'] += 1
                        dirty = True
        if dirty:
            with open(fp, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False)
            stats['file'] += 1
            print('dibersihkan:', os.path.basename(fp))
    print('RINGKASAN:', stats)
    # verifikasi semua JSON masih valid
    n = 0
    for fp in glob.glob(os.path.join(ROOT, 'data', '*_paket_*_learning.json')):
        with open(fp, 'r', encoding='utf-8') as f:
            json.load(f)
        n += 1
    print('validasi JSON OK:', n, 'file')


if __name__ == '__main__':
    main()
