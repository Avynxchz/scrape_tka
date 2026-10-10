# Analisis perilaku tryout — TKA Master (FASE 4, T4.1).
#
# FUNGSI MURNI: input dict -> output dict. Tanpa I/O, tanpa database, tanpa AI.
# Aturan label: Lampiran C. Ambang: config/analyzer.json (versinya dicatat).
#
# Input attempt:
#   { "duration_limit_s": int, "n_questions": int, "ended_by": "user"|"timer",
#     "kunci": {soal_id: kunci},   # opsional; bila ada dipakai untuk "jawaban pertama benar"
#     "items": [ { "soal_id": str, "position": int (1-based), "topic_id": str|None,
#                  "first_answer": str|None, "final_answer": str|None,
#                  "is_correct": bool, "active_ms": int,
#                  "first_answer_ms": int|None, "change_count": int,
#                  "flagged_ragu": bool, "visit_count": int }, ... ] }
#
# is_correct dihitung SERVER dari kunci (klien tidak boleh menentukan).

import json
import os
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config(path=None):
    with open(path or os.path.join(BASE_DIR, "config", "analyzer.json"),
              encoding="utf-8") as f:
        return json.load(f)


def _answered(item):
    return item.get("final_answer") not in (None, "")


def label_item(item, jatah_ms, ended_by, n_questions, cfg, kunci=None):
    """Satu primary_label per soal, sesuai urutan prioritas Lampiran C.2."""
    ragu = bool(item.get("flagged_ragu"))
    correct = bool(item.get("is_correct"))
    active = item.get("active_ms") or 0

    first_correct = False
    if kunci:
        first = item.get("first_answer")
        key = kunci.get(item.get("soal_id"))
        if first not in (None, "") and key is not None:
            first_correct = str(first) == str(key)

    # 1-2: tidak dijawab
    if not _answered(item):
        pos = item.get("position") or 0
        if ended_by == "timer" and pos >= cfg["waktu_habis_pos_ratio"] * n_questions:
            return "waktu_habis"
        return "kosong"
    # 3: jawaban pertama benar -> akhir salah
    if first_correct and not correct:
        return "overthinking"
    # 4: salah + jauh di bawah jatah
    if not correct and active < max(cfg["terburu_min_ms"],
                                    cfg["terburu_ratio"] * jatah_ms):
        return "terburu"
    # 5: salah + lebih dari 2x jatah
    if not correct and active > cfg["macet_ratio"] * jatah_ms:
        return "macet"
    # 6-7: salah, yakin vs ragu
    if not correct and not ragu:
        return "yakin_salah"
    if not correct and ragu:
        return "ragu_salah"
    # 8: benar tapi ragu = rapuh (bukan kebocoran)
    if correct and ragu:
        return "ragu_benar"
    # 9
    return "aman"


def flags_item(item, primary_label, jatah_ms, cfg):
    flags = []
    if (item.get("change_count") or 0) >= cfg["ganti_banyak_min"]:
        flags.append("ganti_banyak")
    if primary_label in ("aman", "ragu_benar") and \
            (item.get("active_ms") or 0) > cfg["lambat_benar_ratio"] * jatah_ms:
        flags.append("lambat_benar")
    return flags


def _bukti(label, n, jatah_ms, cfg):
    if label == "terburu":
        det = max(cfg["terburu_min_ms"], cfg["terburu_ratio"] * jatah_ms) / 1000
        return f"{n} soal dijawab kurang dari {det:g} detik dan salah"
    if label == "overthinking":
        return f"{n} soal: jawaban pertama benar lalu diganti menjadi salah"
    if label == "macet":
        mnt = cfg["macet_ratio"] * jatah_ms / 60000
        return f"{n} soal menghabiskan lebih dari {mnt:g} menit dan salah"
    if label == "yakin_salah":
        return f"{n} soal dijawab tanpa ragu-ragu tapi salah"
    if label == "ragu_salah":
        return f"{n} soal ditandai ragu-ragu dan salah"
    if label == "waktu_habis":
        return f"{n} soal tidak sempat dikerjakan (waktu habis)"
    if label == "kosong":
        return f"{n} soal belum terjawab"
    return f"{n} soal berlabel {label}"


