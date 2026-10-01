import json
import re

cdoc = json.load(open("data/canonical_questions/matematika_paket_2.json", encoding="utf-8"))
for q in cdoc["questions"]:
    st = q.get("stimulus_text") or ""
    tags = re.findall(r"\[(?:Diagram|VISUAL_INFORMATION_UNRESOLVED|Formula|Table)[^\]]*\](?::\s*[^\n]*)?", st)
    if tags:
        print(f"Q{q['question_number']:02d}: found {len(tags)} tag(s):")
        for t in tags:
            print("   ", t[:80] + "...")

ldoc = json.load(open("data/matematika_paket_2_learning.json", encoding="utf-8"))
for q in ldoc["soal"]:
    st = q.get("stimulus", {}).get("text") or ""
    tags = re.findall(r"\[(?:Diagram|VISUAL_INFORMATION_UNRESOLVED|Formula|Table)[^\]]*\](?::\s*[^\n]*)?", st)
    if tags:
        print(f"Learning Q{q.get('nomor', 0):02d}: found {len(tags)} tag(s)")
