# -*- coding: utf-8 -*-
"""scratch/_run_remaining_3.py — Runner untuk menyelesaikan 3 paket terakhir:
1. bahasa_mandarin_paket_2 (soal serupa)
2. bahasa_korea_paket_1 (solusi 5 pilar + soal serupa)
3. bahasa_korea_paket_2 (solusi 5 pilar + soal serupa)

Setelah Fase 4 & 5 tuntas:
- Sinkronisasi ke exports/
- Audit Mutlak Semesta (44/44 Paket)
- Raw Fidelity Audit (40/40 Paket)
"""
import sys
import os
import time
import json
import shutil
import importlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.subject_catalog import MASTER_CATALOG
from pipeline.swarm_manager import swarm_engine

REMAINING_SLUGS = [
    "bahasa_mandarin_paket_2",
    "bahasa_korea_paket_1",
    "bahasa_korea_paket_2",
]

ALL_FINAL_WAVE = [
    "bahasa_arab_paket_1",
    "bahasa_arab_paket_2",
    "bahasa_jepang_paket_1",
    "bahasa_jepang_paket_2",
    "bahasa_jerman_paket_1",
    "bahasa_jerman_paket_2",
    "bahasa_prancis_paket_1",
    "bahasa_prancis_paket_2",
    "bahasa_mandarin_paket_1",
    "bahasa_mandarin_paket_2",
    "bahasa_korea_paket_1",
    "bahasa_korea_paket_2",
]

def main():
    print("=" * 85)
    print("🚀 MENYELESAIKAN 3 PAKET TERAKHIR PUSMENDIK")
    print("=" * 85)
    for s in REMAINING_SLUGS:
        item = MASTER_CATALOG[s]
        print(f"  • {item['name']:35s} (Slug: {s})")
    print("=" * 85)

    targets = [dict(MASTER_CATALOG[s]) for s in REMAINING_SLUGS]

    t0 = time.time()

    # 1. Jalankan Divisi 4 Reasoning API
    print("\n[FASE 4] Menjalankan Reasoning Engine (5 Pilar & Soal Serupa)...")
    swarm_engine._execute_divisi_4_reasoning_api(targets)

    # 2. Jalankan Divisi 5 Auditor
    print("\n[FASE 5] Menjalankan Zero-Trust Quality Guard Auditor...")
    swarm_engine._execute_divisi_5_auditor(targets)

    # 3. Sinkronisasi seluruh 12 Paket Bahasa Asing ke exports/
    print("\n[EXPORTER] Menyinkronkan seluruh output ke exports/...")
    os.makedirs(os.path.join(BASE_DIR, "exports"), exist_ok=True)
    for s in ALL_FINAL_WAVE:
        lrn_src = os.path.join(BASE_DIR, "data", f"{s}_learning.json")
        lrn_dst = os.path.join(BASE_DIR, "exports", f"{s}_learning.json")
        if os.path.exists(lrn_src):
            shutil.copyfile(lrn_src, lrn_dst)
            print(f"  ✓ Exported learning: {s}")

        sol_src = os.path.join(BASE_DIR, "data", "solution_sources", f"{s.upper()}_SOLUTIONS.json")
        sol_dst = os.path.join(BASE_DIR, "exports", f"{s}_solutions.json")
        if os.path.exists(sol_src):
            shutil.copyfile(sol_src, sol_dst)
            print(f"  ✓ Exported solutions: {s}")

    dur = time.time() - t0
    print(f"\n✅ Selesai dalam {dur:.1f} detik (~{dur/60:.1f} menit).")

    # 4. Master Omni Audit
    print("\n" + "=" * 85)
    print("🔍 MENJALANKAN MASTER OMNI AUDIT (44 PAKET)")
    print("=" * 85)
    try:
        import pipeline.master_omni_auditor as moa
        importlib.reload(moa)
        moa.audit_all()
    except Exception as ex:
        print(f"Omni auditor error: {ex}")

    # 5. Raw Fidelity Audit
    print("\n" + "=" * 85)
    print("🔍 MENJALANKAN RAW FIDELITY AUDIT")
    print("=" * 85)
    try:
        import pipeline.raw_fidelity_auditor as rfa
        importlib.reload(rfa)
        rfa.audit_raw_fidelity()
    except Exception as ex:
        print(f"Raw fidelity auditor error: {ex}")

if __name__ == "__main__":
    main()
