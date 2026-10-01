# -*- coding: utf-8 -*-
"""_repair_text_quality.py — Perbaiki teks rusak hasil ekstraksi DOM pada data.

Menjalankan text_quality.repair_math_text pada seluruh field teks:
  - data/*_learning.json  : stimulus.text, pertanyaan.text, opsi, pernyataan
  - data/*_text_only.json : stimulus_text, pertanyaan_text, opsi, pernyataan
  - data/solution_sources/*.json : field Layer 3 (diketahui, reasoning, steps, ...)
  - data/*_sidecar_transcriptions.json : description

Idempoten: field yang sudah bersih tidak diubah. Semua file yang disentuh
dibackup dulu ke data/backup_text_repair_<tanggal>/.
"""
import json
import os
import re
import shutil
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import text_quality  # noqa: E402

DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
BACKUP_DIR = os.path.join(DATA_DIR, f"backup_text_repair_{time.strftime('%Y%m%d_%H%M%S')}")

_MATH_UNICODE = re.compile(r"[\U0001D400-\U0001D7FF]")
_SUSPECT_SHORT = re.compile(r"^[\s.,;:()\[\]{}=+\-–—±×≠≤≥·'\"?!]{1,2}$")


def needs_repair(text):
    """Deteksi teks rusak: unicode matematika, atau baris pecah pendek."""
    if not text or not isinstance(text, str) or "\n" not in text:
        return False
    if _MATH_UNICODE.search(text):
        return True
    short_run = 0
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if len(s) <= 2:
            short_run += 1
            if short_run >= 2:
                return True
            if _SUSPECT_SHORT.match(s):
                return True
        else:
            short_run = 0
    return False


def repair_field(obj, key):
    """Perbaiki obj[key] bila terdeteksi rusak. Return 1 bila berubah."""
    val = obj.get(key)
    if not needs_repair(val):
        return 0
    fixed = text_quality.repair_math_text(val)
    if fixed != val:
        obj[key] = fixed
        return 1
    return 0


def repair_learning_doc(doc):
    n = 0
    for q in doc.get("soal", []):
        n += repair_field(q.get("stimulus") or {}, "text")
        n += repair_field(q.get("pertanyaan") or {}, "text")
        for opt in (q.get("pilihan_jawaban") or []) + (q.get("pernyataan") or []):
            n += repair_field(opt, "text")
            n += repair_field(opt, "full_display")
    return n


def repair_text_only_doc(doc):
    n = 0
    for q in doc.get("soal", []):
        n += repair_field(q, "stimulus_text")
        n += repair_field(q, "pertanyaan_text")
        for opt in (q.get("options") or []) + (q.get("pernyataan") or []):
            n += repair_field(opt, "text")
            n += repair_field(opt, "full_display")
    return n


SOLUTION_TEXT_FIELDS = ("question_title", "diketahui", "ditanyakan",
                        "reasoning", "why_correct")


def repair_solution_doc(doc):
    n = 0
    for s in doc.get("solutions", []):
        for fld in SOLUTION_TEXT_FIELDS:
            n += repair_field(s, fld)
        for st in s.get("steps") or []:
            n += repair_field(st, "title")
            n += repair_field(st, "explanation")
        for lst_key in ("tips", "common_mistakes"):
            lst = s.get(lst_key)
            if isinstance(lst, list):
                for i, item in enumerate(lst):
                    if needs_repair(item):
                        fixed = text_quality.repair_math_text(item)
                        if fixed != item:
                            lst[i] = fixed
                            n += 1
        for g in s.get("glossary") or []:
            n += repair_field(g, "term")
            n += repair_field(g, "meaning")
    return n


def repair_sidecar_doc(doc):
    n = 0
    for entry in doc.values():
        if isinstance(entry, dict):
            n += repair_field(entry, "description")
    return n


def backup(path):
    rel = os.path.relpath(path, DATA_DIR)
    dest = os.path.join(BACKUP_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(path, dest)


def process(path, repairer):
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        print(f"  SKIP {os.path.basename(path)}: {e}")
        return 0
    n = repairer(doc)
    if n:
        backup(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"  {os.path.basename(path)}: {n} field diperbaiki")
    return n


def main():
    print(f"Backup dir: {BACKUP_DIR}")
    total = 0

    print("== Learning JSON ==")
    for fn in sorted(os.listdir(DATA_DIR)):
        if fn.endswith("_learning.json"):
            total += process(os.path.join(DATA_DIR, fn), repair_learning_doc)

    print("== Text-Only JSON ==")
    for fn in sorted(os.listdir(DATA_DIR)):
        if fn.endswith("_text_only.json"):
            total += process(os.path.join(DATA_DIR, fn), repair_text_only_doc)

    print("== Sidecar Transcriptions ==")
    for fn in sorted(os.listdir(DATA_DIR)):
        if fn.endswith("_sidecar_transcriptions.json"):
            total += process(os.path.join(DATA_DIR, fn), repair_sidecar_doc)

    print("== Solution Sources ==")
    if os.path.isdir(SOL_DIR):
        for fn in sorted(os.listdir(SOL_DIR)):
            if fn.endswith(".json") and fn != "registry.json":
                total += process(os.path.join(SOL_DIR, fn), repair_solution_doc)

    print(f"\nSELESAI. Total {total} field teks diperbaiki.")


if __name__ == "__main__":
    main()
