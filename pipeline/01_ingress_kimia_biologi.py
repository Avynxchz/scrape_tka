# -*- coding: utf-8 -*-
"""pipeline/01_ingress_kimia_biologi.py — Automated Ingress (Divisi 1 & 2) for Kimia & Biologi.

Melakukan:
1. Playwright automated session: Login, refresh token, masuk bilik ujian.
2. Sedot seluruh HTML soal + unduh semua gambar PNG lokal ke data/<mapel>/paket_<n>/images/.
3. Langsung melompat ke nomor terakhir -> Submit tes -> Sedot tabel kunci resmi Pusmendik (review_hasil).
4. Normalisasi data ke Layer 2 Learning JSON (binding kunci resmi otoritatif & konversi KaTeX).
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
RAW_DIR = os.path.join(DATA_DIR, "raw_html")
os.makedirs(KUNCI_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

TARGETS = [
    {
        "slug": "kimia_paket_1",
        "mapel_key": "kimia",
        "paket": 1,
        "jenis": "2",
        "val": "9",
        "name": "Kimia (Paket 1)"
    },
    {
        "slug": "kimia_paket_2",
        "mapel_key": "kimia",
        "paket": 2,
        "jenis": "2",
        "val": "89",
        "name": "Kimia (Paket 2)"
    },
    {
        "slug": "biologi_paket_1",
        "mapel_key": "biologi",
        "paket": 1,
        "jenis": "2",
        "val": "10",
        "name": "Biologi (Paket 1)"
    },
    {
        "slug": "biologi_paket_2",
        "mapel_key": "biologi",
        "paket": 2,
        "jenis": "2",
        "val": "90",
        "name": "Biologi (Paket 2)"
    }
]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def download_image(img_rel_url, dest_path):
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
        except Exception:
            time.sleep(1)
    log(f"  [Warning] Gagal mengunduh gambar: {full_url}")
    return None


def run_ingress_for_target(t, headless=True):
    slug = t["slug"]
    mapel_key = t["mapel_key"]
    paket = t["paket"]
    jenis = t["jenis"]
    val = t["val"]
    name = t["name"]

    images_dir = os.path.join(DATA_DIR, mapel_key, f"paket_{paket}", "images")
    os.makedirs(images_dir, exist_ok=True)
    kunci_out = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
    learning_out = os.path.join(DATA_DIR, f"{slug}_learning.json")

    log(f"==================================================================")
    log(f"🚀 MEMULAI INGRESS DIVISI 1 & 2: {name} (ID: {val}, Slug: {slug})")
    log(f"==================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.on("dialog", lambda d: d.accept())

        # 1. Navigasi & Pemilihan Mapel
        log("1. Membuka simulasi Pusmendik...")
        page.goto(SIMULASI_URL, timeout=45000)
        time.sleep(2)

        page.select_option("#jenjang", "sma")
        time.sleep(1)
        page.select_option("#jenis_mapel", str(jenis))
        time.sleep(1.5)

        page.click("#mapel_toggle")
        time.sleep(1)
        opt_loc = page.locator(f".mapel-option[data-value='{val}']")
        if opt_loc.count() == 0:
            raise RuntimeError(f"Mapel value {val} ({name}) tidak ditemukan di dropdown!")
        opt_loc.first.scroll_into_view_if_needed()
        time.sleep(0.5)
        opt_loc.first.click()
        time.sleep(0.5)

        # 2. Login Demo
        log("2. Menuju halaman login...")
        page.click("button.custom-btn")
        page.wait_for_url(lambda u: "login" in u or "simulasi" in u, timeout=25000)
        page.click("button:has-text('Login')")
        page.wait_for_url(lambda u: "konfirmasi_data" in u, timeout=25000)

        # Tutup modal alert jika ada
        try:
            close_btn = page.locator(".modal.show .close, .swal2-close, button:has-text('Tutup')")
            if close_btn.count() > 0 and close_btn.first.is_visible():
                close_btn.first.click()
                time.sleep(1)
        except Exception:
            pass

        # 3. Refresh Token & Isi Form
        log("3. Merefresh token ujian...")
        page.locator("button:has-text('Refresh')").first.click()
        time.sleep(1.5)
        body_text = page.inner_text("body")
        m = re.search(r"Token\s*[:=]\s*([A-Z0-9]{6})", body_text, re.I)
        if not m:
            raise RuntimeError("Gagal menemukan token 6 karakter di halaman konfirmasi data!")
        token = m.group(1).upper()
        log(f"   -> Token didapat: {token}")

        page.fill("#nama_peserta", f"PESERTA {slug.upper()}")
        page.select_option("#tgl", "01")
        page.eval_on_selector("#bulan", "el => { el.selectedIndex = 1; el.dispatchEvent(new Event('change', {bubbles:true})); }")
        page.select_option("#tahun", "2005")
        page.fill("#input-token", token)
        time.sleep(1)

        page.locator("#btnSubmit").first.click()
        page.wait_for_url(lambda u: "konfirmasi_tes" in u, timeout=25000)
        page.click("button:has-text('Mulai')")

        # 4. Di Bilik Ujian - Ekstraksi Soal & Media
        log("4. Masuk ke bilik ujian... Menunggu elemen soal termuat...")
        page.wait_for_selector("#nextSoal", timeout=35000)
        page.wait_for_function("typeof window.lihatSoal === 'function' && typeof window.jumlah_soal !== 'undefined'", timeout=25000)
        time.sleep(2)

        total_soal = page.evaluate("() => window.jumlah_soal")
        log(f"   -> Terdeteksi {total_soal} soal pada bilik ujian.")

        exam_html = page.content()
        # Simpan raw HTML backup
        raw_file = os.path.join(RAW_DIR, f"{slug}.html")
        with open(raw_file, "w", encoding="utf-8") as f:
            f.write(exam_html)
        log(f"   -> Backup raw HTML disimpan ke {raw_file}")

        soup = BeautifulSoup(exam_html, "html.parser")
        soal_divs = soup.find_all("div", class_="soal-soal")
        log(f"   -> Ditemukan {len(soal_divs)} container soal di DOM.")

        parsed_soal = []
        total_images_saved = 0

        for idx, s_div in enumerate(soal_divs):
            q_num = idx + 1
            q_id = s_div.get("id", f"soal-no-{q_num}")

            # Stimulus
            cont_div = s_div.find("div", class_="cont-soal")
            stim_text = ""
            stim_images = []
            stim_html = ""
            if cont_div:
                for img_idx, img in enumerate(cont_div.find_all("img")):
                    src = img.get("src")
                    if src:
                        ext = os.path.splitext(src.split("?")[0])[-1] or ".png"
                        fn = f"soal_{q_num:02d}_stimulus_{img_idx+1:02d}{ext}"
                        local_path = os.path.join(images_dir, fn)
                        download_image(src, local_path)
                        total_images_saved += 1
                        rel_path = f"images/{fn}"
                        stim_images.append({
                            "filename": fn,
                            "rel_path": rel_path,
                            "remote_url": src if src.startswith("http") else f"{BASE_URL}{src}",
                            "data_latex": img.get("data-latex")
                        })
                        img["src"] = rel_path
                stim_text = cont_div.get_text(separator="\n", strip=True)
                stim_html = str(cont_div)

            # Pertanyaan & Opsi
            isi_div = s_div.find("div", class_="isi-soal")
            pertanyaan_text = ""
            pertanyaan_images = []
            pertanyaan_html = ""
            options = []
            pernyataan = []
            tipe_soal = "Pilihan Ganda"

            if isi_div:
                # Deteksi tabel opsi vs tabel data stimulus
                all_tables = isi_div.find_all("table")
                options_table = None
                for tbl in all_tables:
                    if tbl.find_all("input"):
                        options_table = tbl
                        break

                is_matrix = False
                matrix_cols = []
                has_checkbox = False

                if options_table:
                    # Ekstrak tabel opsi dari isi_div agar data table stimulus tetap utuh di pertanyaan
                    options_table.extract()

                    inputs = options_table.find_all("input")
                    has_checkbox = any(inp.get("type") == "checkbox" for inp in inputs)
                    unique_group_names = set(inp.get("name") for inp in inputs if inp.get("name"))

                    # Matriks HANYA jika ada beberapa grup radio independen per baris (len(unique_names) > 1)
                    if len(unique_group_names) > 1:
                        is_matrix = True
                        header_tr = options_table.find("thead")
                        if header_tr:
                            cols = [c.get_text(strip=True) for c in header_tr.find_all(["th", "td"]) if c.get_text(strip=True) and c.get_text(strip=True) not in ("#", "")]
                            if len(cols) >= 2:
                                matrix_cols = cols[1:]

                if is_matrix:
                    tipe_soal = "Benar-Salah" if any("benar" in c.lower() for c in matrix_cols) else "Matriks"
                elif has_checkbox:
                    tipe_soal = "Pilihan Ganda Kompleks"
                else:
                    tipe_soal = "Pilihan Ganda"

                pertanyaan_text = isi_div.get_text(separator="\n", strip=True)
                for p_idx, p_img in enumerate(isi_div.find_all("img")):
                    src = p_img.get("src")
                    if src:
                        ext = os.path.splitext(src.split("?")[0])[-1] or ".png"
                        fn = f"soal_{q_num:02d}_prompt_{p_idx+1:02d}{ext}"
                        local_path = os.path.join(images_dir, fn)
                        download_image(src, local_path)
                        total_images_saved += 1
                        rel_path = f"images/{fn}"
                        p_img["src"] = rel_path
                        pertanyaan_images.append({
                            "filename": fn,
                            "rel_path": rel_path,
                            "remote_url": src if src.startswith("http") else f"{BASE_URL}{src}",
                            "data_latex": p_img.get("data-latex")
                        })
                pertanyaan_html = str(isi_div)

                if options_table:
                    tbody = options_table.find("tbody") or options_table
                    rows = tbody.find_all("tr")
                    item_idx = 0
                    for row in rows:
                        inp = row.find("input")
                        if not inp:
                            continue
                        tds = row.find_all(["td", "th"])
                        if not tds:
                            continue
                        pil = inp.get("pil")
                        if pil and pil.isalpha():
                            pil_key_upper = pil.upper()
                        else:
                            pil_key_upper = chr(ord('A') + item_idx)
                        item_idx += 1

                        content_td = tds[1] if len(tds) > 1 else (tds[0] if tds else None)
                        opt_text = ""
                        opt_latex = None
                        opt_img_info = None

                        if content_td:
                            math_img = content_td.find("img")
                            if math_img:
                                opt_latex = math_img.get("data-latex")
                                src = math_img.get("src")
                                if src:
                                    ext = os.path.splitext(src.split("?")[0])[-1] or ".png"
                                    fn = f"soal_{q_num:02d}_opt_{pil_key_upper.lower()}{ext}"
                                    local_path = os.path.join(images_dir, fn)
                                    download_image(src, local_path)
                                    total_images_saved += 1
                                    rel_path = f"images/{fn}"
                                    opt_img_info = {
                                        "filename": fn,
                                        "rel_path": rel_path,
                                        "remote_url": src if src.startswith("http") else f"{BASE_URL}{src}",
                                        "data_latex": opt_latex
                                    }
                            opt_text = content_td.get_text(separator=" ", strip=True)

                        if is_matrix:
                            # Baris pernyataan dalam tabel matriks
                            if opt_text and opt_text.lower() not in ("pernyataan", "benar", "salah", "#", "variabel"):
                                pernyataan.append({
                                    "key": pil_key_upper,
                                    "text": opt_text,
                                    "latex": opt_latex,
                                    "image": opt_img_info
                                })
                        else:
                            options.append({
                                "key": pil_key_upper,
                                "text": opt_text,
                                "latex": opt_latex,
                                "image": opt_img_info,
                                "full_display": f"${opt_latex}$" if opt_latex else opt_text
                            })

            q_record = {
                "nomor": q_num,
                "id": q_id,
                "tipe_soal": tipe_soal,
                "stimulus": {
                    "text": stim_text,
                    "html": stim_html,
                    "images": stim_images
                },
                "pertanyaan": {
                    "text": pertanyaan_text,
                    "html": pertanyaan_html,
                    "images": pertanyaan_images
                }
            }
            if is_matrix and pernyataan:
                q_record["pernyataan"] = pernyataan
                if matrix_cols:
                    q_record["kolom_pilihan"] = matrix_cols
            else:
                q_record["pilihan_jawaban"] = options

            parsed_soal.append(q_record)

        log(f"   -> Parsed {len(parsed_soal)} soal, Total gambar diunduh: {total_images_saved}")

        # 5. Panen Kunci Otoritatif dari Pusmendik
        log(f"5. Melompat ke nomor {total_soal} untuk memanen kunci resmi...")
        page.evaluate(f"() => window.lihatSoal({total_soal})")
        time.sleep(1.5)

        inp = page.locator(f"#soal-no-{total_soal} input[type=radio], #soal-no-{total_soal} input[type=checkbox]")
        if inp.count() > 0:
            inp.first.click(force=True)
            time.sleep(1)

        log("   -> Klik #nextSoal menuju finish_tes...")
        page.click("#nextSoal")
        page.wait_for_url(lambda u: "finish_tes" in u, timeout=25000)
        time.sleep(1.5)

        log("   -> Di halaman finish_tes, klik SELESAI TES...")
        btn_selesai = page.locator("button", has_text="SELESAI TES").first
        btn_selesai.click()

        page.wait_for_url(lambda u: "review_hasil" in u, timeout=35000)
        log("   -> 🎉 BERHASIL MASUK review_hasil!")
        time.sleep(2)

        rev_content = page.content()
        rev_soup = BeautifulSoup(rev_content, "html.parser")
        rev_table = rev_soup.find("table")
        if not rev_table:
            raise RuntimeError("Tabel rekap kunci tidak ditemukan di halaman review_hasil!")

        kunci_pg = {}
        kunci_bs = {}
        bs_counts = {}
        raw_rows = {}

        rows = rev_table.find_all("tr")
        log(f"6. Mengekstrak {len(rows)-1} baris kunci resmi dari tabel Pusmendik...")
        for tr in rows[1:]:
            tds = tr.find_all("td")
            if len(tds) >= 3:
                no_str = re.sub(r"\D", "", tds[0].get_text(strip=True))
                if not no_str:
                    continue
                no = int(no_str)
                anda_txt = tds[1].get_text("\n", strip=True)
                kunci_txt = tds[2].get_text("\n", strip=True)
                raw_rows[str(no)] = {"anda": anda_txt, "kunci": kunci_txt}

                # Cek apakah kunci berupa pasangan baris-kategori multi-item: "A (X)\nB (Y)..."
                matrix_pairs = re.findall(r"([A-E])\s*\(([^)]+)\)", kunci_txt)
                if len(matrix_pairs) >= 2:
                    kunci_bs[str(no)] = {k.upper(): v.strip() for k, v in matrix_pairs}
                    bs_counts[str(no)] = len(matrix_pairs)
                else:
                    m_let = re.findall(r"\(([A-E])\)", kunci_txt)
                    if m_let:
                        kunci_pg[str(no)] = m_let[0] if len(m_let) == 1 else m_let
                    else:
                        m_raw = re.findall(r"\b([A-E])\b", kunci_txt)
                        if m_raw:
                            kunci_pg[str(no)] = m_raw[0]

        kunci_data = {
            "slug": slug,
            "mapel_id": val,
            "mapel_name": name,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_soal": len(raw_rows),
            "kunci_pg": kunci_pg,
            "kunci_bs": kunci_bs,
            "bs_statement_count": bs_counts,
            "raw_rows": raw_rows
        }
        with open(kunci_out, "w", encoding="utf-8") as f:
            json.dump(kunci_data, f, indent=2, ensure_ascii=False)
        log(f"   -> Kunci resmi disimpan ke {kunci_out}")

        # 6. Mengikat Kunci Resmi ke Layer 2 Learning JSON
        log("7. Mengikat kunci resmi ke Layer 2 Learning JSON...")
        for q in parsed_soal:
            no = q["nomor"]
            no_s = str(no)
            if no_s in kunci_bs:
                q["tipe_soal"] = "Benar-Salah" if any("benar" in v.lower() for v in kunci_bs[no_s].values()) else "Matriks"
                q["kunci_jawaban"] = [f"{k}:{v}" for k, v in sorted(kunci_bs[no_s].items())]
            elif no_s in kunci_pg:
                ans = kunci_pg[no_s]
                q["kunci_jawaban"] = ans
                if isinstance(ans, list) and len(ans) > 1:
                    q["tipe_soal"] = "Pilihan Ganda Kompleks"
            else:
                q["kunci_jawaban"] = "-"

        learning_doc = {
            "paket": paket,
            "mapel": mapel_key,
            "nama_paket": name,
            "total_soal": len(parsed_soal),
            "soal": parsed_soal
        }
        with open(learning_out, "w", encoding="utf-8") as f:
            json.dump(learning_doc, f, indent=2, ensure_ascii=False)
        log(f"   -> Layer 2 Learning JSON tersimpan ke {learning_out}")

        browser.close()

    log(f"✅ [SUKSES TUNTAS] Ingress untuk {name} SELESAI TANPA CACAT!\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingress Kimia & Biologi")
    parser.add_argument("--target", type=str, default="all",
                        choices=["all", "kimia_paket_1", "kimia_paket_2", "biologi_paket_1", "biologi_paket_2"])
    parser.add_argument("--headless", type=bool, default=True)
    args = parser.parse_args()

    selected = TARGETS if args.target == "all" else [t for t in TARGETS if t["slug"] == args.target]
    for target in selected:
        for attempt in range(1, 4):
            try:
                ok = run_ingress_for_target(target, headless=args.headless)
                if ok:
                    break
            except Exception as e:
                log(f"❌ Error attempt {attempt} untuk {target['name']}: {e}")
                time.sleep(3)
