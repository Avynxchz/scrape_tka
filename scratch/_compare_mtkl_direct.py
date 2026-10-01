import sys
import json
import re
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_pkg_options(pkg):
    html_file = f"data/raw_html/matematika_lanjut_paket_{pkg}.html"
    json_file = f"data/matematika_lanjut_paket_{pkg}_learning.json"
    
    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    with open(json_file, encoding="utf-8") as f:
        d = json.load(f)
        
    print(f"\n=======================================================")
    print(f"AUDIT MTK LANJUT PAKET {pkg} DIRECTLY AGAINST RAW PUSMENDIK")
    print(f"=======================================================")
    
    for q in d["soal"]:
        qnum = q["nomor"]
        # Find inputs in raw html for this question
        # Inputs might be named pilihan{qnum} or similar
        inps = soup.find_all("input", attrs={"name": re.compile(rf"^pilihan{qnum}$")})
        if not inps:
            inps = soup.find_all("input", attrs={"name": re.compile(rf"^pilihan_{qnum}_")})
            
        json_opts = q.get("pilihan_jawaban", [])
        
        # If there are inputs and options
        if inps and json_opts:
            for inp, j_opt in zip(inps, json_opts):
                pil = inp.get("pil", "").upper()
                tr = inp.find_parent("tr")
                tds = tr.find_all("td") if tr else []
                content_td = tds[-1] if tds else None
                raw_inner = ""
                if content_td:
                    raw_inner = "".join(str(c) for c in content_td.contents if not str(c).strip().startswith("<?xml"))
                    raw_inner = re.sub(r"<!--[\s\S]*?-->", "", raw_inner).strip()
                    
                j_disp = j_opt.get("full_display") or j_opt.get("text") or j_opt.get("latex")
                j_img = j_opt.get("image", {}).get("filename") if j_opt.get("image") else None
                
                # Check discrepancy
                # If raw_inner has img and text, let's see how it compares
                has_img_raw = "<img" in raw_inner
                has_img_json = bool(j_img)
                
                # Print any question where raw has img or data-latex or complex structure
                if has_img_raw or j_opt.get("latex") or "<table" in raw_inner:
                    print(f"Q{qnum} [{pil}]:")
                    print(f"   RAW HTML: {raw_inner}")
                    print(f"   JSON OPT: text={repr(j_opt.get('text'))}, latex={repr(j_opt.get('latex'))}, img={j_img}")

if __name__ == "__main__":
    check_pkg_options(1)
    check_pkg_options(2)
