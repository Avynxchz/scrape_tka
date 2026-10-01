import glob
import json
import os
import re
from bs4 import BeautifulSoup

raw_html_files = glob.glob("data/raw_html/*.html")
findings = []

for html_file in raw_html_files:
    if "_review" in html_file:
        continue
    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    inputs = soup.find_all("input", attrs={"name": re.compile(r"^pilihan")})
    for inp in inputs:
        tr = inp.find_parent("tr")
        if not tr:
            continue
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        content_td = tds[-1]
        
        # Check order of text and img
        img = content_td.find("img")
        text = content_td.get_text(" ", strip=True)
        # remove xml comments
        text = re.sub(r"\?xml.*?\?", "", text).strip()
        
        if img and text:
            # Check which appears first in DOM
            img_pos = str(content_td).find("<img")
            # find text pos
            first_word = text.split()[0]
            text_pos = str(content_td).find(first_word)
            
            order = "img_first" if img_pos < text_pos else "text_first"
            findings.append((os.path.basename(html_file), inp.get("name"), inp.get("pil"), order, text[:40], img.get("src")[:40]))

print(f"Total options with BOTH image and text: {len(findings)}")
for f in findings:
    print(f"File: {f[0]} | Input: {f[1]} {f[2]} | Order: {f[3]} | Text: '{f[4]}' | Img: {f[5]}")
