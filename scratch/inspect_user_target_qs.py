import json

def inspect_q(subj, pkt, num):
    fn = f'data/{subj}_paket_{pkt}_learning.json'
    with open(fn, encoding='utf-8') as f:
        d = json.load(f)
    q = [x for x in d['soal'] if x['nomor'] == num]
    if not q:
        print(f'{subj} P{pkt} Q{num}: NOT FOUND')
        return
    q = q[0]
    print(f'=== {subj} P{pkt} Q{num} ===')
    stim_img = [im.get('rel_path') or im.get('filename') for im in (q.get('stimulus',{}) or {}).get('images',[])]
    print('Stimulus images:', stim_img)
    pert_img = [im.get('rel_path') or im.get('filename') for im in (q.get('pertanyaan',{}) or {}).get('images',[])]
    print('Pertanyaan images:', pert_img)
    opt_imgs = []
    for opt in q.get('pilihan_jawaban', []):
        im = opt.get('image') or {}
        h = opt.get('html') or ''
        has_img = '<img' in h
        opt_imgs.append((opt.get('key'), im.get('rel_path') or im.get('filename'), has_img, h[:80] if has_img else ''))
    print('Options with images/html:')
    for k, p, has_img, h_snippet in opt_imgs:
        if p or has_img:
            print(f'  {k}: img={p}, has_img={has_img}, snippet={h_snippet}')

print("--- MAT WAJIB P1 ---")
inspect_q('matematika', 1, 9)
inspect_q('matematika', 1, 11)
inspect_q('matematika', 1, 19)

print("\n--- MAT WAJIB P2 ---")
inspect_q('matematika', 2, 8)

print("\n--- MAT LANJUT P1 ---")
with open('data/matematika_lanjut_paket_1_learning.json', encoding='utf-8') as f:
    d = json.load(f)
for q in d['soal']:
    opts_with_imgs = [opt['key'] for opt in q.get('pilihan_jawaban',[]) if opt.get('image') or ('<img' in (opt.get('html') or ''))]
    if opts_with_imgs:
        print(f'MTL P1 Q{q["nomor"]} has option images in: {opts_with_imgs}')

inspect_q('matematika_lanjut', 1, 11)
inspect_q('matematika_lanjut', 1, 16)
inspect_q('matematika_lanjut', 1, 17)
inspect_q('matematika_lanjut', 1, 18)
inspect_q('matematika_lanjut', 1, 20)

print("\n--- MAT LANJUT P2 ---")
inspect_q('matematika_lanjut', 2, 1)
inspect_q('matematika_lanjut', 2, 4)
inspect_q('matematika_lanjut', 2, 16)
inspect_q('matematika_lanjut', 2, 21)
inspect_q('matematika_lanjut', 2, 23)
inspect_q('matematika_lanjut', 2, 25)
