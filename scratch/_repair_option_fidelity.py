import json
import os
import re
from bs4 import BeautifulSoup

def repair_mtkl_p1():
    path = "data/matematika_lanjut_paket_1_learning.json"
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    
    # Q7 in MTKL P1
    for q in d["soal"]:
        if q["nomor"] == 7:
            for opt in q["pilihan_jawaban"]:
                k = opt["key"]
                if k == "C":
                    opt["text"] = "Jarak pusat lingkaran dengan sumbu-$x$ adalah 3."
                    opt["full_display"] = "C. Jarak pusat lingkaran dengan sumbu-$x$ adalah 3."
                elif k == "D":
                    opt["text"] = "Jarak pusat lingkaran dengan sumbu-$y$ adalah 1."
                    opt["full_display"] = "D. Jarak pusat lingkaran dengan sumbu-$y$ adalah 1."
                elif k == "E":
                    opt["text"] = "Garis $y=0$ memotong lingkaran di dua titik."
                    opt["full_display"] = "E. Garis $y=0$ memotong lingkaran di dua titik."
                    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("MTKL P1 Q7 inline latex repaired.")

def repair_mtkl_p2():
    path = "data/matematika_lanjut_paket_2_learning.json"
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
        
    # Q21 in MTKL P2
    for q in d["soal"]:
        if q["nomor"] == 21:
            for opt in q["pilihan_jawaban"]:
                opt["image_first"] = True
                opt["image_position"] = "before"
                # also update full_display to indicate image first
                opt["full_display"] = f"{opt['key']}. [Gambar Pusat] {opt['text']}"
                
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("MTKL P2 Q21 image-first order repaired.")

def repair_pure_latex_options(slug):
    path = f"data/{slug}_learning.json"
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
        
    count = 0
    for q in d["soal"]:
        for opt in q.get("pilihan_jawaban", []):
            latex = opt.get("latex")
            text = (opt.get("text") or "").strip()
            full_d = (opt.get("full_display") or "").strip()
            # If text is empty or full_display has no formula
            if latex and (not text or re.match(r"^[A-E][.\)]\s*$", full_d)):
                opt["text"] = f"${latex}$"
                opt["full_display"] = f"{opt['key']}. ${latex}$"
                count += 1
                
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print(f"{slug}: repaired {count} pure LaTeX option displays.")

if __name__ == "__main__":
    repair_mtkl_p1()
    repair_mtkl_p2()
    repair_pure_latex_options("matematika_paket_1")
    repair_pure_latex_options("matematika_paket_2")
    repair_pure_latex_options("matematika_lanjut_paket_1")
    repair_pure_latex_options("matematika_lanjut_paket_2")
