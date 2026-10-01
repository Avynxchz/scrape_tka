# -*- coding: utf-8 -*-
r"""_fix_render_garbage.py — Perbaiki semua rumus/rusak render yang bocor ke user.

Perbaikan (hasil audit _scan_render_garbage.py + _inspect_math_glue.py):
  1. BI P2 learning soal/8 soal_serupa: "𝑟 𝑖 𝑔 ℎ 𝑡..." + "rightarrow" → "→"
  2. MLANJUT P1 learning soal/12 pilihan: huruf italic 𝑣/𝑤 → LaTeX $v_1$/$w_1$
  3. MTK P1 learning soal/38: 𝐴𝐵𝐶𝐷 italic → ABCD
  4. MTK P1 learning soal/5 + canonical q5: "$" lepas di deskripsi → "USD"
  5. FIS P2 learning soal 11 & 15: diketahui terpotong mid-LaTeX → dilengkapi
  6. Semua learning: full_display == "$" → dibangun dari field latex
  7. BI P2 SOLUTIONS: "rigℎta r row→" → "→"; "3,22tex t metrik..." → teks benar;
     salah gabung "30,96" → "30%–50% ... 96% paket"
  8. MTK P2 EXTRA SOLUTIONS sol17: delimiter $ salah tempat → dirapikan

Setiap file asli dicadangkan ke data/backup_render_fix_20260929/ dulu.
"""
import json
import os
import re
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
BACKUP = os.path.join(DATA, "backup_render_fix_20260929")
os.makedirs(BACKUP, exist_ok=True)

# Peta huruf italic matematis Unicode → ASCII
def _italic_map(c):
    o = ord(c)
    # Italic A-Z / a-z (KaTeX menghasilkan ini untuk variabel)
    if 0x1D434 <= o <= 0x1D44D:   return chr(65 + o - 0x1D434)
    if 0x1D44E <= o <= 0x1D467:   return chr(97 + o - 0x1D44E)
    # Bold A-Z / a-z
    if 0x1D400 <= o <= 0x1D419:   return chr(65 + o - 0x1D400)
    if 0x1D41A <= o <= 0x1D433:   return chr(97 + o - 0x1D41A)
    # Bold-Italic A-Z / a-z
    if 0x1D468 <= o <= 0x1D481:   return chr(65 + o - 0x1D468)
    if 0x1D482 <= o <= 0x1D49B:   return chr(97 + o - 0x1D482)
    # Digit (bold)
    if 0x1D7CE <= o <= 0x1D7D7:   return chr(48 + o - 0x1D7CE)
    if c == "\u210E": return "h"
    if c == "\u210F": return "h"
    if c == "\u2113": return "l"
    return c

def de_italic(s):
    return "".join(_italic_map(c) for c in s)

ARROW_JUNK = re.compile(r"(?:\s*[\U0001D400-\U0001D7FF\u210E\u210F]\s*)+\s*rightarrow\s*")
ARROW_JUNK2 = re.compile(r"\s*rigℎta r row→\s*")

def load(rel):
    return json.load(open(os.path.join(DATA, rel), encoding="utf-8"))

def save(rel, doc):
    path = os.path.join(DATA, rel)
    dst = os.path.join(BACKUP, rel.replace("\\", "__"))
    if not os.path.exists(dst):
        shutil.copy2(path, dst)
    json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

report = []

# ---------------------------------------------------------------- 1. BI P2 learning
rel = "bahasa_indonesia_paket_2_learning.json"
d = load(rel); n = 0
for p in d["soal"][8]["soal_serupa"]["pilihan"]:
    new = ARROW_JUNK.sub(" → ", p.get("text", ""))
    if new != p["text"]:
        p["text"] = re.sub(r"\s{2,}", " ", new).strip(); n += 1
if n: save(rel, d)
report.append((rel, f"soal_serupa q8: {n} pilihan dibersihkan (𝑟𝑖𝑔ℎ𝑡𝑎𝑟𝑟𝑜𝑤 rightarrow → '→')"))

# ------------------------------------------------------- 2. MLANJUT P1 soal/12
rel = "matematika_lanjut_paket_1_learning.json"
d = load(rel); n = 0
for p in d["soal"][12]["pilihan_jawaban"]:
    plain = de_italic(p.get("text", "")).replace("−", "-")
    m_v = re.search(r"v1\s*=\s*(-?\d+)", plain)
    m_w = re.search(r"w1\s*=\s*(-?\d+)", plain)
    if m_v and m_w:
        v, w = m_v.group(1), m_w.group(1)
        p["text"] = f"v1 = {v} dan w1 = {w}."
        p["full_display"] = f"{p['key']}. $v_1 = {v}$ dan $w_1 = {w}$."
        n += 1
if n: save(rel, d)
report.append((rel, f"soal/13 pilihan: {n} opsi italic 𝑣/𝑤 → LaTeX $v_1$/$w_1$"))

# ---------------------------------------------------------- 3. MTK P1 soal/38
rel = "matematika_paket_1_learning.json"
d = load(rel); n = 0
s38 = d["soal"][38]
for fld_path in (("pertanyaan", "text"), ("pertanyaan", "html")):
    val = s38.get(fld_path[0], {}).get(fld_path[1])
    if val and re.search(r"[\U0001D400-\U0001D7FF]", val):
        s38[fld_path[0]][fld_path[1]] = de_italic(val); n += 1
# 4. soal/5 stimulus.text: "$" lepas dalam deskripsi diagram
s5 = d["soal"][5]
st = s5.get("stimulus", {}).get("text", "")
if 'marked "$"' in st:
    s5["stimulus"]["text"] = st.replace('marked "$"', 'marked "USD"'); n += 1
