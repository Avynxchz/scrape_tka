import json
import time
from playwright.sync_api import sync_playwright

SIMULASI_URL = "https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/"

def discover():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Navigating to {SIMULASI_URL}...")
        page.goto(SIMULASI_URL, timeout=45000)
        page.wait_for_timeout(2000)
        
        page.select_option("#jenjang", "sma")
        page.wait_for_timeout(1000)
        page.select_option("#jenis_mapel", "2")
        page.wait_for_timeout(2500)
        
        native_opts = page.eval_on_selector_all(
            "#mapel option",
            "els => els.map(o => ({text: o.textContent.trim(), value: o.value}))"
        )
        print(f"Found {len(native_opts)} native options for SMA Pilihan:")
        for opt in native_opts:
            if opt["value"]:
                print(f"  ID: {opt['value']:<5} Name: {opt['text']}")
                
        page.click("#mapel_toggle")
        page.wait_for_timeout(1000)
        custom_opts = page.eval_on_selector_all(
            ".mapel-option",
            "els => els.map(o => ({text: o.textContent.trim(), value: o.getAttribute('data-value')}))"
        )
        print(f"\nFound {len(custom_opts)} custom dropdown options:")
        for opt in custom_opts:
            if "geo" in opt["text"].lower():
                print(f"  --> MATCH GEOGRAFI: ID: {opt['value']} | Name: {opt['text']}")
                
        browser.close()

if __name__ == "__main__":
    discover()
