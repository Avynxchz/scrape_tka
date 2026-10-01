import json
import re

def strip_transcription(text):
    if not text:
        return text
    # Matches [Diagram ..., [Formula ..., [VISUAL ..., [Table ... until the end of string or until normal text
    return re.sub(r"\n?\[(?:Diagram|VISUAL_INFORMATION_UNRESOLVED|Formula|Table)[\s\S]*$", "", text).strip()

ldoc = json.load(open("data/matematika_paket_2_learning.json", encoding="utf-8"))
for q in ldoc["soal"]:
    st = q.get("stimulus", {}).get("text") or ""
    cleaned = strip_transcription(st)
    if any(k in st for k in ["Diagram", "VISUAL", "Formula", "soal_18"]):
        print(f"Q{q.get('nomor'):02d}:")
        print("  CLEAN:", repr(cleaned))
