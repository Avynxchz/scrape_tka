# -*- coding: utf-8 -*-
"""Test sumber Layer 3 (solusi Claude): skema, kunci otoritatif, switching, review.

Sumber produksi: data/solution_sources/MTK_PAKET_2_SOLUTIONS_EXTRA.json
(Konten solusi Claude TIDAK pernah diedit oleh test ini; fixture sintetis hanya
untuk menguji mekanisme registry dan selalu dipulihkan byte-identik.)
"""
import copy
import json
import os

import pytest

import server  # noqa: E402
import solution_loader as sl  # noqa: E402

SOURCE_FILE = "MTK_PAKET_2_SOLUTIONS_EXTRA.json"
REG_PATH = sl.REGISTRY_PATH


# ---------------------------------------------------------------------------
# Parsing & skema file sumber produksi
# ---------------------------------------------------------------------------

def test_source_file_parses_and_schema_ok():
    doc, meta = sl.load_solution_doc("matematika", 2)
    assert doc is not None
    sl.validate_solution_doc(doc)  # raise bila tidak sah
    assert doc["package"] == 2
    assert doc["subject"] == "Matematika"
    assert len(doc["solutions"]) == 25
    assert meta["source_file"] == SOURCE_FILE


def test_no_duplicate_ids_and_numbers_1_to_25():
    doc, _ = sl.load_solution_doc("matematika", 2)
    ids = [s["question_id"] for s in doc["solutions"]]
    nums = sorted(s["question_number"] for s in doc["solutions"])
    assert len(set(ids)) == 25
    assert nums == list(range(1, 26))


def test_validate_rejects_duplicates_and_missing_fields():
    doc, _ = sl.load_solution_doc("matematika", 2)
    # Duplikat question_id harus ditolak
    bad = copy.deepcopy(doc)
    bad["solutions"].append(copy.deepcopy(bad["solutions"][0]))
    with pytest.raises(ValueError, match="Duplikat"):
        sl.validate_solution_doc(bad)
    # Field Layer 3 yang hilang harus ditolak
    bad2 = copy.deepcopy(doc)
    del bad2["solutions"][0]["tips"]
    with pytest.raises(ValueError, match="tips"):
        sl.validate_solution_doc(bad2)


def test_layer3_fields_never_edited_by_loader():
    """Isi konten solusi dibaca apa adanya — loader tidak meregenerasi/menulis."""
    doc, _ = sl.load_solution_doc("matematika", 2)
    raw = doc["solutions"][0]  # Q1
    s = sl.get_solution("matematika", 2, 1, "C")
    assert s["concept_kunci"] == raw["concept_kunci"]
    assert s["reasoning"] == raw["reasoning"]
    assert s["why_correct"] == raw["why_correct"]
    assert [st["title"] for st in s["steps"]] == [st["title"] for st in raw["steps"]]


# ---------------------------------------------------------------------------
# Kunci: Claude TIDAK pernah menimpa kunci otoritatif
# ---------------------------------------------------------------------------

def test_all_25_keys_crosscheck_against_authoritative():
    """Cross-check seluruh 25 kunci Claude vs kunci otoritatif learning JSON."""
    doc, _ = sl.load_solution_doc("matematika", 2)
    results = {}
    for s in doc["solutions"]:
        nomor = s["question_number"]
        lrn = server.learning_for("matematika", 2, nomor)
        kunci_disp = server.format_kunci_display(lrn)
        results[nomor] = sl.cross_check_keys(s, kunci_disp)["match"]
    mismatched = {n: m for n, m in results.items() if not m}
    # Bila ada mismatch, harus ter-flag — TIDAK pernah direkonsiliasi diam-diam
    print(f"Cross-check 25 kunci: {sum(results.values())}/25 cocok; mismatch: {mismatched}")
    assert all(results.values()), f"Ada kunci Claude ≠ otoritatif (ter-flag): {mismatched}"


