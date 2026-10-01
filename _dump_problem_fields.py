# -*- coding: utf-8 -*-
"""_dump_problem_fields.py — tampilkan nilai lengkap field bermasalah."""
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"

print("=== FISIKA P2 soal10 diketahui ===")
f = json.load(open(DATA + r"\fisika_paket_2_learning.json", encoding="utf-8"))
print(f["soal"][10]["pembahasan"]["diketahui"])
print()
print("=== FISIKA P2 soal14 diketahui ===")
print(f["soal"][14]["pembahasan"]["diketahui"])
print()
print("=== MTK P1 soal5 stimulus.text ===")
m = json.load(open(DATA + r"\matematika_paket_1_learning.json", encoding="utf-8"))
print(m["soal"][5]["stimulus"]["text"])
print()
print("=== CANON MTK P1 q5 stimulus_text ===")
c = json.load(open(DATA + r"\canonical_questions\matematika_paket_1.json", encoding="utf-8"))
for q in c["questions"]:
    if q.get("id") in (5, "5") or "Rina" in json.dumps(q)[:2000]:
        print(q.get("stimulus_text", "")[:800])
        print("---- diagrams[0].description:")
        for dgm in (q.get("visual_context") or {}).get("diagrams") or []:
            print(dgm.get("description", "")[:600])
        break
print()
print("=== BI P2 soal8 soal_serupa pilihan (all) ===")
b = json.load(open(DATA + r"\bahasa_indonesia_paket_2_learning.json", encoding="utf-8"))
ss = b["soal"][8]["soal_serupa"]
for p in ss["pilihan"]:
    print(repr(p.get("text", ""))[:300])
print("pertanyaan:", repr(ss.get("pertanyaan", ""))[:300])
print("pembahasan_singkat:", repr(ss.get("pembahasan_singkat", ""))[:400])
print()
print("=== BI P2 SOLUTIONS italic_h fields ===")
s = json.load(open(DATA + r"\solution_sources\BAHASA_INDONESIA_PAKET_2_SOLUTIONS.json", encoding="utf-8"))
for sol in s["solutions"]:
    for fld in ("diketahui", "reasoning", "why_correct"):
        v = sol.get(fld) or ""
        if "\u210e" in v:
            print(f"q{sol.get('question_number')} {fld}:", repr(v[:300]))
    for st in sol.get("steps") or []:
        v = st.get("explanation") or ""
        if "\u210e" in v:
            print(f"q{sol.get('question_number')} steps/explanation:", repr(v[:300]))
    for t in sol.get("tips") or []:
        if "\u210e" in t:
            print(f"q{sol.get('question_number')} tips:", repr(t[:300]))
