# -*- coding: utf-8 -*-
"""_scan_render_garbage.py — scan pola sampah render di file aktif (user-visible).

Pola:
  1. Huruf italic matematis Unicode (U+1D400-1D7FF) di luar $...$
  2. Kata LaTeX Inggris mentah: 'rightarrow', 'leftarrow', 'tfrac', 'textmetrik'
  3. Artefak 'rigℎta r row', 'tex t metrik t on'
  4. Field terpotong mid-LaTeX (berakhiran backslash / perintah tak tertutup)
"""
import json
import os
import re
import sys
import unicodedata

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"

# file aktif yang dimuat app.js (learning) + server (canonical, solution_sources aktif)
ACTIVE_LEARNING = [
    "matematika_paket_1_learning.json", "matematika_paket_2_learning.json",
    "matematika_lanjut_paket_1_learning.json", "matematika_lanjut_paket_2_learning.json",
    "bahasa_indonesia_paket_1_learning.json", "bahasa_indonesia_paket_2_learning.json",
    "bahasa_inggris_paket_1_learning.json", "bahasa_inggris_paket_2_learning.json",
    "ekonomi_paket_1_learning.json", "ekonomi_paket_2_learning.json",
    "kewirausahaan_paket_1_learning.json", "kewirausahaan_paket_2_learning.json",
    "geografi_paket_1_learning.json", "geografi_paket_2_learning.json",
    "fisika_paket_1_learning.json", "fisika_paket_2_learning.json",
    "kimia_paket_1_learning.json", "kimia_paket_2_learning.json",
    "biologi_paket_1_learning.json", "biologi_paket_2_learning.json",
    "sosiologi_paket_1_learning.json",
    "sejarah_paket_1_learning.json", "sejarah_paket_2_learning.json",
]

MATH_ITALIC = re.compile(r"[\U0001D400-\U0001D7FF\u210E\u210F\u2113]")
WORDS = re.compile(r"rightarrow|leftarrow|textmetrik|metrikton|pertahun\}'|tfrac|dfrac")
FRAG = re.compile(r"rigℎta|tex\s?t\s?metrik|t\s?onpert|t\s?on/ta")


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


def check(text):
    hits = []
    for in_math, seg in segments(text):
        if in_math:
            continue
        if MATH_ITALIC.search(seg):
            hits.append(("italic", seg[:120]))
        for m in WORDS.finditer(seg):
            hits.append(("word", seg[max(0, m.start()-40):m.end()+40]))
        for m in FRAG.finditer(seg):
            hits.append(("frag", seg[max(0, m.start()-40):m.end()+40]))
    # field terpotong: berakhiran aneh
    t = (text or "").rstrip()
    if t and (t.endswith("\\") or re.search(r"\\text\{[^}]*$", t) or re.search(r"\\frac\{[^}]*$", t)
              or re.search(r"=[^=]*\\?[a-z]{1,4}$", t) and t.count("$") % 2 == 1):
        hits.append(("truncated?", t[-100:]))
    return hits


def walk(o, p=""):
    if isinstance(o, str):
        for cat, snip in check(o):
            yield cat, p, snip
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{p}/{i}")
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, f"{p}/{k}")


total = 0
for rel in ACTIVE_LEARNING:
    path = os.path.join(DATA, rel)
    if not os.path.isfile(path):
        print(f"[MISSING] {rel}")
        continue
    d = json.load(open(path, encoding="utf-8"))
    found = list(walk(d))
    if found:
        print(f"\n=== {rel} ({len(found)}) ===")
        for cat, p, snip in found[:25]:
            print(f"  [{cat}] {p}")
            print(f"      {snip!r}"[:250])
        total += len(found)

# solution_sources aktif
sol_dir = os.path.join(DATA, "solution_sources")
reg = json.load(open(os.path.join(sol_dir, "registry.json"), encoding="utf-8"))
for key, meta in reg.items():
    if key.startswith("_"):
        continue
    fn = meta.get("active_source") if isinstance(meta, dict) else None
    if not fn:
        continue
    path = os.path.join(sol_dir, fn)
    if not os.path.isfile(path):
        print(f"[MISSING-SOL] {fn}")
        continue
    d = json.load(open(path, encoding="utf-8"))
    found = list(walk(d))
    if found:
        print(f"\n=== solution_sources/{fn} ({len(found)}) ===")
        for cat, p, snip in found[:25]:
            print(f"  [{cat}] {p}")
            print(f"      {snip!r}"[:250])
        total += len(found)

print(f"\nTOTAL: {total}")
