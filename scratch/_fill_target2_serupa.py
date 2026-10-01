import sys, os, time, json
sys.path.insert(0, '.')

from pipeline.playwright_aistudio_bridge import (
    connect_to_aistudio, start_fresh_chat, inject_and_run, safe_parse_json, log
)
from pipeline.swarm_manager import swarm_engine
from playwright.sync_api import sync_playwright

slug = "bahasa_indonesia_lanjut_paket_2"
name = "Bahasa Indonesia Tingkat Lanjut (Paket 2)"
lrn_path = f"data/{slug}_learning.json"

with open(lrn_path, "r", encoding="utf-8") as f:
    lrn_data = json.load(f)

questions = lrn_data.get("soal", [])
missing = [q for q in questions if not q.get("soal_serupa")]
print(f"Missing soal_serupa for {len(missing)} questions: {[q['nomor'] for q in missing]}")

if not missing:
    print("All soal_serupa are already present!")
    sys.exit(0)

prompt = swarm_engine._build_soal_serupa_prompt(name, missing, slug=slug)
prompt_file = f"data/prompts/{slug}_fill_missing_serupa.txt"
with open(prompt_file, "w", encoding="utf-8") as f:
    f.write(prompt)

with sync_playwright() as p:
    browser, page = connect_to_aistudio(p, port=9222)
    start_fresh_chat(page)

    raw = inject_and_run(
        page,
        prompt_text=prompt,
        prompt_file_path=prompt_file,
        instruction=f"Hasilkan Soal Serupa untuk {len(missing)} butir soal di file terlampir dalam format JSON array murni.",
        timeout_seconds=300
    )

    parsed = safe_parse_json(raw) or []
    print(f"Received {len(parsed)} soal serupa from AI Studio!")

    filled = 0
    serupa_map = {item.get("nomor_soal"): item.get("soal_serupa") for item in parsed if item.get("nomor_soal") and item.get("soal_serupa")}
    for q in questions:
        if q["nomor"] in serupa_map:
            q["soal_serupa"] = serupa_map[q["nomor"]]
            filled += 1

    with open(lrn_path, "w", encoding="utf-8") as f:
        json.dump(lrn_data, f, indent=2, ensure_ascii=False)

    total_with_serupa = sum(1 for q in questions if q.get("soal_serupa"))
    print(f"Updated {filled} questions. Total with soal_serupa now: {total_with_serupa}/{len(questions)}")
