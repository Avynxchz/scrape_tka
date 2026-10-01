import json, os
from PIL import Image

def analyze_target(subj, pkt, num, desc):
    fn = f'data/{subj}_paket_{pkt}_learning.json'
    with open(fn, encoding='utf-8') as f:
        d = json.load(f)
    q = [x for x in d['soal'] if x['nomor'] == num][0]
    print(f"\n==================== {subj.upper()} P{pkt} Q{num} ({desc}) ====================")
    img_dir = f'data/{subj}/paket_{pkt}/images'
    
    # Stimulus
    print("[STIMULUS]")
    stim_html = (q.get('stimulus') or {}).get('html') or ''
    print("  HTML snippet:", stim_html[:150])
    for im in (q.get('stimulus') or {}).get('images', []):
        fname = im.get('filename') or os.path.basename(im.get('rel_path',''))
        p = os.path.join(img_dir, fname)
        if os.path.exists(p):
            with Image.open(p) as img:
                print(f"  Stimulus img: {fname} size={img.size}")
        else:
            print(f"  Stimulus img {fname} NOT FOUND at {p}")
            
    # Pertanyaan
    print("[PERTANYAAN]")
    pert_html = (q.get('pertanyaan') or {}).get('html') or ''
    print("  HTML snippet:", pert_html[:150])
    for im in (q.get('pertanyaan') or {}).get('images', []):
        fname = im.get('filename') or os.path.basename(im.get('rel_path',''))
        p = os.path.join(img_dir, fname)
        if os.path.exists(p):
            with Image.open(p) as img:
                print(f"  Pertanyaan img: {fname} size={img.size}")
        else:
            print(f"  Pertanyaan img {fname} NOT FOUND at {p}")

    # Pilihan
    print("[OPTIONS]")
    for opt in q.get('pilihan_jawaban', []):
        k = opt['key']
        h = opt.get('html') or ''
        im = opt.get('image') or {}
        fname = im.get('filename') or (os.path.basename(im.get('rel_path','')) if im else '')
        size = None
        if fname:
            p = os.path.join(img_dir, fname)
            if os.path.exists(p):
                with Image.open(p) as img: size = img.size
        print(f"  Option {k}: text={opt.get('text')} | img={fname} size={size} | html={h[:100]}")

analyze_target('matematika', 1, 9, "Kecilin gambar di soal & pertanyaan dikit")
analyze_target('matematika', 1, 11, "Kecilin gambar OPSI JAWABAN dikit")
analyze_target('matematika', 1, 19, "Besarin gambar OPSI JAWABAN dikit")
analyze_target('matematika', 2, 8, "Besarin gambar OPSI JAWABAN (A-E) dikit")

# MTL P1
analyze_target('matematika_lanjut', 1, 16, "Kecilin gambar OPSI A")
analyze_target('matematika_lanjut', 1, 18, "Kecilin gambar OPSI (sedang saja)")
analyze_target('matematika_lanjut', 1, 20, "Kecilin gambar OPSI (sedang saja)")

# MTL P2
analyze_target('matematika_lanjut', 2, 1, "Besarkan gambar OPSI dikit agar jelas")
analyze_target('matematika_lanjut', 2, 4, "Kecilkan gambar OPSI dikit")
analyze_target('matematika_lanjut', 2, 16, "Perkecil gambar OPSI (A-E)")
analyze_target('matematika_lanjut', 2, 21, "Kecilkan gambar OPSI A, B, C sama kayak D & E")
analyze_target('matematika_lanjut', 2, 23, "Besarkan gambar PERTANYAAN dikit")
analyze_target('matematika_lanjut', 2, 25, "Besarkan gambar PERTANYAAN dikit")
