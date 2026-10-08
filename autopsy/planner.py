# Penyusun jadwal belajar harian — TKA Master (FASE 4, T4.2).
#
# FUNGSI MURNI: input dict -> output dict. Tanpa I/O, tanpa database, tanpa AI.
# Aturan: Lampiran D. Deterministik: input sama -> output sama.
#
# Input plan(...):
#   today_iso, tka_date_iso ("2026-10-26"), mapel ("matematika"),
#   analysis: hasil autopsy/analyzer.py (kebocoran top-3, rapuh_ids),
#   library: pustaka konten {pilar:{...}, kartu:{...}, soal_serupa:{topik:[ref]},
#                            simulasi:[{ref,title}]},
#   exam_cfg: config/exam.json, daily_minutes=25.
#
# Setiap task: {id, type, ref, title, minutes, reason}.
# type: pilar | soal_serupa | kartu | tinjau_ragu | simulasi_ulang | tinjau_salah

import hashlib
from datetime import date, timedelta

# D.4: kebocoran -> konten (Pilar = konten statis yang SUDAH ADA)
_LEAK_CONTENT = {
    "terburu":      {"pilar": ["5", "4"], "kartu": "anti_ceroboh", "serupa": True},
    "overthinking": {"pilar": ["5", "4"], "kartu": "anti_ceroboh", "serupa": True},
    "yakin_salah":  {"pilar": ["1", "3"], "kartu": None,           "serupa": True},
    "ragu_salah":   {"pilar": ["1", "3"], "kartu": None,           "serupa": True},
    "macet":        {"pilar": [],         "kartu": "strategi_waktu", "serupa": True},
    "waktu_habis":  {"pilar": [],         "kartu": "strategi_waktu", "serupa": True},
    "kosong":       {"pilar": [],         "kartu": "strategi_waktu", "serupa": True},
}

_MENIT = {"pilar": 6, "soal_serupa_per_soal": 3, "kartu": 2, "tinjau_ragu": 8}


def _task_id(hari_ke, type_, ref):
    h = hashlib.sha1(f"{hari_ke}|{type_}|{ref}".encode()).hexdigest()[:4]
    return f"d{hari_ke}-{type_}-{h}"


def _parse_iso(s):
    return date(*map(int, s.split("-")))


def _label_h(day, exam_day):
    delta = (exam_day - day).days
    return f"H-{delta}" if delta > 0 else "H-0"


def _sessions_for_leak(leak, budget, hari_ke, day_iso, library, topics, kartu_used):
    """Susun sesi untuk satu kebocoran dalam budget menit. Kembalikan tasks."""
    tasks = []
    label = leak["label"]
    spec = _LEAK_CONTENT.get(label, {})
    used = 0

    def push(type_, ref, title, minutes, reason):
        tasks.append({"id": _task_id(hari_ke, type_, ref), "type": type_,
                      "ref": ref, "title": title, "minutes": minutes,
                      "reason": reason})

    # (a) pilar sesuai pemetaan D.4
    for p in spec.get("pilar", []):
        if used + _MENIT["pilar"] > budget:
            break
        info = (library.get("pilar") or {}).get(p)
        if not info:
            continue
        push("pilar", info["ref"], info["title"], _MENIT["pilar"], label)
        used += _MENIT["pilar"]
    # (b) soal serupa 3-5 dari topik terkait
    if spec.get("serupa"):
        refs = []
        for t in topics:
            refs += (library.get("soal_serupa") or {}).get(t, [])
        refs = refs[:5]
        if refs:
            n = min(5, max(3, len(refs)))
            refs = refs[:n]
            cost = n * _MENIT["soal_serupa_per_soal"]
            if used + cost <= budget:
                push("soal_serupa", refs,
                     f"{n} soal serupa", cost, label)
                used += cost
    # (c) kartu bila labelnya cocok; kartu sama maks 1x per 3 hari
    kartu = spec.get("kartu")
    if kartu and used + _MENIT["kartu"] <= budget:
        last = kartu_used.get(kartu)
        if last is None or (day_iso - last).days >= 3:
            info = (library.get("kartu") or {}).get(kartu)
            if info:
                push("kartu", info["ref"], info["title"],
                     _MENIT["kartu"], label)
                used += _MENIT["kartu"]
                kartu_used[kartu] = day_iso
    return tasks, used


