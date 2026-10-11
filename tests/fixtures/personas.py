# Delapan persona uji — Lampiran C.4 (FASE 4, T4.3).
# Tiap fungsi mengembalikan attempt dict untuk autopsy/analyzer.py.

JATAH_MS = 180_000  # 3 menit/soal (durasi 75 mnt / 25 soal)


def _item(soal_id, pos, correct=True, active_ms=60_000, ragu=False,
          changes=0, topic=None, first_ok=None, answered=True):
    final = "A" if correct else "B"
    first = "A" if (first_ok if first_ok is not None else correct) else "B"
    return {
        "soal_id": soal_id, "position": pos, "topic_id": topic,
        "first_answer": first if answered else None,
        "final_answer": final if answered else None,
        "is_correct": correct and answered,
        "active_ms": active_ms, "first_answer_ms": 5_000,
        "change_count": changes, "flagged_ragu": ragu, "visit_count": 1,
    }


def _attempt(items, kunci=None, ended_by="user", n=25, dur_s=4500):
    return {"duration_limit_s": dur_s, "n_questions": n, "ended_by": ended_by,
            "kunci": kunci or {}, "items": items}


def p1_terburu():
    """25 soal; 8 dijawab <30 dtk dan salah; 3 salah lain; sisanya benar."""
    items = [_item(f"P1-{i:02d}", i, correct=False, active_ms=20_000)
             for i in range(1, 9)]
    items += [_item(f"P1-{i:02d}", i, correct=False, active_ms=90_000)
              for i in range(9, 12)]
    items += [_item(f"P1-{i:02d}", i, correct=True, active_ms=90_000)
              for i in range(12, 26)]
    return _attempt(items)


def p2_plinplan():
    """6 soal: jawaban pertama benar -> akhir salah."""
    items = [_item(f"P2-{i:02d}", i, correct=False, active_ms=60_000,
                   changes=2, first_ok=True) for i in range(1, 7)]
    kunci = {f"P2-{i:02d}": "A" for i in range(1, 7)}
    return _attempt(items, kunci=kunci, n=6, dur_s=1080)


def p3_yakin_salah():
    """7 salah tanpa ragu, waktu normal, topik Peluang & Barisan."""
    items = [_item(f"P3-{i:02d}", i, correct=False, active_ms=90_000,
                   topic="Peluang") for i in range(1, 5)]
    items += [_item(f"P3-{i:02d}", i, correct=False, active_ms=90_000,
                    topic="Barisan") for i in range(5, 8)]
    items += [_item(f"P3-{i:02d}", i, correct=True, active_ms=90_000,
                    topic="Aljabar") for i in range(8, 26)]
    return _attempt(items)


def p4_ragu_benar():
    """8 benar + ragu; 2 salah."""
    items = [_item(f"P4-{i:02d}", i, correct=True, active_ms=90_000, ragu=True)
             for i in range(1, 9)]
    items += [_item(f"P4-{i:02d}", i, correct=False, active_ms=90_000)
              for i in range(9, 11)]
    items += [_item(f"P4-{i:02d}", i, correct=True, active_ms=90_000)
              for i in range(11, 16)]
    return _attempt(items, n=15, dur_s=2700)


def p5_waktu_habis():
    """Soal 21-25 kosong, ended_by=timer."""
    items = [_item(f"P5-{i:02d}", i, correct=True, active_ms=120_000)
             for i in range(1, 21)]
    items += [_item(f"P5-{i:02d}", i, answered=False, active_ms=0)
              for i in range(21, 26)]
    return _attempt(items, ended_by="timer")


def p6_macet():
    """4 soal >7 menit dan salah."""
    items = [_item(f"P6-{i:02d}", i, correct=False, active_ms=450_000)
             for i in range(1, 5)]
    items += [_item(f"P6-{i:02d}", i, correct=True, active_ms=90_000)
              for i in range(5, 26)]
    return _attempt(items)


def p7_capek():
    """Akurasi 90% di sepertiga awal, 40% di akhir."""
    items = []
    for i in range(1, 31):
        if i <= 10:
            correct = i != 10  # 9/10
        elif i <= 20:
            correct = i % 2 == 0  # 5/10
        else:
            correct = i in (21, 23, 25, 27)  # 4/10
        items.append(_item(f"P7-{i:02d}", i, correct=correct,
                           active_ms=90_000))
    return _attempt(items, n=30, dur_s=5400)


def p8_data_tipis():
    """Hanya 9 soal dijawab."""
    items = [_item(f"P8-{i:02d}", i, correct=(i % 2 == 1), active_ms=90_000)
             for i in range(1, 10)]
    items += [_item(f"P8-{i:02d}", i, answered=False, active_ms=0)
              for i in range(10, 26)]
    return _attempt(items)


PERSONAS = {
    "P1": p1_terburu, "P2": p2_plinplan, "P3": p3_yakin_salah,
    "P4": p4_ragu_benar, "P5": p5_waktu_habis, "P6": p6_macet,
    "P7": p7_capek, "P8": p8_data_tipis,
}
