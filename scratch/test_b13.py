import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def run_test_b13():
    print("=== TEST B13: Visual Upgrade Landing Page ===")
    results = {}
    os.makedirs("evidence/B13", exist_ok=True)
    
    with sync_playwright() as p:
        # 1. Mobile iPhone 13 (390px viewport + touch)
        dev = p.devices['iPhone 13']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            **dev,
            locale='id-ID',
            timezone_id='Asia/Jakarta'
        )
        page = context.new_page()
        page.goto("http://127.0.0.1:8080/?stay=1", wait_until="networkidle")
        page.wait_for_timeout(1000)
        
        # A. Cek Overflow Horizontal
        overflow_mobile = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
        scroll_w = page.evaluate("() => document.documentElement.scrollWidth")
        inner_w = page.evaluate("() => window.innerWidth")
        print(f"Mobile ScrollWidth: {scroll_w}, InnerWidth: {inner_w}, Overflow: {overflow_mobile}")
        assert not overflow_mobile, f"FAIL: Ada horizontal overflow pada mobile! ({scroll_w} > {inner_w})"
        results["mobile_horizontal_overflow"] = False
        
        # B. Cek Tap Target Sizes (min 44px)
        cta_primary = page.locator('#heroCtaPrimary')
        cta_guest = page.locator('#heroCtaGuest')
        login_btn_m = page.locator('#landingLoginBtnMobile')
        btn_menu = page.locator('#btnMenu')
        
        cta_primary_box = cta_primary.bounding_box()
        cta_guest_box = cta_guest.bounding_box()
        login_btn_m_box = login_btn_m.bounding_box()
        btn_menu_box = btn_menu.bounding_box()
        
        print(f"Primary CTA height: {cta_primary_box['height']}")
        print(f"Guest CTA height: {cta_guest_box['height']}")
        print(f"Login button height: {login_btn_m_box['height']}")
        print(f"Menu button height: {btn_menu_box['height']}, width: {btn_menu_box['width']}")
        
        assert cta_primary_box['height'] >= 44, f"Primary CTA height < 44px ({cta_primary_box['height']})"
        assert cta_guest_box['height'] >= 44, f"Guest CTA height < 44px ({cta_guest_box['height']})"
        assert login_btn_m_box['height'] >= 44, f"Mobile login height < 44px ({login_btn_m_box['height']})"
        assert btn_menu_box['height'] >= 44, f"Menu button height < 44px ({btn_menu_box['height']})"
        results["tap_targets_min_44px"] = True
        
        # C. Cek Bottom Tabbar touch targets
        tab_links = page.locator('.tabbar a')
        tab_count = tab_links.count()
        print(f"Tabbar links count: {tab_count}")
        assert tab_count == 4, f"FAIL: Tabbar link count bukan 4: {tab_count}"
        for i in range(tab_count):
            box = tab_links.nth(i).bounding_box()
            assert box['height'] >= 44, f"Tab link {i} height < 44px ({box['height']})"
        results["bottom_tabbar_min_44px"] = True
        
        # D. Capture Mobile AFTER screenshot (390px)
        m_shot_path = "evidence/B13/landing_page_390-after.png"
        page.screenshot(path=m_shot_path, full_page=False)
        print(f"Captured AFTER screenshot mobile: {m_shot_path}")
        
        # 2. Desktop (1280px viewport)
        d_context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            locale='id-ID',
            timezone_id='Asia/Jakarta'
        )
        d_page = d_context.new_page()
        d_page.goto("http://127.0.0.1:8080/?stay=1", wait_until="networkidle")
        d_page.wait_for_timeout(1000)
        
        overflow_desktop = d_page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
        assert not overflow_desktop, "FAIL: Ada horizontal overflow pada desktop!"
        results["desktop_horizontal_overflow"] = False
        
        d_shot_path = "evidence/B13/landing_page_desktop-after.png"
        d_page.screenshot(path=d_shot_path, full_page=False)
        print(f"Captured AFTER screenshot desktop: {d_shot_path}")
        
        # 3. Test Active Session CTA transformation (?stay=1)
        sess_context = browser.new_context(viewport={'width': 1280, 'height': 800})
        sess_page = sess_context.new_page()
        sess_page.goto("http://127.0.0.1:8080/app", wait_until="domcontentloaded")
        sess_page.evaluate("""() => {
            sessionStorage.removeItem('tka_mode');
            localStorage.removeItem('tka_guest_session');
            localStorage.setItem('tka_supabase_auth_token', JSON.stringify({
                access_token: 'fake-jwt-token-b13',
                user: { id: 'usr_b13_test', email: 'siswa.b13@example.com' }
            }));
            localStorage.setItem('tka_device_logged_in', 'true');
            localStorage.setItem('tka_user', JSON.stringify({
                name: 'Budi Santoso',
                email: 'siswa.b13@example.com',
                avatar: '',
                loggedIn: true
            }));
        }""")
        sess_page.goto("http://127.0.0.1:8080/?stay=1", wait_until="networkidle")
        sess_page.wait_for_timeout(1000)
        
        login_btn_text = sess_page.locator('#landingLoginBtnDesktop').inner_text()
        print(f"Active session login button text: {login_btn_text}")
        assert "Lanjut ke Beranda" in login_btn_text, f"FAIL: Tombol login tidak berubah jadi 'Lanjut ke Beranda': {login_btn_text}"
        results["active_session_cta_transformed"] = True
        
        # Save log data
        after_log = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "B13 AFTER: Landing Page upgrade visual premium, mobile-first, tap targets min 44px, no overflow, Outfit font typography",
            "metrics": {
                "mobile_scrollWidth": scroll_w,
                "mobile_innerWidth": inner_w,
                "overflow_mobile": False,
                "overflow_desktop": False,
                "primary_cta_height": cta_primary_box['height'],
                "guest_cta_height": cta_guest_box['height'],
                "login_btn_height": login_btn_m_box['height'],
                "menu_btn_height": btn_menu_box['height']
            },
            "assertions": results
        }
        
        with open("evidence/B13/landing_page-after.log", "w", encoding="utf-8") as f:
            json.dump(after_log, f, indent=2)
            
        print("B13 log saved successfully!")
        browser.close()
        print("=== TEST B13 PASSED ===")

if __name__ == "__main__":
    run_test_b13()
