import os, time
from playwright.sync_api import sync_playwright

OUT_DIR = "scratch/screenshots/matematika"
os.makedirs(OUT_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    d_page = browser.new_page(viewport={"width": 1280, "height": 800})
    m_page = browser.new_page(viewport={"width": 390, "height": 844})

    for pkg, qnums in [(1, [5, 7, 8, 12, 15, 43]), (2, [2, 3, 8, 14])]:
        for q in qnums:
            print(f"Checking Mat P{pkg} Q{q}...")
            # Desktop
            d_page.goto(f"http://localhost:8080/?subject=matematika&paket={pkg}")
            d_page.wait_for_load_state("networkidle")
            time.sleep(0.3)
            d_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
            time.sleep(1.0)
            d_ss = f"{OUT_DIR}/mat_p{pkg}_q{q:02d}_desktop_initial.png"
            d_page.screenshot(path=d_ss)

            # Mobile
            m_page.goto(f"http://localhost:8080/?subject=matematika&paket={pkg}")
            m_page.wait_for_load_state("networkidle")
            time.sleep(0.3)
            m_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
            time.sleep(1.0)
            m_ss = f"{OUT_DIR}/mat_p{pkg}_q{q:02d}_mobile_initial.png"
            m_page.screenshot(path=m_ss)

            # Inspect elements
            info = d_page.evaluate('''() => {
                const stim = document.getElementById('stimulusContainer');
                const prompt = document.getElementById('promptContainer');
                const opts = document.getElementById('optionsContainer');
                const imgs = Array.from(document.querySelectorAll('.cbt-card img')).map(im => ({
                    src: im.src.split('/').pop(),
                    cls: im.className,
                    w: im.clientWidth,
                    h: im.clientHeight,
                    nw: im.naturalWidth,
                    nh: im.naturalHeight,
                    parent: im.parentElement.tagName + '.' + im.parentElement.className
                }));
                return {
                    stimVisible: stim ? stim.style.display !== 'none' : false,
                    imgs: imgs
                };
            }''')
            print(f"  P{pkg} Q{q} imgs: {info['imgs']}")

    browser.close()
