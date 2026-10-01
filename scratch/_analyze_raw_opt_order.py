import sys
import re
from bs4 import BeautifulSoup, NavigableString

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def analyze_raw_options(pkg):
    with open(f"data/raw_html/matematika_lanjut_paket_{pkg}.html", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    print(f"\n=======================================================")
    print(f"PUSMENDIK RAW OPTIONS STRUCTURE FOR PAKET {pkg}")
    print(f"=======================================================")
    
    inputs = soup.find_all("input", attrs={"name": re.compile(r"^pilihan")})
    q_inputs = {}
    for inp in inputs:
        name = inp.get("name", "")
        m = re.search(r"pilihan(\d+)", name)
        if m:
            qnum = int(m.group(1))
            q_inputs.setdefault(qnum, []).append(inp)
            
    for qnum in sorted(q_inputs.keys()):
        inps = q_inputs[qnum]
        print(f"\n--- Soal {qnum} (total opsi: {len(inps)}) ---")
        for inp in inps:
            pil = inp.get("pil", "")
            tr = inp.find_parent("tr")
            if tr:
                tds = tr.find_all("td")
                if len(tds) >= 2:
                    content_td = tds[1]
                    parts = []
                    for elem in content_td.descendants:
                        if elem.name == "img":
                            parts.append(f"<IMG: {elem.get('src', '')}>")
                        elif isinstance(elem, NavigableString):
                            text = str(elem).strip()
                            if text and not text.startswith("?xml"):
                                parts.append(f"TEXT:'{text}'")
                    print(f"  Opsi {pil.upper()}: {' + '.join(parts)}")

if __name__ == "__main__":
    analyze_raw_options(1)
    analyze_raw_options(2)
