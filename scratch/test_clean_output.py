import json, re

def format_pusmendik_html(raw_html, pkg_path):
    if not raw_html:
        return ''
    html = re.sub(r'<!--[\s\S]*?-->', '', raw_html).strip()
    m = re.match(r'^<div\s+class=["\']col-lg-6[^"\']*["\'][^>]*>([\s\S]*)</div>$', html, re.IGNORECASE)
    if m:
        html = m.group(1).strip()
    
    def repl_src(match):
        p1 = match.group(1).lstrip('./')
        return f'src="{pkg_path}{p1}"'
        
    html = re.sub(r'src=["\'](\.?/?images/[^"\']+)["\']', repl_src, html)
    return html

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for no in [1, 4, 8, 13, 17, 20, 25]:
    q = d['soal'][no-1]
    print(f"=== SOAL {no} ===")
    print("STIMULUS CLEANED:")
    print(format_pusmendik_html(q['stimulus'].get('html'), 'data/paket_2/'))
    print("PERTANYAAN CLEANED:")
    print(format_pusmendik_html(q['pertanyaan'].get('html'), 'data/paket_2/'))
    print()
