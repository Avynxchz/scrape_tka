# -*- coding: utf-8 -*-
import json, os, sys
sys.path.insert(0, ".")
import solution_loader

reg = json.load(open("data/solution_sources/registry.json", encoding="utf-8"))
for slug, info in sorted(reg.items()):
    if not isinstance(info, dict):
        continue
    sol_fn = info.get("active_source")
    with open(os.path.join("data/solution_sources", sol_fn), encoding="utf-8") as f:
        doc = json.load(f)

    # find learning json
    for lrn in os.listdir("data"):
        if lrn.endswith("_learning.json"):
            prefix = lrn.replace("_learning.json", "")
            norm_prefix = (prefix.replace("bahasa_inggris", "bing")
                                .replace("ekonomi", "eko")
                                .replace("kewirausahaan", "pkw")
                                .replace("geografi", "geo")
                                .replace("kimia", "kim")
                                .replace("biologi", "bio")
                                .replace("matematika_lanjut", "mtkl")
                                .replace("matematika", "mtk"))
            if prefix == slug or norm_prefix == slug:
                ldoc = json.load(open(os.path.join("data", lrn), encoding="utf-8"))
                soal_map = {q["nomor"]: q for q in ldoc.get("soal", [])}
                for s in doc.get("solutions", []):
                    qnum = s.get("question_number")
                    if qnum in soal_map and s.get("official_answer"):
                        q = soal_map[qnum]
                        kunci = q.get("kunci_jawaban")
                        cc = solution_loader.cross_check_keys(s, kunci)
                        if not cc.get("match"):
                            print(f"[{slug} Q{qnum}] {cc.get('detail')}")
