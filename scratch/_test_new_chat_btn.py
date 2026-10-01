from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    page = browser.contexts[0].pages[0]
    print('Before click:', page.url)
    btn = page.locator("button[aria-label='New chat']")
    print('New chat button count:', btn.count())
    if btn.count() > 0:
        btn.first.click()
        time.sleep(2)
        print('After click:', page.url)
        page.screenshot(path='scratch/_after_new_chat_click.png')
