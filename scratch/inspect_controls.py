from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    pages = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url]
    if not pages:
        print("No AI studio prompt page found!")
        exit(0)
    page = pages[0]
    
    print("Page URL:", page.url)
    print("Page Title:", page.title())

    # 1. Open settings panel if closed
    toggle = page.locator("button.runsettings-toggle-button")
    if toggle.is_visible():
        # Check if settings panel is expanded
        panel = page.locator("ms-prompt-run-settings, .run-settings-container")
        if panel.count() == 0 or not panel.first.is_visible():
            print("Opening settings panel...")
            toggle.click()
            page.wait_for_timeout(1000)

    # Search for thinking level controls
    print("\n--- THINKING LEVEL CONTROLS ---")
    elements = page.locator("mat-select, div[role='combobox'], ms-dropdown, [aria-label*='thinking' i], [aria-label*='Thinking' i]")
    print(f"Candidate dropdowns count: {elements.count()}")
    for i in range(elements.count()):
        el = elements.nth(i)
        txt = el.inner_text().replace('\n', ' ')
        aria = el.get_attribute("aria-label") or ""
        print(f"Dropdown {i}: text='{txt}', aria='{aria}', tag={el.evaluate('e => e.tagName')}")

    # Search specifically near text 'Thinking level'
    tl_container = page.locator("*:has-text('Thinking level')")
    print(f"Elements containing 'Thinking level': {tl_container.count()}")
    for i in range(min(5, tl_container.count())):
        el = tl_container.nth(i)
        print(f"TL {i}: tag={el.evaluate('e => e.tagName')}, class={el.evaluate('e => e.className')}")

    # 2. File inputs and upload buttons
    print("\n--- FILE UPLOAD CONTROLS ---")
    inputs = page.locator("input[type='file']")
    print(f"Input type=file count: {inputs.count()}")
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        print(f"File input {i}: id='{inp.get_attribute('id')}', accept='{inp.get_attribute('accept')}'")

    # Look for insert / upload button in toolbar / chat footer
    buttons = page.locator("button")
    print(f"Total buttons: {buttons.count()}")
    for i in range(buttons.count()):
        btn = buttons.nth(i)
        txt = btn.inner_text().strip().replace('\n', ' ')
        aria = btn.get_attribute("aria-label") or ""
        if any(w in txt.lower() or w in aria.lower() for w in ["insert", "upload", "file", "attach", "add", "drive", "media"]):
            print(f"Upload-related button {i}: text='{txt}', aria='{aria}'")
