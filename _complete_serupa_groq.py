# -*- coding: utf-8 -*-
"""_complete_serupa_groq.py — Lengkapi soal_serupa MTL P1 via Qwen/Groq.

Gemini kena rate limit di semua kunci; soal serupa bersifat teks-murni
(tanpa vision) sehingga provider openai_compatible (Qwen 2.5 27B Groq)
cukup. Prompt & parsing memakai komponen fase 4 swarm apa adanya.
"""
import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import tutor_llm
import text_quality
from pipeline.swarm_manager import swarm_engine

SLUG = "matematika_lanjut_paket_1"
LRN_PATH = os.path.join(BASE_DIR, "data", f"{SLUG}_learning.json")

with open(LRN_PATH, encoding="utf-8") as f:
    lrn_data = json.load(f)

questions = lrn_data["soal"]
missing = [q for q in questions
           if not q.get("soal_serupa") or not q.get("soal_serupa", {}).get("pertanyaan")]
print(f"Soal serupa kurang: {len(missing)}/{len(questions)}", flush=True)
if not missing:
    print("Sudah lengkap — selesai.")
    sys.exit(0)

subject_name = "Matematika Tingkat Lanjut (Paket 1)"
merged = 0
BATCH = 5

for start in range(0, len(missing), BATCH):
    batch = missing[start:start + BATCH]
    prompt = swarm_engine._build_soal_serupa_prompt(subject_name, batch)
    ok = False
    for attempt in range(3):
        try:
            reply, meta = tutor_llm.generate(
                messages=[{"role": "user", "content": prompt}],
                model="qwen-groq", temperature=0.3, max_tokens=8192,
                timeout=180, return_meta=True)
            parsed = swarm_engine._safe_parse_json(reply)
            if not isinstance(parsed, list) or not parsed:
                raise ValueError("Respons bukan JSON list")
            s_map = {}
            for item in parsed:
                no = item.get("nomor_soal")
                sim = item.get("soal_serupa")
                if no and sim and sim.get("pertanyaan"):
                    s_map[int(no)] = sim
            for q in batch:
                if q["nomor"] in s_map:
                    sim = s_map[q["nomor"]]
                    # Normalkan teks agar bebas artefak (idempoten)
                    for fld in ("pertanyaan", "pembahasan_singkat"):
                        if sim.get(fld):
                            sim[fld] = text_quality.repair_math_text(sim[fld])
                    for opt in sim.get("pilihan", []) or []:
                        if opt.get("text"):
                            opt["text"] = text_quality.repair_math_text(opt["text"])
                    q["soal_serupa"] = sim
                    merged += 1
            print(f"Batch Q{batch[0]['nomor']}-Q{batch[-1]['nomor']}: "
                  f"{len(s_map)} soal serupa didapat ({meta['model']})", flush=True)
            ok = True
            break
        except Exception as e:
            print(f"  attempt {attempt + 1} gagal: {str(e)[:120]}", flush=True)
            time.sleep(10)
    if not ok:
        print(f"Batch Q{batch[0]['nomor']}-Q{batch[-1]['nomor']} GAGAL total", flush=True)
    time.sleep(5)

# Simpan checkpoint
with open(LRN_PATH, "w", encoding="utf-8") as f:
    json.dump(lrn_data, f, ensure_ascii=False, indent=2)

done = sum(1 for q in questions
           if (q.get("soal_serupa") or {}).get("pertanyaan"))
print(f"SELESAI: soal_serupa {done}/{len(questions)} (baru ditambah {merged})", flush=True)
