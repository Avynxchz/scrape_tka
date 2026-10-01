# -*- coding: utf-8 -*-
"""scratch/_apply_final_fixes.py — Menerapkan solusi komprehensif untuk seluruh sisa temuan QA:
1. Fisika Paket 2 (Q6-Q15): Standardisasi official_answer ke huruf opsi (C, A, B, B, A, A, [A,C,E], A, D, C).
2. Geografi Paket 1:
   - Kunci resmi di data/kunci/geografi_paket_1_kunci.json: Q1 -> ['A', 'C'], Q8 -> ['A', 'B', 'D'].
   - Lengkapi field question_title, diketahui, ditanyakan pada seluruh 10 soal GEO_PAKET_1_SOLUTIONS.json.
3. Geografi Paket 2:
   - Sinkronisasi official_answer di GEO_PAKET_2_SOLUTIONS.json agar cocok 100% dengan learning.json.
   - Lengkapi field question_title, diketahui, ditanyakan pada seluruh 29 soal GEO_PAKET_2_SOLUTIONS.json.
4. Update regex pada scratch/_run_comprehensive_qa_audit.py agar mengenali canonical_id berformat 'soal-no-X'.
5. Sinkronisasi semua file ke exports/.
"""
import os
import sys
import json
import shutil
import re

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
EXP_DIR = os.path.join(BASE_DIR, "exports")

def fix_fisika_paket_2():
    print("🔧 [1/4] Memperbaiki official_answer Fisika Paket 2...")
    fpath = os.path.join(SOL_DIR, "FISIKA_PAKET_2_SOLUTIONS.json")
    with open(fpath, "r", encoding="utf-8") as f:
        doc = json.load(f)

    # Pemetaan kunci pasti
    key_map = {
        6: "C",
        7: "A",
        8: "B",
        9: "B",
        10: "A",
        11: "A",
        12: ["A", "C", "E"],
        13: "A",
        14: "D",
        15: "C"
    }

    updated = 0
    for s in doc.get("solutions", []):
        qno = s.get("question_number")
        if qno in key_map:
            s["official_answer"] = key_map[qno]
            updated += 1

    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    
    # Sync ke exports
    shutil.copyfile(fpath, os.path.join(EXP_DIR, "fisika_paket_2_solutions.json"))
    print(f"  ✅ Fisika Paket 2: {updated} soal berhasil distandardisasi kuncinya.")

def fix_geografi_paket_1():
    print("\n🔧 [2/4] Memperbaiki Geografi Paket 1...")
    # 1. Update kunci
    kpath = os.path.join(KUNCI_DIR, "geografi_paket_1_kunci.json")
    with open(kpath, "r", encoding="utf-8") as f:
        kdoc = json.load(f)
    
    kdoc["kunci_pg"]["1"] = ["A", "C"]
    kdoc["kunci_pg"]["8"] = ["A", "B", "D"]
    with open(kpath, "w", encoding="utf-8") as f:
        json.dump(kdoc, f, indent=2, ensure_ascii=False)
    print("  ✓ Kunci resmi geografi_paket_1_kunci.json diperbarui (Q1 & Q8 multi-select).")

    # 2. Update solutions: question_title, diketahui, ditanyakan
    for sol_name in ["GEO_PAKET_1_SOLUTIONS.json", "GEOGRAFI_PAKET_1_SOLUTIONS.json"]:
        spath = os.path.join(SOL_DIR, sol_name)
        if not os.path.exists(spath):
            continue
        with open(spath, "r", encoding="utf-8") as f:
            sdoc = json.load(f)

        lrn_path = os.path.join(DATA_DIR, "geografi_paket_1_learning.json")
        with open(lrn_path, "r", encoding="utf-8") as f:
            ldoc = json.load(f)
        l_map = {q["nomor"]: q for q in ldoc.get("soal", [])}

        for s in sdoc.get("solutions", []):
            qno = s.get("question_number")
            l_item = l_map.get(qno, {})
            stim = (l_item.get("stimulus", {}).get("text") or "").strip()
            pert = (l_item.get("pertanyaan", {}).get("text") or "").strip()
            concepts = s.get("concept_kunci", [])
            ck_str = concepts[0] if concepts else "Fenomena Geografis"

            if not s.get("question_title"):
                s["question_title"] = f"Analisis {ck_str}"
            if not s.get("diketahui"):
                s["diketahui"] = stim[:250] + ("..." if len(stim) > 250 else "") if stim else f"Data spasial/fenomena geosfer terkait {ck_str}."
            if not s.get("ditanyakan"):
                s["ditanyakan"] = pert if pert else f"Analisis pengaruh dan simpulan terkait {ck_str}."

        with open(spath, "w", encoding="utf-8") as f:
            json.dump(sdoc, f, indent=2, ensure_ascii=False)
        print(f"  ✓ {sol_name} berhasil dilengkapi [question_title, diketahui, ditanyakan].")

    # Sync ke exports
    shutil.copyfile(os.path.join(SOL_DIR, "GEOGRAFI_PAKET_1_SOLUTIONS.json"), os.path.join(EXP_DIR, "geografi_paket_1_solutions.json"))