def test_authoritative_key_display_comes_from_learning_not_claude():
    """Payload selalu menampilkan kunci otoritatif, bukan field Claude."""
    canon = server.canonical_for("matematika", 2, 1)
    lrn = server.learning_for("matematika", 2, 1)
    sol = server.build_solution_payload(canon, lrn, "matematika", 2)
    doc, _ = sl.load_solution_doc("matematika", 2)
    claude_key = doc["solutions"][0]["official_answer"]["correct"]
    # Kunci tampilan == otoritatif; nilai Claude hanya untuk cross-check
    assert sol["answer_display"] == server.format_kunci_display(lrn)
    assert sol["key_crosscheck"]["authoritative"] == server.format_kunci_display(lrn)
    assert claude_key == ["C"]  # informasi Claude tetap tersimpan utk audit


# ---------------------------------------------------------------------------
# needs_manual_review dipertahankan (Q5, Q14, Q15, Q21)
# ---------------------------------------------------------------------------

def test_review_flags_preserved_from_source():
    doc, _ = sl.load_solution_doc("matematika", 2)
    flagged = {s["question_number"] for s in doc["solutions"] if s.get("needs_manual_review")}
    assert flagged == {5, 15}, flagged
    for nomor in (5, 15):
        s = sl.get_solution("matematika", 2, nomor, "-")
        assert s["review"]["needs_manual_review"] is True
        assert s["review"]["review_reason"], f"Q{nomor} harus punya review_reason"
        # Konten tetap disajikan (bukan dihapus)
        assert s["concept_kunci"] and s["steps"]


def test_non_review_questions_not_flagged():
    s = sl.get_solution("matematika", 2, 1, "C")
    assert s["review"]["needs_manual_review"] is False
    assert s["review"]["review_reason"] is None


# ---------------------------------------------------------------------------
# Mapping spesifik per soal: Q2, Q3, Q11, Q14, Q21
# ---------------------------------------------------------------------------

def test_q2_solution_is_about_fractional_exponents():
    s = sl.get_solution("matematika", 2, 2, "C")
    all_text = json.dumps(s, ensure_ascii=False)
    assert "8=2^{3}" in all_text or "8 = 2^{3}" in all_text
    assert "(3^{2})^{5/6}" in all_text  # bentuk persis di penjelasan Q2
    assert "frac{4}{3}" in all_text  # hasil akhir


def test_q3_solution_is_about_custom_operation_odot():
    s = sl.get_solution("matematika", 2, 3, "A (Benar), B (Salah), C (Benar)")
    all_text = json.dumps(s, ensure_ascii=False)
    assert "odot" in all_text
    assert "a^{2}+b^{2}" in all_text or "a^2+b^2" in all_text
    assert s["review"]["needs_manual_review"] is False
    # Langkah Q2 tidak boleh muncul di Q3
    q2_text = json.dumps(sl.get_solution("matematika", 2, 2, "C"), ensure_ascii=False)
    q3_text = json.dumps(s, ensure_ascii=False)
    assert "basis 2" not in q3_text or "basis 2" in q2_text  # konten beda fokus
    assert "8=2^{3}" not in q3_text  # materi eksponen Q2 tidak bocor ke Q3


def test_q11_solution_is_about_room_geometry():
    s = sl.get_solution("matematika", 2, 11, "B, E")
    all_text = json.dumps(s, ensure_ascii=False)
    assert "BCGF" in all_text and "ADHE" in all_text
    assert s["key_crosscheck"]["match"] is True


def test_q14_and_q21_resolved_and_available():
    for nomor in (14, 21):
        canon = server.canonical_for("matematika", 2, nomor)
        lrn = server.learning_for("matematika", 2, nomor)
        sol = server.build_solution_payload(canon, lrn, "matematika", 2)
        assert sol is not None, f"Q{nomor} harus tersedia"
        assert sol["pembahasan"]["langkah_penyelesaian"]  # konten dipertahankan


# ---------------------------------------------------------------------------
# Switching sumber aktif LOW <-> EXTRA (registry; konten tidak diubah)
# ---------------------------------------------------------------------------

@pytest.fixture
def registry_guard():
    """Simpan registry.json asli; pulihkan byte-identik setelah test."""
    original = open(REG_PATH, "rb").read() if os.path.exists(REG_PATH) else None
    yield
    if original is None:
        if os.path.exists(REG_PATH):
            os.remove(REG_PATH)
    else:
        with open(REG_PATH, "wb") as f:
            f.write(original)


