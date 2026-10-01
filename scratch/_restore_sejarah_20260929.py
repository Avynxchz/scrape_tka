# -*- coding: utf-8 -*-
"""Restore A: SEJARAH_PAKET_2_SOLUTIONS.json aktif (terkontaminasi, 20 solusi)
<- backup_solutions_20260929 (benar, 29 solusi).
Langkah: backup-dulu file rusak ke data/backup_restore_sejarah_20260929/,
validasi backup (validate_solution_doc + jumlah + slug), timpa aktif,
verifikasi ulang, perbarui metadata registry total_questions 20->29."""
import json
import os
import shutil
import sys

sys.path.insert(0, r"D:\PROJECTS\SCRAPE_TKA")
from solution_loader import validate_solution_doc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"
ACT = os.path.join(DATA, "solution_sources", "SEJARAH_PAKET_2_SOLUTIONS.json")
BAK = os.path.join(DATA, "backup_solutions_20260929", "SEJARAH_PAKET_2_SOLUTIONS.json")
NEWBK = os.path.join(DATA, "backup_restore_sejarah_20260929")
REG = os.path.join(DATA, "solution_sources", "registry.json")

# 0. snapshot keadaan aktif (rusak) SEBELUM disentuh
os.makedirs(NEWBK, exist_ok=True)
dst = os.path.join(NEWBK, "SEJARAH_PAKET_2_SOLUTIONS.json")
shutil.copyfile(ACT, dst)
chk = json.load(open(dst, encoding="utf-8"))
print(f"[1] backup file rusak -> {os.path.relpath(dst, DATA)} "
      f"(solutions={len(chk.get('solutions', []))})")

# 1. validasi backup
doc = json.load(open(BAK, encoding="utf-8"))
validate_solution_doc(doc)
n = len(doc["solutions"])
qnums = [s["question_number"] for s in doc["solutions"]]
assert doc.get("slug") == "sejarah_paket_2", doc.get("slug")
assert n == 29 and qnums == list(range(1, 30)), (n, qnums)
q1 = doc["solutions"][0]
print(f"[2] backup valid: validate_solution_doc OK, solutions={n}, "
      f"q1 concept_kunci={q1.get('concept_kunci')}")

# 2. timpa aktif dengan backup
shutil.copyfile(BAK, ACT)

# 3. verifikasi file aktif pasca-tulis
d2 = json.load(open(ACT, encoding="utf-8"))
validate_solution_doc(d2)
raw = open(ACT, encoding="utf-8").read()
print(f"[3] aktif pasca-restore: solutions={len(d2['solutions'])} "
      f"slug={d2.get('slug')} U+00C2={raw.count(chr(0xC2))} "
      f"'Matriks dan.'={raw.count('Matriks dan.')} "
      f"q1={d2['solutions'][0].get('concept_kunci')}")
assert len(d2["solutions"]) == 29
assert raw.count(chr(0xC2)) == 0
assert "Matriks dan." not in raw

# 4. metadata registry: total_questions 20 -> 29 (round-trip terverifikasi identik)
reg = json.load(open(REG, encoding="utf-8"))
old = reg["sejarah_paket_2"].get("total_questions")
reg["sejarah_paket_2"]["total_questions"] = 29
tmp = REG + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(reg, f, ensure_ascii=False, indent=2)
os.replace(tmp, REG)
re_ = json.load(open(REG, encoding="utf-8"))
assert re_["sejarah_paket_2"]["active_source"] == "SEJARAH_PAKET_2_SOLUTIONS.json"
assert re_["sejarah_paket_2"]["total_questions"] == 29
print(f"[4] registry: total_questions {old} -> 29, active_source tetap "
      f"SEJARAH_PAKET_2_SOLUTIONS.json, JSON re-load OK")
print("RESTORE SELESAI + TERVERIFIKASI")
