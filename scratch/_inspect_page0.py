from playwright.sync_api import sync_playwright
p = sync_playwright().start()
b = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
pg = b.contexts[0].pages[0]
turns = pg.locator("ms-chat-turn").count()
print("Turns count:", turns)
body = pg.inner_text("body")[:500]
print("Body preview:", repr(body))
modals = pg.locator(".mat-mdc-dialog-container, .modal, [role='dialog']").count()
print("Modals count:", modals)
if modals > 0:
    for i in range(modals):
        print(f"Modal {i}:", repr(pg.locator(".mat-mdc-dialog-container, .modal, [role='dialog']").nth(i).inner_text()[:200]))
p.stop()
