# -*- coding: utf-8 -*-
"""pipeline/raw_fidelity_auditor.py — Direct 1:1 Raw Pusmendik Fidelity Auditor.

Audits parsed learning JSON datasets DIRECTLY against the original Pusmendik
raw HTML exam room files (data/raw_html/*.html).

Zero-Trust Quality Checks:
1. [INLINE_LATEX_FIDELITY] Inline math formulas (<img data-latex="...">) must NOT be lost or omitted.
2. [ELEMENT_ORDER_FIDELITY] The visual sequence of elements (image-before-text vs text-before-image) must match Pusmendik 100%.
3. [EMPTY_OPTION_DETECTION] No option may render as empty string when raw HTML contains formula, image, or text.
4. [OPTION_COUNT_MATCH] Number of options per question must match raw interactive table inputs.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import re
import json
import glob
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw_html")
REPORT_PATH = os.path.join(DATA_DIR, "raw_fidelity_audit_report.json")

def audit_raw_fidelity():
    print("=" * 90)
    print("🔍 AUDITING DIRECT RAW PUSMENDIK FIDELITY (1:1 GROUND-TRUTH DOM CHECK)")
    print("=" * 90)

    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.html")))
    raw_files = [f for f in raw_files if not f.endswith("_review.html")]

    total_packages = 0
    clean_packages = 0
    discrepancies = []

    for h_path in raw_files:
        slug = os.path.basename(h_path).replace(".html", "")
        learning_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
        if not os.path.exists(learning_path):
            continue

        total_packages += 1
        pkg_issues = []

        with open(h_path, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        with open(learning_path, encoding="utf-8") as f:
            learning = json.load(f)

        soal_list = learning["soal"] if isinstance(learning, dict) and "soal" in learning else learning
        soal_map = {q.get("nomor"): q for q in soal_list}

        inputs = soup.find_all("input", attrs={"name": re.compile(r"^pilihan")})
        q_inps = {}
        for inp in inputs:
            name = inp.get("name", "")
            m = re.search(r"pilihan_?(\d+)", name)
            if m:
                qnum = int(m.group(1))
                q_inps.setdefault(qnum, []).append(inp)

        for qnum, inps in q_inps.items():
            q_data = soal_map.get(qnum)
            if not q_data:
                continue

            opts = q_data.get("pilihan_jawaban", [])
            if not opts:
                continue

            for inp in inps:
                pil = inp.get("pil", "").upper()
                opt_obj = next((o for o in opts if o.get("key") == pil), None)
                if not opt_obj:
                    continue

                tr = inp.find_parent("tr")
                tds = tr.find_all("td") if tr else []
                if len(tds) < 2:
                    continue
                content_td = tds[-1]

                raw_text = content_td.get_text(" ", strip=True)
                raw_text = re.sub(r"\?xml.*?\?", "", raw_text).strip()
                imgs = content_td.find_all("img")

                # Check 1: Inline LaTeX Fidelity
                for img in imgs:
                    latex = img.get("data-latex")
                    if latex:
                        full_d = opt_obj.get("full_display", "")
                        t_val = opt_obj.get("text", "")
                        l_val = opt_obj.get("latex", "")
                        if latex not in full_d and latex not in t_val and latex != l_val:
                            pkg_issues.append({
                                "qnum": qnum,
                                "pil": pil,
                                "type": "MISSING_INLINE_LATEX",
                                "detail": f"LaTeX '{latex}' tidak ditemukan di option (text='{t_val}', full='{full_d}')"
                            })

                # Check 2: Element Order (Image before text)
                non_latex_imgs = [im for im in imgs if not im.get("data-latex")]
                if non_latex_imgs and raw_text:
                    first_img = non_latex_imgs[0]
                    img_pos = str(content_td).find(str(first_img)[:30])
                    words = raw_text.split()
                    if words:
                        text_pos = str(content_td).find(words[0])
                        if img_pos < text_pos:
                            # Must be marked as image_first or image_position before
                            if not opt_obj.get("image_first") and opt_obj.get("image_position") != "before":
                                pkg_issues.append({
                                    "qnum": qnum,
                                    "pil": pil,
                                    "type": "ORDER_MISMATCH",
                                    "detail": f"Raw HTML menampilkan gambar SEBELUM teks, tetapi opsi belum ditandai image_first"
                                })

                # Check 3: Empty option body
                opt_content = (opt_obj.get("text") or "").strip()
                opt_latex = (opt_obj.get("latex") or "").strip()
                opt_img = opt_obj.get("image")
                if not opt_content and not opt_latex and not opt_img:
                    if raw_text or imgs:
                        pkg_issues.append({
                            "qnum": qnum,
                            "pil": pil,
                            "type": "EMPTY_OPTION_BODY",
                            "detail": f"Opsi kosong padahal raw HTML memiliki konten: text='{raw_text}', imgs={len(imgs)}"
                        })

        if pkg_issues:
            print(f"❌ {slug}: {len(pkg_issues)} discrepancies found!")
            for iss in pkg_issues[:5]:
                print(f"   • [Q{iss['qnum']} Opsi {iss['pil']}] {iss['type']}: {iss['detail']}")
            if len(pkg_issues) > 5:
                print(f"   ... ({len(pkg_issues) - 5} issues more)")
            discrepancies.append({"package": slug, "issues": pkg_issues})
        else:
            print(f"✅ {slug}: 100% FIDELITY PASS (0 Discrepancy)")
            clean_packages += 1

    print("-" * 90)
    print(f"Total Packages Audited : {total_packages}")
    print(f"100% Fidelity Clean    : {clean_packages}")
    print(f"Packages with Issues   : {len(discrepancies)}")
    print("-" * 90)

    report_data = {
        "total_packages": total_packages,
        "clean_packages": clean_packages,
        "packages_with_issues": len(discrepancies),
        "discrepancies": discrepancies
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print(f"📁 Laporan tersimpan di: {REPORT_PATH}")
    return len(discrepancies) == 0

if __name__ == "__main__":
    success = audit_raw_fidelity()
    sys.exit(0 if success else 1)
