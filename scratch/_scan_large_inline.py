import os, json, re

large_inline = []

for f in sorted(os.listdir('data')):
    if f.endswith('_learning.json'):
        path = os.path.join('data', f)
        data = json.load(open(path, encoding='utf-8'))
        subject = f.replace('_learning.json', '')
        for q in data.get('soal', []):
            stim_html = (q.get('stimulus') or {}).get('html', '')
            pert_html = (q.get('pertanyaan') or {}).get('html', '')
            for html_type, h in [('stimulus', stim_html), ('pertanyaan', pert_html)]:
                if not h: continue
                # find paragraphs containing img
                p_blocks = re.findall(r'<p[^>]*>([\s\S]*?)</p>', h)
                for p in p_blocks:
                    if '<img' in p:
                        # strip tags to get real text
                        txt = re.sub(r'<[^>]+>', '', p).strip()
                        if txt: # there is text!
                            imgs = re.findall(r'<img[^>]+>', p)
                            for im in imgs:
                                if 'width=' not in im and 'height=' not in im and 'data-latex' not in im:
                                    src_m = re.search(r'src=["\']([^"\']+)["\']', im)
                                    src = src_m.group(1) if src_m else ''
                                    large_inline.append((subject, q.get('nomor'), html_type, src))

print(f"Total candidates: {len(large_inline)}")
for item in large_inline:
    print(item)
