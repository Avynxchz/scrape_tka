# -*- coding: utf-8 -*-
"""Inspeksi skema lengkap (read-only): path field string di learning + solutions,
karakter italic mtl p1, pre-scan U+00C2 di semua data aktif."""
import glob
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"
MATH_ITALIC = re.compile(r"[\U0001D400-\U0001D7FF\u210E\u210F\u2113]")


def jload(rel):
    with open(os.path.join(DATA, rel), encoding="utf-8") as f:
        return json.load(f)


def schema(o, path=(), acc=None):
    """Kumpulkan path (indeks list -> []) untuk semua string."""
    if acc is None:
        acc = {}
    if isinstance(o, str):
        key = ".".join(path) or "<root>"
        acc.setdefault(key, []).append(o)
    elif isinstance(o, list):
        for v in o:
            schema(v, path + ("[]",), acc)
    elif isinstance(o, dict):
        for k, v in o.items():
            schema(v, path + (str(k),), acc)
    return acc


print("== italic char di mtl p1 /soal/12/pertanyaan.html (pola scanner persis) ==")
d = jload("matematika_lanjut_paket_1_learning.json")
h = d["soal"][11]["pertanyaan"]["html"]
ms = list(MATH_ITALIC.finditer(h))
print("matches:", len(ms))
for m in ms:
    a, b = max(0, m.start() - 90), m.end() + 90
    print(f"  U+{ord(m.group()):04X} ctx: {h[a:b]!r}")

print("\n== schema string-fields: sejarah_paket_2_learning.json (path: n_strings) ==")
sch = schema(jload("sejarah_paket_2_learning.json"))
for k in sorted(sch):
    print(f"  {k}: n={len(sch[k])}")
print("sample soal_serupa paths:")
for k in sorted(sch):
    if k.startswith("soal[].soal_serupa"):
        print(f"    {k}: e.g. {sch[k][0][:80]!r}")

print("\n== schema: pilihan_jawaban & pernyataan samples ==")
s0 = d  # sejarah
s = jload("sejarah_paket_2_learning.json")["soal"][0]
print("pilihan_jawaban[0]:", json.dumps(s["pilihan_jawaban"][0], ensure_ascii=False)[:300])
print("pernyataan[0]:", json.dumps(s["pernyataan"][0], ensure_ascii=False)[:300])
print("images[0] stimulus:", json.dumps(s["stimulus"].get("images", [])[:1], ensure_ascii=False)[:300])

print("\n== schema string-fields per learning file (ringkas) ==")
for p in sorted(glob.glob(os.path.join(DATA, "*_learning.json"))):
    fn = os.path.basename(p)
    sc = schema(jload(fn))
    tops = sorted({".".join(k.split(".")[:2]) for k in sc})
    print(f"  {fn}: {len(sc)} distinct string paths")

print("\n== pre-scan U+00C2 di semua data/*.json aktif (top-level + solution_sources) ==")
targets = sorted(glob.glob(os.path.join(DATA, "*.json"))) + sorted(
    glob.glob(os.path.join(DATA, "solution_sources", "*.json")))
for p in targets:
    rel = os.path.relpath(p, DATA)
    if rel.startswith("backup") or os.sep + "backup" in rel:
        continue
    txt = open(p, encoding="utf-8").read()
    n = txt.count("\u00c2")
    if n:
        # konteks tiap kemunculan (maks 5)
        ctxs = []
        for m in re.finditer("\u00c2", txt):
            a, b = max(0, m.start() - 30), m.end() + 30
            ctxs.append(txt[a:b])
            if len(ctxs) >= 5:
                break
        print(f"  {rel}: {n}x U+00C2")
        for c in ctxs:
            print(f"      {c!r}")
print("(selesai — file tanpa output = bersih U+00C2)")

print("\n== schema string-fields: SEMUA solution_sources aktif (path: n) gabungan ==")
reg = jload("solution_sources/registry.json")
allsc = {}
for slug, meta in reg.items():
    if slug.startswith("_") or not isinstance(meta, dict):
        continue
    fn = meta.get("active_source")
    if not fn:
        continue
    doc = jload(f"solution_sources/{fn}")
    sc = schema(doc)
    for k, v in sc.items():
        allsc.setdefault(k, 0)
        allsc[k] += len(v)
    print(f"  {fn}: solutions={len(doc.get('solutions', []))} paths={len(sc)}")
print("\nagg paths:")
for k in sorted(allsc):
    print(f"  {k}: n={allsc[k]}")
