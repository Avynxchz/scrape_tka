# Tes Fase 4 — T4.3 (runner Python biasa; tanpa pytest).
# Cara jalan: python3 tests/test_autopsy.py
# Keluar 0 = semua lulus.

import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "tests", "fixtures"))

from autopsy import analyzer, planner  # noqa: E402
from personas import PERSONAS  # noqa: E402

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))


def test_personas():
    results = {}
    for pid, make in PERSONAS.items():
        results[pid] = analyzer.analyze(make())

    r = results["P1"]
    check("P1 kebocoran #1 = terburu",
          r["kebocoran"] and r["kebocoran"][0]["label"] == "terburu",
          json.dumps([l["label"] for l in r["kebocoran"]]))

    r = results["P2"]
    check("P2 kebocoran #1 = overthinking",
          r["kebocoran"] and r["kebocoran"][0]["label"] == "overthinking",
          json.dumps([l["label"] for l in r["kebocoran"]]))

    r = results["P3"]
    check("P3 kebocoran #1 = yakin_salah",
          r["kebocoran"] and r["kebocoran"][0]["label"] == "yakin_salah")
    tops = {t["topik"] for t in r["topik_prioritas"]}
    check("P3 topik_prioritas memuat Peluang & Barisan",
          {"Peluang", "Barisan"} <= tops, str(tops))

    r = results["P4"]
    check("P4 rapuh_ids >= 3", len(r["rapuh_ids"]) >= 3,
          str(len(r["rapuh_ids"])))
    check("P4 tanpa kebocoran besar",
          all(l["soal_hilang"] <= 2 for l in r["kebocoran"]),
          json.dumps(r["kebocoran"]))

    r = results["P5"]
    check("P5 kebocoran #1 = waktu_habis",
          r["kebocoran"] and r["kebocoran"][0]["label"] == "waktu_habis",
          json.dumps([l["label"] for l in r["kebocoran"]]))

    r = results["P6"]
    check("P6 kebocoran #1 = macet",
          r["kebocoran"] and r["kebocoran"][0]["label"] == "macet",
          json.dumps([l["label"] for l in r["kebocoran"]]))

    r = results["P7"]
    check("P7 fatigue = true", r["fatigue"] is True)

    r = results["P8"]
    check("P8 data_tipis = true", r["data_tipis"] is True)

    return results


LIB = {
    "pilar": {
        "5": {"ref": "pilar-5", "title": "Pilar 5: Trik & Jebakan"},
        "4": {"ref": "pilar-4", "title": "Pilar 4: Langkah Cek Ulang"},
        "1": {"ref": "pilar-1", "title": "Pilar 1: Fondasi Konsep"},
        "3": {"ref": "pilar-3", "title": "Pilar 3: Intuisi"},
    },
    "kartu": {
        "anti_ceroboh": {"ref": "anti_ceroboh", "title": "Kartu Anti-Ceroboh"},
        "strategi_waktu": {"ref": "strategi_waktu", "title": "Kartu Strategi Waktu"},
    },
    "soal_serupa": {
        "Peluang": ["S-P1", "S-P2", "S-P3", "S-P4"],
        "Barisan": ["S-B1", "S-B2", "S-B3"],
        "Aljabar": ["S-A1", "S-A2", "S-A3"],
    },
    "simulasi": [{"ref": "MTK-P2", "title": "Simulasi Matematika Paket 2"}],
    "review": {"ref": "review", "title": "Tinjau ulang jawaban"},
}


def _known_refs():
    refs = set()
    for v in LIB["pilar"].values():
        refs.add(v["ref"])
    for v in LIB["kartu"].values():
        refs.add(v["ref"])
    for lst in LIB["soal_serupa"].values():
        refs.update(lst)
    for s in LIB["simulasi"]:
        refs.add(s["ref"])
    refs.add("review")
    return refs


def test_planner(results):
    with open(os.path.join(BASE, "config", "exam.json"), encoding="utf-8") as f:
        exam = json.load(f)
    analysis = results["P1"]  # kebocoran #1 = terburu
    kw = dict(today_iso="2026-10-09", tka_date_iso="2026-10-26",
              mapel="matematika", analysis=analysis, library=LIB,
              exam_cfg=exam, daily_minutes=25)
    p1 = planner.plan(**kw)
    p2 = planner.plan(**kw)
    check("planner deterministik", p1 == p2)

    days = p1["days"]
    check("exam_day = 2026-10-28 (26+offset MTK=2)", p1["exam_day"] == "2026-10-28")
    check("ada hari H-1", any(d["label_h"] == "H-1" for d in days))
    check("tidak ada tugas setelah H-1",
          all(d["date"] <= "2026-10-27" for d in days))

    h1 = next(d for d in days if d["label_h"] == "H-1")
    check("H-1 tanpa materi baru",
          all(t["type"] not in ("pilar", "soal_serupa", "simulasi_ulang")
              for t in h1["tasks"]),
          json.dumps([t["type"] for t in h1["tasks"]]))
    check("H-1 <= 15 menit", h1["minutes"] <= 15, str(h1["minutes"]))

    normal = [d for d in days if d["label_h"] not in ("H-1", "H-2", "H-3")]
    check("hari biasa <= daily_minutes",
          all(d["minutes"] <= 25 for d in normal),
          str(max(d["minutes"] for d in normal)) if normal else "no-days")

    known = _known_refs()
    bad = []
    for d in days:
        for t in d["tasks"]:
            refs = t["ref"] if isinstance(t["ref"], list) else [t["ref"]]
            for r in refs:
                if r not in known:
                    bad.append(r)
    check("semua ref ada di konten", not bad, str(bad[:3]))

    ids1 = [t["id"] for d in p1["days"] for t in d["tasks"]]
    ids2 = [t["id"] for d in p2["days"] for t in d["tasks"]]
    check("task_id stabil", ids1 == ids2 and len(set(ids1)) == len(ids1))

    h3 = next((d for d in days if d["label_h"] == "H-3"), None)
    check("H-3 simulasi_ulang (rentang>=5 hari)",
          h3 is not None and any(t["type"] == "simulasi_ulang" for t in h3["tasks"]))


def main():
    print("== analyzer: 8 persona ==")
    results = test_personas()
    print("== planner ==")
    test_planner(results)
    print(f"\n{len(PASS)} lulus, {len(FAIL)} gagal")
    if FAIL:
        print("GAGAL:", FAIL)
        sys.exit(1)


if __name__ == "__main__":
    main()
