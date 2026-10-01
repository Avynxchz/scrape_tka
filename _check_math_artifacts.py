# -*- coding: utf-8 -*-
"""_check_math_artifacts.py — Laporan sisa artefak math di seluruh data."""
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ITALIC_H = "\u210E"
# LaTeX mentah di luar $...$ (dilaporkan user: \frac, \left, \lim tampil sebagai teks)
LATEX_CMDS = re.compile(r"\\(frac|dfrac|tfrac|lim|left|right|sqrt|sum|int|theta|pi)\b")
FLATTEN = re.compile(r"\bf\s*rac\b|\br\s*i\s*g\s*h\s*t\b|\bl\s*e\s*f\s*t\b")
LOOSE_EXP = re.compile(r"(?<=[a-z])(\s\d{1,2})(?=\s|$|[+\-<),.;])")


def fields_of(s):
    for fld in ("diketahui", "ditanyakan", "reasoning", "why_correct"):
        yield fld, s.get(fld)
    for st in s.get("steps") or []:
        yield "step", st.get("explanation")


def in_math_free(text):
    """Buang segmen $...$ (LaTeX valid yang akan dirender KaTeX)."""
    return re.sub(r"\$[^$]*\$", " ", text or "")


def main():
    sol_dir = os.path.join("data", "solution_sources")
    print("=== LAPORAN SISA ARTEFAK MATH (di luar $...$) ===")
    total = {"h": 0, "latex": 0, "flatten": 0}
    for fn in sorted(os.listdir(sol_dir)):
        if not fn.endswith(".json") or fn == "registry.json":
            continue
        d = json.load(open(os.path.join(sol_dir, fn), encoding="utf-8"))
        n_h = n_latex = n_fl = 0
        samples = []
        for s in d.get("solutions", []):
            for fld, val in fields_of(s):
                clean = in_math_free(str(val or ""))
                n_h += clean.count(ITALIC_H)
                hits = LATEX_CMDS.findall(clean)
                n_latex += len(hits)
                fl = FLATTEN.findall(clean)
                n_fl += len(fl)
                if hits and len(samples) < 2:
                    samples.append(f"{fld}: ...{(clean[max(0,clean.find(hits[0])-30):clean.find(hits[0])+40]).strip()!r}")
        if n_h or n_latex or n_fl:
            print(f"{fn}: italic-ℎ={n_h}, latex-mentah={n_latex}, flatten={n_fl}")
            for sv in samples:
                print(f"   {sv}")
        total["h"] += n_h
        total["latex"] += n_latex
        total["flatten"] += n_fl
    print(f"\nTOTAL: italic-ℎ={total['h']}, latex-mentah={total['latex']}, flatten={total['flatten']}")

    # Diketahui ambigu/terlalu pendek
    print("\n=== DIKETAHUI AMBIGU (< 15 char atau tanpa angka/rumus) ===")
    n_amb = 0
    for fn in sorted(os.listdir(sol_dir)):
        if not fn.endswith(".json") or fn == "registry.json":
            continue
        d = json.load(open(os.path.join(sol_dir, fn), encoding="utf-8"))
        for s in d.get("solutions", []):
            dik = re.sub(r"\$[^$]*\$", "RUMUS", str(s.get("diketahui") or "")).strip()
            if len(dik) < 15 or not re.search(r"\d|RUMUS", dik):
                n_amb += 1
                print(f"  {fn} Q{s.get('question_number')}: {s.get('diketahui')!r}")
    if not n_amb:
        print("  (tidak ada)")


if __name__ == "__main__":
    main()