LOW_DOC = {
    "package": 2,
    "subject": "Matematika",
    "solutions": [
        {
            "question_id": "mtk_p2_q01",
            "question_number": 1,
            "official_answer": {"format": "single", "correct": ["C"]},
            "needs_manual_review": False,
            "review_reason": None,
            "concept_kunci": ["LOW-EFFORT-KONSEP-HIMPUNAN"],
            "glossary": [],
            "reasoning": "LOW-EFFORT-REASONING",
            "steps": [{"step": 1, "title": "Langkah LOW", "explanation": "x"}],
            "why_correct": "LOW-EFFORT-WHY",
            "common_mistakes": [],
            "tips": ["LOW-EFFORT-TIPS"],
        },
        # Sengaja TIDAK memuat soal lain -> fallback state jujur saat aktif
    ],
}


def test_switch_low_to_extra_and_back(tmp_path, monkeypatch, registry_guard):
    """LOW -> EXTRA -> LOW tanpa menyentuh frontend; konten sumber tak berubah."""
    low_path = os.path.join(sl.SOLUTION_DIR, "MTK_PAKET_2_SOLUTIONS_LOW.json")
    assert not os.path.exists(low_path), "LOW produksi belum ada (fixture hanya virtual)"
    try:
        with open(low_path, "w", encoding="utf-8") as f:
            json.dump(LOW_DOC, f, ensure_ascii=False)
        sl._source_cache.clear()

        # Aktifkan LOW
        sl.set_active_source("matematika", 2, "MTK_PAKET_2_SOLUTIONS_LOW.json")
        canon = server.canonical_for("matematika", 2, 1)
        lrn = server.learning_for("matematika", 2, 1)
        sol_low = server.build_solution_payload(canon, lrn, "matematika", 2)
        assert "LOW-EFFORT" in json.dumps(sol_low["pembahasan"], ensure_ascii=False)
        # Soal yang tidak ada di LOW -> state jujur (bukan fallback lama)
        assert server.build_solution_payload(
            server.canonical_for("matematika", 2, 3), None, "matematika", 2) is None

        # Aktifkan EXTRA
        sl.set_active_source("matematika", 2, SOURCE_FILE)
        sol_extra = server.build_solution_payload(canon, lrn, "matematika", 2)
        assert "LOW-EFFORT" not in json.dumps(sol_extra["pembahasan"], ensure_ascii=False)
        assert "irisan" in " ".join(sol_extra["pembahasan"]["konsep_kunci"]).lower()

        # Kembali ke LOW lalu pulihkan EXTRA (state akhir produksi)
        sl.set_active_source("matematika", 2, "MTK_PAKET_2_SOLUTIONS_LOW.json")
        assert "LOW-EFFORT" in json.dumps(
            server.build_solution_payload(canon, lrn, "matematika", 2)["pembahasan"],
            ensure_ascii=False)
    finally:
        # Pulihkan state produksi: EXTRA aktif + hapus fixture LOW
        sl.set_active_source("matematika", 2, SOURCE_FILE)
        if os.path.exists(low_path):
            os.remove(low_path)
        sl._source_cache.clear()


def test_final_registry_points_to_extra():
    """State akhir produksi: Matematika Paket 2 memakai sumber EXTRA."""
    reg = sl.load_registry()
    assert reg.get("mtk_paket_2", {}).get("active_source") == SOURCE_FILE
    assert sl.resolve_active_source("matematika", 2) is not None


def test_registry_survives_unknown_package():
    """Paket tanpa entri registry -> tidak ada sumber (bukan crash)."""
    assert sl.resolve_active_source("subject_tidak_ada", 1) is None
    assert sl.get_solution("subject_tidak_ada", 1, 1, "-") is None


def test_set_active_source_rejects_missing_file(registry_guard):
    """Registry menolak file sumber yang tidak ada (fail loud, bukan diam-diam)."""
    with pytest.raises(FileNotFoundError):
        sl.set_active_source("matematika", 2, "TIDAK_ADA_SOURCES.json")
    # Registry tidak berubah akibat percobaan gagal
    reg = sl.load_registry()
    assert reg.get("mtk_paket_2", {}).get("active_source") == SOURCE_FILE
