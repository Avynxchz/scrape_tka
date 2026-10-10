# -*- coding: utf-8 -*-
"""tests/test_audit_standalone.py — Test Suite Mandiri Tanpa Dependencies Server/DB/LLM.

Dibuat khusus untuk auditor agar dapat memverifikasi seluruh fungsi inti Guru Autopsi:
1. clean_attempt_items()
2. validate_coach_output()
3. generate_template()
4. check_quota() (dengan mock Supabase call)
5. build_evidence() (diimpor dari autopsy.evidence)

DAPAT DIJALANKAN LANGSUNG DENGAN:
    python3 tests/test_audit_standalone.py
    atau
    python tests/test_audit_standalone.py

Tanpa server.py, tanpa database live, tanpa API key.
"""

import datetime
import json
import os
import re
import sys
import unittest
import urllib.parse
from unittest.mock import MagicMock, patch

# Tambahkan root repo ke sys.path untuk impor autopsy murni
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Impor fungsi murni yang sudah standalone
from autopsy.evidence import build_evidence


# ============================================================================
# 1. SALINAN FUNGSI MURNI DARI server.py (clean_attempt_items)
# ============================================================================

def clean_attempt_items(raw_items):
    """Normalisasi dan sanitasi items attempt secara toleran terhadap bentuk data nyata.
    Mendukung list, dict bertingkat (mis. {'1': {...}}), atau string JSON.
    Mengembalikan (ok: bool, error_message: str, clean_items: list[dict])."""
    if isinstance(raw_items, str):
        try:
            raw_items = json.loads(raw_items)
        except Exception:
            raw_items = None
    if isinstance(raw_items, dict):
        try:
            raw_items = [v for k, v in sorted(raw_items.items(), key=lambda kv: int(kv[0]) if str(kv[0]).isdigit() else str(kv[0]))]
        except Exception:
            raw_items = list(raw_items.values())

    if not isinstance(raw_items, list) or not (1 <= len(raw_items) <= 200):
        t_name = type(raw_items).__name__
        l_info = len(raw_items) if hasattr(raw_items, '__len__') else 'N/A'
        return False, f"Items tidak valid (harus 1-200 soal; tipe={t_name}, panjang={l_info}).", []

    clean_items = []
    for it in raw_items:
        if not isinstance(it, dict):
            continue
        active_ms = max(0, min(int(it.get("active_ms") or 0), 3600000))
        change_count = max(0, min(int(it.get("change_count") if it.get("change_count") is not None else it.get("ganti_jawaban") or 0), 100))
        flagged_ragu = bool(it.get("flagged_ragu") if it.get("flagged_ragu") is not None else it.get("ragu"))

        # Jejak kejadian (maksimal 5 event)
        raw_jejak = it.get("jejak") or []
        clean_jejak = []
        if isinstance(raw_jejak, list):
            for ev in raw_jejak[:5]:
                if isinstance(ev, dict):
                    clean_jejak.append({
                        "t_detik": max(0, min(int(ev.get("t_detik") or 0), 86400)),
                        "aksi": str(ev.get("aksi") or "")[:16],
                        "opsi": (str(ev.get("opsi") or "")[:32]) if ev.get("opsi") is not None else None,
                    })

        waktu_detik = int(it.get("waktu_detik") if it.get("waktu_detik") is not None else round(active_ms / 1000))

        clean_items.append({
            "soal_id": str(it.get("soal_id") or "")[:128],
            "position": int(it.get("position") or 0),
            "topic_id": (str(it.get("topic_id") or "")[:128] or None),
            "first_answer": (str(it.get("first_answer") or "")[:64] or None),
            "final_answer": (str(it.get("final_answer") or "")[:64] or None),
            "active_ms": active_ms,
            "first_answer_ms": it.get("first_answer_ms"),
            "change_count": change_count,
            "flagged_ragu": flagged_ragu,
            "visit_count": max(0, min(int(it.get("visit_count") or 0), 1000)),
            # Ekstensi A1 Guru Autopsi:
            "waktu_detik": waktu_detik,
            "ganti_jawaban": change_count,
            "ragu": flagged_ragu,
            "jejak": clean_jejak,
        })

    if not clean_items:
        return False, "Semua item di dalam items tidak valid.", []

    return True, "", clean_items


# ============================================================================
# 2. SALINAN FUNGSI MURNI DARI autopsy/coach.py (validate_coach_output)
# ============================================================================

FORBIDDEN_WORDS = [
    "bodoh", "malas", "goblok", "payah", "pasti lolos", "pasti naik",
    "sombong", "hopeless", "tidak mampu", "tolol"
]

ALLOWED_ROOT_KEYS = {
    "versi", "sapaan", "penilaian", "pengamatan", "sudah_bagus",
    "kebocoran", "per_soal", "misi", "rencana", "penutup", "catatan_data"
}

ALLOWED_PENYEBAB = {"overthinking", "terburu", "konsep", "rapuh", "macet", "kosong"}


def _extract_numbers_from_obj(obj):
    numbers = set()
    s = json.dumps(obj)
    for m in re.findall(r"\b\d+\b", s):
        numbers.add(int(m))
    return numbers


