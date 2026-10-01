import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]
    
    btn = page.locator("button[aria-label*='Insert images, videos, audio, or files' i]")
    if btn.is_visible():
        btn.click()
        page.wait_for_timeout(1000)
        menu_items = page.locator("div[role='menu'] button, .mat-mdc-menu-content button, mat-menu button")
        print(f"Menu items count: {menu_items.count()}")
        for i in range(menu_items.count()):
            print(f"Item {i}: {menu_items.nth(i).inner_text().strip().replace('\n', ' ')}")
