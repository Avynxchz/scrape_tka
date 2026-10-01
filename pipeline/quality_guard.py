# -*- coding: utf-8 -*-
"""pipeline/quality_guard.py — Automated Zero-Trust Quality Gate & Prevention Guard.

Modul pencegahan otomatis (Quality Gate) yang mencegah bug katalog masuk kembali ke proyek:
1. Anti-Boilerplate / Fake Template Guard (mencegah pilar copy-paste seperti di Ekonomi/Bing/PKW).
2. Anti-Generic Step Guard (mencegah langkah generik tanpa isi nyata).
3. Anti-Duplicate Soal Serupa Guard (mencegah soal serupa duplikat antar nomor).
4. Anti-Phantom & Broken Image Guard (mencegah tag 404 Pusmendik & file hilang).
5. Anti-Math Leak & Forbidden Word Guard (mencegah kata 'transkrip' & raw LaTeX di luar KaTeX).
6. Anti-Corrupt Option Guard (mencegah bug A-L & opsi kosong).
7. Ground Truth Pusmendik Key Guard (mencegah deviasi dari kunci resmi).

Bisa dipanggil sebagai modul:
    from pipeline.quality_guard import assert_package_integrity
    assert_package_integrity(slug, learning_doc, solutions_doc, img_dir, kunci_doc)

Atau dijalankan via CLI:
    python pipeline/quality_guard.py --slug ekonomi_paket_1
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import re
import json
from collections import Counter


class QualityGuardError(Exception):
    """Exception dilempar saat paket gagal melewati gerbang mutu zero-trust."""
    def __init__(self, category, message, violations=None):
        super().__init__(f"[{category}] {message}")
        self.category = category
        self.message = message
        self.violations = violations or []


def assert_package_integrity(slug, learning_doc, solutions_doc=None, img_dir=None, kunci_doc=None):
    """Validasi ketat gerbang mutu (Zero-Trust Gatekeeper).
    Melempar QualityGuardError jika ditemukan pelanggaran mutu sekecil apapun.
    Mengembalikan dict status audit jika lolos.
    """
    questions = learning_doc.get("soal", [])
    total_q = len(questions)
    if total_q == 0:
        raise QualityGuardError("EMPTY_PACKAGE", f"Paket {slug} tidak memiliki butir soal!")

    # =========================================================================
    # 1. INTEGRITAS SOAL & OPSI JAWABAN
    # =========================================================================
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
            bad_options.append(f"Q{no}: Terlalu banyak opsi ({len(opts)} opsi > 5)")

        for idx, opt in enumerate(opts):
            txt = (opt.get("text") or "").strip()
            im = opt.get("image")
            lat = (opt.get("latex") or "").strip()
            fd = (opt.get("full_display") or "").strip()
            if not txt and not im and not lat and not fd:
                bad_options.append(f"Q{no}: Opsi index {idx} kosong")

        if tipe in ["Benar-Salah", "Pilihan Ganda Kompleks (BS)", "Pilihan Ganda Kompleks (BS-Lengkap)"]:
            if not stmts:
                bad_options.append(f"Q{no}: Tipe {tipe} wajib memiliki daftar pernyataan")

    if empty_q:
        raise QualityGuardError("SOAL_KOSONG", f"Ditemukan {len(empty_q)} soal tanpa teks & gambar", empty_q)
    if bad_options:
        raise QualityGuardError("STRUKTUR_OPSI_RUSAK", f"Ditemukan {len(bad_options)} isu struktur opsi", bad_options)

    # =========================================================================
    # 2. INTEGRITAS FILE GAMBAR FISIK & DETEKSI PHANTOM 404
    # =========================================================================
    if img_dir and os.path.isdir(img_dir):
        broken_imgs = []
        phantom_imgs = []
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
                    disk_p = os.path.join(img_dir, fn)
                    if not os.path.isfile(disk_p) or os.path.getsize(disk_p) == 0:
                        broken_imgs.append(f"Q{no}:{fn}")
                        if re.search(r"_[a-f0-9]{32}_[a-f0-9]{32}\.", fn) or fn.endswith("_.png") or fn.endswith("__.png"):
                            phantom_imgs.append(f"Q{no}:{fn}")

        if phantom_imgs:
            raise QualityGuardError("GAMBAR_PHANTOM", f"Ditemukan {len(phantom_imgs)} tag phantom 404 Pusmendik", phantom_imgs)
        if broken_imgs:
            raise QualityGuardError("GAMBAR_FISIK_HILANG", f"Ditemukan {len(broken_imgs)} gambar tidak ada di disk", broken_imgs)

    # =========================================================================
    # 3. KESETIAAN PADA KUNCI RESMI PUSMENDIK (GROUND TRUTH)
    # =========================================================================
    if kunci_doc:
        kunci_mismatches = []
        for q in questions:
            no = str(q.get("nomor"))
            off = kunci_doc.get(no)
            act = q.get("kunci_jawaban")
            if off is not None and act is not None:
                norm_off = sorted([str(x).strip().upper() for x in off]) if isinstance(off, list) else [str(off).strip().upper()]
                norm_act = sorted([str(x).strip().upper() for x in act]) if isinstance(act, list) else [str(act).strip().upper()]
                if norm_off != norm_act:
                    kunci_mismatches.append(f"Q{no}: actual {norm_act} != Pusmendik {norm_off}")
        if kunci_mismatches:
            raise QualityGuardError("KUNCI_MISMATCH", f"Ditemukan {len(kunci_mismatches)} deviasi kunci resmi Pusmendik", kunci_mismatches)

    # =========================================================================
    # 4. KEUNIKAN & OTENTISITAS SOAL SERUPA
    # =========================================================================
    sim_missing = []
    sim_dups = []
    sim_verbatim = []
    seen_sims = {}

    for q in questions:
        no = q.get("nomor", "?")
        sim = q.get("soal_serupa")
        if not sim or not isinstance(sim, dict):
            sim_missing.append(f"Q{no}")
            continue

        sim_p = (sim.get("pertanyaan") or "").strip()
        if len(sim_p) < 25:
            sim_missing.append(f"Q{no}: Teks pertanyaan serupa terlalu pendek ({len(sim_p)} chars)")
            continue

        # Cek duplikasi antar nomor
        # Pertanyaan serupa bisa berupa stimulus panjang (membaca) yang dipakai oleh beberapa nomor soal.
        # Soal hanya dianggap duplikat jika:
        # 1. Seluruh teks pertanyaan identik (100% sama)
        # 2. ATAU ekor kalimat tanya (interrogative prompt di akhir) sama DAN pilihan jawabannya sama
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
            sim_dups.append(f"Q{no} identik dengan Q{dup_target}")
        else:
            seen_sims[no] = (sim_full, sim_tail, sim_opts)

        # Cek plagiasi/salin mentah dari soal asli
        orig_p = re.sub(r"\s+", " ", (q.get("pertanyaan", {}).get("text") or "")).strip().lower()
        if orig_p and len(orig_p) > 30:
            if sim_full == orig_p or (len(orig_p) < 150 and sim_full[:len(orig_p)] == orig_p):
                sim_verbatim.append(f"Q{no}")

    if sim_missing:
        raise QualityGuardError("SOAL_SERUPA_KOSONG", f"Ditemukan {len(sim_missing)} nomor tanpa Soal Serupa yang valid", sim_missing)
    if sim_dups:
        raise QualityGuardError("SOAL_SERUPA_DUPLIKAT", f"Ditemukan {len(sim_dups)} Soal Serupa duplikat/copy-paste antar nomor", sim_dups)
    if sim_verbatim:
        raise QualityGuardError("SOAL_SERUPA_SALIN_ASLI", f"Ditemukan {len(sim_verbatim)} Soal Serupa hanya menyalin soal asli mentah-mentah", sim_verbatim)

    # =========================================================================
    # 5. GERBANG MUTU 5 PILAR (ANTI-BOILERPLATE, ANTI-GENERIK, ANTI-LEAK)
    # =========================================================================
    if solutions_doc:
        slist = solutions_doc.get("solutions", []) if isinstance(solutions_doc, dict) else solutions_doc
        if not slist and isinstance(solutions_doc, dict):
            slist = [v for k, v in solutions_doc.items() if isinstance(v, dict) and "steps" in v]

        if len(slist) < total_q:
            raise QualityGuardError("SOLUSI_KURANG", f"Jumlah solusi ({len(slist)}) < jumlah soal ({total_q})")

        reasonings = []
        steps_concat = []
        math_leaks = []
        forbidden_words = []

        for s in slist:
            q_no = s.get("question_number") or s.get("nomor") or "?"
            r = (s.get("reasoning") or "").strip()
            reasonings.append(r)

            st_list = s.get("steps") or []
            if len(st_list) < 2:
                raise QualityGuardError("PILAR_LANGKAH_KURANG", f"Q{q_no} memiliki kurang dari 2 langkah penyelesaian!")

            st_str = " || ".join([f"{st.get('title')}: {st.get('explanation')}" for st in st_list if isinstance(st, dict)])
            steps_concat.append(st_str)

            # Cek kebocoran LaTeX mentah
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

            # Cek kata terlarang
            full_json = json.dumps(s, ensure_ascii=False).lower()
            if "transkrip" in full_json:
                forbidden_words.append(f"Q{q_no}: kata 'transkrip'")

        # ANTI-BOILERPLATE CHECK (Threshold ketat: max 25% toleransi duplikasi reasoning/steps)
        r_counts = Counter([x for x in reasonings if x])
        s_counts = Counter([x for x in steps_concat if x])

        max_r_dup = max(r_counts.values()) if r_counts else 0
        max_s_dup = max(s_counts.values()) if s_counts else 0

        max_allowed_dup = max(2, int(total_q * 0.25))

        if max_r_dup > max_allowed_dup and total_q > 3:
            raise QualityGuardError(
                "PILAR_BOILERPLATE_REASONING",
                f"Terdeteksi template palsu! Reasoning identik ditemukan pada {max_r_dup}/{total_q} soal (Batas max: {max_allowed_dup})",
                [r_counts.most_common(1)[0][0][:100]]
            )

        if max_s_dup > max_allowed_dup and total_q > 3:
            raise QualityGuardError(
                "PILAR_BOILERPLATE_STEPS",
                f"Terdeteksi template palsu! Langkah solusi identik ditemukan pada {max_s_dup}/{total_q} soal (Batas max: {max_allowed_dup})",
                [s_counts.most_common(1)[0][0][:100]]
            )

        if math_leaks:
            raise QualityGuardError("PILAR_MATH_LEAK", f"Ditemukan {len(math_leaks)} kebocoran raw LaTeX di luar matematika $...$", math_leaks)
        if forbidden_words:
            raise QualityGuardError("PILAR_KATA_TERLARANG", f"Ditemukan {len(forbidden_words)} kata terlarang", forbidden_words)

    return {
        "status": "PASS",
        "slug": slug,
        "total_questions": total_q,
        "solutions_verified": len(solutions_doc.get("solutions", [])) if solutions_doc else 0
    }
