# -*- coding: utf-8 -*-
"""pipeline/02_generate_solutions_kimia_biologi.py — Automated 5-Pillar Layer 3 Generator.

Generates 5-pillar pedagogical solutions for Kimia & Biologi using Gemini 3 Flash / Gemini Pro
via micro-batching with strict official key adherence and multimodal diagram vision.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import re
import json
import time
import argparse
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.insert(0, BASE_DIR)

import tutor_llm
import solution_loader

DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
REG_PATH = os.path.join(SOL_DIR, "registry.json")
os.makedirs(SOL_DIR, exist_ok=True)

TARGET_CONFIGS = {
    "kimia_paket_1": {
        "slug": "kimia_paket_1",
        "subject_name": "Kimia",
        "paket": 1,
        "prefix": "kim",
        "learning_file": "kimia_paket_1_learning.json",
        "kunci_file": "kimia_paket_1_kunci.json",
        "output_file": "KIMIA_PAKET_1_SOLUTIONS.json",
        "images_dir": os.path.join(DATA_DIR, "kimia", "paket_1", "images")
    },
    "kimia_paket_2": {
        "slug": "kimia_paket_2",
        "subject_name": "Kimia",
        "paket": 2,
        "prefix": "kim",
        "learning_file": "kimia_paket_2_learning.json",
        "kunci_file": "kimia_paket_2_kunci.json",
        "output_file": "KIMIA_PAKET_2_SOLUTIONS.json",
        "images_dir": os.path.join(DATA_DIR, "kimia", "paket_2", "images")
    },
    "biologi_paket_1": {
        "slug": "biologi_paket_1",
        "subject_name": "Biologi",
        "paket": 1,
        "prefix": "bio",
        "learning_file": "biologi_paket_1_learning.json",
        "kunci_file": "biologi_paket_1_kunci.json",
        "output_file": "BIOLOGI_PAKET_1_SOLUTIONS.json",
        "images_dir": os.path.join(DATA_DIR, "biologi", "paket_1", "images")
    },
    "biologi_paket_2": {
        "slug": "biologi_paket_2",
        "subject_name": "Biologi",
        "paket": 2,
        "prefix": "bio",
        "learning_file": "biologi_paket_2_learning.json",
        "kunci_file": "biologi_paket_2_kunci.json",
        "output_file": "BIOLOGI_PAKET_2_SOLUTIONS.json",
        "images_dir": os.path.join(DATA_DIR, "biologi", "paket_2", "images")
    }
}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def safe_parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        pass

    # Double unescaped backslashes from LaTeX (e.g. \text, \Delta, \rightarrow)
    fixed = re.sub(r'\\(?!["\\])', r'\\\\', text)
    try:
        return json.loads(fixed, strict=False)
    except json.JSONDecodeError:
        pass

    # Fallback: escape all backslashes except those before quotes
    fixed2 = re.sub(r'\\(?!")', r'\\\\', text)
    return json.loads(fixed2, strict=False)


def build_batch_prompt(subject_name, batch_questions, batch_kunci):
    q_texts = []
    for q in batch_questions:
        no = q["nomor"]
        no_s = str(no)
        kunci = batch_kunci.get(no_s, q.get("kunci_jawaban", "-"))

        stimulus = q.get("stimulus", {}).get("text", "").strip()
        soal = q.get("pertanyaan", {}).get("text", "").strip()

        items_desc = []
        if q.get("pernyataan"):
            for p in q["pernyataan"]:
                items_desc.append(f"  - {p.get('key')}. {p.get('text')}")
        elif q.get("pilihan_jawaban"):
            for opt in q["pilihan_jawaban"]:
                txt = opt.get("full_display") or opt.get("text") or ""
                items_desc.append(f"  - {opt.get('key')}. {txt}")

        items_str = "\n".join(items_desc) if items_desc else "(Tidak ada pilihan eksplisit)"

        q_block = f"""---
[SOAL NOMOR {no}]
Tipe: {q.get('tipe_soal', 'Pilihan Ganda')}
Kunci Resmi Pusmendik (MUTLAK): {kunci}
Stimulus:
{stimulus or '(Tidak ada teks stimulus - lihat diagram/gambar)'}

Pertanyaan:
{soal}

Pilihan / Pernyataan:
{items_str}
"""
        q_texts.append(q_block)

    prompt = f"""Kamu adalah Pakar Edukasi dan Master Guru {subject_name} untuk Tes Kemampuan Akademik (TKA) SMA Pusmendik Kemdikbud.
