import os
import sys
import importlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

auditor = importlib.import_module("pipeline.05_automated_auditor")
targets = [
    ("bahasa_indonesia_lanjut_paket_1", "bahasa_indonesia_lanjut", 1, "ind"),
    ("bahasa_indonesia_lanjut_paket_2", "bahasa_indonesia_lanjut", 2, "ind"),
    ("bahasa_inggris_lanjut_paket_1", "bahasa_inggris_lanjut", 1, "ing"),
    ("bahasa_inggris_lanjut_paket_2", "bahasa_inggris_lanjut", 2, "ing"),
]

all_passed = True
results = {}

for slug, mapel, paket, prefix in targets:
    issues, warnings = auditor.audit_subject_package(slug, mapel, paket, prefix)
    passed = len(issues) == 0
    results[slug] = {"passed": passed, "issues": issues, "warnings": warnings}
    if not passed:
        all_passed = False

print("\n" + "="*80)
print("🏆 FINAL ZERO-TRUST AUDIT RECAP - WAVE 1 (4 PAKET - 78 SOAL)")
print("="*80)
for slug, res in results.items():
    status = "✅ 100% PASS (0 ISSUES)" if res["passed"] else f"❌ FAILED ({len(res['issues'])} issues)"
    print(f"  • {slug:<35}: {status}")

if all_passed:
    print("\n🎉 SELURUH PAKET WAVE 1 LOLOS AUDIT MUTU ZERO-TRUST SECARA SEMPURNA!")
    sys.exit(0)
else:
    print("\n❌ ADA ISU YANG BELUM TUNTAS!")
    sys.exit(1)
