import json

def inspect_pkg(pkg_num):
    json_path = f"data/matematika_lanjut_paket_{pkg_num}_learning.json"
    
    with open(json_path, encoding="utf-8") as f:
        d = json.load(f)
    
    soal_list = d["soal"] if isinstance(d, dict) and "soal" in d else d
    print(f"\n=================== MTK LANJUT PAKET {pkg_num} ({len(soal_list)} soal) ===================")
    for q in soal_list:
        num = q.get("nomor") or q.get("number")
        qtype = q.get("jenis") or q.get("question_type") or q.get("type")
        opts = q.get("opsi") or q.get("options") or []
        ans = q.get("kunci") or q.get("answer") or q.get("correct_answer")
        print(f"\nQ{num} [Jenis: {qtype}] [Kunci: {ans}]")
        if isinstance(opts, list):
            for i, opt in enumerate(opts):
                if isinstance(opt, dict):
                    print(f"  {opt.get('key') or opt.get('label') or i}: {str(opt.get('text') or opt.get('isi') or opt)[:100]}")
                else:
                    print(f"  [{i}]: {str(opt)[:100]}")
        elif isinstance(opts, dict):
            for k, v in opts.items():
                print(f"  {k}: {str(v)[:100]}")

if __name__ == "__main__":
    inspect_pkg(1)
    inspect_pkg(2)
