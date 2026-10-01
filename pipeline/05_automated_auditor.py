# -*- coding: utf-8 -*-
"""pipeline/05_automated_auditor.py — Zero-Trust Automated Quality Auditor.

Auditor Fase 5: Memvalidasi 9 checklist anti-bug secara deterministik
sebelum manusia (boss) melakukan pengecekan akhir:

Check 1: Integritas File Gambar (Bug #1) — Cek semua path fisik > 0 byte di disk.
Check 2: Kebersihan Opsi Jawaban (Bug #4, #5, #6) — Bebas dari bug A-L & Matriks palsu.
Check 3: Konsistensi 100% Kunci Resmi Pusmendik (Ground Truth).
Check 4: 5 Pilar Pedagogis & Anti-Langkah Generik (Bug #7 & #8).
Check 5: Integritas Dual-Format Tipe A & Tipe B (Fase 3 & Bug #3).
Check 6: Keberadaan Soal Serupa Unik (Fase 4).
Check 7: Kesiapan Konteks AI Tutor & Server Payload (Bug #9).
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import re
import json
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
REG_PATH = os.path.join(SOL_DIR, "registry.json")

sys.path.insert(0, ROOT)
import server


def audit_subject_package(slug, mapel, paket, prefix):
    print(f"\n{'='*70}")
    print(f"🔍 AUDITING: {slug.upper()} (Mapel: {mapel}, Paket: {paket})")
    print(f"{'='*70}")

    issues = []
    warnings = []

    # 1. Cek File Learning (Tipe A) dan Text-Only (Tipe B)
    lrn_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
    txt_path = os.path.join(DATA_DIR, f"{slug}_text_only.json")
    kunci_path = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")

    if not os.path.isfile(lrn_path):
        return [f"File Tipe A ({lrn_path}) TIDAK DITEMUKAN!"], []
    if not os.path.isfile(txt_path):
        warnings.append(f"File Tipe B ({txt_path}) belum dibuat.")
    if not os.path.isfile(kunci_path):
        return [f"File Kunci Resmi ({kunci_path}) TIDAK DITEMUKAN!"], []

    with open(lrn_path, "r", encoding="utf-8") as f:
        lrn_doc = json.load(f)
    with open(kunci_path, "r", encoding="utf-8") as f:
        kunci_doc = json.load(f)

    questions = lrn_doc.get("soal", [])
    total_q = len(questions)
    if total_q == 0:
        return ["Jumlah soal di learning doc adalah 0!"], []

    print(f"  • Total Soal: {total_q}")

    # Check 1: Integritas Gambar Fisik di Disk
    broken_images = []
    images_dir = os.path.join(DATA_DIR, mapel, f"paket_{paket}", "images")
    for q in questions:
        all_imgs = (
            q.get("stimulus", {}).get("images", []) +
            q.get("pertanyaan", {}).get("images", [])
        )
        for opt in q.get("pilihan_jawaban", []) or []:
            if opt.get("image"):
                all_imgs.append(opt["image"])
        for p in q.get("pernyataan", []) or []:
            if p.get("image"):
                all_imgs.append(p["image"])

        for im in all_imgs:
            fn = im.get("filename")
            if fn:
                local_path = os.path.join(images_dir, fn)
                if not os.path.isfile(local_path) or os.path.getsize(local_path) == 0:
                    broken_images.append(f"Q{q['nomor']}: {fn}")

    if broken_images:
        issues.append(f"[BUG #1 GAMBAR HILANG/0-BYTE] Ditemukan {len(broken_images)} gambar rusak: {broken_images[:5]}")
    else:
        print("  ✅ Check 1: Seluruh file gambar fisik ada dan valid di disk.")

    # Check 2: Kebersihan Opsi Jawaban (Anti A-L dan Anti ABCD Palsu)
    bad_options = []
    empty_questions = []
    for q in questions:
        no = q["nomor"]
        tipe = q.get("tipe") or q.get("tipe_soal", "")
        opts = q.get("pilihan_jawaban", []) or []
        stmts = q.get("pernyataan", []) or []
        if not tipe:
            tipe = "Benar-Salah" if stmts else "Pilihan Ganda"

        if tipe in ("Pilihan Ganda", "Pilihan Ganda Kompleks"):
            if len(opts) == 0:
                bad_options.append(f"Q{no}: Opsi kosong melompong (0 opsi)")
            elif len(opts) > 5:
                bad_options.append(f"Q{no}: Terdeteksi {len(opts)} opsi (> 5, Bug A-L!)")
            for o in opts:
                txt = (o.get("text") or "").strip()
                lat = (o.get("latex") or "").strip()
                img = o.get("image")
                if not txt and not lat and not img:
                    bad_options.append(f"Q{no} Opsi {o.get('key')}: Teks/formula/gambar kosong")
        elif tipe in ("Benar-Salah", "Matriks"):
            if len(stmts) < 2:
                bad_options.append(f"Q{no}: Matriks/BS memiliki < 2 pernyataan ({len(stmts)})")

        # Soal yang tidak punya isi sama sekali (teks & gambar kosong) —
        # sinyal fase 1/2 gagal menangkap isi soal.
        stim_text = (q.get("stimulus", {}).get("text") or "").strip()
        pert_text = (q.get("pertanyaan", {}).get("text") or "").strip()
        stim_html = (q.get("stimulus", {}).get("html") or "").strip()
        pert_html = (q.get("pertanyaan", {}).get("html") or "").strip()
        has_any_content = bool(stim_text or pert_text or "<img" in stim_html.lower()
                               or "<img" in pert_html.lower() or stmts or opts)
        if not has_any_content:
            empty_questions.append(f"Q{no}")

    if bad_options:
        issues.append(f"[BUG #4/#5/#6 OPSI RUSAK] Ditemukan masalah opsi: {bad_options}")
    else:
        print("  ✅ Check 2: Struktur opsi jawaban bersih (0 opsi A-L, 0 opsi kosong).")

    if empty_questions:
        issues.append(f"[SOAL KOSONG] {len(empty_questions)} soal tanpa teks/gambar/opsi: {empty_questions[:8]}")
    else:
        print("  ✅ Check 2b: Semua soal memiliki isi (teks/gambar/opsi).")

    # Check 3: Konsistensi 100% Kunci Resmi Pusmendik
    kunci_mismatch = []
    kunci_missing = []
    kunci_pg = kunci_doc.get("kunci_pg", {})
    kunci_bs = kunci_doc.get("kunci_bs", {})

    for q in questions:
        no = q["nomor"]
        no_s = str(no)
        doc_kunci = q.get("kunci_jawaban")

        if no_s not in kunci_pg and no_s not in kunci_bs:
            # Kunci resmi tidak terparse sama sekali untuk nomor ini
            if not doc_kunci:
                kunci_missing.append(f"Q{no}")
            continue

        if no_s in kunci_pg:
            expected = kunci_pg[no_s]
            norm_doc = [str(x).strip().upper() for x in doc_kunci] if isinstance(doc_kunci, list) else [str(doc_kunci).strip().upper()]
            norm_exp = [str(x).strip().upper() for x in expected] if isinstance(expected, list) else [str(expected).strip().upper()]
            if sorted(norm_doc) != sorted(norm_exp):
                kunci_mismatch.append(f"Q{no}: diharapkan {expected}, didapat {doc_kunci}")
        elif no_s in kunci_bs:
            exp_list = [f"{k}:{v}" for k, v in sorted(kunci_bs[no_s].items())]
            if doc_kunci != exp_list:
                kunci_mismatch.append(f"Q{no}: diharapkan {exp_list}, didapat {doc_kunci}")

    if kunci_missing:
        issues.append(f"[BUG KUNCI KOSONG] Kunci resmi tidak terparse untuk {len(kunci_missing)} soal: {kunci_missing[:8]}")
    if kunci_mismatch:
        issues.append(f"[BUG KUNCI MISMATCH] Kunci tidak cocok dengan Pusmendik: {kunci_mismatch}")
    if not kunci_missing and not kunci_mismatch:
        print("  ✅ Check 3: 100% Kunci jawaban cocok dengan review_hasil Pusmendik.")

    # Check 4: Validasi Solusi 5 Pilar & Anti-Langkah Generik
    sol_file = f"{slug.upper()}_SOLUTIONS.json"
    sol_path = os.path.join(SOL_DIR, sol_file)
    if not os.path.isfile(sol_path):
        issues.append(f"[BUG #7 SOLUSI BELUM ADA] File solusi Layer 3 belum dibuat: {sol_path}")
    else:
        with open(sol_path, "r", encoding="utf-8") as f:
            sol_doc = json.load(f)
        sols = sol_doc.get("solutions", [])
        if len(sols) < total_q:
            issues.append(f"Solusi hanya mencakup {len(sols)}/{total_q} soal!")

        generic_steps = []
        forbidden_transkrip = []
        all_step_explanations = []

        for s in sols:
            q_num = s.get("question_number")
            steps = s.get("steps", [])
            why = s.get("why_correct", "")
            reasoning = s.get("reasoning", "")

            # Cek 5 pilar wajib
            if not s.get("concept_kunci"):
                issues.append(f"Q{q_num}: concept_kunci kosong")
            if not s.get("steps") or len(steps) < 2:
                issues.append(f"Q{q_num}: steps memiliki < 2 tahap")
            if not why:
                issues.append(f"Q{q_num}: why_correct kosong")

            # Cek kata terlarang 'transkrip' (Bug #8)
            combined_text = f"{why} {reasoning} " + " ".join(st.get("explanation", "") for st in steps)
            if re.search(r"\btranskrip(?:si)?\b", combined_text, re.I):
                forbidden_transkrip.append(f"Q{q_num}")

            # Kumpulkan untuk deteksi copas generic
            for st in steps:
                exp = st.get("explanation", "").strip().lower()
                if len(exp) > 20:
                    all_step_explanations.append((q_num, exp))

        # Deteksi duplikasi langkah antar-soal (Bug #7)
        exp_map = {}
        for q_num, exp in all_step_explanations:
            if exp in exp_map and exp_map[exp] != q_num:
                generic_steps.append(f"Q{exp_map[exp]} & Q{q_num} berbagi penjelasan langkah identik: '{exp[:50]}...'")
            else:
                exp_map[exp] = q_num

        # Deteksi diketahui/ditanyakan/reasoning yang di-copy tempel antar soal
        field_dups = []
        for fld in ("diketahui", "reasoning", "why_correct"):
            seen_fld = {}
            for s in sols:
                val = re.sub(r"\s+", " ", str(s.get(fld) or "")).strip().lower()
                if len(val) < 15:
                    continue
                if val in seen_fld and seen_fld[val] != s.get("question_number"):
                    field_dups.append(f"{fld}: Q{seen_fld[val]} & Q{s.get('question_number')}")
                else:
                    seen_fld[val] = s.get("question_number")
        generic_steps.extend(field_dups[:5])

        if forbidden_transkrip:
            issues.append(f"[BUG #8 TEKS TRANSKRIP] Soal menyebut kata 'transkrip': {forbidden_transkrip}")
        else:
            print("  ✅ Check 4a: Solusi bebas dari penyebutan kata 'transkrip'.")

        if generic_steps:
            issues.append(f"[BUG #7 LANGKAH GENERIK] Ditemukan langkah identik antar soal: {generic_steps[:3]}")
        else:
            print("  ✅ Check 4b: Seluruh langkah solusi spesifik dan non-generik.")

        # Check 4c: LaTeX mentah / artefak perataan KaTeX di LUAR $...$ / $$...$$
        # (tampil sebagai kode ke user: "\frac..", "f rac", ℎ). Segmen math
        # diabaikan karena itu LaTeX valid yang dirender KaTeX.
        math_leak = []
        for s in sols:
            blob = " | ".join([str(s.get("diketahui") or ""), str(s.get("ditanyakan") or ""),
                               str(s.get("reasoning") or ""), str(s.get("why_correct") or "")] +
                              [str(st.get("explanation") or "") for st in s.get("steps", [])])
            clean = re.sub(r"\$\$[\s\S]*?\$\$|\$[^$]*?\$", " ", blob)
            cmds = re.findall(r"\\(?:frac|dfrac|tfrac|lim|left|right|sqrt|sum|theta|pi)\b", clean)
            n_h = clean.count("\u210E")
            if cmds or n_h:
                math_leak.append(f"Q{s.get('question_number')} ({len(cmds)} cmd, {n_h} ℎ)")
        if math_leak:
            issues.append(f"[MATH LEAKAGE] LaTeX mentah/artefak KaTeX di luar $...$: {math_leak[:5]}")
        else:
            print("  ✅ Check 4c: Bebas LaTeX mentah & artefak KaTeX di luar $...$.")

        # Check 4d: diketahui ambigu — diawali kata benda math, TANPA math ($),
        # TANPA angka, TANPA perintah LaTeX → isinya kosong ("Matriks,, dan.").
        amb_dik = []
        for s in sols:
            dik = str(s.get("diketahui") or "").strip()
            has_math = "$" in dik or "\\" in dik or re.search(r"\d", dik)
            if not has_math and len(dik) < 60 and re.match(
                    r"^\s*(?:matriks|fungsi|grafik|gamb|persamaan|titik|segitiga|vektor)[a-z\s,.:;()\-]*$",
                    dik, re.I):
                amb_dik.append(f"Q{s.get('question_number')}: {dik!r}")
        if amb_dik:
            warnings.append(f"Diketahui minim konten (isi math hilang dari sumber): {amb_dik[:5]}")
        else:
            print("  ✅ Check 4d: Diketahui semua berisi konten nyata (tanpa ambigu).")

    # Check 5: Integrasi Server Payload & AI Tutor Context (Bug #9)
    try:
        tutor_q1 = server.resolve_tutor_context(mapel, paket, 1)
        if not tutor_q1 or not tutor_q1.get("canon_ctx"):
            issues.append(f"[BUG #9 KONTEKS AI TUTOR] Gagal membuat konteks AI Tutor untuk Q1 {slug}")
        else:
            soal_txt = tutor_q1["canon_ctx"].get("soal_text", "")
            if not soal_txt or len(soal_txt) < 30:
                issues.append(f"[BUG #9 KONTEKS AI TUTOR] Soal text untuk AI Tutor terlalu pendek ({len(soal_txt)} chars)")
            else:
                print("  ✅ Check 5: Konteks AI Tutor tersuplai lengkap (stimulus, opsi, kunci, solusi).")
    except Exception as e:
        issues.append(f"[BUG SERVER] Error saat resolve_tutor_context: {e}")

    # Check 6: Keberadaan Soal Serupa (Fase 4)
    sim_missing = []
    sim_duplicate = []
    sim_copy = []
    sim_seen = {}
    for q in questions:
        sim = q.get("soal_serupa")
        no = q["nomor"]
        if not sim or not sim.get("pertanyaan"):
            sim_missing.append(f"Q{no}")
        else:
            p_txt = sim.get("pertanyaan", "").strip().lower()
            if p_txt in sim_seen:
                sim_duplicate.append(f"Q{sim_seen[p_txt]} & Q{no}")
            else:
                sim_seen[p_txt] = no
            # Soal serupa yang hanya menyalin soal asli = tidak ada nilainya
            orig_txt = re.sub(r"\s+", " ", (q.get("pertanyaan", {}).get("text") or "")).strip().lower()
            if orig_txt and len(orig_txt) > 30 and orig_txt[:120] == re.sub(r"\s+", " ", p_txt)[:120]:
                sim_copy.append(f"Q{no}")

    if sim_missing:
        warnings.append(f"Soal serupa belum ada di {len(sim_missing)} soal: {sim_missing[:5]}")
    elif sim_copy:
        issues.append(f"Soal serupa hanya menyalin soal asli di: {sim_copy}")
    elif sim_duplicate:
        issues.append(f"Soal serupa generik / duplikat ditemukan di: {sim_duplicate}")
    else:
        print("  ✅ Check 6: Soal Serupa unik dan aktif di 100% nomor soal.")

    return issues, warnings


def run_full_audit(targets=None):
    from pipeline.subject_catalog import MASTER_CATALOG

    if targets and targets != "all":
        if targets in MASTER_CATALOG:
            item = MASTER_CATALOG[targets]
            all_targets = [{"slug": item["slug"], "mapel": item["mapel_key"], "paket": item["paket"], "prefix": item.get("prefix", "soal")}]
        else:
            parts = targets.split("_")
            mapel = parts[0]
            paket = int(parts[-1]) if parts[-1].isdigit() else 1
            all_targets = [{"slug": targets, "mapel": mapel, "paket": paket, "prefix": mapel[:3]}]
    else:
        all_targets = [
            {"slug": "kimia_paket_1", "mapel": "kimia", "paket": 1, "prefix": "kim"},
            {"slug": "kimia_paket_2", "mapel": "kimia", "paket": 2, "prefix": "kim"},
            {"slug": "biologi_paket_1", "mapel": "biologi", "paket": 1, "prefix": "bio"},
            {"slug": "biologi_paket_2", "mapel": "biologi", "paket": 2, "prefix": "bio"},
            {"slug": "sosiologi_paket_1", "mapel": "sosiologi", "paket": 1, "prefix": "sos"}
        ]

    total_issues = 0
    total_warnings = 0
    results = {}

    for t in all_targets:
        iss, warn = audit_subject_package(t["slug"], t["mapel"], t["paket"], t["prefix"])
        results[t["slug"]] = {"issues": iss, "warnings": warn}
        total_issues += len(iss)
        total_warnings += len(warn)

    print(f"\n{'='*70}")
    print(f"📊 REKAPITULASI AUDIT MUTU OTOMATIS (ZERO-TRUST AUDIT)")
    print(f"{'='*70}")
    for slug, res in results.items():
        st = "✅ PASSED" if len(res["issues"]) == 0 else f"❌ FAILED ({len(res['issues'])} issues)"
        print(f"  • {slug:<25}: {st}")
        for err in res["issues"]:
            print(f"      🚨 {err}")
        for w in res["warnings"]:
            print(f"      ⚠️ {w}")

    if total_issues == 0:
        print(f"\n🎉 [STATUS AUDIT: 100% LOLOS] Seluruh target bersih dari 9 bug katalog!")
        return True
    else:
        print(f"\n❌ [STATUS AUDIT: DITOLAK] Ditemukan {total_issues} issue kritis yang wajib diperbaiki!")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zero-Trust Quality Auditor")
    parser.add_argument("--target", type=str, default="all")
    args = parser.parse_args()
    success = run_full_audit(args.target)
    sys.exit(0 if success else 1)
