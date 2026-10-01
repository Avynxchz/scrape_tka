import json, re

with open('data/kimia_paket_1_learning.json', encoding='utf-8') as f:
    d = json.load(f)

q2 = [s for s in d['soal'] if s['nomor'] == 2][0]
print('Original stimulus HTML:')
print(repr(q2['stimulus']['html']))

rawHtml = q2['stimulus']['html']
pkgPath = 'data/kimia/paket_1/'

html = re.sub(r'<!--[\s\S]*?-->', '', rawHtml).strip()
wrapperMatch = re.match(r'^<div\s+class=["\']col-lg-6[^"\']*["\'][^>]*>([\s\S]*)</div>$', html, re.I)
if wrapperMatch:
    html = wrapperMatch.group(1).strip()

def repl(m):
    p1 = m.group(1)
    parts = p1.split('/')
    fname = parts[-1].split('?')[0]
    base = pkgPath if pkgPath.endswith('/') else pkgPath + '/'
    return f'src="{base}images/{fname}"'

res = re.sub(r'src=["\']([^"\']+\.(?:png|jpe?g|gif|webp|svg))(?:\?[^"\']*)?["\']', repl, html, flags=re.I)
print('\nProcessed HTML:')
print(res)
