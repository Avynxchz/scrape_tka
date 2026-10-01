# -*- coding: utf-8 -*-
"""_patch_server_crlf.py — tambahkan batas huruf pada replacements clean_katex_artifacts (server.py)."""
import io

p = r"D:\PROJECTS\SCRAPE_TKA\server.py"
t = io.open(p, encoding="utf-8", newline="").read()

old = (
    "    # Ganti duplikasi LaTeX mentah yang diekstrak berantakan\n"
    "    replacements = [\n"
    "        (r'\\\\?times', r'×'),\n"
    "        (r'\\\\?neq', r'≠'),\n"
    "        (r'\\\\?leq', r'≤'),\n"
    "        (r'\\\\?geq', r'≥'),\n"
    "        (r'\\\\?pm', r'±'),\n"
    "        (r'\\\\?approx', r'≈'),\n"
    "        (r'\\\\?rightarrow', r'→'),\n"
    "        (r'\\\\?leftarrow', r'←'),\n"
    "        (r'\\\\?cdot', r'·'),\n"
    "        (r'\\\\?circ', r'°'),\n"
    "        (r'\\\\?degree', r'°'),\n"
    "    ]"
).replace("\n", "\r\n")

new = (
    "    # Ganti duplikasi LaTeX mentah yang diekstrak berantakan.\n"
    "    # PENTING (bug 2026-09-29: \"±atrix\\": batas huruf supaya tidak\n"
    "    # menyambar command LaTeX seperti \"pmatrix\" (mengandung \"pm\").\n"
    "    # (?<![a-zA-Z]) tetap mengizinkan digit (\"4times2\" -> \"4×2\").\n"
    "    replacements = [\n"
    "        (r'(?<![a-zA-Z])\\\\?times(?![a-zA-Z])', r'×'),\n"
    "        (r'(?<![a-zA-Z])\\\\?neq(?![a-zA-Z])', r'≠'),\n"
    "        (r'(?<![a-zA-Z])\\\\?leq(?![a-zA-Z])', r'≤'),\n"
    "        (r'(?<![a-zA-Z])\\\\?geq(?![a-zA-Z])', r'≥'),\n"
    "        (r'(?<![a-zA-Z])\\\\?pm(?![a-zA-Z])', r'±'),\n"
    "        (r'(?<![a-zA-Z])\\\\?approx(?![a-zA-Z])', r'≈'),\n"
    "        (r'(?<![a-zA-Z])\\\\?rightarrow(?![a-zA-Z])', r'→'),\n"
    "        (r'(?<![a-zA-Z])\\\\?leftarrow(?![a-zA-Z])', r'←'),\n"
    "        (r'(?<![a-zA-Z])\\\\?cdot(?![a-zA-Z])', r'·'),\n"
    "        (r'(?<![a-zA-Z])\\\\?circ(?![a-zA-Z])', r'°'),\n"
    "        (r'(?<![a-zA-Z])\\\\?degree(?![a-zA-Z])', r'°'),\n"
    "    ]"
).replace("\n", "\r\n")

assert old in t, "blok tidak ketemu"
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("patched OK")
