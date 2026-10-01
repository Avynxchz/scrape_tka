import os, sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

OUT_DIR = os.path.join(os.getcwd(), "scratch", "screenshots", "fisika")
os.makedirs(OUT_DIR, exist_ok=True)

test_cases = [
    # Fisika P1
    {"pkg": 1, "q": 14, "issues": "P (Sudut 60° pada gaya)"},
    # Fisika P2
    {"pkg": 2, "q": 1, "issues": "P (Kecepatan km·jam⁻¹)"},
    {"pkg": 2, "q": 2, "issues": "P (Percepatan m·s⁻²)"},
    {"pkg": 2, "q": 7, "issues": "P (Kecepatan m·s⁻¹ & sudut 53°)"},
    {"pkg": 2, "q": 9, "issues": "P (Kunci pas sudut 37° & percepatan sudut rad·s⁻²)"},
    {"pkg": 2, "q": 11, "issues": "P (Volume gas m³)"},
    {"pkg": 2, "q": 15, "issues": "P (Suhu derajat 50°)"}
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    d_ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    d_page = d_ctx.new_page()

    m_ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
    m_page = m_ctx.new_page()

    records = []

    for tc in test_cases:
        pkg = tc["pkg"]
        q = tc["q"]
        print(f"Verifying Fisika P{pkg} Q{q}...")

        # Desktop
        d_url = f"http://localhost:8080/?subject=fisika&paket={pkg}"
        d_page.goto(d_url)
        d_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        d_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.2)
        d_ss = os.path.join(OUT_DIR, f"fisika_p{pkg}_q{q:02d}_desktop.png")
        d_page.screenshot(path=d_ss, full_page=False)

        stim_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#stimulusContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight, w: i.offsetWidth, h: i.offsetHeight, cls: i.className}))")
        prompt_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#promptContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight, w: i.offsetWidth, h: i.offsetHeight, cls: i.className}))")
        opt_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#optionsContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight, w: i.offsetWidth, h: i.offsetHeight, cls: i.className}))")

        all_imgs = stim_imgs + prompt_imgs + opt_imgs

        # Mobile
        m_url = f"http://localhost:8080/?subject=fisika&paket={pkg}"
        m_page.goto(m_url)
        m_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        m_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.2)
        m_ss = os.path.join(OUT_DIR, f"fisika_p{pkg}_q{q:02d}_mobile.png")
        m_page.screenshot(path=m_ss, full_page=False)

        m_overflow = m_page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")

        has_foreign = any("biologi" in i["src"].lower() or "ekonomi" in i["src"].lower() for i in all_imgs)
        all_loaded = all(i["complete"] and i["nw"] > 0 for i in all_imgs) if all_imgs else True

        status = "Fixed" if (not has_foreign and all_loaded and not m_overflow) else "Belum"

        record = {
            "mapel": "Fisika", "paket": pkg, "nomor": q,
            "masalah": tc["issues"], "status": status,
            "desktop_ss": d_ss, "mobile_ss": m_ss,
            "all_imgs_count": len(all_imgs),
            "all_loaded": all_loaded,
            "mobile_overflow": m_overflow
        }
        records.append(record)
        print(f"  -> P{pkg} Q{q}: Status={status} (AllImgs={len(all_imgs)}, Loaded={all_loaded}, Overflow={m_overflow})")

    browser.close()

    with open("scratch/fisika_verification_summary.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print("\nFisika verification completed!")
