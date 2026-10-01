import time
from playwright.sync_api import sync_playwright

def verify_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        
        print("Navigating to http://127.0.0.1:8080/index.html...")
        page.goto("http://127.0.0.1:8080/index.html", timeout=30000)
        page.wait_for_timeout(1000)
        
        # Switch to Geografi
        print("Selecting Geografi (Pilihan)...")
        page.select_option("#subjectSelect", "geografi")
        page.wait_for_timeout(1500)
        
        title_text = page.inner_text("#brandTitle")
        print(f"Brand Title: {title_text}")
        assert "GEOGRAFI" in title_text
        
        # Question 1 verification
        q_num = page.inner_text("#qNumBadge")
        q_label = page.inner_text("#qLabelHeader")
        print(f"Active question badge: {q_num} ({q_label})")
        
        # Verify stimulus image is rendered
        stim_img = page.locator("#stimulusContainer img")
        assert stim_img.count() > 0
        img_src = stim_img.first.get_attribute("src")
        print(f"Found stimulus image: {img_src}")
        
        # Open Tata Cara Penyelesaian (5 Pillars)
        print("Opening Tata Cara Penyelesaian...")
        page.click("#btnToggleExplanation")
        page.wait_for_timeout(1500)
        
        # Check that learningSection is visible
        learning_sec = page.locator("#learningSection")
        assert learning_sec.is_visible()
        expl_text = learning_sec.inner_text()
        print("Pillars found in explanation panel:")
        for heading in ["Konsep", "Glosarium", "Mengapa", "Langkah", "Tips"]:
            if heading.lower() in expl_text.lower():
                print(f"  -> {heading}: OK")
                
        # Test Similar Question Drill
        print("Testing Latihan Soal Serupa...")
        sim_prompt = page.locator("#simPromptContainer").inner_text()
        print(f"Similar Question Prompt: {sim_prompt[:100]}...")
        
        sim_opts = page.locator(".sim-opt-item")
        print(f"Found {sim_opts.count()} options for similar question.")
        if sim_opts.count() > 0:
            sim_opts.first.click()
            page.wait_for_timeout(300)
            page.click("#btnCheckSimAnswer")
            page.wait_for_timeout(500)
            fb_text = page.locator("#simFeedback").inner_text()
            print(f"Feedback: {fb_text[:100]}...")
            
        # Take full page screenshot
        screenshot_path = "d:/PROJECTS/SCRAPE_TKA/app_geografi_q1_pillars.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Test Daftar Soal Modal
        page.click("#btnOpenDaftarSoal")
        page.wait_for_timeout(500)
        modal_title = page.inner_text("#modalTitle")
        print(f"Modal opened: {modal_title}")
        grid_items = page.locator("#soalGrid .grid-item")
        print(f"Total questions in modal grid: {grid_items.count()} (Expected: 10)")
        assert grid_items.count() == 10
        page.screenshot(path="d:/PROJECTS/SCRAPE_TKA/app_geografi_modal_grid.png")
        print("Modal screenshot saved to: d:/PROJECTS/SCRAPE_TKA/app_geografi_modal_grid.png")
        
        browser.close()
        print("\n=== BROWSER UI VERIFICATION 100% SUKSES! ===")

if __name__ == "__main__":
    verify_ui()
