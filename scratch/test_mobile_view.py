import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

OUT_DIR = os.path.join(os.getcwd(), "scratch", "screenshots_mobile")
os.makedirs(OUT_DIR, exist_ok=True)

test_cases = [
    {"name": "mobile_mat_p1_q13", "subject": "matematika", "pkg": 1, "q": 13, "desc": "Mobile - Mat P1 Q13 Table"},
    {"name": "mobile_jerman_p1_q10", "subject": "bahasa_jerman", "pkg": 1, "q": 10, "desc": "Mobile - B Jerman P1 Q10"},
    {"name": "mobile_kimia_p1_q06", "subject": "kimia", "pkg": 1, "q": 6, "desc": "Mobile - Kimia P1 Q6 sp2/sp3"},
    {"name": "mobile_mtl_p2_q21", "subject": "matematika_lanjut", "pkg": 2, "q": 21, "desc": "Mobile - MTL P2 Q21 inline L"},
    {"name": "mobile_arab_p1_q05", "subject": "bahasa_arab", "pkg": 1, "q": 5, "desc": "Mobile - B Arab P1 Q5 RTL"},
    {"name": "mobile_geografi_p1_q02", "subject": "geografi", "pkg": 1, "q": 2, "desc": "Mobile - Geografi P1 Q2"}
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
    page = context.new_page()

    for tc in test_cases:
        url = f"http://localhost:8080/?subject={tc['subject']}&paket={tc['pkg']}"
        page.goto(url)
        page.wait_for_load_state("networkidle")
        time.sleep(0.4)
        page.evaluate(f"state.currentIndex = {tc['q'] - 1}; renderQuestion();")
        time.sleep(1.0)
        ss_path = os.path.join(OUT_DIR, f"{tc['name']}.png")
        page.screenshot(path=ss_path, full_page=False)
        print(f"Captured {tc['name']} -> {ss_path}")

    browser.close()
    print("Mobile visual checks completed with full image loading!")
