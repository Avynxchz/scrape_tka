import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import time
from playwright.sync_api import sync_playwright

def ensure_thinking_level_high(page):
    print("Memeriksa Thinking Level...")
    # Cari select
    select = page.locator("mat-select[aria-label='Thinking Level'], mat-select:has-text('Thinking')")
    
    if select.count() == 0 or not select.first.is_visible():
        # Coba buka settings panel jika tertutup
        toggle = page.locator("button.runsettings-toggle-button")
        if toggle.count() > 0 and toggle.first.is_visible():
            print("Membuka panel settings AI Studio...")
            toggle.first.click()
            time.sleep(1.0)
            select = page.locator("mat-select[aria-label='Thinking Level'], mat-select:has-text('Thinking')")

    if select.count() > 0:
        val = select.first.inner_text().strip()
        print(f"Thinking Level saat ini: '{val}'")
        if "High" in val:
            print("✅ Thinking Level sudah 'High'!")
            return True
        else:
            print(f"Mengubah Thinking Level dari '{val}' ke 'High'...")
            select.first.click()
            time.sleep(0.8)
            opt_high = page.locator("mat-option:has-text('High')")
            if opt_high.count() > 0:
                opt_high.first.click()
                time.sleep(0.5)
                print("✅ Berhasil memilih Thinking Level 'High'!")
                return True
            else:
                print("⚠️ Opsi 'High' tidak ditemukan di mat-option list!")
    else:
        print("⚠️ Mat-select Thinking Level tidak ditemukan.")
    return False

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]
    page.bring_to_front()
    res = ensure_thinking_level_high(page)
    print("Result:", res)
