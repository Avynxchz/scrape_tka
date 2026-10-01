import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pg = next(x for x in b.contexts[0].pages if "aistudio" in x.url.lower())
    
    # Close any open dialogs/overlays
    close_btns = pg.locator("button:has-text('close'), button:has-text('Skip'), button[aria-label*='Close' i]")
    for i in range(close_btns.count()):
        try:
            if close_btns.nth(i).is_visible():
                close_btns.nth(i).click()
                print("Clicked close/skip button")
        except Exception:
            pass

    # Look for "Models" tab/button
    models_btn = pg.locator("button:has-text('Models'), [role='tab']:has-text('Models'), div:has-text('Models')")
    print("Found 'Models' elements:", models_btn.count())
    for i in range(models_btn.count()):
        try:
            el = models_btn.nth(i)
            if el.is_visible() and el.inner_text().strip() == "Models":
                print(f"Clicking Models element {i}...")
                el.click()
                break
        except Exception as e:
            print("Click error:", e)

    pg.wait_for_timeout(2000)
    print("New Body snippet:")
    print("\n".join(pg.inner_text("body").splitlines()[:35]))