def plan(today_iso, tka_date_iso, mapel, analysis, library, exam_cfg,
         daily_minutes=25):
    tka_date = _parse_iso(tka_date_iso)
    today = _parse_iso(today_iso)
    offset = (exam_cfg.get("exam_day_offset") or {}).get(mapel, 0)
    exam_day = tka_date + timedelta(days=offset)
    last_study = exam_day - timedelta(days=1)

    leaks = (analysis.get("kebocoran") or [])[:3]
    rapuh_ids = analysis.get("rapuh_ids") or []
    topics = [t["topik"] for t in (analysis.get("topik_prioritas") or [])]

    days = []
    if today > last_study:
        # Rentang kosong: rencana "hanya hari ini".
        tasks = []
        kartu = (_LEAK_CONTENT.get((leaks[0]["label"] if leaks else ""), {})
                 .get("kartu"))
        if kartu and (library.get("kartu") or {}).get(kartu):
            info = library["kartu"][kartu]
            tasks.append({"id": _task_id(1, "kartu", info["ref"]),
                          "type": "kartu", "ref": info["ref"],
                          "title": info["title"], "minutes": _MENIT["kartu"],
                          "reason": "hari_terakhir"})
        days.append({"date": today_iso, "hari_ke": 1, "label_h": "H-0",
                     "minutes": sum(t["minutes"] for t in tasks),
                     "tasks": tasks})
        return {"tka_date": tka_date_iso,
                "exam_day": exam_day.isoformat(), "days": days}

    all_days = []
    d = today
    while d <= last_study:
        all_days.append(d)
        d += timedelta(days=1)

    kartu_used = {}
    out_days = []
    n_days = len(all_days)
    for i, day in enumerate(all_days):
        hari_ke = i + 1
        day_iso = day.isoformat()
        label_h = _label_h(day, exam_day)
        tasks = []

        if day == last_study:
            # D.2 H-1: tinjau ragu (maks 8) + satu kartu. Tanpa materi baru.
            ragu = rapuh_ids[:8]
            if ragu:
                tasks.append({"id": _task_id(hari_ke, "tinjau_ragu", "review"),
                              "type": "tinjau_ragu", "ref": "review",
                              "soal_ids": ragu,
                              "title": f"Tinjau {len(ragu)} soal ragu-ragu",
                              "minutes": _MENIT["tinjau_ragu"],
                              "reason": "H-1"})
            top_label = leaks[0]["label"] if leaks else None
            kartu = (_LEAK_CONTENT.get(top_label, {}).get("kartu")
                     if top_label else None)
            if kartu and (library.get("kartu") or {}).get(kartu):
                info = library["kartu"][kartu]
                tasks.append({"id": _task_id(hari_ke, "kartu", info["ref"]),
                              "type": "kartu", "ref": info["ref"],
                              "title": info["title"],
                              "minutes": _MENIT["kartu"],
                              "reason": "H-1"})
        elif n_days >= 5 and day == last_study - timedelta(days=2):
            # D.2: H-3 simulasi ulang (sesi panjang, opsional)
            sims = library.get("simulasi") or []
            if sims:
                s = sims[0]
                tasks.append({"id": _task_id(hari_ke, "simulasi_ulang", s["ref"]),
                              "type": "simulasi_ulang", "ref": s["ref"],
                              "title": s["title"], "minutes": daily_minutes,
                              "reason": "simulasi_ulang", "long": True})
        elif n_days >= 5 and day == last_study - timedelta(days=1):
            # D.2: H-2 tinjau kebocoran 10 menit
            if leaks:
                tasks.append({"id": _task_id(hari_ke, "tinjau_salah",
                                             "review"),
                              "type": "tinjau_salah", "ref": "review",
                              "soal_ids": leaks[0]["contoh"][:5],
                              "title": "Tinjau soal yang salah",
                              "minutes": 10,
                              "reason": leaks[0]["label"]})
        else:
            # D.3: hari biasa — bagi daily_minutes proporsional prioritas
            if leaks:
                weights = [max(l["prioritas"], 0.01) for l in leaks]
                total_w = sum(weights)
                budgets = [max(5, int(daily_minutes * w / total_w))
                           for w in weights]
                # normalisasi agar jumlah = daily_minutes
                diff = daily_minutes - sum(budgets)
                budgets[0] += diff
                for leak, budget in zip(leaks, budgets):
                    ts, _ = _sessions_for_leak(leak, max(budget, 0), hari_ke,
                                               day, library, topics,
                                               kartu_used)
                    tasks.extend(ts)

        minutes = sum(t["minutes"] for t in tasks)
        out_days.append({"date": day_iso, "hari_ke": hari_ke,
                         "label_h": label_h, "minutes": minutes,
                         "tasks": tasks})

    return {"tka_date": tka_date_iso, "exam_day": exam_day.isoformat(),
            "days": out_days}
