# -*- coding: utf-8 -*-
"""_dump_bi_q13.py — teks soal BI P2 q13 (fakta 30,96)."""
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

b = json.load(open(r"D:\PROJECTS\SCRAPE_TKA\data\bahasa_indonesia_paket_2_learning.json", encoding="utf-8"))
for s in b["soal"]:
    blob = json.dumps(s, ensure_ascii=False)
    if "30,96" in blob:
        print("NOMOR:", s["nomor"])
        print("STIMULUS:", (s.get("stimulus") or {}).get("text", "")[:1200])
        print()
        print("PERTANYAAN:", (s.get("pertanyaan") or {}).get("text", "")[:400])
