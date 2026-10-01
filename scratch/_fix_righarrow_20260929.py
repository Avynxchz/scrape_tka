# -*- coding: utf-8 -*-
"""_fix_righarrow_20260929.py — bersihkan artefak 'rigℎta r row' (pecahan 'rightarrow')
dari pipeline ekstraksi lama, di semua file data aktif. Idempoten.
Pola di data: '1511 rigℎta r row→Jalur'  ->  '1511 → Jalur'
"""
import glob
import io
import json
import os
import re
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"
BACKUP = os.path.join(DATA, "backup_render_fix_20260929_v2")

PAT_ARROW = re.compile(r"\s*r\s?ig[ℎh]ta\s+r\s?row\s*→\s*")   # dengan panah
PAT_BARE = re.compile(r"\s*r\s?ig[ℎh]ta\s+r\s?row\s*")          # tanpa panah (fallback)


def fix(s):
    s = PAT_ARROW.sub(" → ", s)
    s = PAT_BARE.sub(" → ", s)
    return s


def walk(o):
    if isinstance(o, str):
        return fix(o) if ("igℎta" in o or "ighta" in o) else o
    if isinstance(o, list):
        return [walk(v) for v in o]
    if isinstance(o, dict):
        return {k: (v if k == "data_latex" else walk(v)) for k, v in o.items()}
    return o


total = 0
targets = (
    glob.glob(os.path.join(DATA, "*_learning.json"))
    + glob.glob(os.path.join(DATA, "solution_sources", "*.json"))
)
for p in targets:
    d = json.load(io.open(p, encoding="utf-8"))
    nd = walk(d)
    if json.dumps(nd, ensure_ascii=False) != json.dumps(d, ensure_ascii=False):
        rel = os.path.relpath(p, DATA)
        dst = os.path.join(BACKUP, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy2(p, dst)
        with io.open(p, "w", encoding="utf-8") as f:
            json.dump(nd, f, ensure_ascii=False, indent=2)
        json.load(io.open(p, encoding="utf-8"))
        n = len(PAT_ARROW.findall(str(d))) + len(PAT_BARE.findall(str(d)))
        print(f"[FIXED] {rel}: ~{n} artefak dibersihkan")
        total += n
print(f"TOTAL artefak: {total}")
