import json, os

with open('data/biologi_paket_2_learning.json', encoding='utf-8') as f:
    d = json.load(f)

img_dir = 'data/biologi/paket_2/images'
for q in d['soal']:
    if q['nomor'] in [3, 4, 5, 7, 9, 16, 17, 19, 20, 25, 28]:
        stim_imgs = [i.get('filename') or i.get('rel_path') for i in (q.get('stimulus') or {}).get('images', [])]
        print(f"Q{q['nomor']}: stim_imgs={stim_imgs}")
        for im in stim_imgs:
            p = os.path.join(img_dir, os.path.basename(im))
            print(f"  {im} exists={os.path.exists(p)} size={os.path.getsize(p) if os.path.exists(p) else 0}")
