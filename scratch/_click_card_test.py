from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    page = browser.contexts[0].pages[0]
    print('URL before:', page.url)
    
    # Locate Code and Chat card
    card = page.locator("text='Code and Chat'").first
    print('Card count:', card.count())
    if card.count() > 0:
        print('Clicking card...')
        card.click(force=True)
        time.sleep(3)
        print('URL after:', page.url)
        page.screenshot(path='scratch/_after_click_card.png')