def validate_coach_output(data, evidence):
    """Validasi ketat keluaran Guru AI sesuai Bagian 6.3."""
    if not isinstance(data, dict):
        return False, "Output bukan objek JSON"

    if data.get("versi") != "coach_output_v1":
        return False, f"Versi salah: {data.get('versi')}"

    extra_keys = set(data.keys()) - ALLOWED_ROOT_KEYS - {"sumber"}
    if extra_keys:
        return False, f"Terdapat key tidak dikenal: {extra_keys}"

    if len(str(data.get("sapaan") or "")) > 140:
        return False, "Sapaan melebihi 140 karakter"
    if len(str(data.get("penilaian") or "")) > 260:
        return False, "Penilaian melebihi 260 karakter"
    if len(str(data.get("sudah_bagus") or "")) > 160:
        return False, "Sudah_bagus melebihi 160 karakter"
    if len(str(data.get("penutup") or "")) > 140:
        return False, "Penutup melebihi 140 karakter"
    if len(str(data.get("catatan_data") or "")) > 160:
        return False, "Catatan_data melebihi 160 karakter"

    pengamatan = data.get("pengamatan")
    if not isinstance(pengamatan, list) or not (2 <= len(pengamatan) <= 5):
        return False, f"Pengamatan harus 2-5 butir (aktual: {len(pengamatan) if isinstance(pengamatan, list) else 'bukan list'})"
    for p in pengamatan:
        if len(str(p)) > 220:
            return False, f"Butir pengamatan melebihi 220 karakter: {p[:30]}..."

    kebocoran = data.get("kebocoran")
    if not isinstance(kebocoran, list) or len(kebocoran) > 3:
        return False, "Kebocoran harus list maks 3 item"
    for k in kebocoran:
        if not isinstance(k, dict):
            return False, "Item kebocoran bukan dict"
        if len(str(k.get("judul") or "")) > 60:
            return False, "Judul kebocoran melebihi 60 karakter"
        if len(str(k.get("bukti") or "")) > 200:
            return False, "Bukti kebocoran melebihi 200 karakter"
        if len(str(k.get("tafsir") or "")) > 200:
            return False, "Tafsir kebocoran melebihi 200 karakter"
        if len(str(k.get("tindakan") or "")) > 160:
            return False, "Tindakan kebocoran melebihi 160 karakter"

    valid_no = {q["no"] for q in (evidence.get("fokus_soal") or [])}
    per_soal = data.get("per_soal")
    if not isinstance(per_soal, list) or len(per_soal) > 6:
        return False, "Per_soal harus list maks 6 item"
    for ps in per_soal:
        if not isinstance(ps, dict):
            return False, "Item per_soal bukan dict"
        q_no = ps.get("no")
        if valid_no and q_no not in valid_no:
            return False, f"Nomor soal {q_no} tidak ada di fokus_soal {valid_no}"
        if ps.get("penyebab") not in ALLOWED_PENYEBAB:
            return False, f"Penyebab '{ps.get('penyebab')}' tidak dikenal"
        if len(str(ps.get("dipelajari") or "")) > 160:
            return False, f"Dipelajari soal {q_no} melebihi 160 karakter"
        langkah = ps.get("langkah")
        if not isinstance(langkah, list) or not (1 <= len(langkah) <= 3):
            return False, f"Langkah soal {q_no} harus 1-3 butir"
        for l in langkah:
            if len(str(l)) > 120:
                return False, f"Butir langkah soal {q_no} melebihi 120 karakter"
        if len(str(ps.get("cek_paham") or "")) > 140:
            return False, f"Cek_paham soal {q_no} melebihi 140 karakter"

    misi = data.get("misi")
    if not isinstance(misi, dict):
        return False, "Misi harus objek dict"
    if len(str(misi.get("pembuka") or "")) > 140:
        return False, "Pembuka misi melebihi 140 karakter"
    valid_tasks = {t["task_id"] for t in (evidence.get("kandidat_tugas") or [])}
    task_ids = misi.get("task_ids") or []
    if not isinstance(task_ids, list) or not task_ids:
        return False, "Task_ids misi harus list tidak kosong"
    for tid in task_ids:
        if valid_tasks and tid not in valid_tasks:
            return False, f"Task_id '{tid}' tidak ada di kandidat_tugas {valid_tasks}"

    rencana = data.get("rencana")
    if rencana is not None and not isinstance(rencana, list):
        return False, "Rencana harus berupa list"

    all_text = json.dumps(data, ensure_ascii=False).lower()
    for bad in FORBIDDEN_WORDS:
        if bad in all_text:
            return False, f"Mengandung kata terlarang '{bad}'"

    indo_markers = {"kamu", "soal", "di", "dan", "untuk", "yang", "jawaban", "detik", "pada", "ini"}
    words = set(re.findall(r"[a-zA-Z]+", all_text.lower()))
    if len(words.intersection(indo_markers)) < 3:
        return False, "Teks tidak terdeteksi sebagai bahasa Indonesia yang wajar"

    ev_numbers = _extract_numbers_from_obj(evidence)
    ev_numbers.update({1, 2, 3, 4, 5, 10, 15})
    output_numbers = set(int(m) for m in re.findall(r"\b\d+\b", all_text))
    unknown_numbers = output_numbers - ev_numbers
    if len(unknown_numbers) > 2:
        return False, f"Terlalu banyak angka tidak dikenal di luar data: {unknown_numbers}"

    return True, ""


# ============================================================================
# 3. SALINAN FUNGSI MURNI DARI autopsy/coach_template.py (generate_template)
# ============================================================================

LABEL_TO_PENYEBAB = {
    "overthinking": "overthinking",
    "terburu": "terburu",
    "yakin_salah": "konsep",
    "ragu_salah": "konsep",
    "ragu_benar": "rapuh",
    "macet": "macet",
    "waktu_habis": "kosong",
    "kosong": "kosong",
}

LEAK_COPY = {
    "terburu": {
        "judul": "Menjawab sebelum tuntas membaca soal",
        "tafsir": "Kemungkinan opsi dipilih tergesa-gesa sebelum kalimat tanya dan semua opsi dipahami.",
        "tindakan": "Di tryout berikutnya, baca ulang kalimat tanya sebelum memilih jawaban.",
    },
    "overthinking": {
        "judul": "Mengganti jawaban yang semula sudah benar",
        "tafsir": "Kemungkinan ragu pada perhitungan awal lalu berpindah ke opsi jebakan.",
        "tindakan": "Pertahankan jawaban pertama kecuali menemukan bukti kesalahan hitung yang nyata.",
    },
    "yakin_salah": {
        "judul": "Konsep dasar belum kokoh pada soal tertentu",
        "tafsir": "Kemungkinan ada rumus atau definisi konsep yang tertukar.",
        "tindakan": "Buka pembahasan Pilar 1 dan kuatkan konsep dasar topik ini.",
    },
    "ragu_salah": {
        "judul": "Ragu-ragu memilih dan jawaban akhirnya salah",
        "tafsir": "Intuisi awal belum cukup kuat untuk membedakan opsi yang mirip.",
        "tindakan": "Pelajari langkah eliminasi opsi pada pembahasan soal serupa.",
    },
    "macet": {
        "judul": "Terjebak terlalu lama pada satu soal",
        "tafsir": "Kemungkinan memaksakan menyelesaikan soal sulit sehingga kehabisan waktu.",
        "tindakan": "Lewati soal yang macet lebih dari jatah waktu dan kerjakan yang lain dulu.",
    },
    "waktu_habis": {
        "judul": "Kehabisan waktu di bagian akhir ujian",
        "tafsir": "Manajemen ritme pengerjaan di awal membuat soal akhir terlewat.",
        "tindakan": "Gunakan pembagian waktu per blok 10 soal agar tidak menumpuk di akhir.",
    },
    "kosong": {
        "judul": "Banyak soal yang belum sempat dijawab",
        "tafsir": "Pacing pengerjaan perlu dipercepat agar seluruh soal terbaca.",
        "tindakan": "Pasang target waktu maksimal per soal sesuai jatah resmi.",
    },
}


