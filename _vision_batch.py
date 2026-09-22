# -*- coding: utf-8 -*-
"""_vision_batch.py — Paket transkripsi vision terkonsolidasi + konversi hasil.

Mempersiapkan SATU paket untuk pass transkripsi vision Claude Web atas SEMUA
elemen visual unresolved pada lapisan kanonis:

    data/canonical_questions/_vision_batch/
    ├── VISION_MANIFEST.json   ← manifest + kontrak output yang wajib dikembalikan
    ├── images/                ← 100 berkas unik (dedup by sha256, byte-identical)
    │                            dinamai V###__<nama_asli>.png (bebas tabrakan)
    ├── VISION_REVIEW.pdf      ← contact sheet berlabel visual_id (untuk review)
    └── results/               ← (setelah Claude) hasil per-slug siap `ingest`

Prinsip:
  - Dedup AMAN: setiap referensi asli dipertahankan sebagai `occurrences`
    (slug, package, question_number, section, original_filename) → tidak ada
    kehilangan pemetaan soal/opsi/sumber.
  - visual_id stabil & deterministik (urutan paket → nomor soal → urutan unresolved).
  - Konversi hasil (`convert`) memvalidasi ketat lalu menulis hasil per-slug
    dalam format persis yang diterima `python _vision_packet.py ingest`.
  - Read-only terhadap data otoritatif; builder kanonis tidak diubah.

Perintah:
    python _vision_batch.py build            # buat manifest + images + PDF
    python _vision_batch.py convert HASIL.json [HASIL2.json ...]
"""
import hashlib
import json
import os
import sys
import glob as globmod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_canonical_questions import PACKAGES, OUT_DIR, ROOT  # noqa: E402

BATCH_DIR = os.path.join(OUT_DIR, "_vision_batch")
REPRESENTATION_TYPES = ("formula", "diagram", "graph", "table", "text", "mixed")
CONFIDENCE = ("high", "medium", "low")

INSTRUCTIONS = [
    "TASK: visual transcription only. You are given images from an Indonesian",
    "national exam (TKA) question bank. For each image, describe/transcribe EXACTLY",
    "what is visibly printed. You must NOT solve questions, must NOT infer missing",
    "information, must NOT complete unreadable parts, and must NOT fabricate",
    "formulas, numbers, labels, axis values, or graph data.",
    "",
    "Return ONE JSON object with a single key \"visuals\": a list with EXACTLY one",
    "entry per visual_id in VISION_MANIFEST.json, using this exact shape:",
    "",
    '  {',
    '    "visual_id": "V001",',
    '    "representation_type": "formula|diagram|graph|table|text|mixed",',
    '    "latex": "LaTeX string, or null",',
    '    "description": "faithful textual description, or null",',
    '    "confidence": "high|medium|low",',
    '    "unresolved": false,',
    '    "notes": null',
    '  }',
    "",
    "Field rules:",
    "- latex: set ONLY when the image is a mathematical expression/formula",
    "  (equation, inequality, fraction, root, exponent, set, interval). Keep",
    "  Indonesian decimal commas (e.g. 0,5) and wording exactly as printed.",
    "- description: set ONLY for tables (render as a Markdown table), graphs",
    "  (axes, labels, scale, plotted lines/points, intercepts, legend), diagrams",
    "  (objects, labels, measures, positions, connections as shown), or other",
    "  meaningful visuals.",
    "- representation_type: 'formula' if latex is set; otherwise the closest of",
    "  diagram|graph|table|text|mixed.",
    "- If any part is unreadable or ambiguous: keep what IS readable, set",
    '  "unresolved": true, put the readable part in latex/description, and explain',
    '  the ambiguity in "notes". NEVER guess.',
    "- One image may repeat across several questions (deduplicated by content);",
    "  transcribe it once — the manifest maps it back to every occurrence.",
]


def load_unresolved():
    """Kumpulkan semua elemen unresolved per paket dari canonical JSON."""
    out = {}
    for slug, subject, package, raw_dir in PACKAGES:
        path = os.path.join(OUT_DIR, f"{slug}.json")
        doc = json.load(open(path, encoding="utf-8"))
        imgs_root = os.path.join(ROOT, raw_dir, "images")
        items = []
        for q in doc["questions"]:
            # Peta filename → lokasi presisi dari source_images (role resmi)
            loc = {}
            for img in q["source_images"]:
                loc[img["filename"]] = img["role"]
            for u in q["visual_context"]["unresolved"]:
                fname = u["element"]
                fpath = os.path.join(imgs_root, fname)
                if not os.path.exists(fpath):
                    raise SystemExit(f"file sumber hilang: {fpath}")
                items.append({
                    "slug": slug, "subject": subject, "package": package,
                    "question_number": q["question_number"], "question_id": q["id"],
                    "question_type": q["type"],
                    "section": loc.get(fname, "unknown"),
                    "original_filename": fname,
                    "kind_hint": u["kind"], "reason": u["reason"],
                    "source_path": fpath,
                })
        if items:
            out[slug] = items
    return out


