# -*- coding: utf-8 -*-
"""Inspeksi read-only: bandingkan SEJARAH_PAKET_2 aktif vs backup, cek registry,
petakan struktur field learning JSON (untuk desain script cleaning)."""
import glob
import json
import os
import sys

sys.path.insert(0, r"D:\PROJECTS\SCRAPE_TKA")
from solution_loader import validate_solution_doc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"

print("== learning files (data/*_learning.json) ==")
lf = sorted(glob.glob(os.path.join(DATA, "*_learning.json")))
print("count:", len(lf))
for p in lf:
    print("  ", os.path.basename(p))

print("\n== SEJARAH_PAKET_2 compare ==")
act = os.path.join(DATA, "solution_sources", "SEJARAH_PAKET_2_SOLUTIONS.json")
bak = os.path.join(DATA, "backup_solutions_20260929", "SEJARAH_PAKET_2_SOLUTIONS.json")
for label, p in (("ACTIVE", act), ("BACKUP", bak)):
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    sols = d.get("solutions", [])
    print(f"{label}: solutions={len(sols)} subject={d.get('subject')!r} package={d.get('package')!r} model={d.get('model')!r}")
    print("  qnums:", [s.get("question_number") for s in sols])
    if sols:
        q1 = sols[0]
        print("  q1 question_id:", q1.get("question_id"))
        print("  q1 concept_kunci:", q1.get("concept_kunci"))
        r = (q1.get("reasoning") or "")[:220].replace("\n", " | ")
        print("  q1 reasoning[:220]:", r)
    try:
        validate_solution_doc(d)
        print("  validate_solution_doc: OK")
    except Exception as e:
        print("  validate_solution_doc: FAIL ->", e)
    raw = open(p, encoding="utf-8").read()
    print("  U+00C2 count:", raw.count("\u00c2"))
    print("  'Matriks dan.' occ:", raw.count("Matriks dan."))
    print("  'Matriks,, dan' occ:", raw.count("Matriks,, dan"))
    # top-level keys
    print("  top-level keys:", sorted(d.keys()))

print("\n== registry sejarah_paket_2 ==")
reg = json.load(open(os.path.join(DATA, "solution_sources", "registry.json"), encoding="utf-8"))
print(json.dumps(reg.get("sejarah_paket_2"), ensure_ascii=False, indent=2))


def census(o, keys=None):
    if keys is None:
        keys = {}
    if isinstance(o, dict):
        for k, v in o.items():
            info = keys.setdefault(k, {"count": 0, "types": set()})
            info["count"] += 1
            info["types"].add(type(v).__name__)
            census(v, keys)
    elif isinstance(o, list):
        for v in o:
            census(v, keys)
    return keys


print("\n== key census: sejarah_paket_2_learning.json ==")
sample = json.load(open(os.path.join(DATA, "sejarah_paket_2_learning.json"), encoding="utf-8"))
print("top-level type:", type(sample).__name__)
if isinstance(sample, dict):
    for k, v in sample.items():
        print(f"  top: {k}: {type(v).__name__}" + (f" len={len(v)}" if isinstance(v, (list, dict, str)) else f" = {v!r}"))
kc = census(sample)
for k in sorted(kc):
    info = kc[k]
    print(f"  {k}: n={info['count']} types={sorted(info['types'])}")

print("\n== key census: MTK_PAKET_1_SOLUTIONS.json (sample solution file) ==")
sol = json.load(open(os.path.join(DATA, "solution_sources", "MTK_PAKET_1_SOLUTIONS.json"), encoding="utf-8"))
kc2 = census(sol)
for k in sorted(kc2):
    info = kc2[k]
    print(f"  {k}: n={info['count']} types={sorted(info['types'])}")