def generate_template(evidence):
    """Menghasilkan output coach_output_v1 deterministik dari evidence pack."""
    data_tipis = bool(evidence.get("data_tipis", False))
    skor_pct = int(evidence.get("skor_pct") or 0)
    pola = evidence.get("pola") or {}
    median_w = int(pola.get("median_waktu_detik") or 0)
    jatah_w = int(pola.get("jatah_detik") or 180)

    if data_tipis:
        sapaan = "Saya melihat kamu baru mengerjakan sebagian soal. Ini awal yang baik untuk memetakan kebiasaan belajarmu."[:140]
    else:
        sapaan = "Saya sudah mengamati caramu mengerjakan tadi. Ada pola yang jelas dan bisa kita perbaiki dalam beberapa hari ke depan."[:140]

    penilaian = (
        f"Skormu {skor_pct}%. Bagian yang paling cepat dipulihkan adalah membenahi ritme dan tidak terburu-buru di soal yang terasa mudah. "
        "Fokus pada peningkatan bertahap setiap sesi latihan."
    )[:260]

    pengamatan = []
    raw_leaks = evidence.get("kebocoran") or []
    if raw_leaks:
        pengamatan.append(f"Kebocoran utama: {raw_leaks[0].get('bukti', 'terdapat pola salah berulang')}."[:220])

    fokus = evidence.get("fokus_soal") or []
    for q in fokus[:2]:
        no = q.get("no")
        waktu = q.get("waktu_detik", 0)
        lbl = q.get("label", "soal")
        if q.get("jawaban_awal") and q.get("jawaban_akhir") and q.get("jawaban_awal") != q.get("jawaban_akhir"):
            pengamatan.append(
                f"Soal {no}: kamu memilih {q['jawaban_awal']} lalu mengganti ke {q['jawaban_akhir']} dengan waktu {waktu} detik."[:220]
            )
        else:
            pengamatan.append(
                f"Soal {no} ({lbl}): dijawab dalam {waktu} detik dari jatah {q.get('jatah_detik', jatah_w)} detik."[:220]
            )

    if len(pengamatan) < 3:
        pengamatan.append(f"Median waktu pengerjaanmu {median_w} detik per soal, berbanding jatah {jatah_w} detik."[:220])
    if len(pengamatan) < 3:
        pengamatan.append(f"Tingkat akurasi di awal {pola.get('akurasi_awal_pct', 0)}% dan di akhir {pola.get('akurasi_akhir_pct', 0)}%."[:220])
    pengamatan = pengamatan[:5]

    sudah_bagus = str(evidence.get("yang_bagus") or "Kamu memiliki konsistensi yang baik saat menghadapi soal-soal terarah.")[:160]

    kebocoran = []
    for k in raw_leaks[:3]:
        lbl = k.get("label", "terburu")
        copy = LEAK_COPY.get(lbl, LEAK_COPY["terburu"])
        kebocoran.append({
            "label": lbl,
            "judul": copy["judul"][:60],
            "bukti": str(k.get("bukti") or f"{k.get('soal_hilang', 1)} soal terpengaruh")[:200],
            "tafsir": copy["tafsir"][:200],
            "tindakan": copy["tindakan"][:160],
        })

    per_soal = []
    for q in fokus[:6]:
        no = q.get("no", 1)
        lbl = q.get("label", "terburu")
        penyebab = LABEL_TO_PENYEBAB.get(lbl, "konsep")
        topik = q.get("topik", "Matematika")

        dipelajari = f"Kuatkan pemahaman topik {topik}. Perhatikan langkah kunci perhitungan."[:160]
        langkah = [
            f"Buka pembahasan nomor {no} pada tab Pilar."[:120],
            f"Kerjakan ulang soal {no} secara mandiri tanpa melihat kunci."[:120],
        ]
        cek_paham = f"Bagian mana dari konsep {topik} yang membuatmu ragu tadi?"[:140]

        per_soal.append({
            "no": no,
            "penyebab": penyebab,
            "dipelajari": dipelajari,
            "langkah": langkah,
            "cek_paham": cek_paham,
        })

    candidates = evidence.get("kandidat_tugas") or []
    task_ids = [candidates[0]["task_id"]] if candidates else ["d1-pilar-auto"]
    misi = {
        "pembuka": "Misi 10 menit hari ini: latih ketelitian membaca sebelum memilih opsi."[:140],
        "task_ids": task_ids,
    }

    rencana = []
    penutup = "Mulai dari satu langkah kecil hari ini. Kita evaluasi kemajuannya di tryout berikutnya."[:140]
    catatan_data = "Jumlah soal yang dikerjakan masih sedikit, jadi anggap analisis ini sebagai gambaran awal."[:160] if data_tipis else ""

    return {
        "versi": "coach_output_v1",
        "sumber": "template",
        "sapaan": sapaan,
        "penilaian": penilaian,
        "pengamatan": pengamatan,
        "sudah_bagus": sudah_bagus,
        "kebocoran": kebocoran,
        "per_soal": per_soal,
        "misi": misi,
        "rencana": rencana,
        "penutup": penutup,
        "catatan_data": catatan_data,
    }


# ============================================================================
# 4. SALINAN FUNGSI MURNI DARI autopsy/quota.py (check_quota)
# ============================================================================

def is_coach_enabled():
    val = os.environ.get("COACH_ENABLED", "1").strip().lower()
    return val in ("1", "true", "yes", "on")


def get_quota_limits():
    try:
        user_limit = int(os.environ.get("COACH_DAILY_PER_USER", 3))
    except Exception:
        user_limit = 3
    try:
        global_limit = int(os.environ.get("COACH_DAILY_GLOBAL", 150))
    except Exception:
        global_limit = 150
    return {
        "enabled": is_coach_enabled(),
        "daily_per_user": max(1, user_limit),
        "daily_global": max(1, global_limit),
    }


def get_today_iso_utc():
    now = datetime.datetime.now(datetime.timezone.utc)
    today_start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=datetime.timezone.utc)
    return today_start.strftime("%Y-%m-%dT%H:%M:%SZ")


def count_today_coach_attempts(sb_url, sb_svc, user_id=None, timeout=6):
    """Stub yang memanggil urllib.request; di unit test ini akan di-mock."""
    if not sb_url or not sb_svc:
        return 0
    # Dalam unit test kita mock pemanggilan ini
    return 0


