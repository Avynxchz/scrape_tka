import glob, os
for f in sorted(glob.glob(r"D:\PROJECTS\SCRAPE_TKA\data\kunci\*.json")):
    import json
    d = json.load(open(f, encoding="utf-8"))
    print(os.path.basename(f), "| PG:", len(d["kunci_pg"]), "| BS:", d["kunci_bs"])
