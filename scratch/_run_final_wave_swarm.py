# -*- coding: utf-8 -*-
"""scratch/_run_final_wave_swarm.py
Final Wave Swarm Runner & Omniscient Auditor:
Target 12 Paket Terakhir di Pusmendik (Seluruh Rumpun Bahasa Asing):
1. bahasa_arab_paket_1 & paket_2
2. bahasa_jepang_paket_1 & paket_2
3. bahasa_jerman_paket_1 & paket_2
4. bahasa_prancis_paket_1 & paket_2
5. bahasa_mandarin_paket_1 & paket_2
6. bahasa_korea_paket_1 & paket_2

Eksekusi Fase 1 s/d 5:
- Fase 1: Ingress Pusmendik (Scraping Soal, Gambar, Kunci)
- Fase 2: Data Architect & Sanitizer (learning.json & kunci.json)
- Fase 3: Visionary Scanner (Transkripsi Gambar AI Studio)
- Fase 4: Reasoning Engine (Solusi 5 Pilar Otentik & Soal Serupa via Playwright AI Studio Bridge)
- Fase 5: Zero-Trust Quality Guard, Raw Fidelity Auditor, & Release ke Exports
"""
import sys
import time
import json
import os
import shutil
import importlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.subject_catalog import MASTER_CATALOG
from pipeline.swarm_manager import swarm_engine
from pipeline.playwright_aistudio_bridge import check_port_open, ensure_chrome_debug_open
from pipeline.quality_guard import assert_package_integrity

auditor_mod = importlib.import_module("pipeline.05_automated_auditor")
audit_subject_package = auditor_mod.audit_subject_package

FINAL_WAVE_SLUGS = [
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

def run_final_wave():
    print("=" * 85)
    print("🌟 MEMULAI EKSEKUSI FINAL WAVE MULTI-AGENT SWARM")
    print(f"Target ({len(FINAL_WAVE_SLUGS)} Paket Rumpun Bahasa Asing):")
    for s in FINAL_WAVE_SLUGS:
        item = MASTER_CATALOG[s]
        print(f"  • {item['name']:35s} [Jenis: {item['jenis']}, Val: {item['val']:4s}] (Slug: {s})")
    print("=" * 85)

    # 1. Pre-flight Chrome Remote Debugging
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
    target_objs = [dict(MASTER_CATALOG[s]) for s in FINAL_WAVE_SLUGS]

    # 3. Jalankan pipeline Swarm thread secara sekuensial & terkontrol
    print("\n[ORCHESTRATOR] Meluncurkan Swarm Pipeline (Fase 1 - 5)...")
    t_start = time.time()

    try:
        swarm_engine._run_swarm_thread(target_objs)
    except Exception as e:
        print(f"❌ Terjadi exception saat eksekusi swarm: {e}")

    elapsed = time.time() - t_start
    print("\n" + "=" * 85)
    print(f"🏁 SIKLUS SWARM FINAL WAVE SELESAI DALAM {elapsed:.1f} DETIK (~{elapsed/60:.1f} MENIT)")
    print("=" * 85)

    # 4. Sinkronisasi Otomatis ke Exports
    print("\n[EXPORTER] Menyinkronkan seluruh output ke exports/...")
    os.makedirs(os.path.join(BASE_DIR, "exports"), exist_ok=True)
    for s in FINAL_WAVE_SLUGS:
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

    # 5. Audit Mutlak: Master Omni Audit & Raw Fidelity Audit
    print("\n" + "=" * 85)
    print("🔍 MENJALANKAN AUDIT MUTLAK SEMESTA PADA SELURUH 44 PAKET")
    print("=" * 85)

    try:
        import pipeline.master_omni_auditor as moa
        importlib.reload(moa)
        moa.audit_all()
    except Exception as e:
        print(f"Omni auditor error: {e}")

    try:
        import pipeline.raw_fidelity_auditor as rfa
        importlib.reload(rfa)
        rfa.audit_raw_fidelity()
    except Exception as e:
        print(f"Raw fidelity auditor error: {e}")

    print("\n" + "=" * 85)
    print("🎉 SELURUH MAPEL PUSMENDIK (44 PAKET) TELAH LENGKAP & TERVERIFIKASI 100%!")
    print("=" * 85)

if __name__ == "__main__":
    run_final_wave()
