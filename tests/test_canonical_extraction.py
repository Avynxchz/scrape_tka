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
    build_package, OUT_DIR, partial_statement_pairs, norm,
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


# --- varian baru builder (fisika/geografi): pernyataan-di-raw & bukti tak lengkap ---

def test_partial_statement_pairs_salvages_empty_value():
    # Kasus nyata: fisika_paket_1 q3 'A (Benar)\nB (Salah)\nC ()'
    out = partial_statement_pairs("A (Benar)\nB (Salah)\nC ()")
    assert out == {"A": "Benar", "B": "Salah", "C": None}
    # Bukan pola pernyataan -> None (format PGK '(A) teks' tidak tersentuh)
    assert partial_statement_pairs("(A) teks opsi (B) teks opsi") is None
    assert partial_statement_pairs("(C)") is None
    # Lengkap -> None (sudah ditangani parse_official_row)
    assert partial_statement_pairs("A (Benar)\nB (Salah)\nC (Benar)") is None


def test_norm_folds_typographic_variants():
    # 'm.s -1' (raw) vs 'm·s⁻¹' (learning) — semakna, beda penulisan
    assert norm("10 m.s -1") == norm("10 m·s⁻¹")


def test_pernyataan_in_raw_variant_builds(tmp_path):
    """Soal BS dengan field `pernyataan` langsung di raw (bukan opsi B/C/D)."""
    raw_q = {"nomor": 1, "tipe_soal": "Benar-Salah", "stimulus": {"text": "s"},
             "pertanyaan": {"text": "p"}, "pilihan_jawaban": [],
             "pernyataan": [
                 {"key": "A", "text": "Pernyataan A.", "latex": None, "image": None},
                 {"key": "B", "text": "Pernyataan B.", "latex": None, "image": None},
                 {"key": "C", "text": "Pernyataan C.", "latex": None, "image": None},
             ]}
    kunci = {"slug": "slug", "raw_rows": {"1": {"kunci": "A (Benar)\nB (Salah)\nC (Benar)"}}}
    lrn_q = {"nomor": 1, "kunci_jawaban": ["A:Benar", "B:Salah", "C:Benar"],
             "pernyataan": [{"key": k, "text": f"Pernyataan {k}."} for k in "ABC"]}
    q = build_question(raw_q, kunci, lrn_q, "slug", "Fisika", 1, ROOT, ImageDims())
    assert q["type"] == "BS"
    assert [s["key"] for s in q["statements"]] == ["A", "B", "C"]
    assert q["official_answer"] == {
        "format": "per_statement",
        "statements": {"A": "Benar", "B": "Salah", "C": "Benar"},
    }


def test_header_row_duplicate_key_is_dropped():
    """Baris header tabel terekam dgn kunci duplikat di awal (geo_p2 q23/q27)."""
    raw_q = {"nomor": 23, "tipe_soal": "Pernyataan-Label", "stimulus": {"text": "s"},
             "pertanyaan": {"text": "p"}, "pilihan_jawaban": [],
             "pernyataan": [
                 {"key": "A", "text": "Kategori umum.", "latex": None, "image": None},
                 {"key": "A", "text": "Pernyataan A.", "latex": None, "image": None},
                 {"key": "B", "text": "Pernyataan B.", "latex": None, "image": None},
                 {"key": "C", "text": "Pernyataan C.", "latex": None, "image": None},
             ]}
    kunci = {"slug": "slug", "raw_rows": {"23": {"kunci": "A (Lebih kecil)\nB (Lebih besar)\nC (Sama besar)"}}}
    lrn_q = {"nomor": 23, "kunci_jawaban": ["A:Lebih kecil", "B:Lebih besar", "C:Sama besar"],
             "pernyataan": [{"key": k, "text": f"Pernyataan {k}."} for k in "ABC"]}
    q = build_question(raw_q, kunci, lrn_q, "slug", "Geografi", 2, ROOT, ImageDims())
    assert q["type"] == "LABEL"
    assert [(s["key"], s["text"]) for s in q["statements"]] == [
        ("A", "Pernyataan A."), ("B", "Pernyataan B."), ("C", "Pernyataan C.")]


