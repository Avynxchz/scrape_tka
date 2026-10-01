# -*- coding: utf-8 -*-
"""_audit_integrity_suite.py — Audit Integritas Menyeluruh 23 Paket Live.
Memeriksa:
1. Kesesuaian Kunci Otoritatif vs File Solusi.
2. Keberadaan Fisik Gambar Soal (Deteksi Broken Images).
3. Validitas Opsi Jawaban & Tipe Soal (PG biasa, PG Kompleks, Benar-Salah/Tepat).
4. Ketersediaan Soal Serupa di setiap soal aktif.
"""
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"D:\PROJECTS\SCRAPE_TKA"
DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
REG_PATH = os.path.join(SOL_DIR, "registry.json")

sys.path.insert(0, BASE_DIR)
import solution_loader

registry = json.load(open(REG_PATH, encoding="utf-8"))

total_packages = 0
total_questions = 0
total_images_checked = 0
broken_images = []
missing_keys = []
key_mismatches = []
missing_serupa = []

type_distribution = {}

print("=== MEMULAI AUDIT INTEGRITAS MENYELURUH 23 PAKET LIVE ===")

for slug, reg_entry in sorted(registry.items()):
    if not isinstance(reg_entry, dict) or "active_source" not in reg_entry:
        continue

    total_packages += 1
    sol_file = reg_entry["active_source"]
    sol_path = os.path.join(SOL_DIR, sol_file)

    # Deteksi nama file learning
    # Contoh slug: 'matematika_paket_1' -> 'matematika_paket_1_learning.json'
    # 'mtk_paket_1' -> 'matematika_paket_1_learning.json'
    subj_map = {
        "mtk": "matematika", "mtkl": "matematika_lanjut", "bing": "bahasa_inggris",
        "eko": "ekonomi", "pkw": "kewirausahaan", "geo": "geografi", "fis": "fisika",
        "kim": "kimia", "bio": "biologi", "sos": "sosiologi", "ind": "bahasa_indonesia",
        "sej": "sejarah"
    }

    lrn_file = f"{slug}_learning.json"
    if not os.path.isfile(os.path.join(DATA_DIR, lrn_file)):
        # coba decode prefix
        parts = slug.split("_paket_")
        if len(parts) == 2 and parts[0] in subj_map:
            lrn_file = f"{subj_map[parts[0]]}_paket_{parts[1]}_learning.json"

    lrn_path = os.path.join(DATA_DIR, lrn_file)
    if not os.path.isfile(lrn_path):
        print(f"[WARN] Learning JSON tidak ditemukan untuk {slug} (dicari: {lrn_file})")
        continue

    lrn_doc = json.load(open(lrn_path, encoding="utf-8"))
    sol_doc = json.load(open(sol_path, encoding="utf-8")) if os.path.isfile(sol_path) else {}

    soal_list = lrn_doc.get("soal", [])
    solutions = sol_doc.get("solutions", [])
    sol_by_num = {s.get("question_number"): s for s in solutions}

    # Direktori gambar paket
    # Pola: data/<mapel>/paket_<no>/images/ atau data/images/
    parts = lrn_file.replace("_learning.json", "").split("_paket_")
    mapel_folder = parts[0]
    paket_no = parts[1] if len(parts) > 1 else "1"
    pkg_img_dir = os.path.join(DATA_DIR, mapel_folder, f"paket_{paket_no}", "images")

    for q in soal_list:
        total_questions += 1
        qnum = q.get("nomor")
        kunci = q.get("kunci_jawaban")

        # 1. Cek Kunci
        if kunci is None or kunci == "" or kunci == "-":
            missing_keys.append(f"{slug} Q{qnum}")

        # 2. Cek Crosscheck Kunci dengan Solusi Claude
        if qnum in sol_by_num:
            sol_entry = sol_by_num[qnum]
            # Bandingkan kunci resmi vs solusi
            cc = solution_loader.cross_check_keys(sol_entry, kunci)
            if not cc.get("match"):
                key_mismatches.append(f"{slug} Q{qnum}: {cc.get('detail')}")

        # 3. Tipe Soal
        tipe = q.get("tipe_soal") or q.get("tipe") or "Pilihan Ganda"
        if q.get("pernyataan"):
            tipe = "Pernyataan / Benar-Salah"
        elif q.get("tipe_soal") == "Pilihan Ganda Kompleks" or isinstance(kunci, list):
            tipe = "Pilihan Ganda Kompleks"
        type_distribution[tipe] = type_distribution.get(tipe, 0) + 1

        # 4. Cek Fisik Gambar
        imgs = (q.get("stimulus", {}).get("images", []) or []) + (q.get("pertanyaan", {}).get("images", []) or [])
        # juga cek html img src
        html_chunks = [q.get("stimulus", {}).get("html", ""), q.get("pertanyaan", {}).get("html", "")]
        for chunk in html_chunks:
            for m in re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', chunk or ""):
                fn = os.path.basename(m)
                imgs.append({"filename": fn})

        for im in imgs:
            fn = im.get("filename") if isinstance(im, dict) else os.path.basename(str(im))
            if fn:
                total_images_checked += 1
                # Cari di beberapa lokasi kandidat
                cand1 = os.path.join(pkg_img_dir, fn)
                cand2 = os.path.join(DATA_DIR, "images", fn)
                cand3 = os.path.join(DATA_DIR, fn)
                found = os.path.isfile(cand1) or os.path.isfile(cand2) or os.path.isfile(cand3)
                if not found:
                    # Cari di seluruh subfolder data
                    for root, _, files in os.walk(DATA_DIR):
                        if fn in files:
                            found = True
                            break
                if not found:
                    broken_images.append(f"{slug} Q{qnum}: {fn}")

        # 5. Cek Soal Serupa
        sim = q.get("soal_serupa")
        if not sim or not sim.get("pertanyaan"):
            missing_serupa.append(f"{slug} Q{qnum}")

print(f"\n--- HASIL AUDIT ---")
print(f"Total Paket Diperiksa    : {total_packages} paket")
print(f"Total Soal Diperiksa     : {total_questions} soal")
print(f"Total Gambar Diperiksa   : {total_images_checked} gambar")
print(f"Missing Kunci Jawaban    : {len(missing_keys)} (Harus 0)")
print(f"Broken Images            : {len(broken_images)} (Harus 0)")
print(f"Missing Soal Serupa      : {len(missing_serupa)} ({len(missing_serupa)}/{total_questions})")
print(f"Key Mismatch (Audit)     : {len(key_mismatches)} notice")

print("\n--- Distribusi Tipe Soal ---")
for t, cnt in sorted(type_distribution.items(), key=lambda x: -x[1]):
    print(f"  • {t:30s}: {cnt} soal")

if missing_keys:
    print(f"\n[DAFTAR MISSING KUNCI]: {missing_keys[:10]}")

if broken_images:
    print(f"\n[DAFTAR BROKEN IMAGES]: {broken_images[:10]}")

if key_mismatches:
    print(f"\n[CONTOH KEY MISMATCH DETAIL]:")
    for km in key_mismatches[:5]:
        print(f"  - {km}")
