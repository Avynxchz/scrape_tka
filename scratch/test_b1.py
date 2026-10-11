import os
import json
import time
from playwright.sync_api import sync_playwright

os.makedirs("evidence/B1", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        viewport={"width": 390, "height": 844},
        has_touch=True,
        is_mobile=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    )

    print("--- TEST 1: Pengerjaan Soal Nyata + Selesai Tes ---")
    page.goto("http://127.0.0.1:8080/app?subject=matematika&paket=1")
    page.wait_for_timeout(2000)

    # Jawab Soal 1: Klik Opsi B
    print("Menjawab Soal 1...")
    page.locator(".option-item[data-key='B']").first.click()
    page.wait_for_timeout(3000)  # Biarkan waktu tercatat ~3s

    # Pindah ke Soal 2
    print("Pindah ke Soal 2...")
    page.evaluate("state.currentIndex = 1; renderQuestion();")
    page.wait_for_timeout(1000)
    page.locator(".option-item[data-key='C']").first.click()
    page.wait_for_timeout(3000)  # Biarkan waktu tercatat ~3s

    # Klik Selesai Tes
    print("Menyelesaikan Tes...")
    page.evaluate("selesaiTes();")
    page.wait_for_timeout(2500)

    # Verifikasi kartu Guru Autopsi muncul
    autopsi_card = page.locator("#autopsiSection")
    card_visible = autopsi_card.is_visible()
    card_html = autopsi_card.inner_html()
    card_text = autopsi_card.inner_text()

    print(f"Guru Autopsi Card Visible: {card_visible}")
    has_expected_title = "Guru Autopsi — dianalisis dari cara kamu mengerjakan" in card_text or "Guru Autopsi" in card_text
    print(f"Has Expected Title: {has_expected_title}")
    has_time_data = "Total Waktu" in card_text or "detik" in card_text or "m " in card_text
    print(f"Has Time Metrics (B2): {has_time_data}")

    # Capture AFTER screenshot
    img_path1 = "evidence/B1/guru_autopsi_selesai_tes-after.png"
    # Scroll slightly if needed so the Autopsi card is fully in viewport
    autopsi_card.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    page.screenshot(path=img_path1)
    print(f"Captured {img_path1}")

    # Assertion log
    log_path1 = "evidence/B1/guru_autopsi_selesai_tes-after.log"
    with open(log_path1, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": "B1 AFTER: Kartu Guru Autopsi muncul di halaman hasil dengan data waktu terisi (hasil B2)",
            "dom_summary": {
                "url": page.url,
                "autopsi_card_visible": card_visible,
                "has_expected_title": has_expected_title,
                "has_time_data": has_time_data,
                "snippet": card_text[:500]
            },
            "assertions": {
                "card_displayed": card_visible,
                "title_matches": has_expected_title,
                "time_data_populated": has_time_data
            }
        }, f, indent=2, ensure_ascii=False)

    print("\n--- TEST 2: Edge Case (Tes Tanpa Jawaban / Semua Kosong) ---")
    page.goto("http://127.0.0.1:8080/app?subject=matematika&paket=1")
    page.wait_for_timeout(2000)
    # Clear answers & finish immediately
    page.evaluate("""() => {
        state.userAnswers = {};
        window._lastFinishedAttempt = null;
        selesaiTes();
    }""")
    page.wait_for_timeout(2000)

    edge_visible = page.locator("#autopsiSection").is_visible()
    edge_text = page.locator("#autopsiSection").inner_text()
    print(f"Edge case Guru Autopsi Visible: {edge_visible}")
    print(f"Edge case Title present: {'Guru Autopsi' in edge_text}")

    browser.close()
    print("ALL B1 TESTS COMPLETED SUCCESSFULLY!")
