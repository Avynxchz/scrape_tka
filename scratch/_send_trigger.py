from playwright.sync_api import sync_playwright
import time

p = sync_playwright().start()
b = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
pg = b.contexts[0].pages[0]
inp = pg.locator("textarea[placeholder*='prompt' i], textarea").last
inp.click(force=True)
time.sleep(0.5)
msg = "Berdasarkan file yang sudah diunggah, tolong hasilkan solusi 5 pilar dalam format JSON array sekarang."
inp.fill(msg)
time.sleep(0.5)
pg.keyboard.press("Control+Enter")
time.sleep(3.0)
print("Submitted follow up! Current turns count:", pg.locator("ms-chat-turn").count())
p.stop()
