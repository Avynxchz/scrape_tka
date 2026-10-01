# -*- coding: utf-8 -*-
import os
import sys
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1100})
        page = context.new_page()
        
        # Buka langsung ke MTL Paket 2
        url = "http://localhost:8080/?subject=matematika_lanjut&paket=2"
        print(f"Navigating to {url} ...")
        page.goto(url)
        page.wait_for_timeout(2500)

        # 1. Buka Soal No. 8 (index 7) dan tampilkan tata cara
        print("Rendering Soal No. 8...")
        page.evaluate("""() => {
            state.currentIndex = 7; // Soal 8
            renderQuestion();
            state.explanationVisible = true;
            document.getElementById('learningSection').style.display = 'flex';
            setExplanationCollapsed(false);
            renderExplanation(getCurrentQuestion());
        }""")
        page.wait_for_timeout(2000)
        page.evaluate("() => { renderMath(); }")
        page.wait_for_timeout(1000)

        out_q8 = os.path.join("scratch", "ui_mtl_p2_q8.png")
        page.screenshot(path=out_q8, full_page=True)
        print(f"[OK] Screenshot Q8 tersimpan di: {out_q8}")

        # 2. Buka Soal No. 3 (index 2 - Hotel)
        print("Rendering Soal No. 3...")
        page.evaluate("""() => {
            state.currentIndex = 2; // Soal 3
            renderQuestion();
            state.explanationVisible = true;
            document.getElementById('learningSection').style.display = 'flex';
            setExplanationCollapsed(false);
            renderExplanation(getCurrentQuestion());
        }""")
        page.wait_for_timeout(2000)
        page.evaluate("() => { renderMath(); }")
        page.wait_for_timeout(1000)

        out_q3 = os.path.join("scratch", "ui_mtl_p2_q3.png")
        page.screenshot(path=out_q3, full_page=True)
        print(f"[OK] Screenshot Q3 tersimpan di: {out_q3}")

        browser.close()
        print("UI Verification Done!")

if __name__ == "__main__":
    run()
