# -*- coding: utf-8 -*-
"""Pre-count trigger deteksi 'pola rusak' di semua target (read-only).
Mencetak per file: jumlah string terdeteksi + sampel, agar false positive
terlihat SEBELUM script cleaning dijalankan."""
import glob
import json
import os
import re
import sys

sys.path.insert(0, r"D:\PROJECTS\SCRAPE_TKA")
from text_quality import merge_fragmented_lines

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"
MATH_ITALIC = re.compile(r"[\U0001D400-\U0001D7FF\u210E\u210F\u2113]")
WORDS = re.compile(r"rightarrow|leftarrow|textmetrik|metrikton|pertahun\}'|tfrac|dfrac")
FRAG = re.compile(r"rigℎta|tex\s?t\s?metrik|t\s?onpert|t\s?on/ta")
WSYM = re.compile(r"(?<=[\d\)\}])\s*times\s*(?=[\d\(\{\$])|(?<![\w])(?:times|neq|leq|geq|cdot|approx|rightarrow|leftarrow)(?=[\d\(\{])")
ECHO = re.compile(r"(\d+[×±≠≤≥≈·]\d+)\1")
EXCLUDE_LEAVES = {"data_latex", "latex", "filename", "rel_path", "remote_url", "id", "slug", "source"}


def segments(text):
    parts = re.split(r"(\$\$[\s\S]*?\$\$|\$[^$\n]*?\$)", text)
    out = []
    for p in parts:
        if p.startswith("$$") and p.endswith("$$") and len(p) > 3:
            out.append((True, p))
        elif p.startswith("$") and p.endswith("$") and len(p) > 1:
            out.append((True, p))
        elif p:
            out.append((False, p))
    return out


def fragmented(text):
    """True bila ada run >=2 baris pendek/fragmen yang akan digabung."""
    lines = text.split("\n")
    if len(lines) < 2:
        return False
    merged = merge_fragmented_lines(text)
    # bandingkan jumlah baris non-kosong sebelum/sesudah
    def ncode(ls):
        return [l.strip() for l in ls if l.strip()]
    a, b = ncode(lines), ncode(merged)
    if len(a) != len(b):
        return True
    return a != b


def triggers(s):
    hits = []
    for in_math, seg in segments(s):
        if in_math:
            continue
        if MATH_ITALIC.search(seg):
            hits.append("italic")
        if WORDS.search(seg):
            hits.append("words")
        if FRAG.search(seg):
            hits.append("frag")
        if WSYM.search(seg):
            hits.append("wsym")
    if "\u00c2" in s:
        hits.append("mojibake")
    if ECHO.search(s):
        hits.append("echo")
    if fragmented(s):
        hits.append("frag_lines")
    return hits


def walk(o, leaf=None, p=""):
    if isinstance(o, str):
        yield leaf, p, o
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, leaf, f"{p}/{i}")
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, k if isinstance(v, str) else (k if isinstance(v, list) else None), f"{p}/{k}")


targets = []
for p in sorted(glob.glob(os.path.join(DATA, "*_learning.json"))):
    targets.append(("learning", os.path.relpath(p, DATA), p))
reg = json.load(open(os.path.join(DATA, "solution_sources", "registry.json"), encoding="utf-8"))
for slug, meta in reg.items():
    if slug.startswith("_") or not isinstance(meta, dict):
        continue
    fn = meta.get("active_source")
    if fn:
        fp = os.path.join(DATA, "solution_sources", fn)
        targets.append(("solution", f"solution_sources/{fn}", fp))

grand = 0
for kind, rel, fp in targets:
    d = json.load(open(fp, encoding="utf-8"))
    found = []
    for leaf, p, s in walk(d):
        if leaf in EXCLUDE_LEAVES:
            continue
        t = triggers(s)
        if t:
            found.append((leaf, p, t, s))
    raw = open(fp, encoding="utf-8").read()
    nl = "NL" if raw.endswith("\n") else "noNL"
    if found:
        print(f"\n=== {rel} ({len(found)} strings, {nl}) ===")
        for leaf, p, t, s in found[:8]:
            print(f"  [{','.join(t)}] leaf={leaf} {p}")
            print(f"      {s[:160]!r}")
        if len(found) > 8:
            print(f"  ... +{len(found)-8} more")
        grand += len(found)
    else:
        print(f"--- {rel}: 0 ({nl})")

print(f"\nGRAND TOTAL triggered strings: {grand}")

# registry round-trip check
regtxt = open(os.path.join(DATA, "solution_sources", "registry.json"), encoding="utf-8").read()
rt = json.dumps(json.loads(regtxt), ensure_ascii=False, indent=2)
print("registry round-trip identical:", rt == regtxt or rt + "\n" == regtxt or rt.strip() == regtxt.strip())
