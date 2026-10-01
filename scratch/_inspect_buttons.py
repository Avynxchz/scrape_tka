from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    page = browser.contexts[0].pages[0]
    print('URL:', page.url)
    btns = page.locator('button')
    print(f'Total buttons: {btns.count()}')
    for i in range(btns.count()):
        b = btns.nth(i)
        lbl = b.get_attribute('aria-label') or b.inner_text() or ''
        if any(k in lbl.lower() for k in ['new', 'chat', 'explore', 'code', 'run', 'plus', 'add', 'tune', 'settings']):
            print(f'   Button {i}: aria-label="{b.get_attribute("aria-label")}" text="{b.inner_text().strip()}"')
