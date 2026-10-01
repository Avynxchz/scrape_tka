# -*- coding: utf-8 -*-
"""_fix_mlanjut13_html.py — bersihkan italic Unicode di HTML soal 13 MLANJUT P1.

HTML ini dirender langsung ke user (promptContainer.innerHTML). Huruf italic
Unicode (𝒖𝒗𝒘𝑣𝑤) tampil aneh; diganti variabel LaTeX yang dirender KaTeX:
  𝒖 = (1,1,−1)  →  $\mathbf{u} = (1, 1, -1)$
  𝑣1 → $v_1$, 𝑤1 → $w_1$, dst.
"""
import json
import os
import re
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"
rel = "matematika_lanjut_paket_1_learning.json"
path = os.path.join(DATA, rel)
backup = os.path.join(DATA, "backup_render_fix_20260929", rel)
if not os.path.exists(backup):
    shutil.copy2(path, backup)

d = json.load(open(path, encoding="utf-8"))
h = d["soal"][12]["pertanyaan"]["html"]

# tampilkan isi <p> utama dulu untuk verifikasi
m = re.search(r"<p>(.*?)</p>", h, re.S)
print("SEBELUM:", (m.group(1) if m else h)[:400])

new = h
# vektor bold-italic: 𝒖 𝒗 𝒘 (U+1D4C6.. range bold-italic small)
new = new.replace("𝒖", r"$\mathbf{u}$")
new = new.replace("𝒗", r"$\mathbf{v}$")
new = new.replace("𝒘", r"$\mathbf{w}$")
new = new.replace("𝑣1", r"$v_1$")
new = new.replace("𝑤1", r"$w_1$")
new = new.replace("𝑤2", r"$w_2$")
new = new.replace("−", "-")

# jangan sampai ada $ ganda akibat replace berurutan (mis. $v_1$ di dalam $...$)
# — di HTML soal ini tidak ada $...$ lain, aman.

d["soal"][12]["pertanyaan"]["html"] = new
json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

d2 = json.load(open(path, encoding="utf-8"))
m2 = re.search(r"<p>(.*?)</p>", d2["soal"][12]["pertanyaan"]["html"], re.S)
print()
print("SESUDAH:", (m2.group(1) if m2 else "")[:400])
