from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    page = browser.contexts[0].pages[0]
    print('Before:', page.url)
    gemini_btn = page.locator("text='Gemini 3.8 Flash'").first
    if gemini_btn.count() > 0:
        gemini_btn.click(force=True)
        time.sleep(3)
        print('After:', page.url)
        page.screenshot(path='scratch/_after_click_gemini_38.png')
