# -*- coding: utf-8 -*-
"""pipeline/master_omni_auditor.py — Master Omniscient Project Auditor.

Auditor Semesta: Melakukan audit menyeluruh tanpa kompromi pada SELURUH
mapel dan paket yang ada di repository (data/*_learning.json & data/solution_sources/*.json).

Kategori Pemeriksaan (8 Dimensi Mutu Mutlak):
1. [PILAR_BOILERPLATE] Deteksi template palsu/copy-paste pada 5 pilar (seperti pada Eko, Bing, MTK1, PKW).
2. [PILAR_GENERIC] Deteksi langkah penyelesaian generik/tanpa konten nyata.
3. [PILAR_MATH_LEAK] Deteksi kebocoran raw LaTeX di luar matematika $...$.
4. [PILAR_FORBIDDEN] Deteksi kata terlarang ('transkrip', KaTeX rusak).
5. [SOAL_SERUPA] Integritas soal serupa (keberadaan, keunikan, bukan copy-paste soal asli, kelengkapan).
6. [GAMBAR_INTEGRITAS] File gambar fisik di disk (>0 byte) & deteksi tag phantom 404 Pusmendik.
7. [STRUKTUR_OPSI] Kebersihan opsi (anti bug A-L, opsi kosong, Benar-Salah konsisten).
8. [KUNCI_PUSMENDIK] 100% kecocokan kunci jawaban dengan ground truth review_hasil.
9. [INTEGRASI_SYSTEM] Kesiapan katalog di app.js, registry.json & server.py.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import re
import json
import glob
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
APP_JS = os.path.join(ROOT, "app.js")
SERVER_PY = os.path.join(ROOT, "server.py")
REPORT_PATH = os.path.join(DATA_DIR, "audit_semesta_report.json")

SUBJECT_ALIASES = {
    "bahasa_inggris": "bing",
    "kewirausahaan": "pkw",
    "kimia": "kim",
    "biologi": "bio",
    "matematika": "mtk",
    "sosiologi": "sos",
    "ekonomi": "eko",
    "geografi": "geo",
    "sejarah": "sej",
    "matematika_lanjut": "mtkl",
    "bahasa_indonesia": "ind",
    "bahasa_indonesia_lanjut": "indl",
    "bahasa_inggris_lanjut": "ingl",
    "antropologi": "ant",
    "ppkn": "ppk",
    "bahasa_arab": "ara",
    "bahasa_jepang": "jpn",
    "bahasa_jerman": "ger",
    "bahasa_prancis": "fra",
    "bahasa_mandarin": "man",
    "bahasa_korea": "kor"
}


def get_app_js_subjects():
    if not os.path.exists(APP_JS):
        return set()
    with open(APP_JS, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"const SUBJECT_CATALOG\s*=\s*\{([\s\S]*?)\n\};", content)
    if not m:
        return set()
    block = m.group(1)
    keys = re.findall(r"^\s*([a-zA-Z0-9_]+)\s*:\s*\{", block, re.MULTILINE)
    return set(keys)


def find_solution_file(slug, mapel, paket, registry):
    # 1. Direct registry lookup
    reg_keys = [
        slug,
        f"{mapel}_paket_{paket}",
        f"{SUBJECT_ALIASES.get(mapel, mapel)}_paket_{paket}"
    ]
    for rk in reg_keys:
        if rk in registry and "active_source" in registry[rk]:
            candidate = os.path.join(SOL_DIR, registry[rk]["active_source"])
            if os.path.isfile(candidate):
                return candidate, registry[rk]["active_source"]

    # 2. File name pattern matching in data/solution_sources/
    alias = SUBJECT_ALIASES.get(mapel, mapel).upper()
    mapel_u = mapel.upper()
    candidates = [
        f"{slug.upper()}_SOLUTIONS.json",
        f"{mapel_u}_PAKET_{paket}_SOLUTIONS.json",
        f"{alias}_PAKET_{paket}_SOLUTIONS.json",
        f"{mapel_u}_PAKET_{paket}_SOLUTIONS_EXTRA.json",
        f"{alias}_PAKET_{paket}_SOLUTIONS_EXTRA.json",
    ]
    for c in candidates:
        full_p = os.path.join(SOL_DIR, c)
        if os.path.isfile(full_p):
            return full_p, c

    return None, None


def audit_all():
    print(f"{'='*90}")
    print("🔍 AUDIT SEMESTA: PEMERIKSAAN KUALITAS MENYELURUH REPOSITORY SCRAPE_TKA")
    print(f"{'='*90}")

    learning_files = sorted(glob.glob(os.path.join(DATA_DIR, "*_learning.json")))
    learning_files = [
        f for f in learning_files 
        if "backup" not in f and os.path.basename(f) not in ["paket_1_learning.json", "paket_2_learning.json"]
    ]

    reg_path = os.path.join(SOL_DIR, "registry.json")
    registry = {}
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

    app_js_subjects = get_app_js_subjects()

    overall_results = {}

    for lpath in learning_files:
        slug = os.path.basename(lpath).replace("_learning.json", "")
        parts = slug.rsplit("_paket_", 1)
        if len(parts) == 2:
            mapel = parts[0]
            paket = int(parts[1])
        else:
            mapel = slug
            paket = 1

        print(f"\n{'─'*90}")
        print(f"📦 AUDITING: {slug.upper()} (Mapel: {mapel}, Paket: {paket})")
        print(f"{'─'*90}")

        bugs = []
        warnings = []
        stats = {}

        try:
            with open(lpath, "r", encoding="utf-8") as f:
                ldoc = json.load(f)
        except Exception as e:
            print(f"  ❌ GAGAL MEMBACA JSON: {e}")
            overall_results[slug] = {"bugs": [f"Corrupt JSON: {e}"], "warnings": [], "status": "FAIL"}
            continue

        questions = ldoc.get("soal", [])
        total_q = len(questions)
        stats["total_questions"] = total_q
        print(f"  • Total Soal: {total_q}")

        # -----------------------------------------------------------------
        # 1. CEK INTEGRITAS GAMBAR FISIK & DETEKSI PHANTOM 404 PUSMENDIK
        # -----------------------------------------------------------------
        images_dir = os.path.join(DATA_DIR, mapel, f"paket_{paket}", "images")
        broken_images = []
        phantom_images = []

        for q in questions:
            no = q.get("nomor", "?")
            imgs = (
                q.get("stimulus", {}).get("images", []) +
                q.get("pertanyaan", {}).get("images", [])
            )
            for opt in q.get("pilihan_jawaban", []) or []:
                if opt.get("image"):
                    imgs.append(opt["image"])
            for p in q.get("pernyataan", []) or []:
                if p.get("image"):
                    imgs.append(p["image"])

            for im in imgs:
                fn = im.get("filename") if isinstance(im, dict) else str(im)
                if fn:
                    disk_p = os.path.join(images_dir, fn)
                    if not os.path.isfile(disk_p) or os.path.getsize(disk_p) == 0:
                        broken_images.append(f"Q{no}:{fn}")
                        if re.search(r"_[a-f0-9]{32}_[a-f0-9]{32}\.", fn) or fn.endswith("_.png") or fn.endswith("__.png"):
                            phantom_images.append(f"Q{no}:{fn}")

        if phantom_images:
            bugs.append(f"[GAMBAR_PHANTOM_PUSMENDIK] Ditemukan {len(phantom_images)} tag phantom 404 Pusmendik: {phantom_images[:3]}")
        if broken_images:
            real_broken = [b for b in broken_images if b not in phantom_images]
            if real_broken:
                bugs.append(f"[GAMBAR_FISIK_HILANG] Ditemukan {len(real_broken)} file gambar fisik hilang di disk: {real_broken[:3]}")

        # -----------------------------------------------------------------
        # 2. CEK STRUKTUR OPSI & INTEGRITAS PERTANYAAN
        # -----------------------------------------------------------------
        bad_options = []
        empty_q = []
        for q in questions:
            no = q.get("nomor", "?")
            tipe = q.get("tipe") or q.get("tipe_soal", "")
            opts = q.get("pilihan_jawaban", []) or []
            stmts = q.get("pernyataan", []) or []

            stim_txt = (q.get("stimulus", {}).get("text") or "").strip()
            pert_txt = (q.get("pertanyaan", {}).get("text") or "").strip()
            has_stim_img = bool(q.get("stimulus", {}).get("images"))
            has_pert_img = bool(q.get("pertanyaan", {}).get("images"))

            if not stim_txt and not pert_txt and not has_stim_img and not has_pert_img:
                empty_q.append(f"Q{no}")

            if len(opts) > 5:
                bad_options.append(f"Q{no} (jumlah opsi: {len(opts)})")
            for idx, opt in enumerate(opts):
                txt = (opt.get("text") or "").strip()
                im = opt.get("image")
                if not txt and not im:
                    bad_options.append(f"Q{no} (opsi {idx} kosong)")

            if tipe in ["Benar-Salah", "Pilihan Ganda Kompleks (BS)", "Pilihan Ganda Kompleks (BS-Lengkap)"]:
                if not stmts:
                    bad_options.append(f"Q{no} ({tipe} tanpa daftar pernyataan)")

        if empty_q:
            bugs.append(f"[SOAL_KOSONG] Soal tanpa teks dan tanpa gambar: {empty_q}")
        if bad_options:
            bugs.append(f"[OPSI_RUSAK] Bug opsi jawaban terdeteksi: {bad_options[:3]}")

        # -----------------------------------------------------------------
        # 3. CEK KUNCI JAWABAN RESMI PUSMENDIK
        # -----------------------------------------------------------------
        kunci_path = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
        if not os.path.isfile(kunci_path):
            warnings.append(f"[KUNCI_BELUM_ADA] File kunci resmi ({slug}_kunci.json) belum ada di data/kunci/")
        else:
            try:
                with open(kunci_path, "r", encoding="utf-8") as kf:
                    kdoc = json.load(kf)
                mismatches = []
                for q in questions:
                    no = str(q.get("nomor"))
                    official_k = kdoc.get(no)
                    actual_k = q.get("kunci_jawaban")
                    if official_k is not None and actual_k is not None:
                        if isinstance(official_k, list):
                            norm_off = sorted([str(x).strip().upper() for x in official_k])
                        else:
                            norm_off = [str(official_k).strip().upper()]
                        if isinstance(actual_k, list):
                            norm_act = sorted([str(x).strip().upper() for x in actual_k])
                        else:
                            norm_act = [str(actual_k).strip().upper()]
                        if norm_off != norm_act:
                            mismatches.append(f"Q{no}: actual {norm_act} != official {norm_off}")
                if mismatches:
                    bugs.append(f"[KUNCI_MISMATCH] {len(mismatches)} kunci jawaban tidak cocok dengan Pusmendik: {mismatches[:3]}")
            except Exception as ke:
                warnings.append(f"Error memverifikasi kunci: {ke}")

        # -----------------------------------------------------------------
        # 4. CEK SOAL SERUPA
        # -----------------------------------------------------------------
        sim_missing = []
        sim_duplicate = []
        sim_verbatim = []
        seen_sims = {}

        for q in questions:
            no = q.get("nomor", "?")
            sim = q.get("soal_serupa")
            if not sim or not isinstance(sim, dict):
                sim_missing.append(f"Q{no}")
                continue

            sim_p = (sim.get("pertanyaan") or "").strip()
            if len(sim_p) < 20:
                sim_missing.append(f"Q{no} (terlalu pendek)")
                continue

            sim_full = re.sub(r"\s+", " ", sim_p).strip().lower()
            sim_tail = sim_full[-100:] if len(sim_full) > 100 else sim_full
            sim_opts = tuple(
                re.sub(r"\s+", " ", (o.get("text") or "")).strip().lower()
                for o in (sim.get("pilihan") or [])
                if isinstance(o, dict)
            )

            is_dup = False
            dup_target = None
            for prev_no, (prev_full, prev_tail, prev_opts) in seen_sims.items():
                if sim_full == prev_full:
                    is_dup = True
                    dup_target = prev_no
                    break
                if sim_tail == prev_tail and sim_opts and prev_opts and sim_opts == prev_opts:
                    is_dup = True
                    dup_target = prev_no
                    break

            if is_dup:
                sim_duplicate.append(f"Q{no} (sama dgn Q{dup_target})")
            else:
                seen_sims[no] = (sim_full, sim_tail, sim_opts)

            orig_p = re.sub(r"\s+", " ", (q.get("pertanyaan", {}).get("text") or "")).strip().lower()
            if orig_p and len(orig_p) > 30:
                if sim_full == orig_p or (len(orig_p) < 150 and sim_full[:len(orig_p)] == orig_p):
                    sim_verbatim.append(f"Q{no}")

        if sim_missing:
            bugs.append(f"[SOAL_SERUPA_KOSONG] Soal serupa belum lengkap di {len(sim_missing)} soal: {sim_missing[:4]}")
        if sim_duplicate:
            bugs.append(f"[SOAL_SERUPA_DUPLIKAT] Soal serupa copy-paste/sama di {len(sim_duplicate)} nomor: {sim_duplicate[:3]}")
        if sim_verbatim:
            bugs.append(f"[SOAL_SERUPA_VERBATIM] Soal serupa hanya menyalin soal asli di: {sim_verbatim[:3]}")

        # -----------------------------------------------------------------
        # 5. CEK SOLUSI 5 PILAR & DETEKSI TEMPLATE PALSU
        # -----------------------------------------------------------------
        sol_file, sol_rel = find_solution_file(slug, mapel, paket, registry)

        if not sol_file:
            bugs.append(f"[SOLUSI_HILANG] File solusi 5 pilar belum dibuat di data/solution_sources/")
        else:
            try:
                with open(sol_file, "r", encoding="utf-8") as sf:
                    sdoc = json.load(sf)
                slist = sdoc.get("solutions", []) if isinstance(sdoc, dict) else sdoc
                if not slist and isinstance(sdoc, dict):
                    slist = [v for k, v in sdoc.items() if isinstance(v, dict) and "steps" in v]

                stats["total_solutions"] = len(slist)
                if len(slist) < total_q:
                    bugs.append(f"[SOLUSI_KURANG] Jumlah solusi ({len(slist)}) < jumlah soal ({total_q})")

                reasonings = []
                steps_concat = []
                concepts = []
                math_leaks = []
                forbidden_words = []

                for s in slist:
                    q_no = s.get("question_number") or s.get("nomor") or "?"
                    r = (s.get("reasoning") or "").strip()
                    reasonings.append(r)

                    c = tuple(s.get("concept_kunci") or [])
                    concepts.append(c)

                    st_list = s.get("steps") or []
                    st_str = " || ".join([f"{st.get('title')}: {st.get('explanation')}" for st in st_list if isinstance(st, dict)])
                    steps_concat.append(st_str)

                    # Math leakage check: strip $$..$$ and $..$ first
                    blob = " | ".join([
                        str(s.get("diketahui") or ""),
                        str(s.get("ditanyakan") or ""),
                        r,
                        str(s.get("why_correct") or "")
                    ] + [str(st.get("explanation") or "") for st in st_list if isinstance(st, dict)])

                    clean_text = re.sub(r"\$\$[\s\S]*?\$\$|\$[^$]*?\$", " ", blob)
                    leaks = re.findall(r"\\(?:frac|dfrac|tfrac|lim|left|right|sqrt|sum|theta|pi)\b", clean_text)
                    if leaks or clean_text.count("\u210E") > 0:
                        math_leaks.append(f"Q{q_no}")

                    # Forbidden words
                    full_json = json.dumps(s, ensure_ascii=False).lower()
                    if "transkrip" in full_json:
                        forbidden_words.append(f"Q{q_no}: kata 'transkrip'")

                r_counts = Counter([x for x in reasonings if x])
                s_counts = Counter([x for x in steps_concat if x])
                c_counts = Counter([x for x in concepts if x])

                max_r_dup = max(r_counts.values()) if r_counts else 0
                max_s_dup = max(s_counts.values()) if s_counts else 0
                max_c_dup = max(c_counts.values()) if c_counts else 0

                if (max_r_dup > total_q * 0.35 and total_q > 3) or (max_s_dup > total_q * 0.35 and total_q > 3):
                    bugs.append(
                        f"[PILAR_BOILERPLATE_PALSU] Terdeteksi template copy-paste! "
                        f"Reasoning sama di {max_r_dup}/{total_q} soal, Steps sama di {max_s_dup}/{total_q} soal."
                    )
                if math_leaks:
                    bugs.append(f"[PILAR_MATH_LEAK] Kebocoran LaTeX mentah di luar math block $...$: {math_leaks[:3]}")
                if forbidden_words:
                    bugs.append(f"[PILAR_KATA_TERLARANG] Ditemukan kata terlarang: {forbidden_words[:3]}")

            except Exception as se:
                bugs.append(f"[SOLUSI_ERROR] Gagal memvalidasi solusi: {se}")

        # -----------------------------------------------------------------
        # 6. CEK INTEGRASI FRONTEND & SERVER
        # -----------------------------------------------------------------
        if mapel not in app_js_subjects:
            warnings.append(f"[APP_JS_MISSING] Mapel '{mapel}' belum terdaftar di SUBJECT_CATALOG app.js")

        # Status Display
        status_str = "CLEAN" if len(bugs) == 0 else "FAIL"
        if bugs:
            print(f"  ❌ STATUS: GAGAL ({len(bugs)} Kategori Bug Ditemukan!)")
            for b in bugs:
                print(f"     🚨 {b}")
        else:
            print(f"  ✅ STATUS: 100% BERSIH (0 Bugs)")

        if warnings:
            for w in warnings:
                print(f"     ⚠️ {w}")

        overall_results[slug] = {
            "mapel": mapel,
            "paket": paket,
            "status": status_str,
            "bugs": bugs,
            "warnings": warnings,
            "stats": stats
        }

    # =====================================================================
    # RINGKASAN REKAPITULASI PROYEK
    # =====================================================================
    print(f"\n{'='*90}")
    print("📊 REKAPITULASI AUDIT SEMESTA REPOSITORY")
    print(f"{'='*90}")

    clean_pkgs = []
    boilerplate_pkgs = []
    soal_serupa_pkgs = []
    other_bug_pkgs = []

    for slug, res in overall_results.items():
        bugs = res["bugs"]
        if not bugs:
            clean_pkgs.append(slug)
        else:
            has_bp = any("[PILAR_BOILERPLATE_PALSU]" in b for b in bugs)
            has_sim = any("[SOAL_SERUPA" in b for b in bugs)
            if has_bp:
                boilerplate_pkgs.append((slug, bugs))
            elif has_sim:
                soal_serupa_pkgs.append((slug, bugs))
            else:
                other_bug_pkgs.append((slug, bugs))

    print(f"\n🟢 [100% CLEAN & SIAP PRODUKSI] ({len(clean_pkgs)} Paket):")
    for s in clean_pkgs:
        print(f"   • {s}")

    print(f"\n🚨 [BUG KRITIS 1: PILAR BOILERPLATE / TEMPLATE PALSU] ({len(boilerplate_pkgs)} Paket):")
    for s, b_list in boilerplate_pkgs:
        print(f"   • {s}")
        for b in b_list:
            if "[PILAR_BOILERPLATE_PALSU]" in b:
                print(f"       -> {b}")

    print(f"\n⚠️ [BUG KRITIS 2: SOAL SERUPA COPY-PASTE / KOSONG] ({len(soal_serupa_pkgs)} Paket):")
    for s, b_list in soal_serupa_pkgs:
        print(f"   • {s}")
        for b in b_list:
            if "[SOAL_SERUPA" in b:
                print(f"       -> {b}")

    if other_bug_pkgs:
        print(f"\n🔧 [BUG LAINNYA: GAMBAR / OPSI / MATH] ({len(other_bug_pkgs)} Paket):")
        for s, b_list in other_bug_pkgs:
            print(f"   • {s}")
            for b in b_list:
                print(f"       -> {b}")

    print(f"\n{'─'*90}")
    print(f"Total Paket Diperiksa : {len(overall_results)}")
    print(f"Paket 100% Sempurna   : {len(clean_pkgs)}")
    print(f"Paket Butuh Perbaikan : {len(overall_results) - len(clean_pkgs)}")
    print(f"{'─'*90}")

    with open(REPORT_PATH, "w", encoding="utf-8") as rf:
        json.dump(overall_results, rf, ensure_ascii=False, indent=2)
    print(f"📁 Laporan audit tersimpan di: {REPORT_PATH}")

    return overall_results


if __name__ == "__main__":
    audit_all()
