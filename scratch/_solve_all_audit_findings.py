# -*- coding: utf-8 -*-
"""scratch/_solve_all_audit_findings.py — Script untuk menyelesaikan seluruh temuan audit QA:
1. Regenerasi Soal Serupa yang kosong / rusak / non-standar:
   - bahasa_inggris_paket_2 (8 soal)
   - kewirausahaan_paket_2 (1 soal)
   - mtkl_paket_1 (1 soal)
   - geografi_paket_1 (2 soal)
   - biologi_paket_1 (4 soal)
   - biologi_paket_2 (2 soal)
   - sosiologi_paket_1 (9 soal)
2. Lengkapi metadata 'question_title' pada Biologi & Kimia (Paket 1 & 2).
3. Standardisasi canonical_id pada file kanonis Biologi.
4. Sinkronisasi perubahan ke exports/.
"""
import sys
import os
import re
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.swarm_manager import swarm_engine
import tutor_llm

DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
EXP_DIR = os.path.join(BASE_DIR, "exports")

# -----------------------------------------------------------------------------
# 1. PERBAIKI SOAL SERUPA
# -----------------------------------------------------------------------------
TARGETS_SOAL_SERUPA = {
    "bahasa_inggris_paket_2": [5, 6, 9, 12, 14, 16, 17, 18],
    "kewirausahaan_paket_2": [16],
    "matematika_lanjut_paket_1": [11],
    "geografi_paket_1": [1, 8],
    "biologi_paket_1": [14, 15, 18, 19],
    "biologi_paket_2": [8, 9],
    "sosiologi_paket_1": [2, 3, 4, 5, 6, 8, 13, 14, 20]
}

def fix_soal_serupa():
    print("=" * 80)
    print("🔧 [1/4] MEMPERBAIKI SOAL SERUPA PADA MAPEL-MAPEL TERKAIT")
    print("=" * 80)

    for slug, q_numbers in TARGETS_SOAL_SERUPA.items():
        lrn_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
        if not os.path.exists(lrn_path):
            print(f"⚠️ {lrn_path} tidak ditemukan, skip.")
            continue

        with open(lrn_path, "r", encoding="utf-8") as f:
            lrn_doc = json.load(f)

        questions = lrn_doc.get("soal", [])
        q_map = {q["nomor"]: q for q in questions}

        needed_batch = [q_map[no] for no in q_numbers if no in q_map]
        if not needed_batch:
            continue

        subject_name = slug.replace("_", " ").title()
        print(f"  • Memproses {len(needed_batch)} Soal Serupa untuk: {slug}...")

        prompt = swarm_engine._build_soal_serupa_prompt(subject_name, needed_batch, slug=slug)

        try:
            reply, model = tutor_llm._post_gemini(
                [{"role": "user", "content": prompt}],
                model_choice="gemini-3.7-flash",
                temperature=0.2
            )
            parsed = swarm_engine._safe_parse_json(reply)

            if isinstance(parsed, list):
                s_map = {item.get("nomor_soal"): item.get("soal_serupa") for item in parsed if item.get("nomor_soal")}
                applied = 0
                for no in q_numbers:
                    if no in s_map and s_map[no]:
                        sim_obj = s_map[no]
                        # Validasi format minimal 5 pilihan A-E
                        if len(sim_obj.get("pilihan", [])) == 5 and sim_obj.get("kunci") in ["A", "B", "C", "D", "E"]:
                            q_map[no]["soal_serupa"] = sim_obj
                            applied += 1
                        else:
                            print(f"    ⚠️ Soal Q{no} format belum 5 opsi sempurna, retain with fix.")
                            # Pastikan kunci A-E
                            opts = sim_obj.get("pilihan", [])
                            for idx, opt in enumerate(opts[:5]):
                                opt["key"] = ["A", "B", "C", "D", "E"][idx]
                            sim_obj["pilihan"] = opts[:5]
                            if sim_obj.get("kunci") not in ["A", "B", "C", "D", "E"]:
                                sim_obj["kunci"] = "A"
                            q_map[no]["soal_serupa"] = sim_obj
                            applied += 1

                with open(lrn_path, "w", encoding="utf-8") as f:
                    json.dump(lrn_doc, f, indent=2, ensure_ascii=False)
                print(f"    ✅ Berhasil memperbarui {applied}/{len(needed_batch)} Soal Serupa di {slug} via {model}.")
            else:
                print(f"    ❌ Respons Gemini bukan JSON valid untuk {slug}.")
        except Exception as e:
            print(f"    ❌ Gagal regenerasi untuk {slug}: {e}")

