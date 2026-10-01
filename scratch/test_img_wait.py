import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    page.goto('http://localhost:8080/?subject=matematika_lanjut&paket=2')
    page.wait_for_load_state('networkidle')
    page.evaluate('state.currentIndex = 20; renderQuestion();')
    time.sleep(1.0)
    page.screenshot(path='scratch/screenshots/mtl_p2_q21_loaded.png')
    browser.close()
print("Saved mtl_p2_q21_loaded.png")
