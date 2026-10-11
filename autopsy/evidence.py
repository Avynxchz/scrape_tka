# -*- coding: utf-8 -*-
"""autopsy/evidence.py — Evidence builder untuk Guru Autopsi (FASE A, A2).

FUNGSI MURNI: attempt dict + analyzer + planner -> coach_input_v1 dict.
Tanpa memanggil AI, tanpa query database langsung.
Mengikuti Kontrak Data Bagian 6.1.
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from autopsy import analyzer, planner

DEFAULT_LIB = {
    "pilar": {
        "5": {"ref": "pilar-5", "title": "Pilar 5: Trik & Jebakan"},
        "4": {"ref": "pilar-4", "title": "Pilar 4: Langkah Cek Ulang"},
        "1": {"ref": "pilar-1", "title": "Pilar 1: Fondasi Konsep"},
        "3": {"ref": "pilar-3", "title": "Pilar 3: Intuisi"},
        "2": {"ref": "pilar-2", "title": "Pilar 2: Strategi Waktu"},
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


def load_exam_cfg():
    cfg_path = os.path.join(BASE_DIR, "config", "exam.json")
    if os.path.isfile(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "exam_day_offset": {"matematika": 2, "bahasa_indonesia": 0, "bahasa_inggris": 1},
        "mapel": {"matematika": {"durasi_menit": 75, "jatah_per_soal_menit": 3.0, "soal": 25}},
    }


def _clean_text_snippet(text, max_len=240):
    if not text:
        return ""
    clean = " ".join(str(text).replace("\n", " ").split())
    if len(clean) > max_len:
        return clean[:max_len - 3] + "..."
    return clean


def build_evidence(attempt, analysis=None, tka_date_iso="2026-10-26",
                   today_iso="2026-10-10", library=None, exam_cfg=None,
                   content_map=None):
    """Membangun evidence pack coach_input_v1 dari data attempt."""
    exam_cfg = exam_cfg or load_exam_cfg()
    lib = library or DEFAULT_LIB
    content_map = content_map or {}

    # Jika hasil analisis belum diberikan, hitung menggunakan analyzer
    if analysis is None:
        analysis = analyzer.analyze(attempt)

    mapel = str(attempt.get("mapel") or attempt.get("subject") or "matematika").lower()
    paket = int(attempt.get("paket") or 1)
    items = attempt.get("items") or []
    labeled_items = analysis.get("items") or items
    n_q = int(attempt.get("n_questions") or len(labeled_items) or 25)
    dur_s = int(attempt.get("duration_limit_s") or 4500)
    durasi_batas_menit = max(1, round(dur_s / 60))
    ended_by = "timer" if attempt.get("ended_by") == "timer" else "user"

    # Waktu & statistik dasar
    total_active_ms = sum(int(x.get("active_ms") or 0) for x in labeled_items)
    durasi_aktif_menit = max(0, round(total_active_ms / 60000))
    n_answered = sum(1 for x in labeled_items if x.get("final_answer") not in (None, ""))
    n_benar = sum(1 for x in labeled_items if bool(x.get("is_correct")))
    n_kosong = max(0, n_q - n_answered)
    skor_pct = round(100 * n_benar / n_q) if n_q > 0 else 0

    # Hari menuju ujian
    hari_menuju_ujian = 16
    try:
        from datetime import date
        d_today = date(*map(int, today_iso.split("-")))
        d_tka = date(*map(int, tka_date_iso.split("-")))
        hari_menuju_ujian = max(0, (d_tka - d_today).days)
    except Exception:
        pass

    # Pola pengerjaan (awal, tengah, akhir)
    by_pos = sorted(labeled_items, key=lambda x: int(x.get("position") or 0))
    k = max(1, len(by_pos) // 3)
    seg1 = by_pos[:k]
    seg2 = by_pos[k:2 * k]
    seg3 = by_pos[2 * k:]

    def acc_pct(seg):
        if not seg:
            return 0
        c = sum(1 for x in seg if x.get("is_correct"))
        return round(100 * c / len(seg))

    # Median waktu pengerjaan per soal
    times = [
        int(x.get("waktu_detik") if x.get("waktu_detik") is not None
            else round((x.get("active_ms") or 0) / 1000))
        for x in labeled_items
    ]
    times.sort()
    if times:
        mid = len(times) // 2
        median_w = times[mid] if len(times) % 2 != 0 else round((times[mid - 1] + times[mid]) / 2)
    else:
        median_w = 0

    jatah_detik = round(dur_s / n_q) if n_q > 0 else 180

    pola = {
        "akurasi_awal_pct": acc_pct(seg1),
        "akurasi_tengah_pct": acc_pct(seg2),
        "akurasi_akhir_pct": acc_pct(seg3),
        "fatigue": bool(analysis.get("fatigue", False)),
        "median_waktu_detik": median_w,
        "jatah_detik": jatah_detik,
    }

    # Topik
    topics = []
    for t in analysis.get("topik", []):
        topics.append({
            "topik": t.get("topik") or "Umum",
            "n": int(t.get("n") or 0),
            "benar": int(t.get("benar") or 0),
            "akurasi_pct": round(float(t.get("akurasi") or 0) * 100),
        })

    # Kebocoran (maks 3)
    kebocoran = []
    for leak in (analysis.get("kebocoran") or [])[:3]:
        kebocoran.append({
            "label": leak.get("label"),
            "soal_hilang": int(leak.get("soal_hilang") or 0),
            "bukti": leak.get("bukti", ""),
            "contoh": leak.get("contoh") or [],
        })

    # Pemilihan fokus_soal (maks 8)
    PRIORITY_LABELS = ["overthinking", "terburu", "yakin_salah", "ragu_salah", "macet", "kosong"]
    fokus_items = []
    chosen_ids = set()

    for lbl in PRIORITY_LABELS:
        if len(fokus_items) >= 8:
            break
        matching = [
            x for x in labeled_items
            if x.get("primary_label") == lbl and str(x.get("soal_id")) not in chosen_ids
        ]
        # Satu wakil saja untuk kosong beruntun
        if lbl == "kosong":
            filtered_kosong = []
            last_pos = None
            for it in matching:
                pos = int(it.get("position") or 0)
                if last_pos is not None and pos == last_pos + 1:
                    last_pos = pos
                    continue
                filtered_kosong.append(it)
                last_pos = pos
            matching = filtered_kosong

        # Maksimal 3 soal per label
        for it in matching[:3]:
            if len(fokus_items) >= 8:
                break
            fokus_items.append(it)
            chosen_ids.add(str(it.get("soal_id")))

    # Tambah maksimal 2 soal ragu_benar
    if len(fokus_items) < 8:
        ragu_benar_items = [
            x for x in labeled_items
            if x.get("primary_label") == "ragu_benar" and str(x.get("soal_id")) not in chosen_ids
        ]
        for it in ragu_benar_items[:min(2, 8 - len(fokus_items))]:
            fokus_items.append(it)
            chosen_ids.add(str(it.get("soal_id")))

    # Bangun fokus_soal array
    fokus_soal = []
    for it in fokus_items:
        q_no = int(it.get("position") or 0)
        sid = str(it.get("soal_id") or f"Q-{q_no}")
        lbl = it.get("primary_label", "konsep")
        q_topik = str(it.get("topic_id") or "Matematika")
        kunci_ans = str(it.get("kunci") or (attempt.get("kunci") or {}).get(sid) or "A")
        first_ans = str(it.get("first_answer")) if it.get("first_answer") not in (None, "") else None
        final_ans = str(it.get("final_answer")) if it.get("final_answer") not in (None, "") else None
        is_corr = bool(it.get("is_correct"))
        w_detik = int(it.get("waktu_detik") if it.get("waktu_detik") is not None
                      else round((it.get("active_ms") or 0) / 1000))
        g_jawaban = int(it.get("ganti_jawaban") if it.get("ganti_jawaban") is not None
                        else it.get("change_count") or 0)
        is_ragu = bool(it.get("ragu") if it.get("ragu") is not None
                       else it.get("flagged_ragu"))

        # Jejak
        jejak = []
        raw_jejak = it.get("jejak") or []
        for ev in raw_jejak[:5]:
            if isinstance(ev, dict):
                jejak.append({
                    "t_detik": int(ev.get("t_detik") or 0),
                    "aksi": str(ev.get("aksi") or "pilih"),
                    "opsi": str(ev.get("opsi")) if ev.get("opsi") is not None else None,
                })

        # Ambil konten soal & pembahasan jika ada di content_map
        c_entry = content_map.get(sid) or content_map.get(q_no) or {}
        ringkas_soal = _clean_text_snippet(
            c_entry.get("ringkas_soal") or it.get("ringkas_soal") or it.get("pertanyaan") or
            f"Soal nomor {q_no} tentang materi {q_topik}.", max_len=240
        )
        pembahasan_ringkas = _clean_text_snippet(
            c_entry.get("pembahasan_ringkas") or it.get("pembahasan_ringkas") or it.get("pembahasan") or "",
            max_len=300
        )

        p_num = "5" if lbl in ("overthinking", "terburu") else ("1" if lbl in ("yakin_salah", "ragu_salah") else "2")
        pilar_refs = c_entry.get("pilar_refs") or it.get("pilar_refs") or [f"{sid}#{p_num}"]
        serupa_refs = c_entry.get("serupa_refs") or it.get("serupa_refs") or [f"{sid}-S1"]

        fokus_soal.append({
            "no": q_no,
            "soal_id": sid,
            "topik": q_topik,
            "label": lbl,
            "kunci": kunci_ans,
            "jawaban_awal": first_ans,
            "jawaban_akhir": final_ans,
            "benar": is_corr,
            "waktu_detik": w_detik,
            "jatah_detik": jatah_detik,
            "ganti_jawaban": g_jawaban,
            "ragu": is_ragu,
            "jejak": jejak,
            "ringkas_soal": ringkas_soal,
            "pembahasan_ringkas": pembahasan_ringkas,
            "pilar_refs": pilar_refs,
            "serupa_refs": serupa_refs,
        })

    # Penghitungan yang_bagus
    best_topic = None
    for t in topics:
        if t["n"] >= 2 and t["akurasi_pct"] >= 70:
            if best_topic is None or t["akurasi_pct"] > best_topic["akurasi_pct"]:
                best_topic = t
    if best_topic:
        yang_bagus = f"Akurasi {best_topic['akurasi_pct']}% pada topik {best_topic['topik']}."
    else:
        soal_benar = [x for x in labeled_items if x.get("is_correct")]
        if soal_benar:
            pos_benar = soal_benar[0].get("position", 1)
            yang_bagus = f"Menjawab tepat soal nomor {pos_benar} dengan baik."
        else:
            yang_bagus = "Menyelesaikan pengerjaan tryout untuk evaluasi komprehensif."

    # Kandidat tugas dari planner
    kandidat_tugas = []
    seen_ids = set()
    try:
        plan_res = planner.plan(today_iso, tka_date_iso, mapel, analysis, lib, exam_cfg)
        for d in plan_res.get("days", []):
            for t in d.get("tasks", []):
                tid = t.get("id")
                if tid and tid not in seen_ids:
                    seen_ids.add(tid)
                    kandidat_tugas.append({
                        "task_id": tid,
                        "judul": str(t.get("title") or t.get("judul") or "Latihan")[:60],
                        "menit": int(t.get("minutes") or t.get("menit") or 6),
                        "alasan": str(t.get("reason") or t.get("alasan") or "latihan")[:40],
                    })
                if len(kandidat_tugas) >= 5:
                    break
            if len(kandidat_tugas) >= 5:
                break
    except Exception:
        pass

    if not kandidat_tugas:
        kandidat_tugas = [
            {"task_id": "d1-pilar-auto", "judul": "Pilar 5: Trik & Jebakan", "menit": 6, "alasan": "terburu"},
            {"task_id": "d1-soal-auto", "judul": "3 soal serupa", "menit": 9, "alasan": "latihan"},
        ]

    return {
        "versi": "coach_input_v1",
        "mapel": mapel,
        "paket": paket,
        "skor_pct": skor_pct,
        "n_soal": n_q,
        "n_dijawab": n_answered,
        "n_benar": n_benar,
        "n_kosong": n_kosong,
        "durasi_batas_menit": durasi_batas_menit,
        "durasi_aktif_menit": durasi_aktif_menit,
        "ended_by": ended_by,
        "hari_menuju_ujian": hari_menuju_ujian,
        "data_tipis": bool(analysis.get("data_tipis", False)),
        "pola": pola,
        "kebocoran": kebocoran,
        "topik": topics,
        "fokus_soal": fokus_soal,
        "yang_bagus": yang_bagus,
        "kandidat_tugas": kandidat_tugas,
        "rencana_hari": None,
    }