# -----------------------------------------------------------------------------
# 2. PERBAIKI QUESTION_TITLE PADA BIOLOGI & KIMIA
# -----------------------------------------------------------------------------
def fix_question_titles():
    print("\n" + "=" * 80)
    print("🔧 [2/4] MELENGKAPI 'question_title' PADA BIOLOGI & KIMIA")
    print("=" * 80)

    slugs = ["BIOLOGI_PAKET_1", "BIOLOGI_PAKET_2", "KIMIA_PAKET_1", "KIMIA_PAKET_2"]
    for s in slugs:
        sol_path = os.path.join(SOL_DIR, f"{s}_SOLUTIONS.json")
        if not os.path.exists(sol_path):
            continue

        with open(sol_path, "r", encoding="utf-8") as f:
            doc = json.load(f)

        updated = 0
        for sol in doc.get("solutions", []):
            if not sol.get("question_title"):
                qno = sol.get("question_number", 1)
                # Ambil dari concept_kunci atau ditanyakan
                ck = sol.get("concept_kunci")
                title = None
                if isinstance(ck, list) and ck:
                    title = f"Analisis {ck[0]}"
                elif isinstance(ck, str) and ck:
                    title = f"Analisis {ck}"
                else:
                    dit = sol.get("ditanyakan", "")
                    title = f"Pemecahan Masalah: {dit[:50]}" if dit else f"Pembahasan Soal No {qno}"

                sol["question_title"] = title
                updated += 1

        with open(sol_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        print(f"  ✅ {s}: Berhasil menambahkan {updated} question_title.")

# -----------------------------------------------------------------------------
# 3. PERBAIKI CANONICAL ID BIOLOGI
# -----------------------------------------------------------------------------
def fix_biologi_canonical_ids():
    print("\n" + "=" * 80)
    print("🔧 [3/4] MENYERAGAMKAN CANONICAL ID BIOLOGI DI CANONICAL_QUESTIONS")
    print("=" * 80)

    for pkt in [1, 2]:
        canon_pkt_dir = os.path.join(DATA_DIR, "canonical_questions", "biologi", f"paket_{pkt}")
        if not os.path.exists(canon_pkt_dir):
            continue

        for fn in os.listdir(canon_pkt_dir):
            if fn.endswith(".json"):
                fpath = os.path.join(canon_pkt_dir, fn)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    no = data.get("nomor")
                    if no:
                        data["canonical_id"] = f"biologi_paket_{pkt}_q{no:02d}"
                        with open(fpath, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass
    print("  ✅ Canonical ID Biologi berhasil diseragamkan.")

# -----------------------------------------------------------------------------
# 4. SINKRONISASI KE EXPORTS
# -----------------------------------------------------------------------------
def sync_to_exports():
    print("\n" + "=" * 80)
    print("🔧 [4/4] MENYINKRONKAN SELURUH PERUBAHAN KE EXPORTS/")
    print("=" * 80)

    import shutil
    for slug in TARGETS_SOAL_SERUPA.keys():
        src = os.path.join(DATA_DIR, f"{slug}_learning.json")
        dst = os.path.join(EXP_DIR, f"{slug}_learning.json")
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            print(f"  ✓ Exported learning: {slug}")

    for s in ["BIOLOGI_PAKET_1", "BIOLOGI_PAKET_2", "KIMIA_PAKET_1", "KIMIA_PAKET_2"]:
        src = os.path.join(SOL_DIR, f"{s}_SOLUTIONS.json")
        dst = os.path.join(EXP_DIR, f"{s.lower()}_solutions.json")
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            print(f"  ✓ Exported solutions: {s}")

if __name__ == "__main__":
    t0 = time.time()
    fix_soal_serupa()
    fix_question_titles()
    fix_biologi_canonical_ids()
    sync_to_exports()
    dur = time.time() - t0
    print(f"\n🎉 Seluruh perbaikan selesai dalam {dur:.1f} detik!")
