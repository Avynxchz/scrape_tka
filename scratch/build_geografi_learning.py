import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from _repair_keys import parse_official_row
RAW_PATH = os.path.join(ROOT, "data", "geografi", "paket_1", "geografi_paket_1.json")
KUNCI_PATH = os.path.join(ROOT, "data", "kunci", "geografi_paket_1_kunci.json")
OUT_PATH = os.path.join(ROOT, "data", "geografi_paket_1_learning.json")

def main():
    with open(RAW_PATH, encoding="utf-8") as f:
        raw_data = json.load(f)
    with open(KUNCI_PATH, encoding="utf-8") as f:
        kunci_data = json.load(f)
        
    raw_rows = kunci_data["raw_rows"]
    questions = []
    
    for q in raw_data["soal"]:
        no = q["nomor"]
        s = dict(q)
        row = raw_rows.get(str(no))
        if not row:
            raise ValueError(f"No official row for question {no}")
        
        kind, payload = parse_official_row(row["kunci"])
        
        if kind == "bs":
            s["tipe_soal"] = "Benar-Salah"
            opts = {o["key"]: o for o in s.get("pilihan_jawaban", [])}
            pernyataan = []
            for stmt_key, src_key in zip(["A", "B", "C"], ["B", "C", "D"]):
                src = opts.get(src_key, {})
                item = {"key": stmt_key}
                if src.get("text"):
                    item["text"] = src["text"].strip()
                if src.get("latex"):
                    item["latex"] = src["latex"]
                if src.get("image"):
                    item["image"] = src["image"]
                pernyataan.append(item)
            s["pernyataan"] = pernyataan
            s.pop("pilihan_jawaban", None)
            s["kunci_jawaban"] = [f"{k}:{payload[k]}" for k in ["A", "B", "C"] if k in payload]
            
        elif kind == "multi":
            s["tipe_soal"] = "Pilihan Ganda Kompleks"
            s["kunci_jawaban"] = sorted(payload)
            for opt in s.get("pilihan_jawaban", []):
                opt["full_display"] = opt.get("text", "")
                
        elif kind == "single":
            s["tipe_soal"] = "Pilihan Ganda"
            s["kunci_jawaban"] = payload[0]
            for opt in s.get("pilihan_jawaban", []):
                opt["full_display"] = opt.get("text", "")
                
        questions.append(s)
        
    out_doc = {
        "paket": "Geografi Paket 1",
        "total_soal": len(questions),
        "soal": questions
    }
    
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out_doc, f, ensure_ascii=False, indent=2)
    print(f"Successfully generated {OUT_PATH} with {len(questions)} questions!")

if __name__ == "__main__":
    main()
