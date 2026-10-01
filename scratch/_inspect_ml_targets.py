import json

def inspect_ml(pkg, numbers):
    with open(f'data/matematika_lanjut_paket_{pkg}_learning.json', encoding='utf-8') as f:
        d = json.load(f)
    for q in d.get('soal', []):
        no = q.get('nomor')
        if no in numbers:
            print(f"=== MAT LANJUT P{pkg} Q{no} ===")
            print("Type:", q.get('tipe_soal'))
            stim = q.get('stimulus') or {}
            pert = q.get('pertanyaan') or {}
            print("Stim text:", repr(stim.get('text', ''))[:100])
            print("Stim html:", stim.get('html', '')[:200])
            print("Pert text:", repr(pert.get('text', ''))[:100])
            print("Pert html:", pert.get('html', '')[:200])
            opts = q.get('pilihan_jawaban') or q.get('opsi') or []
            print("Opts count:", len(opts))
            for o in opts[:3]:
                print("  Opt sample:", o)

print("--- P1 ---")
inspect_ml(1, [11, 16, 17])
print("--- P2 ---")
inspect_ml(2, [1, 8, 12, 14, 22, 25])
