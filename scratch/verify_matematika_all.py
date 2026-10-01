import os, sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

OUT_DIR = os.path.join(os.getcwd(), "scratch", "screenshots", "matematika")
os.makedirs(OUT_DIR, exist_ok=True)

test_cases = [
    # Matematika P1
    {"pkg": 1, "q": 5, "issues": "B (Diagram pertidaksamaan & formula)"},
    {"pkg": 1, "q": 7, "issues": "B (Opsi pecahan / formula invers)"},
    {"pkg": 1, "q": 8, "issues": "B (Komposisi fungsi f(g(x)))"},
    {"pkg": 1, "q": 12, "issues": "B+L (Pecahan bakteri 1/2 dan 1/4 inline teks)"},
    {"pkg": 1, "q": 13, "issues": "Tabel responsive Interval, Indikator, Interpretasi"},
    {"pkg": 1, "q": 15, "issues": "B (Diagram rak buku proporsional & opsi pecahan)"},
    {"pkg": 1, "q": 43, "issues": "B (Pernyataan grafik f(x)=4(x^2-8x+12))"},
    # Matematika P2
    {"pkg": 2, "q": 2, "issues": "K (Bentuk sederhana pecahan akar diperbesar)"},
    {"pkg": 2, "q": 3, "issues": "Gambar tidak sama persis -> Verifikasi 100% presisi gambar resmi CBT Pusmendik"},
    {"pkg": 2, "q": 8, "issues": "Di sumber besar, di kita kecil -> max-height 460px desktop & responsif aman mobile"},
    {"pkg": 2, "q": 14, "issues": "K (Diagram koordinat rotasi/refleksi opsi A-E diperbesar & terbaca)"}
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
        print(f"Verifying Matematika P{pkg} Q{q}...")

        # Desktop
        d_url = f"http://localhost:8080/?subject=matematika&paket={pkg}"
        d_page.goto(d_url)
        d_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        d_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.2)
        d_ss = os.path.join(OUT_DIR, f"matematika_p{pkg}_q{q:02d}_desktop.png")
        d_page.screenshot(path=d_ss, full_page=False)

        stim_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#stimulusContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight, w: i.offsetWidth, h: i.offsetHeight, cls: i.className}))")
        prompt_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#promptContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight, w: i.offsetWidth, h: i.offsetHeight, cls: i.className}))")
        opt_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#optionsContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight, w: i.offsetWidth, h: i.offsetHeight, cls: i.className}))")

        all_imgs = stim_imgs + prompt_imgs + opt_imgs

        # Mobile
        m_url = f"http://localhost:8080/?subject=matematika&paket={pkg}"
        m_page.goto(m_url)
        m_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        m_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.2)
        m_ss = os.path.join(OUT_DIR, f"matematika_p{pkg}_q{q:02d}_mobile.png")
        m_page.screenshot(path=m_ss, full_page=False)

        m_overflow = m_page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")

        has_foreign = any("biologi" in i["src"].lower() or "ekonomi" in i["src"].lower() for i in all_imgs)
        all_loaded = all(i["complete"] and i["nw"] > 0 for i in all_imgs) if all_imgs else True

        # Khusus Q15: gambar rak buku harus diagram-img bukan icon mini
        q15_ok = True
        if pkg == 1 and q == 15:
            q15_ok = any('diagram-img' in i['cls'] and i['h'] > 150 for i in stim_imgs)

        # Khusus Q8 P2: gambar grafik harus leluasa (w > 400 di desktop)
        q8_ok = True
        if pkg == 2 and q == 8:
            q8_ok = any(i['w'] >= 450 for i in stim_imgs)

        status = "Fixed" if (not has_foreign and all_loaded and not m_overflow and q15_ok and q8_ok) else "Belum"

        record = {
            "mapel": "Matematika", "paket": pkg, "nomor": q,
            "masalah": tc["issues"], "status": status,
            "desktop_ss": d_ss, "mobile_ss": m_ss,
            "stim_imgs_count": len(stim_imgs),
            "opt_imgs_count": len(opt_imgs),
            "mobile_overflow": m_overflow,
            "q15_ok": q15_ok,
            "q8_ok": q8_ok
        }
        records.append(record)
        print(f"  -> P{pkg} Q{q}: Status={status} (AllImgs={len(all_imgs)}, Loaded={all_loaded}, Overflow={m_overflow})")

    browser.close()

    with open("scratch/matematika_verification_summary.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print("\nMatematika verification completed!")
