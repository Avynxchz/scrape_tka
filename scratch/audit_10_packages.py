# -*- coding: utf-8 -*-
import os, sys, json, re
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.quality_guard import assert_package_integrity, QualityGuardError

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci_jawaban")
if not os.path.isdir(KUNCI_DIR):
    KUNCI_DIR = os.path.join(DATA_DIR, "kunci")

pkgs = [
    "ekonomi_paket_1",
    "ekonomi_paket_2",
    "kewirausahaan_paket_1",
    "kewirausahaan_paket_2",
    "bahasa_inggris_paket_1",
    "bahasa_inggris_paket_2",
    "matematika_paket_1",
    "matematika_paket_2",
    "bahasa_indonesia_paket_1",
    "sejarah_paket_1"
]

print("=" * 80)
print("AUDIT BESAR-BESARAN 10 MAPEL (ZERO-TRUST QUALITY AUDIT)")
print("=" * 80)

results = {}

for slug in pkgs:
    parts = slug.rsplit("_paket_", 1)
    mapel = parts[0]
    paket = parts[1]
    
    lrn_p = os.path.join(DATA_DIR, f"{slug}_learning.json")
    sol_p = os.path.join(SOL_DIR, f"{slug.upper()}_SOLUTIONS.json")
    kunci_p = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
    img_dir = os.path.join(DATA_DIR, mapel, f"paket_{paket}", "images")
    
    print(f"\n[{slug.upper()}]")
    if not os.path.isfile(lrn_p):
        print("  ❌ Learning file missing:", lrn_p)
        results[slug] = {"status": "MISSING_LEARNING"}
        continue

    with open(lrn_p, "r", encoding="utf-8") as f:
        ldoc = json.load(f)

    sdoc = None
    if os.path.isfile(sol_p):
        with open(sol_p, "r", encoding="utf-8") as f:
            sdoc = json.load(f)
    else:
        print("  ⚠️ Solution file not found in upper case, searching...")
        # check registry
        reg_p = os.path.join(SOL_DIR, "registry.json")
        if os.path.isfile(reg_p):
            with open(reg_p, "r", encoding="utf-8") as rf:
                reg = json.load(rf)
            active = reg.get(slug, {}).get("active_source")
            if active and os.path.isfile(os.path.join(SOL_DIR, active)):
                sol_p = os.path.join(SOL_DIR, active)
                with open(sol_p, "r", encoding="utf-8") as sf:
                    sdoc = json.load(sf)

    kdoc = None
    if os.path.isfile(kunci_p):
        with open(kunci_p, "r", encoding="utf-8") as f:
            kdoc = json.load(f)

    print(f"  • Learning file: {os.path.basename(lrn_p)} ({len(ldoc.get('soal', []))} questions)")
    print(f"  • Solution file: {os.path.basename(sol_p) if sdoc else 'NONE'} ({len(sdoc.get('solutions', [])) if sdoc else 0} solutions)")
    print(f"  • Kunci file: {os.path.basename(kunci_p) if kdoc else 'NONE'}")
    print(f"  • Image dir: {img_dir} (exists: {os.path.isdir(img_dir)}, files: {len(os.listdir(img_dir)) if os.path.isdir(img_dir) else 0})")

    try:
        assert_package_integrity(slug, ldoc, sdoc, img_dir, kdoc)
        print("  ✅ 100% PASSED ZERO-TRUST QUALITY GUARD!")
        results[slug] = {"status": "PASS", "issues": []}
    except QualityGuardError as e:
        print(f"  ❌ FAILED [{e.category}]: {e.message}")
        if e.violations:
            for v in e.violations[:5]:
                print(f"     -> {v}")
        results[slug] = {"status": "FAIL", "category": e.category, "message": e.message, "violations": e.violations}

print("\n" + "=" * 80)
print("REKAPITULASI STATUS 10 MAPEL")
print("=" * 80)
for slug, res in results.items():
    st = "✅ PASS" if res["status"] == "PASS" else f"❌ FAIL [{res.get('category')}]: {res.get('message')}"
    print(f"• {slug:30}: {st}")
