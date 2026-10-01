# -*- coding: utf-8 -*-
"""pipeline/03_generate_soal_serupa.py — Automated Practice Question (Soal Serupa) Generator.

Fase 4: Menghasilkan soal serupa teks murni (tanpa gambar) untuk setiap soal TKA
agar siswa dapat menguji pemahaman konsepnya secara mandiri.
Hasil disimpan langsung ke dalam `data/<slug>_learning.json`.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import re
import json
import time
import argparse
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.insert(0, BASE_DIR)

import tutor_llm

DATA_DIR = os.path.join(BASE_DIR, "data")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def safe_parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text, strict=False)
    except json.JSONDecodeError:
        pass
    fixed = re.sub(r'\\(?!["\\])', r'\\\\', text)
    try:
        return json.loads(fixed, strict=False)
    except json.JSONDecodeError:
        pass
    fixed2 = re.sub(r'\\(?!")', r'\\\\', text)
    return json.loads(fixed2, strict=False)


def build_prompt(subject_name, batch_questions):
    items = []
    for q in batch_questions:
        no = q["nomor"]
        stim = q.get("stimulus", {}).get("text", "").strip()
        pert = q.get("pertanyaan", {}).get("text", "").strip()
        kunci = q.get("kunci_jawaban", "-")
        items.append(f"""---
[SOAL ACUAN NO {no}]
Kunci Resmi: {kunci}
Stimulus Teks: {stim or '(Lihat topik pertanyaan)'}
Pertanyaan: {pert}
""")

    prompt = f"""Kamu adalah Pakar Pembuat Soal TKA Saintek SMA Kemdikbud ({subject_name}).
Tugasmu adalah membuat SOAL SERUPA / LATIHAN PEMANTAPAN (Text-Only, tanpa memerlukan gambar atau grafik)
untuk setiap soal acuan berikut. Soal latihan harus menguji konsep materi yang persis sama, namun dengan narasi, variasi variabel, atau skenario baru.

ATURAN WAJIB:
1. Soal latihan HARUS TEKS MURNI (tidak boleh mengandalkan diagram atau gambar baru).
2. Sediakan 5 pilihan jawaban (A, B, C, D, E).
3. Berikan 1 kunci yang pasti benar (hanya pilih A/B/C/D/E) dan pembahasan singkat yang padat & ilmiah.
4. Output WAJIB berupa JSON ARRAY yang valid, tanpa teks pengantar atau penutup apapun selain JSON!

FORMAT JSON PER ELEMEN:
{{
  "nomor_soal": <nomor_soal_acuan>,
  "soal_serupa": {{
    "pertanyaan": "<Teks pertanyaan latihan pemantapan lengkap beserta stimulus singkat bila ada>",
    "pilihan": [
      {{"key": "A", "text": "<Pilihan A>"}},
      {{"key": "B", "text": "<Pilihan B>"}},
      {{"key": "C", "text": "<Pilihan C>"}},
      {{"key": "D", "text": "<Pilihan D>"}},
      {{"key": "E", "text": "<Pilihan E>"}}
    ],
    "kunci": "<A/B/C/D/E>",
    "pembahasan_singkat": "<Penjelasan ringkas mengapa kunci tersebut benar>"
  }}
}}

DAFTAR SOAL ACUAN:
{"".join(items)}
"""
    return prompt


def generate_for_slug(slug, subject_name, batch_size=5):
    lrn_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
    if not os.path.isfile(lrn_path):
        log(f"File {lrn_path} tidak ditemukan!")
        return False

    with open(lrn_path, "r", encoding="utf-8") as f:
        lrn_doc = json.load(f)

    questions = lrn_doc.get("soal", [])
    total_q = len(questions)
    log(f"==================================================================")
    log(f"🎯 GENERATING SOAL SERUPA: {slug} ({total_q} soal, mapel: {subject_name})")
    log(f"==================================================================")

    # Cek apakah sudah terisi semua
    missing_q = [q for q in questions if not q.get("soal_serupa")]
    if not missing_q:
        log("Semua soal sudah memiliki soal_serupa. Melewati.")
        return True

    log(f"Ditemukan {len(missing_q)} soal yang belum memiliki soal_serupa.")

    batches = [questions[i:i + batch_size] for i in range(0, total_q, batch_size)]
    q_map = {q["nomor"]: q for q in questions}

    for b_idx, batch in enumerate(batches, 1):
        q_start = batch[0]["nomor"]
        q_end = batch[-1]["nomor"]
        log(f"--- Batch {b_idx}/{len(batches)} (Soal {q_start}-{q_end}) ---")

        prompt = build_prompt(subject_name, batch)

        for attempt in range(1, 4):
            try:
                reply, model = tutor_llm._post_gemini(
                    messages=[{"role": "user", "content": prompt}],
                    model_choice="gemini-flash",
                    temperature=0.4,
                    max_tokens=4096,
                    timeout=90
                )
                parsed = safe_parse_json(reply)
                if not isinstance(parsed, list):
                    raise ValueError("Hasil AI bukan JSON list!")

                for item in parsed:
                    no = item.get("nomor_soal")
                    sim = item.get("soal_serupa")
                    if no in q_map and sim:
                        q_map[no]["soal_serupa"] = sim

                log(f"  ✅ Batch {b_idx} Sukses! ({len(parsed)} soal serupa dibuat)")
                break
            except Exception as e:
                log(f"  ❌ Batch {b_idx} Gagal attempt {attempt}: {e}")
                time.sleep(2)
        else:
            log(f"  ⚠️ Melewatkan batch {b_idx} setelah 3 percobaan.")

    # Simpan kembali ke file learning
    with open(lrn_path, "w", encoding="utf-8") as f:
        json.dump(lrn_doc, f, indent=2, ensure_ascii=False)
    log(f"🎉 Soal serupa berhasil disimpan ke {lrn_path}\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Soal Serupa")
    parser.add_argument("--target", type=str, default="all",
                        choices=["all", "kimia_paket_1", "kimia_paket_2", "biologi_paket_1", "biologi_paket_2"])
    args = parser.parse_args()

    targets = [
        ("kimia_paket_1", "Kimia"),
        ("kimia_paket_2", "Kimia"),
        ("biologi_paket_1", "Biologi"),
        ("biologi_paket_2", "Biologi")
    ]
    if args.target != "all":
        targets = [t for t in targets if t[0] == args.target]

    for slug, subj in targets:
        generate_for_slug(slug, subj)
