import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath("."))

from playwright.sync_api import sync_playwright

SIMULASI_URL = "https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/"

def test_language_values():
    test_targets = [
        {"name": "Bahasa Arab P1", "jenis": "2", "val": "22"},
        {"name": "Bahasa Jerman P1", "jenis": "2", "val": "18"},
        {"name": "Bahasa Prancis P1", "jenis": "2", "val": "17"},
        {"name": "Bahasa Jepang P1", "jenis": "2", "val": "19"},
        {"name": "Bahasa Mandarin P1", "jenis": "2", "val": "20"},
        {"name": "Bahasa Korea P1", "jenis": "2", "val": "21"},
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to Pusmendik...")
        page.goto(SIMULASI_URL, timeout=30000)
        page.wait_for_selector("#jenis_mapel", timeout=15000)
        
        # Select Jenjang SMA (value 2)
        page.select_option("#jenjang", "2")
        page.wait_for_timeout(1000)
        
        for t in test_targets:
            # Select Jenis
            page.select_option("#jenis_mapel", t["jenis"])
            page.wait_for_timeout(800)
            
            # Check if option with value exists in #mapel
            opt = page.locator(f"#mapel option[value='{t['val']}']")
            count = opt.count()
            text = opt.inner_text() if count > 0 else "NOT FOUND"
            print(f"Target {t['name']} (val={t['val']}): found={count > 0} -> text='{text}'")
            
        browser.close()

if __name__ == "__main__":
    test_language_values()