Tugasmu adalah menyusun pembahasan pedagogis 5 PILAR yang sangat mendalam, jelas, dan manusiawi untuk soal-soal berikut.

ATURAN WAJIB & STRICT CONSTRAINTS:
1. KUNCI RESMI PUSMENDIK ADALAH MUTLAK (SINGLE GROUND TRUTH). Kamu WAJIB membuktikan dan menjelaskan secara ilmiah mengapa kunci tersebut benar. DILARANG KERAS mengubah atau membantah kunci resmi.
2. Jelaskan langkah-langkah secara sistematis menggunakan formula, hukum konsep, dan logika sains yang kuat.
3. Notasi matematika/rumus kimia gunakan format KaTeX: `$rumus$` untuk inline dan `$$rumus$$` untuk baris mandiri.
4. Output WAJIB berupa JSON ARRAY yang valid, tanpa teks pengantar atau penutup apapun selain JSON!

FORMAT JSON PER ELEMEN SOAL:
{{
  "question_number": <nomor_soal>,
  "concept_kunci": ["<Konsep 1>", "<Konsep 2>"],
  "glossary": [
    {{"term": "<Istilah/Simbol>", "meaning": "<Penjelasan arti ringkas>"}}
  ],
  "diketahui": "<Variabel dan data yang diketahui dari soal/gambar>",
  "ditanyakan": "<Inti hal yang ditanyakan soal>",
  "reasoning": "<Uraian penalaran ilmiah mendasar yang melandasi permasalahan ini>",
  "steps": [
    {{"step": 1, "title": "<Judul Tahap 1>", "explanation": "<Penjelasan langkah rinci>"}},
    {{"step": 2, "title": "<Judul Tahap 2>", "explanation": "<Penjelasan langkah rinci>"}}
  ],
  "why_correct": "<Penjelasan gamblang mengapa kunci resmi tersebut adalah opsi yang benar>",
  "tips": ["<Tips cepat atau metode praktis untuk mengingat konsep ini>"],
  "common_mistakes": ["<Jebakan umum atau kesalahan fatal yang sering dialami siswa>"]
}}

