import json, re

def check_has_stimulus(html_str):
    if not html_str:
        return False
    # Check if contains any <img tag
    if re.search(r'<img\b', html_str, re.IGNORECASE):
        return True
    # Strip comments and tags
    clean = re.sub(r'<!--[\s\S]*?-->', '', html_str)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = clean.replace('&nbsp;', ' ').replace('\u00a0', ' ').strip()
    return len(clean) > 0

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for q in d['soal']:
    no = q['nomor']
    s_html = q.get('stimulus', {}).get('html', '')
    has_s = check_has_stimulus(s_html)
    print(f"Q{no:02d}: has_stimulus={has_s}")
