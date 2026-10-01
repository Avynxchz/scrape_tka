import json

for sub in ['bahasa_inggris', 'bahasa_inggris_lanjut']:
    path = f'data/{sub}_paket_2_learning.json'
    try:
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        for q in d['soal']:
            no = q['nomor']
            opts = q.get('pilihan_jawaban') or q.get('opsi', [])
            has_img = any(o.get('image') or '<img' in str(o.get('html', '')) for o in opts)
            if has_img:
                print(f"{sub} P2 Q{no} has image in options!")
                for o in opts:
                    if o.get('image') or '<img' in str(o.get('html', '')):
                        print(f"  Opt {o.get('key')}: img={o.get('image')} html={repr(o.get('html'))}")
    except Exception as e:
        print(sub, e)
