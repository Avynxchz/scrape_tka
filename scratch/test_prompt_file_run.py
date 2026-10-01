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
    page.bring_to_front()

    # Create a small prompt file
    prompt_file = os.path.abspath("scratch/test_calc.txt")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write("Soal 1: 15 * 4 = ?\nSoal 2: Akar kuadrat dari 144 = ?\nHasilkan output dalam format JSON: [{\"nomor\": 1, \"jawaban\": 60}, ...]")

    print("Uploading file to AI Studio...")
    file_input = page.locator("input[type='file']")
    file_input.first.set_input_files(prompt_file)
    time.sleep(2.0)

    # Check input box
    input_box = page.locator("textarea[placeholder*='prompt' i], textarea[aria-label*='prompt' i], ms-autosize-textarea textarea, textarea").last
    input_box.click()
    instruction = "Selesaikan soal pada file terlampir dan berikan output format JSON sesuai instruksi di dalamnya."
    input_box.fill(instruction)
    time.sleep(1.0)

    print("Submitting via Ctrl+Enter...")
    page.keyboard.press("Control+Enter")
    print("Submitted! Monitoring response...")
    
    start_time = time.time()
    for _ in range(30):
        time.sleep(2.0)
        # Check latest response
        code_blocks = page.locator("pre code, pre.code-block")
        if code_blocks.count() > 0:
            txt = code_blocks.last.inner_text()
            if "jawaban" in txt or "60" in txt:
                print(f"SUCCESS! Output received ({int(time.time() - start_time)}s):\n{txt}")
                break
        else:
            bubble = page.locator("ms-chat-turn:last-child")
            if bubble.count() > 0 and "60" in bubble.inner_text():
                print(f"SUCCESS in bubble:\n{bubble.inner_text()}")
                break
