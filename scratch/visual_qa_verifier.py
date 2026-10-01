import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

OUT_DIR = os.path.join(os.getcwd(), "scratch", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 860})
        page = context.new_page()

        test_cases = [
            {"name": "kimia_p2_q22", "subject": "kimia", "pkg": 2, "q": 22, "desc": "Kimia P2 No 22 (Equilibrium chart, no lion)"},
            {"name": "kimia_p2_q24", "subject": "kimia", "pkg": 2, "q": 24, "desc": "Kimia P2 No 24 (Organic chem mechanism, no lion)"},
            {"name": "kimia_p1_q06", "subject": "kimia", "pkg": 1, "q": 6, "desc": "Kimia P1 No 6 (sp2 / sp3 orbital formatting)"},
            {"name": "kimia_p1_q08", "subject": "kimia", "pkg": 1, "q": 8, "desc": "Kimia P1 No 8 (10^-10 exponent formatting)"},
            {"name": "kimia_p1_q17", "subject": "kimia", "pkg": 1, "q": 17, "desc": "Kimia P1 No 17 (10^-6 M formatting)"},
            {"name": "kimia_p2_q21", "subject": "kimia", "pkg": 2, "q": 21, "desc": "Kimia P2 No 21 (30 C degree symbol)"},
            {"name": "mtl_p2_q13", "subject": "matematika_lanjut", "pkg": 2, "q": 13, "desc": "Mat Lanjut P2 No 13 (inline vector images left-to-right)"},
            {"name": "mtl_p2_q21", "subject": "matematika_lanjut", "pkg": 2, "q": 21, "desc": "Mat Lanjut P2 No 21 (inline letter L in sentence)"},
            {"name": "mat_p1_q13", "subject": "matematika", "pkg": 1, "q": 13, "desc": "Mat P1 No 13 (responsive table, text interpretasi not clipped)"},
            {"name": "jerman_p1_q10", "subject": "bahasa_jerman", "pkg": 1, "q": 10, "desc": "B Jerman P1 No 10 (text next to image not cut off)"},
            {"name": "arab_p1_q05", "subject": "bahasa_arab", "pkg": 1, "q": 5, "desc": "B Arab P1 No 5 (Arabic RTL right alignment)"},
            {"name": "geografi_p1_q02", "subject": "geografi", "pkg": 1, "q": 2, "desc": "Geografi P1 No 2 (authentic geography map, no ekonomi chart)"},
            {"name": "geografi_p2_q05", "subject": "geografi", "pkg": 2, "q": 5, "desc": "Geografi P2 No 5 (map sizing & lightbox zoom)"},
            {"name": "mtl_p1_q05", "subject": "matematika_lanjut", "pkg": 1, "q": 5, "desc": "Mat Lanjut P1 No 5 (option diagram size > 85px)"},
            {"name": "biologi_p2_q25", "subject": "biologi", "pkg": 2, "q": 25, "desc": "Biologi P2 No 25 (genetics diagram, no lion)"}
        ]

        for tc in test_cases:
            print(f"Testing {tc['name']} ({tc['desc']})...")
            url = f"http://localhost:8080/?subject={tc['subject']}&paket={tc['pkg']}"
            page.goto(url)
            page.wait_for_load_state("networkidle")
            time.sleep(0.4)

            # Jump to question
            page.evaluate(f"""() => {{
                state.currentIndex = {tc['q'] - 1};
                renderQuestion();
            }}""")
            time.sleep(0.4)

            # Test lightbox on geografi_p2_q05
            if tc['name'] == 'geografi_p2_q05':
                img = page.query_selector('#stimulusContainer img')
                if img:
                    img.click()
                    time.sleep(0.3)
                    zoom_btn = page.query_selector('.lightbox-toolbar button:has-text("Perbesar")')
                    if zoom_btn:
                        zoom_btn.click()
                        time.sleep(0.2)

            ss_path = os.path.join(OUT_DIR, f"{tc['name']}.png")
            page.screenshot(path=ss_path, full_page=False)

            prompt_text = page.inner_text("#promptContainer") if page.query_selector("#promptContainer") else ""
            opts_text = page.inner_text("#optionsContainer") if page.query_selector("#optionsContainer") else ""
            stim_imgs = page.evaluate("() => Array.from(document.querySelectorAll('#stimulusContainer img')).map(i => i.src)")
            opt_imgs = page.evaluate("() => Array.from(document.querySelectorAll('#optionsContainer img')).map(i => ({src: i.src, w: i.clientWidth, h: i.clientHeight}))")

            print(f"  -> {tc['name']}: Prompt len={len(prompt_text)}, Opts len={len(opts_text)}, StimImgs={len(stim_imgs)}, OptImgs={len(opt_imgs)}")
            print(f"     Prompt: {prompt_text[:80]!r}")
            print(f"     Opts: {opts_text[:100]!r}")

        browser.close()
        print("\nAll Playwright visual verifications completed!")

if __name__ == "__main__":
    run_tests()
