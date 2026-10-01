# -*- coding: utf-8 -*-
"""_dump_fisika_context.py — konteks soal fisika P2 nomor 10 & 14."""
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

f = json.load(open(r"D:\PROJECTS\SCRAPE_TKA\data\fisika_paket_2_learning.json", encoding="utf-8"))
for idx in (10, 14):
    s = f["soal"][idx]
    print(f"===== FIS P2 nomor {s['nomor']} =====")
    print("STIMULUS:", (s.get("stimulus") or {}).get("text", "")[:400])
    print("PERTANYAAN:", (s.get("pertanyaan") or {}).get("text", "")[:400])
    pemb = s.get("pembahasan") or {}
    print("PEMBAHASAN keys:", list(pemb.keys()))
    print("DIKETAHUI:", pemb.get("diketahui"))
    print()
