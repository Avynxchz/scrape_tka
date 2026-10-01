# -*- coding: utf-8 -*-
"""_debug_mtk39.py — kenapa soal 39 text belum terganti."""
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

d = json.load(open(r"D:\PROJECTS\SCRAPE_TKA\data\matematika_paket_1_learning.json", encoding="utf-8"))
# temukan SEMUA soal yang mengandung italic di pertanyaan/text
for i, q in enumerate(d["soal"]):
    t = (q.get("pertanyaan") or {}).get("text") or ""
    if re.search(r"[\U0001D400-\U0001D7FF]", t):
        print(f"idx {i} nomor {q['nomor']}: {t[:100]!r}")
        print("  codepoints:", [hex(ord(c)) for c in t if ord(c) > 0xFFFF][:10])
