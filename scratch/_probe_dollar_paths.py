# -*- coding: utf-8 -*-
"""Cari path JSON persis yang memuat '$', backslash-lat, 'atrix' di slice non-hitungan."""
import json, re, sys
from pathlib import Path

ROOT = Path(r"D:\PROJECTS\SCRAPE_TKA")
FILES = [
    "data/bahasa_indonesia_paket_1_learning.json",
    "data/bahasa_indonesia_paket_2_learning.json",
    "data/bahasa_inggris_paket_1_learning.json",
    "data/bahasa_inggris_paket_2_learning.json",
    "data/biologi_paket_1_learning.json",
    "data/biologi_paket_2_learning.json",
    "data/geografi_paket_1_learning.json",
    "data/geografi_paket_2_learning.json",
    "data/sosiologi_paket_1_learning.json",
    "data/sejarah_paket_1_learning.json",
    "data/sejarah_paket_2_learning.json",
    "data/solution_sources/BAHASA_INDONESIA_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/BAHASA_INDONESIA_PAKET_2_SOLUTIONS.json",
    "data/solution_sources/BING_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/BING_PAKET_2_SOLUTIONS.json",
    "data/solution_sources/BIOLOGI_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/BIOLOGI_PAKET_2_SOLUTIONS.json",
    "data/solution_sources/GEO_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/GEO_PAKET_2_SOLUTIONS.json",
    "data/solution_sources/SOSIOLOGI_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/SEJARAH_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/SEJARAH_PAKET_2_SOLUTIONS.json",
]

DOLLAR = "$"
BS_LAT = re.compile(r"\\[a-zA-Z]+")
ATRIX = re.compile(r"atrix", re.IGNORECASE)

for rel in FILES:
    p = ROOT / rel
    if not p.exists():
        print("MISSING", rel)
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    found = {}

    def walk(v, path):
        if isinstance(v, str):
            tags = []
            if DOLLAR in v:
                tags.append("DOLLAR")
            m = BS_LAT.search(v)
            if m:
                tags.append("BSLAT:" + m.group(0))
            m = ATRIX.search(v)
            if m:
                tags.append("ATRIX")
            for t in tags:
                key = (re.sub(r"\[\d+\]", "[N]", path), t)
                if key not in found:
                    found[key] = [0, v]
                found[key][0] += 1
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, path + "[%d]" % i)
        elif isinstance(v, dict):
            for k, x in v.items():
                walk(x, path + "." + str(k))

    walk(d, "$")
    if found:
        print("==", rel.split("/")[-1])
        for (path, tag), (n, ex) in sorted(found.items()):
            print("  %-28s %-18s count=%d" % (path, tag, n))
            print("     contoh: %r" % ex[:140])
