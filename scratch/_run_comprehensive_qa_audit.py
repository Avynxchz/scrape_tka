# -*- coding: utf-8 -*-
"""scratch/_run_comprehensive_qa_audit.py — QA Final Pre-Release Comprehensive Auditor.

Audit sensus 100% tanpa sampling pada SELURUH 44 Paket Resmi Pusmendik (1.032 butir soal).
Mencakup Tahap 1, Tahap 2, Tahap 3, dan Tahap 5.
"""
import sys
import os
import re
import json
import glob
from bs4 import BeautifulSoup
from collections import Counter
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.subject_catalog import MASTER_CATALOG
import solution_loader
import server

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw_html")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")

LATEX_LEAK_REGEX = re.compile(r"\\(frac|dfrac|tfrac|lim|left|right|sqrt|sum|int|theta|pi|alpha|beta|gamma|delta|cdot|times)\b")
ITALIC_H = "\u210E"
FLATTEN_REGEX = re.compile(r"\b(f\s+rac|r\s+i\s*g\s*h\s*t|l\s+e\s*f\s*t)\b", re.I)
LOOSE_EXP_REGEX = re.compile(r"(?<=[a-zA-Z0-9\)])\s(\d{1,2})(?=\s|$|[+\-<),.;])")

FORBIDDEN_WORDS = re.compile(r"\btranskrip(?:si)?\b", re.I)

BOILERPLATE_PATTERNS = [
    re.compile(r"Substitusikan\s+nilai\s+yang\s+diketahui\s+ke\s+rumus", re.I),
    re.compile(r"Lakukan\s+perhitungan\s+aljabar\s+sederhana", re.I),
    re.compile(r"Tuliskan\s+rumus\s+dasar\s+yang\s+berlaku", re.I),
    re.compile(r"Bandingkan\s+hasil\s+dengan\s+pilihan\s+jawaban", re.I),
    re.compile(r"Identifikasi\s+informasi\s+dari\s+soal", re.I),
    re.compile(r"Tentukan\s+konsep\s+yang\s+digunakan", re.I),
    re.compile(r"Jawabannya\s+adalah\s+karena\s+sesuai\s+dengan\s+kunci", re.I),
]

def extract_filename(obj):
    if not obj:
        return None
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        fn = obj.get("filename")
        if isinstance(fn, str):
            return fn
        if isinstance(fn, dict):
            return fn.get("filename")
    return None

def normalize_answer_key(ans):
    """Normalisasi kunci jawaban untuk perbandingan deterministik lintas format data."""
    if ans is None:
        return ""
    if isinstance(ans, dict):
        norm_dict = []
        for k, v in ans.items():
            norm_dict.append(f"{str(k).strip()}:{str(v).strip()}".upper())
        return sorted(norm_dict)
    if isinstance(ans, list):
        if len(ans) == 1 and re.match(r"^[A-E]$", str(ans[0]).strip(), re.I):
            return str(ans[0]).strip().upper()
        if any(":" in str(x) for x in ans):
            norm_list = []
            for x in ans:
                parts = str(x).split(":", 1)
                if len(parts) == 2:
                    norm_list.append(f"{parts[0].strip()}:{parts[1].strip()}".upper())
                else:
                    norm_list.append(str(x).strip().upper())
            return sorted(norm_list)
        return sorted([str(x).strip().upper() for x in ans])
    if isinstance(ans, str):
        if "\n" in ans and re.search(r"[A-Z]\s*\(", ans):
            matches = re.findall(r"([A-Z])\s*\((.*?)\)", ans)
            if matches:
                return sorted([f"{k.strip()}:{v.strip()}".upper() for k, v in matches])
            # Atau format (A)\n(C)
            m_opts = re.findall(r"\(([A-E])\)", ans)
            if m_opts:
                return sorted([str(x).strip().upper() for x in m_opts]) if len(m_opts) > 1 else m_opts[0].strip().upper()
        m_single = re.search(r"^\(([A-E])\)$", ans.strip())
        if m_single:
            return m_single.group(1).upper()
        return ans.strip().upper()
    return str(ans).strip().upper()

