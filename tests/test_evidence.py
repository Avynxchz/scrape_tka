# -*- coding: utf-8 -*-
"""tests/test_evidence.py — Pengujian Evidence Builder (Fase A2).

Menguji:
1. Fixture persona Terburu (P1).
2. Fixture persona Yakin-tapi-salah (P3).
3. Fixture persona Data-tipis (P8).
4. Skema ketat coach_input_v1, pembatasan fokus_soal maks 8, batasan karakter,
   dan estimasi ukuran token payload (< 3.500 token).
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "tests", "fixtures"))

from autopsy.evidence import build_evidence  # noqa: E402
from personas import p1_terburu, p3_yakin_salah, p8_data_tipis, p4_ragu_benar, p5_waktu_habis  # noqa: E402

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    status = "PASS" if cond else "FAIL"
    print(f"{status} {name}" + (f" — {detail}" if detail and not cond else ""))


def estimate_tokens(obj):
    # Estimasi 1 token ~= 4 karakter JSON string
    dumped = json.dumps(obj, ensure_ascii=False)
    return len(dumped) // 4, len(dumped)


def test_persona_terburu():
    att = p1_terburu()
    ev = build_evidence(att)

    check("P1 versi = coach_input_v1", ev["versi"] == "coach_input_v1")
    check("P1 kebocoran #1 = terburu", ev["kebocoran"] and ev["kebocoran"][0]["label"] == "terburu")
    check("P1 fokus_soal ada dan <= 8", 1 <= len(ev["fokus_soal"]) <= 8)
    check("P1 label fokus_soal memuat terburu", any(x["label"] == "terburu" for x in ev["fokus_soal"]))

    # Cek kandidat tugas
    check("P1 kandidat_tugas memuat id & judul", bool(ev["kandidat_tugas"]) and "task_id" in ev["kandidat_tugas"][0])

    # Ukuran payload
    toks, chars = estimate_tokens(ev)
    check(f"P1 ukuran payload di bawah 3.500 token ({toks} token / {chars} char)", toks < 3500)


def test_persona_yakin_salah():
    att = p3_yakin_salah()
    ev = build_evidence(att)

    check("P3 versi = coach_input_v1", ev["versi"] == "coach_input_v1")
    check("P3 kebocoran #1 = yakin_salah", ev["kebocoran"] and ev["kebocoran"][0]["label"] == "yakin_salah")
    check("P3 data_tipis = False", ev["data_tipis"] is False)
    check("P3 fokus_soal memuat yakin_salah", any(x["label"] == "yakin_salah" for x in ev["fokus_soal"]))
    check("P3 topik memuat Peluang atau Barisan", any(t["topik"] in ("Peluang", "Barisan") for t in ev["topik"]))
    check("P3 yang_bagus terisi string valid", isinstance(ev["yang_bagus"], str) and len(ev["yang_bagus"]) > 0)

    toks, chars = estimate_tokens(ev)
    check(f"P3 ukuran payload di bawah 3.500 token ({toks} token / {chars} char)", toks < 3500)


def test_persona_data_tipis():
    att = p8_data_tipis()
    ev = build_evidence(att)

    check("P8 versi = coach_input_v1", ev["versi"] == "coach_input_v1")
    check("P8 data_tipis = True", ev["data_tipis"] is True)
    check("P8 n_soal dan n_dijawab konsisten (9 dijawab, 16 kosong)", ev["n_dijawab"] == 9 and ev["n_kosong"] == 16 and ev["n_soal"] == 25)
    check("P8 fokus_soal <= 8", len(ev["fokus_soal"]) <= 8)

    toks, chars = estimate_tokens(ev)
    check(f"P8 ukuran payload di bawah 3.500 token ({toks} token / {chars} char)", toks < 3500)


def test_field_constraints_and_limits():
    # Uji batasan karakter dan pembatasan fokus_soal
    att = p4_ragu_benar()
    ev = build_evidence(att)

    # Maksimal 2 ragu_benar
    n_ragu_benar = sum(1 for x in ev["fokus_soal"] if x["label"] == "ragu_benar")
    check("Maksimal 2 soal ragu_benar di fokus_soal", n_ragu_benar <= 2)

    # Uji kosong beruntun pada P5
    att_p5 = p5_waktu_habis()
    ev_p5 = build_evidence(att_p5)
    n_kosong = sum(1 for x in ev_p5["fokus_soal"] if x["label"] in ("kosong", "waktu_habis"))
    check("Soal kosong/waktu_habis beruntun hanya mengambil 1 wakil", n_kosong <= 1)

    for q in ev["fokus_soal"]:
        check(f"Q{q['no']} ringkas_soal <= 240 karakter", len(q["ringkas_soal"]) <= 240)
        check(f"Q{q['no']} pembahasan_ringkas <= 300 karakter", len(q["pembahasan_ringkas"]) <= 300)
        check(f"Q{q['no']} jejak <= 5 event", len(q["jejak"]) <= 5)
        check(f"Q{q['no']} pilar_refs non-empty", len(q["pilar_refs"]) > 0)


def run_all():
    print("=== TEST A2: EVIDENCE BUILDER (COACH_INPUT_V1) ===")
    test_persona_terburu()
    test_persona_yakin_salah()
    test_persona_data_tipis()
    test_field_constraints_and_limits()
    print(f"\n{len(PASS)} lulus, {len(FAIL)} gagal\n")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    run_all()
