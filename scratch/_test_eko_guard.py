import os
import sys
import json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pipeline.quality_guard import assert_package_integrity, QualityGuardError

packages = [
    "ekonomi_paket_1",
    "ekonomi_paket_2",
    "kewirausahaan_paket_1",
    "kewirausahaan_paket_2",
    "bahasa_inggris_paket_1",
    "bahasa_inggris_paket_2"
]

DATA_DIR = os.path.join(ROOT, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")

for slug in packages:
    parts = slug.rsplit("_paket_", 1)
    mapel = parts[0]
    paket = parts[1]
    
    lrn_p = os.path.join(DATA_DIR, f"{slug}_learning.json")
    sol_p = os.path.join(SOL_DIR, f"{slug.upper()}_SOLUTIONS.json")
    kunci_p = os.path.join(DATA_DIR, "kunci", f"{slug}_kunci.json")
    img_dir = os.path.join(DATA_DIR, mapel, f"paket_{paket}", "images")
    
    if not os.path.exists(lrn_p) or not os.path.exists(sol_p):
        print(f"❌ {slug}: File learning or solution missing!")
        continue
        
    lrn_doc = json.load(open(lrn_p, encoding="utf-8"))
    sol_doc = json.load(open(sol_p, encoding="utf-8"))
    kunci_doc = json.load(open(kunci_p, encoding="utf-8")) if os.path.exists(kunci_p) else None
    
    print(f"\n{'='*70}")
    print(f"Checking {slug}:")
    print(f"{'='*70}")
    try:
        res = assert_package_integrity(slug, lrn_doc, sol_doc, img_dir, kunci_doc)
        print(f"  ✅ Quality Guard PASS: {res['status']}")
    except QualityGuardError as e:
        print(f"  🚨 Quality Guard REJECT [{e.category}]: {e.message}")
        if e.violations:
            for v in e.violations[:3]:
                print(f"     -> {v}")
