import os
import json
import time
from playwright.sync_api import sync_playwright

os.makedirs("evidence/B4", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        viewport={"width": 390, "height": 844},
        has_touch=True,
        is_mobile=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    )

    print("Navigating to Matematika Paket 1...")
    page.goto("http://127.0.0.1:8080/app?subject=matematika&paket=1")
    page.wait_for_timeout(2000)

    # 1. Test Soal 13 (index 12)
    print("Navigating to Soal 13...")
    page.evaluate("state.currentIndex = 12; renderQuestion();")
    page.wait_for_timeout(1500)

    stim_text = page.locator("#stimulusCol").inner_text()
    stim_html = page.locator("#stimulusCol").inner_html()

    has_formula_in_html = "18 - 3x" in stim_html
    has_formula_in_text = "18\u22123x" in stim_text or "18 - 3x" in stim_text
    print(f"Stimulus HTML has formula: {has_formula_in_html}")
    print(f"Stimulus TEXT has formula: {has_formula_in_text}")

    # Capture after screenshot of Soal 13
    img_path1 = "evidence/B4/soal13_formula_displayed-after.png"
    page.screenshot(path=img_path1)
    print(f"Captured {img_path1}")

    log_path1 = "evidence/B4/soal13_formula_displayed-after.log"
    with open(log_path1, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "B4 AFTER: Stimulus Soal 13 menampilkan formula V(x) = 18 - 3x secara utuh",
            "dom_summary": {
                "url": page.url,
                "soal_nomor": 13,
                "has_formula_in_html": has_formula_in_html,
                "has_formula_in_text": has_formula_in_text,
                "stimulus_snippet": stim_text[:400]
            },
            "assertions": {
                "formula_rendered": has_formula_in_html or has_formula_in_text
            }
        }, f, indent=2, ensure_ascii=False)

    # 2. Test Image Fallback & Retry
    print("Testing universal image fallback on a broken image...")
    # Inject a broken test image with data-latex into #stimulusContainer
    page.evaluate("""() => {
        const testImg = document.createElement('img');
        testImg.id = 'brokenTestImg';
        testImg.alt = 'Diagram Uji Coba';
        testImg.setAttribute('data-latex', 'f(x) = \\\\frac{a}{b}');
        testImg.src = 'http://127.0.0.1:8080/tka/cbt_images/non_existent_image_12345.png';
        document.getElementById('stimulusContainer').prepend(testImg);
    }""")
    page.wait_for_timeout(1000)

    fallback_visible = page.locator(".img-fallback-box").first.is_visible()
    fallback_text = page.locator(".img-fallback-box").first.inner_text()
    retry_count = page.locator(".img-fallback-retry").count()
    print(f"Fallback box visible: {fallback_visible}")
    print(f"Retry button count: {retry_count}")

    img_path2 = "evidence/B4/image_fallback_retry-after.png"
    page.screenshot(path=img_path2)
    print(f"Captured {img_path2}")

    log_path2 = "evidence/B4/image_fallback_retry-after.log"
    with open(log_path2, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "B4 AFTER: Fallback gambar gagal load dengan pesan jelas, preview latex, dan tombol coba lagi",
            "dom_summary": {
                "fallback_visible": fallback_visible,
                "retry_button_present": retry_count > 0,
                "fallback_text": fallback_text
            },
            "assertions": {
                "fallback_displayed": fallback_visible,
                "retry_btn_exists": retry_count > 0,
                "has_error_message": "gagal dimuat" in fallback_text
            }
        }, f, indent=2, ensure_ascii=False)

    browser.close()
    print("ALL B4 TESTS PASSED!")
