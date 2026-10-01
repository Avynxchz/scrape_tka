# -*- coding: utf-8 -*-
"""Inspeksi struktur detail untuk desain cleaning (read-only)."""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"


def jload(rel):
    with open(os.path.join(DATA, rel), encoding="utf-8") as f:
        return json.load(f)


print("== mtl p1 soal/12 pertanyaan.html (italic finding) ==")
d = jload("matematika_lanjut_paket_1_learning.json")
h = d["soal"][11]["pertanyaan"]["html"]
# tampilkan bagian yang mengandung math italic
import re
for m in re.finditer(r"[\U0001D400-\U0001D7FF\u210E\u210F\u2113]", h):
    a, b = max(0, m.start() - 60), m.end() + 60
    print("  ...", repr(h[a:b]))
print("  total len:", len(h))

print("\n== sejarah_paket_2 soal[0] keys & soal_serupa ==")
s = jload("sejarah_paket_2_learning.json")["soal"][0]
print("soal keys:", sorted(s.keys()))
print("soal_serupa:", json.dumps(s["soal_serupa"], ensure_ascii=False)[:900])
print("\nstimulus:", json.dumps(s["stimulus"], ensure_ascii=False)[:600])
print("\npertanyaan:", json.dumps(s["pertanyaan"], ensure_ascii=False)[:400])
print("\npilihan[0..1]:", json.dumps(s["pilihan"][:2], ensure_ascii=False)[:400])
print("\nfull_display[:300]:", repr((s.get("full_display") or "")[:300]))
print("\nkunci:", s.get("kunci"), "| kunci_jawaban:", s.get("kunci_jawaban"))

print("\n== kimia_paket_2 soal[7] stimulus.images[0] ==")
k = jload("kimia_paket_2_learning.json")["soal"][7]
print("images:", json.dumps(k["stimulus"].get("images"), ensure_ascii=False)[:500])

print("\n== paket_1_learning.json top-level (legacy?) ==")
p1 = jload("paket_1_learning.json")
print("type:", type(p1).__name__, "keys:", list(p1.keys())[:10] if isinstance(p1, dict) else len(p1))

print("\n== variasi struktur antar learning files ==")
for fn in ["matematika_paket_1_learning.json", "kimia_paket_1_learning.json",
           "bahasa_indonesia_paket_1_learning.json", "paket_1_learning.json", "paket_2_learning.json"]:
    try:
        dd = jload(fn)
        soal = dd.get("soal") if isinstance(dd, dict) else None
        n = len(soal) if isinstance(soal, list) else "?"
        one = soal[0] if isinstance(soal, list) and soal else {}
        print(f"  {fn}: soal={n} soal-keys={sorted(one.keys())[:20] if isinstance(one, dict) else type(one).__name__}")
    except Exception as e:
        print(f"  {fn}: ERROR {e}")

print("\n== MTK_PAKET_1_SOLUTIONS solusi[0] (shape) ==")
sol = jload("solution_sources/MTK_PAKET_1_SOLUTIONS.json")["solutions"][0]
print("keys:", sorted(sol.keys()))
print("official_answer:", json.dumps(sol.get("official_answer"), ensure_ascii=False)[:200])
print("glossary[:2]:", json.dumps(sol.get("glossary", [])[:2], ensure_ascii=False)[:300])
print("steps[0]:", json.dumps(sol.get("steps", [])[:1], ensure_ascii=False)[:300])
