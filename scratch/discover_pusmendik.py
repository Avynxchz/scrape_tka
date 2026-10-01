import time, json
from playwright.sync_api import sync_playwright

BASE_URL = "https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/"

def discover_subjects():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Navigating to {BASE_URL}...")
        page.goto(BASE_URL, timeout=45000)
        time.sleep(2)
        
        # 1. Inspect SMA Wajib (jenis_mapel = 1)
        page.select_option("#jenjang", "sma")
        page.select_option("#jenis_mapel", "1")
        time.sleep(1)
        
        page.click("#mapel_toggle")
        time.sleep(0.5)
        wajib_opts = page.query_selector_all(".mapel-option")
        wajib_list = []
        for opt in wajib_opts:
            val = opt.get_attribute("data-value")
            text = opt.inner_text().strip()
            wajib_list.append({"val": val, "name": text})
        results["sma_wajib"] = wajib_list
        page.click("#mapel_toggle") # close
        time.sleep(0.5)
        
        # 2. Inspect SMA Pilihan (jenis_mapel = 2)
        page.select_option("#jenis_mapel", "2")
        time.sleep(1)
        
        page.click("#mapel_toggle")
        time.sleep(0.5)
        pilihan_opts = page.query_selector_all(".mapel-option")
        pilihan_list = []
        for opt in pilihan_opts:
            val = opt.get_attribute("data-value")
            text = opt.inner_text().strip()
            pilihan_list.append({"val": val, "name": text})
        results["sma_pilihan"] = pilihan_list
        
        browser.close()
        
    print(json.dumps(results, indent=2, ensure_ascii=False))
    with open("scratch/pusmendik_catalog.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    discover_subjects()
