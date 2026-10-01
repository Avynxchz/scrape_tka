# -*- coding: utf-8 -*-
import os
import sys
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()

        url = "http://localhost:8080/?subject=matematika_lanjut&paket=2"
        print(f"Opening {url} ...")
        page.goto(url)
        page.wait_for_timeout(2500)

        # 1. Simulasikan menjawab soal 1 & 2
        print("Answering question 1 and 2...")
        page.evaluate("""() => {
            selectOption('B', false); // Jawab nomor 1
            state.currentIndex = 1;   // Pindah ke nomor 2
            renderQuestion();
            selectOption('A', false); // Jawab nomor 2
        }""")
        page.wait_for_timeout(1000)

        # 2. Buka modal Selesai Tes
        print("Opening finish modal...")
        page.evaluate("() => { openFinishModal(); }")
        page.wait_for_timeout(500)

        out_modal = os.path.join("scratch", "ui_finish_modal.png")
        page.screenshot(path=out_modal)
        print(f"[OK] Modal Selesai Tes screenshot: {out_modal}")

        # 3. Klik Selesai Tes (trigger selesaiTes())
        print("Clicking Selesai Tes...")
        page.evaluate("() => { selesaiTes(); }")
        page.wait_for_timeout(1500)

        # Cek apakah overlay reviewHasilOverlay memiliki class 'open'
        is_open = page.evaluate("() => document.getElementById('reviewHasilOverlay').classList.contains('open')")
        benar = page.evaluate("() => document.getElementById('reviewScoreBenar').innerText")
        salah = page.evaluate("() => document.getElementById('reviewScoreSalah').innerText")
        kosong = page.evaluate("() => document.getElementById('reviewScoreKosong').innerText")
        persen = page.evaluate("() => document.getElementById('reviewScorePersen').innerText")

        print(f"[REVIEW STATUS] Overlay Open: {is_open}")
        print(f"[SCORES] Benar: {benar}, Salah: {salah}, Kosong: {kosong}, Skor: {persen}")

        out_review = os.path.join("scratch", "ui_review_hasil.png")
        page.screenshot(path=out_review)
        print(f"[OK] Reviu Hasil Simulasi screenshot: {out_review}")

        browser.close()

if __name__ == "__main__":
    run()