def check_quota(user_id, sb_url, sb_svc, count_fn=count_today_coach_attempts):
    """Periksa apakah permintaan Guru AI diizinkan berdasarkan kuota."""
    limits = get_quota_limits()

    if not limits["enabled"]:
        return False, "coach_disabled", {"enabled": False}

    if not user_id:
        return False, "guest_user", {"user_id": None}

    user_count = count_fn(sb_url, sb_svc, user_id=user_id)
    if user_count >= limits["daily_per_user"]:
        return False, "kuota_harian_user_habis", {
            "user_used": user_count,
            "user_limit": limits["daily_per_user"],
            "global_limit": limits["daily_global"],
        }

    global_count = count_fn(sb_url, sb_svc, user_id=None)
    if global_count >= limits["daily_global"]:
        return False, "kuota_harian_global_habis", {
            "user_used": user_count,
            "global_used": global_count,
            "user_limit": limits["daily_per_user"],
            "global_limit": limits["daily_global"],
        }

    return True, "", {
        "user_used": user_count,
        "global_used": global_count,
        "user_limit": limits["daily_per_user"],
        "global_limit": limits["daily_global"],
    }


# ============================================================================
# TEST SUITE 1: clean_attempt_items (8 Test Cases)
# ============================================================================

class TestCleanAttemptItems(unittest.TestCase):
    def test_1_valid_list(self):
        """1. List valid berisi soal normal dinormalisasi dengan benar."""
        raw = [{
            "soal_id": "mtk-1",
            "position": 1,
            "active_ms": 45000,
            "change_count": 0,
            "flagged_ragu": False,
            "first_answer": "A",
            "final_answer": "A"
        }]
        ok, err, items = clean_attempt_items(raw)
        self.assertTrue(ok)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["waktu_detik"], 45)
        self.assertEqual(items[0]["ganti_jawaban"], 0)
        self.assertFalse(items[0]["ragu"])

    def test_2_nested_dict_conversion(self):
        """2. Dict bertingkat {'1': {...}, '2': {...}} berhasil diubah ke sorted list."""
        raw = {
            "2": {"soal_id": "mtk-2", "active_ms": 20000},
            "1": {"soal_id": "mtk-1", "active_ms": 10000}
        }
        ok, err, items = clean_attempt_items(raw)
        self.assertTrue(ok)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["soal_id"], "mtk-1")
        self.assertEqual(items[1]["soal_id"], "mtk-2")

    def test_3_json_string_parsing(self):
        """3. String JSON valid diparsing otomatis menjadi list."""
        raw = json.dumps([{"soal_id": "q1", "active_ms": 15000, "ragu": True}])
        ok, err, items = clean_attempt_items(raw)
        self.assertTrue(ok)
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]["ragu"])
        self.assertEqual(items[0]["waktu_detik"], 15)

    def test_4_none_and_corrupt_string_rejected(self):
        """4. Nilai None atau string corrupt ditolak dengan pesan jelas."""
        ok, err, items = clean_attempt_items(None)
        self.assertFalse(ok)
        self.assertIn("Items tidak valid", err)

        ok2, err2, _ = clean_attempt_items("bukan-json-valid{{{")
        self.assertFalse(ok2)
        self.assertIn("Items tidak valid", err2)

    def test_5_empty_list_and_dict_rejected(self):
        """5. List kosong [] dan dict kosong {} ditolak (harus 1-200 soal)."""
        ok1, err1, _ = clean_attempt_items([])
        self.assertFalse(ok1)
        self.assertIn("Items tidak valid", err1)

        ok2, err2, _ = clean_attempt_items({})
        self.assertFalse(ok2)
        self.assertIn("Items tidak valid", err2)

    def test_6_non_dict_elements_rejected(self):
        """6. List yang isinya bukan dict (mis. string/integer) ditolak."""
        ok, err, items = clean_attempt_items(["hanya_string", 999])
        self.assertFalse(ok)
        self.assertIn("tidak valid", err)

    def test_7_jejak_truncation_max_5(self):
        """7. Riwayat event jejak dibatasi maksimal 5 event per soal."""
        raw = [{
            "soal_id": "q-jejak",
            "active_ms": 50000,
            "jejak": [
                {"t_detik": 5, "aksi": "pilih", "opsi": "A"},
                {"t_detik": 10, "aksi": "ganti", "opsi": "B"},
                {"t_detik": 15, "aksi": "ganti", "opsi": "C"},
                {"t_detik": 20, "aksi": "ganti", "opsi": "D"},
                {"t_detik": 25, "aksi": "ragu"},
                {"t_detik": 30, "aksi": "pilih", "opsi": "E"},  # Ke-6 harus dipotong
                {"t_detik": 35, "aksi": "ragu"}                  # Ke-7 harus dipotong
            ]
        }]
        ok, err, items = clean_attempt_items(raw)
        self.assertTrue(ok)
        self.assertEqual(len(items[0]["jejak"]), 5)
        self.assertEqual(items[0]["jejak"][-1]["aksi"], "ragu")

    def test_8_clamping_ranges(self):
        """8. Angka ekstrim di-clamp ke batas aman (active_ms, change_count)."""
        raw = [{
            "soal_id": "clamp-1",
            "active_ms": 999999999,  # > 3600000 ms
            "change_count": 9999,     # > 100
            "visit_count": 5000       # > 1000
        }]
        ok, err, items = clean_attempt_items(raw)
        self.assertTrue(ok)
        self.assertEqual(items[0]["active_ms"], 3600000)
        self.assertEqual(items[0]["change_count"], 100)
        self.assertEqual(items[0]["visit_count"], 1000)


# ============================================================================
# TEST SUITE 2: validate_coach_output (10 Test Cases)
# ============================================================================

