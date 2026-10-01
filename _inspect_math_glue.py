# -*- coding: utf-8 -*-
r"""_inspect_math_glue.py — Audit menyeluruh: LaTeX bocor / ter-glue di SEMUA field teks.

Target masalah (laporan boss): rumus tampil sebagai kode mentah, contoh:
  "limxto3frac x 3− 3 x2+2 x+15+3x−9 x 2=frac7−67=−frac767 lim xto3​"

Pola yang dicari pada teks DI LUAR $...$ / $$...$$:
  A. LaTeX utuh tanpa delimiter  : \frac, \lim, \sqrt, ... (backslash masih ada)
  B. LaTeX kehilangan backslash  : "limxto", "fracx", "xto3", "frac7", kata
     "frac"/"lim"/"to" berdiri sendiri di antara angka/simbol
  C. Artefak perataan KaTeX      : "f rac", "l eft", "r ight", glyph ℎ
  D. Tanda kurung math delimiters gantung: \( \) \[ \] tanpa pasangan

Output: daftar file -> field -> cuplikan masalah. Tidak mengubah apa pun.
"""
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# --- Detektor ----------------------------------------------------------------
LATEX_CMDS = re.compile(
    r"\\(?:frac|dfrac|tfrac|lim|left|right|sqrt|sum|int|prod|theta|pi|alpha|beta|"
    r"gamma|delta|cdot|times|approx|neq|leq|geq|pm|infty|rightarrow|Rightarrow|log|sin|cos|tan)\b"
)
# LaTeX yang sudah kehilangan backslash-nya (glued copy dari render KaTeX)
GLUED = re.compile(
    r"\blimxto\b|\bxto\d|\bto\dfrac\b|\blim\s*x\s*to\b|"
    r"\bfrac\s?[x\d]|\bfrac\b(?=\s*[-+=])|"
    r"=frac|=−frac|\blim\b(?=\s*[\dx(])|"
    r"\bf\s+rac\b|\bl\s+eft\b|\br\s+i\s*g\s*h\s*t\b"
)
ITALIC_H = "\u210E"
HANGING_DELIM = re.compile(r"\\[()\[\]]")


def segments(text):
    r"""Pecah teks jadi [(in_math, segmen)]. $$...$$ lalu $...$ = math."""
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


def odd_dollars(text):
    """Jumlah $ ganjil = delimiter math rusak (pasangan $...$ nggak tertutup)."""
    return text.count("$") % 2 == 1


def find_issues(text):
    """Return list of (kategori, cuplikan) untuk satu nilai string."""
    if not text or not isinstance(text, str):
        return []
    found = []
    if odd_dollars(text):
        found.append(("dollar_ganjil", text[:120]))
    for in_math, seg in segments(text):
        if in_math:
            continue
        for m in LATEX_CMDS.finditer(seg):
            found.append(("latex_mentah", seg[max(0, m.start() - 40):m.end() + 40]))
        for m in GLUED.finditer(seg):
            found.append(("glued", seg[max(0, m.start() - 40):m.end() + 40]))
        if ITALIC_H in seg:
            found.append(("italic_h", seg[:80]))
        for m in HANGING_DELIM.finditer(seg):
            found.append(("delim_gantung", seg[max(0, m.start() - 40):m.end() + 40]))
    return found


def walk_strings(obj, path=()):
    """Yield (path, nilai_string) untuk semua string di struktur JSON."""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, path + (i,))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, path + (k,))


def audit_file(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return [("FILE_ERROR", str(e))]
    issues = []
    for fpath, val in walk_strings(d):
        for cat, snip in find_issues(val):
            loc = "/".join(str(x) for x in fpath[:4])
            issues.append((cat, loc, snip.replace("\n", " ")[:150]))
    return issues


def main():
    skip_dirs = {"backup_kunci", "backup_raw_20260920", "backup_solutions_20260929",
                 "backup_text_repair_20260929_050255", "backup_text_repair_20260929_051009",
                 "_vision_batch", "claude_input", "claude_output"}
    grand = {}
    for root, dirs, files in os.walk(DATA_DIR):
        dirs[:] = [x for x in dirs if x not in skip_dirs]
        for fn in files:
            if not fn.endswith(".json"):
                continue
            full = os.path.join(root, fn)
            issues = audit_file(full)
            if issues:
                rel = os.path.relpath(full, DATA_DIR)
                grand[rel] = issues
    if not grand:
        print("BERSIH: tidak ada LaTeX bocor / glued / artefak di data aktif.")
        return
    for rel, issues in sorted(grand.items()):
        print(f"\n=== {rel} ({len(issues)} temuan) ===")
        bycat = {}
        for it in issues:
            bycat.setdefault(it[0], []).append(it)
        for cat, lst in bycat.items():
            print(f"  [{cat}] x{len(lst)}")
            for it in lst[:6]:
                body = " | ".join(str(x) for x in it[1:])
                print(f"    - {body}")
            if len(lst) > 6:
                print(f"    ... (+{len(lst) - 6} lagi)")
    total = sum(len(v) for v in grand.values())
    print(f"\nTOTAL temuan: {total} di {len(grand)} file")


if __name__ == "__main__":
    main()
