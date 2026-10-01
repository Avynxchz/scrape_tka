import json
import re
from bs4 import BeautifulSoup

def compare_raw_vs_json(pkg):
    html_path = f"data/raw_html/matematika_lanjut_paket_{pkg}.html"
    json_path = f"data/matematika_lanjut_paket_{pkg}_learning.json"
    
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"==================================================")
    print(f"COMPARING MTK LANJUT PAKET {pkg}")
    print(f"==================================================")
    
    # In Pusmendik raw html, check each question element
    # Let's inspect how questions/options are structured in the HTML
    items = soup.find_all("div", class_="item") or soup.find_all("div", class_="soal-item")
    if not items:
        # Let's look for how options are marked in HTML
        tables = soup.find_all("table")
        print(f"Total tables found: {len(tables)}")
        
    # Let's inspect each question in json
    for q in data["soal"]:
        num = q["nomor"]
        tipe = q["tipe"]
        opts = q.get("pilihan_jawaban", [])
        print(f"\n--- Q{num} ({tipe}) ---")
        if opts:
            for o in opts:
                print(f"  [{o.get('key')}]: text='{o.get('text')}' | latex='{o.get('latex')}' | full='{o.get('full_display')}'")
        else:
            print("  (No pilihan_jawaban, checking pernyataan / table_headers)")
            if q.get("table_headers"):
                print("  Headers:", q.get("table_headers"))
            if q.get("pernyataan"):
                for p in q.get("pernyataan"):
                    print("  Pernnyataan:", p)

if __name__ == "__main__":
    compare_raw_vs_json(1)
    compare_raw_vs_json(2)