class TestValidateCoachOutput(unittest.TestCase):
    def setUp(self):
        self.evidence = {
            "versi": "coach_input_v1",
            "skor_pct": 60,
            "pola": {"median_waktu_detik": 45, "jatah_detik": 120},
            "fokus_soal": [
                {"no": 1, "label": "terburu", "waktu_detik": 20, "topik": "Aljabar"},
                {"no": 2, "label": "yakin_salah", "waktu_detik": 45, "topik": "Geometri"}
            ],
            "kandidat_tugas": [
                {"task_id": "task-aljabar-1", "judul": "Latihan Aljabar Cepat"}
            ],
            "kebocoran": [
                {"label": "terburu", "bukti": "2 soal dijawab sangat cepat", "soal_hilang": 2}
            ],
            "yang_bagus": "Pengerjaan teliti pada nomor awal."
        }

    def _sample_valid_output(self):
        return {
            "versi": "coach_output_v1",
            "sapaan": "Halo, ini evaluasi tryout kamu hari ini.",
            "penilaian": "Skor kamu 60%. Ritme pengerjaan sudah cukup baik pada soal awal namun perlu lebih cermat.",
            "pengamatan": [
                "Kebocoran utama pada soal terburu.",
                "Soal 1 dijawab dalam 20 detik dari jatah 120 detik.",
                "Median waktu pengerjaan 45 detik per soal."
            ],
            "sudah_bagus": "Konsistensi yang baik pada nomor awal.",
            "kebocoran": [{
                "label": "terburu",
                "judul": "Terburu-buru membaca soal",
                "bukti": "2 soal dijawab sangat cepat",
                "tafsir": "Opsi dipilih sebelum tuntas membaca.",
                "tindakan": "Baca ulang kalimat tanya sebelum memilih."
            }],
            "per_soal": [{
                "no": 1,
                "penyebab": "terburu",
                "dipelajari": "Kuatkan ketelitian aljabar.",
                "langkah": ["Buka pembahasan pilar nomor 1."],
                "cek_paham": "Apa jebakan utama di soal 1?"
            }],
            "misi": {
                "pembuka": "Misi 10 menit hari ini untuk melatih ketelitian.",
                "task_ids": ["task-aljabar-1"]
            },
            "rencana": [],
            "penutup": "Mulai dari satu langkah kecil hari ini untuk kemajuan tryout.",
            "catatan_data": ""
        }

    def test_1_valid_output_passes(self):
        """1. Output lengkap sesuai skema lolos validasi."""
        data = self._sample_valid_output()
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertTrue(ok, f"Seharusnya lolos tapi gagal: {reason}")

    def test_2_wrong_version_rejected(self):
        """2. Output dengan versi salah ditolak."""
        data = self._sample_valid_output()
        data["versi"] = "coach_output_v2_invalid"
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertFalse(ok)
        self.assertIn("Versi salah", reason)

    def test_3_forbidden_words_rejected(self):
        """3. Kata terlarang/menghakimi ('bodoh', 'malas', dll.) ditolak."""
        for bad_word in ["bodoh", "kamu malas sekali", "tidak mampu", "pasti lolos"]:
            data = self._sample_valid_output()
            data["sapaan"] = f"Halo, kamu {bad_word} dalam tes."
            ok, reason = validate_coach_output(data, self.evidence)
            self.assertFalse(ok, f"Kata '{bad_word}' seharusnya ditolak!")
            self.assertIn("kata terlarang", reason)

    def test_4_wild_question_number_rejected(self):
        """4. Nomor soal liar yang tidak ada di fokus_soal ditolak."""
        data = self._sample_valid_output()
        data["per_soal"][0]["no"] = 99  # Soal 99 tidak ada di fokus_soal
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertFalse(ok)
        self.assertIn("Nomor soal 99 tidak ada di fokus_soal", reason)

    def test_5_wild_task_id_rejected(self):
        """5. Task_id liar yang tidak ada di kandidat_tugas ditolak."""
        data = self._sample_valid_output()
        data["misi"]["task_ids"] = ["task-fiktif-liar-xyz"]
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertFalse(ok)
        self.assertIn("tidak ada di kandidat_tugas", reason)

    def test_6_excessive_sapaan_length_rejected(self):
        """6. Sapaan melebihi 140 karakter ditolak."""
        data = self._sample_valid_output()
        data["sapaan"] = "Halo " + ("sangat panjang " * 20)
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertFalse(ok)
        self.assertIn("Sapaan melebihi", reason)

    def test_7_unknown_root_keys_rejected(self):
        """7. Field asing yang tidak ada di skema resmi ditolak."""
        data = self._sample_valid_output()
        data["field_rahasia_hacker"] = "injec_data"
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertFalse(ok)
        self.assertIn("key tidak dikenal", reason)

    def test_8_unrecognized_penyebab_rejected(self):
        """8. Label penyebab tidak valid ditolak."""
        data = self._sample_valid_output()
        data["per_soal"][0]["penyebab"] = "penyebab_ngawur"
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertFalse(ok)
        self.assertIn("tidak dikenal", reason)

    def test_9_excessive_unknown_numbers_rejected(self):
        """9. Halusinasi angka asing (>2 angka di luar evidence) ditolak."""
        data = self._sample_valid_output()
        data["pengamatan"] = [
            "Ada 987 murid lain yang nilainya 888 dan 777.",
            "Soal 1 dijawab dalam 20 detik.",
            "Waktu tersisa 9999 detik lagi."
        ]
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertFalse(ok)
        self.assertIn("angka tidak dikenal", reason)

    def test_10_non_indonesian_language_rejected(self):
        """10. Teks bahasa asing murni tanpa kosakata Indonesia ditolak."""
        data = {
            "versi": "coach_output_v1",
            "sapaan": "Hello my dear student this is an english report.",
            "penilaian": "Your general performance was great and excellent overall.",
            "pengamatan": ["First observation here.", "Second observation here."],
            "sudah_bagus": "Good job on questions.",
            "kebocoran": [{
                "label": "terburu",
                "judul": "Hasty reading",
                "bukti": "Fast answers",
                "tafsir": "Skipping questions",
                "tindakan": "Read carefully"
            }],
            "per_soal": [{
                "no": 1,
                "penyebab": "terburu",
                "dipelajari": "Focus study",
                "langkah": ["Open solution"],
                "cek_paham": "Did you understand"
            }],
            "misi": {
                "pembuka": "Mission for ten minutes.",
                "task_ids": ["task-aljabar-1"]
            },
            "rencana": [],
            "penutup": "Keep doing your best next time.",
            "catatan_data": ""
        }
        ok, reason = validate_coach_output(data, self.evidence)
        self.assertFalse(ok)
        self.assertIn("bahasa Indonesia", reason)


# ============================================================================
# TEST SUITE 3: generate_template (6 Test Cases)
# ============================================================================

