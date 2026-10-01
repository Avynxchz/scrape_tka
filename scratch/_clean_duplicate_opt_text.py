import glob
import json
import re

for slug in ["matematika_paket_1", "matematika_paket_2", "matematika_lanjut_paket_1", "matematika_lanjut_paket_2"]:
    path = f"data/{slug}_learning.json"
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
        
    cleaned = 0
    for q in d["soal"]:
        for opt in q.get("pilihan_jawaban", []):
            # If option has image, and text is pure latex formula, clear text
            if opt.get("image"):
                t = (opt.get("text") or "").strip()
                l = (opt.get("latex") or "").strip()
                if t and (t == f"${l}$" or (t.startswith("$") and t.endswith("$") and not re.sub(r"\$[^$]+\$", "", t).strip())):
                    opt["text"] = ""
                    cleaned += 1
                    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"{slug}: cleaned {cleaned} options where pure formula text duplicated the image.")
