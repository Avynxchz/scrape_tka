import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:8080/?subject=matematika_lanjut&paket=2')
    page.wait_for_load_state('networkidle')
    page.evaluate('state.currentIndex = 20; renderQuestion();')
    time.sleep(0.3)
    opts_html = page.evaluate('() => Array.from(document.querySelectorAll(".option-item")).map(el => el.innerHTML)')
    for idx, h in enumerate(opts_html):
        print(f"Option {idx}:", h)
    browser.close()