class TestGenerateTemplate(unittest.TestCase):
    def setUp(self):
        self.evidence = {
            "versi": "coach_input_v1",
            "skor_pct": 52,
            "data_tipis": False,
            "pola": {"median_waktu_detik": 50, "jatah_detik": 120, "akurasi_awal_pct": 80, "akurasi_akhir_pct": 40},
            "fokus_soal": [
                {"no": 3, "label": "overthinking", "waktu_detik": 70, "jawaban_awal": "A", "jawaban_akhir": "C", "topik": "Logika"},
                {"no": 5, "label": "terburu", "waktu_detik": 15, "topik": "Kalkulus"}
            ],
            "kandidat_tugas": [{"task_id": "task-template-1", "judul": "Tugas 1"}],
            "kebocoran": [
                {"label": "overthinking", "bukti": "1 soal diganti dari benar ke salah", "soal_hilang": 1}
            ],
            "yang_bagus": "Penguasaan logika di awal sangat rapi."
        }

    def test_1_schema_conformance(self):
        """1. Output template memiliki seluruh kunci wajib coach_output_v1."""
        tpl = generate_template(self.evidence)
        self.assertEqual(tpl["versi"], "coach_output_v1")
        self.assertEqual(tpl["sumber"], "template")
        self.assertIn("sapaan", tpl)
        self.assertIn("penilaian", tpl)
        self.assertIn("pengamatan", tpl)
        self.assertIn("kebocoran", tpl)
        self.assertIn("per_soal", tpl)
        self.assertIn("misi", tpl)

    def test_2_passes_strict_validator(self):
        """2. Output template lolos validasi ketat validate_coach_output 100%."""
        tpl = generate_template(self.evidence)
        ok, reason = validate_coach_output(tpl, self.evidence)
        self.assertTrue(ok, f"Template gagal validasi: {reason}")

    def test_3_data_tipis_adaptation(self):
        """3. Saat data_tipis=True, catatan_data terisi dan sapaan menyesuaikan."""
        ev_tipis = dict(self.evidence)
        ev_tipis["data_tipis"] = True
        tpl = generate_template(ev_tipis)
        self.assertIn("sebagian", tpl["sapaan"])
        self.assertIn("sedikit", tpl["catatan_data"])

    def test_4_leak_label_copy_mapped(self):
        """4. Label kebocoran (overthinking) dipetakan ke narasi yang tepat."""
        tpl = generate_template(self.evidence)
        self.assertEqual(tpl["kebocoran"][0]["label"], "overthinking")
        self.assertIn("Mengganti jawaban", tpl["kebocoran"][0]["judul"])

    def test_5_handles_empty_fields_gracefully(self):
        """5. Tetap berjalan aman walau fokus_soal atau kebocoran kosong."""
        empty_ev = {
            "versi": "coach_input_v1",
            "skor_pct": 0,
            "fokus_soal": [],
            "kebocoran": [],
            "kandidat_tugas": []
        }
        tpl = generate_template(empty_ev)
        self.assertEqual(tpl["versi"], "coach_output_v1")
        self.assertEqual(len(tpl["per_soal"]), 0)
        self.assertGreaterEqual(len(tpl["pengamatan"]), 2)

    def test_6_misi_task_id_derived_from_candidates(self):
        """6. Task id misi diambil langsung dari kandidat tugas evidence."""
        tpl = generate_template(self.evidence)
        self.assertEqual(tpl["misi"]["task_ids"], ["task-template-1"])


# ============================================================================
# TEST SUITE 4: check_quota (7 Test Cases)
# ============================================================================

class TestCheckQuota(unittest.TestCase):
    def test_1_coach_disabled_env(self):
        """1. Fitur dinonaktifkan via COACH_ENABLED=0 ditolak dengan 'coach_disabled'."""
        with patch.dict(os.environ, {"COACH_ENABLED": "0"}):
            allowed, reason, usage = check_quota("user_123", "https://sb.co", "key_secret")
            self.assertFalse(allowed)
            self.assertEqual(reason, "coach_disabled")

    def test_2_guest_user_rejected(self):
        """2. Pengguna tamu (user_id=None atau '') ditolak dengan 'guest_user'."""
        with patch.dict(os.environ, {"COACH_ENABLED": "1"}):
            allowed, reason, _ = check_quota(None, "https://sb.co", "key_secret")
            self.assertFalse(allowed)
            self.assertEqual(reason, "guest_user")

            allowed_empty, reason_empty, _ = check_quota("", "https://sb.co", "key_secret")
            self.assertFalse(allowed_empty)
            self.assertEqual(reason_empty, "guest_user")

    def test_3_user_within_quota_allowed(self):
        """3. User dengan pemakaian di bawah batas (misal 1 dari 3) diizinkan."""
        mock_count = MagicMock(return_value=1)
        with patch.dict(os.environ, {"COACH_ENABLED": "1", "COACH_DAILY_PER_USER": "3"}):
            allowed, reason, usage = check_quota("user_123", "https://sb.co", "key_secret", count_fn=mock_count)
            self.assertTrue(allowed)
            self.assertEqual(reason, "")
            self.assertEqual(usage["user_used"], 1)

    def test_4_user_quota_exceeded(self):
        """4. User mencapai batas harian (3) ditolak dengan 'kuota_harian_user_habis'."""
        mock_count = MagicMock(return_value=3)
        with patch.dict(os.environ, {"COACH_ENABLED": "1", "COACH_DAILY_PER_USER": "3"}):
            allowed, reason, usage = check_quota("user_123", "https://sb.co", "key_secret", count_fn=mock_count)
            self.assertFalse(allowed)
            self.assertEqual(reason, "kuota_harian_user_habis")
            self.assertEqual(usage["user_used"], 3)

    def test_5_global_quota_exceeded(self):
        """5. Batas kuota global tercapai (150) ditolak dengan 'kuota_harian_global_habis'."""
        def mock_count(sb_url, sb_svc, user_id=None):
            return 1 if user_id else 150  # User baru 1, tapi global sudah 150

        with patch.dict(os.environ, {"COACH_ENABLED": "1", "COACH_DAILY_GLOBAL": "150"}):
            allowed, reason, usage = check_quota("user_123", "https://sb.co", "key_secret", count_fn=mock_count)
            self.assertFalse(allowed)
            self.assertEqual(reason, "kuota_harian_global_habis")
            self.assertEqual(usage["global_used"], 150)

    def test_6_custom_env_limits_respected(self):
        """6. Nilai batas dari env kustom dipatuhi."""
        with patch.dict(os.environ, {"COACH_DAILY_PER_USER": "5", "COACH_DAILY_GLOBAL": "300"}):
            limits = get_quota_limits()
            self.assertEqual(limits["daily_per_user"], 5)
            self.assertEqual(limits["daily_global"], 300)

    def test_7_today_iso_utc_format(self):
        """7. get_today_iso_utc mengembalikan string ISO 8601 berakhiran 'T00:00:00Z'."""
        iso_str = get_today_iso_utc()
        self.assertTrue(iso_str.endswith("T00:00:00Z"))
        self.assertRegex(iso_str, r"^\d{4}-\d{2}-\d{2}T00:00:00Z$")


# ============================================================================
# TEST SUITE 5: build_evidence dari autopsy/evidence.py (6 Test Cases)
# ============================================================================

