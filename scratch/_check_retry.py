import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
pg = b.contexts[0].pages[0]
retry_btns = pg.locator("button:has-text('Retry'), button[aria-label*='Retry' i], button:has-text('Regenerate')")
print("Retry buttons count:", retry_btns.count())
for i in range(retry_btns.count()):
    b_el = retry_btns.nth(i)
    print(i, repr(b_el.inner_text()), repr(b_el.get_attribute('aria-label')), b_el.is_visible())
p.stop()
