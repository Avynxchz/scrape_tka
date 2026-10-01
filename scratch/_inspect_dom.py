import sys
import re
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pg = next(x for x in b.contexts[0].pages if "aistudio" in x.url.lower())
    body = pg.inner_text("body")
    buttons = Array = [b.inner_text() for b in pg.locator("button").all()]
    is_generating = any("Stop" in btn for btn in buttons)
    questions = re.findall(r'"question_number"\s*:\s*(\d+)', body)
    print("URL:", pg.url[:60])
    print(f"Generating: {is_generating} | Body chars: {len(body)} | Questions found: {len(questions)} -> {questions}")
