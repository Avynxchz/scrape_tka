import sys
import os
import json
import importlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, ".")
auditor_mod = importlib.import_module("pipeline.05_automated_auditor")
audit_subject_package = auditor_mod.audit_subject_package

TARGETS = [
    ("teknik_mesin_paket_1", "teknik_mesin", 1, "tms"),
    ("teknik_otomotif_paket_1", "teknik_otomotif", 1, "tot"),
    ("teknik_jaringan_paket_1", "teknik_jaringan", 1, "tkj"),
    ("akuntansi_paket_1", "akuntansi", 1, "akl"),
    ("manajemen_perkantoran_paket_1", "manajemen_perkantoran", 1, "mplb"),
]

for slug, mapel, paket, prefix in TARGETS:
    issues, warnings = audit_subject_package(slug, mapel, paket, prefix)
    print(f"\n[HASIL AUDIT {slug}]:")
    print(f"  Critical Issues ({len(issues)}):")
    for iss in issues:
        print(f"    - {iss}")
    print(f"  Warnings ({len(warnings)}):")
    for w in warnings:
        print(f"    - {w}")
