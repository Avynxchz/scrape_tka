import json
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Fix fisika_paket_1 Q6 options full_display and text
fis1_path = os.path.join(ROOT, "data", "fisika_paket_1_learning.json")
if os.path.exists(fis1_path):
    with open(fis1_path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    for q in doc.get("soal", []):
        if q.get("nomor") == 6:
            for opt in q.get("pilihan_jawaban", []):
                if opt.get("latex") and not opt.get("text"):
                    opt["text"] = f"${opt['latex']}$"
                    opt["full_display"] = f"${opt['latex']}$"
    with open(fis1_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print("✅ Fixed fisika_paket_1 Q6 option display text.")

# 2. Fix MTK_PAKET_2_SOLUTIONS_EXTRA.json Q21 reasoning and Q5 review_reason
mtk2_path = os.path.join(ROOT, "data", "solution_sources", "MTK_PAKET_2_SOLUTIONS_EXTRA.json")
if os.path.exists(mtk2_path):
    with open(mtk2_path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    for s in doc.get("solutions", []):
        if s.get("question_number") == 5:
            s["review_reason"] = None
        if s.get("question_number") == 21:
            s["reasoning"] = (
                "Soal menguji kemampuan membaca dan menginterpretasikan data tren pada grafik garis multivariat kelulusan sekolah Yayasan Cahaya. "
                "Berdasarkan visual grafik, kelulusan SMA 1 Bintang menunjukkan peningkatan konsisten sejak tahun 2020 (Pernyataan A benar) "
                "dan kelulusan SMA 2 Bintang konstan/tetap pada tiga tahun terakhir (Pernyataan D benar)."
            )
            s["steps"] = [
                {
                    "step": 1,
                    "title": "Analisis Kurva SMA 1 Bintang",
                    "explanation": "Amati grafik untuk SMA 1 Bintang mulai tahun 2020 ke atas. Garis menunjukkan tren kenaikan berkelanjutan, membuktikan pernyataan A tepat."
                },
                {
                    "step": 2,
                    "title": "Analisis Kurva SMA 2 Bintang",
                    "explanation": "Amati grafik untuk SMA 2 Bintang pada tiga tahun terakhir. Garis bersifat mendatar (nilai konstan), membuktikan pernyataan D tepat."
                },
                {
                    "step": 3,
                    "title": "Verifikasi Opsi Salah (B, C, E)",
                    "explanation": "Pernyataan B, C, dan E gugur karena data pada tahun-tahun terkait mengalami fluktuasi penurunan dan tidak konsisten naik."
                }
            ]
            s["why_correct"] = "Pernyataan A dan D terbukti sesuai secara langsung dengan pembacaan grafik garis pada periode yang ditanyakan."
    with open(mtk2_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print("✅ Fixed MTK_PAKET_2_SOLUTIONS_EXTRA Q21 and Q5.")
