import json, re

d = json.load(open('data/matematika_paket_2_learning.json', encoding='utf-8'))
for q in d['soal']:
    no = q['nomor']
    s_h = q.get('stimulus', {}).get('html', '')
    p_h = q.get('pertanyaan', {}).get('html', '')
    s_imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', s_h)
    p_imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', p_h)
    print(f"Q{no:02d}: stim_imgs={s_imgs} | pert_imgs={p_imgs}")
