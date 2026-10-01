import os, json, glob

wave1_slugs = [
    'bahasa_indonesia_lanjut_paket_1',
    'bahasa_indonesia_lanjut_paket_2',
    'bahasa_inggris_lanjut_paket_1',
    'bahasa_inggris_lanjut_paket_2'
]

print("=== 1. REMOVING SOLUTION SOURCE FILES ===")
for s in wave1_slugs:
    sol_file = f"data/solution_sources/{s.upper()}_SOLUTIONS.json"
    if os.path.exists(sol_file):
        os.remove(sol_file)
        print(f"Removed: {sol_file}")

print("\n=== 2. RESETTING REGISTRY.JSON ===")
reg_file = "data/solution_sources/registry.json"
if os.path.exists(reg_file):
    with open(reg_file, "r", encoding="utf-8") as f:
        reg = json.load(f)
    for s in wave1_slugs:
        if s in reg:
            del reg[s]
            print(f"Removed from registry: {s}")
    with open(reg_file, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)

print("\n=== 3. RESETTING SOAL_SERUPA IN LEARNING FILES ===")
for s in wave1_slugs:
    lrn_file = f"data/{s}_learning.json"
    if os.path.exists(lrn_file):
        with open(lrn_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        reset_count = 0
        for q in data.get("soal", []):
            if "soal_serupa" in q and q["soal_serupa"] is not None:
                q["soal_serupa"] = None
                reset_count += 1
        with open(lrn_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Reset {reset_count} soal_serupa in {lrn_file}")

print("\n=== 4. REMOVING PROMPTS & RAW LLM OUTPUTS FOR WAVE 1 ===")
for s in wave1_slugs:
    for p in glob.glob(f"data/prompts/{s}*.*") + glob.glob(f"data/raw_llm_outputs/{s}*.*"):
        os.remove(p)
        print(f"Removed: {p}")

print("\n=== CLEANUP FINISHED! PHASE 4 WAVE 1 IS COMPLETELY FRESH! ===")
