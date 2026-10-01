import json, os
from PIL import Image

data = json.load(open('data/bahasa_arab_paket_1_learning.json', encoding='utf-8'))
print("=== BAHASA ARAB PAKET 1 IMAGES INVENTORY ===")
for q in data['soal']:
    no = q['nomor']
    print(f"\n--- Soal No {no} ---")
    
    # Stimulus images
    stim_h = (q.get('stimulus') or {}).get('html', '')
    import re
    stim_imgs = re.findall(r'src=["\']([^"\']+)["\']', stim_h)
    for src in stim_imgs:
        fname = src.split('/')[-1]
        fpath = os.path.join('data/bahasa_arab/paket_1/images', fname)
        size = Image.open(fpath).size if os.path.exists(fpath) else 'NOT FOUND'
        print(f"  Stimulus img: {fname} size={size}")
        
    # Pertanyaan images
    pert_h = (q.get('pertanyaan') or {}).get('html', '')
    pert_imgs = re.findall(r'src=["\']([^"\']+)["\']', pert_h)
    for src in pert_imgs:
        fname = src.split('/')[-1]
        fpath = os.path.join('data/bahasa_arab/paket_1/images', fname)
        size = Image.open(fpath).size if os.path.exists(fpath) else 'NOT FOUND'
        print(f"  Pertanyaan img: {fname} size={size}")
        
    # Option images
    for o in q.get('pilihan_jawaban', []):
        if o.get('image'):
            fname = o['image']['filename']
            fpath = os.path.join('data/bahasa_arab/paket_1/images', fname)
            size = Image.open(fpath).size if os.path.exists(fpath) else 'NOT FOUND'
            print(f"  Opt {o.get('key')} img: {fname} size={size}")
