import json, sys, re

sys.stdout.reconfigure(encoding='utf-8')

# Simulate what build_solution_payload does for diketahui/ditanyakan
d = json.load(open('data/paket_2/matematika_paket_2.json', encoding='utf-8'))

for q in d['soal']:
    no = q['nomor']
    stim = (q.get('stimulus', {}).get('text') or '').strip()
    q_txt = (q.get('pertanyaan', {}).get('text') or '').strip()
    stim_clean = re.sub(r'[\r\n]+', ' ', stim).strip()
    q_clean = re.sub(r'[\r\n]+', ' ', q_txt).strip()
    
    diketahui = stim_clean if stim_clean else q_clean
    ditanyakan = q_clean if stim_clean else "Menyederhanakan dan menentukan nilai akhir yang ekuivalen."
    
    print(f"=== Q{no:02d} ===")
    print(f"  DIK: {diketahui[:200]}")
    print(f"  DIT: {ditanyakan[:200]}")
    print()
