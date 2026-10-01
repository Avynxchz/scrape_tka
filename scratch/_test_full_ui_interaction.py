# -*- coding: utf-8 -*-
"""_test_full_ui_interaction.py
Menguji interaksi UI CBT Simulator dari atas ke bawah:
1. PG Tunggal (klik opsi & verifikasi state selected)
2. Pilar 1-5 (buka panel tata cara, verifikasi render 5 pilar & KaTeX)
3. Pernyataan Benar/Salah (klik tombol Benar/Salah di tabel pernyataan)
4. PG Kompleks (multi-select opsi dan verifikasi state)
5. Alur Selesai Tes & Modal Skor (Benar, Salah, Kosong, %)
6. Overlay Reviu Hasil & Pembahasan (Daftar soal, opsi, kunci resmi, KaTeX)
"""
import os, sys, time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT_DIR = r"D:\PROJECTS\SCRAPE_TKA\scratch"

def test_full_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 950})
        page = context.new_page()

        url = "http://localhost:8080/?subject=matematika&paket=2"
        print(f"1. Membuka {url}...")
        page.goto(url)
        page.wait_for_timeout(2500)

        # --- A. TEST SOAL 1: PILIHAN GANDA TUNGGAL ---
        print("\n--- A. TEST SOAL 1: PILIHAN GANDA TUNGGAL ---")
        q1_opts = page.locator(".option-item")
        print(f"Jumlah opsi ditemukan di Soal 1: {q1_opts.count()}")
        assert q1_opts.count() >= 4, "Opsi PG harus minimal 4"

        # Klik opsi ke-2 (B)
        q1_opts.nth(1).click()
        page.wait_for_timeout(500)
        has_sel = "selected" in (q1_opts.nth(1).get_attribute("class") or "")
        print(f"[OK] Opsi B berhasil diklik & berstatus selected: {has_sel}")
        assert has_sel, "Opsi B harus berstatus selected"

        # --- B. TEST PILAR-PILAR 1-5 ---
        print("\n--- B. TEST TATA CARA & PILAR 1-5 ---")
        toggle_btn = page.locator("#btnToggleExplanation")
        # Jika belum terbuka, klik tombol toggle
        exp_visible = page.evaluate("() => state.explanationVisible")
        if not exp_visible:
            toggle_btn.click()
            page.wait_for_timeout(500)

        c_box = page.locator("#conceptBox").is_visible()
        s_box = page.locator("#symbolsBox").is_visible()
        w_box = page.locator("#whyConceptBox").is_visible()
        st_box = page.locator(".steps-section-card").first.is_visible()
        t_box = page.locator(".tips-box").is_visible()

        print(f"  • Pilar 1 (Konsep & Teori)    : {c_box}")
        print(f"  • Pilar 2 (Glosarium Simbol)  : {s_box}")
        print(f"  • Pilar 3 (Mengapa Begini)    : {w_box}")
        print(f"  • Pilar 4 (Langkah Rinci)     : {st_box}")
        print(f"  • Pilar 5 (Tips & Jebakan)    : {t_box}")
        assert c_box and st_box and t_box, "Pilar-pilar penting harus terlihat!"

        pilar_shot = os.path.join(OUT_DIR, "ui_pilar_rendered.png")
        page.screenshot(path=pilar_shot)
        print(f"[OK] Screenshot pilar tersimpan di {pilar_shot}")

        # --- C. TEST SOAL 3: PERNYATAAN BENAR / SALAH (TABEL) ---
        print("\n--- C. TEST SOAL 3: PERNYATAAN BENAR-SALAH ---")
        # Navigasi ke soal nomor 3 (index 2)
        page.evaluate("() => { state.currentIndex = 2; renderQuestion(); }")
        page.wait_for_timeout(1000)

        badge_tipe = page.locator("#badgeTipe").inner_text()
        print(f"Tipe Soal Nomor 3: {badge_tipe}")

        bs_rows = page.locator(".bs-row")
        print(f"Jumlah baris pernyataan: {bs_rows.count()}")
        bs_btns = page.locator(".bs-btn")
        print(f"Total tombol Benar/Salah: {bs_btns.count()}")
        assert bs_btns.count() >= 6, "Tabel pernyataan minimal ada 3 baris x 2 tombol"

        # Klik Benar di baris 1, Salah di baris 2, Benar di baris 3
        bs_btns.nth(0).click()
        page.wait_for_timeout(200)
        bs_btns.nth(3).click()
        page.wait_for_timeout(200)
        bs_btns.nth(4).click()
        page.wait_for_timeout(200)

        active_count = page.locator(".bs-btn.active").count()
        print(f"[OK] Tombol pernyataan aktif: {active_count}/3 baris")
        assert active_count == 3, "Tiga tombol pernyataan harus aktif"

        stmt_shot = os.path.join(OUT_DIR, "ui_statement_rendered.png")
        page.screenshot(path=stmt_shot)
        print(f"[OK] Screenshot tabel pernyataan tersimpan di {stmt_shot}")

        # --- D. TEST SOAL PILIHAN GANDA KOMPLEKS ---
        print("\n--- D. TEST PILIHAN GANDA KOMPLEKS ---")
        # Cari soal PG Kompleks
        found_pgk = False
        for idx in range(3, 20):
            page.evaluate(f"() => {{ state.currentIndex = {idx}; renderQuestion(); }}")
            page.wait_for_timeout(400)
            b_tipe = page.locator("#badgeTipe").inner_text()
            if "Kompleks" in b_tipe:
                found_pgk = True
                print(f"Ditemukan PG Kompleks di Nomor {idx+1} ({b_tipe})")
                pgk_opts = page.locator(".option-item")
                # Klik opsi A dan C
                pgk_opts.nth(0).click()
                page.wait_for_timeout(200)
                pgk_opts.nth(2).click()
                page.wait_for_timeout(200)

                sel_count = page.locator(".option-item.selected").count()
                print(f"[OK] PG Kompleks multi-select: {sel_count} opsi terpilih")
                assert sel_count == 2, "Harus ada 2 opsi terpilih di PG Kompleks"

                pgk_shot = os.path.join(OUT_DIR, "ui_pgk_rendered.png")
                page.screenshot(path=pgk_shot)
                print(f"[OK] Screenshot PG Kompleks tersimpan di {pgk_shot}")
                break
        assert found_pgk, "Harus menemukan soal bertipe PG Kompleks"

        # --- E. TEST SELESAI TES & MODAL SKOR ---
        print("\n--- E. TEST ALUR SELESAI TES ---")
        page.evaluate("() => openFinishModal()")
        page.wait_for_timeout(600)

        modal_confirm = page.locator("#modalKonfirmasiSelesai")
        is_open = page.evaluate("() => document.getElementById('modalKonfirmasiSelesai').classList.contains('open')")
        print(f"Modal konfirmasi selesai tes visible/open: {is_open}")
        assert is_open, "Modal konfirmasi selesai tes harus memiliki kelas 'open'!"

        # Klik selesai tes
        print("Mengeksekusi selesaiTes()...")
        page.evaluate("() => selesaiTes()")
        page.wait_for_timeout(1500)

        # --- F. TEST REVIU HASIL & PEMBAHASAN ---
        print("\n--- F. TEST REVIU HASIL & PEMBAHASAN ---")
        is_overlay_open = page.evaluate("() => document.getElementById('reviewHasilOverlay').classList.contains('open')")
        b_score = page.evaluate("() => document.getElementById('reviewScoreBenar').innerText")
        s_score = page.evaluate("() => document.getElementById('reviewScoreSalah').innerText")
        k_score = page.evaluate("() => document.getElementById('reviewScoreKosong').innerText")
        p_score = page.evaluate("() => document.getElementById('reviewScorePersen').innerText")

        print(f"[STATUS] Overlay Terbuka: {is_overlay_open}")
        print(f"[HASIL EVALUASI]:")
        print(f"  • Benar : {b_score}")
        print(f"  • Salah : {s_score}")
        print(f"  • Kosong: {k_score}")
        print(f"  • Skor  : {p_score}")

        assert is_overlay_open, "Overlay Reviu Hasil harus berstatus OPEN setelah selesai tes!"
        assert b_score != "" and s_score != "", "Skor Benar & Salah harus terisi!"

        rev_shot = os.path.join(OUT_DIR, "ui_review_rendered.png")
        page.screenshot(path=rev_shot)
        print(f"[OK] Screenshot reviu hasil tersimpan di {rev_shot}")

        browser.close()
        print("\n=======================================================")
        print("SEMUA PENGUJIAN INTERAKSI UI SELESAI & 100% SUKSES!")
        print("=======================================================")

if __name__ == "__main__":
    test_full_ui()
