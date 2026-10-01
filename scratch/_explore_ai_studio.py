import sys, time, json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

print("Connecting to Chrome on port 9222...")
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    
    # List all open tabs
    print(f"Total open pages: {len(context.pages)}")
    for i, pg in enumerate(context.pages):
        print(f"  Page {i}: {pg.title()} | URL: {pg.url}")
        
    ai_pages = [pg for pg in context.pages if "aistudio.google.com" in pg.url.lower()]
    if not ai_pages:
        print("No AI Studio page found! Opening new one...")
        page = context.new_page()
        page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded")
    else:
        page = ai_pages[0]
        page.bring_to_front()
        
    print(f"\nActive AI Studio Page: {page.url}")
    print(f"Title: {page.title()}")
    
    # 1. Inspect all buttons on the page
    buttons = page.locator("button")
    btn_count = buttons.count()
    print(f"\nTotal buttons on page: {btn_count}")
    run_buttons = []
    new_chat_buttons = []
    tool_buttons = []
    
    for i in range(btn_count):
        try:
            b = buttons.nth(i)
            if not b.is_visible():
                continue
            txt = b.inner_text().strip().replace('\n', ' ')
            aria = b.get_attribute("aria-label") or ""
            cls = b.get_attribute("class") or ""
            
            if "run" in txt.lower() or "run" in aria.lower():
                run_buttons.append((i, txt, aria, cls))
            if "new" in txt.lower() or "new" in aria.lower() or "plus" in cls.lower():
                new_chat_buttons.append((i, txt, aria, cls))
            if any(k in txt.lower() or k in aria.lower() for k in ["tool", "search", "code", "grounding"]):
                tool_buttons.append((i, txt, aria, cls))
        except Exception:
            pass
            
    print("\n--- RUN BUTTONS ---")
    for b in run_buttons:
        print(f"  Index {b[0]}: Text='{b[1]}' | Aria='{b[2]}' | Class='{b[3][:40]}'")
        
    print("\n--- NEW CHAT BUTTONS ---")
    for b in new_chat_buttons:
        print(f"  Index {b[0]}: Text='{b[1]}' | Aria='{b[2]}' | Class='{b[3][:40]}'")
        
    print("\n--- TOOL BUTTONS / TOGGLES ---")
    for b in tool_buttons:
        print(f"  Index {b[0]}: Text='{b[1]}' | Aria='{b[2]}' | Class='{b[3][:40]}'")
        
    # 2. Inspect slide toggles (Tools are usually mat-slide-toggle)
    toggles = page.locator("mat-slide-toggle, input[type='checkbox']")
    print(f"\nTotal slide toggles / checkboxes: {toggles.count()}")
    for i in range(toggles.count()):
        try:
            t = toggles.nth(i)
            vis = t.is_visible()
            txt = t.inner_text().strip().replace('\n', ' ')
            aria = t.get_attribute("aria-label") or ""
            checked = t.get_attribute("aria-checked") or t.is_checked()
            print(f"  Toggle {i}: visible={vis}, checked={checked}, text='{txt}', aria='{aria}'")
        except Exception as e:
            print(f"  Toggle {i} error: {e}")
            
    # 3. Inspect Input / Textarea
    inputs = page.locator("textarea, [contenteditable='true']")
    print(f"\nTotal inputs: {inputs.count()}")
    for i in range(inputs.count()):
        try:
            inp = inputs.nth(i)
            vis = inp.is_visible()
            ph = inp.get_attribute("placeholder") or ""
            print(f"  Input {i}: visible={vis}, placeholder='{ph}'")
        except Exception as e:
            print(f"  Input {i} error: {e}")
            
    # 4. Check File input
    file_inps = page.locator("input[type='file']")
    print(f"\nTotal file inputs: {file_inps.count()}")
    
    # 5. Check overlays / dialogs / banners
    overlays = page.locator(".cdk-overlay-container, mat-dialog-container, .modal, [role='dialog'], .banner")
    print(f"\nTotal overlays/dialogs: {overlays.count()}")
    for i in range(overlays.count()):
        try:
            ov = overlays.nth(i)
            if ov.is_visible():
                print(f"  Visible overlay {i}: {ov.inner_text()[:100]}...")
        except Exception as e:
            print(f"  Overlay {i} error: {e}")
