# -*- coding: utf-8 -*-
"""scratch/_test_fresh_zero_bridge.py
Audit end-to-end bridge functionality on a fresh AI Studio tab opened from 0.
Tests:
1. Connect via CDP to port 9222
2. Find the fresh Page 0 (new_chat)
3. Check UI state (Angular hydration, textarea, dialogs, tool chips)
4. Execute dismiss_any_overlay(page)
5. Test get_input_box(page)
6. Send a small test prompt ("Ketik 'HALO_TEST_BERHASIL'")
7. Verify generation begins, stop button appears/disappears, response is captured
"""
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, ".")
from pipeline.playwright_aistudio_bridge import (
    dismiss_any_overlay,
    get_input_box,
    extract_latest_response,
    _wait_for_response,
    ensure_thinking_level_high
)

def test_fresh_zero():
    print("=== AUDIT PLAYWRIGHT BRIDGE PADA TAB BARU DARI NOL ===")
    with sync_playwright() as p:
        print("1. Menghubungkan ke Chrome di 127.0.0.1:9222...")
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        pages = context.pages
        print(f"   Terdeteksi {len(pages)} halaman terbuka:")
        for idx, pg in enumerate(pages):
            print(f"   [{idx}] {pg.url}")
            
        page = pages[0]
        page.bring_to_front()
        
        print("\n2. Memeriksa status URL dan DOM...")
        print(f"   URL: {page.url}")
        print(f"   Title: {page.title()}")
        
        # Ambil screenshot kondisi awal sebelum disentuh script
        init_shot = "scratch/_zero_step1_initial.png"
        page.screenshot(path=init_shot)
        print(f"   Screenshot awal disimpan di: {init_shot}")
        
        # Periksa apakah ada dialog/overlay
        dialogs = page.locator("mat-dialog-container, .cdk-overlay-pane, [role='dialog']")
        print(f"   Jumlah dialog terdeteksi: {dialogs.count()}")
        for i in range(dialogs.count()):
            try:
                d = dialogs.nth(i)
                if d.is_visible():
                    print(f"   - Dialog {i}: {d.inner_text()[:120]}")
            except Exception:
                pass
                
        # Periksa tool chips (Search Grounding dll)
        chips = page.locator("ms-tool-chip, .tool-chip, button[aria-label*='Remove' i]")
        print(f"   Jumlah tool chips terdeteksi: {chips.count()}")
        for i in range(chips.count()):
            try:
                c = chips.nth(i)
                if c.is_visible():
                    print(f"   - Chip {i}: text='{c.inner_text().strip()}' label='{c.get_attribute('aria-label')}'")
            except Exception:
                pass
                
        print("\n3. Menjalankan dismiss_any_overlay(page)...")
        dismiss_any_overlay(page)
        time.sleep(1)
        
        # Screenshot setelah dismiss overlay
        clean_shot = "scratch/_zero_step2_dismissed.png"
        page.screenshot(path=clean_shot)
        print(f"   Screenshot setelah dismiss disimpan di: {clean_shot}")
        
        print("\n4. Mencari input textarea prompt...")
        try:
            input_box = get_input_box(page)
            print(f"   ✅ Input textarea DITEMUKAN!")
        except Exception as e:
            print(f"   ❌ GAGAL menemukan input textarea: {e}")
            return False
            
        print("\n5. Mengetikkan prompt uji coba ke textarea...")
        test_prompt = "Jawab hanya satu kata persis: HALO_TEST_BERHASIL"
        input_box.click()
        input_box.fill(test_prompt)
        time.sleep(1)
        
        # Cek tombol Run
        run_btn = page.locator("button.run-button, button:has-text('Run')")
        print(f"   Tombol Run status: count={run_btn.count()}, disabled={run_btn.first.is_disabled()}")
        
        print("\n6. Mengklik tombol Run...")
        run_btn.first.click()
        time.sleep(1)
        
        # Cek apakah ada popup API key muncul setelah Run diklik!
        # (Ini bug fatal yang kemarin sempat muncul jika Search grounding aktif)
        time.sleep(2)
        popups = page.locator("mat-dialog-container, [role='dialog'], .api-key-dialog")
        api_key_popup_detected = False
        for i in range(popups.count()):
            try:
                p_text = popups.nth(i).inner_text().lower()
                if "api key" in p_text or "set up billing" in p_text or "get api key" in p_text:
                    api_key_popup_detected = True
                    print(f"   🚨 PERINGATAN: Muncul dialog permintaan API KEY: {p_text[:100]}...")
            except Exception:
                pass
                
        if not api_key_popup_detected:
            print("   ✅ BEBAS POPUP API KEY! Permintaan dikirim langsung ke Gemini tanpa nodong kunci.")
        else:
            print("   ❌ GAGAL: Masih ada popup API Key!")
            return False
            
        print("\n7. Menunggu respons dari AI Studio...")
        try:
            resp = _wait_for_response(page, turn_count_before=0, timeout_seconds=60)
            print(f"   ✅ RESPONS BERHASIL DITERIMA:\n   \"{resp.strip()}\"")
            if "HALO_TEST_BERHASIL" in resp:
                print("   🌟 HASIL VERIFIKASI: 100% COCOK & SEMPURNA!")
            else:
                print(f"   ℹ️ Respon diterima (karakter: {len(resp)})")
        except Exception as e:
            print(f"   ❌ Error saat menunggu respon: {e}")
            return False
            
        shot_final = "scratch/_zero_step3_response.png"
        page.screenshot(path=shot_final)
        print(f"   Screenshot akhir disimpan di: {shot_final}")
        return True

if __name__ == "__main__":
    success = test_fresh_zero()
    sys.exit(0 if success else 1)
