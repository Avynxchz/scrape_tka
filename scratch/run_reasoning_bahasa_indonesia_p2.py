# -*- coding: utf-8 -*-
"""scratch/run_reasoning_bahasa_indonesia_p2.py — Autonomous Divisi 4 Runner for Bahasa Indonesia Paket 2.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from pipeline.swarm_manager import swarm_engine
from pipeline.subject_catalog import MASTER_CATALOG
import importlib
auditor = importlib.import_module("pipeline.05_automated_auditor")

print("=" * 70, flush=True)
print("🚀 LAUNCHING AUTONOMOUS DIVISI 4 REASONING ENGINE (MEGA-BATCH)", flush=True)
print("🎯 TARGET: Bahasa Indonesia Paket 2", flush=True)
print("=" * 70, flush=True)

target = MASTER_CATALOG["bahasa_indonesia_paket_2"]

start_time = time.time()
swarm_engine._execute_divisi_4_reasoning([target])
elapsed = time.time() - start_time
print(f"\n⏱️ Divisi 4 selesai dalam {elapsed:.1f} detik.", flush=True)

# Divisi 5 Audit
print("\n" + "=" * 70, flush=True)
print("🔍 EXECUTING DIVISI 5 ZERO-TRUST QUALITY AUDITOR", flush=True)
print("=" * 70, flush=True)
swarm_engine._execute_divisi_5_auditor([target])

# Run Auditor CLI verification
print("\n" + "=" * 70, flush=True)
print("📊 FINAL AUDITOR VERIFICATION RUN", flush=True)
print("=" * 70, flush=True)
success = auditor.run_full_audit("bahasa_indonesia_paket_2")
print(f"\nFinal Audit Success: {success}", flush=True)
sys.exit(0 if success else 1)
