# -*- coding: utf-8 -*-
"""_retry_serupa_sidecar.py — Retry fase 4 (soal_serupa MTL P1) + sisa sidecar.

Jeda antar-panggilan diperbesar agar tidak menggosok kuota per-menit kunci
Gemini (penyebab gagalnya run pertama: 429 setelah fase 3 vision).
"""
import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from pipeline.swarm_manager import swarm_engine
from pipeline.subject_catalog import MASTER_CATALOG

def report():
    for slug in ("matematika_lanjut_paket_1", "matematika_lanjut_paket_2",
                 "sejarah_paket_2"):
        with open(os.path.join("data", f"{slug}_learning.json"), encoding="utf-8") as f:
            d = json.load(f)
        n = sum(1 for q in d["soal"] if (q.get("soal_serupa") or {}).get("pertanyaan"))
        print(f"{slug}: soal_serupa {n}/{len(d['soal'])}")
    for mk, p in (("matematika_lanjut", 2), ("sejarah", 2)):
        slug = f"{mk}_paket_{p}"
        sc = json.load(open(f"data/{slug}_sidecar_transcriptions.json", encoding="utf-8"))
        imgdir = f"data/{mk}/paket_{p}/images"
        files = [f for f in os.listdir(imgdir) if f.endswith(".png")]
        print(f"{slug}: sidecar {len(sc)}/{len(files)}")

print("Tunggu 60s agar kuota per-menit kunci Gemini pulih...", flush=True)
time.sleep(60)

print("=== FASE 4 retry: soal_serupa MTL P1 ===", flush=True)
try:
    swarm_engine._execute_divisi_4_reasoning_api(
        [MASTER_CATALOG["matematika_lanjut_paket_1"]])
    print("FASE 4 SELESAI.", flush=True)
except Exception as e:
    print(f"FASE 4 ERROR: {e}", flush=True)

time.sleep(30)
print("=== FASE 3 retry: sisa sidecar (MTL P2 + Sejarah P2) ===", flush=True)
try:
    swarm_engine._execute_divisi_3_visionary([
        MASTER_CATALOG["matematika_lanjut_paket_2"],
        MASTER_CATALOG["sejarah_paket_2"]])
    print("FASE 3 SELESAI.", flush=True)
except Exception as e:
    print(f"FASE 3 ERROR: {e}", flush=True)

print("=== HASIL AKHIR ===", flush=True)
report()
