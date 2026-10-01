import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
pg = b.contexts[0].pages[0]
turns = pg.locator("ms-chat-turn")
n = turns.count()
print("Total turns:", n)
for i in range(n):
    t = turns.nth(i)
    txt = t.inner_text()
    print(f"--- TURN {i} (len: {len(txt)}) ---")
    print(txt[:300])
p.stop()
