import json

def inspect(pkg, numbers):
    with open(f'data/matematika_paket_{pkg}_learning.json', encoding='utf-8') as f:
        d = json.load(f)
    for q in d.get('soal', []):
        no = q.get('nomor')
        if no in numbers:
            print(f"==================== P{pkg} No {no} ====================")
            stim = q.get('stimulus') or {}
            pert = q.get('pertanyaan') or {}
            print("Stimulus Text:", repr(stim.get('text', ''))[:100])
            print("Stimulus Images:", stim.get('images'))
            print("Stimulus HTML:", stim.get('html', ''))
            print("Pertanyaan Text:", repr(pert.get('text', ''))[:100])
            print("Pertanyaan HTML:", pert.get('html', ''))
            pilihan = q.get('pilihan_jawaban', [])
            for p in pilihan:
                print("  Opt:", p.get('key'), "text:", repr(p.get('text')), "latex:", p.get('latex'), "image:", p.get('image'), "html:", p.get('html'))
            pernyataan = q.get('pernyataan', [])
            for p in pernyataan:
                print("  Pernyataan:", p)

print("MATEMATIKA P1")
inspect(1, [5, 7, 8, 12, 15, 43])
print("\nMATEMATIKA P2")
inspect(2, [2, 3, 8, 14])
