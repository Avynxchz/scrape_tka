# -*- coding: utf-8 -*-
"""_vision_packet.py — Packet review vision + ingestion transkripsi (deterministik).

Arsitektur side-car (layer terpisah, tanpa duplikasi sumber):
    data/canonical_questions/_review_paket_N/     → paket unggahan (PDF + images/ + notes.json)
    data/canonical_questions/_vision/<slug>.json  → side-car transkripsi (faktual per elemen)

Builder kanonis (`build_canonical_questions.py`) membaca side-car ini secara
opsional: `data-latex` resmi tetap prioritas; transkripsi vision hanya mengisi
yang belum terwakili secara semantik. Tanpa side-car, builder deterministik
menghasilkan penanda [VISUAL_INFORMATION_UNRESOLVED] yang eksplisit — bukan tebakan.

Perintah:
    python _vision_packet.py build [slug ...]   # buat packet review per paket
    python _vision_packet.py ingest <slug> <result.json>  # tulis side-car + rebuild
"""
import json
import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_canonical_questions import (  # noqa: E402
    PACKAGES, OUT_DIR, ROOT, load_sidecar,
)

REVIEW_ROOT = os.path.join(OUT_DIR, "_review")
VISION_DIR = os.path.join(OUT_DIR, "_vision")

# Satu instruksi untuk semua elemen: faktual, per elemen, tanpa penalaran.
INSTRUCTIONS = [
    "You are transcribing question images from an Indonesian national exam (TKA).",
    "Work ONLY from what is visibly printed in each image.",
    "For each image, output one JSON object keyed by filename with fields:",
    '  "latex": a LaTeX string if the image is a mathematical expression, formula,',
    "     equation, inequality, fraction, root, exponent, set, or interval — otherwise null.",
    '  "description": a faithful textual description if the image is a table, graph,',
    "     diagram, or other meaningful visual — otherwise null.",
    "Rules:",
    "- Never solve, infer, simplify, or complete anything; do not guess unreadable parts.",
    "- If something is unreadable, set the field to null and add \"note\" explaining why.",
    "- Tables: output as Markdown table inside description.",
    "- Graphs: describe axes, labels, scale, plotted lines/points, intercepts, legends.",
    "- Diagrams: describe objects, labels, measures, positions, connections as shown.",
    "- Keep numbers, symbols, and wording EXACTLY as printed (Indonesian decimal comma stays).",
]


def slug_meta(slug):
    for s, subject, package, raw_dir in PACKAGES:
        if s == slug:
            return subject, package, raw_dir
    raise SystemExit(f"slug tidak dikenal: {slug}")


def gather_unresolved(slug):
    """Kumpulkan unresolved elements per soal dari canonical JSON yang ada."""
    path = os.path.join(OUT_DIR, f"{slug}.json")
    doc = json.load(open(path, encoding="utf-8"))
    by_q = {}
    for q in doc["questions"]:
        els = []
        for u in q["visual_context"]["unresolved"]:
            els.append({
                "filename": u["element"],
                "kind": u["kind"],
                "location": u.get("location") or "?",
                "context": u.get("context") or "?",
                "current_marker": u.get("rendered_marker") or "",
            })
        if els:
            by_q[str(q["question_number"])] = els
    return doc, by_q


def cmd_build(slugs):
    if not slugs:
        slugs = [p[0] for p in PACKAGES]
    for slug in slugs:
        subject, package, raw_dir = slug_meta(slug)
        doc, by_q = gather_unresolved(slug)
        if not by_q:
            print(f"{slug}: tidak ada unresolved — packet dilewati")
            continue
        rev = os.path.join(REVIEW_ROOT, f"paket_{package}" if subject == "Matematika" else f"{slug}")
        img_dir = os.path.join(rev, "images")
        os.makedirs(img_dir, exist_ok=True)

        src_root = os.path.join(ROOT, raw_dir, "images")
        copied = []
        for nomor, els in sorted(by_q.items(), key=lambda kv: int(kv[0])):
            for el in els:
                src = os.path.join(src_root, el["filename"])
                if not os.path.exists(src):
                    raise SystemExit(f"file hilang: {src}")
                dst = os.path.join(img_dir, os.path.basename(el["filename"]))
                shutil.copyfile(src, dst)
                copied.append(el)

        notes = {
            "purpose": "vision_transcription_review_packet",
            "slug": slug,
            "subject": subject,
            "package": package,
            "instructions": INSTRUCTIONS,
            "questions": by_q,
        }
        with open(os.path.join(rev, "notes.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
            f.write("\n")

        # Paket Matematika: PDF visual dari packet no-key mtk2 bila ada; selain itu PNG langsung.
        pdf_hint = None
        if subject == "Matematika" and package == 2:
            cand = os.path.join(ROOT, "claude_input", "retest", "MTK_P2_RETEST_VISUAL.pdf")
            pdf_hint = os.path.relpath(cand, ROOT) if os.path.exists(cand) else None
        print(f"{slug}: {len(copied)} gambar → {os.path.relpath(rev, ROOT)} (notes.json)")
        if pdf_hint:
            print(f"  PDF referensi: {pdf_hint}")


def cmd_ingest(slug, result_path):
    """Tulis side-car dari hasil Claude + rebuild canonical untuk slug tsb."""
    result = json.load(open(result_path, encoding="utf-8"))
    subject, package, raw_dir = slug_meta(slug)
    src_root = os.path.join(ROOT, raw_dir, "images")

    # Validasi: hanya filename yang memang unresolved di canonical, dan ada di disk.
    _, by_q = gather_unresolved(slug)
    allowed = {}
    for nomor, els in by_q.items():
        for el in els:
            allowed[os.path.basename(el["filename"])] = el

    sidecar = load_sidecar(slug)
    accepted, rejected = 0, []
    for fname, entry in result.items():
        fname = os.path.basename(fname)
        if fname not in allowed:
            rejected.append((fname, "bukan elemen unresolved pada slug ini"))
            continue
        latex = entry.get("latex")
        desc = entry.get("description")
        note = entry.get("note")
        if not latex and not desc:
            rejected.append((fname, f"tidak ada latex/description (note={note!r})"))
            continue
        if latex and not isinstance(latex, str):
            rejected.append((fname, "latex bukan string"))
            continue
        if desc and not isinstance(desc, str):
            rejected.append((fname, "description bukan string"))
            continue
        src = os.path.join(src_root, allowed[fname]["filename"])
        if not os.path.exists(src):
            rejected.append((fname, "file sumber hilang"))
            continue
        sidecar[fname] = {"latex": latex or None, "description": desc or None}
        accepted += 1

    os.makedirs(VISION_DIR, exist_ok=True)
    out = os.path.join(VISION_DIR, f"{slug}.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sidecar, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(f"{slug}: side-car {out} — accepted={accepted} rejected={len(rejected)}")
    for fname, why in rejected:
        print(f"  REJECTED {fname}: {why}")

    # Rebuild canonical slug ini (builder membaca side-car)
    from build_canonical_questions import build_package
    for s, subj, pkg, rd in PACKAGES:
        if s == slug:
            doc, _ = build_package(s, subj, pkg, rd)
            ready = sum(1 for q in doc["questions"] if q["transcription_status"] == "ai_ready")
            unres = sum(q["unresolved_count"] for q in doc["questions"])
            print(f"  rebuild: questions={doc['total_questions']} ai_ready={ready} unresolved={unres}")
            break


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        cmd_build(sys.argv[2:])
    elif len(sys.argv) >= 4 and sys.argv[1] == "ingest":
        cmd_ingest(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
