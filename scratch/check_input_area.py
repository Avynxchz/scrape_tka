import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]
    
    # Check text inside user turns and input containers
    print("=== PROMPT AREA INSPECTION ===")
    user_turns = page.locator("ms-user-turn, ms-text-chunk, ms-file-chunk, ms-chat-turn")
    print(f"Turns count: {user_turns.count()}")
    for i in range(max(0, user_turns.count() - 5), user_turns.count()):
        t = user_turns.nth(i)
        print(f"Turn {i} ({t.evaluate('e => e.tagName')}): {t.inner_text()[:120].strip()}")

    # Check button aria-label='Insert images, videos, audio, or files'
    insert_btn = page.locator("button[aria-label*='Insert images, videos, audio, or files' i]")
    print(f"Insert btn count: {insert_btn.count()}")
