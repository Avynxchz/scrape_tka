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

def has_visible_stimulus_content(html_str):
    if not html_str:
        return False
    if re.search(r'<img\b', html_str, re.IGNORECASE):
        return True
    text = re.sub(r'<!--[\s\S]*?-->', '', html_str)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('\u00a0', ' ').strip()
    return len(text) > 0

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for q in d['soal']:
    no = q['nomor']
    stim_html = q.get('stimulus', {}).get('html', '')
    pert_html = q.get('pertanyaan', {}).get('html', '')
    
    has_stim = has_visible_stimulus_content(stim_html)
    rendered_stim = format_pusmendik_html(stim_html, 'data/paket_2/') if has_stim else '(NO STIMULUS)'
    rendered_pert = format_pusmendik_html(pert_html, 'data/paket_2/')
    
    # Check for any AI vision / transcription markers in the rendered output
    ai_markers = ['[Diagram', 'VISUAL_INFORMATION', '[Formula', '[Table', '[Graph']
    stim_has_ai = any(m in rendered_stim for m in ai_markers)
    pert_has_ai = any(m in rendered_pert for m in ai_markers)
    
    # Count images in rendered output
    stim_imgs = len(re.findall(r'<img\b', rendered_stim))
    pert_imgs = len(re.findall(r'<img\b', rendered_pert))
    
    print(f"Q{no:02d} [{q.get('tipe_soal')}]: has_stim={has_stim} (imgs={stim_imgs}), pert_imgs={pert_imgs} | AI tags: stim={stim_has_ai}, pert={pert_has_ai}")
    if stim_has_ai or pert_has_ai:
        print(f"  WARNING: AI tags found in Q{no}!")
