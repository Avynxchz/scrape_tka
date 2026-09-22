# -*- coding: utf-8 -*-
"""Tes integrasi lapisan kanonis ke server AI Tutor & panel penyelesaian."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import server  # noqa: E402  (import aman — server hanya jalan di __main__)
import solution_loader  # noqa: E402


def test_canonical_for_all_subjects():
    for subject, pkgs in server.SUBJECT_SLUGS.items():
        for pkg in pkgs:
            q = server.canonical_for(subject, pkg, 1)
            assert q is not None, f"{subject} paket {pkg} nomor 1 hilang"
            assert q["question_number"] == 1


def test_canonical_for_out_of_range():
    assert server.canonical_for("matematika", 2, 999) is None
    assert server.canonical_for("subject_ngaco", 1, 1) is None


def test_visual_question_answered_from_canonical_transcription():
    """Soal dengan tabel/gambar tertranskripsi harus dijawab dari deskripsi nyata."""
    q = server.canonical_for("ekonomi", 1, 16)  # punya tabel kopi hasil vision
    assert q is not None
    ctx = server.build_canonical_context(q, server.learning_for("ekonomi", 1, 16))
    assert "KUNCI RESMI" in ctx["soal_text"]
    assert ctx["visual_text"] != "Soal ini tidak memiliki elemen visual."
    q_data = {"_canonical": ctx, "subject": "ekonomi"}
    reply = server.get_ai_tutor_response(1, 16, "gambar di soal ini apa ya?", q_data)
    assert "Deskripsi Gambar" in reply
    # Deskripsi nyata dari pass vision (bukan placeholder)
    assert len(reply) > 200


def test_kunci_question_uses_canonical_display():
    ctx = server.build_canonical_context(
        server.canonical_for("matematika", 2, 1),
        server.learning_for("matematika", 2, 1),
    )
    q_data = {"_canonical": ctx, "subject": "matematika"}
    reply = server.get_ai_tutor_response(2, 1, "apa kunci jawabannya?", q_data)
    assert ctx["kunci_display"] in reply


def test_langkah_without_claude_steps_is_honest():
    ctx = server.build_canonical_context(
        server.canonical_for("matematika", 2, 1),
        server.learning_for("matematika", 2, 1),
    )
    assert ctx["langkah_claude"] == []  # fase solusi Claude belum berjalan
    q_data = {"_canonical": ctx, "subject": "matematika"}
    reply = server.get_ai_tutor_response(2, 1, "bagaimana langkah pengerjaannya?", q_data)
    assert "belum tersedia" in reply
    assert "STIMULUS" in reply or "SOAL" in reply  # konteks soal tetap diberikan


def test_solution_payload_pending_without_claude_steps():
    canon = server.canonical_for("matematika", 1, 1)
    lrn = server.learning_for("matematika", 1, 1)
    assert server.build_solution_payload(canon, lrn) is None


def test_solution_payload_with_active_layer3(tmp_path, monkeypatch):
    """Bila sumber Layer 3 aktif memuat soal ini, payload pembahasan tersusun lengkap."""
    canon = server.canonical_for("matematika", 2, 1)
    lrn = server.learning_for("matematika", 2, 1)
    sol = server.build_solution_payload(canon, lrn, "matematika", 2)
    assert sol is not None, "registry aktif (EXTRA) harus memuat mtk2 q1"
    p = sol["pembahasan"]
    assert len(p["langkah_penyelesaian"]) >= 4
    assert p["konsep_kunci"] and isinstance(p["konsep_kunci"], list)
    assert "irisan" in " ".join(p["konsep_kunci"]).lower()
    assert p["mengapa_begini"], "reasoning + why_correct harus terisi"
    assert sol["answer_display"] == "C"
    assert sol["canonical_id"] == canon["id"]
    # Sumber tercatat & kunci otoritatif dipertahankan
    assert sol["source"]["file"] == "MTK_PAKET_2_SOLUTIONS_EXTRA.json"
    assert sol["key_crosscheck"]["match"] is True
    assert sol["key_crosscheck"]["authoritative"] == "C"


def test_solution_payload_review_flag_preserved():
    """needs_manual_review dari file sumber dipertahankan + kunci tetap otoritatif."""
    canon = server.canonical_for("matematika", 2, 5)
    lrn = server.learning_for("matematika", 2, 5)
    sol = server.build_solution_payload(canon, lrn, "matematika", 2)
    assert sol is not None
    assert sol["review"]["needs_manual_review"] is True
    assert sol["review"]["review_reason"], "alasan review harus ikut tersimpan"
    # Konten tetap disajikan (bukan dihapus), hanya ditandai
    assert sol["pembahasan"]["langkah_penyelesaian"]


def test_key_mismatch_flagged_not_reconciled():
    """Kunci Claude ≠ otoritatif -> mismatch di-flag; kunci otoritatif tidak pernah berubah."""
    canon = server.canonical_for("matematika", 2, 1)
    lrn = server.learning_for("matematika", 2, 1)
    kunci_asli = "C"
    cc = solution_loader.cross_check_keys(
        {"official_answer": {"format": "single", "correct": ["A"]}}, kunci_asli)
    assert cc["match"] is False
    assert cc["authoritative"] == kunci_asli  # tidak direkonsiliasi


def test_visual_unresolved_is_flagged_honestly():
    """Soal mtk2 q14 (6 grafik belum tertranskripsi) harus ditandai jujur."""
    q = server.canonical_for("matematika", 2, 14)
    ctx = server.build_canonical_context(q, server.learning_for("matematika", 2, 14))
    assert "belum terwakili teks" in ctx["visual_text"]


# ===========================================================================
# PEMISAHAN LAPISAN: Layer 2 (konteks kanonis) vs Layer 3 (solusi Claude)
# ===========================================================================


def test_collect_visual_items_is_layer2_not_solution():
    """Visual items = transkripsi Layer 2; tersedia walau solusi (Layer 3) belum ada."""
    canon = server.canonical_for("ekonomi", 1, 16)  # punya tabel kopi hasil vision
    items = server.collect_visual_items(canon)
    assert items and any("abel" in i["kind"] or "Visual" in i["kind"] for i in items)
    # Solusi tetap None -> panel harus menampilkan status jujur
    assert server.build_solution_payload(canon, server.learning_for("ekonomi", 1, 16)) is None


def test_tutor_does_not_leak_legacy_generic_content():
    """Konten enrichment generik lama TIDAK boleh disajikan sebagai penjelasan spesifik."""
    ctx = server.build_canonical_context(
        server.canonical_for("matematika", 2, 3),
        server.learning_for("matematika", 2, 3),
    )
    q_data = {
        "_canonical": ctx,
        "subject": "matematika",
        "topik": "Operasi Hitung Bilangan Bulat",
        "pembahasan": {
            "konsep_kunci": "LEGACY-KONSEP-GENERIK",
            "mengapa_begini": "LEGACY-ALASAN-GENERIK",
            "tips_trik": "LEGACY-TIPS-GENERIK",
        },
    }
    for pesan in ("kenapa jawabannya seperti itu?", "kasih tips dong", "jelaskan donk"):
        reply = server.get_ai_tutor_response(2, 3, pesan, q_data)
        assert "LEGACY" not in reply, f"Konten legacy bocor untuk pesan: {pesan}"


def test_tutor_glossary_uses_question_specific_canonical_formulas():
    """Glosarium tutor = notasi yang BENAR-BENAR muncul di soal ini (bukan umum)."""
    canon = server.canonical_for("matematika", 2, 3)  # definisi operasi a ⊙ b
    ctx = server.build_canonical_context(canon, server.learning_for("matematika", 2, 3))
    assert ctx["formulas"], "soal uji harus punya formula kanonis"
    q_data = {
        "_canonical": ctx,
        "subject": "matematika",
        "topik": "Operasi",
        "pembahasan": {"glosarium_simbol": [{"simbol": "x", "nama": "Variabel", "arti": "LEGACY-GENERIK"}]},
    }
    reply = server.get_ai_tutor_response(2, 3, "apa arti simbolnya?", q_data)
    assert "\\odot" in reply  # notasi spesifik soal ini
    assert "LEGACY-GENERIK" not in reply  # glosarium generik lama tidak bocor


def test_tutor_langkah_prefers_claude_steps_only():
    """Langkah legacy generik tidak dipakai; hanya langkah hasil Claude (Layer 3)."""
    ctx = server.build_canonical_context(
        server.canonical_for("matematika", 2, 1),
        server.learning_for("matematika", 2, 1),
    )
    q_data = {
        "_canonical": ctx,
        "subject": "matematika",
        "topik": "Himpunan",
        "pembahasan": {"langkah_penyelesaian": ["LEGACY-LANGKAH-GENERIK"]},
    }
    reply = server.get_ai_tutor_response(2, 1, "bagaimana langkah pengerjaannya?", q_data)
    assert "LEGACY" not in reply
    assert "belum tersedia" in reply

    # Bila Layer 3 aktif memuat soal ini -> langkahnya dipakai verbatim
    l3 = solution_loader.get_solution("matematika", 2, 1, "C")
    assert l3 and l3["steps"], "sumber aktif harus memuat langkah mtk2 q1"
    q_data2 = {
        "_canonical": ctx,
        "subject": "matematika",
        "topik": "Himpunan",
        "_solution_layer3": l3,
    }
    reply2 = server.get_ai_tutor_response(2, 1, "bagaimana langkah pengerjaannya?", q_data2)
    assert "Tentukan anggota himpunan A" in reply2  # judul langkah asli Q1
    assert "LEGACY" not in reply2
