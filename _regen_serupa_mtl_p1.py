# -*- coding: utf-8 -*-
"""_regen_serupa_mtl_p1.py — Regenerasi soal_serupa MTL P1 yang off-concept.

10 soal yang isinya murni gambar (teks kosong) menghasilkan soal serupa
generik karena prompt lama tidak menyertakan transkripsi sidecar. Script ini
menghapus soal_serupa nomor tersebut lalu meregenerasinya via Qwen/Groq
dengan prompt sidecar-aware (swarm_engine._build_soal_serupa_prompt slug=...).
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
REGEN_NOS = {1, 2, 3, 9, 10, 16, 17, 18, 19, 20}

with open(LRN_PATH, encoding="utf-8") as f:
    lrn_data = json.load(f)

targets = [q for q in lrn_data["soal"] if q["nomor"] in REGEN_NOS]
for q in targets:
    q["soal_serupa"] = None
with open(LRN_PATH, "w", encoding="utf-8") as f:
    json.dump(lrn_data, f, ensure_ascii=False, indent=2)
print(f"soal_serupa dihapus untuk {len(targets)} soal: {sorted(REGEN_NOS)}", flush=True)

subject_name = "Matematika Tingkat Lanjut (Paket 1)"
merged = 0
BATCH = 5

for start in range(0, len(targets), BATCH):
    batch = targets[start:start + BATCH]
    prompt = swarm_engine._build_soal_serupa_prompt(subject_name, batch, slug=SLUG)
    got = 0
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
                    for fld in ("pertanyaan", "pembahasan_singkat"):
                        if sim.get(fld):
                            sim[fld] = text_quality.repair_math_text(sim[fld])
                    for opt in sim.get("pilihan", []) or []:
                        if opt.get("text"):
                            opt["text"] = text_quality.repair_math_text(opt["text"])
                    q["soal_serupa"] = sim
                    merged += 1
                    got += 1
            print(f"Batch Q{batch[0]['nomor']}-Q{batch[-1]['nomor']}: {got} didapat", flush=True)
            break
        except Exception as e:
            print(f"  attempt {attempt + 1} gagal: {str(e)[:120]}", flush=True)
            time.sleep(10)
    time.sleep(5)

with open(LRN_PATH, "w", encoding="utf-8") as f:
    json.dump(lrn_data, f, ensure_ascii=False, indent=2)

done = sum(1 for q in lrn_data["soal"] if (q.get("soal_serupa") or {}).get("pertanyaan"))
print(f"SELESAI: soal_serupa {done}/{len(lrn_data['soal'])} (regenerasi {merged})", flush=True)

# Preview konsep hasil regenerasi
for q in sorted(targets, key=lambda x: x["nomor"]):
    serupa = (q.get("soal_serupa") or {}).get("pertanyaan", "")
    print(f"  Q{q['nomor']:02d}: {serupa[:90]}", flush=True)