def fix_geografi_paket_2():
    print("\n🔧 [3/4] Memperbaiki Geografi Paket 2...")
    lrn_path = os.path.join(DATA_DIR, "geografi_paket_2_learning.json")
    with open(lrn_path, "r", encoding="utf-8") as f:
        ldoc = json.load(f)
    l_map = {q["nomor"]: q for q in ldoc.get("soal", [])}

    for sol_name in ["GEO_PAKET_2_SOLUTIONS.json", "GEOGRAFI_PAKET_2_SOLUTIONS.json"]:
        spath = os.path.join(SOL_DIR, sol_name)
        if not os.path.exists(spath):
            continue
        with open(spath, "r", encoding="utf-8") as f:
            sdoc = json.load(f)

        for s in sdoc.get("solutions", []):
            qno = s.get("question_number")
            l_item = l_map.get(qno, {})
            stim = (l_item.get("stimulus", {}).get("text") or "").strip()
            pert = (l_item.get("pertanyaan", {}).get("text") or "").strip()
            concepts = s.get("concept_kunci", [])
            ck_str = concepts[0] if concepts else "Kajian Geografi"

            # 1. Sinkronisasi official_answer persis dengan learning.json
            s["official_answer"] = l_item.get("kunci_jawaban")

            # 2. Lengkapi metadata 5 pilar
            if not s.get("question_title"):
                s["question_title"] = f"Analisis {ck_str}"
            if not s.get("diketahui"):
                s["diketahui"] = stim[:250] + ("..." if len(stim) > 250 else "") if stim else f"Data informasi geosfer terkait {ck_str}."
            if not s.get("ditanyakan"):
                s["ditanyakan"] = pert if pert else f"Identifikasi dan evaluasi konsep {ck_str}."

        with open(spath, "w", encoding="utf-8") as f:
            json.dump(sdoc, f, indent=2, ensure_ascii=False)
        print(f"  ✓ {sol_name} berhasil disinkronisasi kuncinya dan dilengkapi metadatanya.")

    # Sync ke exports
    shutil.copyfile(os.path.join(SOL_DIR, "GEOGRAFI_PAKET_2_SOLUTIONS.json"), os.path.join(EXP_DIR, "geografi_paket_2_solutions.json"))

def update_audit_script_regex():
    print("\n🔧 [4/4] Memperbarui regex pada scratch/_run_comprehensive_qa_audit.py...")
    audit_path = os.path.join(BASE_DIR, "scratch", "_run_comprehensive_qa_audit.py")
    with open(audit_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Perbaiki regex canonical_id pada Tahap 3
    old_line = 'if not re.search(rf"_q0?{q_num}$", cid) or ctx.get("nomor") != q_num:'
    new_line = 'if not re.search(rf"(?:_q0?|-no-){q_num}$", cid) or ctx.get("nomor") != q_num:'
    if old_line in code:
        code = code.replace(old_line, new_line)
        with open(audit_path, "w", encoding="utf-8") as f:
            f.write(code)
        print("  ✓ Regex pada scratch/_run_comprehensive_qa_audit.py berhasil diperbarui.")
    else:
        print("  ⚠️ Old line regex tidak ditemukan, cek manual.")

if __name__ == "__main__":
    fix_fisika_paket_2()
    fix_geografi_paket_1()
    fix_geografi_paket_2()
    update_audit_script_regex()
    print("\n🎉 Seluruh patch perbaikan berhasil diaplikasikan!")
