# -*- coding: utf-8 -*-
"""_harvest_keys.py — Harvest official answer keys from Pusmendik CBT.
Robust implementation matching Matematika Paket 2 standard.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import re
import json
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://pusmendik.kemendikdasmen.go.id"
SIMULASI_URL = f"{BASE_URL}/tka/simulasi_tka/"
ROOT = os.path.dirname(os.path.abspath(__file__))
KUNCI_DIR = os.path.join(ROOT, "data", "kunci")
os.makedirs(KUNCI_DIR, exist_ok=True)

TARGETS = [
    {"slug": "geografi_paket_2", "jenis": "2", "val": "93", "name": "Geografi Paket 2"},
    {"slug": "fisika_paket_1", "jenis": "2", "val": "8", "name": "Fisika Paket 1"},
    {"slug": "fisika_paket_2", "jenis": "2", "val": "88", "name": "Fisika Paket 2"}
]

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def harvest_target(target, headless=True):
    slug = target["slug"]
    jenis = target["jenis"]
    val = target["val"]
    name = target["name"]
    out_file = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")

    log(f"==================================================")
    log(f"[HARVEST] Memulai panen kunci resmi: {name} (ID {val})")
    log(f"==================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.on("dialog", lambda d: d.accept())

        log("1. Buka simulasi_tka...")
        page.goto(SIMULASI_URL, timeout=45000)
        time.sleep(2)

        page.select_option("#jenjang", "sma")
        time.sleep(1)
        page.select_option("#jenis_mapel", str(jenis))
        time.sleep(2)

        page.click("#mapel_toggle")
        time.sleep(1)
        loc = page.locator(f".mapel-option[data-value='{val}']")
        if loc.count() == 0:
            raise RuntimeError(f"Mapel value {val} not found in dropdown!")
        loc.first.scroll_into_view_if_needed()
        time.sleep(0.5)
        loc.first.click()
        time.sleep(0.5)

        selected_label = page.inner_text("#mapel_selected_label")
        log(f"   -> Terpilih: {selected_label}")

        log("2. Login...")
        page.click("button.custom-btn")
        page.wait_for_url(lambda u: "login" in u or "simulasi" in u, timeout=20000)
        page.click("button:has-text('Login')")
        page.wait_for_url(lambda u: "konfirmasi_data" in u, timeout=20000)

        log("3. Refresh token...")
        page.locator("button:has-text('Refresh')").first.click()
        time.sleep(1.5)
        m = re.search(r"Token\s*[:=]\s*([A-Z0-9]{6})", page.inner_text("body"), re.I)
        token = m.group(1).upper()
        log(f"   -> Token: {token}")

        log("4. Isi form & submit...")
        page.fill("#nama_peserta", "PESERTA RESMI TKA")
        page.select_option("#tgl", "01")
        page.eval_on_selector("#bulan", "el => { el.selectedIndex = 1; el.dispatchEvent(new Event('change', {bubbles:true})); }")
        page.select_option("#tahun", "2005")
        page.fill("#input-token", token)
        time.sleep(1)

        page.locator("#btnSubmit").first.click()
        page.wait_for_url(lambda u: "konfirmasi_tes" in u, timeout=25000)
        page.click("button:has-text('Mulai')")
        page.wait_for_selector("#nextSoal", timeout=30000)
        log("   -> Di Bilik Ujian!")

        # Tunggu sampai script Pusmendik (lihatSoal & jumlah_soal) termuat penuh
        log("5. Menunggu inisialisasi script ujian Pusmendik...")
        page.wait_for_function("typeof window.lihatSoal === 'function' && typeof window.jumlah_soal !== 'undefined'", timeout=20000)
        total_soal = page.evaluate("() => window.jumlah_soal")
        log(f"   -> Total soal terdeteksi: {total_soal}")

        # Lompat ke soal terakhir
        log(f"6. Lompat ke soal nomor {total_soal}...")
        page.evaluate(f"() => window.lihatSoal({total_soal})")
        time.sleep(1.5)

        # Klik opsi soal terakhir dengan force=True
        inp = page.locator(f"#soal-no-{total_soal} input[type=radio], #soal-no-{total_soal} input[type=checkbox]")
        if inp.count() > 0:
            inp.first.click(force=True)
            time.sleep(1)

        log("7. Klik #nextSoal pada nomor terakhir -> Menuju finish_tes...")
        page.click("#nextSoal")

        page.wait_for_url(lambda u: "finish_tes" in u, timeout=25000)
        log("   -> Di halaman finish_tes! Klik SELESAI TES...")
        time.sleep(1.5)

        btn_sel = page.locator("button", has_text="SELESAI TES").first
        btn_sel.click()

        page.wait_for_url(lambda u: "review_hasil" in u, timeout=30000)
        log("   -> 🎉 REACHED review_hasil!")
        time.sleep(2)

        # Parse tabel review hasil Pusmendik
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        table = soup.find("table")
        if not table:
            raise RuntimeError("Table review not found on review_hasil!")

        kunci_pg = {}
        kunci_bs = {}
        bs_statement_counts = {}
        raw_rows = {}

        rows = table.find_all("tr")
        log(f"8. Mengekstrak {len(rows)-1} baris kunci resmi dari tabel Pusmendik...")
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

                # Benar-Salah format: "A (Benar)\nB (Salah)\nC (Benar)"
                bs_pairs = re.findall(r"([A-E])\s*\((Benar|Salah)\)", kunci_txt, re.IGNORECASE)
                if bs_pairs:
                    kunci_bs[str(no)] = {k.upper(): v.capitalize() for k, v in bs_pairs}
                    bs_statement_counts[str(no)] = len(bs_pairs)
                else:
                    # PG
                    m = re.findall(r"\(([A-E])\)", kunci_txt)
                    if m:
                        kunci_pg[str(no)] = m[0] if len(m) == 1 else m
                    else:
                        m_raw = re.findall(r"\b([A-E])\b", kunci_txt)
                        if m_raw:
                            kunci_pg[str(no)] = m_raw[0]

        result_data = {
            "slug": slug,
            "mapel_id": val,
            "mapel_name": name,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_soal": len(raw_rows),
            "kunci_pg": kunci_pg,
            "kunci_bs": kunci_bs,
            "bs_statement_count": bs_statement_counts,
            "raw_rows": raw_rows
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        log(f"🎉 [SUKSES] Kunci resmi {name} berhasil disimpan!")
        log(f"   -> Total: {len(raw_rows)} soal, PG: {len(kunci_pg)}, B-S: {len(kunci_bs)}")
        log(f"   -> File: {out_file}\n")

        browser.close()
        return True

if __name__ == "__main__":
    target_arg = sys.argv[1] if len(sys.argv) > 1 else None
    targets_to_run = [t for t in TARGETS if t["slug"] == target_arg] if target_arg else TARGETS
    for t in targets_to_run:
        for attempt in range(1, 4):
            try:
                ok = harvest_target(t, headless=True)
                if ok:
                    break
            except Exception as e:
                log(f"❌ Error attempt {attempt} for {t['name']}: {e}")
                time.sleep(3)
