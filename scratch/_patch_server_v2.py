# -*- coding: utf-8 -*-
"""_patch_server_v2.py — batas huruf untuk replacements clean_katex_artifacts (server.py).
Pendekatan per-baris: baris (r'\\?word', r'sym'), di-rewrite jadi berbatas huruf.
"""
import io
import re

p = r"D:\PROJECTS\SCRAPE_TKA\server.py"
lines = io.open(p, encoding="utf-8", newline="").read().split("\r\n")

WORDS = ["times", "neq", "leq", "geq", "pm", "approx",
         "rightarrow", "leftarrow", "cdot", "circ", "degree"]
SYM = {"times": "×", "neq": "≠", "leq": "≤", "geq": "≥", "pm": "±",
       "approx": "≈", "rightarrow": "→", "leftarrow": "←", "cdot": "·",
       "circ": "°", "degree": "°"}

line_re = re.compile(r"^(\s*)\(r'\\\\\?(" + "|".join(WORDS) + r")', r'(.)'\),\s*$")

out = []
n = 0
for ln in lines:
    m = line_re.match(ln)
    if m:
        indent, word, sym = m.groups()
        assert sym == SYM[word], f"simbol tak terduga untuk {word}: {sym!r}"
        out.append(f"{indent}(r'(?<![a-zA-Z])\\\\?{word}(?![a-zA-Z])', r'{sym}'),")
        n += 1
    else:
        out.append(ln)

io.open(p, "w", encoding="utf-8", newline="").write("\r\n".join(out))
print(f"baris di-rewrite: {n}")
