import os, sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

OUT_BASE = os.path.join(os.getcwd(), "scratch", "screenshots")

test_cases = [
    # GEOGRAFI
    {"mapel": "geografi", "pkg": 1, "q": 3, "issues": "G (Peta/Citra Geografi resmi CBT P1 Q3)"},
    {"mapel": "geografi", "pkg": 1, "q": 4, "issues": "G (Peta/Citra Geografi resmi CBT P1 Q4)"},
    {"mapel": "geografi", "pkg": 1, "q": 5, "issues": "G (Peta/Citra Geografi resmi CBT P1 Q5)"},
    {"mapel": "geografi", "pkg": 1, "q": 7, "issues": "G (Peta/Citra Geografi resmi CBT P1 Q7)"},
    {"mapel": "geografi", "pkg": 2, "q": 1, "issues": "Z + AI (Peta Geografi P2 Q1 Zoom & AI Context)"},
    {"mapel": "geografi", "pkg": 2, "q": 4, "issues": "Z + AI (Peta Geografi P2 Q4 Zoom & AI Context)"},

    # SOSIOLOGI
    {"mapel": "sosiologi", "pkg": 1, "q": 2, "issues": "Infografis penuh teks diperbesar + Z (Kriteria Game Daring)"},
    {"mapel": "sosiologi", "pkg": 1, "q": 12, "issues": "Infografis penuh teks diperbesar + Z (Durasi Medsos)"},
    {"mapel": "sosiologi", "pkg": 1, "q": 16, "issues": "Infografis penuh teks diperbesar + Z (Jenis Norma Sosial)"},
    {"mapel": "sosiologi", "pkg": 2, "q": 5, "issues": "Infografis diperbesar + Z + AI context (Kelompok Sosial)"},
    {"mapel": "sosiologi", "pkg": 2, "q": 6, "issues": "Tabel kualitatif diperbesar + Z + AI context (Pelayanan Publik)"},

    # ANTROPOLOGI
    {"mapel": "antropologi", "pkg": 2, "q": 8, "issues": "K (Foto Kain Ulos Batak diperbesar & tidak tertekan 2.4em)"},

    # BAHASA INGGRIS LANJUT
    {"mapel": "bahasa_inggris_lanjut", "pkg": 2, "q": 22, "issues": "Gambar opsi jawaban diperbesar (Diagram 600x150 opsi A-E)"},

    # BAHASA ARAB
    {"mapel": "bahasa_arab", "pkg": 1, "q": 5, "issues": "Gambar rata kanan (Stimulus & opsi bahasa Arab)"},
    {"mapel": "bahasa_arab", "pkg": 1, "q": 6, "issues": "Gambar rata kanan (Stimulus & opsi bahasa Arab)"},
    {"mapel": "bahasa_arab", "pkg": 1, "q": 9, "issues": "Gambar rata kanan (Stimulus & pertanyaan)"},
    {"mapel": "bahasa_arab", "pkg": 2, "q": 9, "issues": "Gambar rata kanan (Stimulus P2 Q9)"},
    {"mapel": "bahasa_arab", "pkg": 2, "q": 27, "issues": "Gambar rata kanan (Stimulus P2 Q27)"},

    # BAHASA JERMAN
    {"mapel": "bahasa_jerman", "pkg": 2, "q": 3, "issues": "K (Anzeige iklan flyer 585x611 diperbesar)"},
    {"mapel": "bahasa_jerman", "pkg": 2, "q": 13, "issues": "K (Tabel Unsere Schul-AGs 811x306 diperbesar tidak tertekan 240px)"},
    {"mapel": "bahasa_jerman", "pkg": 2, "q": 14, "issues": "K (Tabel Unsere Schul-AGs 811x306 diperbesar)"},
    {"mapel": "bahasa_jerman", "pkg": 2, "q": 15, "issues": "K (Tabel Unsere Schul-AGs 811x306 diperbesar)"},
    {"mapel": "bahasa_jerman", "pkg": 2, "q": 26, "issues": "K (Infografik teks 1024x968 diperbesar)"},

    # BAHASA PRANCIS
    {"mapel": "bahasa_prancis", "pkg": 2, "q": 4, "issues": "K (Gambar opsi jawaban diperbesar)"},
    {"mapel": "bahasa_prancis", "pkg": 2, "q": 6, "issues": "K (Poster stimulus 875x1024 diperbesar)"},
    {"mapel": "bahasa_prancis", "pkg": 2, "q": 7, "issues": "K (Infografik stimulus 962x764 diperbesar)"},
    {"mapel": "bahasa_prancis", "pkg": 2, "q": 8, "issues": "K (Stimulus 962x764 & gambar opsi jawaban diperbesar)"},
    {"mapel": "bahasa_prancis", "pkg": 2, "q": 13, "issues": "K (Gambar opsi jawaban diperbesar)"},
    {"mapel": "bahasa_prancis", "pkg": 2, "q": 15, "issues": "K (Poster stimulus 667x552 diperbesar)"},
    {"mapel": "bahasa_prancis", "pkg": 2, "q": 17, "issues": "K (Poster stimulus 724x1024 diperbesar)"},
    {"mapel": "bahasa_prancis", "pkg": 2, "q": 29, "issues": "K (Gambar opsi jawaban diperbesar)"}
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    d_ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    d_page = d_ctx.new_page()

    m_ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
    m_page = m_ctx.new_page()

    results_by_mapel = {}

    for tc in test_cases:
        mapel = tc["mapel"]
        pkg = tc["pkg"]
        q = tc["q"]
        subj_dir = os.path.join(OUT_BASE, mapel)
        os.makedirs(subj_dir, exist_ok=True)

        print(f"Verifying {mapel} P{pkg} Q{q}...")

        # Desktop
        d_url = f"http://localhost:8080/?subject={mapel}&paket={pkg}"
        d_page.goto(d_url)
        d_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        d_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.2)
        d_ss = os.path.join(subj_dir, f"{mapel}_p{pkg}_q{q:02d}_desktop.png")
        d_page.screenshot(path=d_ss, full_page=False)

        all_imgs = d_page.evaluate("""() => {
            const queryImgs = sel => Array.from(document.querySelectorAll(sel)).map(i => ({
                src: i.src.split('/').pop(),
                complete: i.complete,
                nw: i.naturalWidth,
                nh: i.naturalHeight,
                w: i.offsetWidth,
                h: i.offsetHeight,
                cls: i.className
            }));
            return queryImgs('#stimulusContainer img').concat(
                   queryImgs('#promptContainer img'),
                   queryImgs('#optionsContainer img')
            );
        }""")

        # Mobile
        m_url = f"http://localhost:8080/?subject={mapel}&paket={pkg}"
        m_page.goto(m_url)
        m_page.wait_for_load_state("networkidle")
        time.sleep(0.3)
        m_page.evaluate(f"state.currentIndex = {q - 1}; renderQuestion();")
        time.sleep(1.2)
        m_ss = os.path.join(subj_dir, f"{mapel}_p{pkg}_q{q:02d}_mobile.png")
        m_page.screenshot(path=m_ss, full_page=False)

        m_overflow = m_page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")

        has_foreign = any("singa" in i["src"].lower() for i in all_imgs)
        all_loaded = all(i["complete"] and i["nw"] > 0 for i in all_imgs) if all_imgs else True

        # Mapel-specific checks
        extra_ok = True
        if mapel == "antropologi" and q == 8:
            # Foto ulos tidak boleh tertekan <= 50px
            extra_ok = any(i["h"] > 100 for i in all_imgs)
        elif mapel == "bahasa_jerman" and q in [13, 14, 15]:
            # Tabel AGs tidak boleh tertekan <= 240px lebar
            extra_ok = any(i["w"] > 300 for i in all_imgs)
        elif mapel == "bahasa_inggris_lanjut" and q == 22:
            # Opsi jawaban diagram 600x150 tidak boleh < 80px tinggi
            extra_ok = any(i["h"] >= 80 for i in all_imgs)

        status = "Fixed" if (not has_foreign and all_loaded and not m_overflow and extra_ok) else "Belum"

        record = {
            "mapel": mapel, "paket": pkg, "nomor": q,
            "masalah": tc["issues"], "status": status,
            "desktop_ss": d_ss, "mobile_ss": m_ss,
            "all_imgs_count": len(all_imgs),
            "all_loaded": all_loaded,
            "mobile_overflow": m_overflow,
            "extra_ok": extra_ok
        }

        if mapel not in results_by_mapel:
            results_by_mapel[mapel] = []
        results_by_mapel[mapel].append(record)

        print(f"  -> {mapel} P{pkg} Q{q}: Status={status} (Imgs={len(all_imgs)}, Loaded={all_loaded}, Overflow={m_overflow}, ExtraOk={extra_ok})")

    browser.close()

    with open("scratch/batch_verification_summary.json", "w", encoding="utf-8") as f:
        json.dump(results_by_mapel, f, indent=2)
    print("\nBatch verification completed!")
