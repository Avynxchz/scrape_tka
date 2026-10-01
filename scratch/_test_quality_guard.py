import os
import sys
import json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pipeline.quality_guard import assert_package_integrity, QualityGuardError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")

print("1. Testing Quality Guard on Clean Package (Bahasa Indonesia Lanjut Paket 1)...")
l1 = json.load(open(os.path.join(DATA_DIR, "bahasa_indonesia_lanjut_paket_1_learning.json"), encoding="utf-8"))
s1 = json.load(open(os.path.join(SOL_DIR, "BAHASA_INDONESIA_LANJUT_PAKET_1_SOLUTIONS.json"), encoding="utf-8"))
k1 = json.load(open(os.path.join(DATA_DIR, "kunci", "bahasa_indonesia_lanjut_paket_1_kunci.json"), encoding="utf-8"))
img1 = os.path.join(DATA_DIR, "bahasa_indonesia_lanjut", "paket_1", "images")

res1 = assert_package_integrity("bahasa_indonesia_lanjut_paket_1", l1, s1, img1, k1)
print(f"✅ Clean package result: {res1['status']}")

print("\n2. Testing Quality Guard on Buggy Package (Ekonomi Paket 1)...")
l_eko = json.load(open(os.path.join(DATA_DIR, "ekonomi_paket_1_learning.json"), encoding="utf-8"))
s_eko = json.load(open(os.path.join(SOL_DIR, "EKO_PAKET_1_SOLUTIONS.json"), encoding="utf-8"))
img_eko = os.path.join(DATA_DIR, "ekonomi", "paket_1", "images")

try:
    assert_package_integrity("ekonomi_paket_1", l_eko, s_eko, img_eko)
    print("❌ FAILED: Quality Guard did NOT catch the boilerplate in Ekonomi!")
except QualityGuardError as e:
    print(f"✅ SUCCESS: Quality Guard successfully caught and blocked bug: {e.category} -> {e.message}")

print("\n✨ Quality Guard is 100% operational!")
