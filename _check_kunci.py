import glob, os
kunci_pattern = os.path.join(os.path.dirname(__file__), "data", "kunci", "*.json")
for f in sorted(glob.glob(kunci_pattern)):
    import json
    d = json.load(open(f, encoding="utf-8"))
    print(os.path.basename(f), "| PG:", len(d["kunci_pg"]), "| BS:", d["kunci_bs"])
