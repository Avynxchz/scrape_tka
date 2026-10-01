import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]
    
    # Check copy/download/export buttons in the UI
    btns = page.locator("button, a")
    print(f"Total elements: {btns.count()}")
    for i in range(btns.count()):
        el = btns.nth(i)
        aria = el.get_attribute("aria-label") or ""
        txt = el.inner_text().strip().replace('\n', ' ')
        title = el.get_attribute("title") or ""
        all_text = f"{txt} {aria} {title}".lower()
        if any(w in all_text for w in ["export", "download", "copy", "get code", "share", "save"]):
            print(f"Button {i}: txt='{txt}', aria='{aria}', title='{title}'")
