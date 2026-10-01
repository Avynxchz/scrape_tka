# -*- coding: utf-8 -*-
"""gemini_reasoner.py — Automated Reasoning Engine using Google Gemini Flash.
Executes micro-batch reasoning prompts from claude_input/ and ingests to claude_output/ & data/solution_sources/.
"""
import os
import re
import json
import time
import traceback
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

MODELS_ORDER = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3-flash-preview",
]

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan di .env!")
    from google import genai
    return genai.Client(api_key=api_key)

def clean_json_text(text):
    """Strip markdown code fences and whitespace."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()

def call_gemini_with_failover(client, prompt_text, logger=None, max_retries_per_model=2):
    """Call Gemini Flash with automatic failover across models and exponential backoff on 429/503."""
    last_err = None
    for model_name in MODELS_ORDER:
        for attempt in range(max_retries_per_model):
            try:
                if logger:
                    logger("GEMINI", f"Calling {model_name} (Attempt {attempt+1})...", "info")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text
                )
                if response and response.text:
                    return response.text, model_name
            except Exception as e:
                last_err = e
                err_msg = str(e)
                is_rate_limit = "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg
                is_busy = "503" in err_msg or "UNAVAILABLE" in err_msg
                if is_rate_limit or is_busy:
                    wait_time = 4 * (attempt + 1)
                    if logger:
                        logger("GEMINI", f"Model {model_name} ({'429 Quota' if is_rate_limit else '503 Busy'}). Cooling down {wait_time}s...", "warning")
                    time.sleep(wait_time)
                else:
                    if logger:
                        logger("GEMINI", f"Model {model_name} error: {err_msg[:80]}... Mencoba model lain", "warning")
                    break
    raise RuntimeError(f"Semua model Gemini gagal: {last_err}")

def seed_existing_batch1(logger=None):
    """Reuse existing winning Model 1 solution for Geografi P2 Batch 1 if available."""
    src = r"D:\Documents\jawaban-dari-gmflsh38.json"
    out_dir = os.path.join(BASE_DIR, "claude_output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "GEOGRAFI_PAKET_2_PROMPT_BATCH_1.json")
    
    if os.path.exists(src) and not os.path.exists(dst):
        try:
            with open(src, "r", encoding="utf-8") as f:
                d = json.load(f)
            with open(dst, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            if logger:
                logger("GEMINI", "Batch 1 Geografi P2 (Soal 1-5) di-load dari cache pemenang!", "info")
        except Exception as e:
            pass

def run_all_batches(swarm_manager=None):
    """Run all remaining micro-batches in claude_input/ using Gemini Flash."""
    def log(tag, msg, level="info"):
        if swarm_manager:
            swarm_manager.log(tag, msg, level)
        else:
            try:
                print(f"[{tag}] {msg}")
            except Exception:
                safe_msg = msg.encode("ascii", errors="replace").decode("ascii")
                print(f"[{tag}] {safe_msg}")

    client = get_gemini_client()
    seed_existing_batch1(log)

    input_dir = os.path.join(BASE_DIR, "claude_input")
    output_dir = os.path.join(BASE_DIR, "claude_output")
    os.makedirs(output_dir, exist_ok=True)

    prompt_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".md") and "_PROMPT_BATCH_" in f])
    log("GEMINI", f"Ditemukan {len(prompt_files)} micro-batch prompt. Memulai eksekusi...", "info")

    completed = 0
    total = len(prompt_files)

    for idx, p_file in enumerate(prompt_files, start=1):
        stem = p_file[:-3]  # strip .md
        out_file = os.path.join(output_dir, f"{stem}.json")

        if os.path.exists(out_file):
            log("GEMINI", f"[{idx}/{total}] {stem} sudah selesai (Cache Hit) -> Skip", "info")
            completed += 1
            if swarm_manager:
                with swarm_manager.lock:
                    swarm_manager.divisions["divisi_4"]["progress"] = int((completed / total) * 100)
            continue

        log("GEMINI", f"[{idx}/{total}] Memproses {stem}...", "info")
        prompt_path = os.path.join(input_dir, p_file)
        with open(prompt_path, "r", encoding="utf-8") as f:
            p_text = f.read()

        # Add explicit instruction for strict Model 1 JSON output
        augmented_prompt = (
            p_text + "\n\n"
            "PENTING SEKALI: Keluarkan HANYA JSON murni berstandar Model 1:\n"
            "{\n"
            '  "package": 2,\n'
            '  "subject": "Geografi",\n'
            '  "solutions": [\n'
            '    {\n'
            '      "question_id": "...",\n'
            '      "question_number": 1,\n'
            '      "official_answer": null,\n'
            '      "needs_manual_review": false,\n'
            '      "concept_kunci": ["..."],\n'
            '      "glossary": [{"term": "...", "meaning": "..."}],\n'
            '      "reasoning": "...",\n'
            '      "steps": [{"step": 1, "title": "...", "explanation": "..."}],\n'
            '      "why_correct": "...",\n'
            '      "tips": ["..."],\n'
            '      "common_mistakes": ["..."],\n'
            '      "soal_serupa": {"pertanyaan": "...", "opsi": [{"key": "A", "text": "..."}], "kunci": "A", "pembahasan_singkat": "..."}\n'
            '    }\n'
            '  ]\n'
            "}\n"
            "Dilarang membungkus dengan teks pengantar atau penutup apapun selain kode JSON."
        )

        try:
            raw_output, used_model = call_gemini_with_failover(client, augmented_prompt, log)
            cleaned = clean_json_text(raw_output)
            parsed = json.loads(cleaned)

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)

            log("GEMINI", f"✅ {stem} selesai diproses oleh {used_model}! Tersimpan ke claude_output/", "info")
            completed += 1

            if swarm_manager:
                with swarm_manager.lock:
                    d4 = swarm_manager.divisions["divisi_4"]
                    d4["progress"] = int((completed / total) * 100)
                    d4["current_task"] = f"Gemini Flash memproses {stem}... ({completed}/{total})"

            # Polite pause to respect rate limits
            time.sleep(2)
        except Exception as e:
            log("GEMINI", f"❌ Gagal memproses {stem}: {str(e)[:120]}", "warning")
            time.sleep(2)

    log("GEMINI", f"🎉 Seluruh batch selesai diproses ({completed}/{total})!", "info")
    
    # Trigger Divisi 5 Compilation & Merge
    compile_and_ingest_solutions(log)
    return completed

def compile_and_ingest_solutions(logger=None):
    """Divisi 5: Merge micro-batches into master solution sources and compile learning JSON."""
    def log(tag, msg, level="info"):
        if logger:
            logger(tag, msg, level)
        else:
            print(f"[{tag}] {msg}")

    log("AUDITOR", "Memulai audit dan penggabungan solusi dari claude_output/...", "info")
    output_dir = os.path.join(BASE_DIR, "claude_output")
    solutions_dir = os.path.join(BASE_DIR, "data", "solution_sources")
    os.makedirs(solutions_dir, exist_ok=True)

    mappings = [
        ("GEOGRAFI_PAKET_2", "GEO_PAKET_2_SOLUTIONS.json", 2, "Geografi"),
        ("FISIKA_PAKET_1", "FISIKA_PAKET_1_SOLUTIONS.json", 1, "Fisika"),
        ("FISIKA_PAKET_2", "FISIKA_PAKET_2_SOLUTIONS.json", 2, "Fisika"),
    ]

    for prefix, master_filename, pkg_num, subj_name in mappings:
        batch_files = sorted([f for f in os.listdir(output_dir) if f.startswith(prefix) and f.endswith(".json")])
        if not batch_files:
            continue

        merged_solutions = []
        for bf in batch_files:
            try:
                with open(os.path.join(output_dir, bf), "r", encoding="utf-8") as f:
                    data = json.load(f)
                sols = data.get("solutions", [])
                merged_solutions.extend(sols)
            except Exception as e:
                log("AUDITOR", f"Gagal membaca {bf}: {e}", "warning")

        if merged_solutions:
            # Sort by question_number if available
            merged_solutions.sort(key=lambda x: x.get("question_number", 0))
            master_doc = {
                "package": pkg_num,
                "subject": subj_name,
                "total_solutions": len(merged_solutions),
                "solutions": merged_solutions
            }
            master_path = os.path.join(solutions_dir, master_filename)
            with open(master_path, "w", encoding="utf-8") as f:
                json.dump(master_doc, f, indent=2, ensure_ascii=False)
            log("AUDITOR", f"✅ {master_filename} berhasil dikompilasi ({len(merged_solutions)} butir solusi Layer 3)!", "info")

    # Run CBT Integrator (Phase 5)
    try:
        from pipeline.cbt_integrator import run_cbt_integration
        run_cbt_integration()
        log("AUDITOR", "🚀 Database pembelajaran CBT *_learning.json berhasil di-enrich dan hot-reloaded!", "success")
    except Exception as e:
        log("AUDITOR", f"Peringatan integrasi CBT: {e}", "warning")

