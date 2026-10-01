# -*- coding: utf-8 -*-
"""scratch/run_remaining_purifier.py — Runner untuk menuntaskan 6 paket tersisa via Playwright AI Studio Bridge."""
import sys, os, time
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.playwright_aistudio_bridge import run_phase_4_via_playwright

REMAINING_SLUGS = [
    "ekonomi_paket_1",
    "ekonomi_paket_2",
    "bahasa_inggris_paket_1",
    "bahasa_inggris_paket_2",
    "matematika_paket_2",
    "kewirausahaan_paket_2",
]

print("=" * 80)
print(f"🚀 MEMULAI OPERASI PURIFIER UNTUK {len(REMAINING_SLUGS)} PAKET TERSISA")
print("=" * 80)

success_list = []
failed_list = []

for idx, slug in enumerate(REMAINING_SLUGS, 1):
    print("\n" + "#" * 80)
    print(f"[{idx}/{len(REMAINING_SLUGS)}] PROSES TARGET: {slug.upper()}")
    print("#" * 80)
    try:
        run_phase_4_via_playwright(slug=slug, port=9222)
        print(f"✅ TARGET {slug.upper()} 100% SUKSES DAN LOLOS AUDIT!")
        success_list.append(slug)
    except Exception as e:
        print(f"❌ TARGET {slug.upper()} GAGAL DENGAN ERROR: {e}")
        failed_list.append((slug, str(e)))
    time.sleep(3)

print("\n" + "=" * 80)
print("📊 HASIL AKHIR OPERASI PURIFIER")
print("=" * 80)
print(f"Sukses: {len(success_list)}/{len(REMAINING_SLUGS)}")
for s in success_list:
    print(f"  • {s}: ✅ 100% PASS")
if failed_list:
    print(f"Gagal: {len(failed_list)}/{len(REMAINING_SLUGS)}")
    for s, err in failed_list:
        print(f"  • {s}: ❌ {err}")