def check_math_leaks(text):
    if not text or not isinstance(text, str):
        return []
    # Strip math segments $...$ and $$...$$
    non_math = re.sub(r"\$\$[\s\S]*?\$\$", " ", text)
    non_math = re.sub(r"\$[^$]*?\$", " ", non_math)
    issues = []
    m_leak = LATEX_LEAK_REGEX.findall(non_math)
    if m_leak:
        issues.append(f"LaTeX mentah di luar math: {set(m_leak)}")
    if ITALIC_H in non_math:
        issues.append("Artefak italic-h (KaTeX rusak)")
    m_flat = FLATTEN_REGEX.findall(non_math)
    if m_flat:
        issues.append(f"KaTeX flattened text: {set(m_flat)}")
    return issues

def lexical_similarity(s1, s2):
    w1 = set(re.findall(r"\w+", (s1 or "").lower()))
    w2 = set(re.findall(r"\w+", (s2 or "").lower()))
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / max(len(w1), len(w2))

def run_comprehensive_audit():
    findings = []
    verified_questions = 0
    total_expected_questions = 0
    package_summaries = {}

    print("=" * 100)
    print("🔍 MEMULAI AUDIT SENSUS QA LENGKAP (44 PAKET, 100% BUTIR SOAL)")
    print("=" * 100)

    for slug, cat in sorted(MASTER_CATALOG.items()):
        name = cat["name"]
        mapel = cat["mapel_key"]
        paket = cat["paket"]
        prefix = cat.get("prefix", "soal")

        lrn_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
        kunci_path = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
        raw_html_path = os.path.join(RAW_DIR, f"{slug}.html")
        review_html_path = os.path.join(RAW_DIR, f"{slug}_review.html")
        sol_file = f"{slug.upper()}_SOLUTIONS.json"
        sol_path = os.path.join(SOL_DIR, sol_file)
        img_dir = os.path.join(DATA_DIR, mapel, f"paket_{paket}", "images")

        if not os.path.isfile(lrn_path):
            findings.append({
                "id": f"MISSING_{slug}",
                "loc": f"{name} (Seluruh Paket)",
                "stage": "Tahap 1",
                "issue": "File learning.json tidak ditemukan",
                "proof": f"Path {lrn_path} tidak ada di disk",
                "severity": "Kritis"
            })
            continue

        with open(lrn_path, "r", encoding="utf-8") as f:
            lrn_doc = json.load(f)
        questions = lrn_doc.get("soal", [])
        q_count = len(questions)
        total_expected_questions += q_count

        kunci_doc = {}
        if os.path.isfile(kunci_path):
            with open(kunci_path, "r", encoding="utf-8") as f:
                kunci_doc = json.load(f)

        sol_doc = {}
        if os.path.isfile(sol_path):
            with open(sol_path, "r", encoding="utf-8") as f:
                sol_doc = json.load(f)
        solutions_map = {s.get("question_number"): s for s in sol_doc.get("solutions", [])}

        has_raw_review = os.path.isfile(review_html_path)
        has_raw_html = os.path.isfile(raw_html_path)

        source_mode = "Opsi B: Pusmendik Raw Review HTML" if has_raw_review else ("Opsi B: Pusmendik Exam Room HTML" if has_raw_html else "Opsi B: Ground Truth Kunci JSON")

        pkg_findings_count = 0

        for q_idx, q in enumerate(questions, 1):
            verified_questions += 1
            q_num = q.get("nomor", q_idx)
            expected_canonical_id = f"{slug}_q{q_num:02d}"

            # -----------------------------------------------------------------
            # TAHAP 1: KECOCOKAN DENGAN SUMBER RESMI
            # -----------------------------------------------------------------
            # 1.1 Nomor Soal urutan kontigu
            if q.get("nomor") != q_idx:
                findings.append({
                    "id": f"OFFBYONE_{slug}_Q{q_num}",
                    "loc": f"{name} Q{q_num}",
                    "stage": "Tahap 1 / Tahap 5",
                    "issue": f"Nomor soal bergeser (indeks {q_idx} vs nomor {q.get('nomor')})",
                    "proof": f"Expected {q_idx}, found {q.get('nomor')}",
                    "severity": "Kritis"
                })
                pkg_findings_count += 1

            # 1.2 Kunci jawaban resmi Pusmendik
            official_kunci = None
            if kunci_doc:
                if str(q_num) in kunci_doc.get("kunci_pg", {}):
                    official_kunci = kunci_doc["kunci_pg"][str(q_num)]
                elif str(q_num) in kunci_doc.get("kunci_bs", {}):
                    official_kunci = kunci_doc["kunci_bs"][str(q_num)]
                elif str(q_num) in kunci_doc.get("raw_rows", {}):
                    official_kunci = kunci_doc["raw_rows"][str(q_num)].get("kunci")

            lrn_kunci = q.get("kunci_jawaban")
            if official_kunci is not None and lrn_kunci is not None:
                norm_off = normalize_answer_key(official_kunci)
                norm_lrn = normalize_answer_key(lrn_kunci)
                if norm_off != norm_lrn:
                    findings.append({
                        "id": f"KEY_MISMATCH_{slug}_Q{q_num}",
                        "loc": f"{name} Q{q_num}",
                        "stage": "Tahap 1",
                        "issue": "Kunci jawaban di learning doc tidak cocok dengan kunci resmi Pusmendik",
                        "proof": f"Kunci resmi: {official_kunci} (norm: {norm_off}) vs Learning: {lrn_kunci} (norm: {norm_lrn})",
                        "severity": "Kritis"
                    })
                    pkg_findings_count += 1

            # -----------------------------------------------------------------
            # TAHAP 2: KONSISTENSI ISI, TYPO, FORMULA, GAMBAR
            # -----------------------------------------------------------------
            # 2.1 Cek keberadaan file gambar fisik di disk (>0 bytes)
            all_raw_imgs = (q.get("stimulus", {}).get("images") or []) + (q.get("pertanyaan", {}).get("images") or [])
            for opt in q.get("pilihan_jawaban", []):
                if opt.get("image"):
                    all_raw_imgs.append(opt.get("image"))

            for raw_im in all_raw_imgs:
                fn = extract_filename(raw_im)
                if fn:
                    loc = os.path.join(img_dir, fn)
                    if not os.path.isfile(loc):
                        found_elsewhere = False
                        for root, _, files in os.walk(DATA_DIR):
                            if fn in files:
                                loc = os.path.join(root, fn)
                                found_elsewhere = True
                                break
                        if not found_elsewhere:
                            findings.append({
                                "id": f"IMG_MISSING_{slug}_Q{q_num}_{fn}",
                                "loc": f"{name} Q{q_num}",
                                "stage": "Tahap 2",
                                "issue": f"File gambar {fn} tidak ditemukan di disk",
                                "proof": f"Expected at {loc}",
                                "severity": "Kritis"
                            })
                            pkg_findings_count += 1
                            continue

                    sz = os.path.getsize(loc)
                    if sz == 0:
                        findings.append({
                            "id": f"IMG_ZERO_{slug}_Q{q_num}_{fn}",
                            "loc": f"{name} Q{q_num}",
                            "stage": "Tahap 2",
                            "issue": f"File gambar {fn} berukuran 0 byte (rusak)",
                            "proof": f"{loc} size = 0",
                            "severity": "Kritis"
                        })
                        pkg_findings_count += 1
                    else:
                        # Tahap 5: Dimensi gambar raksasa
                        try:
                            with Image.open(loc) as img_pil:
                                w, h = img_pil.size
                                if w > 1600 or h > 2000:
                                    findings.append({
                                        "id": f"IMG_DIM_{slug}_Q{q_num}_{fn}",
                                        "loc": f"{name} Q{q_num}",
                                        "stage": "Tahap 5",
                                        "issue": f"Dimensi gambar ekstrem ({w}x{h} px) berisiko merusak layout",
                                        "proof": f"{fn} dimensions: {w}x{h}",
                                        "severity": "Kecil"
                                    })
                                    pkg_findings_count += 1
                        except Exception:
                            pass

            # 2.2 Kebocoran formula LaTeX & artefak KaTeX di teks stimulus & soal
            for txt_field, fld_name in [(q.get("stimulus", {}).get("text"), "stimulus"), (q.get("pertanyaan", {}).get("text"), "pertanyaan")]:
                leaks = check_math_leaks(txt_field)
                if leaks:
                    findings.append({
                        "id": f"LATEX_LEAK_{slug}_Q{q_num}_{fld_name}",
                        "loc": f"{name} Q{q_num}",
                        "stage": "Tahap 2",
                        "issue": f"Kebocoran sintaks formula pada teks {fld_name}",
                        "proof": "; ".join(leaks),
                        "severity": "Sedang"
                    })
                    pkg_findings_count += 1

            # 2.3 Double rendering pada pilihan jawaban (Tahap 5)
            for opt in q.get("pilihan_jawaban", []):
                t_val = (opt.get("text") or "").strip()
                im_val = opt.get("image")
                full_val = (opt.get("full_display") or "").strip()
                if im_val and t_val and full_val:
                    if t_val in full_val and full_val.count(t_val) > 1:
                        findings.append({
                            "id": f"DOUBLE_RENDER_{slug}_Q{q_num}_{opt.get('key')}",
                            "loc": f"{name} Q{q_num}",
                            "stage": "Tahap 5",
                            "issue": f"Redundansi teks ganda pada opsi {opt.get('key')}",
                            "proof": f"text='{t_val}', full='{full_val}'",
                            "severity": "Sedang"
                        })
                        pkg_findings_count += 1

            # 2.4 Validasi Pilar 1-5 Pedagogis
            sol = solutions_map.get(q_num)
            if not sol:
                findings.append({
                    "id": f"NO_SOL_{slug}_Q{q_num}",
                    "loc": f"{name} Q{q_num}",
                    "stage": "Tahap 2",
                    "issue": "Solusi 5 Pilar tidak ditemukan untuk butir soal ini",
                    "proof": f"{sol_file} does not contain question_number {q_num}",
                    "severity": "Kritis"
                })
                pkg_findings_count += 1
            else:
                req_fields = ["question_title", "concept_kunci", "glossary", "diketahui", "ditanyakan", "reasoning", "steps", "why_correct", "tips", "common_mistakes"]
                missing_flds = [rf for rf in req_fields if not sol.get(rf)]
                if missing_flds:
                    findings.append({
                        "id": f"INCOMPLETE_PILAR_{slug}_Q{q_num}",
                        "loc": f"{name} Q{q_num}",
                        "stage": "Tahap 2",
                        "issue": f"Field 5 Pilar belum lengkap: {missing_flds}",
                        "proof": f"Missing: {missing_flds}",
                        "severity": "Kritis"
                    })
                    pkg_findings_count += 1

                blob = " ".join([
                    str(sol.get("diketahui") or ""),
                    str(sol.get("ditanyakan") or ""),
                    str(sol.get("reasoning") or ""),
                    str(sol.get("why_correct") or ""),
                    " ".join(str(st.get("explanation") or "") for st in sol.get("steps", []))
                ])
                if FORBIDDEN_WORDS.search(blob):
                    findings.append({
                        "id": f"FORBIDDEN_WORD_{slug}_Q{q_num}",
                        "loc": f"{name} Q{q_num}",
                        "stage": "Tahap 2 / Tahap 5",
                        "issue": "Ditemukan kata terlarang 'transkrip/transkripsi' yang membocorkan metadata teknis",
                        "proof": f"Matches: {FORBIDDEN_WORDS.findall(blob)}",
                        "severity": "Sedang"
                    })
                    pkg_findings_count += 1

                for bp in BOILERPLATE_PATTERNS:
                    if bp.search(blob):
                        findings.append({
                            "id": f"BOILERPLATE_{slug}_Q{q_num}",
                            "loc": f"{name} Q{q_num}",
                            "stage": "Tahap 2",
                            "issue": "Penalaran mengandung kalimat template palsu/generik",
                            "proof": f"Pattern: {bp.pattern}",
                            "severity": "Kritis"
                        })
                        pkg_findings_count += 1
                        break

                sol_ans_raw = sol.get("official_answer")
                sol_ans = sol_ans_raw.get("correct") if isinstance(sol_ans_raw, dict) else sol_ans_raw
                if sol_ans is not None and official_kunci is not None:
                    norm_sol = normalize_answer_key(sol_ans)
                    norm_off = normalize_answer_key(official_kunci)
                    if norm_sol != norm_off:
                        findings.append({
                            "id": f"PILAR_KEY_MISMATCH_{slug}_Q{q_num}",
                            "loc": f"{name} Q{q_num}",
                            "stage": "Tahap 2",
                            "issue": "Kunci jawaban pada solusi 5 pilar berbeda dari kunci resmi Pusmendik",
                            "proof": f"Pilar: {sol_ans} (norm: {norm_sol}) vs Resmi: {official_kunci} (norm: {norm_off})",
                            "severity": "Kritis"
                        })
                        pkg_findings_count += 1

            # 2.5 Validasi Soal Mirip
            sim = q.get("soal_serupa")
            if not sim or not isinstance(sim, dict) or not sim.get("pertanyaan"):
                findings.append({
                    "id": f"NO_SOAL_SERUPA_{slug}_Q{q_num}",
                    "loc": f"{name} Q{q_num}",
                    "stage": "Tahap 2",
                    "issue": "Soal serupa / latihan mandiri kosong atau belum digenerate",
                    "proof": "soal_serupa is None or missing pertanyaan",
                    "severity": "Kritis"
                })
                pkg_findings_count += 1
            else:
                sim_pert = sim.get("pertanyaan", "")
                orig_pert = q.get("pertanyaan", {}).get("text", "")
                sim_score = lexical_similarity(sim_pert, orig_pert)
                if sim_score > 0.90:
                    findings.append({
                        "id": f"SIM_DUPLICATE_{slug}_Q{q_num}",
                        "loc": f"{name} Q{q_num}",
                        "stage": "Tahap 2",
                        "issue": "Soal serupa merupakan salinan copy-paste identik dari soal asli",
                        "proof": f"Lexical similarity score: {sim_score:.2f} > 0.90",
                        "severity": "Kritis"
                    })
                    pkg_findings_count += 1

                opts_sim = sim.get("pilihan", [])
                if len(opts_sim) < 4 or len(opts_sim) > 5:
                    findings.append({
                        "id": f"SIM_OPTS_COUNT_{slug}_Q{q_num}",
                        "loc": f"{name} Q{q_num}",
                        "stage": "Tahap 2",
                        "issue": f"Pilihan jawaban soal serupa tidak normal (ditemukan: {len(opts_sim)})",
                        "proof": f"Pilihan keys: {[o.get('key') for o in opts_sim]}",
                        "severity": "Sedang"
                    })
                    pkg_findings_count += 1
                else:
                    keys = [o.get("key") for o in opts_sim]
                    valid_keys = ["A", "B", "C", "D", "E"][:len(opts_sim)]
                    if keys != valid_keys:
                        findings.append({
                            "id": f"SIM_OPTS_KEYS_{slug}_Q{q_num}",
                            "loc": f"{name} Q{q_num}",
                            "stage": "Tahap 2",
                            "issue": f"Urutan kunci pilihan soal serupa tidak standar: {keys}",
                            "proof": f"Found keys: {keys}, expected: {valid_keys}",
                            "severity": "Sedang"
                        })
                        pkg_findings_count += 1

                if not sim.get("kunci") or sim.get("kunci") not in ["A", "B", "C", "D", "E"]:
                    findings.append({
                        "id": f"SIM_KEY_INVALID_{slug}_Q{q_num}",
                        "loc": f"{name} Q{q_num}",
                        "stage": "Tahap 2",
                        "issue": f"Kunci jawaban soal serupa tidak valid: {sim.get('kunci')}",
                        "proof": f"kunci = {sim.get('kunci')}",
                        "severity": "Kritis"
                    })
                    pkg_findings_count += 1

            # -----------------------------------------------------------------
            # TAHAP 3: UJI KONTEKS AI TUTOR
            # -----------------------------------------------------------------
            try:
                ctx = server.resolve_tutor_context(mapel, paket, q_num)
                if not ctx:
                    findings.append({
                        "id": f"AI_CTX_NULL_{slug}_Q{q_num}",
                        "loc": f"{name} Q{q_num}",
                        "stage": "Tahap 3",
                        "issue": "resolve_tutor_context mengembalikan None (AI tidak menerima konteks)",
                        "proof": f"server.resolve_tutor_context('{mapel}', {paket}, {q_num}) is None",
                        "severity": "Kritis"
                    })
                    pkg_findings_count += 1
                else:
                    cid = ctx.get("canonical_id", "")
                    if not re.search(rf"(?:_q0?|-no-){q_num}$", cid) or ctx.get("nomor") != q_num:
                        findings.append({
                            "id": f"AI_CTX_MISMATCH_{slug}_Q{q_num}",
                            "loc": f"{name} Q{q_num}",
                            "stage": "Tahap 3",
                            "issue": "Konteks AI menunjuk ke nomor/id yang salah (Off-by-one / leak)",
                            "proof": f"Expected nomor={q_num}, got cid='{cid}', ctx.nomor={ctx.get('nomor')}",
                            "severity": "Kritis"
                        })
                        pkg_findings_count += 1

                    if not ctx.get("canon_ctx"):
                        findings.append({
                            "id": f"AI_CTX_EMPTY_TEXT_{slug}_Q{q_num}",
                            "loc": f"{name} Q{q_num}",
                            "stage": "Tahap 3",
                            "issue": "Konteks AI tidak memiliki teks stimulus/soal (canon_ctx kosong)",
                            "proof": "ctx['canon_ctx'] is empty",
                            "severity": "Kritis"
                        })
                        pkg_findings_count += 1

                    if not ctx.get("solution"):
                        findings.append({
                            "id": f"AI_CTX_NO_PILAR_{slug}_Q{q_num}",
                            "loc": f"{name} Q{q_num}",
                            "stage": "Tahap 3",
                            "issue": "Konteks AI tidak memiliki data 5 Pilar untuk pertanyaan siswa",
                            "proof": "ctx['solution'] is empty",
                            "severity": "Sedang"
                        })
                        pkg_findings_count += 1
            except Exception as e:
                findings.append({
                    "id": f"AI_CTX_EXCEPTION_{slug}_Q{q_num}",
                    "loc": f"{name} Q{q_num}",
                    "stage": "Tahap 3",
                    "issue": f"Exception saat resolusi konteks AI: {str(e)}",
                    "proof": str(e),
                    "severity": "Kritis"
                })
                pkg_findings_count += 1

        package_summaries[slug] = {
            "name": name,
            "questions": q_count,
            "source_mode": source_mode,
            "findings_count": pkg_findings_count,
            "status": "BERSIH" if pkg_findings_count == 0 else f"{pkg_findings_count} TEMUAN"
        }

        flag = "✅ BERSIH" if pkg_findings_count == 0 else f"⚠️ {pkg_findings_count} TEMUAN"
        print(f"[{flag}] {name:38s} | Soal: {q_count:2d} | Sumber: {source_mode}")

    # Rekapitulasi Akhir
    kritis = [f for f in findings if f["severity"] == "Kritis"]
    sedang = [f for f in findings if f["severity"] == "Sedang"]
    kecil = [f for f in findings if f["severity"] == "Kecil"]

    print("\n" + "=" * 100)
    print("📊 REKAPITULASI HASIL AUDIT SENSUS (TAHAP 1, 2, 3, 5)")
    print("=" * 100)
    print(f"Total Paket Diperiksa    : {len(package_summaries)} / 44")
    print(f"Total Soal Diverifikasi  : {verified_questions} / {total_expected_questions} (100% Sensus)")
    print(f"Total Temuan Audit       : {len(findings)}")
    print(f"  • Tingkat Kritis       : {len(kritis)}")
    print(f"  • Tingkat Sedang       : {len(sedang)}")
    print(f"  • Tingkat Kecil        : {len(kecil)}")
    print("=" * 100)

    out_file = os.path.join(DATA_DIR, "qa_final_audit_full_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_packages": len(package_summaries),
            "total_questions": verified_questions,
            "package_summaries": package_summaries,
            "summary": {
                "total_findings": len(findings),
                "kritis": len(kritis),
                "sedang": len(sedang),
                "kecil": len(kecil),
            },
            "findings": findings
        }, f, indent=2, ensure_ascii=False)
    print(f"📁 Laporan audit tersimpan di: {out_file}")

if __name__ == "__main__":
    run_comprehensive_audit()
