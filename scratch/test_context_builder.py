# -*- coding: utf-8 -*-
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from server import learning_for, canonical_for, format_kunci_display, format_visual_context

def test_builder(canon, lrn_q):
    vc = canon.get("visual_context", {}) if canon else {}
    parts = []

    stim_text = (
        (canon.get("stimulus_text") if canon else "")
        or (canon.get("stimulus") if canon else "")
        or (lrn_q.get("stimulus", {}).get("text") if lrn_q else "")
    )
    if stim_text and stim_text.strip():
        parts.append("[STIMULUS]\n" + stim_text.strip())

    q_text = (
        (canon.get("question_text") if canon else "")
        or (canon.get("question") if canon else "")
        or (lrn_q.get("pertanyaan", {}).get("text") if lrn_q else "")
    )
    if q_text and q_text.strip():
        parts.append("[SOAL]\n" + q_text.strip())

    statements = (lrn_q.get("pernyataan") if lrn_q else None) or (canon.get("statements") if canon else None)
    options = (lrn_q.get("pilihan_jawaban") if lrn_q else None) or (canon.get("options") if canon else None)

    if statements:
        st_lines = []
        for s in statements:
            k = s.get("key", "")
            txt = s.get("text") or s.get("display") or ""
            img_note = f" [Gambar: {s['image']['filename']}]" if s.get("image") else ""
            st_lines.append(f"  {k}. {txt}{img_note}")
        parts.append("[PERNYATAAN / ITEM KONDISI]\n" + "\n".join(st_lines))
    elif options:
        opt_lines = []
        if isinstance(options, dict):
            for k, v in options.items():
                opt_lines.append(f"  {k}. {v}")
        elif isinstance(options, list):
            for opt in options:
                k = opt.get("key", "")
                txt = opt.get("full_display") or opt.get("text") or (f"${opt['latex']}$" if opt.get("latex") else "")
                img_note = f" [Gambar: {opt['image']['filename']}]" if opt.get("image") else ""
                opt_lines.append(f"  {k}. {txt}{img_note}")
        if opt_lines:
            parts.append("[OPSI JAWABAN]\n" + "\n".join(opt_lines))

    imgs = []
    if lrn_q:
        imgs = lrn_q.get("stimulus", {}).get("images", []) + lrn_q.get("pertanyaan", {}).get("images", [])
    img_lines = []
    for im in imgs:
        fn = im.get("filename", "")
        img_lines.append(f"- Diagram gambar: {fn}")
    visual_text = format_visual_context(vc)
    if img_lines:
        visual_desc = "\n".join(img_lines)
        if visual_text and visual_text != "Soal ini tidak memiliki elemen visual.":
            visual_desc += "\n" + visual_text
        parts.append("[KONTEKS VISUAL / GAMBAR SOAL]\n" + visual_desc)
    elif visual_text:
        parts.append("[KONTEKS VISUAL]\n" + visual_text)

    kunci_disp = format_kunci_display(lrn_q or {})
    parts.append(f"[KUNCI RESMI] {kunci_disp}")

    if lrn_q and lrn_q.get("pembahasan"):
        pb = lrn_q["pembahasan"]
        if pb.get("diketahui"):
            parts.append(f"[INFORMASI DIKETAHUI DARI DIAGRAM & SOAL]\n{pb['diketahui']}")

    return "\n\n".join(parts)

for s, p, n in [('fisika', 1, 1), ('fisika', 1, 7), ('geografi', 2, 2)]:
    c = canonical_for(s, p, n)
    l = learning_for(s, p, n)
    res = test_builder(c, l)
    print(f"\n==================== {s.upper()} P{p} Q{n} ====================")
    print(res)
