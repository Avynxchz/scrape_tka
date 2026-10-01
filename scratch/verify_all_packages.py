import json, glob, re, os

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

def has_visible_stimulus_content(html_str):
    if not html_str:
        return False
    if re.search(r'<img\b', html_str, re.IGNORECASE):
        return True
    text = re.sub(r'<!--[\s\S]*?-->', '', html_str)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('\u00a0', ' ').strip()
    return len(text) > 0

files = glob.glob('data/*_learning.json')
total_q = 0
ai_leakage = 0
missing_html = 0

for f in files:
    d = json.load(open(f, encoding='utf-8'))
    for q in d.get('soal', []):
        total_q += 1
        s_h = q.get('stimulus', {}).get('html', '')
        p_h = q.get('pertanyaan', {}).get('html', '')
        if not s_h and not p_h:
            missing_html += 1
        
        r_s = format_pusmendik_html(s_h, '')
        r_p = format_pusmendik_html(p_h, '')
        
        for marker in ['[Diagram', 'VISUAL_INFORMATION', '[Formula', '[Table', '[Graph']:
            if marker in r_s or marker in r_p:
                ai_leakage += 1
                print(f"Leakage in {os.path.basename(f)} Q{q.get('nomor')}: {marker}")

print(f"Total Questions: {total_q}")
print(f"Missing HTML: {missing_html}")
print(f"AI Leakage: {ai_leakage}")
