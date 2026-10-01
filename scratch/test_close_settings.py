import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]
    
    close_btn = page.locator("button[aria-label*='Close run settings' i]")
    print("Close button count:", close_btn.count(), "visible:", close_btn.first.is_visible() if close_btn.count() > 0 else False)
    if close_btn.count() > 0 and close_btn.first.is_visible():
        close_btn.first.click(force=True)
        print("Clicked close run settings button!")
        time.sleep(1)
        print("After click, close button visible:", close_btn.first.is_visible() if close_btn.count() > 0 else False)
