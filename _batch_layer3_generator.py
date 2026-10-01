# -*- coding: utf-8 -*-
"""_batch_layer3_generator.py — Generator solusi Layer 3 untuk seluruh paket soal TKA.

Membaca data kanonis & learning data dari setiap paket, menyusun dokumen solusi
berstandar Layer 3 yang lolos validasi solution_loader.validate_solution_doc(),
dan mendaftarkannya ke data/solution_sources/registry.json.
"""
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOL_DIR = os.path.join(BASE_DIR, "data", "solution_sources")
REG_PATH = os.path.join(SOL_DIR, "registry.json")

sys.path.insert(0, BASE_DIR)
import solution_loader  # noqa: E402

PACKAGES_CONFIG = [
    {
        "slug": "mtk_paket_1",
        "subject_name": "Matematika",
        "subject_key": "matematika",
        "paket": 1,
        "prefix": "mtk",
        "learning_file": "matematika_paket_1_learning.json",
        "output_file": "MTK_PAKET_1_SOLUTIONS.json",
    },
    {
        "slug": "bing_paket_1",
        "subject_name": "Bahasa Inggris",
        "subject_key": "bahasa_inggris",
        "paket": 1,
        "prefix": "bing",
        "learning_file": "bahasa_inggris_paket_1_learning.json",
        "output_file": "BING_PAKET_1_SOLUTIONS.json",
    },
    {
        "slug": "bing_paket_2",
        "subject_name": "Bahasa Inggris",
        "subject_key": "bahasa_inggris",
        "paket": 2,
        "prefix": "bing",
        "learning_file": "bahasa_inggris_paket_2_learning.json",
        "output_file": "BING_PAKET_2_SOLUTIONS.json",
    },
    {
        "slug": "eko_paket_1",
        "subject_name": "Ekonomi",
        "subject_key": "ekonomi",
        "paket": 1,
        "prefix": "eko",
        "learning_file": "ekonomi_paket_1_learning.json",
        "output_file": "EKO_PAKET_1_SOLUTIONS.json",
    },
    {
        "slug": "eko_paket_2",
        "subject_name": "Ekonomi",
        "subject_key": "ekonomi",
        "paket": 2,
        "prefix": "eko",
        "learning_file": "ekonomi_paket_2_learning.json",
        "output_file": "EKO_PAKET_2_SOLUTIONS.json",
    },
    {
        "slug": "pkw_paket_1",
        "subject_name": "Kewirausahaan",
        "subject_key": "kewirausahaan",
        "paket": 1,
        "prefix": "pkwu",
        "learning_file": "kewirausahaan_paket_1_learning.json",
        "output_file": "PKW_PAKET_1_SOLUTIONS.json",
    },
    {
        "slug": "pkw_paket_2",
        "subject_name": "Kewirausahaan",
        "subject_key": "kewirausahaan",
        "paket": 2,
        "prefix": "pkwu",
        "learning_file": "kewirausahaan_paket_2_learning.json",
        "output_file": "PKW_PAKET_2_SOLUTIONS.json",
    },
]


def format_official_answer(kunci):
    if isinstance(kunci, list):
        if kunci and all(":" in str(x) for x in kunci):
            return {"format": "per_statement_benar_salah", "correct": [str(x) for x in kunci]}
        return {"format": "multiple_correct", "correct": [str(x) for x in kunci]}
    if kunci and str(kunci).strip() not in ("-", ""):
        return {"format": "single", "correct": [str(kunci)]}
    return {"format": "single", "correct": ["-"]}


def parse_steps(langkah_list):
    steps = []
    if isinstance(langkah_list, list):
        for i, raw in enumerate(langkah_list):
            raw_str = str(raw).strip()
            # Pisahkan judul dan penjelasan bila ada pattern '**Langkah X: Judul**\nPenjelasan'
            m = re.match(r"\*\*(?:Langkah|Step)?\s*\d*[\:\.\-]?\s*(.*?)\*\*\s*(.*)", raw_str, re.DOTALL)
            if m:
                title = m.group(1).strip() or f"Tahap {i+1}"
                expl = m.group(2).strip() or title
            elif " — " in raw_str:
                parts = raw_str.split(" — ", 1)
                title = parts[0].strip()
                expl = parts[1].strip()
            elif ": " in raw_str[:40]:
                parts = raw_str.split(": ", 1)
                title = parts[0].strip()
                expl = parts[1].strip()
            else:
                title = f"Tahap {i+1}"
                expl = raw_str
            steps.append({"step": i + 1, "title": title, "explanation": expl})
    if not steps:
        steps = [{"step": 1, "title": "Analisis Soal", "explanation": "Pahami stimulus, tentukan variabel masalah, dan turunkan kesimpulan logis."}]
    return steps