def cmd_build():
    unresolved = load_unresolved()

    # --- dedup by byte hash, urutan deterministik ----------------------------
    visual_list = []           # [{visual_id, sha256, file, kind_hint, occurrences, ...}]
    by_hash = {}
    for slug in unresolved:    # PACKAGES order (dict insertion order)
        for it in unresolved[slug]:
            data = open(it["source_path"], "rb").read()
            sha = hashlib.sha256(data).hexdigest()
            if sha not in by_hash:
                vid = f"V{len(visual_list) + 1:03d}"
                ext = os.path.splitext(it["original_filename"])[1] or ".png"
                target = f"{vid}__{it['original_filename']}"
                entry = {
                    "visual_id": vid,
                    "sha256": sha,
                    "file": f"images/{target}",
                    "kind_hint": it["kind_hint"],
                    "bytes": len(data),
                    "occurrences": [],
                    "source_path": it["source_path"],  # internal; dibuang saat dump
                }
                by_hash[sha] = entry
                visual_list.append(entry)
            by_hash[sha]["occurrences"].append({
                "slug": it["slug"], "subject": it["subject"],
                "package": it["package"],
                "question_number": it["question_number"],
                "question_id": it["question_id"],
                "question_type": it["question_type"],
                "section": it["section"],
                "original_filename": it["original_filename"],
            })

    manifest = {
        "purpose": "vision_transcription_batch (deduplicated by sha256; mapping preserved)",
        "created_for": "single Claude Web pass — transcription only, no solving/inference",
        "totals": {
            "unresolved_references": sum(len(v) for v in unresolved.values()),
            "unique_visuals": len(visual_list),
            "questions_with_unresolved": len({
                (v["slug"], v["question_number"])
                for items in unresolved.values() for v in items
            }),
        },
        "instructions": INSTRUCTIONS,
        "output_contract": {
            "wrapper": {"visuals": []},
            "per_visual_required_keys": [
                "visual_id", "representation_type", "latex", "description",
                "confidence", "unresolved", "notes",
            ],
            "enums": {
                "representation_type": list(REPRESENTATION_TYPES),
                "confidence": list(CONFIDENCE),
            },
            "rule": "one entry per visual_id; latex XOR description (or both null when unresolved)",
        },
        "visuals": visual_list,
    }

    os.makedirs(os.path.join(BATCH_DIR, "images"), exist_ok=True)
    for v in visual_list:
        dst = os.path.join(BATCH_DIR, v["file"].replace("/", os.sep))
        with open(v["source_path"], "rb") as src, open(dst, "wb") as out:
            out.write(src.read())

    with open(os.path.join(BATCH_DIR, "VISION_MANIFEST.json"), "w", encoding="utf-8", newline="\n") as f:
        dumped = [
            {k: v for k, v in vis.items() if k != "source_path"}
            for vis in visual_list
        ]
        manifest["visuals"] = dumped
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

    build_pdf(visual_list)

    t = manifest["totals"]
    print(f"manifest : {os.path.relpath(os.path.join(BATCH_DIR, 'VISION_MANIFEST.json'), ROOT)}")
    print(f"images   : {len(visual_list)} unique files "
          f"({sum(v['bytes'] for v in visual_list) / 1e6:.1f} MB) → {os.path.relpath(os.path.join(BATCH_DIR, 'images'), ROOT)}")
    print(f"pdf      : {os.path.relpath(os.path.join(BATCH_DIR, 'VISION_REVIEW.pdf'), ROOT)}")
    print(f"totals   : unresolved_refs={t['unresolved_references']} unique={t['unique_visuals']} "
          f"questions={t['questions_with_unresolved']}")


