import json

def inspect_ml_full():
    for pkg in [1, 2]:
        with open(f'data/matematika_lanjut_paket_{pkg}_learning.json', encoding='utf-8') as f:
            d = json.load(f)
        nums = [11, 16, 17] if pkg == 1 else [1, 8, 12, 14, 22, 25]
        for q in d.get('soal', []):
            if q.get('nomor') in nums:
                no = q.get('nomor')
                print(f"=== MAT LANJUT P{pkg} Q{no} ===")
                stim = q.get('stimulus') or {}
                pert = q.get('pertanyaan') or {}
                print("STIM HTML:", repr(stim.get('html'))[:200])
                print("PERT HTML:", repr(pert.get('html'))[:200])
                opts = q.get('pilihan_jawaban') or q.get('opsi') or []
                print("OPTS COUNT:", len(opts))
                for o in opts[:3]:
                    print("  OPT:", o.get('key'), "image:", o.get('image'), "html:", repr(o.get('html'))[:100])
                stmts = q.get('pernyataan') or []
                for s in stmts[:3]:
                    print("  STMT:", s.get('key'), s.get('text'), s.get('image'))

inspect_ml_full()