DAFTAR SOAL YANG HARUS DIBUATKAN SOLUSI:
{"".join(q_texts)}
"""
    return prompt


def generate_solutions_for_target(cfg, batch_size=4):
    slug = cfg["slug"]
    subj = cfg["subject_name"]
    paket = cfg["paket"]
    prefix = cfg["prefix"]

    log(f"==================================================================")
    log(f"🧠 MEMULAI GENERASI SOLUSI 5 PILAR LAYER 3: {subj} Paket {paket}")
    log(f"==================================================================")

    lrn_path = os.path.join(DATA_DIR, cfg["learning_file"])
    kunci_path = os.path.join(DATA_DIR, "kunci", cfg["kunci_file"])

    with open(lrn_path, "r", encoding="utf-8") as f:
        lrn_data = json.load(f)
    with open(kunci_path, "r", encoding="utf-8") as f:
        kunci_data = json.load(f)

    questions = lrn_data.get("soal", [])
    total_q = len(questions)
    log(f"Total soal terdeteksi: {total_q}")

    # Gabungkan kunci resmi
    kunci_map = {}
    for k, v in kunci_data.get("kunci_pg", {}).items():
        kunci_map[str(k)] = v
    for k, v in kunci_data.get("kunci_bs", {}).items():
        kunci_map[str(k)] = [f"{k_}:{v_}" for k_, v_ in sorted(v.items())]

    all_solutions = []

    # Bagi ke micro-batches
    batches = [questions[i:i + batch_size] for i in range(0, total_q, batch_size)]
    log(f"Dibagi menjadi {len(batches)} micro-batches (ukuran batch: {batch_size})...")

    for b_idx, batch in enumerate(batches, 1):
        q_start = batch[0]["nomor"]
        q_end = batch[-1]["nomor"]
        log(f"\n--- Memproses Batch {b_idx}/{len(batches)} (Soal {q_start}-{q_end}) ---")

        # Kumpulkan gambar untuk batch ini
        batch_images = []
        for q in batch:
            for im in q.get("stimulus", {}).get("images", []) + q.get("pertanyaan", {}).get("images", []):
                fn = im.get("filename")
                if fn:
                    local_img = os.path.join(cfg["images_dir"], fn)
                    if os.path.isfile(local_img) and local_img not in batch_images:
                        batch_images.append(local_img)

        prompt = build_batch_prompt(subj, batch, kunci_map)

        for attempt in range(1, 4):
            try:
                log(f"  Mengirim prompt ke Gemini 3 Flash (Attempt {attempt}, Lampiran gambar: {len(batch_images)})...")
                reply_text, model_used = tutor_llm._post_gemini(
                    messages=[{"role": "user", "content": prompt}],
                    model_choice="gemini-flash",
                    image_paths=batch_images,
                    temperature=0.3,
                    max_tokens=4096,
                    timeout=90
                )
                batch_sol_list = safe_parse_json(reply_text)
                if not isinstance(batch_sol_list, list):
                    raise ValueError("Hasil AI bukan JSON list!")

                # Normalisasi ID & official_answer format
                for sol_item in batch_sol_list:
                    no = sol_item.get("question_number")
                    no_s = str(no)
                    sol_item["question_id"] = f"{prefix}_p{paket}_q{no:02d}"
                    raw_kunci = kunci_map.get(no_s, "-")

                    if isinstance(raw_kunci, list):
                        if raw_kunci and all(":" in str(x) for x in raw_kunci):
                            ans_fmt = {"format": "per_statement_benar_salah", "correct": [str(x) for x in raw_kunci]}
                        else:
                            ans_fmt = {"format": "multiple_correct", "correct": [str(x) for x in raw_kunci]}
                    else:
                        ans_fmt = {"format": "single", "correct": [str(raw_kunci)]}

                    sol_item["official_answer"] = ans_fmt
                    sol_item["needs_manual_review"] = False
                    sol_item["review_reason"] = None
                    if not sol_item.get("reasoning"):
                        sol_item["reasoning"] = sol_item.get("why_correct") or f"Penalaran soal {no} berdasarkan konsep {subj}."
                    if not sol_item.get("concept_kunci"):
                        sol_item["concept_kunci"] = [f"Konsep {subj} Soal {no}"]
                    if not sol_item.get("glossary"):
                        sol_item["glossary"] = [{"term": subj, "meaning": f"Disiplin ilmu {subj}"}]
                    if not sol_item.get("tips"):
                        sol_item["tips"] = ["Periksa kembali data pada stimulus dan teliti setiap opsi jawaban."]
                    if not sol_item.get("common_mistakes"):
                        sol_item["common_mistakes"] = ["Terburu-buru memilih opsi sebelum memeriksa seluruh data."]
                    all_solutions.append(sol_item)

                log(f"  ✅ Batch {b_idx} SUKSES! ({len(batch_sol_list)} solusi dihasilkan oleh {model_used})")
                break
            except Exception as e:
                log(f"  ❌ Gagal memproses batch {b_idx} (attempt {attempt}): {e}")
                time.sleep(3)
        else:
            raise RuntimeError(f"Gagal memproses batch {b_idx} setelah 3 percobaan!")

    # Validasi seluruh dokumen solusi
    final_doc = {
        "package": paket,
        "subject": subj,
        "solutions": sorted(all_solutions, key=lambda x: x.get("question_number", 0))
    }

    log("\nMemvalidasi struktur dokumen via solution_loader...")
    solution_loader.validate_solution_doc(final_doc)
    log("✅ Validasi skema 5 pilar lolos 100%!")

    # Simpan file solusi
    out_path = os.path.join(SOL_DIR, cfg["output_file"])
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_doc, f, indent=2, ensure_ascii=False)
    log(f"Solusi Layer 3 berhasil disimpan ke {out_path}")

    # Daftarkan ke registry.json
    with open(REG_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    reg_key = f"{prefix}_paket_{paket}"
    registry[reg_key] = {"active_source": cfg["output_file"]}
    with open(REG_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    log(f"✅ Berhasil didaftarkan ke registry.json dengan key: '{reg_key}' -> '{cfg['output_file']}'\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 5-Pillar Layer 3 Solutions")
    parser.add_argument("--target", type=str, default="all",
                        choices=["all", "kimia_paket_1", "kimia_paket_2", "biologi_paket_1", "biologi_paket_2"])
    args = parser.parse_args()

    targets = list(TARGET_CONFIGS.keys()) if args.target == "all" else [args.target]
    for t_slug in targets:
        generate_solutions_for_target(TARGET_CONFIGS[t_slug])
    log("🎉 [SELESAI] Seluruh solusi 5 pilar Layer 3 telah tuntas dihasilkan dan divalidasi!")
