# -*- coding: utf-8 -*-
"""scratch/verify_bug_fixes.py — Verifikasi perbaikan Bug 1 (Guru Autopsi Skor 0%) & Bug 2 (Ruang AI 0 Soal)."""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("VISITOR_ADMIN_KEY", "test_admin_key_12345")

import ai_room
from autopsy import evidence, coach_template

print("=== 1. VERIFIKASI BUG 1: GURU AUTOPSI SKOR AKURASI ===")

# Simulasi attempt Bahasa Indonesia Paket 1: 20 soal, 3 benar, 17 salah (skor 15%)
# Kunci Bahasa Indonesia Paket 1:
kunci_map = ai_room.load_kunci_mapel("bahasa_indonesia", 1)
print(f"Kunci mapel bahasa_indonesia paket 1 termuat: {len(kunci_map)} butir soal.")

items = []
for i in range(1, 21):
    pos = str(i)
    kunci = kunci_map.get(pos, "A")
    # Jadikan soal 1, 2, 3 benar, sisanya salah
    if i <= 3:
        user_ans = kunci
    else:
        # Pilih jawaban yang pasti salah
        user_ans = "B" if kunci != "B" else "C"
    
    # Client mengirim is_correct: True untuk 1..3, False untuk 4..20
    is_corr = (i <= 3)
    items.append({
        "soal_id": f"bahasa_indonesia:1:{i}",
        "position": i,
        "first_answer": user_ans,
        "final_answer": user_ans,
        "is_correct": is_corr,
        "active_ms": 3000,
        "waktu_detik": 3,
        "change_count": 0,
        "flagged_ragu": False,
        "visit_count": 1
    })

attempt_data = {
    "subject": "bahasa_indonesia",
    "mapel": "bahasa_indonesia",
    "paket": 1,
    "n_questions": 20,
    "duration_limit_s": 1800,
    "ended_by": "user",
    "score": 15,
    "n_correct": 3,
    "items": items
}

# Test 1A: Evidence builder dengan items yang memiliki is_correct
ev1 = evidence.build_evidence(attempt_data)
print(f"Test 1A - Hasil evidence: n_benar={ev1['n_benar']}, skor_pct={ev1['skor_pct']}%")
assert ev1['n_benar'] == 3, f"Expected 3 benar, got {ev1['n_benar']}"
assert ev1['skor_pct'] == 15, f"Expected 15% skor, got {ev1['skor_pct']}"

# Test 1B: Fallback template coach
out1 = coach_template.generate_template(ev1)
print(f"Test 1B - Fallback template penilaian: '{out1['penilaian']}'")
assert "15%" in out1['penilaian'], f"Expected '15%' in penilaian, got '{out1['penilaian']}'"
assert "0%" not in out1['penilaian'], f"Unexpected '0%' in penilaian!"

# Test 1C: Server enrichment saat payload TIDAK membawa is_correct (auto-evaluate dari kunci)
items_without_corr = []
for it in items:
    clean_it = dict(it)
    del clean_it["is_correct"]
    items_without_corr.append(clean_it)

attempt_raw = {
    "subject": "bahasa_indonesia",
    "mapel": "bahasa_indonesia",
    "paket": 1,
    "n_questions": 20,
    "duration_limit_s": 1800,
    "ended_by": "user",
    "items": items_without_corr
}

# Jalankan logika auto-eval seperti di _handle_post_autopsy_coach
for x in attempt_raw["items"]:
    if x.get("is_correct") is None:
        x["is_correct"] = ai_room.is_answer_correct(x, "bahasa_indonesia", 1)

ev1c = evidence.build_evidence(attempt_raw)
print(f"Test 1C - Auto-eval dari kunci: n_benar={ev1c['n_benar']}, skor_pct={ev1c['skor_pct']}%")
assert ev1c['n_benar'] == 3, f"Expected 3 benar via auto-eval, got {ev1c['n_benar']}"
assert ev1c['skor_pct'] == 15, f"Expected 15% via auto-eval, got {ev1c['skor_pct']}"

print("-> BUG 1 FIX VERIFIED: Skor 15% dan 3 benar terhitung sempurna!\n")

print("=== 2. VERIFIKASI BUG 2: AI ROOM DATA AGREGAT & SOAL SALAH ===")

# Test 2A: Agregasi dari attempt user
aggr = ai_room.calculate_mapel_aggregates([attempt_data], "bahasa_indonesia", is_guest=False)
print(f"Test 2A - Agregat: total_soal={aggr['total_soal']}, akurasi={aggr['akurasi']}%, rata2_waktu={aggr['waktu_rata2_per_soal']}s")
assert aggr['total_soal'] == 20, f"Expected 20 soal, got {aggr['total_soal']}"
assert aggr['akurasi'] == 15.0, f"Expected 15.0% akurasi, got {aggr['akurasi']}"
assert aggr['total_attempt'] == 1, f"Expected 1 attempt, got {aggr['total_attempt']}"

# Test 2B: 5 Soal terakhir yang salah
last_wrong = ai_room.get_last_wrong_questions([attempt_data], "bahasa_indonesia", limit=5)
print(f"Test 2B - Jumlah soal salah diambil: {len(last_wrong)} butir")
assert len(last_wrong) == 5, f"Expected 5 salah, got {len(last_wrong)}"
print(f"  Contoh soal salah #1: Nomor {last_wrong[0]['nomor']}, Topik={last_wrong[0]['topik']}, User={last_wrong[0]['user_answer']}, Kunci={last_wrong[0]['kunci']}")

# Test 2C: System Prompt Ruang AI Mapel
prompt = ai_room.build_ai_room_system_prompt(aggr, last_wrong)
print("Test 2C - Potongan prompt AI Room:")
for line in prompt.split("\n")[4:12]:
    print("  ", line)
assert "Total soal dikerjakan: 20 butir" in prompt
assert "Akurasi keseluruhan: 15.0%" in prompt

# Test 2D: Signature & Bearer auth pada fetch_supabase_attempts
import inspect
sig = inspect.signature(ai_room.fetch_supabase_attempts)
print(f"Test 2D - Signature fetch_supabase_attempts: {sig}")
assert "user_token" in sig.parameters, "Parameter user_token harus ada pada fetch_supabase_attempts"

print("-> BUG 2 FIX VERIFIED: Ruang AI membaca 20 soal, akurasi 15%, dan 5 butir soal salah!\n")
print("=== SEMUA PENGUJIAN INTI LOLOS 100% ===")
