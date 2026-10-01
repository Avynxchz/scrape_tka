# -*- coding: utf-8 -*-
"""Inspeksi lanjutan (read-only): leaf-name union, italic mtl soal[12],
U+00C2 pre-scan, tipe item list solusi, kunci_jawaban string-form."""
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


def leaf_names(o, acc=None, listctx=None):
    """Nama leaf field untuk string; listctx = nama key list induk utk bare strings."""
    if acc is None:
        acc = {}
    if isinstance(o, str):
        acc[(listctx,)] = acc.get((listctx,), 0) + 1
    elif isinstance(o, list):
        for v in o:
            leaf_names(v, acc, listctx)
    elif isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str):
                acc[(k,)] = acc.get((k,), 0) + 1
            else:
                leaf_names(v, acc, k if isinstance(v, list) else None)
    return acc


print("== mtl p1 soal[12] pertanyaan.html italic ==")
d = jload("matematika_lanjut_paket_1_learning.json")
h = d["soal"][12]["pertanyaan"]["html"]
ms = list(MATH_ITALIC.finditer(h))
print("len:", len(h), "matches:", len(ms))
for m in ms:
    a, b = max(0, m.start() - 90), m.end() + 90
    print(f"  U+{ord(m.group()):04X} ctx: {h[a:b]!r}")
# juga cek semua string di file itu yang match italic
def walk_str(o, p=""):
    if isinstance(o, str):
        if MATH_ITALIC.search(o):
            yield p, o
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk_str(v, f"{p}/{i}")
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from walk_str(v, f"{p}/{k}")

for p, s in walk_str(d):
    print("  ITALIC-STR:", p, "->", MATH_ITALIC.findall(s)[:5])

print("\n== leaf-name union: 25 learning files ==")
acc_all = {}
for p in sorted(glob.glob(os.path.join(DATA, "*_learning.json"))):
    acc = leaf_names(jload(p))
    for k, n in acc.items():
        acc_all[k] = acc_all.get(k, 0) + n
for (name,), n in sorted(acc_all.items()):
    print(f"  {name}: n={n}")

print("\n== U+00C2 pre-scan (data/*.json + solution_sources/*.json, tanpa backup) ==")
targets = sorted(glob.glob(os.path.join(DATA, "*.json"))) + sorted(
    glob.glob(os.path.join(DATA, "solution_sources", "*.json")))
found_any = False
for p in targets:
    rel = os.path.relpath(p, DATA)
    txt = open(p, encoding="utf-8").read()
    n = txt.count("\u00c2")
    if n:
        found_any = True
        ctxs = []
        for m in re.finditer("\u00c2", txt):
            a, b = max(0, m.start() - 40), m.end() + 40
            ctxs.append(txt[a:b].replace("\n", "\\n"))
            if len(ctxs) >= 8:
                break
        print(f"  {rel}: {n}x")
        for c in ctxs:
            print(f"      {c!r}")
if not found_any:
    print("  (tidak ada U+00C2 di file aktif manapun)")

print("\n== kunci_jawaban string-form samples ==")
for p in sorted(glob.glob(os.path.join(DATA, "*_learning.json"))):
    dd = jload(p)
    for s in dd.get("soal", []):
        kj = s.get("kunci_jawaban")
        if isinstance(kj, str):
            print(f"  {os.path.basename(p)} soal {s.get('nomor')}: {kj!r:.120}")
            break

print("\n== tipe item list di solution files (union ringkas) ==")
reg = jload("solution_sources/registry.json")
item_types = {}
for slug, meta in reg.items():
    if slug.startswith("_") or not isinstance(meta, dict):
        continue
    fn = meta.get("active_source")
    doc = jload(f"solution_sources/{fn}")
    for s in doc.get("solutions", []):
        for key in ("concept_kunci", "glossary", "steps", "tips", "common_mistakes", "pernyataan"):
            v = s.get(key)
            if isinstance(v, list) and v:
                t = type(v[0]).__name__
                item_types.setdefault(key, set()).add(t)
                if isinstance(v[0], dict):
                    item_types.setdefault(key + ".keys", set()).update(v[0].keys())
for k in sorted(item_types):
    print(f"  {k}: {sorted(item_types[k])}")
