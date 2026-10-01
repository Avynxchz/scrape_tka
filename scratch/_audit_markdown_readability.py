# -*- coding: utf-8 -*-
"""_audit_markdown_readability.py — Scanner Audit Keterbacaan Presisi Tinggi.

Mendeteksi:
1. Header markdown mentah (^#{2,6}\s)
2. Tabel pipa markdown asli (memiliki baris pembatas |---|)
3. Preamble ekstraksi teknis AI ('Berikut adalah ekstraksi/analisis...', 'Transkripsi Rumus:')
4. Dua rumus inline berurutan tanpa jeda kata/baris baru ($a$ $b$)
5. Matriks ordo >=2x2 yang masih terjepit di dalam inline math ($...$) dan bukan display ($$...$$)
"""
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"D:\PROJECTS\SCRAPE_TKA"
DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
REG_PATH = os.path.join(SOL_DIR, "registry.json")

# Regex Presisi
MD_HEADER = re.compile(r"(?:^|\n)\s*#{2,6}\s")
MD_PIPE_TABLE = re.compile(r"(?:^|\n)\s*\|.+?\|.+?\|\s*\n\s*\|(?:\s*:?-+:?\s*\|)+", re.MULTILINE)
MD_PREAMBLE = re.compile(
    r"(?:^|\n)(?:Berikut\s+adalah\s+(?:analisis|ekstraksi|transkripsi|data|ringkasan)|Transkripsi\s+Rumus:)",
    re.IGNORECASE,
)
# Rumus inline beruntun: $a$ $b$ (bukan $$...$$) di baris yang sama
CONSEC_INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)[^\$\n]+?(?<!\$)\$(?!\$)\s+(?<!\$)\$(?!\$)[^\$\n]+?(?<!\$)\$(?!\$)")

# Matriks ordo >=2x2 di dalam inline math ($...$)
INLINE_MATRIX = re.compile(r"(?<!\$)\$(?!\$)[^\$\n]*?\\begin\{(?:p|b|B|v|V)matrix\}[\s\S]*?\\end\{(?:p|b|B|v|V)matrix\}[^\$\n]*?(?<!\$)\$(?!\$)")

registry = json.load(open(REG_PATH, encoding="utf-8"))
active_files = set()
for slug, v in registry.items():
    if isinstance(v, dict) and "active_source" in v:
        active_files.add(v["active_source"])

results = []

for fname in sorted(active_files):
    fpath = os.path.join(SOL_DIR, fname)
    if not os.path.isfile(fpath):
        continue

    doc = json.load(open(fpath, encoding="utf-8"))
    solutions = doc.get("solutions", [])

    for s in solutions:
        qnum = s.get("question_number")

        fields_to_check = {
            "diketahui": s.get("diketahui") or "",
            "ditanyakan": s.get("ditanyakan") or "",
            "reasoning": s.get("reasoning") or "",
            "why_correct": s.get("why_correct") or "",
        }
        for i, step in enumerate(s.get("steps", [])):
            if isinstance(step, dict):
                fields_to_check[f"steps[{i}].explanation"] = step.get("explanation") or ""
            elif isinstance(step, str):
                fields_to_check[f"steps[{i}]"] = step

        for fld, text in fields_to_check.items():
            if not text:
                continue
            issues = []
            if MD_HEADER.search(text):
                issues.append("md-header (###)")
            if MD_PIPE_TABLE.search(text):
                issues.append("md-pipe-table (|...|)")
            if MD_PREAMBLE.search(text):
                issues.append("preamble-ekstraksi")
            if CONSEC_INLINE_MATH.search(text):
                # Kecualikan jika hanya variabel kecil seperti "$x$ dan $y$" yang sudah dipisahkan kata
                # Regex CONSEC_INLINE_MATH hanya cocok jika berurutan langsung dengan spasi: "$a$ $b$"
                issues.append("consecutive-math ($a$ $b$)")
            if INLINE_MATRIX.search(text):
                issues.append("inline-matrix (harus $$)")

            if issues:
                results.append({
                    "file": fname,
                    "qnum": qnum,
                    "field": fld,
                    "issues": issues,
                    "snippet": text.replace("\n", " ⏎ ")[:140]
                })

print(f"\n=== HASIL AUDIT KETERBACAAN PRESISI ===")
print(f"Total temuan: {len(results)}")

by_file = {}
by_issue = {}
for r in results:
    by_file[r["file"]] = by_file.get(r["file"], 0) + 1
    for iss in r["issues"]:
        by_issue[iss] = by_issue.get(iss, 0) + 1

print("\n--- Ringkasan per Pola Masalah ---")
for k, v in sorted(by_issue.items(), key=lambda x: -x[1]):
    print(f"  {k:28s}: {v}")

print("\n--- Ringkasan per File Solusi ---")
for k, v in sorted(by_file.items(), key=lambda x: -x[1]):
    print(f"  {k:40s}: {v} temuan")

report_file = os.path.join(BASE_DIR, "scratch", "audit_keterbacaan_20260930.md")
with open(report_file, "w", encoding="utf-8") as rf:
    rf.write("# Laporan Audit Keterbacaan Presisi (2026-09-30)\n\n")
    rf.write(f"Total temuan: {len(results)} pada {len(by_file)} file.\n\n")
    rf.write("## Ringkasan per Isu\n")
    for k, v in sorted(by_issue.items(), key=lambda x: -x[1]):
        rf.write(f"- **{k}**: {v}\n")
    rf.write("\n## Ringkasan per File\n")
    for k, v in sorted(by_file.items(), key=lambda x: -x[1]):
        rf.write(f"- `{k}`: {v}\n")
    rf.write("\n## Daftar Detail Temuan\n")
    for r in results:
        rf.write(f"- `{r['file']}` Q{r['qnum']} [{r['field']}] -> {', '.join(r['issues'])}\n")
        rf.write(f"  - Cuplikan: `{r['snippet']}`\n\n")

print(f"\nLaporan lengkap tersimpan di: {report_file}")
