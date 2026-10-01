# -*- coding: utf-8 -*-
"""ingest_geografi_solutions.py — Ingestion, schema validation, and key auditing for Geografi Paket 1."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import solution_loader
from _repair_keys import parse_official_row

KUNCI_PATH = os.path.join(ROOT, "data", "kunci", "geografi_paket_1_kunci.json")
SOLUTIONS_PATH = os.path.join(ROOT, "data", "solution_sources", "GEO_PAKET_1_SOLUTIONS.json")
REGISTRY_PATH = os.path.join(ROOT, "data", "solution_sources", "registry.json")


def audit_and_ingest(input_data):
    """Takes input_data (file path or dict), validates schema, cross-checks keys,

    saves to GEO_PAKET_1_SOLUTIONS.json, and registers in registry.json.
    """
    if isinstance(input_data, str):
        if os.path.isfile(input_data):
            with open(input_data, encoding="utf-8") as f:
                doc = json.load(f)
        else:
            doc = json.loads(input_data)
    else:
        doc = input_data

    # 1. Structural Validation via solution_loader
    solution_loader.validate_solution_doc(doc)

    # 2. Check 5 Pillars & soal_serupa for every question
    required_pillars = [
        "concept_kunci", "glossary", "reasoning", "steps",
        "why_correct", "tips", "common_mistakes", "soal_serupa"
    ]
    for s in doc["solutions"]:
        qid = s["question_id"]
        for p in required_pillars:
            if p not in s:
                raise ValueError(f"Soal {qid} tidak memiliki field '{p}'")

        # Steps validation
        steps = s["steps"]
        if not isinstance(steps, list) or len(steps) < 2:
            raise ValueError(f"Soal {qid} 'steps' harus berupa list minimal 2 tahap")
        for st in steps:
            for k in ("step", "title", "explanation"):
                if k not in st:
                    raise ValueError(f"Soal {qid} step missing key '{k}'")

        # soal_serupa validation
        sim = s["soal_serupa"]
        for k in ("pertanyaan", "opsi", "kunci", "pembahasan_singkat"):
            if k not in sim:
                raise ValueError(f"Soal {qid} soal_serupa missing key '{k}'")
        if not isinstance(sim["opsi"], list) or len(sim["opsi"]) < 4:
            raise ValueError(f"Soal {qid} soal_serupa 'opsi' minimal 4 opsi (A-D)")

    # 3. Authoritative Key Cross-Check
    with open(KUNCI_PATH, encoding="utf-8") as f:
        kunci_data = json.load(f)
    raw_rows = kunci_data["raw_rows"]

    audit_report = []
    all_matched = True

    for s in doc["solutions"]:
        qnum = s["question_number"]
        row = raw_rows.get(str(qnum))
        if not row:
            raise ValueError(f"Tidak ada bukti resmi untuk soal {qnum}")

        kind, payload = parse_official_row(row["kunci"])
        sol_ans = s.get("official_answer", {})

        matched = False
        if kind == "bs":
            # payload is dict {'A': 'Benar', ...}
            sol_stmts = sol_ans.get("statements", {})
            if sol_stmts == payload:
                matched = True
        elif kind == "multi":
            sol_correct = sorted(sol_ans.get("correct", []))
            if sol_correct == sorted(payload):
                matched = True
        elif kind == "single":
            sol_correct = sol_ans.get("correct", [])
            if sol_correct == payload:
                matched = True

        if not matched:
            all_matched = False
            s["needs_manual_review"] = True
            s["review_reason"] = f"Official key mismatch: sol={sol_ans} vs evidence={payload}"
            audit_report.append(f"[MISMATCH] Soal {qnum}: sol={sol_ans} vs evidence={payload} -> flagged")
        else:
            s["needs_manual_review"] = False
            audit_report.append(f"[MATCH OK] Soal {qnum}: kunci resmi {payload} terverifikasi 100%")

    # 4. Save to destination
    with open(SOLUTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"File tersimpan di: {SOLUTIONS_PATH}")

    # 5. Register in registry.json
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        reg = json.load(f)
    reg["geo_paket_1"] = {
        "active_source": "GEO_PAKET_1_SOLUTIONS.json"
    }
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    print("Berhasil didaftarkan ke data/solution_sources/registry.json!")

    for r in audit_report:
        print(f"  {r}")
    print(f"\nStatus: {'SEMUA KUNCI COCOK (100% PASS)' if all_matched else 'ADA MISMATCH (REVIEW REQUIRED)'}")
    return all_matched


if __name__ == "__main__":
    if len(sys.argv) > 1:
        audit_and_ingest(sys.argv[1])
    else:
        print("Usage: python scratch/ingest_geografi_solutions.py <path_to_json_file>")