def test_documented_edge_cases_in_built_canonicals(canonical_docs):
    """Kasus tepi nyata hasil rebuild (terdokumentasi, bukan tebakan)."""
    fis1 = {q["question_number"]: q for q in canonical_docs["fisika_paket_1"]["questions"]}
    # q3: bukti resmi 'C ()' kosong -> null + evidence_gap eksplisit
    assert fis1[3]["official_answer"]["statements"]["C"] is None
    assert fis1[3]["official_answer"]["evidence_gap"] == ["C"]
    # q14: teks pernyataan A hilang di raw -> fallback learning bertanda
    st_a = next(s for s in fis1[14]["statements"] if s["key"] == "A")
    assert st_a["text_provenance"] == "learning_reference (raw scrape missing)"
    assert fis1[14]["transcription_status"] == "manual_review"
    # q1: bukti resmi menang atas learning yang keliru (C: Salah)
    assert fis1[1]["official_answer"]["statements"]["C"] == "Salah"


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
        "geografi_paket_1": 10, "geografi_paket_2": 29,
        "fisika_paket_1": 20, "fisika_paket_2": 24,
    }
    assert set(canonical_docs) == set(EXPECTED), "PACKAGES vs EXPECTED tidak sinkron"
    for slug, n in EXPECTED.items():
        assert canonical_docs[slug]["total_questions"] == n


def test_graded_items_total_384(canonical_docs):
    total = 0
    for doc in canonical_docs.values():
        for q in doc["questions"]:
            total += 1 if q["type"] in ("PG", "PGK") else len(q["statements"])
    assert total == 384


def test_type_distribution_preserved(canonical_docs):
    dist = {}
    for doc in canonical_docs.values():
        for q in doc["questions"]:
            dist[q["type"]] = dist.get(q["type"], 0) + 1
    assert dist == {"PG": 163, "PGK": 77, "BS": 35, "LABEL": 13}


def test_official_answers_match_learning_keys(canonical_docs):
    """official_answer harus identik dengan kunci otoritatif learning JSON.

    Ketidakcocokan yang DIPIN (terdokumentasi eksplisit — tes ini GAGAL bila
    pin usang atau muncul mismatch baru):
    - ("matematika_paket_1", 31, "C"): bukti resmi C=Salah vs learning C=Benar.
      Data penentu (tabel volume wisatawan) ada di gambar yang masih unresolved
      -> belum dapat diadili; dilarang "memperbaiki" buta-buta.
    - paket "kewirausahaan_paket_2": learning didedup 30->29 (Fase 3 #13) namun
      canonical masih 30 soal (rebuild butuh dedup lapis raw) -> perbandingan
      per-nomor tidak valid sampai canonical dibangun ulang selaras.
    """
    from _key_guard import _canon
    PINNED_MISMATCHES = {("matematika_paket_1", 31, "C")}
    PINNED_DRIFT_SLUGS = {"kewirausahaan_paket_2"}
    mismatches = set()
    for slug, doc in canonical_docs.items():
        if slug in PINNED_DRIFT_SLUGS:
            continue
        lrn = json.load(open(os.path.join(ROOT, "data", f"{slug}_learning.json"), encoding="utf-8"))
        lrn_by_no = {q["nomor"]: q for q in lrn["soal"]}
        for q in doc["questions"]:
            lq = lrn_by_no[q["question_number"]]
            if q["type"] in ("PG", "PGK"):
                canon = q["official_answer"]["correct"]
                exp = (lq["kunci_jawaban"] if isinstance(lq["kunci_jawaban"], list)
                       else [lq["kunci_jawaban"]])
                if sorted(_canon(x) for x in canon) != sorted(_canon(x) for x in exp):
                    mismatches.add((slug, q["question_number"], "key"))
            else:
                stmts = q["official_answer"]["statements"]
                # Learning menyimpan kunci pernyataan sbg list "A:Benar"
                lrn_map = dict(item.split(":", 1) for item in lq["kunci_jawaban"])
                for st in q["statements"]:
                    official_val = stmts[st["key"]]
                    if official_val is None:
                        # Celah bukti resmi ('X ()' kosong di review) — tercatat
                        # di official_answer.evidence_gap; tak ada yang diverifikasi
                        continue
                    if official_val.lower() != lrn_map[st["key"]].lower():
                        mismatches.add((slug, q["question_number"], st["key"]))
    assert mismatches == PINNED_MISMATCHES, (
        f"mismatch baru atau pin usang: {sorted(mismatches ^ PINNED_MISMATCHES)}"
    )


def test_kewirausahaan_paket_2_drift_is_pinned():
    """Pin drift yang diketahui: learning 29 soal (dedup Fase 3 #13) vs
    canonical 30 soal. HAPUS tes ini saat canonical dibangun ulang selaras
    (butuh keputusan dedup lapis raw + kunci)."""
    lrn = json.load(open(os.path.join(ROOT, "data", "kewirausahaan_paket_2_learning.json"),
                         encoding="utf-8"))["soal"]
    can = json.load(open(os.path.join(OUT_DIR, "kewirausahaan_paket_2.json"),
                         encoding="utf-8"))["questions"]
    assert len(lrn) == 29 and len(can) == 30


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
