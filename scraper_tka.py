import os
import re
import json
import time
import argparse
import urllib.request
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://pusmendik.kemendikdasmen.go.id"
SIMULASI_URL = f"{BASE_URL}/tka/simulasi_tka/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_image(img_rel_url, dest_path):
    """Download an image from Pusmendik relative URL and save locally."""
    if not img_rel_url:
        return None
    full_url = img_rel_url if img_rel_url.startswith("http") else f"{BASE_URL}{img_rel_url}"
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return dest_path

    for attempt in range(3):
        try:
            req = urllib.request.Request(full_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    with open(dest_path, "wb") as f:
                        f.write(resp.read())
                    return dest_path
        except Exception as e:
            time.sleep(1)
    print(f"  [Warning] Failed to download {full_url}")
    return None

def fetch_exam_html_via_playwright(mapel_val, jenis_mapel="1", headless=True):
    """
    Automates the entire simulation flow:
    1. Select SMK (sma) -> Jenis Mapel (jenis_mapel: 1=Wajib, 2=Pilihan) -> Mapel (mapel_val)
    2. Click Mulai Simulasi
    3. Click Login
    4. Refresh & read Token, fill participant data, Submit
    5. Click Mulai Tes
    6. Return the full HTML containing all questions
    """
    print(f"\n[Playwright] Launching browser (headless={headless})...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        
        print(f"[1/5] Navigating to {SIMULASI_URL}...")
        page.goto(SIMULASI_URL, timeout=45000)
        time.sleep(2)
        
        # Select SMK (sma) & Jenis Mapel
        page.select_option("#jenjang", "sma")
        page.select_option("#jenis_mapel", str(jenis_mapel))
        time.sleep(1)
        
        # Open custom dropdown and click the specific package
        page.click("#mapel_toggle")
        time.sleep(0.5)
        mapel_sel = f".mapel-option[data-value='{mapel_val}']"
        page.wait_for_selector(mapel_sel, timeout=10000)
        page.click(mapel_sel)
        time.sleep(0.5)
        
        selected_label = page.inner_text("#mapel_selected_label")
        print(f"[2/5] Selected subject: {selected_label} (ID: {mapel_val})")
        
        # Click Mulai Simulasi
        print("[2/5] Clicking 'Mulai Simulasi' and redirecting to Login...")
        page.click("button.custom-btn")
        page.wait_for_url(lambda u: "login" in u or "simulasi" in u, timeout=20000)
        time.sleep(2)
        
        # Check login page
        print("[3/5] On login page, clicking 'Login'...")
        page.click("button:has-text('Login'), input[value='Login']")
        page.wait_for_url(lambda u: "konfirmasi_data" in u, timeout=20000)
        time.sleep(2)
        
        # Dismiss any modal / alert if visible
        try:
            close_btn = page.locator(".modal.show .close, .swal2-close, button:has-text('Tutup')")
            if close_btn.count() > 0 and close_btn.is_visible():
                print("[Info] Closing popup notification...")
                close_btn.click()
                time.sleep(1)
        except Exception:
            pass
            
        # Refresh token 1x as recommended
        print("[4/5] Refreshing test token...")
        refresh_btn = page.locator("button:has-text('Refresh'), a:has-text('Refresh')")
        if refresh_btn.count() > 0:
            refresh_btn.click()
            time.sleep(1.5)
            
        body_text = page.inner_text("body")
        token_match = re.search(r"Token\s*:\s*([A-Z0-9]+)", body_text)
        if not token_match:
            raise RuntimeError(f"Could not extract token from page: {body_text[:300]}")
        token_val = token_match.group(1)
        print(f"[4/5] Extracted refreshed token: {token_val}")
        
        # Fill Konfirmasi Data Peserta
        page.fill("#nama_peserta", "Peserta Simulasi")
        page.select_option("#tgl", "01")
        page.select_option("#bulan", "01")
        page.select_option("#tahun", "2005")
        page.fill("#input-token", token_val)
        time.sleep(0.5)
        
        print("[4/5] Submitting participant confirmation...")
        page.click("button:has-text('Submit'), input[value='Submit']")
        time.sleep(2)
        
        # Konfirmasi Tes page
        print("[5/5] Clicking 'Mulai' on Konfirmasi Tes...")
        page.click("button:has-text('Mulai'), input[value='Mulai'], a:has-text('Mulai')")
        time.sleep(3)
        
        # Wait for questions to load
        page.wait_for_selector(".soal-soal, #soal-no-1", timeout=30000)
        print("[5/5] Exam page loaded successfully!")
        
        # Extract the full innerHTML of container
        exam_html = page.evaluate("""() => {
            const card = document.querySelector('.card-body, #soal, .content-soal, .box-body') || document.body;
            return card.innerHTML;
        }""")
        
        browser.close()
        return exam_html

def parse_and_save_exam(exam_html, paket_name, output_dir):
    """
    Parses questions, stimulus, formulas, and options from exam HTML,
    downloads all referenced images, and outputs JSON and Markdown files.
    """
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    soup = BeautifulSoup(exam_html, "html.parser")
    soal_divs = soup.find_all("div", class_="soal-soal")
    print(f"\n[Parser] Found {len(soal_divs)} questions in {paket_name}.")
    
    parsed_questions = []
    
    for idx, s_div in enumerate(soal_divs):
        q_num = idx + 1
        q_id = s_div.get("id", f"soal-no-{q_num}")
        
        # 1. Stimulus / Context (cont-soal)
        cont_div = s_div.find("div", class_="cont-soal")
        stimulus_text = ""
        stimulus_images = []
        if cont_div:
            # Process stimulus images
            for img_idx, img in enumerate(cont_div.find_all("img")):
                src = img.get("src")
                if src:
                    ext = os.path.splitext(src.split("?")[0])[-1] or ".png"
                    img_filename = f"soal_{q_num:02d}_stimulus_{img_idx+1:02d}{ext}"
                    local_img_path = os.path.join(images_dir, img_filename)
                    download_image(src, local_img_path)
                    rel_path = f"images/{img_filename}"
                    stimulus_images.append({
                        "filename": img_filename,
                        "rel_path": rel_path,
                        "remote_url": src if src.startswith("http") else f"{BASE_URL}{src}"
                    })
                    # Replace in html representation
                    img["src"] = rel_path
            stimulus_text = cont_div.get_text(separator="\n", strip=True)
            stimulus_html = str(cont_div)
        else:
            stimulus_html = ""
            
        # 2. Pertanyaan & Opsi (isi-soal)
        isi_div = s_div.find("div", class_="isi-soal")
        if not isi_div:
            continue
            
        # Determine question type
        has_checkbox = len(isi_div.find_all("input", {"type": "checkbox"})) > 0
        tipe_soal = "Pilihan Ganda Kompleks" if has_checkbox else "Pilihan Ganda"
        
        # Separate prompt paragraph(s) from options table
        prompt_paras = []
        for p in isi_div.find_all("p", recursive=False):
            prompt_paras.append(p.get_text(separator=" ", strip=True))
        pertanyaan_text = "\n".join(prompt_paras) if prompt_paras else ""
        
        # Check for images in prompt
        prompt_images = []
        for p_img_idx, p_img in enumerate(isi_div.find_all("img", recursive=False)):
            src = p_img.get("src")
            if src:
                ext = os.path.splitext(src.split("?")[0])[-1] or ".png"
                img_filename = f"soal_{q_num:02d}_prompt_{p_img_idx+1:02d}{ext}"
                local_img_path = os.path.join(images_dir, img_filename)
                download_image(src, local_img_path)
                rel_path = f"images/{img_filename}"
                prompt_images.append({
                    "filename": img_filename,
                    "rel_path": rel_path,
                    "remote_url": src if src.startswith("http") else f"{BASE_URL}{src}"
                })
        
        # 3. Extract Options from table
        options = []
        table = isi_div.find("table")
        if table:
            rows = table.find_all("tr")
            for r_idx, row in enumerate(rows):
                # Look for input
                inp = row.find("input")
                pil_key = inp.get("pil", chr(ord('a') + r_idx)) if inp else chr(ord('a') + r_idx)
                pil_key_upper = pil_key.upper()
                
                # Second td contains label/text/math
                tds = row.find_all("td")
                content_td = tds[1] if len(tds) > 1 else (tds[0] if tds else None)
                
                opt_text = ""
                opt_latex = None
                opt_img_info = None
                
                if content_td:
                    # Check for math image with data-latex
                    math_img = content_td.find("img")
                    if math_img:
                        opt_latex = math_img.get("data-latex")
                        img_src = math_img.get("src")
                        if img_src:
                            ext = os.path.splitext(img_src.split("?")[0])[-1] or ".png"
                            img_filename = f"soal_{q_num:02d}_opsi_{pil_key.lower()}{ext}"
                            local_img_path = os.path.join(images_dir, img_filename)
                            download_image(img_src, local_img_path)
                            opt_img_info = {
                                "filename": img_filename,
                                "rel_path": f"images/{img_filename}",
                                "remote_url": img_src if img_src.startswith("http") else f"{BASE_URL}{img_src}"
                            }
                    opt_text = content_td.get_text(separator=" ", strip=True)
                    
                options.append({
                    "key": pil_key_upper,
                    "text": opt_text,
                    "latex": opt_latex,
                    "image": opt_img_info
                })
                
        parsed_questions.append({
            "nomor": q_num,
            "id": q_id,
            "tipe_soal": tipe_soal,
            "stimulus": {
                "text": stimulus_text,
                "images": stimulus_images,
                "html": stimulus_html
            },
            "pertanyaan": {
                "text": pertanyaan_text,
                "images": prompt_images
            },
            "pilihan_jawaban": options
        })
    
    # Save to JSON
    json_path = os.path.join(output_dir, f"{paket_name.lower().replace(' ', '_')}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "paket": paket_name,
            "total_soal": len(parsed_questions),
            "soal": parsed_questions
        }, f, ensure_ascii=False, indent=2)
    print(f"[Output] JSON saved to: {json_path}")
    
    # Save to Markdown
    md_path = os.path.join(output_dir, f"{paket_name.lower().replace(' ', '_')}.md")
    write_markdown(parsed_questions, paket_name, md_path)
    print(f"[Output] Markdown saved to: {md_path}")
    
    return parsed_questions

def write_markdown(questions, paket_name, md_path):
    """Formats parsed questions into a clean, human-readable Markdown file."""
    lines = [
        f"# Kumpulan Soal Simulasi TKA - {paket_name}",
        f"**Jenjang:** SMK / SMA / MA / Sederajat (Mata Pelajaran Wajib)",
        f"**Total Soal:** {len(questions)} butir",
        f"**Sumber:** Portal Pusmendik Kemendikdasmen (Simulasi ANBK / TKA)",
        "\n---\n"
    ]
    
    for q in questions:
        q_num = q["nomor"]
        tipe = q["tipe_soal"]
        lines.append(f"## Soal No. {q_num} `[{tipe}]`\n")
        
        # Stimulus
        stim = q["stimulus"]
        if stim["text"]:
            lines.append("### Stimulus / Bacaan:")
            lines.append(stim["text"])
            lines.append("")
        if stim["images"]:
            for img in stim["images"]:
                lines.append(f"![Diagram Stimulus Soal {q_num}]({img['rel_path']})\n")
                
        # Pertanyaan
        pertanyaan = q["pertanyaan"]
        if pertanyaan["text"]:
            lines.append("### Pertanyaan:")
            lines.append(pertanyaan["text"])
            lines.append("")
        if pertanyaan["images"]:
            for img in pertanyaan["images"]:
                lines.append(f"![Gambar Pertanyaan Soal {q_num}]({img['rel_path']})\n")
                
        # Opsi Pilihan Jawaban
        options = q["pilihan_jawaban"]
        if options:
            lines.append("### Pilihan Jawaban:")
            for opt in options:
                key = opt["key"]
                content_parts = []
                if opt["latex"]:
                    content_parts.append(f"${opt['latex']}$")
                if opt["text"] and opt["text"] != opt.get("latex"):
                    content_parts.append(opt["text"])
                if opt["image"]:
                    content_parts.append(f"![Opsi {key}]({opt['image']['rel_path']})")
                
                content_str = " ".join(content_parts) if content_parts else "(Opsi kosong)"
                bullet = f"- **[{key}]** {content_str}"
                lines.append(bullet)
            lines.append("")
            
        lines.append("\n---\n")
        
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    parser = argparse.ArgumentParser(description="Scraper Soal Simulasi TKA Pusmendik")
    parser.add_argument("--subject", type=str, default="all",
                        choices=["all", "matematika", "bahasa_inggris", "ekonomi", "kewirausahaan"],
                        help="Pilih mapel untuk di-scrape")
    parser.add_argument("--paket", type=str, default="all", choices=["1", "2", "all"],
                        help="Pilih paket: '1', '2', atau 'all'")
    parser.add_argument("--headless", type=bool, default=True, help="Jalankan browser headless atau terlihat")
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    catalog = {
        "matematika": [
            {"val": "7", "jenis": "1", "name": "Matematika Paket 1", "output": os.path.join(base_dir, "data", "paket_1")},
            {"val": "82", "jenis": "1", "name": "Matematika Paket 2", "output": os.path.join(base_dir, "data", "paket_2")}
        ],
        "bahasa_inggris": [
            {"val": "3", "jenis": "1", "name": "Bahasa Inggris Paket 1", "output": os.path.join(base_dir, "data", "bahasa_inggris", "paket_1")},
            {"val": "84", "jenis": "1", "name": "Bahasa Inggris Paket 2", "output": os.path.join(base_dir, "data", "bahasa_inggris", "paket_2")}
        ],
        "ekonomi": [
            {"val": "12", "jenis": "2", "name": "Ekonomi Paket 1", "output": os.path.join(base_dir, "data", "ekonomi", "paket_1")},
            {"val": "92", "jenis": "2", "name": "Ekonomi Paket 2", "output": os.path.join(base_dir, "data", "ekonomi", "paket_2")}
        ],
        "kewirausahaan": [
            {"val": "23", "jenis": "2", "name": "Kewirausahaan Paket 1", "output": os.path.join(base_dir, "data", "kewirausahaan", "paket_1")},
            {"val": "103", "jenis": "2", "name": "Kewirausahaan Paket 2", "output": os.path.join(base_dir, "data", "kewirausahaan", "paket_2")}
        ]
    }
    
    tasks = []
    selected_subjects = list(catalog.keys()) if args.subject == "all" else [args.subject]
    
    for subj in selected_subjects:
        for idx, item in enumerate(catalog[subj], start=1):
            if args.paket == "all" or args.paket == str(idx):
                tasks.append(item)
        
    for t in tasks:
        print("="*60)
        print(f"Memulai scraping: {t['name']} (ID: {t['val']}, Jenis: {t['jenis']})")
        print(f"Output folder: {t['output']}")
        print("="*60)
        html_content = fetch_exam_html_via_playwright(t["val"], jenis_mapel=t["jenis"], headless=args.headless)
        parse_and_save_exam(html_content, t["name"], t["output"])
        print(f"\n[Selesai] Berhasil mengekstrak {t['name']}!")
        
    print("\n" + "="*60)
    print("SELURUH PROSES SCRAPING TELAH SELESAI DENGAN SUKSES!")
    print("="*60)

if __name__ == "__main__":
    main()
