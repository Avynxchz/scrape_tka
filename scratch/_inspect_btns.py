from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
pg = b.contexts[0].pages[-1]
print('URL:', pg.url)
sel = "button:has-text('Stop'), button[aria-label*='Cancel' i], button[aria-label*='Stop' i]"
btns = pg.locator(sel)
print('Count:', btns.count())
for i in range(btns.count()):
    el = btns.nth(i)
    print(i, repr(el.inner_text()), repr(el.get_attribute('aria-label')), el.is_visible())
b.close()
p.stop()
