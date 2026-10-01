# -*- coding: utf-8 -*-
"""build_canonical_questions.py — Lapisan kanonis AI-readable untuk seluruh bank soal TKA.

Arsitektur:

    RAW SCRAPE (data/<subj>/paket_<n>/<slug>.json, struktur asli situs resmi)
    data/kunci/<slug>_kunci.json   (BUKTI kunci resmi dari review_hasil)
    data/<slug>_learning.json      ( struktur pembelajaran; HANYA untuk cross-check)
            │  (baca-saja; tidak ada file otoritatif yang ditulis)
            ▼
    data/canonical_questions/<slug>.json   (lapisan teks kanonis untuk LLM)

Aturan kesetiaan (fidelity):
- Teks sumber disalin VERBATIM (tidak diparafrasekan, tidak "dibenahi").
- Formula inline memakai `data-latex` resmi dari situs (atribut semantik pada
  <img>) — BUKAN hasil OCR.
- Gambar tanpa representasi semantik DITANDAI eksplisit
  ([VISUAL_INFORMATION_UNRESOLVED: ...]) dan masuk daftar `unresolved`;
  builder TIDAK menebak, TIDAK mengisi nilai, TIDAK menyederhanakan.
- Kunci resmi diturunkan ulang dari bukti mentah (raw_rows) dan diverifikasi
  silang terhadap data learning; perbedaan = gagal keras (tidak menulis output).
- Deterministik: tanpa timestamp, output sama persis bila input sama.

Builder ini HANYA mengekstraksi. Tidak ada penjelasan/pembahasan/konten tutor
yang dibuat di sini (pemisahan ekstraksi vs enrichment by design).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "data", "canonical_questions")
VISION_DIR = os.path.join(ROOT, "data", "canonical_questions", "_vision")

SCHEMA_VERSION = "1.0"
ANSWER_SOURCE = "official_review_scrape (data/kunci/, review_hasil Pusmendik)"

# Util dari alat perbaikan yang sudah tervalidasi (pengurai baris kunci resmi).
sys.path.insert(0, ROOT)
from _repair_keys import parse_official_row  # noqa: E402  (fungsi murni, tanpa efek samping)

PACKAGES = [
    # slug, subject, package, direktori raw
    ("matematika_paket_1", "Matematika", 1, "data/paket_1"),
    ("matematika_paket_2", "Matematika", 2, "data/paket_2"),
    ("bahasa_inggris_paket_1", "Bahasa Inggris", 1, "data/bahasa_inggris/paket_1"),
    ("bahasa_inggris_paket_2", "Bahasa Inggris", 2, "data/bahasa_inggris/paket_2"),
    ("ekonomi_paket_1", "Ekonomi", 1, "data/ekonomi/paket_1"),
    ("ekonomi_paket_2", "Ekonomi", 2, "data/ekonomi/paket_2"),
    ("kewirausahaan_paket_1", "Kewirausahaan", 1, "data/kewirausahaan/paket_1"),
    ("kewirausahaan_paket_2", "Kewirausahaan", 2, "data/kewirausahaan/paket_2"),
    ("geografi_paket_1", "Geografi", 1, "data/geografi/paket_1"),
]

SUBJECT_PREFIX = {
    "Matematika": "mtk",
    "Bahasa Inggris": "bing",
    "Ekonomi": "eko",
    "Kewirausahaan": "pkwu",
    "Geografi": "geo",
}

# --- Klasifikasi visual (deterministik, berbasis ukuran + konteks teks) -----
# Formula hasil render MathJax resmi berukuran kecil (pita teks tunggal);
# diagram/grafik/tabel jauh lebih besar. Ambang dari pengukuran dataset:
# formula terbesar 573 B / 94 px; aset visual terkecil 2.033 B / 43 px, tapi
# aset visual nyata >= ~5 KB. Gabungan tinggi+byte aman untuk keduanya.
FORMULA_MAX_H = 140
FORMULA_MAX_BYTES = 12000

RE_TABLE_HINT = re.compile(r"\btabel\b|\btable\b", re.I)
RE_GRAPH_HINT = re.compile(r"\bgrafik\b|\bgraph\b|diagram lingkaran|\bpie chart\b", re.I)


def load_sidecar(slug):
    """Muat transkripsi vision side-car `_vision/<slug>.json` bila ada (opsional).

    Bentuk: {filename: {"latex": str | null, "description": str | null}}.
    """
    path = os.path.join(VISION_DIR, f"{slug}.json")
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    return {}


def classify_visual(width, height, nbytes, context_text):
    """Kembalikan 'formula' | 'table' | 'graph' | 'diagram' secara deterministik.

    Dimensi None (file tak terbaca) → bukan formula; jatuh ke jenis konteks.
    """
    if (
        height is not None and nbytes is not None
        and height <= FORMULA_MAX_H and nbytes <= FORMULA_MAX_BYTES
    ):
        return "formula"
    if RE_TABLE_HINT.search(context_text or ""):
        return "table"
    if RE_GRAPH_HINT.search(context_text or ""):
        return "graph"
    return "diagram"


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def unresolved_marker(kind, filename, note):
    return f"[VISUAL_INFORMATION_UNRESOLVED: {filename} — {note}]"


class ImageDims:
    """Dimensi gambar (dengan cache) — gagal halus bila file tak terbaca."""

    def __init__(self):
        self._cache = {}

    def get(self, path):
        if path not in self._cache:
            try:
                from PIL import Image
                with Image.open(path) as im:
                    self._cache[path] = (im.width, im.height, os.path.getsize(path))
            except Exception:
                self._cache[path] = (None, None, None)
        return self._cache[path]


def image_entry(img, role, represented_by=None):
    e = {
        "filename": img["filename"],
        "rel_path": img["rel_path"],
        "remote_url": img["remote_url"],
        "role": role,
    }
    if img.get("data_latex"):
        e["data_latex"] = img["data_latex"]
    if represented_by:
        # Gambar terwakili semantik oleh representasi lain (mis. latex opsi)
        e["represented_by"] = represented_by
    return e


def render_visual_reference(unres, kind, filename, note):
    """Catat unresolved + kembalikan penanda teksnya."""
    unres.append({"kind": kind, "element": filename, "reason": note})
    return unresolved_marker(kind, filename, note)


def render_inline_images(images, location, ctx, dims, unres, formulas, visuals):
    """Render daftar <img> inline menjadi teks kanonis + entri visual_context.

    Prioritas representasi:
      1. `data-latex` resmi dari situs (atribut semantik <img>)
      2. transkripsi vision tersimpan di side-car `_vision/<slug>.json`
         (hasil pass Claude Web — faktual, per elemen, tanpa penalaran)
      3. penanda eksplisit [VISUAL_INFORMATION_UNRESOLVED] + entri unresolved

    Mengembalikan string teks (penanda untuk yang belum terrepresentasi).
    """
    parts = []
    sidecar = ctx.get("sidecar") or {}
    for img in images:
        latex = img.get("data_latex")
        w, h, nbytes = dims.get(os.path.join(ctx["images_root"], img["rel_path"]))
        if latex:
            formulas.append({"latex": latex, "image": img["rel_path"], "location": location, "source": "official data-latex"})
            parts.append(f"${latex}$")
            continue
        kind = classify_visual(w, h, nbytes, ctx["section_text"])
        t = sidecar.get(img["filename"])
        if t and t.get("latex"):
            formulas.append({"latex": t["latex"], "image": img["rel_path"], "location": location, "source": "vision transcription"})
            parts.append(f"${t['latex']}$")
        elif t and t.get("description"):
            # Deskripsi vision: masuk bucket table/graph/diagram sesuai klasifikasi;
            # visual kecil berklasifikasi 'formula' tapi berdeskripsi teks → 'others'
            bucket = f"{kind}s" if kind in ("table", "graph", "diagram") else "others"
            entry = {"image": img["rel_path"], "location": location, "description": t["description"], "source": "vision transcription"}
            visuals[bucket].append(entry)
            parts.append(f"[{kind.title()} — {img['filename']}]: {t['description']}")
        elif kind == "formula":
            note = "server-rendered formula image without data-latex; transcription pending vision pass"
            parts.append(render_visual_reference(unres, "formula", img["filename"], note))
        else:
            note = f"{kind} image; textual description pending vision transcription"
            parts.append(render_visual_reference(unres, kind, img["filename"], note))
            visuals[kind + "s"].append({"image": img["rel_path"], "location": location})
    return " ".join(p for p in parts if p)


def option_display(opt, ctx, dims, unres, formulas, visuals):
    """Teks kanonis satu opsi: text (verbatim) + latex inline + penanda unresolved."""
    parts = []
    txt = (opt.get("text") or "").strip()
    if txt:
        parts.append(txt)
    if opt.get("latex"):
        parts.append(f"${opt['latex']}$")
    img = opt.get("image")
    if img and not opt.get("latex"):
        entry = dict(img)
        entry["data_latex"] = None
        parts.append(render_inline_images([entry], f"option {opt['key']}", ctx, dims, unres, formulas, visuals))
    return " ".join(parts).strip()


def derive_official_answer(kunci, nomor, qtype):
    """Turunkan kunci resmi dari bukti mentah (raw_rows) — sumber satu-satunya."""
    row = kunci["raw_rows"].get(str(nomor))
    if not row:
        raise ValueError(f"{kunci['slug']}: bukti kunci untuk soal {nomor} tidak ada")
    kind, payload = parse_official_row(row["kunci"])
    if qtype in ("BS", "LABEL"):
        if kind not in ("bs", "label"):
            raise ValueError(f"{kunci['slug']} soal {nomor}: bukti bukan format pernyataan ({kind})")
        return {"format": "per_statement", "statements": payload}
    if qtype == "PG":
        if kind != "single":
            raise ValueError(f"{kunci['slug']} soal {nomor}: bukti bukan kunci tunggal ({kind})")
        return {"format": "single", "correct": payload}
    if qtype == "PGK":
        if kind not in ("multi", "single"):
            raise ValueError(f"{kunci['slug']} soal {nomor}: bukti kunci PGK tidak terbaca ({kind})")
        return {"format": "multiple", "correct": payload}
    raise ValueError(f"tipe tak dikenal: {qtype}")


def check_against_learning(q, official, lrn_q, slug):
    """Cross-check kunci resmi vs data learning (wajib identik secara normalisasi)."""
    k = lrn_q.get("kunci_jawaban")
    probs = []
    if official["format"] == "per_statement":
        lrn_map = {}
        for item in k or []:
            key, _, val = item.partition(":")
            lrn_map[key] = val
        for key, val in official["statements"].items():
            if norm(lrn_map.get(key, "")) != norm(val):
                probs.append(f"kunci pernyataan {key}: bukti={val!r} learning={lrn_map.get(key)!r}")
    elif official["format"] == "single":
        if not isinstance(k, str) or norm(k) != norm(official["correct"][0]):
            probs.append(f"kunci: bukti={official['correct'][0]!r} learning={k!r}")
    else:
        if not isinstance(k, list) or sorted(norm(x) for x in k) != sorted(norm(x) for x in official["correct"]):
            probs.append(f"kunci PGK: bukti={official['correct']!r} learning={k!r}")
    if probs:
        raise ValueError(f"{slug} soal {q['nomor']}: kunci learning ≠ bukti resmi → {probs}")
    return official


def qtype_from_raw(raw_q):
    tipe = (raw_q.get("tipe_soal") or "").lower()
    if "kompleks" in tipe:
        return "PGK"
    return "PG"


def build_question(raw_q, kunci, lrn_q, slug, subject, package, images_root, dims, sidecar=None):
    nomor = raw_q["nomor"]
    qtype = qtype_from_raw(raw_q)
    # Tipe pernyataan bersumber dari kunci resmi (bukan dari teks tipe learning):
    prov = kunci["raw_rows"].get(str(nomor), {}).get("kunci", "")
    kind, payload = parse_official_row(prov)
    if kind == "bs":
        qtype = "BS"
    elif kind == "label":
        qtype = "LABEL"
    elif kind == "multi" and qtype == "PG":
        # Bukti resmi multi-kunci mendahului deteksi tipe dari HTML mentah
        qtype = "PGK"

    unres, formulas = [], []
    visuals = {"tables": [], "graphs": [], "diagrams": [], "others": []}
    src_images = []

    # --- Stimulus -----------------------------------------------------------
    stim = raw_q.get("stimulus") or {}
    stim_text = (stim.get("text") or "").strip()
    ctx = {"images_root": images_root, "section_text": stim_text, "sidecar": sidecar}
    stim_parts = [stim_text] if stim_text else []
    stim_imgs = [image_entry(i, "stimulus") for i in (stim.get("images") or [])]
    src_images.extend(stim_imgs)
    stim_visual = render_inline_images(stim.get("images") or [], "stimulus", ctx, dims, unres, formulas, visuals)
    if stim_visual:
        stim_parts.append(stim_visual)
    stimulus_text_canon = "\n".join(stim_parts).strip()

    # --- Pertanyaan ---------------------------------------------------------
    pert = raw_q.get("pertanyaan") or {}
    pert_text = (pert.get("text") or "").strip()
    ctx = {"images_root": images_root, "section_text": pert_text, "sidecar": sidecar}
    pert_imgs = [image_entry(i, "question") for i in (pert.get("images") or [])]
    src_images.extend(pert_imgs)
    pert_visual = render_inline_images(pert.get("images") or [], "question", ctx, dims, unres, formulas, visuals)
    question_text_canon = pert_text
    if pert_visual:
        question_text_canon = (question_text_canon + "\n" + pert_visual).strip()

    # --- Opsi / Pernyataan --------------------------------------------------
    official = check_against_learning(
        raw_q, derive_official_answer(kunci, nomor, qtype), lrn_q, slug
    )

    options, statements = None, None
    if qtype in ("PG", "PGK"):
        options = {}
        ctx = {"images_root": images_root, "section_text": pert_text or stim_text, "sidecar": sidecar}
        for opt in raw_q.get("pilihan_jawaban") or []:
            key = opt["key"]
            options[key] = option_display(opt, ctx, dims, unres, formulas, visuals)
            if opt.get("image"):
                src_images.append(image_entry(
                    opt["image"], f"option {key}",
                    represented_by="option latex" if opt.get("latex") else None,
                ))
    else:
        # Soal pernyataan: opsi resmi B/C/D adalah pernyataan A/B/C (opsi A = header tabel)
        statements = []
        opts = {o["key"]: o for o in raw_q.get("pilihan_jawaban") or []}
        for stmt_key, src_key in zip(["A", "B", "C"], ["B", "C", "D"]):
            src = opts.get(src_key, {})
            item = {"key": stmt_key}
            text_bits = []
            if (src.get("text") or "").strip():
                text_bits.append(src["text"].strip())
                item["text"] = src["text"].strip()
            if src.get("latex"):
                item["latex"] = src["latex"]
                text_bits.append(f"${src['latex']}$")
            if src.get("image"):
                item["image"] = src["image"]
                src_images.append(image_entry(
                    src["image"], f"statement {stmt_key}",
                    represented_by="statement latex" if src.get("latex") else None,
                ))
                if not src.get("latex"):
                    # Tanpa representasi semantik -> gambar perlu transkripsi vision
                    entry = dict(src["image"])
                    entry["data_latex"] = None
                    ctx = {"images_root": images_root, "section_text": pert_text or stim_text, "sidecar": sidecar}
                    rendered = render_inline_images(
                        [entry], f"statement {stmt_key}", ctx, dims, unres, formulas, visuals
                    )
                    text_bits.append(rendered)
            if not text_bits:
                note = "statement has no text, latex, or image representation"
                item["text"] = render_visual_reference(unres, "statement", stmt_key, note)
            item["display"] = " ".join(text_bits).strip()
            statements.append(item)
        # Cross-check pernyataan turunan vs pernyataan otoritatif (learning)
        lrn_stmts = {s["key"]: s for s in (lrn_q.get("pernyataan") or [])}
        for st in statements:
            ls = lrn_stmts.get(st["key"])
            if not ls:
                raise ValueError(f"{slug} soal {nomor}: pernyataan {st['key']} tidak ada di learning")
            if (ls.get("text") or "").strip():
                if norm(ls["text"]) != norm(st.get("text") or ""):
                    raise ValueError(
                        f"{slug} soal {nomor} pernyataan {st['key']}: teks learning ≠ turunan raw"
                    )
            elif ls.get("image"):
                if ls["image"]["filename"] != (st.get("image") or {}).get("filename"):
                    raise ValueError(
                        f"{slug} soal {nomor} pernyataan {st['key']}: gambar learning ≠ turunan raw"
                    )

    # --- Rangkuman visual_context & status ----------------------------------
    has_visuals = bool(formulas or any(visuals.values()) or stim_imgs or pert_imgs)
    visual_context = {
        "description": (
            "This question contains visual elements that are also represented above "
            "in text where a semantic representation existed; unresolved elements are "
            "explicitly marked."
            if has_visuals
            else "No visual elements in this question."
        ),
        "formulas": formulas,
        "tables": visuals["tables"],
        "graphs": visuals["graphs"],
        "diagrams": visuals["diagrams"],
        "others": visuals["others"],
        "unresolved": unres,
    }

    qid = f"{SUBJECT_PREFIX[subject]}_p{package}_q{nomor:02d}"
    canon = {
        "id": qid,
        "slug": slug,
        "subject": subject,
        "package": package,
        "question_number": nomor,
        "source_id": raw_q.get("id") or f"soal-no-{nomor}",
        "type": qtype,
        "stimulus_text": stimulus_text_canon,
        "stimulus_images": stim_imgs,
        "question_text": question_text_canon,
        "question_images": pert_imgs,
    }
    if options is not None:
        canon["options"] = options
    if statements is not None:
        canon["statements"] = statements
    canon["visual_context"] = visual_context
    canon["source_images"] = src_images
    canon["official_answer"] = official
    canon["answer_source"] = ANSWER_SOURCE
    canon["unresolved_count"] = len(unres)
    canon["transcription_status"] = "manual_review" if unres else "ai_ready"
    return canon


def build_package(slug, subject, package, raw_dir, out_dir=OUT_DIR, dims=None):
    dims = dims or ImageDims()
    raw = json.load(open(os.path.join(ROOT, raw_dir, f"{slug}.json"), encoding="utf-8"))
    kunci = json.load(open(os.path.join(ROOT, "data", "kunci", f"{slug}_kunci.json"), encoding="utf-8"))
    lrn = json.load(open(os.path.join(ROOT, "data", f"{slug}_learning.json"), encoding="utf-8"))

    lrn_by_no = {q["nomor"]: q for q in lrn["soal"]}
    # Side-car transkripsi vision (opsional; file hanya ada bila pass Claude sudah jalan)
    sidecar = load_sidecar(slug)
    questions = []
    for raw_q in raw["soal"]:
        nomor = raw_q["nomor"]
        if nomor not in lrn_by_no:
            raise ValueError(f"{slug}: soal {nomor} tidak ada di learning JSON")
        questions.append(
            build_question(
                raw_q, kunci, lrn_by_no[nomor], slug, subject, package,
                images_root=os.path.join(ROOT, raw_dir), dims=dims, sidecar=sidecar,
            )
        )

    doc = {
        "schema_version": SCHEMA_VERSION,
        "slug": slug,
        "subject": subject,
        "package": package,
        "total_questions": len(questions),
        "source": {
            "raw_scrape": os.path.join(raw_dir, f"{slug}.json"),
            "official_key_evidence": f"data/kunci/{slug}_kunci.json",
            "official_key_scraped_at": kunci.get("scraped_at"),
            "learning_reference": f"data/{slug}_learning.json",
            "extraction": "deterministic structured extraction (data-latex + source text); no OCR",
        },
        "questions": questions,
    }

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{slug}.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return doc, out_path


def main():
    report = []
    for slug, subject, package, raw_dir in PACKAGES:
        doc, path = build_package(slug, subject, package, raw_dir)
        ready = sum(1 for q in doc["questions"] if q["transcription_status"] == "ai_ready")
        unres = sum(q["unresolved_count"] for q in doc["questions"])
        report.append((slug, doc["total_questions"], ready, unres, path))
        print(f"{slug:28s} questions={doc['total_questions']:3d} ai_ready={ready:3d} unresolved={unres:3d}")
    total = sum(r[1] for r in report)
    print(f"TOTAL questions={total}")


if __name__ == "__main__":
    main()
