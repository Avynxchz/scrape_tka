import json

def inspect_questions(pkg, numbers):
    with open(f'data/matematika_paket_{pkg}_learning.json', encoding='utf-8') as f:
        d = json.load(f)
    for q in d.get('soal', []):
        no = q.get('nomor')
        if no in numbers:
            print(f'=== P{pkg} No {no} ===')
            print('Type:', q.get('tipe_soal'))
            stim = q.get('stimulus')
            print('Stimulus type:', type(stim))
            if isinstance(stim, str):
                print('Stimulus:', stim[:150])
            elif isinstance(stim, dict):
                print('Stimulus dict keys:', stim.keys())
            elif isinstance(stim, list):
                print('Stimulus list len:', len(stim))
            pert = q.get('pertanyaan')
            print('Pertanyaan:', str(pert)[:150])
            print('Gambar stimulus:', q.get('gambar_stimulus'))
            opts = q.get('opsi', [])
            print('Opsi count:', len(opts))
            if opts and isinstance(opts[0], dict):
                print('Opsi keys:', opts[0].keys())
                for o in opts:
                    if o.get('gambar'):
                        print('  Opt img:', o.get('label'), o.get('gambar'))
                    elif o.get('html'):
                        print('  Opt html:', o.get('label'), str(o.get('html'))[:80])

print('--- P1 ---')
inspect_questions(1, [5, 7, 8, 12, 15, 43])
print('--- P2 ---')
inspect_questions(2, [2, 3, 8, 14])
