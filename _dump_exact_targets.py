# -*- coding: utf-8 -*-
"""_dump_exact_targets.py — nilai persis field yang akan diperbaiki."""
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"

m = json.load(open(DATA + r"\matematika_lanjut_paket_1_learning.json", encoding="utf-8"))
s = m["soal"][12]
print("=== MLANJUT P1 soal/12 (nomor", s["nomor"], ") ===")
for p in s.get("pilihan_jawaban", []):
    print(json.dumps(p, ensure_ascii=False)[:220])

print()
s = json.load(open(DATA + r"\solution_sources\BAHASA_INDONESIA_PAKET_2_SOLUTIONS.json", encoding="utf-8"))
sol = s["solutions"][12]
print("=== BI P2 SOLUTIONS solutions[12] diketahui (EXACT) ===")
print(repr(sol["diketahui"]))
print()
print("=== solutions[12] steps[2] explanation (EXACT) ===")
print(repr(sol["steps"][2]["explanation"]))
print()
sol = s["solutions"][8]
print("=== solutions[8] steps[2] explanation (EXACT) ===")
print(repr(sol["steps"][2]["explanation"]))
print()
sol = s["solutions"][15]
print("=== solutions[15] tips[0] (EXACT) ===")
print(repr(sol["tips"][0]))
print()
x = json.load(open(DATA + r"\solution_sources\MTK_PAKET_2_SOLUTIONS_EXTRA.json", encoding="utf-8"))
sol = x["solutions"][17]
print("=== MTK P2 EXTRA solutions[17] diketahui (EXACT) ===")
print(repr(sol["diketahui"]))