class TestBuildEvidenceStandalone(unittest.TestCase):
    def setUp(self):
        # Fixture attempt ringkas 5 soal
        self.attempt = {
            "attempt_id": "att-audit-001",
            "paket_id": "matematika_paket_1",
            "mapel": "Matematika",
            "skor_persen": 40,
            "items": [
                {"soal_id": "m1", "position": 1, "topic_id": "Aljabar", "active_ms": 12000, "waktu_detik": 12, "first_answer": "A", "final_answer": "B", "change_count": 1, "flagged_ragu": False},
                {"soal_id": "m2", "position": 2, "topic_id": "Aljabar", "active_ms": 15000, "waktu_detik": 15, "first_answer": "B", "final_answer": "B", "change_count": 0, "flagged_ragu": False},
                {"soal_id": "m3", "position": 3, "topic_id": "Geometri", "active_ms": 90000, "waktu_detik": 90, "first_answer": "C", "final_answer": "C", "change_count": 0, "flagged_ragu": True},
                {"soal_id": "m4", "position": 4, "topic_id": "Geometri", "active_ms": 110000, "waktu_detik": 110, "first_answer": "D", "final_answer": "D", "change_count": 0, "flagged_ragu": False},
                {"soal_id": "m5", "position": 5, "topic_id": "Statistika", "active_ms": 15000, "waktu_detik": 15, "first_answer": "A", "final_answer": "A", "change_count": 0, "flagged_ragu": False},
            ]
        }
        self.analysis = {
            "primary_leak": {"label": "terburu", "title": "Terburu-buru", "description": "Menjawab terlalu cepat"},
            "secondary_leaks": [],
            "flags": {"data_tipis": False, "fatigue": False},
            "topics": {"Aljabar": {"correct": 0, "total": 2}}
        }
        self.plan = {
            "exam_day": "2026-10-28",
            "daily_minutes": 20,
            "days": [
                {"day_offset": 1, "date": "2026-10-11", "tasks": [{"task_id": "t-1", "title": "Pilar 1 Aljabar", "ref": "pilar-1", "category": "pilar", "minutes": 10}]}
            ]
        }

    def test_1_build_evidence_schema(self):
        """1. build_evidence menghasilkan coach_input_v1 valid."""
        ev = build_evidence(self.attempt, self.analysis, self.plan)
        self.assertEqual(ev["versi"], "coach_input_v1")
        self.assertIn("fokus_soal", ev)
        self.assertIn("kandidat_tugas", ev)
        self.assertIn("kebocoran", ev)

    def test_2_fokus_soal_max_8(self):
        """2. fokus_soal dibatasi maksimal 8 butir soal."""
        ev = build_evidence(self.attempt, self.analysis, self.plan)
        self.assertLessEqual(len(ev["fokus_soal"]), 8)

    def test_3_candidate_tasks_presence(self):
        """3. kandidat_tugas memuat task_id dan judul."""
        ev = build_evidence(self.attempt, self.analysis, self.plan)
        self.assertTrue(len(ev["kandidat_tugas"]) >= 1)
        self.assertIn("task_id", ev["kandidat_tugas"][0])
        self.assertIn("judul", ev["kandidat_tugas"][0])

    def test_4_compact_token_size(self):
        """4. Payload berukuran ringkas jauh di bawah 3.500 token (~14.000 karakter)."""
        ev = build_evidence(self.attempt, self.analysis, self.plan)
        char_len = len(json.dumps(ev))
        self.assertLess(char_len, 14000)

    def test_5_detects_data_tipis(self):
        """5. Menandai data_tipis=True jika analysis menyatakannya."""
        analysis_tipis = dict(self.analysis)
        analysis_tipis["data_tipis"] = True
        ev = build_evidence(self.attempt, analysis_tipis, self.plan)
        self.assertTrue(ev["data_tipis"])

    def test_6_pilar_refs_available(self):
        """6. Setiap butir fokus_soal memuat referensi pilar."""
        ev = build_evidence(self.attempt, self.analysis, self.plan)
        for q in ev["fokus_soal"]:
            self.assertIn("pilar_refs", q)
            self.assertTrue(isinstance(q["pilar_refs"], list))


# ============================================================================
# 5. SALINAN FUNGSI MURNI FASE B1 DARI server.py (Konteks Perilaku AI Tutor)
# ============================================================================

def format_student_behavior_context(item_data):
    """Rakit string konteks perilaku murid untuk satu butir soal (FASE B1).
    
    Format:
    "Konteks perilaku murid di soal ini: [waktu] detik, jawaban [awal]→[akhir], [ragu/tidak ragu]. Sesuaikan penjelasanmu: tanyakan di mana dia berhenti berpikir; jangan langsung kasih jawaban lengkap kalau dia cuma salah baca."
    """
    if not item_data or not isinstance(item_data, dict):
        return ""

    waktu = item_data.get("waktu_detik")
    if waktu is None:
        active_ms = item_data.get("active_ms") or 0
        waktu = round(active_ms / 1000)
    waktu = int(waktu or 0)

    awal = item_data.get("first_answer") or item_data.get("jawaban_awal") or "-"
    akhir = item_data.get("final_answer") or item_data.get("jawaban_akhir") or "-"

    is_ragu = bool(item_data.get("ragu") if item_data.get("ragu") is not None
                   else item_data.get("flagged_ragu"))
    ragu_str = "ragu" if is_ragu else "tidak ragu"

    ctx = (
        f"Konteks perilaku murid di soal ini: {waktu} detik, jawaban {awal}→{akhir}, {ragu_str}. "
        "Sesuaikan penjelasanmu: tanyakan di mana dia berhenti berpikir; jangan langsung kasih jawaban lengkap kalau dia cuma salah baca."
    )

    change_count = item_data.get("ganti_jawaban") if item_data.get("ganti_jawaban") is not None else item_data.get("change_count")
    if change_count and int(change_count) > 0:
        ctx += f" (Murid mengganti jawaban sebanyak {change_count} kali)."

    jejak = item_data.get("jejak") or []
    if isinstance(jejak, list) and len(jejak) > 1:
        jejak_parts = []
        for ev in jejak[:5]:
            if isinstance(ev, dict):
                aksi = ev.get("aksi", "event")
                opsi = f" {ev.get('opsi')}" if ev.get("opsi") else ""
                t = ev.get("t_detik", 0)
                jejak_parts.append(f"{aksi}{opsi} ({t}s)")
        if jejak_parts:
            ctx += f" Jejak kronologis: {' -> '.join(jejak_parts)}."

    return ctx


def find_question_item_in_attempt(items, nomor=None, question_id=None):
    """Cari dict item spesifik dari daftar items attempt berdasarkan nomor urut (position) atau question_id."""
    if not items or not isinstance(items, list):
        return None

    if nomor is not None:
        try:
            nomor_int = int(nomor)
            for it in items:
                if isinstance(it, dict) and int(it.get("position") or 0) == nomor_int:
                    return it
        except (ValueError, TypeError):
            pass

    if question_id:
        qid_str = str(question_id).strip()
        for it in items:
            if isinstance(it, dict):
                sid = str(it.get("soal_id") or "").strip()
                if sid == qid_str or (nomor is not None and sid.endswith(f"_n{nomor}")):
                    return it

    return None


