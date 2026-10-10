import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def run_test_b12():
    print("=== TEST B12: Akses Langsung AI Room per Mapel ===")
    results = {}
    
    with sync_playwright() as p:
        # iPhone 13 / 390px viewport + touch
        device = p.devices['iPhone 13']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            **device,
            locale='id-ID',
            timezone_id='Asia/Jakarta'
        )
        page = context.new_page()
        
        # 1. Buka app sebagai tamu di Beranda
        page.goto("http://127.0.0.1:8080/app?tka_mode=guest", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        
        page.evaluate("window.homeShowPanel && window.homeShowPanel('beranda')")
        page.wait_for_timeout(600)
        
        # 2. Assert Ruang AI links di Beranda
        ai_room_links = page.locator('a[href*="/ruang/"], button[onclick*="/ruang/"]')
        count = ai_room_links.count()
        print(f"AI room links count on Beranda: {count}")
        assert count > 0, f"FAIL: Ditemukan {count} link AI room di Beranda (harus > 0)"
        results["ai_room_links_count"] = count
        
        # Cek komponen spesifik: #aiRoomsBar
        ai_rooms_bar = page.locator('#aiRoomsBar')
        assert ai_rooms_bar.count() > 0, "FAIL: #aiRoomsBar tidak ditemukan di Beranda!"
        results["ai_rooms_bar_present"] = True
        
        # Simpan screenshot Beranda menampilkan Ruang AI bar
        os.makedirs("evidence/B12", exist_ok=True)
        beranda_shot = page.screenshot(path="scratch/b12_beranda_ai_bar.png")
        
        # 3. Klik salah satu chip Ruang AI (misal Ruang MATEMATIKA)
        first_ai_link = page.locator('a[href="/ruang/matematika"]').first
        assert first_ai_link.count() > 0, "FAIL: Link /ruang/matematika tidak ditemukan!"
        
        # Navigasi ke Ruang Matematika
        with page.expect_navigation():
            first_ai_link.click()
            
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)
        
        current_url = page.url
        print(f"Navigated to: {current_url}")
        assert "/ruang/matematika" in current_url, f"FAIL: URL salah: {current_url}"
        results["navigation_url_valid"] = True
        
        # 4. Verifikasi elemen UI di Ruang Mapel
        title_el = page.locator('#roomTitle')
        assert title_el.count() > 0, "FAIL: #roomTitle tidak ditemukan!"
        title_text = title_el.inner_text()
        print(f"Room title: {title_text}")
        assert "MATEMATIKA" in title_text.upper(), f"FAIL: Judul tidak memuat MATEMATIKA: {title_text}"
        results["room_title"] = title_text
        
        # Chat input & send button
        chat_input = page.locator('#chatInput')
        btn_send = page.locator('#btnSend')
        assert chat_input.count() > 0, "FAIL: #chatInput tidak ditemukan!"
        assert btn_send.count() > 0, "FAIL: #btnSend tidak ditemukan!"
        results["chat_controls_present"] = True
        
        # Welcome message & quick chips
        welcome_greeting = page.locator('#welcomeGreeting')
        quick_chips = page.locator('#quickChips .quick-chip')
        assert welcome_greeting.count() > 0, "FAIL: #welcomeGreeting tidak ditemukan!"
        chips_count = quick_chips.count()
        print(f"Quick chips count: {chips_count}")
        assert chips_count >= 3, f"FAIL: Kurang dari 3 starter prompt chips: {chips_count}"
        results["quick_chips_count"] = chips_count
        
        # 5. Capture screenshot AFTER di halaman Ruang Mapel (390px mobile viewport)
        after_png_path = "evidence/B12/ai_room_akses_langsung-after.png"
        page.screenshot(path=after_png_path, full_page=False)
        print(f"Captured AFTER screenshot: {after_png_path}")
        
        # Ambil dump DOM dan storage
        storage_dump = page.evaluate("""() => {
            const ls = {};
            for (let i = 0; i < localStorage.length; i++) {
                const k = localStorage.key(i);
                ls[k] = localStorage.getItem(k);
            }
            const ss = {};
            for (let i = 0; i < sessionStorage.length; i++) {
                const k = sessionStorage.key(i);
                ss[k] = sessionStorage.getItem(k);
            }
            return { localStorage: ls, sessionStorage: ss };
        }""")
        
        after_log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "B12 AFTER: Link Ruang AI per mapel langsung dapat diakses dari Beranda & Modul dengan empty state interaktif di Ruang Mapel",
            "dom_summary": {
                "url": page.url,
                "roomTitle": title_text,
                "quickChipsCount": chips_count,
                "hasChatInput": True,
                "hasSendButton": True
            },
            "assertions": results,
            "storage_dump": storage_dump
        }
        
        with open("evidence/B12/ai_room_akses_langsung-after.log", "w", encoding="utf-8") as f:
            json.dump(after_log_data, f, indent=2)
            
        print("B12 log saved successfully!")
        browser.close()
        print("=== TEST B12 PASSED ===")

if __name__ == "__main__":
    run_test_b12()
