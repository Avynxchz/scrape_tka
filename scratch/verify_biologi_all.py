import os, sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

OUT_DIR = os.path.join(os.getcwd(), "scratch", "screenshots", "biologi")
os.makedirs(OUT_DIR, exist_ok=True)

test_cases = [
    # Biologi P1
    {"pkg": 1, "q": 1, "issues": "Audit teks/konteks Biologi P1"},
    {"pkg": 1, "q": 10, "issues": "Audit teks/konteks Biologi P1"},
    {"pkg": 1, "q": 20, "issues": "Audit teks/konteks Biologi P1"},
    # Biologi P2
    {"pkg": 2, "q": 3, "issues": "G (Respirasi aerob)"},
    {"pkg": 2, "q": 4, "issues": "G (Fotosintesis Sachs)"},
    {"pkg": 2, "q": 5, "issues": "G (Enzimologi tabung reaksi)"},
    {"pkg": 2, "q": 7, "issues": "G (Komponen darah eritrosit/leukosit, bukan B. Inggris)"},
    {"pkg": 2, "q": 9, "issues": "G (Patofisiologi kardiovaskular)"},
    {"pkg": 2, "q": 16, "issues": "G (Uji bahan makanan/lugol)"},
    {"pkg": 2, "q": 17, "issues": "G (Homeostasis urin/olahraga)"},
    {"pkg": 2, "q": 19, "issues": "G (Data zona bening antibiotik)"},
    {"pkg": 2, "q": 20, "issues": "G (Grafik tinggi tanaman media tanam)"},
    {"pkg": 2, "q": 25, "issues": "G (Anatomi kulit/kelenjar keringat, bukan singa)"},
    {"pkg": 2, "q": 28, "issues": "G (Struktur neuron sel saraf)"}
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
        print(f"Verifying Biologi P{pkg} Q{q}...")

        # Desktop
        d_url = f"http://localhost:8080/?subject=biologi&paket={pkg}"
        d_page.goto(d_url)
        d_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        d_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.0)
        d_ss = os.path.join(OUT_DIR, f"biologi_p{pkg}_q{q:02d}_desktop.png")
        d_page.screenshot(path=d_ss, full_page=False)

        stim_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#stimulusContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight}))")
        opt_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#optionsContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight}))")

        # Mobile
        m_url = f"http://localhost:8080/?subject=biologi&paket={pkg}"
        m_page.goto(m_url)
        m_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        m_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.0)
        m_ss = os.path.join(OUT_DIR, f"biologi_p{pkg}_q{q:02d}_mobile.png")
        m_page.screenshot(path=m_ss, full_page=False)

        has_foreign = any("bahasa_inggris" in i["src"].lower() or "ekonomi" in i["src"].lower() for i in stim_imgs + opt_imgs)
        all_loaded = all(i["complete"] and i["nw"] > 0 for i in stim_imgs + opt_imgs)

        status = "Fixed" if (not has_foreign and all_loaded) else "Belum"

        record = {
            "mapel": "Biologi", "paket": pkg, "nomor": q,
            "masalah": tc["issues"], "status": status,
            "desktop_ss": d_ss, "mobile_ss": m_ss,
            "stim_imgs_count": len(stim_imgs),
            "opt_imgs_count": len(opt_imgs)
        }
        records.append(record)
        print(f"  -> P{pkg} Q{q}: Status={status} (StimImgs={len(stim_imgs)}, AllLoaded={all_loaded})")

    browser.close()

    with open("scratch/biologi_verification_summary.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print("\nBiologi verification completed!")
