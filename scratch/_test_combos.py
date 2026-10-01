import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pg = next(x for x in b.contexts[0].pages if "aistudio" in x.url.lower())
    buttons = pg.locator("button, a.nav-item, div[role='button']").all()
    print("Clickable elements found:", len(buttons))
    add_btn = buttons[9]
    print("Clicking element [9]:", add_btn.inner_text().strip())
    add_btn.click()
    pg.wait_for_timeout(2000)
    menu_items = pg.locator("button, [role='menuitem'], a").all()
    print("New elements after click:")
    for m in menu_items:
        t = m.inner_text().strip().replace('\n', ' ')
        if t and any(k in t.lower() for k in ['chat', 'prompt', 'model', 'freeform', 'structured']):
            print("  ->", t)
