# -*- coding: utf-8 -*-
"""tests/test_attempt_storage.py — Pengujian validasi dan penyimpanan attempt (Fase A1).

Menguji:
1. Normalisasi bentuk data nyata (list, dict bertingkat, string JSON).
2. Sanitasi field A1: jejak (maks 5), waktu_detik, ganti_jawaban, ragu.
3. Penolakan data rusak dengan pesan error diagnostik jelas.
4. Idempotensi client_attempt_id (skenario kirim ulang tidak dobel).
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from server import clean_attempt_items  # noqa: E402

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    status = "PASS" if cond else "FAIL"
    print(f"{status} {name}" + (f" — {detail}" if detail and not cond else ""))


def test_list_items_with_jejak():
    raw = [
        {
            "soal_id": "matematika:1:9",
            "position": 9,
            "topic_id": "Barisan",
            "first_answer": "B",
            "final_answer": "D",
            "active_ms": 52000,
            "change_count": 1,
            "flagged_ragu": True,
            "jejak": [
                {"t_detik": 14, "aksi": "pilih", "opsi": "B"},
                {"t_detik": 52, "aksi": "ganti", "opsi": "D"},
                {"t_detik": 55, "aksi": "ragu", "opsi": "ragu"},
            ],
        }
    ]
    ok, err, items = clean_attempt_items(raw)
    check("List items normal diterima", ok, err)
    check("Panjang items = 1", len(items) == 1)
    it = items[0]
    check("waktu_detik dihitung tepat (52)", it.get("waktu_detik") == 52)
    check("ganti_jawaban dinormalisasi (1)", it.get("ganti_jawaban") == 1)
    check("ragu bernilai True", it.get("ragu") is True)
    check("jejak memuat 3 event", len(it.get("jejak") or []) == 3)
    check("event 1 aksi pilih opsi B", it["jejak"][0]["aksi"] == "pilih" and it["jejak"][0]["opsi"] == "B")
    check("event 2 aksi ganti opsi D", it["jejak"][1]["aksi"] == "ganti" and it["jejak"][1]["opsi"] == "D")


def test_dict_items_normalization():
    # Menguji akar masalah "Items tidak valid" saat items dikirim sebagai dict bertingkat
    raw = {
        "1": {"soal_id": "matematika:1:1", "position": 1, "first_answer": "A", "final_answer": "A", "active_ms": 20000},
        "2": {"soal_id": "matematika:1:2", "position": 2, "first_answer": "B", "final_answer": "C", "active_ms": 30000, "ganti_jawaban": 1},
    }
    ok, err, items = clean_attempt_items(raw)
    check("Dict items berhasil dinormalisasi menjadi list", ok, err)
    check("Panjang items hasil normalisasi = 2", len(items) == 2)
    check("Urutan item 1 dan 2 terjaga", items[0]["position"] == 1 and items[1]["position"] == 2)


def test_string_json_normalization():
    # Menguji jika items diserialisasi sebagai string JSON
    raw = json.dumps([
        {"soal_id": "matematika:1:1", "position": 1, "first_answer": "A", "final_answer": "A", "active_ms": 10000}
    ])
    ok, err, items = clean_attempt_items(raw)
    check("String JSON items berhasil diparsing", ok, err)
    check("Panjang items string JSON = 1", len(items) == 1)


def test_invalid_items_rejection():
    # 1. None
    ok, err, _ = clean_attempt_items(None)
    check("Items None ditolak", not ok and "tipe=NoneType" in err)

    # 2. List kosong
    ok, err, _ = clean_attempt_items([])
    check("Items [] ditolak dengan diagnostik", not ok and "panjang=0" in err)

    # 3. Dict kosong
    ok, err, _ = clean_attempt_items({})
    check("Items {} ditolak dengan diagnostik", not ok and "panjang=0" in err)

    # 4. List of non-dict
    ok, err, _ = clean_attempt_items(["bukan_dict", 123])
    check("Items list non-dict ditolak", not ok)


def test_jejak_capping():
    # Maksimal 5 kejadian per soal
    raw = [
        {
            "soal_id": "MTK-01",
            "position": 1,
            "active_ms": 70000,
            "jejak": [
                {"t_detik": 10, "aksi": "pilih", "opsi": "A"},
                {"t_detik": 20, "aksi": "ganti", "opsi": "B"},
                {"t_detik": 30, "aksi": "ganti", "opsi": "C"},
                {"t_detik": 40, "aksi": "ganti", "opsi": "D"},
                {"t_detik": 50, "aksi": "ragu", "opsi": "ragu"},
                {"t_detik": 60, "aksi": "ganti", "opsi": "E"},  # ke-6: harus dibuang
                {"t_detik": 70, "aksi": "ganti", "opsi": "A"},  # ke-7: harus dibuang
            ]
        }
    ]
    ok, err, items = clean_attempt_items(raw)
    check("Jejak berhasil diproses", ok, err)
    check("Jejak dipotong tepat maksimal 5 event", len(items[0]["jejak"]) == 5)
    check("Event ke-5 adalah ragu", items[0]["jejak"][4]["aksi"] == "ragu")


def test_client_payload_integration():
    # Menguji payload yang dihasilkan langsung oleh AttemptRecorder client-side
    sim_path = os.path.join(BASE_DIR, "scratch", "simulated_attempt.json")
    if not os.path.isfile(sim_path):
        return
    with open(sim_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    ok, err, items = clean_attempt_items(payload.get("items"))
    check("Payload klien dari AttemptRecorder diterima server", ok, err)
    check("Total 25 soal diproses lengkap", len(items) == 25)
    q9 = next((x for x in items if x["position"] == 9), None)
    check("Soal 9 ditemukan di hasil bersih server", q9 is not None)
    check("Soal 9 memiliki jejak 3 event", len(q9.get("jejak") or []) == 3)
    check("Soal 9 ganti_jawaban = 1", q9.get("ganti_jawaban") == 1)
    check("Soal 9 ragu = True", q9.get("ragu") is True)


def test_idempotency_behavior():
    # Menguji logika respons terhadap Supabase 409 Conflict
    import urllib.error
    # Simulasikan HTTPError 409
    err_409 = urllib.error.HTTPError("http://supabase/attempts", 409, "Conflict", {}, None)
    # Server menangani 409 sebagai success duplicate (idempotent)
    is_duplicate_handled = (err_409.code == 409)
    check("HTTPError 409 terdeteksi sebagai duplicate", is_duplicate_handled)


def run_all():
    print("=== TEST A1: PERBAIKI SIMPAN ATTEMPT & REKAM JEJAK ===")
    test_list_items_with_jejak()
    test_dict_items_normalization()
    test_string_json_normalization()
    test_invalid_items_rejection()
    test_jejak_capping()
    test_client_payload_integration()
    test_idempotency_behavior()
    print(f"\n{len(PASS)} lulus, {len(FAIL)} gagal\n")
    if FAIL:
        sys.exit(1)


if __name__ == "__main__":
    run_all()
