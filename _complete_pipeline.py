# -*- coding: utf-8 -*-
"""_complete_pipeline.py — Lengkapi fase 3 & 4 untuk paket yang belum tuntas.

Fase 3: transkripsi sidecar untuk gambar yang belum tercover
         (MTL P1: 1, MTL P2: 7, Sejarah P2: 7 gambar).
Fase 4: soal_serupa MTL P1 yang masih 0/20 (solusi 5 Pilar sudah lengkap
         sehingga hanya bagian soal serupa yang dijalankan).
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from pipeline.swarm_manager import swarm_engine
from pipeline.subject_catalog import MASTER_CATALOG

TARGETS = [MASTER_CATALOG["matematika_lanjut_paket_1"],
           MASTER_CATALOG["matematika_lanjut_paket_2"],
           MASTER_CATALOG["sejarah_paket_2"]]

print("=" * 70)
print("TAHAP A — FASE 3: VISIONARY SCANNER (sidecar untuk gambar kurang)")
print("=" * 70)
try:
    swarm_engine._execute_divisi_3_visionary(TARGETS)
    print("FASE 3 SELESAI.")
except Exception as e:
    print(f"FASE 3 ERROR: {e}")

print("=" * 70)
print("TAHAP B — FASE 4: REASONING API (soal_serupa MTL P1)")
print("=" * 70)
try:
    swarm_engine._execute_divisi_4_reasoning_api(TARGETS)
    print("FASE 4 SELESAI.")
except Exception as e:
    print(f"FASE 4 ERROR: {e}")

# Ringkasan akhir
import json
for slug in ("matematika_lanjut_paket_1", "matematika_lanjut_paket_2",
             "sejarah_paket_2"):
    with open(os.path.join("data", f"{slug}_learning.json"), encoding="utf-8") as f:
        d = json.load(f)
    n_serupa = sum(1 for q in d["soal"] if (q.get("soal_serupa") or {}).get("pertanyaan"))
    print(f"{slug}: soal_serupa {n_serupa}/{len(d['soal'])}")

sc = json.load(open("data/sejarah_paket_2_sidecar_transcriptions.json", encoding="utf-8"))
print(f"sejarah_paket_2 sidecar: {len(sc)} transkripsi")
print("SELESAI SEMUA.")
