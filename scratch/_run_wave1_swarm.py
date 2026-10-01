# -*- coding: utf-8 -*-
"""scratch/_run_wave1_swarm.py
Wave 1 Runner:
Executes the full automated pipeline (Fase 1-5) for the 4 target packages:
1. bahasa_indonesia_lanjut_paket_1 (10 questions)
2. bahasa_indonesia_lanjut_paket_2 (29 questions)
3. bahasa_inggris_lanjut_paket_1 (10 questions)
4. bahasa_inggris_lanjut_paket_2 (29 questions)

Followed by an exhaustive Zero-Trust Audit & UI E2E verification.
"""
import sys
import time
import json
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, ".")
from pipeline.subject_catalog import MASTER_CATALOG
from pipeline.swarm_manager import swarm_engine
from pipeline.playwright_aistudio_bridge import check_port_open, ensure_chrome_debug_open
import importlib
auditor_mod = importlib.import_module("pipeline.05_automated_auditor")
audit_subject_package = auditor_mod.audit_subject_package

WAVE_1_SLUGS = [
    "bahasa_indonesia_lanjut_paket_1",
    "bahasa_indonesia_lanjut_paket_2",
    "bahasa_inggris_lanjut_paket_1",
    "bahasa_inggris_lanjut_paket_2"
]

def main():
    print("=" * 80)
    print("🚀 MEMULAI EKSEKUSI WAVE 1 MULTI-AGENT SWARM")
    print(f"Target ({len(WAVE_1_SLUGS)} Paket):")
    for s in WAVE_1_SLUGS:
        item = MASTER_CATALOG[s]
        print(f"  • {item['name']} (Slug: {s})")
    print("=" * 80)

    # 1. Pastikan Chrome remote debugging standby
    print("\n[PRE-FLIGHT] Memeriksa kesiapan Chrome port 9222...")
    if not check_port_open(9222):
        print("Membuka Chrome port 9222...")
        ensure_chrome_debug_open(9222)
        time.sleep(2)
    if check_port_open(9222):
        print("✅ Chrome port 9222 AKTIF & SIAP.")
    else:
        print("⚠️ Chrome port 9222 belum aktif, pipeline akan fallback otomatis bila diperlukan.")

    # 2. Persiapkan objek target
    target_objs = [dict(MASTER_CATALOG[s]) for s in WAVE_1_SLUGS]

    # 3. Jalankan pipeline Swarm thread secara sekuensial & terkontrol
    print("\n[ORCHESTRATOR] Meluncurkan Swarm Pipeline (Fase 1 - 5)...")
    t_start = time.time()
    
    try:
        swarm_engine._run_swarm_thread(target_objs)
    except Exception as e:
        print(f"❌ Terjadi exception saat eksekusi swarm: {e}")

    elapsed = time.time() - t_start
    print("\n" + "=" * 80)
    print(f"🏁 SIKLUS SWARM WAVE 1 SELESAI DALAM {elapsed:.1f} DETIK")
    print("=" * 80)

    # 4. Audit Besar-Besaran Zero-Trust (9 Checklist Deterministik)
    print("\n" + "=" * 80)
    print("🔍 MEMULAI AUDIT BESAR-BESARAN ZERO-TRUST PADA KE-4 MAPEL")
    print("=" * 80)
    
    audit_results = {}
    total_issues = 0
    total_warnings = 0

    for s in WAVE_1_SLUGS:
        item = MASTER_CATALOG[s]
        issues, warnings = audit_subject_package(
            slug=s,
            mapel=item["mapel_key"],
            paket=item["paket"],
            prefix=item.get("prefix", "soal")
        )
        audit_results[s] = {"issues": issues, "warnings": warnings}
        total_issues += len(issues)
        total_warnings += len(warnings)

    print("\n" + "=" * 80)
    print("📊 REKAPITULASI AUDIT DETERMINISTIK WAVE 1")
    print("=" * 80)
    for s, res in audit_results.items():
        status_icon = "✅ PASS" if not res["issues"] else f"❌ FAIL ({len(res['issues'])} issues)"
        print(f"• {s:<35} : {status_icon} | {len(res['warnings'])} warnings")

    if total_issues == 0:
        print(f"\n🎉 HASIL AKHIR: 100% LOLOS AUDIT ZERO-TRUST! (0 BUGS / 0 ISSUES)")
    else:
        print(f"\n⚠️ DITEMUKAN {total_issues} ISU! HARAP DIPERIKSA.")

    return total_issues == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
