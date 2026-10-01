import os
import json
import time

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
DATA_DIR = os.path.join(BASE_DIR, "data")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
REG_PATH = os.path.join(SOL_DIR, "registry.json")

def load_or_reconstruct_kunci(slug, kunci_path=None):
    if kunci_path and os.path.isfile(kunci_path):
        try:
            with open(kunci_path, "r", encoding="utf-8") as f:
                doc = json.load(f)
            if doc.get("kunci_pg") or doc.get("kunci_bs"):
                return doc
        except Exception:
            pass

    sol_file = None
    if os.path.isfile(REG_PATH):
        try:
            with open(REG_PATH, "r", encoding="utf-8") as f:
                reg = json.load(f)
            if slug in reg and "active_source" in reg[slug]:
                candidate = os.path.join(SOL_DIR, reg[slug]["active_source"])
                if os.path.isfile(candidate):
                    sol_file = candidate
        except Exception:
            pass

    if not sol_file:
        candidate = os.path.join(SOL_DIR, f"{slug.upper()}_SOLUTIONS.json")
        if os.path.isfile(candidate):
            sol_file = candidate

    if not sol_file and os.path.isdir(SOL_DIR):
        for fn in os.listdir(SOL_DIR):
            if fn.lower().startswith(slug.lower()) and fn.endswith(".json"):
                sol_file = os.path.join(SOL_DIR, fn)
                break

    if sol_file and os.path.isfile(sol_file):
        with open(sol_file, "r", encoding="utf-8") as f:
            sol_data = json.load(f)
        kunci_pg = {}
        kunci_bs = {}
        raw_rows = {}
        for s in sol_data.get("solutions", []):
            q_num = str(s.get("question_number", 0))
            oa = s.get("official_answer")
            if not oa or not isinstance(oa, dict):
                continue
            fmt = oa.get("format", "")
            corr = oa.get("correct")
            if fmt in ("per_statement_benar_salah", "per_statement") or isinstance(corr, dict) or (isinstance(corr, list) and any(":" in str(x) for x in corr)):
                bs_dict = {}
                if isinstance(corr, list):
                    for item in corr:
                        if ":" in str(item):
                            k, v = str(item).split(":", 1)
                            bs_dict[k.strip().upper()] = v.strip()
                elif isinstance(corr, dict):
                    bs_dict = {k.strip().upper(): str(v).strip() for k, v in corr.items()}
                if bs_dict:
                    kunci_bs[q_num] = bs_dict
                    raw_rows[q_num] = {"kunci": "\n".join(f"{k} ({v})" for k, v in bs_dict.items())}
            elif fmt in ("multiple_correct", "multiple") or isinstance(corr, list):
                arr = [str(x).strip().upper() for x in corr]
                kunci_pg[q_num] = arr
                raw_rows[q_num] = {"kunci": "\n".join(f"({x})" for x in arr)}
            elif corr is not None:
                c_str = str(corr).strip().upper()
                kunci_pg[q_num] = c_str
                raw_rows[q_num] = {"kunci": f"({c_str})"}

        doc = {
            "slug": slug,
            "mapel_id": "1",
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kunci_pg": kunci_pg,
            "kunci_bs": kunci_bs,
            "raw_rows": raw_rows
        }
        if kunci_path:
            with open(kunci_path, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
        return doc

    return {"slug": slug, "kunci_pg": {}, "kunci_bs": {}, "raw_rows": {}}

if __name__ == "__main__":
    kunci_path = os.path.join(KUNCI_DIR, "sejarah_paket_1_kunci.json")
    doc = load_or_reconstruct_kunci("sejarah_paket_1", kunci_path)
    print("Reconstructed kunci for sejarah_paket_1:")
    print("kunci_pg:", json.dumps(doc["kunci_pg"], indent=2))
    print("kunci_bs:", json.dumps(doc["kunci_bs"], indent=2))
