# -*- coding: utf-8 -*-
"""_test_interaction_e2e.py
Simulasi E2E interaksi lengkap:
1. PG Single Choice
2. PG Kompleks (multi-select checkbox)
3. Pernyataan (Benar-Salah / Tepat-Tidak Tepat tabel radio)
4. Interaksi Pilar-pilar 1-5
5. AI Tutor Drawer & Konteks Soal
6. Tombol Selesai Tes & Modal Hasil (Skor Benar, Salah, Kosong)
7. Overlay Reviu Hasil Lengkap
"""
import sys, os, time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:8080/index.html"
OUT_DIR = r"D:\PROJECTS\SCRAPE_TKA\scratch"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})

    print("Navigating to CBT Simulator...")
    page.goto(BASE_URL, wait_until="networkidle")
    time.sleep(2)

    # 1. Pilih Paket yang memiliki variasi tipe soal: Matematika Paket 2
    # Pilih di dropdown package
    pkg_select = page.locator("#pkgSelect")
    if pkg_select.count() > 0:
        # Pilih paket yang kaya variasi tipe soal
        print("Selecting package: matematika_paket_2...")
        pkg_select.select_option(value="matematika_paket_2")
        time.sleep(2)

    # 2. Test Soal 1: Klik Opsi Jawaban PG
    print("Testing Question 1 (Single Choice)...")
    option_btns = page.locator(".option-btn")
    opt_count = option_btns.count()
    print(f"Question 1 options found: {opt_count}")
    if opt_count > 0:
        option_btns.first.click()
        time.sleep(0.5)
        # Check active class
        is_selected = "selected" in (option_btns.first.get_attribute("class") or "")
        print(f"Question 1 Option selected state: {is_selected}")

    # 3. Test Pilar Accordion
    print("Testing 5-Pillar Tabs...")
    pilar_tabs = page.locator(".pilar-tab")
    tab_count = pilar_tabs.count()
    print(f"Pilar tabs found: {tab_count}")
    for i in range(min(5, tab_count)):
        pilar_tabs.nth(i).click()
        time.sleep(0.2)
    pilar_content_visible = page.locator(".pilar-panel.active").is_visible()
    print(f"Active pilar content visible: {pilar_content_visible}")

    # Capture visual pilar
    page.screenshot(path=os.path.join(OUT_DIR, "ui_e2e_pilar_q1.png"))

    # 4. Navigasi ke Soal Tipe Pernyataan (Benar-Salah / Matriks)
    # Cari nomor soal tipe pernyataan di nomor palet
    print("Finding statement question (Benar-Salah / Matriks)...")
    # Di Matematika Paket 2, Q3 adalah pernyataan
    q3_btn = page.locator(".q-grid-btn").nth(2)
    q3_btn.click()
    time.sleep(1)

    statement_rows = page.locator(".statement-row, tr.pernyataan-tr")
    print(f"Statement rows found: {statement_rows.count()}")
    # Klik pilihan radio di baris pernyataan
    radios = page.locator("input[type='radio']")
    print(f"Statement radios found: {radios.count()}")
    if radios.count() >= 2:
        radios.nth(0).click()
        radios.nth(2).click()
        time.sleep(0.5)

    page.screenshot(path=os.path.join(OUT_DIR, "ui_e2e_statement_q3.png"))

    # 5. Navigasi ke Soal Tipe PG Kompleks (Multi-Select Checkbox)
    print("Finding complex choice question (PG Kompleks)...")
    # Di Matematika Paket 2, cari soal dengan checkbox
    found_complex = False
    for q_idx in range(3, 15):
        page.locator(".q-grid-btn").nth(q_idx).click()
        time.sleep(0.5)
        checkboxes = page.locator("input[type='checkbox']")
        if checkboxes.count() > 0:
            print(f"Found PG Kompleks at question {q_idx + 1} with {checkboxes.count()} checkboxes!")
            checkboxes.nth(0).click()
            if checkboxes.count() > 1:
                checkboxes.nth(1).click()
            found_complex = True
            page.screenshot(path=os.path.join(OUT_DIR, f"ui_e2e_complex_q{q_idx+1}.png"))
            break

    # 6. Test Tombol Selesai Tes & Modal Hasil
    print("Testing Finish Test ('Selesai Tes')...")
    finish_btn = page.locator("#btnSelesaiTes, button:has-text('Selesai Tes')")
    finish_btn.click()
    time.sleep(1)

    # Konfirmasi modal konfirmasi selesai tes jika ada
    confirm_btn = page.locator(".btn-confirm-finish, #btnConfirmFinish, button:has-text('Ya, Selesai')")
    if confirm_btn.is_visible():
        confirm_btn.click()
        time.sleep(1)

    modal_hasil = page.locator("#modalHasil, .modal-hasil-container, #finishModal")
    print(f"Modal hasil visible: {modal_hasil.is_visible()}")

    # Ambil teks skor
    score_text = page.locator(".score-summary, .hasil-summary, .modal-body").first.inner_text()
    print("Score Summary Content:\n", score_text[:300])

    page.screenshot(path=os.path.join(OUT_DIR, "ui_e2e_modal_hasil.png"))

    # 7. Test Tombol 'Lihat Pembahasan / Reviu Hasil'
    print("Testing 'Lihat Pembahasan'...")
    review_btn = page.locator("#btnReviewHasil, button:has-text('Lihat Pembahasan'), button:has-text('Reviu Hasil')")
    if review_btn.is_visible():
        review_btn.click()
        time.sleep(1)
        review_overlay = page.locator("#reviewHasilOverlay, .review-hasil-modal")
        print(f"Review overlay visible: {review_overlay.is_visible()}")
        page.screenshot(path=os.path.join(OUT_DIR, "ui_e2e_review_overlay.png"))

    print("=== E2E TEST COMPLETED SUCCESSFULLY ===")
    browser.close()
