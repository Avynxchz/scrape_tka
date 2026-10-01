from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
for i, pg in enumerate(b.contexts[0].pages):
    print(f"Page {i}: {pg.url}")
p.stop()
