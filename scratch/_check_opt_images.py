import json

for pkg in [1, 2]:
    with open(f"data/matematika_lanjut_paket_{pkg}_learning.json", encoding="utf-8") as f:
        d = json.load(f)
    print(f"\n=== MTK LANJUT PAKET {pkg} OPTIONS WITH IMAGES OR SPECIAL STRUCTURE ===")
    for q in d["soal"]:
        opts = q.get("pilihan_jawaban", [])
        for o in opts:
            if o.get("image") or (o.get("text") and o.get("latex")):
                print(f"Q{q['nomor']} [{o.get('key')}]: text='{o.get('text')}', latex='{o.get('latex')}', img={o.get('image')}")
