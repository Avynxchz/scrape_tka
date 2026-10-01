import glob
import json
import os
import re
from bs4 import BeautifulSoup, NavigableString

raw_files = sorted(glob.glob("data/raw_html/*.html"))
raw_files = [f for f in raw_files if not f.endswith("_review.html")]

findings = []

for h_path in raw_files:
    slug = os.path.basename(h_path).replace(".html", "")
    learning_path = f"data/{slug}_learning.json"
    if not os.path.exists(learning_path):
        continue
        
    with open(h_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    with open(learning_path, encoding="utf-8") as f:
        learning = json.load(f)
        
    soal_list = learning["soal"] if isinstance(learning, dict) and "soal" in learning else learning
    soal_map = {q.get("nomor"): q for q in soal_list}
    
    # Find all option tables or question blocks in soup
    inputs = soup.find_all("input", attrs={"name": re.compile(r"^pilihan")})
    # Group inputs by question number
    q_inps = {}
    for inp in inputs:
        name = inp.get("name", "")
        m = re.search(r"pilihan_?(\d+)", name)
        if m:
            qnum = int(m.group(1))
            q_inps.setdefault(qnum, []).append(inp)
            
    for qnum, inps in q_inps.items():
        q_data = soal_map.get(qnum)
        if not q_data:
            continue
            
        opts = q_data.get("pilihan_jawaban", [])
        if not opts:
            continue
            
        for inp in inps:
            pil = inp.get("pil", "").upper()
            opt_obj = next((o for o in opts if o.get("key") == pil), None)
            if not opt_obj:
                continue
                
            tr = inp.find_parent("tr")
            tds = tr.find_all("td") if tr else []
            if len(tds) < 2:
                continue
            content_td = tds[-1]
            
            # Extract raw structure
            raw_text = content_td.get_text(" ", strip=True)
            raw_text = re.sub(r"\?xml.*?\?", "", raw_text).strip()
            imgs = content_td.find_all("img")
            
            # Check 1: Inline formula inside text (like MTKL P1 Q7)
            # If imgs have data-latex and there is surrounding text
            for img in imgs:
                latex = img.get("data-latex")
                if latex:
                    # check if latex is in opt_obj text or full_display
                    full_d = opt_obj.get("full_display", "")
                    t_val = opt_obj.get("text", "")
                    if latex not in full_d and latex not in t_val:
                        findings.append({
                            "slug": slug,
                            "qnum": qnum,
                            "pil": pil,
                            "type": "MISSING_INLINE_LATEX",
                            "latex": latex,
                            "raw_text": raw_text,
                            "current_text": t_val,
                            "current_full": full_d
                        })
                        
            # Check 2: Img position vs text position (like MTKL P2 Q21)
            # If img does NOT have data-latex, but is an image, check order
            non_latex_imgs = [im for im in imgs if not im.get("data-latex")]
            if non_latex_imgs and raw_text:
                first_img = non_latex_imgs[0]
                img_pos = str(content_td).find(str(first_img)[:30])
                # find text pos
                words = raw_text.split()
                if words:
                    text_pos = str(content_td).find(words[0])
                    order = "img_first" if img_pos < text_pos else "text_first"
                    if order == "img_first":
                        findings.append({
                            "slug": slug,
                            "qnum": qnum,
                            "pil": pil,
                            "type": "IMG_BEFORE_TEXT",
                            "raw_text": raw_text,
                            "img_src": first_img.get("src"),
                            "current_text": opt_obj.get("text")
                        })

print(f"\n=======================================================")
print(f"OMNI RAW AUDIT FINDINGS: {len(findings)} ISSUES DETECTED")
print(f"=======================================================")
for f in findings:
    print(f"[{f['type']}] {f['slug']} Q{f['qnum']} Opsi {f['pil']}:")
    for k, v in f.items():
        if k not in ["slug", "qnum", "pil", "type"]:
            print(f"   {k}: {repr(v)}")
