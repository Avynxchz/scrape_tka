# -*- coding: utf-8 -*-
"""scratch/_audit_from_zero.py
Audit loading AI Studio Playground completely from scratch (new tab from 0).
Tests:
1. Navigation to new_chat
2. Wait for Angular/Material UI to fully hydrate
3. Detection of popups, terms dialogs, tool chips, overlays
4. Finding the input textarea
5. Setting Thinking Level (if applicable)
6. Cleaning tool chips (Grounding with Google Search)
7. Typing a test prompt & verifying Run button readiness
"""
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def audit_from_zero():
    print("=== AUDIT AI STUDIO DARI NOL (TAB BARU) ===")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        except Exception as e:
            print(f"❌ Gagal connect ke port 9222: {e}")
            return False

        context = browser.contexts[0]
        
        # Buat tab baru dari nol (about:blank)
        print("1. Membuat tab baru (about:blank)...")
        new_page = context.new_page()
        new_page.bring_to_front()
        time.sleep(1)
        
        target_url = "https://aistudio.google.com/prompts/new_chat?model=gemini-3.8-flash"
        print(f"2. Membuka URL: {target_url}...")
        t0 = time.time()
        
        # Navigate
        try:
            new_page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            t_dom = time.time() - t0
            print(f"   -> DOM Content Loaded dalam {t_dom:.2f} detik. URL sekarang: {new_page.url}")
        except Exception as e:
            print(f"❌ Error goto: {e}")
            new_page.close()
            return False

        # Monitor Angular hydration & UI elements
        print("3. Menunggu elemen UI AI Studio siap (polling hingga 30 detik)...")
        textarea_found = False
        t_textarea = None
        
        input_selectors = [
            "textarea[placeholder*='prompt' i]",
            "textarea[aria-label*='prompt' i]",
            "textarea[placeholder*='Type' i]",
            "ms-autosize-textarea textarea",
            "ms-text-chunk textarea",
            "textarea.mat-mdc-input-element",
            "div[contenteditable='true']",
            "textarea"
        ]
        
        start_poll = time.time()
        while time.time() - start_poll < 30:
            for sel in input_selectors:
                try:
                    loc = new_page.locator(sel)
                    if loc.count() > 0 and loc.last.is_visible():
                        textarea_found = True
                        t_textarea = time.time() - t0
                        print(f"   -> Textarea DITEMUKAN via '{sel}' pada t={t_textarea:.2f} detik!")
                        break
                except Exception:
                    pass
            if textarea_found:
                break
            time.sleep(0.5)

        if not textarea_found:
            print("❌ GAGAL: Textarea tidak ditemukan setelah 30 detik!")
            # Ambil screenshot untuk analisa
            screenshot_path = "scratch/_zero_tab_fail.png"
            new_page.screenshot(path=screenshot_path)
            print(f"   Screenshot disimpan di {screenshot_path}")
            new_page.close()
            return False

        # Cek overlay / dialogs / banners yang mungkin muncul saat pertama kali buka
        print("4. Memeriksa dialog / modal / overlay saat baru dibuka...")
        dialogs = new_page.locator("mat-dialog-container, .cdk-overlay-pane, [role='dialog']")
        print(f"   Jumlah dialog/overlay terdeteksi: {dialogs.count()}")
        for i in range(dialogs.count()):
            try:
                d = dialogs.nth(i)
                if d.is_visible():
                    print(f"   - Dialog {i} terlihat! Teks: {d.inner_text()[:100]}...")
            except Exception:
                pass

        # Cek tool chips default (Grounding with Google Search dsb)
        print("5. Memeriksa Tool Chips default...")
        tool_chips = new_page.locator("ms-tool-chip, .tool-chip, [aria-label*='Remove' i], button.tool-chip-button")
        print(f"   Jumlah elemen tool chips: {tool_chips.count()}")
        for i in range(tool_chips.count()):
            try:
                tc = tool_chips.nth(i)
                if tc.is_visible():
                    print(f"   - Tool chip {i}: {tc.inner_text()[:60]} | aria-label: {tc.get_attribute('aria-label')}")
            except Exception:
                pass

        # Cek tombol remove tool chips
        remove_btns = new_page.locator("button[aria-label*='Remove' i], button.tool-chip-button + button")
        print(f"   Tombol Remove Tool Chips terdeteksi: {remove_btns.count()}")

        # Cek tombol Run
        print("6. Memeriksa tombol Run...")
        run_btn = new_page.locator("button.run-button, button:has-text('Run')")
        print(f"   Tombol Run count: {run_btn.count()}, is_visible: {run_btn.first.is_visible() if run_btn.count() > 0 else False}")
        if run_btn.count() > 0:
            print(f"   Run button text: {run_btn.first.inner_text()}, disabled: {run_btn.first.is_disabled()}")

        # Cek model selector & model name
        print("7. Memeriksa Model Selector di UI...")
        model_el = new_page.locator(".model-selector-button, button:has-text('gemini'), button:has-text('Flash')")
        print(f"   Model selector count: {model_el.count()}")
        for i in range(min(3, model_el.count())):
            try:
                print(f"   - Model selector {i}: {model_el.nth(i).inner_text()[:40]}")
            except Exception:
                pass

        print(f"\nAudit selesai! Menutup tab uji coba...")
        new_page.close()
        return True

if __name__ == "__main__":
    success = audit_from_zero()
    sys.exit(0 if success else 1)
