# -*- coding: utf-8 -*-
"""_check_odd_dollars.py — detail semua field aktif dengan jumlah $ ganjil."""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"


def walk(o, p=""):
    if isinstance(o, str):
        if o.count("$") % 2 == 1:
            print(f"  {p}: ($ x{o.count('$')})")
            print("   ", repr(o[:400]))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f"{p}/{i}")
    elif isinstance(o, dict):
        for k, v in o.items():
            walk(v, f"{p}/{k}")


targets = [
    "fisika_paket_2_learning.json",
    "matematika_paket_1_learning.json",
    "matematika_paket_2_learning.json",
    "matematika_lanjut_paket_1_learning.json",
    "matematika_lanjut_paket_2_learning.json",
    "kimia_paket_1_learning.json",
    "kimia_paket_2_learning.json",
    "canonical_questions\\matematika_paket_1.json",
    "canonical_questions\\matematika_paket_2.json",
    "solution_sources\\MTK_PAKET_2_SOLUTIONS_EXTRA.json",
]
for rel in targets:
    path = os.path.join(DATA, rel)
    if not os.path.isfile(path):
        continue
    print(f"\n===== {rel} =====")
    d = json.load(open(path, encoding="utf-8"))
    walk(d, rel.split("\\")[0].replace(".json", ""))
