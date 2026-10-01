from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]
    
    toggle = page.locator("button.runsettings-toggle-button")
    if toggle.is_visible():
        print("Clicking runsettings-toggle-button...")
        toggle.click()
        time.sleep(2)
        
    # Check text in the newly opened settings panel
    panel = page.locator("ms-prompt-run-settings, .run-settings-container, mat-drawer")
    print("Panel count:", panel.count())
    for i in range(panel.count()):
        print(f"Panel {i} text:\n{panel.nth(i).inner_text()[:400]}")
