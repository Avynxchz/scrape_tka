# -*- coding: utf-8 -*-
"""_fix_kunci_matrix_misfire.py — Perbaiki kunci PG multi-jawaban yang salah
terbaca sebagai matriks Benar-Salah oleh _parse_review_kunci.

Pola korban: kunci resmi "(C)\\nDanau C\\n(D)\\nDanau D\\n(E)\\nDanau E"
(ikut serta C, D, E) terparse jadi kunci_bs {C:'D', D:'E'} karena regex
matriks menangkap huruf terakhir teks opsi sebelum kurung berikutnya.

Deteksi sempit: entri kunci_bs yang SEMUA nilainya huruf tunggal A-E.
Perbaikan: turunkan kembali kunci_pg dari raw_rows, hapus kunci_bs, lalu
sinkronkan learning JSON (kunci_jawaban) dan file solusi (official_answer).
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
LRN_DIR = DATA_DIR

SINGLE_LETTER = re.compile(r"^[A-E]$")
EXPLICIT_LETTERS = re.compile(r"\(\s*([A-E])\s*\)")


def is_misfire(kunci_bs):
    if not kunci_bs:
        return False
    return all(SINGLE_LETTER.match(str(v).strip().upper()) for v in kunci_bs.values())


def fix_kunci_doc(path):
    changed = []
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    for no, bs in list(doc.get("kunci_bs", {}).items()):
        if not is_misfire(bs):
            continue
        raw = doc.get("raw_rows", {}).get(no, {}).get("kunci", "")
        letters = EXPLICIT_LETTERS.findall(raw)
        if not letters:
            continue
        new_kunci = letters if len(letters) > 1 else letters[0]
        doc["kunci_pg"][no] = new_kunci
        del doc["kunci_bs"][no]
        changed.append((no, bs, new_kunci))
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    return changed


def fix_learning(path, changed_nos):
    if not changed_nos:
        return 0
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    n = 0
    for q in doc.get("soal", []):
        no = str(q.get("nomor"))
        if no in changed_nos:
            q["kunci_jawaban"] = changed_nos[no]
            n += 1
    if n:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    return n


def fix_solutions(path, changed_nos):
    if not changed_nos:
        return 0
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    n = 0
    for s in doc.get("solutions", []):
        no = str(s.get("question_number"))
        if no in changed_nos:
            k = changed_nos[no]
            if isinstance(k, list):
                s["official_answer"] = {"format": "multiple_correct", "correct": k}
            else:
                s["official_answer"] = {"format": "single_choice", "correct": k}
            n += 1
    if n:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    return n


def main():
    total = 0
    for fn in sorted(os.listdir(KUNCI_DIR)):
        if not fn.endswith("_kunci.json"):
            continue
        slug = fn[:-len("_kunci.json")]
        path = os.path.join(KUNCI_DIR, fn)
        changed_list = fix_kunci_doc(path)
        if not changed_list:
            continue
        changed_nos = {no: k for no, _old, k in changed_list}
        print(f"{slug}: {len(changed_list)} kunci diperbaiki:")
        for no, old, new in changed_list:
            print(f"  Q{no}: {old} -> {new}")
        n1 = fix_learning(os.path.join(LRN_DIR, f"{slug}_learning.json"), changed_nos)
        n2 = fix_solutions(os.path.join(SOL_DIR, f"{slug.upper()}_SOLUTIONS.json"), changed_nos)
        print(f"  learning: {n1} soal, solutions: {n2} official_answer diperbarui")
        total += len(changed_list)
    print(f"\nSELESAI. {total} kunci diperbaiki.")


if __name__ == "__main__":
    main()
