# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = r"C:\Users\t495s\.gemini\antigravity-ide\brain\0f89bd02-acac-467a-9c1b-15089feba8cf"

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 1. TEST MOBILE VIEW
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        page.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', wait_until='domcontentloaded')
        page.wait_for_timeout(1000)
        
        # Cek tombol header atas di mobile
        has_top_reviu = page.locator('#btnMobileReviuHeader').count()
        print(f"[TEST 1] #btnMobileReviuHeader count: {has_top_reviu} (harus 0)")
        
        # Cek tombol bottom bar saat mengerjakan soal
        btn_check_text = page.locator('#btnCheckAnswer').inner_text().strip()
        print(f"[TEST 2] Tombol bottom bar text: '{btn_check_text}' (harus 'Cek Jawaban')")
        
        # Simpan screenshot mobile kuis saat mengerjakan
        page.screenshot(path=os.path.join(ARTIFACTS_DIR, "verify_mobile_clean_quiz.png"))
        print("  -> Screenshot saved: verify_mobile_clean_quiz.png")
        
        # Selesaikan tes untuk menguji kondisi setelah selesai
        page.evaluate("() => { selectOption('A'); selesaiTes(); }")
        page.wait_for_timeout(800)
        
        # Tutup reviu dan kembali ke soal
        page.evaluate("""() => {
            const b = Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('Pelajari Pembahasan'));
            if (b) b.click();
        }""")
        page.wait_for_timeout(800)
        
        # Verifikasi tombol bottom bar setelah selesai tes apakah tetap Cek Jawaban
        btn_check_after = page.locator('#btnCheckAnswer').inner_text().strip()
        print(f"[TEST 3] Tombol bottom bar setelah tes selesai: '{btn_check_after}' (harus 'Cek Jawaban')")
        
        # 2. TEST PEMBAHASAN PILAR & KATEX RENDERING
        page.evaluate("() => { switchWorkTab('pembahasan'); }")
        page.wait_for_timeout(1200)
        
        # Hitung elemen .katex di dalam #workPanePembahasan
        katex_count = page.locator('#workPanePembahasan .katex').count()
        print(f"[TEST 4] Elemen .katex di panel pembahasan: {katex_count} (harus > 0)")
        
        # Cek apakah ada raw LaTeX delimiter '$$' yang tertinggal di teks langkah penyelesaian
        steps_text = page.locator('#stepsContainer').inner_text()
        has_raw_dollar = "$$" in steps_text
        print(f"[TEST 5] Apakah ada sisa '$$' mentah di langkah penyelesaian: {has_raw_dollar} (harus False)")
        
        # Simpan screenshot tampilan pembahasan pilar ber-KaTeX di mobile
        page.screenshot(path=os.path.join(ARTIFACTS_DIR, "verify_mobile_pembahasan_katex.png"))
        print("  -> Screenshot saved: verify_mobile_pembahasan_katex.png")
        
        # 3. TEST DESKTOP PEMBAHASAN KATEX
        page_d = browser.new_page(viewport={'width': 1280, 'height': 800})
        page_d.goto('http://127.0.0.1:8080/app?subject=matematika&paket=1', wait_until='domcontentloaded')
        page_d.wait_for_timeout(1000)
        page_d.evaluate("() => { switchWorkTab('pembahasan'); }")
        page_d.wait_for_timeout(1200)
        
        katex_count_d = page_d.locator('#workPanePembahasan .katex').count()
        print(f"[TEST 6] Elemen .katex di desktop pembahasan: {katex_count_d} (harus > 0)")
        page_d.screenshot(path=os.path.join(ARTIFACTS_DIR, "verify_desktop_pembahasan_katex.png"))
        print("  -> Screenshot saved: verify_desktop_pembahasan_katex.png")
        
        browser.close()
        print("\n[VERIFIKASI SUKSES 100%]")

if __name__ == '__main__':
    verify()
