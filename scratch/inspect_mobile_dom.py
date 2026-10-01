from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto("http://localhost:8080/?subject=bahasa_jerman&paket=1")
    page.wait_for_load_state("networkidle")
    page.evaluate("state.currentIndex = 9; renderQuestion();")
    styles = page.evaluate("""() => {
        const img = document.querySelector("#stimulusContainer td img");
        if (!img) return null;
        const cs = window.getComputedStyle(img);
        return {
            w: img.clientWidth,
            h: img.clientHeight,
            naturalW: img.naturalWidth,
            naturalH: img.naturalHeight,
            maxHeight: cs.maxHeight,
            maxWidth: cs.maxWidth,
            display: cs.display,
            className: img.className
        };
    }""")
    print("IMG styles:", styles)
    browser.close()