def _topic_stats(labeled, jatah_ms, cfg):
    groups = {}
    for it in labeled:
        t = it.get("topic_id") or "tanpa_topik"
        g = groups.setdefault(t, {"n": 0, "benar": 0, "waktu_ms": 0,
                                  "labels": Counter()})
        g["n"] += 1
        if it.get("is_correct"):
            g["benar"] += 1
        g["waktu_ms"] += it.get("active_ms") or 0
        g["labels"][it["primary_label"]] += 1
    out = []
    for topic, g in groups.items():
        n, benar = g["n"], g["benar"]
        out.append({
            "topik": topic,
            "n": n,
            "benar": benar,
            "akurasi": round(benar / n, 3) if n else 0,
            "rata_waktu_s": round(g["waktu_ms"] / n / 1000, 1) if n else 0,
            "n_salah": n - benar,
            "label_dominan": g["labels"].most_common(1)[0][0] if g["labels"] else None,
        })
    prior = [t for t in out
             if (t["n"] >= cfg["topik_min_n"] and
                 t["akurasi"] < cfg["topik_max_akurasi"])
             or t["n_salah"] >= cfg["topik_min_salah"]]
    prior.sort(key=lambda t: -t["n_salah"])
    return out, prior


def analyze(attempt, cfg=None):
    """Analisis satu attempt. Kembalikan dict hasil (JSON-able)."""
    cfg = cfg or load_config()
    items = attempt.get("items", []) or []
    n = attempt.get("n_questions") or len(items) or 1
    dur_s = attempt.get("duration_limit_s") or 0
    jatah_ms = (dur_s * 1000 / n) if dur_s and n else cfg["default_jatah_ms"]
    ended_by = attempt.get("ended_by", "user")
    kunci = attempt.get("kunci") or {}

    labeled = []
    for it in items:
        lb = label_item(it, jatah_ms, ended_by, n, cfg, kunci)
        labeled.append({**it, "primary_label": lb,
                        "flags": flags_item(it, lb, jatah_ms, cfg)})

    answered = [x for x in labeled if _answered(x)]
    n_answered = len(answered)
    total_active_ms = sum(x.get("active_ms") or 0 for x in labeled)

    data_tipis = (n_answered < cfg["data_tipis_min_answered"] or
                  (dur_s and total_active_ms <
                   cfg["data_tipis_active_ratio"] * dur_s * 1000))

    # fatigue: akurasi sepertiga terakhir turun >= 25pp vs sepertiga pertama
    fatigue = False
    if n_answered >= cfg["fatigue_min_answered"]:
        by_pos = sorted(answered, key=lambda x: x.get("position") or 0)
        k = max(1, len(by_pos) // 3)
        first = by_pos[:k]
        last = by_pos[-k:]
        acc = lambda grp: sum(1 for x in grp if x.get("is_correct")) / len(grp)
        if acc(first) - acc(last) >= cfg["fatigue_drop_pp"] / 100:
            fatigue = True

    # kebocoran: soal_hilang x bobot_pulih, top-3
    counts = Counter(x["primary_label"] for x in labeled
                     if x["primary_label"] not in ("aman", "ragu_benar"))
    leaks = []
    for label, cnt in counts.items():
        bobot = cfg["bobot_pulih"].get(label)
        if cnt > 0 and bobot:
            leaks.append({
                "label": label,
                "soal_hilang": cnt,
                "bobot_pulih": bobot,
                "prioritas": round(cnt * bobot, 3),
                "bukti": _bukti(label, cnt, jatah_ms, cfg),
                "contoh": [x.get("soal_id") for x in labeled
                           if x["primary_label"] == label][:3],
            })
    leaks.sort(key=lambda x: (-x["prioritas"], x["label"]))
    leaks = leaks[:cfg["max_kebocoran"]]

    rapuh_ids = [x.get("soal_id") for x in labeled
                 if x["primary_label"] == "ragu_benar"]

    topics, topik_prioritas = _topic_stats(labeled, jatah_ms, cfg)

    return {
        "config_version": cfg.get("version", "analyzer_v1"),
        "n_questions": n,
        "n_answered": n_answered,
        "n_correct": sum(1 for x in labeled if x.get("is_correct")),
        "jatah_ms": int(jatah_ms),
        "data_tipis": bool(data_tipis),
        "fatigue": bool(fatigue),
        "kebocoran": leaks,
        "rapuh_ids": rapuh_ids,
        "rapuh_catatan": (f"{len(rapuh_ids)} soal dijawab benar tapi ditandai "
                          "ragu-ragu — konsepnya rapuh, perlu dikunci."
                          if len(rapuh_ids) >= cfg["rapuh_min_tampil"] else None),
        "topik": topics,
        "topik_prioritas": topik_prioritas,
        "items": labeled,
    }
