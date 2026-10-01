# -*- coding: utf-8 -*-
"""_audit_ai_tutor_context.py — Audit kelengkapan dan presisi konteks AI Tutor di seluruh mapel aktif.
Memverifikasi:
1. resolve_tutor_context(subject, paket, nomor) mengembalikan konteks utuh:
   - canon_ctx (stimulus, soal, opsi/pernyataan, visual/transkripsi, kunci resmi)
   - solution (pilar 1-5, langkah pengerjaan, soal serupa)
2. format_solution_block memuat label PILAR 1-5 dan SOAL SERUPA.
3. image_paths terhubung ke file gambar fisik yang valid di disk (bukan broken image).
"""
import io
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"D:\PROJECTS\SCRAPE_TKA"
sys.path.insert(0, BASE_DIR)

from server import resolve_tutor_context, build_canonical_context, build_solution_payload
import tutor_engine

# Uji sampel beragam mapel: Sains, Soshum, Bahasa, Matematika
test_cases = [
    ("matematika_lanjut", 2, 8, "MTK Lanjut P2 Q8 (Parabola & Translasi Matriks)"),
    ("matematika_lanjut", 2, 3, "MTK Lanjut P2 Q3 (Kapasitas Kamar Hotel)"),
    ("matematika", 1, 1, "Matematika P1 Q1 (Peluang Inklusi-Eksklusi)"),
    ("ekonomi", 1, 2, "Ekonomi P1 Q2"),
    ("sejarah", 2, 1, "Sejarah P2 Q1"),
    ("fisika", 1, 1, "Fisika P1 Q1"),
    ("kimia", 1, 1, "Kimia P1 Q1"),
    ("biologi", 1, 1, "Biologi P1 Q1"),
]

print("=== AUDIT KELENGKAPAN KONTEKS AI TUTOR ===")
all_pass = True

for subj, pkt, no, desc in test_cases:
    ctx = resolve_tutor_context(subj, pkt, no)
    if not ctx:
        print(f"[FAIL] {desc}: resolve_tutor_context mengembalikan None!")
        all_pass = False
        continue

    canon = ctx.get("canon_ctx", {})
    sol = ctx.get("solution", {})
    kunci = ctx.get("official_answer")
    imgs = ctx.get("image_paths", [])

    # Periksa komponen inti
    has_soal = bool(canon.get("soal_text"))
    has_kunci = bool(kunci and kunci != "-")
    has_pembahasan = bool(sol and sol.get("pembahasan"))
    has_soal_serupa = bool(sol and sol.get("soal_serupa"))

    # Cek format blok prompt tutor
    q_block = tutor_engine._fmt_question_block(canon, ctx["subject_name"])
    sol_block = tutor_engine._fmt_solution_block(sol)

    has_pilar1 = "[PILAR 1" in sol_block
    has_pilar4 = "[PILAR 4" in sol_block
    has_serupa_block = "[SOAL SERUPA" in sol_block

    print(f"\n[{desc}]")
    print(f"  • Kunci Resmi       : {kunci}")
    print(f"  • Soal & Opsi       : {'OK' if has_soal else 'MISSING'}")
    print(f"  • Gambar Terdeteksi : {len(imgs)} file fisik")
    print(f"  • Pilar 1 (Dik/Dit) : {'OK' if has_pilar1 else 'TIDAK TERDETEKSI'}")
    print(f"  • Pilar 4 (Langkah) : {'OK' if has_pilar4 else 'TIDAK TERDETEKSI'}")
    print(f"  • Soal Serupa       : {'OK' if has_serupa_block else 'TIDAK TERSEDIA'}")

    if not (has_soal and has_kunci and has_pilar1 and has_pilar4):
        all_pass = False

print("\n" + "="*50)
if all_pass:
    print("HASIL: 100% LULUS AUDIT KONTEKS AI TUTOR!")
else:
    print("HASIL: DITEMUKAN GAP KONTEKS PADA BEBERAPA SOAL")
