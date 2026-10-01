import sys, json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    pages = [pg for pg in context.pages if "aistudio.google.com" in pg.url.lower()]
    print(f"Found {len(pages)} AI Studio pages")
    if not pages:
        sys.exit(0)
    page = pages[0]
    print("Page URL:", page.url)
    print("Page Title:", page.title())

    # Check for modals / dialogs / banners
    dialogs = page.locator("mat-dialog-container, .modal, [role='dialog'], .cdk-overlay-pane")
    print(f"Open dialogs/overlays count: {dialogs.count()}")
    for i in range(min(5, dialogs.count())):
        try:
            d = dialogs.nth(i)
            if d.is_visible():
                print(f"  Visible Dialog {i}: {d.inner_text()[:150]}...")
        except Exception as e:
            print(f"  Dialog {i} error: {e}")

    # Check input box
    inputs = page.locator("textarea, [contenteditable='true']")
    print(f"Found {inputs.count()} input/textarea elements:")
    for i in range(inputs.count()):
        inp = inputs.nth(i)
        vis = inp.is_visible()
        tag = inp.evaluate("el => el.tagName")
        placeholder = inp.get_attribute("placeholder") or ""
        print(f"  Input {i}: visible={vis}, tag={tag}, placeholder='{placeholder}'")

    # Check buttons
    run_btn = page.locator("button:has-text('Run'), button[aria-label*='Run' i]")
    stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
    print(f"Run button visible: {run_btn.count() > 0 and run_btn.first.is_visible()}")
    print(f"Stop button visible: {stop_btn.count() > 0 and stop_btn.first.is_visible()}")

    # Check chat turns count
    turns = page.locator("ms-chat-turn")
    print(f"Chat turns count: {turns.count()}")

    # Check if there are tool chips or settings
    tools = page.locator("ms-tool-chip, mat-slide-toggle, .tool-toggle")
    print(f"Tools toggles/chips count: {tools.count()}")
