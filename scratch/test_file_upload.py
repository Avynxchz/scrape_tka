import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import os
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]

    test_file = os.path.abspath("scratch/sample_prompt.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Halo ini isi prompt dari file sample_prompt.txt")

    file_input = page.locator("input[type='file']")
    print("Setting input files...")
    file_input.first.set_input_files(test_file)
    time.sleep(3)

    # Check all elements with sample_prompt
    matches = page.locator("*:has-text('sample_prompt')")
    print("Matches count:", matches.count())
    for i in range(min(5, matches.count())):
        el = matches.nth(i)
        print(f"Match {i}: tag={el.evaluate('e => e.tagName')}, class={el.evaluate('e => e.className')}")
