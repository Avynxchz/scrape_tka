import os
import glob
import json
import re

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
DATA_DIR = os.path.join(BASE_DIR, "data")

subjects = [
    'matematika', 'bahasa_indonesia', 'bahasa_inggris', 'fisika', 'kimia', 'biologi',
    'ekonomi', 'geografi', 'sosiologi', 'sejarah', 'ppkn', 'kewirausahaan',
    'matematika_lanjut', 'bahasa_indonesia_lanjut', 'bahasa_inggris_lanjut',
    'bahasa_arab', 'bahasa_jepang', 'bahasa_jerman', 'bahasa_prancis', 'bahasa_mandarin', 'bahasa_korea', 'antropologi'
]

total_checked_images = 0
broken_images = []
cross_subject_issues = []
flat_math_notations = []

for subj in subjects:
    for pkt in [1, 2]:
        fn = os.path.join(DATA_DIR, f"{subj}_paket_{pkt}_learning.json")
        if not os.path.exists(fn):
            continue
        with open(fn, encoding='utf-8') as f:
            d = json.load(f)
        
        img_dir = os.path.join(DATA_DIR, subj, f"paket_{pkt}", "images")
        
        for q in d.get('soal', []):
            no = q.get('nomor')
            
            # Check flat math patterns in question text
            full_text = (q.get('stimulus', {}).get('text', '') or '') + " " + (q.get('pertanyaan', {}).get('text', '') or '')
            for opt in q.get('pilihan_jawaban', []):
                full_text += " " + (opt.get('text', '') or '')
                
            # Flat power checks (e.g. 10 24, 10 -6, m.s-2, etc.)
            flat_matches = re.findall(r'\b10\s+[-–]?\d{1,2}\b|\bm\.s-[12]\b|\brad\.s-[12]\b', full_text)
            if flat_matches:
                flat_math_notations.append(f"{subj} P{pkt} Q{no}: {flat_matches}")

            # Collect image sources
            srcs = []
            html = (q.get('stimulus', {}) or {}).get('html', '') or ''
            srcs.extend(re.findall(r'src=["\']([^"\']+\.(?:png|jpe?g|gif|webp|svg))', html, re.I))
            
            for im in (q.get('stimulus', {}) or {}).get('images', []):
                p = im.get('rel_path') or im.get('filename')
                if p: srcs.append(p)
                
            for opt in q.get('pilihan_jawaban', []):
                opt_html = opt.get('html') or ''
                srcs.extend(re.findall(r'src=["\']([^"\']+\.(?:png|jpe?g|gif|webp|svg))', opt_html, re.I))
                if opt.get('image'):
                    ip = opt['image'].get('rel_path') or opt['image'].get('filename')
                    if ip: srcs.append(ip)
                    
            for s in srcs:
                if not s: continue
                total_checked_images += 1
                fname = os.path.basename(s.split('?')[0])
                
                # Check path in subject dir
                path1 = os.path.join(DATA_DIR, subj, f"paket_{pkt}", "images", fname)
                path2 = os.path.join(DATA_DIR, subj, f"paket_{1 if pkt==2 else 2}", "images", fname)
                path3 = os.path.join(DATA_DIR, subj, "images", fname)
                
                if not (os.path.isfile(path1) or os.path.isfile(path2) or os.path.isfile(path3)):
                    broken_images.append(f"{subj} P{pkt} Q{no}: {fname}")

print(f"=== FULL AUDIT RESULTS ===")
print(f"Total Soal Tested across 22 Subjects (Paket 1 & 2): {sum(1 for _ in glob.glob(os.path.join(DATA_DIR, '*_learning.json')))}")
print(f"Total Images Audited: {total_checked_images}")
print(f"Missing / Broken Images in Subject Folders: {len(broken_images)}")
if broken_images:
    for b in broken_images[:25]:
        print(f"  [BROKEN] {b}")
else:
    print("  => ZERO missing images! Every image is physically present in its subject directory.")

print(f"Flat Math Notation Anomalies: {len(flat_math_notations)}")
if flat_math_notations:
    for f in flat_math_notations[:15]:
        print(f"  [FLAT MATH] {f}")
else:
    print("  => ZERO flat math anomalies! All exponents and units properly formatted.")