def build_pdf(visual_list):
    """Contact sheet berlabel: visual_id + meta + gambar ukuran asli (fit halaman)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Image as RLImage, KeepTogether, PageBreak)
    from reportlab.lib.styles import getSampleStyleSheet
    from PIL import Image as PILImage

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    meta = styles["Code"]
    body = styles["BodyText"]

    doc = SimpleDocTemplate(
        os.path.join(BATCH_DIR, "VISION_REVIEW.pdf"), pagesize=A4,
        title="TKA Vision Transcription Batch", author="canonical pipeline",
    )
    W, H = A4
    maxw, maxh = W - 3 * cm, H - 7 * cm

    story = [
        Paragraph("TKA — Vision Transcription Batch", h1),
        Paragraph(
            "Transcribe each visual EXACTLY as printed. No solving, no inference, "
            "no fabrication. Output contract: see VISION_MANIFEST.json "
            "(one JSON entry per visual_id). Ambiguity must stay marked "
            "(unresolved: true + notes).", body),
        Spacer(1, 6),
    ]
    for i, v in enumerate(visual_list):
        occ = v["occurrences"]
        lines = [
            f"{v['visual_id']}  |  kind_hint={v['kind_hint']}  |  "
            f"sha256={v['sha256'][:16]}  |  {len(occ)} occurrence(s)",
        ]
        for o in occ:
            lines.append(
                f"  -> {o['slug']} · Q{o['question_number']} · {o['section']} · "
                f"{o['original_filename']}")
        block = [
            Paragraph(lines[0], meta),
            *[Paragraph(x, meta) for x in lines[1:]],
            Spacer(1, 3),
        ]
        try:
            with PILImage.open(v["source_path"]) as im:
                w, h = im.size
            scale = min(1.0, maxw / w, maxh / h)
            if scale < 1.0:
                block.append(RLImage(v["source_path"], width=w * scale, height=h * scale))
            else:
                block.append(RLImage(v["source_path"], width=w, height=h))
        except Exception:
            block.append(Paragraph("[image could not be embedded]", body))
        story.append(KeepTogether(block))
        if (i + 1) % 2 == 0:
            story.append(PageBreak())

    doc.build(story)


def cmd_convert(result_paths):
    """Validasi hasil Claude → hasil per-slug siap `_vision_packet.py ingest`."""
    manifest = json.load(open(os.path.join(BATCH_DIR, "VISION_MANIFEST.json"), encoding="utf-8"))
    visuals = {v["visual_id"]: v for v in manifest["visuals"]}

    per_slug = {}
    problems, seen = [], set()
    for rp in result_paths:
        result = json.load(open(rp, encoding="utf-8"))
        for item in result.get("visuals", []):
            vid = item.get("visual_id")
            if vid not in visuals:
                problems.append(f"{vid}: visual_id tidak ada di manifest")
                continue
            if vid in seen:
                problems.append(f"{vid}: duplikat pada hasil")
                continue
            seen.add(vid)
            rt, conf = item.get("representation_type"), item.get("confidence")
            if rt not in REPRESENTATION_TYPES:
                problems.append(f"{vid}: representation_type '{rt}' tidak valid")
                continue
            if conf not in CONFIDENCE:
                problems.append(f"{vid}: confidence '{conf}' tidak valid")
                continue
            latex, desc = item.get("latex"), item.get("description")
            if item.get("unresolved"):
                continue  # tetap unresolved di kanonis — tidak masuk side-car
            if not latex and not desc:
                problems.append(f"{vid}: unresolved=false tapi latex & description kosong")
                continue
            if latex and not isinstance(latex, str):
                problems.append(f"{vid}: latex bukan string")
                continue
            if desc and not isinstance(desc, str):
                problems.append(f"{vid}: description bukan string")
                continue
            v = visuals[vid]
            for occ in v["occurrences"]:
                per_slug.setdefault(occ["slug"], {})[occ["original_filename"]] = {
                    "latex": latex or None, "description": desc or None,
                }

    missing = sorted(set(visuals) - seen)
    os.makedirs(os.path.join(BATCH_DIR, "results"), exist_ok=True)
    for slug, mapping in sorted(per_slug.items()):
        out = os.path.join(BATCH_DIR, "results", f"{slug}_result.json")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        print(f"OK  {slug}: {len(mapping)} elemen → {os.path.relpath(out, ROOT)}")
        print(f"    ingest: PYTHONIOENCODING=utf-8 python _vision_packet.py ingest {slug} "
              f"{os.path.relpath(out, ROOT).replace(os.sep, '/')}")

    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  -", p)
    if missing:
        print(f"\nBELUM ditranskripsi ({len(missing)}): {', '.join(missing)}")
        print("Visual ini tetap unresolved di kanonis sampai diingest dengan hasilnya.")
    if problems:
        raise SystemExit(1)


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        cmd_build()
    elif len(sys.argv) >= 3 and sys.argv[1] == "convert":
        cmd_convert(sys.argv[2:])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
