from playwright.sync_api import sync_playwright
import os
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    
    # Filter AI studio pages
    ai_pages = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url]
    if not ai_pages:
        print("No AI Studio tab found!")
        exit(0)
    
    page = ai_pages[0]
    page.bring_to_front()
    print("Using page:", page.url)

    # 1. Test Thinking Level Setting
    print("\n1. Testing Thinking Level...")
    thinking_select = page.locator("mat-select[aria-label='Thinking Level'], mat-select:has-text('Thinking')")
    if thinking_select.count() > 0:
        curr_val = thinking_select.first.inner_text().strip()
        print(f"Current thinking level: '{curr_val}'")
        if "High" not in curr_val:
            print("Switching to High...")
            thinking_select.first.click()
            time.sleep(0.5)
            # Find mat-option with High
            opt = page.locator("mat-option:has-text('High')")
            if opt.count() > 0:
                opt.first.click()
                print("Clicked 'High' option!")
            else:
                print("High option not found in dropdown!")
        else:
            print("Thinking level is ALREADY High!")
    else:
        print("Thinking select not directly visible, opening settings panel...")
        toggle = page.locator("button.runsettings-toggle-button")
        if toggle.is_visible():
            toggle.click()
            time.sleep(1)
            thinking_select = page.locator("mat-select[aria-label='Thinking Level'], mat-select:has-text('Thinking')")
            print("After toggle, thinking select count:", thinking_select.count())

    # 2. Test Tab cleanup logic
    print(f"\n2. Total tabs before cleanup: {len(context.pages)}")
    ai_tabs = [pg for pg in context.pages if "aistudio.google.com" in pg.url]
    print(f"Total AI Studio tabs: {len(ai_tabs)}")
    # If more than 1 AI studio tab, we can keep the first and close the others
    for extra_page in ai_tabs[1:]:
        print(f"Closing redundant tab: {extra_page.url[:60]}")
        extra_page.close()
    print(f"Total tabs after cleanup: {len(context.pages)}")

    # 3. Test File input
    test_file = os.path.abspath("scratch/test_prompt.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Halo Gemini! Ini adalah file uji coba injeksi prompt via upload file.")

    file_input = page.locator("input[type='file']")
    print(f"\n3. File input count: {file_input.count()}")
    if file_input.count() > 0:
        print("Attaching test file...")
        file_input.first.set_input_files(test_file)
        time.sleep(2)
        print("File attached! Checking UI for attached file chip/badge...")
        chips = page.locator("mat-chip, ms-file-chunk, .file-chip, [aria-label*='test_prompt']")
        print(f"Attached chips count: {chips.count()}")
        for i in range(chips.count()):
            print(f"Chip {i}: {chips.nth(i).inner_text()}")
