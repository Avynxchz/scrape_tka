# -*- coding: utf-8 -*-
"""scratch/_run_wave2_swarm.py
Wave 2 Swarm Runner & Full End-to-End Auditor:
Target 5 Paket Rumpun Soshum & Lintas Minat:
1. sosiologi_paket_2
2. antropologi_paket_1
3. antropologi_paket_2
4. ppkn_paket_1
5. ppkn_paket_2

Eksekusi Fase 1 s/d 5:
- Fase 1: Ingress Pusmendik (Scraping Soal, Gambar, Kunci)
- Fase 2: Data Architect & Sanitizer (learning.json & kunci.json)
- Fase 3: Visionary OCR / Transcription (Transkripsi Gambar AI Studio)
- Fase 4: Reasoning Engine (Solusi 5 Pilar Otentik & Soal Serupa via Playwright AI Studio Bridge)
- Fase 5: Zero-Trust Quality Guard & Automated Auditor
"""
import sys
import time
import json
import os
import importlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.subject_catalog import MASTER_CATALOG
from pipeline.swarm_manager import swarm_engine
from pipeline.playwright_aistudio_bridge import check_port_open, ensure_chrome_debug_open
from pipeline.quality_guard import assert_package_integrity, QualityGuardError

auditor_mod = importlib.import_module("pipeline.05_automated_auditor")
audit_subject_package = auditor_mod.audit_subject_package

WAVE_2_SLUGS = [
    "sosiologi_paket_2",
    "antropologi_paket_1",
    "antropologi_paket_2",
    "ppkn_paket_1",
    "ppkn_paket_2",
]

def main():
    print("=" * 80)
    print("🚀 MEMULAI EKSEKUSI WAVE 2 MULTI-AGENT SWARM")
    print(f"Target ({len(WAVE_2_SLUGS)} Paket):")
    for s in WAVE_2_SLUGS:
        item = MASTER_CATALOG[s]
        print(f"  • {item['name']} [Jenis: {item['jenis']}, Val: {item['val']}] (Slug: {s})")
    print("=" * 80)

    # 1. Pre-flight: Pastikan Chrome remote debugging standby
    print("\n[PRE-FLIGHT] Memeriksa kesiapan Chrome port 9222...")
    if not check_port_open(9222):
        print("Membuka Chrome port 9222...")
        ensure_chrome_debug_open(9222)
        time.sleep(3)
    if check_port_open(9222):
        print("✅ Chrome port 9222 AKTIF & SIAP.")
    else:
        print("⚠️ Chrome port 9222 belum aktif, pipeline akan fallback otomatis bila diperlukan.")

    # 2. Persiapkan objek target
    target_objs = [dict(MASTER_CATALOG[s]) for s in WAVE_2_SLUGS]

    # 3. Jalankan pipeline Swarm thread secara sekuensial & terkontrol
    print("\n[ORCHESTRATOR] Meluncurkan Swarm Pipeline (Fase 1 - 5)...")
    t_start = time.time()

    try:
        swarm_engine._run_swarm_thread(target_objs)
    except Exception as e:
        print(f"❌ Terjadi exception saat eksekusi swarm: {e}")

    elapsed = time.time() - t_start
    print("\n" + "=" * 80)
    print(f"🏁 SIKLUS SWARM WAVE 2 SELESAI DALAM {elapsed:.1f} DETIK")
    print("=" * 80)

    # 4. Audit Besar-Besaran Zero-Trust (9 Checklist Deterministik + Quality Guard)
    print("\n" + "=" * 80)
    print("🔍 MEMULAI AUDIT BESAR-BESARAN ZERO-TRUST PADA KE-5 MAPEL WAVE 2")
    print("=" * 80)

    audit_results = {}
    discovered_bugs = []
    total_issues = 0
    total_warnings = 0

    for s in WAVE_2_SLUGS:
        item = MASTER_CATALOG[s]
        mapel = item["mapel_key"]
        paket = item["paket"]
        prefix = item.get("prefix", "soal")

        print(f"\n--- AUDIT: {s.upper()} ---")
        issues, warnings = audit_subject_package(
            slug=s,
            mapel=mapel,
            paket=paket,
            prefix=prefix
        )

        # Cek Quality Guard juga secara eksplisit
        lrn_p = os.path.join(BASE_DIR, "data", f"{s}_learning.json")
        sol_p = os.path.join(BASE_DIR, "data", "solution_sources", f"{s.upper()}_SOLUTIONS.json")
        kunci_p = os.path.join(BASE_DIR, "data", "kunci", f"{s}_kunci.json")
        img_dir = os.path.join(BASE_DIR, "data", mapel, f"paket_{paket}", "images")

        qg_status = "PASS"
        qg_error = None
        if os.path.isfile(lrn_p) and os.path.isfile(sol_p):
            with open(lrn_p, "r", encoding="utf-8") as f:
                ldoc = json.load(f)
            with open(sol_p, "r", encoding="utf-8") as f:
                sdoc = json.load(f)
            kdoc = None
            if os.path.isfile(kunci_p):
                with open(kunci_p, "r", encoding="utf-8") as f:
                    kdoc = json.load(f)
            try:
                assert_package_integrity(slug=s, learning_doc=ldoc, solutions_doc=sdoc, img_dir=img_dir, kunci_doc=kdoc)
            except QualityGuardError as qge:
                qg_status = "FAIL"
                qg_error = str(qge)
                discovered_bugs.append({
                    "target": s,
                    "phase": "QualityGuard",
                    "category": qge.category,
                    "message": qge.message,
                    "violations": qge.violations
                })
        else:
            qg_status = "INCOMPLETE"
            discovered_bugs.append({
                "target": s,
                "phase": "Filesystem",
                "category": "FILE_MISSING",
                "message": f"File learning/solusi tidak ditemukan ({lrn_p} / {sol_p})",
                "violations": []
            })

        if issues:
            for iss in issues:
                discovered_bugs.append({
                    "target": s,
                    "phase": "AutomatedAuditor",
                    "category": "AUDIT_ISSUE",
                    "message": iss,
                    "violations": []
                })

        audit_results[s] = {
            "issues": issues,
            "warnings": warnings,
            "qg_status": qg_status,
            "qg_error": qg_error
        }
        total_issues += len(issues)
        total_warnings += len(warnings)

    print("\n" + "=" * 80)
    print("📊 REKAPITULASI AUDIT DETERMINISTIK WAVE 2")
    print("=" * 80)
    for s, res in audit_results.items():
        qg_icon = "✅" if res["qg_status"] == "PASS" else "❌"
        audit_icon = "✅ PASS" if not res["issues"] else f"❌ FAIL ({len(res['issues'])} issues)"
        print(f"• {s:<30} : Audit={audit_icon} | QualityGuard={qg_icon} {res['qg_status']} | Warnings={len(res['warnings'])}")

    # Simpan laporan temuan bug jika ada
    bug_report_path = os.path.join(BASE_DIR, "scratch", "wave2_bug_report.json")
    with open(bug_report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "targets": WAVE_2_SLUGS,
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "discovered_bugs": discovered_bugs,
            "audit_results": audit_results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n📁 Laporan audit tersimpan di: {bug_report_path}")

    if total_issues == 0 and not discovered_bugs:
        print("\n🎉 HASIL AKHIR: 100% LOLOS AUDIT ZERO-TRUST! (0 BUGS / 0 ISSUES)")
        return True
    else:
        print(f"\n⚠️ DITEMUKAN {len(discovered_bugs)} TEMUAN/BUG! MEMBUTUHKAN TINDAK LANJUT.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
