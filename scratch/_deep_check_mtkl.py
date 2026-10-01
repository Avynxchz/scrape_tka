import sys
import json
import re
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_html_options(pkg):
    html_path = f"data/raw_html/matematika_lanjut_paket_{pkg}.html"
    json_path = f"data/matematika_lanjut_paket_{pkg}_learning.json"
    
    with open(html_path, encoding="utf-8") as f:
        raw_html = f.read()
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
        
    soup = BeautifulSoup(raw_html, "html.parser")
    
    print(f"\n=======================================================")
    print(f"CHECKING MTK LANJUT PAKET {pkg}")
    print(f"=======================================================")
    
    # In Pusmendik, options are often inside table or div with radio/checkbox
    # Let's inspect all tables and inputs/labels in raw_html
    # Let's find all question blocks
    # Often in Pusmendik HTML: <div class="col-lg-6 isi-soal"> or similar
    isi_soal_divs = soup.find_all("div", class_=re.compile(r"isi-soal|cont-soal"))
    print(f"Total isi-soal/cont-soal divs: {len(isi_soal_divs)}")
    
    # Also let's check review html!
    rev_path = f"data/raw_html/matematika_lanjut_paket_{pkg}_review.html"
    try:
        with open(rev_path, encoding="utf-8") as f:
            rev_soup = BeautifulSoup(f.read(), "html.parser")
        rev_rows = rev_soup.find_all("tr")
        print(f"Total review rows: {len(rev_rows)}")
    except Exception as e:
        print(f"Review html error: {e}")

    # Inspect each question in json
    for q in data["soal"]:
        num = q["nomor"]
        tipe = q["tipe"]
        opts = q.get("pilihan_jawaban", [])
        pernyataan = q.get("pernyataan", [])
        tbl_headers = q.get("table_headers", [])
        
        # Check if question has tables or complex layout in its html
        q_html = (q.get("pertanyaan", {}).get("html") or "") + (q.get("stimulus", {}).get("html") or "")
        has_table = "<table" in q_html.lower()
        has_grid = "display: flex" in q_html.lower() or "grid" in q_html.lower() or "col-" in q_html.lower()
        
        print(f"\n[Q{num}] Tipe: {tipe} | Opts: {len(opts)} | Pernyataan: {len(pernyataan)} | Headers: {tbl_headers} | HasTable: {has_table}")
        if opts:
            keys = [o.get("key") for o in opts]
            texts = [o.get("text") or o.get("latex") or "" for o in opts]
            print(f"   Keys: {keys}")
            for o in opts:
                print(f"     {o.get('key')}: text={repr(o.get('text'))[:60]}, latex={repr(o.get('latex'))[:60]}")
        if pernyataan:
            for p in pernyataan:
                print(f"     Pernyataan {p.get('key')}: {repr(p.get('text'))[:60]}")

if __name__ == "__main__":
    check_html_options(1)
    check_html_options(2)