if n: save(rel, d)
report.append((rel, f"soal/39 italic ABCD → ASCII + soal/6 '$' lepas → USD: {n} field"))

# ------------------------------------------------- 4b. canonical MTK P1 q5
rel = r"canonical_questions\matematika_paket_1.json"
d = load(rel); n = 0
for q in d["questions"]:
    stxt = q.get("stimulus_text") or ""
    if 'marked "$"' in stxt:
        q["stimulus_text"] = stxt.replace('marked "$"', 'marked "USD"'); n += 1
    for dg in (q.get("visual_context") or {}).get("diagrams") or []:
        ds = dg.get("description") or ""
        if 'marked "$"' in ds:
            dg["description"] = ds.replace('marked "$"', 'marked "USD"'); n += 1
if n: save(rel, d)
report.append((rel, f"q5 deskripsi diagram '$' lepas → USD: {n} field"))

# ------------------------------------------------------- 5. FIS P2 diketahui
rel = "fisika_paket_2_learning.json"
d = load(rel); n = 0
s = d["soal"][10]  # nomor 11 — kapal selam
if s["nomor"] == 11 and s["pembahasan"]["diketahui"].endswith("\\text{ kg/"):
    s["pembahasan"]["diketahui"] = (
        "Untuk membuat kapal selam terapung atau melayang mendekati permukaan laut, "
        "massa jenis rata-rata kapal selam harus sama dengan atau lebih kecil dari "
        "massa jenis air laut ($\\rho_{air} = 1.000\\text{ kg/m}^3$). Massa kapal selam "
        "$m = 200.000\\text{ kg}$ dan massa jenisnya saat di dasar laut "
        "$\\rho_{kapal} = 1.250\\text{ kg/m}^3$."
    ); n += 1
s = d["soal"][14]  # nomor 15 — gerak parabola
if s["nomor"] == 15 and s["pembahasan"]["diketahui"].endswith("$y = 3,05\\text"):
    s["pembahasan"]["diketahui"] = (
        "Dalam gerak parabola, lintasan proyektil sangat bergantung pada nilai kecepatan "
        "awal ($v_0$) dan sudut elevasi ($\\theta$). Untuk koordinat target ring basket "
        "tertentu ($x = 3\\text{ m}$, $y = 3,05\\text{ m}$), hasil tembakan ditentukan "
        "oleh besar kecepatan awal bola. Diketahui pula $\\sin(50°) = 0,766$ dan "
        "$\\cos(50°) = 0,643$."
    ); n += 1
if n: save(rel, d)
report.append((rel, f"diketahui terpotong soal 11 & 15 dilengkapi: {n} field"))

# ------------------------------------- 6. semua learning: full_display == "$"
LEARNING_FILES = [f for f in os.listdir(DATA) if f.endswith("_learning.json")]
n_total = 0
for fn in LEARNING_FILES:
    d = load(fn); n = 0
    for s in d.get("soal", []):
        for p in s.get("pilihan_jawaban") or []:
            if p.get("full_display") == "$" and p.get("latex"):
                p["full_display"] = f"${p['latex']}$"
                n += 1
    if n:
        save(fn, d); n_total += n
        report.append((fn, f"full_display '$' rusak → $latex$: {n} opsi"))
if not n_total:
    report.append(("-", "tidak ada full_display '$' lain"))

# ---------------------------------------------------- 7. BI P2 SOLUTIONS
rel = r"solution_sources\BAHASA_INDONESIA_PAKET_2_SOLUTIONS.json"
d = load(rel); n = 0
sol = d["solutions"][8]
new = ARROW_JUNK2.sub(" → ", sol["steps"][2]["explanation"])
if new != sol["steps"][2]["explanation"]:
    sol["steps"][2]["explanation"] = new; n += 1
sol = d["solutions"][12]
sol["diketahui"] = (
    "Opini penulis: 'Aktivitas manusia memberikan dampak besar terhadap pencemaran "
    "lingkungan di Indonesia.' Data dalam teks: peningkatan timbunan sampah medis "
    "sebesar 30% hingga 50%, 96% paket delivery makanan berbungkus plastik tebal & "
    "bubble wrap, dan Indonesia negara ke-2 penyumbang polusi sampah di lautan "
    "(3,22 metrik ton per tahun)."
); n += 1
expl = sol["steps"][2]["explanation"]
expl2 = expl.replace(
    "(3,22tex t metrik t onpertaℎu n 3,22 textmetriktonpertahun)",
    "(3,22 metrik ton per tahun)",
)
if expl2 != expl:
    sol["steps"][2]["explanation"] = expl2; n += 1
sol = d["solutions"][15]
new = ARROW_JUNK2.sub(" → ", sol["tips"][0])
if new != sol["tips"][0]:
    sol["tips"][0] = new; n += 1
if n: save(rel, d)
report.append((rel, f"rigℎta r row→'→', 'tex t metrik'→teks benar, '30,96'→'30%–50%/96%': {n} field"))

# ---------------------------------------------------- 8. MTK P2 EXTRA sol17
rel = r"solution_sources\MTK_PAKET_2_SOLUTIONS_EXTRA.json"
d = load(rel); n = 0
sol = d["solutions"][17]
old = sol["diketahui"]
new = old.replace(
    "20\\text{ cm} $\\times$ 30\\text{ cm}$",
    "$20\\text{ cm} \\times 30\\text{ cm}$",
)
if new != old:
    sol["diketahui"] = new; n += 1
if n: save(rel, d)
report.append((rel, "sol17 diketahui: delimiter $ salah tempat dirapikan"))

print("=== HASIL PERBAIKAN ===")
for rel, msg in report:
    print(f"[OK] {rel}: {msg}")
print(f"\nBackup → {BACKUP}")
