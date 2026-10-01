# -*- coding: utf-8 -*-
"""_inspect_leak.py — Lihat konteks kebocoran LaTeX pada satu soal."""
import json
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

fn = sys.argv[1] if len(sys.argv) > 1 else "MATEMATIKA_LANJUT_PAKET_1_SOLUTIONS.json"
qno = int(sys.argv[2]) if len(sys.argv) > 2 else 5

d = json.load(open(f"data/solution_sources/{fn}", encoding="utf-8"))
s = next(x for x in d["solutions"] if x.get("question_number") == qno)
blob = " | ".join([str(s.get("diketahui") or ""), str(s.get("ditanyakan") or ""),
                   str(s.get("reasoning") or ""), str(s.get("why_correct") or "")] +
                  [str(x.get("explanation") or "") for x in s.get("steps", [])])
clean = re.sub(r"\$[^$]*\$", " ", blob)
pat = re.compile(r"\\(?:frac|dfrac|tfrac|lim|left|right|sqrt|sum|theta|pi)\b")
for m in pat.finditer(clean):
    st = max(0, m.start() - 60)
    print("LEAK:", repr(clean[st:m.end() + 40]))
