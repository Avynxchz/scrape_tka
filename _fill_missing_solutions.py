# -*- coding: utf-8 -*-
"""_fill_missing_solutions.py — Isi solusi 5 Pilar yang kurang via AI Studio.

Dipakai bila audit menemukan "Solusi hanya mencakup X/Y soal" setelah
regenerasi (continuation lama gagal karena ekstraksi berbasis indeks turn).
Script ini mengirim prompt continuation HANYA untuk nomor yang belum ada,
dengan ekstraksi last-JSON-turn yang tahan virtualisasi DOM.
"""
import sys
import os
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import text_quality
from playwright.sync_api import sync_playwright
from pipeline.playwright_aistudio_bridge import (
    connect_to_aistudio, _resolve_standard_page, start_fresh_chat,
    _wait_attachments_ready, _submit_prompt, _wait_for_response,
    safe_parse_json, PROMPT_DIR, log,
)
from pipeline.swarm_manager import swarm_engine
from pipeline.subject_catalog import MASTER_CATALOG


def standardize(sol, no, prefix, paket, name, kunci_map):
    sol["question_id"] = f"{prefix}_p{paket}_q{no:02d}"
    sol["concept_kunci"] = sol.get("concept_kunci") or sol.get("concept_tags") or [name]
    raw_k = kunci_map.get(str(no), "-")
    if isinstance(raw_k, list):
        sol["official_answer"] = {"format": "per_statement_benar_salah", "correct": [str(x) for x in raw_k]}
    else:
        sol["official_answer"] = {"format": "single_choice", "correct": str(raw_k)}
    for fld in ("why_correct", "reasoning", "diketahui", "ditanyakan", "question_title"):
        if sol.get(fld):
            sol[fld] = text_quality.repair_math_text(
                sol[fld].replace("transkripsi", "kutipan").replace("transkrip", "kutipan"))
    for st in sol.get("steps", []):
        for fld in ("explanation", "title"):
            if st.get(fld):
                st[fld] = text_quality.repair_math_text(
                    st[fld].replace("transkripsi", "kutipan").replace("transkrip", "kutipan"))
    return sol


def fill(slug, page, passes=3):
    item = MASTER_CATALOG[slug]
    name, paket, prefix = item["name"], item["paket"], item.get("prefix", "soal")
    lrn = json.load(open(os.path.join("data", f"{slug}_learning.json"), encoding="utf-8"))
    kunci = json.load(open(os.path.join("data", "kunci", f"{slug}_kunci.json"), encoding="utf-8"))
    kunci_map = {}
    for k, v in kunci.get("kunci_pg", {}).items():
        kunci_map[str(k)] = v
    for k, v in kunci.get("kunci_bs", {}).items():
        kunci_map[str(k)] = [f"{k_}:{v_}" for k_, v_ in sorted(v.items())]

    sol_path = os.path.join("data", "solution_sources", f"{slug.upper()}_SOLUTIONS.json")
    doc = json.load(open(sol_path, encoding="utf-8"))
    sols_map = {s["question_number"]: s for s in doc.get("solutions", [])}
    questions = lrn["soal"]
    total_q = len(questions)

    for p in range(1, passes + 1):
        missing = [q for q in questions if q["nomor"] not in sols_map]
        if not missing:
            break
        log(f"[{slug}] Pass {p}: {len(missing)} solusi kurang: {[q['nomor'] for q in missing]}", "WARNING")
        prompt = swarm_engine._build_5pillar_prompt(name, missing, kunci_map, slug=slug)
        prompt_file = os.path.join(PROMPT_DIR, f"{slug}_fill_p{p}.txt")
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        try:
            raw = None
            for attempt in range(2):
                dismiss_ok = True
                try:
                    from pipeline.playwright_aistudio_bridge import dismiss_any_overlay
                    dismiss_any_overlay(page)
                except Exception:
                    pass
                fin = page.locator("input[type='file']")
                if fin.count() == 0:
                    raise RuntimeError("Input file tidak ditemukan")
                fin.first.set_input_files(prompt_file)
                _wait_attachments_ready(page, [prompt_file], 40)
                time.sleep(1.0)
                box = page.locator("ms-autosize-textarea textarea, textarea").first
                box.click(force=True)
                instruction = (f"Lengkapi PEMBAHASAN 5 PILAR untuk nomor yang belum ada: "
                               f"{[q['nomor'] for q in missing]}. Format JSON array persis sama, "
                               f"tanpa nomor lain.")
                box.evaluate("(el, t) => { el.value = t; el.dispatchEvent(new Event('input', {bubbles:true})); }", instruction)
                time.sleep(1.0)
                if not _submit_prompt(page):
                    log(f"[{slug}] submit attempt {attempt+1} gagal — retry", "WARNING")
                    continue
                raw = _wait_for_response(page, 0, timeout_seconds=420)
                break
            if not raw:
                log(f"[{slug}] Pass {p} gagal total (submit).", "ERROR")
                continue

            parsed = safe_parse_json(raw)
            if not isinstance(parsed, list):
                parsed = []
            n_new = 0
            for it in parsed:
                no = it.get("question_number")
                if no and no in [q["nomor"] for q in missing] and no not in sols_map:
                    sols_map[no] = standardize(it, no, prefix, paket, name, kunci_map)
                    n_new += 1
            doc["solutions"] = [sols_map[k] for k in sorted(sols_map.keys())]
            with open(sol_path, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
            log(f"[{slug}] Pass {p}: +{n_new} solusi (total {len(sols_map)}/{total_q})",
                "SUCCESS" if n_new else "WARNING")
        except Exception as e:
            log(f"[{slug}] Pass {p} error: {str(e)[:100]}", "ERROR")

    return len(sols_map), total_q


if __name__ == "__main__":
    targets = sys.argv[1:] or ["matematika_lanjut_paket_2", "sejarah_paket_2"]
    with sync_playwright() as p:
        browser, page = connect_to_aistudio(p, port=9222)
        page = _resolve_standard_page(browser, page)
        if page is None:
            print("Playground standar tidak ditemukan — jalankan Chrome AI Studio dulu.")
            sys.exit(1)
        for slug in targets:
            # Chat baru per target: konten turn lama dibuang AI Studio bila
            # percakapan terlalu panjang, jadi tiap target mulai dari kosong.
            if not start_fresh_chat(page):
                log("Gagal membuka chat baru — memakai percakapan yang ada.", "WARNING")
            have, total = fill(slug, page)
            print(f"HASIL {slug}: {have}/{total}")
