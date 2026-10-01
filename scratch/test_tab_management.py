import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    
    print(f"Total halaman terbuka: {len(context.pages)}")
    ai_pages = [pg for pg in context.pages if "aistudio.google.com" in pg.url.lower()]
    print(f"Halaman AI Studio: {len(ai_pages)}")
    
    if len(ai_pages) > 1:
        for pg in ai_pages[1:]:
            print(f"Menutup tab berlebih: {pg.url[:60]}")
            pg.close()
    
    target_page = ai_pages[0] if ai_pages else context.new_page()
    target_page.bring_to_front()
    print("Tab aktif utama:", target_page.url)