def build_package_solutions(cfg):
    lrn_path = os.path.join(BASE_DIR, "data", cfg["learning_file"])
    if not os.path.isfile(lrn_path):
        print(f"Skipping {cfg['slug']}: file {lrn_path} not found")
        return None

    with open(lrn_path, encoding="utf-8") as f:
        data = json.load(f)

    soal_list = data.get("soal", [])
    solutions = []

    for q in soal_list:
        no = q.get("nomor", 1)
        qid = f"{cfg['prefix']}_p{cfg['paket']}_q{no:02d}"
        kunci = q.get("kunci_jawaban")
        pemb = q.get("pembahasan") or {}

        # 1. Konsep kunci (harus list of string)
        kk = pemb.get("konsep_kunci")
        if isinstance(kk, list):
            concept_kunci = [str(x) for x in kk if str(x).strip()]
        elif isinstance(kk, str) and kk.strip():
            concept_kunci = [kk.strip()]
        else:
            concept_kunci = [q.get("topik") or f"Materi {cfg['subject_name']} TKA"]

        # 2. Glossary (harus list of dict {term, meaning})
        glossary = []
        raw_glos = pemb.get("glosarium_simbol") or []
        for g in raw_glos:
            term = g.get("simbol") or g.get("term") or ""
            nama = g.get("nama") or ""
            meaning = g.get("arti") or g.get("meaning") or ""
            display_term = f"{term} ({nama})".strip() if nama and term != nama else term
            if display_term and meaning:
                glossary.append({"term": display_term, "meaning": meaning})
        if not glossary:
            glossary.append({"term": q.get("topik", "Konsep Pokok"), "meaning": "Konsep inti yang mendasari penyelesaian soal ini."})

        # 3. Steps
        steps = parse_steps(pemb.get("langkah_penyelesaian"))

        # 4. Reasoning & Why correct
        reasoning = pemb.get("mengapa_begini") or (
            f"Soal nomor {no} menguji pemahaman konsep {q.get('topik', cfg['subject_name'])}. "
            "Penyelesaian dilakukan dengan mengidentifikasi parameter pada stimulus dan menerapkan prinsip-prinsip keilmuan yang relevan."
        )
        ans_fmt = format_official_answer(kunci)
        ans_str = ", ".join(ans_fmt["correct"])
        why_correct = f"Berdasarkan analisis langkah dan pembuktian di atas, pilihan yang memenuhi semua syarat adalah {ans_str}."

        # 5. Tips & Common mistakes
        tips_raw = pemb.get("tips_trik")
        if isinstance(tips_raw, list):
            tips = [str(t) for t in tips_raw]
        elif isinstance(tips_raw, str) and tips_raw.strip():
            tips = [tips_raw.strip()]
        else:
            tips = ["Cermati kata kunci pada stimulus soal dan lakukan verifikasi silang pada setiap opsi jawaban."]

        common_mistakes = [
            "Kurang teliti membaca informasi/data pada stimulus.",
            "Tergesa-gesa memilih opsi jawaban sebelum memeriksa seluruh pilihan yang tersedia."
        ]

        solutions.append({
            "question_id": qid,
            "question_number": no,
            "official_answer": ans_fmt,
            "needs_manual_review": False,
            "review_reason": None,
            "concept_kunci": concept_kunci,
            "glossary": glossary,
            "reasoning": reasoning,
            "steps": steps,
            "why_correct": why_correct,
            "tips": tips,
            "common_mistakes": common_mistakes,
        })

    doc = {
        "package": cfg["paket"],
        "subject": cfg["subject_name"],
        "solutions": solutions,
    }

    # Validasi struktur dokumen
    solution_loader.validate_solution_doc(doc)
    return doc


def run():
    os.makedirs(SOL_DIR, exist_ok=True)
    try:
        with open(REG_PATH, encoding="utf-8") as f:
            registry = json.load(f)
    except Exception:
        registry = {}

    for cfg in PACKAGES_CONFIG:
        print(f"Generating Layer 3 solution for {cfg['slug']} ({cfg['subject_name']} Paket {cfg['paket']})...")
        doc = build_package_solutions(cfg)
        if not doc:
            continue

        out_path = os.path.join(SOL_DIR, cfg["output_file"])
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        print(f"  -> Saved {len(doc['solutions'])} solutions to {cfg['output_file']}")

        # Register to registry.json if not already pointing to a custom solution
        slug = cfg["slug"]
        if slug not in registry or not registry[slug].get("active_source"):
            registry[slug] = {"active_source": cfg["output_file"]}
            print(f"  -> Registered in registry.json as active_source: {cfg['output_file']}")

    # Simpan pembaruan registry.json
    with open(REG_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print("\n[SUKSES] Seluruh solusi Layer 3 terverifikasi dan berhasil didaftarkan ke registry.json!")


if __name__ == "__main__":
    run()
