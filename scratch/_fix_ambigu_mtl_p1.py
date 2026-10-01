# -*- coding: utf-8 -*-
"""_fix_ambigu_mtl_p1.py — isi ulang 'diketahui' ambigu q1-q2 solusi MTL P1
dari transkripsi vision asli (sidecar)."""
import io
import json

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"
p = DATA + r"\solution_sources\MATEMATIKA_LANJUT_PAKET_1_SOLUTIONS.json"

d = json.load(io.open(p, encoding="utf-8"))

fixes = {
    0: (
        "Matriks $P = \\begin{pmatrix} 1 & 2 \\\\ -1 & -4 \\end{pmatrix}$ "
        "dan $Q = \\begin{pmatrix} 2 & 5 \\\\ -1 & 2 \\end{pmatrix}$."
    ),
    1: (
        "Matriks $A = \\begin{pmatrix} -1 & 2 \\\\ 3 & 4 \\end{pmatrix}$, "
        "$B = \\begin{pmatrix} -2 & 0 \\\\ 3 & 3 \\end{pmatrix}$, dan "
        "$C = \\begin{pmatrix} -4 & 4 \\\\ -3 & 2 \\end{pmatrix}$."
    ),
}

for i, baru in fixes.items():
    lama = d["solutions"][i].get("diketahui", "")
    d["solutions"][i]["diketahui"] = baru
    print(f"q{i+1}: {lama!r}")
    print(f"   -> {baru!r}")

json.dump(d, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.load(io.open(p, encoding="utf-8"))
print("JSON valid")
