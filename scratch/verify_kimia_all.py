import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

OUT_DIR = os.path.join(os.getcwd(), "scratch", "screenshots", "kimia")
os.makedirs(OUT_DIR, exist_ok=True)

test_cases = [
    # Kimia P1
    {"pkg": 1, "q": 2, "issues": "G (Gambar harus titrasi/kimia, bukan ekonomi)"},
    {"pkg": 1, "q": 4, "issues": "G (Grafik laju SO3) + P (10^-2 M/detik)"},
    {"pkg": 1, "q": 6, "issues": "P (sp2 / sp3 superskrip)"},
    {"pkg": 1, "q": 8, "issues": "P (10^-10 pangkat minus)"},
    {"pkg": 1, "q": 10, "issues": "G (Gambar sel elektrokimia/kimia)"},
    {"pkg": 1, "q": 17, "issues": "P (10^-6 M, pH 4)"},
    {"pkg": 1, "q": 19, "issues": "P + G (Pilihan rumus mol fraksi)"},
    {"pkg": 1, "q": 20, "issues": "P (Laju reaksi, suhu 30°C, 60°C)"},
    # Kimia P2
    {"pkg": 2, "q": 1, "issues": "G (Sistem koloid / kimia, bukan geografi)"},
    {"pkg": 2, "q": 3, "issues": "P (Pangkat / reaksi kimia)"},
    {"pkg": 2, "q": 5, "issues": "G (Grafik titrasi/titik ekuivalen)"},
    {"pkg": 2, "q": 6, "issues": "G (Grafik entalpi pembentukan)"},
    {"pkg": 2, "q": 8, "issues": "G (Struktur Lewis/ikatan)"},
    {"pkg": 2, "q": 9, "issues": "G (Diagram sel volta)"},
    {"pkg": 2, "q": 10, "issues": "G (Tabel indikator limbah + pilihan a-e)"},
    {"pkg": 2, "q": 11, "issues": "G (Kurva titrasi basa)"},
    {"pkg": 2, "q": 12, "issues": "G (Grafik kelarutan garam)"},
    {"pkg": 2, "q": 14, "issues": "P (Notasi laju / konsentrasi)"},
    {"pkg": 2, "q": 15, "issues": "G (Bagan proses kontak/kimia)"},
    {"pkg": 2, "q": 16, "issues": "G (Grafik energi aktivasi)"},
    {"pkg": 2, "q": 19, "issues": "G + P (Bagan pemurnian air + eksponen)"},
    {"pkg": 2, "q": 20, "issues": "G + P (Bagan korosi besi + eksponen)"},
    {"pkg": 2, "q": 21, "issues": "P (Derajat Celcius 400°C, ±25°C)"},
    {"pkg": 2, "q": 22, "issues": "G (Grafik kesetimbangan [A], [B], bukan singa)"},
    {"pkg": 2, "q": 23, "issues": "P (Eksponen Kc/Kp/laju)"},
    {"pkg": 2, "q": 24, "issues": "G (Skema elektroda X dan Y, bukan singa)"}
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # 1. Desktop Pass
    d_ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    d_page = d_ctx.new_page()

    # 2. Mobile Pass
    m_ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
    m_page = m_ctx.new_page()

    records = []

    for tc in test_cases:
        pkg = tc["pkg"]
        q = tc["q"]
        print(f"Verifying Kimia P{pkg} Q{q}...")

        # --- Desktop ---
        d_url = f"http://localhost:8080/?subject=kimia&paket={pkg}"
        d_page.goto(d_url)
        d_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        d_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.0)
        d_ss = os.path.join(OUT_DIR, f"kimia_p{pkg}_q{q:02d}_desktop.png")
        d_page.screenshot(path=d_ss, full_page=False)

        # Inspect DOM & Images
        stim_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#stimulusContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight}))")
        opt_imgs = d_page.evaluate("() => Array.from(document.querySelectorAll('#optionsContainer img')).map(i => ({src: i.src, complete: i.complete, nw: i.naturalWidth, nh: i.naturalHeight}))")
        p_text = d_page.inner_text("#promptContainer") if d_page.query_selector("#promptContainer") else ""
        o_text = d_page.inner_text("#optionsContainer") if d_page.query_selector("#optionsContainer") else ""

        # --- Mobile ---
        m_url = f"http://localhost:8080/?subject=kimia&paket={pkg}"
        m_page.goto(m_url)
        m_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        m_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.0)
        m_ss = os.path.join(OUT_DIR, f"kimia_p{pkg}_q{q:02d}_mobile.png")
        m_page.screenshot(path=m_ss, full_page=False)

        # Check for lion or ekonomi leak
        has_lion = any("lion" in i["src"].lower() or "bahasa_inggris" in i["src"].lower() for i in stim_imgs + opt_imgs)
        has_ekonomi = any("ekonomi" in i["src"].lower() for i in stim_imgs + opt_imgs)
        all_imgs_loaded = all(i["complete"] and i["nw"] > 0 for i in stim_imgs + opt_imgs)

        status = "Fixed" if (not has_lion and not has_ekonomi and all_imgs_loaded) else "Belum"

        record = {
            "mapel": "Kimia", "paket": pkg, "nomor": q,
            "masalah": tc["issues"],
            "status": status,
            "desktop_ss": d_ss, "mobile_ss": m_ss,
            "stim_imgs_count": len(stim_imgs),
            "opt_imgs_count": len(opt_imgs),
            "prompt_sample": p_text[:80].replace("\n", " "),
            "opts_sample": o_text[:100].replace("\n", " ")
        }
        records.append(record)
        print(f"  -> P{pkg} Q{q}: Status={status} (StimImgs={len(stim_imgs)}, OptImgs={len(opt_imgs)}, AllLoaded={all_imgs_loaded})")

    browser.close()

    with open("scratch/kimia_verification_summary.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print("\nKimia verification complete!")

if __name__ == "__main__":
    pass  # logic is above

