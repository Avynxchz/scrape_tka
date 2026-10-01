from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print("Current URL:", page.url)
    
    # Coba klik 'Code and Chat'
    card = page.locator("text='Code and Chat'")
    if card.count() > 0:
        print("Clicking Code and Chat card...")
        card.first.click()
        time.sleep(4)
        print("New URL:", page.url)
        page.screenshot(path="scratch/_zero_after_code_and_chat.png")
    else:
        print("Card Code and Chat not found")
