import sys, time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

print("Connecting to Chrome on port 9222...")
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url.lower()][0]
    page.bring_to_front()

    print("1. Closing any open dialogs/overlays (pressing Escape and closing model selection)...")
    page.keyboard.press("Escape")
    time.sleep(1.0)
    
    # Check if model selection dialog is still open
    close_btns = page.locator("button[aria-label='Close dialog'], button:has-text('close')")
    for i in range(close_btns.count()):
        try:
            b = close_btns.nth(i)
            if b.is_visible() and ("close" in b.inner_text().lower() or "close" in (b.get_attribute("aria-label") or "").lower()):
                b.click()
                print("  Clicked close button")
                time.sleep(0.5)
                break
        except Exception:
            pass

    print("2. Removing Grounding with Google Search / any tools...")
    remove_chips = page.locator("button[aria-label*='Remove' i], button.tool-chip-button + button")
    print(f"  Found {remove_chips.count()} remove chip buttons")
    for i in range(remove_chips.count()):
        try:
            rc = remove_chips.nth(i)
            if rc.is_visible():
                aria = rc.get_attribute("aria-label") or ""
                print(f"  Clicking remove chip: '{aria}'")
                rc.click()
                time.sleep(0.5)
        except Exception as e:
            print(f"  Error clicking remove chip: {e}")

    # Check switches for tools
    switches = page.locator("button.mdc-switch--selected, [role='switch'][aria-checked='true']")
    print(f"  Found {switches.count()} active switches")
    for i in range(switches.count()):
        try:
            sw = switches.nth(i)
            if sw.is_visible():
                aria = sw.get_attribute("aria-label") or ""
                print(f"  Toggling off switch: '{aria}'")
                sw.click()
                time.sleep(0.5)
        except Exception as e:
            print(f"  Error toggling switch: {e}")

    # 3. Test typing into textarea
    print("3. Testing prompt injection into textarea...")
    textarea = page.locator("textarea[placeholder*='prompt' i], textarea").first
    textarea.click(force=True)
    time.sleep(0.5)
    test_msg = 'Katakan HANYA kata "BISMILLAH_BERHASIL" tanpa tanda kutip atau penjelasan apapun.'
    textarea.fill(test_msg)
    time.sleep(1.0)

    # 4. Click Run button
    print("4. Clicking Run button...")
    run_btn = page.locator("button:has-text('Run')").first
    print(f"  Run button text: '{run_btn.inner_text().strip()}'")
    run_btn.click()

    # 5. Wait for generation to start and finish
    print("5. Monitoring streaming...")
    started = False
    for _ in range(15):
        time.sleep(1.0)
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
        if stop_btn.count() > 0 and stop_btn.first.is_visible():
            started = True
            print("  Generation started! (Stop button is visible)")
            break
            
    if not started:
        print("  Warning: Stop button not detected yet, checking turns...")

    # Wait for completion (Stop button disappears)
    print("6. Waiting for generation to complete...")
    for _ in range(30):
        time.sleep(1.0)
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
        is_generating = (stop_btn.count() > 0 and stop_btn.first.is_visible())
        if not is_generating:
            print("  Generation completed!")
            break

    time.sleep(2.0)
    
    # 7. Extract the model's response
    print("7. Extracting response from DOM...")
    turns = page.locator("ms-chat-turn")
    print(f"  Total chat turns: {turns.count()}")
    if turns.count() > 0:
        last_turn = turns.last
        print("\n--- MODEL RESPONSE ---")
        print(last_turn.inner_text().strip())
        print("----------------------")