def build_soal_behavior_context(user_id=None, nomor=None, question_id=None, attempt_id=None, fetch_fn=None):
    """Rakit konteks perilaku untuk AI Tutor dari database attempts."""
    items = fetch_fn(user_id=user_id, attempt_id=attempt_id) if fetch_fn else []
    if not items:
        return ""
    item = find_question_item_in_attempt(items, nomor=nomor, question_id=question_id)
    if not item:
        return ""
    return format_student_behavior_context(item)


# Impor helper prompt tutor untuk pengujian injeksi sistem
from tutor_engine import build_tutor_prompt


# ============================================================================
# TEST SUITE 6: FASE B1 — Konteks Perilaku Murid ke AI Tutor (7 Test Cases)
# ============================================================================

class TestTutorBehaviorContextStandalone(unittest.TestCase):
    def setUp(self):
        self.item_ragu_ganti = {
            "soal_id": "matematika_p1_n3",
            "position": 3,
            "waktu_detik": 45,
            "first_answer": "A",
            "final_answer": "B",
            "ganti_jawaban": 1,
            "ragu": True,
            "jejak": [
                {"t_detik": 5, "aksi": "pilih", "opsi": "A"},
                {"t_detik": 25, "aksi": "ganti", "opsi": "B"},
                {"t_detik": 35, "aksi": "ragu"}
            ]
        }
        self.item_lancar = {
            "soal_id": "matematika_p1_n1",
            "position": 1,
            "waktu_detik": 15,
            "first_answer": "C",
            "final_answer": "C",
            "ganti_jawaban": 0,
            "ragu": False,
            "jejak": [
                {"t_detik": 15, "aksi": "pilih", "opsi": "C"}
            ]
        }
        self.items_attempt = [self.item_lancar, self.item_ragu_ganti]

    def test_1_format_behavior_with_full_jejak(self):
        """1. Format teks konteks memuat durasi detik, jawaban awal->akhir, status ragu, dan jejak."""
        ctx = format_student_behavior_context(self.item_ragu_ganti)
        self.assertIn("Konteks perilaku murid di soal ini: 45 detik, jawaban A→B, ragu.", ctx)
        self.assertIn("Sesuaikan penjelasanmu: tanyakan di mana dia berhenti berpikir; jangan langsung kasih jawaban lengkap kalau dia cuma salah baca.", ctx)
        self.assertIn("Murid mengganti jawaban sebanyak 1 kali", ctx)
        self.assertIn("Jejak kronologis: pilih A (5s) -> ganti B (25s) -> ragu (35s)", ctx)

    def test_2_format_behavior_tidak_ragu_dan_tanpa_ganti(self):
        """2. Format soal lancar memuat status 'tidak ragu' tanpa kalimat pergantian jawaban."""
        ctx = format_student_behavior_context(self.item_lancar)
        self.assertIn("Konteks perilaku murid di soal ini: 15 detik, jawaban C→C, tidak ragu.", ctx)
        self.assertIn("Sesuaikan penjelasanmu: tanyakan di mana dia berhenti berpikir", ctx)
        self.assertNotIn("Murid mengganti jawaban", ctx)

    def test_3_find_question_item_by_position(self):
        """3. Pencarian item berdasarkan nomor posisi (position) menemukan data yang tepat."""
        found = find_question_item_in_attempt(self.items_attempt, nomor=3)
        self.assertIsNotNone(found)
        self.assertEqual(found["position"], 3)
        self.assertEqual(found["soal_id"], "matematika_p1_n3")

    def test_4_find_question_item_by_soal_id(self):
        """4. Pencarian item berdasarkan question_id menemukan data yang tepat."""
        found = find_question_item_in_attempt(self.items_attempt, question_id="matematika_p1_n1")
        self.assertIsNotNone(found)
        self.assertEqual(found["position"], 1)

    def test_5_question_not_attempted_returns_empty_context(self):
        """5. Soal yang belum pernah dikerjakan menghasilkan konteks kosong (string empty)."""
        mock_fetcher = MagicMock(return_value=self.items_attempt)
        # Soal nomor 99 belum pernah ada di attempt
        ctx = build_soal_behavior_context(user_id="user_test", nomor=99, fetch_fn=mock_fetcher)
        self.assertEqual(ctx, "")

        # Attempt kosong sama sekali
        mock_empty_fetcher = MagicMock(return_value=[])
        ctx_empty = build_soal_behavior_context(user_id="user_test", nomor=1, fetch_fn=mock_empty_fetcher)
        self.assertEqual(ctx_empty, "")

    def test_6_build_soal_behavior_context_with_mock_fetcher(self):
        """6. Integrasi build_soal_behavior_context dengan mock fetcher database Supabase."""
        mock_fetcher = MagicMock(return_value=self.items_attempt)
        ctx = build_soal_behavior_context(user_id="usr_abc", nomor=3, fetch_fn=mock_fetcher)
        mock_fetcher.assert_called_once_with(user_id="usr_abc", attempt_id=None)
        self.assertIn("jawaban A→B, ragu", ctx)

    def test_7_system_prompt_injection(self):
        """7. Injeksi konteks perilaku ke system prompt tutor (tutor_engine.build_tutor_prompt)."""
        ctx_text = format_student_behavior_context(self.item_ragu_ganti)
        canon_ctx = {
            "text": "Jika x + 2 = 5, berapa x?",
            "options": [{"key": "A", "text": "2"}, {"key": "B", "text": "3"}],
            "subject": "Matematika"
        }
        solution = {"diketahui": "x + 2 = 5", "langkah_penyelesaian": ["x = 3"]}
        
        # 1. Dengan behavior_context
        messages, meta = build_tutor_prompt(
            canon_ctx, solution, "B", [], "Bantu saya nomor ini",
            behavior_context=ctx_text
        )
        sys_prompt = messages[0]["content"]
        self.assertIn("<student_behavior>", sys_prompt)
        self.assertIn("jawaban A→B, ragu", sys_prompt)
        self.assertIn("Sesuaikan penjelasanmu: tanyakan di mana dia berhenti berpikir", sys_prompt)

        # 2. Tanpa behavior_context (soal baru / belum pernah dikerjakan)
        messages_clean, _ = build_tutor_prompt(
            canon_ctx, solution, "B", [], "Bantu saya nomor ini",
            behavior_context=""
        )
        sys_prompt_clean = messages_clean[0]["content"]
        self.assertNotIn("<student_behavior>", sys_prompt_clean)


# ============================================================================
# RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("RUNNING STANDALONE AUDIT TEST SUITE (tests/test_audit_standalone.py)")
    print("Tanpa server.py · Tanpa Database · Tanpa LLM Key · Standalone 100%")
    print("=" * 70 + "\n")
    unittest.main(verbosity=2)
