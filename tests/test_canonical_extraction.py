# -*- coding: utf-8 -*-
"""Tes pipeline transkripsi kanonis (build_canonical_questions.py).

Cakupan (sesuai perubahan pipeline):
  - klasifikasi visual deterministik
  - render inline: data-latex → side-car → penanda unresolved eksplisit
  - prioritas sumber (data-latex resmi > side-car)
  - derivasi & konsistensi kunci resmi (tipe + jawaban, lintas paket)
  - integriti dataset (jumlah soal, tipe, gambar, status transkripsi)
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from build_canonical_questions import (  # noqa: E402
    classify_visual, render_inline_images, ImageDims, load_sidecar,
    build_question, derive_official_answer, parse_official_row, PACKAGES,
    build_package, OUT_DIR,
)


# --- unit: klasifikasi visual ------------------------------------------------

@pytest.mark.parametrize("h,bytes_,text,expected", [
    (94, 573, "hasil dari", "formula"),
    (300, 30000, "perhatikan grafik berikut", "graph"),
    (300, 30000, "tabel berikut menyatakan", "table"),
    (300, 30000, "perhatikan bangun berikut", "diagram"),
])
def test_classify_visual(h, bytes_, text, expected):
    assert classify_visual(600, h, bytes_, text) == expected


# --- unit: render inline ------------------------------------------------------

def _ctx(section=""):
    return {"images_root": ROOT, "section_text": section, "sidecar": {}}


def test_render_inline_uses_official_data_latex():
    unres, formulas, visuals = [], [], {"tables": [], "graphs": [], "diagrams": []}
    img = {"filename": "f.png", "rel_path": "images/f.png", "data_latex": "x \\le 10"}
    out = render_inline_images([img], "question", _ctx(), ImageDims(), unres, formulas, visuals)
    assert out == "$x \\le 10$"
    assert not unres and formulas[0]["source"] == "official data-latex"


def test_render_inline_unresolved_marker_is_explicit():
    # Gambar tak ada di disk → dims None → klasifikasi diagram (fallback kind tetap deterministik)
    unres, formulas, visuals = [], [], {"tables": [], "graphs": [], "diagrams": []}
    img = {"filename": "nope.png", "rel_path": "images/nope.png"}
    out = render_inline_images([img], "question", _ctx(), ImageDims(), unres, formulas, visuals)
    assert "VISUAL_INFORMATION_UNRESOLVED" in out
    assert len(unres) == 1 and unres[0]["element"] == "nope.png"


def test_render_inline_sidecar_fills_unrepresented(tmp_path, monkeypatch):
    # Side-car hanya dipakai BILA tidak ada data-latex resmi (prioritas sumber)
    monkeypatch.setattr(
        "build_canonical_questions.load_sidecar", lambda slug: {
            "sc.png": {"latex": None, "description": "Tabel: Bulan | Penjualan"}
        }
    )
    from build_canonical_questions import build_package as _bp  # hanya memastikan import jalan
    _ = _bp
    unres, formulas, visuals = [], [], {"tables": [], "graphs": [], "diagrams": []}
    img = {"filename": "sc.png", "rel_path": "images/sc.png"}
    ctx = _ctx()
    ctx["sidecar"] = {"sc.png": {"latex": None, "description": "Tabel: Bulan | Penjualan"}}
    out = render_inline_images([img], "question", ctx, ImageDims(), unres, formulas, visuals)
    assert "Tabel: Bulan | Penjualan" in out and "UNRESOLVED" not in out
    assert not unres


# --- tipe & kunci resmi --------------------------------------------------------

def test_parse_official_row_kinds():
    # Bentuk riil di data/kunci/: kunci tunggal berbentuk '(C)'
    assert parse_official_row("(C)")[0] == "single"
    assert parse_official_row("(A;D)")[0] == "multi"
    # Bentuk riil BS (pasangan per baris, label di dalam kurung)
    kind, payload = parse_official_row("A (Benar)\nB (Salah)\nC (Benar)")
    assert kind == "bs" and payload["A"] == "Benar"
    # Bentuk riil label (baris baru, bukan titik-koma)
    kind, payload = parse_official_row("A (Similarity)\nB (Similarity)\nC (Difference)")
    assert kind == "label" and payload["C"] == "Difference"
    assert parse_official_row("bebas")[0] == "unknown"


def test_multi_key_promotes_pg_to_pgk(tmp_path):
    """Kunci resmi multi-huruf mendahului deteksi tipe dari HTML mentah."""
    raw_q = {"nomor": 1, "tipe_soal": "Pilihan Ganda", "stimulus": {"text": "s"},
             "pertanyaan": {"text": "p"}, "pilihan_jawaban": [
                 {"key": k, "text": "t"} for k in "ABCDE"]}
    kunci = {"slug": "slug", "raw_rows": {"1": {"kunci": "(A;D)"}}}
    lrn_q = {"nomor": 1, "kunci_jawaban": ["A", "D"], "tipe_soal": "PG"}
    dims = ImageDims()
    q = build_question(raw_q, kunci, lrn_q, "slug", "Matematika", 1, ROOT, dims)
    assert q["type"] == "PGK"
    assert q["official_answer"] == {"format": "multiple", "correct": ["A", "D"]}


def test_type_mismatch_against_learning_raises():
    """Kunci tunggal resmi tapi learning PGK → bentrok, harus raise (jaga tipe)."""
    raw_q = {"nomor": 1, "tipe_soal": "Pilihan Ganda", "stimulus": {"text": "s"},
             "pertanyaan": {"text": "p"}, "pilihan_jawaban": [
                 {"key": k, "text": "t"} for k in "ABCDE"]}
    kunci = {"slug": "slug", "raw_rows": {"1": {"kunci": "(C)"}}}
    lrn_q = {"nomor": 1, "kunci_jawaban": ["A", "D"], "tipe_soal": "PG"}
    with pytest.raises(ValueError):
        build_question(raw_q, kunci, lrn_q, "slug", "Matematika", 1, ROOT, ImageDims())


# --- dataset penuh (invariant lintas paket) ------------------------------------

@pytest.fixture(scope="module")
def canonical_docs():
    docs = {}
    for slug, subject, package, raw_dir in PACKAGES:
        docs[slug] = json.load(open(os.path.join(OUT_DIR, f"{slug}.json"), encoding="utf-8"))
    return docs


def test_question_counts_match_raw(canonical_docs):
    EXPECTED = {
        "matematika_paket_1": 46, "matematika_paket_2": 25,
        "bahasa_inggris_paket_1": 20, "bahasa_inggris_paket_2": 25,
        "ekonomi_paket_1": 20, "ekonomi_paket_2": 29,
        "kewirausahaan_paket_1": 10, "kewirausahaan_paket_2": 30,
    }
    for slug, n in EXPECTED.items():
        assert canonical_docs[slug]["total_questions"] == n


def test_graded_items_total_259(canonical_docs):
    total = 0
    for doc in canonical_docs.values():
        for q in doc["questions"]:
            total += 1 if q["type"] in ("PG", "PGK") else len(q["statements"])
    assert total == 259


def test_type_distribution_preserved(canonical_docs):
    dist = {}
    for doc in canonical_docs.values():
        for q in doc["questions"]:
            dist[q["type"]] = dist.get(q["type"], 0) + 1
    assert dist == {"PG": 117, "PGK": 61, "BS": 22, "LABEL": 5}


def test_official_answers_match_learning_keys(canonical_docs):
    """official_answer harus identik dengan kunci otoritatif learning JSON."""
    from _key_guard import _canon
    for slug, doc in canonical_docs.items():
        lrn = json.load(open(os.path.join(ROOT, "data", f"{slug}_learning.json"), encoding="utf-8"))
        lrn_by_no = {q["nomor"]: q for q in lrn["soal"]}
        for q in doc["questions"]:
            lq = lrn_by_no[q["question_number"]]
            if q["type"] in ("PG", "PGK"):
                canon = q["official_answer"]["correct"]
                assert sorted(_canon(x) for x in canon) == sorted(
                    _canon(x) for x in (lq["kunci_jawaban"] if isinstance(lq["kunci_jawaban"], list) else [lq["kunci_jawaban"]])
                ), f"{slug} soal {q['question_number']}"
            else:
                stmts = q["official_answer"]["statements"]
                # Learning menyimpan kunci pernyataan sbg list "A:Benar"
                lrn_map = dict(item.split(":", 1) for item in lq["kunci_jawaban"])
                for st in q["statements"]:
                    assert stmts[st["key"]].lower() == lrn_map[st["key"]].lower()


def test_canonical_answer_shape(canonical_docs):
    """PG → {'format':'single','correct':[X]}; PGK → format 'multiple';
    BS/LABEL → format 'per_statement' dengan payload per kunci pernyataan."""
    for doc in canonical_docs.values():
        for q in doc["questions"]:
            oa = q["official_answer"]
            if q["type"] == "PG":
                assert oa["format"] == "single" and len(oa["correct"]) == 1
            elif q["type"] == "PGK":
                assert oa["format"] == "multiple" and 2 <= len(oa["correct"]) <= 5
            else:
                assert oa["format"] == "per_statement"
                assert set(oa["statements"]) == {s["key"] for s in q["statements"]}


def test_unresolved_implies_manual_review(canonical_docs):
    for doc in canonical_docs.values():
        for q in doc["questions"]:
            expected = "manual_review" if q["unresolved_count"] else "ai_ready"
            assert q["transcription_status"] == expected


def test_all_source_images_exist_on_disk(canonical_docs):
    roots = {slug: os.path.join(ROOT, raw) for slug, _, _, raw in PACKAGES}
    for slug, doc in canonical_docs.items():
        for q in doc["questions"]:
            for img in q["source_images"]:
                p = os.path.join(roots[slug], img["rel_path"])
                assert os.path.exists(p), f"{slug}: {p} hilang"


def test_every_image_ref_has_transcription_or_marker(canonical_docs):
    """Tak ada gambar 'diam': terwakili (latex/deskripsi) ATAU penanda eksplisit."""
    for doc in canonical_docs.values():
        for q in doc["questions"]:
            refs = {i["filename"] for i in q["source_images"]}
            covered = set()
            for f in q["visual_context"]["formulas"]:
                covered.add(os.path.basename(f["image"]))
            for grp in ("tables", "graphs", "diagrams", "others"):
                for v in q["visual_context"][grp]:
                    covered.add(os.path.basename(v["image"]))
            for u in q["visual_context"]["unresolved"]:
                covered.add(os.path.basename(u["element"]))
            # Gambar dengan representasi semantik lain (mis. latex opsi) tercakup juga
            covered |= {
                i["filename"] for i in q["source_images"] if i.get("represented_by")
            }
            missing = refs - covered
            assert not missing, f"{doc['slug']} soal {q['question_number']}: {missing}"


def test_sidecar_file_shape():
    """Side-car (bila ada) harus peta filename → {latex, description}."""
    path = os.path.join(OUT_DIR, "_vision", "matematika_paket_2.json")
    if os.path.exists(path):
        sc = load_sidecar("matematika_paket_2")
        assert isinstance(sc, dict)
        for fname, entry in sc.items():
            assert set(entry) <= {"latex", "description"}
            assert entry.get("latex") or entry.get("description")
