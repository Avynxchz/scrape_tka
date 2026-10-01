# -*- coding: utf-8 -*-
"""_audit_pilar_full.py — audit penuh pola teks rusak (pilar 1 & langkah) SEMUA mapel.
READ-ONLY. Laporan: scratch/audit_penuh_20260929.md
Pola: (1) echo vertikal, (2) LaTeX korup (±atrix / command terpisah spasi),
(3) LaTeX mentah di luar $...$, (4) echo ganda, (5) unicode math italic,
(6) diketahui ambigu.
"""
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"
OUT = r"D:\PROJECTS\SCRAPE_TKA\scratch\audit_penuh_20260929.md"

MATH_ITALIC = re.compile(r"[\U0001D400-\U0001D7FF\u210E]")
BAD_MATRIX = re.compile(r"±atrix|p\s?matrix|b\s?egin\{|\bb e g i n")
SPACED_CMD = re.compile(r"\\(?:fr|sq|le|ri|be|en|ti|cd|ti)\s(?:ac|rt|ft|ght|gin|d|mes|mes|cdot)\b")
RAW_LATEX_WORDS = re.compile(r"\\(begin|frac|sqrt|lim|int|sum|matrix|left|right|cdot|times)\b")
SHORT = lambda s: len(s.strip()) <= 4


def split_math(s):
    return re.split(r"(\$\$[\s\S]*?\$\$|\$[^$\n]*?\$)", s)


def out_side_math(s, pat):
    parts = split_math(s)
    return any(pat.search(p) for i, p in enumerate(parts) if i % 2 == 0)


def vertical_echo(s):
    lines = [l.strip() for l in s.split("\n")]
    run = 0
    for l in lines:
        run = run + 1 if l and SHORT(l) else 0
        if run >= 6:
            # harus ada versi utuh juga (echo) -> ada baris panjang berisi rangkaian sama
            compact = "".join(l for l in lines if l and SHORT(l))
            return True
    return False


def double_echo(s):
    # token rangkaian >=5 char diulang langsung
    m = re.search(r"([\w°×±≠≤≥≈·/^\{\}\\$]{6,}) ?\1", s)
    return bool(m)


def ambiguous(s):
    t = s.strip()
    if 0 < len(t) < 120:
        if re.match(r"^[A-Z][a-zA-Z\s]{2,20}(,,|, dan\.?$| dan\.?$)", t) and t.count(" ") <= 3:
            return True
    return False


def check(s):
    hits = []
    if MATH_ITALIC.search(s):
        hits.append("italic-unicode")
    if BAD_MATRIX.search(s):
        hits.append("latex-korup")
    if out_side_math(s, SPACED_CMD):
        hits.append("latex-korup-spasi")
    if out_side_math(s, RAW_LATEX_WORDS):
        hits.append("latex-mentah")
    if vertical_echo(s):
        hits.append("echo-vertikal")
    if double_echo(s):
        hits.append("echo-ganda")
    if ambiguous(s):
        hits.append("ambigu")
    return hits


# Field user-visible yang DISCAN (termasuk blind spot: pembahasan.*, soal_serupa.*)
SCAN_KEYS = {
    "diketahui", "ditanyakan", "reasoning", "steps", "why_correct", "tips",
    "common_mistakes", "glossary", "official_answer", "text", "title",
    "pertanyaan", "stimulus", "pembahasan", "soal_serupa", "question",
    "konsep", "mengapa", "visual", "pilihan",
}
SKIP_KEYS = {"data_latex", "html", "src", "alt", "slug", "id", "images", "image"}

rows = []


def walk(o, path, fname):
    if isinstance(o, str):
        key = path.split("/")[-1].split("[")[0]
        if key in SKIP_KEYS:
            return
        hits = check(o)
        if hits:
            rows.append((fname, path, ",".join(hits), o.replace("\n", "⏎")[:110]))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f"{path}[{i}]", fname)
    elif isinstance(o, dict):
        for k, v in o.items():
            walk(v, f"{path}/{k}", fname)


targets = []
for f in sorted(os.listdir(DATA)):
    if f.endswith(".json") and os.path.isfile(os.path.join(DATA, f)):
        targets.append(os.path.join(DATA, f))
ss = os.path.join(DATA, "solution_sources")
if os.path.isdir(ss):
    for f in sorted(os.listdir(ss)):
        if f.endswith(".json"):
            targets.append(os.path.join(ss, f))

for p in targets:
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception as e:
        print("[SKIP]", os.path.basename(p), e)
        continue
    walk(d, "$", os.path.basename(p))

per_file = {}
per_pattern = {}
for fname, path, pat, snip in rows:
    per_file.setdefault(fname, {}).setdefault(pat, 0)
    per_file[fname][pat] += 1
    per_pattern[pat] = per_pattern.get(pat, 0) + 1

lines = [
    "# Audit Penuh Teks Rusak — " + "2026-09-29",
    "",
    f"Total temuan: {len(rows)} | File terdampak: {len(per_file)}",
    "",
    "## Per pola",
]
for k, v in sorted(per_pattern.items(), key=lambda x: -x[1]):
    lines.append(f"- {k}: {v}")
lines += ["", "## Detail (file | path | pola | cuplikan)"]
for fname, path, pat, snip in rows:
    lines.append(f"- {fname} | {path} | {pat} | {snip!r}")

io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"TOTAL: {len(rows)} temuan di {len(per_file)} file")
for k, v in sorted(per_pattern.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
print()
for fname, pats in sorted(per_file.items()):
    tot = sum(pats.values())
    print(f"  {fname}: {tot} {dict(pats)}")
