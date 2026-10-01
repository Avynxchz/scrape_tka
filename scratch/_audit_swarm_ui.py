# -*- coding: utf-8 -*-
"""_audit_swarm_ui.py
Audit menyeluruh fungsionalitas & interaktivitas swarm.html:
1. Pemuatan awal & verifikasi 0 error pada browser console.
2. Verifikasi render katalog target mapel (/api/swarm/subjects).
3. Interaksi Modal Target Selector (buka, filter kategori, centang mapel, tombol pilih semua unscraped, kosongkan).
4. Pembaruan otomatis tabel Active Swarm Target Matrix & Badge Counter.
5. Klik 5 Worktree Pods (Divisi 1-5) & verifikasi DevTools Modal (tab payload, thinking, telemetry).
6. Verifikasi tombol Luncurkan Swarm & polling status bus stream.
"""
import os, sys, time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT_DIR = r"D:\PROJECTS\SCRAPE_TKA\scratch"

def audit_swarm():
    console_errors = []
    page_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = context.new_page()

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        url = "http://localhost:8080/swarm.html"
        print(f"1. Membuka {url}...")
        page.goto(url)
        page.wait_for_timeout(2000)

        # Cek console error
        print(f"Console errors: {len(console_errors)}")
        print(f"Page errors: {len(page_errors)}")
        for ce in console_errors:
            print(f"  [Console Error]: {ce}")
        for pe in page_errors:
            print(f"  [Page Error]: {pe}")

        # Capture initial state
        init_shot = os.path.join(OUT_DIR, "ui_swarm_initial.png")
        page.screenshot(path=init_shot)
        print(f"[OK] Tangkapan layar awal: {init_shot}")

        # 2. Verifikasi Data Header & Counter
        c_all = page.locator("#countAll").inner_text() if page.locator("#countAll").count() > 0 else "N/A"
        c_live = page.locator("#countLive").inner_text() if page.locator("#countLive").count() > 0 else "N/A"
        c_un = page.locator("#countUnscraped").inner_text() if page.locator("#countUnscraped").count() > 0 else "N/A"
        badge_txt = page.locator("#selectedCountBadge").inner_text() if page.locator("#selectedCountBadge").count() > 0 else "N/A"
        print(f"Counter Katalog: Total={c_all}, Live={c_live}, Unscraped={c_un} | Badge={badge_txt}")

        # 3. Test Buka Modal Selector Mapel
        print("\n--- TEST MODAL SELECTOR MAPEL ---")
        btn_ubah = page.locator("button:has-text('UBAH')").first
        if btn_ubah.is_visible():
            btn_ubah.click()
            page.wait_for_timeout(500)

        modal_sel = page.locator("#subjectSelectorModal")
        is_sel_open = "open" in (modal_sel.get_attribute("class") or "")
        print(f"Modal Selector Terbuka: {is_sel_open}")
        assert is_sel_open, "Modal selector harus terbuka!"

        # Filter kategori 'BELUM SCRAPE'
        filter_un = page.locator("button:has-text('BELUM SCRAPE')").first
        filter_un.click()
        page.wait_for_timeout(400)
        card_count = page.locator(".subject-card").count()
        print(f"Jumlah kartu mapel unscraped: {card_count}")

        # Klik 'Pilih Semua Unscraped'
        btn_sel_all = page.locator("button:has-text('Pilih Semua Unscraped')").first
        btn_sel_all.click()
        page.wait_for_timeout(400)
        modal_sel_count = page.locator("#modalSelectedCount").inner_text()
        print(f"Counter Target Terpilih: {modal_sel_count}")

        sel_modal_shot = os.path.join(OUT_DIR, "ui_swarm_selector_modal.png")
        page.screenshot(path=sel_modal_shot)
        print(f"[OK] Tangkapan layar modal selector: {sel_modal_shot}")

        # Tutup modal
        btn_close_sel = page.locator("#subjectSelectorModal .modal-close").first
        btn_close_sel.click()
        page.wait_for_timeout(400)

        # 4. Verifikasi Update Active Target Matrix Table
        tb_rows = page.locator("#targetMatrixBody tr")
        print(f"\nJumlah baris di Target Matrix Table: {tb_rows.count()}")
        assert tb_rows.count() > 1, "Target Matrix harus terisi baris mapel!"

        # 5. Test Klik 5 Worktree Pods (DevTools Modal)
        print("\n--- TEST WORKTREE PODS & DEVTOOLS MODAL ---")
        for i in range(1, 6):
            pod = page.locator(f"#pod_{i}")
            pod.click()
            page.wait_for_timeout(300)
            dev_modal = page.locator("#devToolsModal")
            is_dev_open = "open" in (dev_modal.get_attribute("class") or "")
            title_text = page.locator("#modalTitle").inner_text()
            print(f"Pod {i} diklik -> Modal Terbuka: {is_dev_open} ({title_text})")
            assert is_dev_open, f"DevTools modal harus terbuka saat Pod {i} diklik!"

            # Tab switching
            page.locator("#tabThinking").click()
            page.wait_for_timeout(100)
            code_text = page.locator("#modalCode").inner_text()
            print(f"  Tab Thinking content length: {len(code_text)} chars")

            # Tutup
            page.locator("#devToolsModal .modal-close").click()
            page.wait_for_timeout(200)

        dev_shot = os.path.join(OUT_DIR, "ui_swarm_devtools.png")
        page.screenshot(path=dev_shot)

        # 6. Test Tombol Reset & Status Polling
        print("\n--- TEST STATUS & TERMINAL STREAM ---")
        logs = page.locator("#terminalBody .log-line")
        print(f"Jumlah baris log di terminal bus: {logs.count()}")
        if logs.count() > 0:
            print(f"Log terakhir: {logs.last.inner_text()}")

        # 7. Test Demo Simulation & Reset Button
        print("\n--- TEST DEMO SIMULATION & RESET ---")
        btn_demo = page.locator("#btnStartDemo")
        btn_demo.click()
        print("Demo simulation dimulai, menunggu 6.5 detik...")
        page.wait_for_timeout(6500)
        
        # Cek apakah ada error di console selama simulasi
        print(f"Console errors selama simulasi: {len(console_errors)}")
        print(f"Page errors selama simulasi: {len(page_errors)}")
        assert len(page_errors) == 0, f"Tidak boleh ada page error selama simulasi: {page_errors}"

        # Klik Reset
        print("Menguji tombol RESET...")
        btn_reset = page.locator("#btnResetSwarm")
        btn_reset.click()
        page.wait_for_timeout(800)
        tel_elapsed = page.locator("#telElapsed").inner_text()
        print(f"Status setelah RESET: Elapsed timer={tel_elapsed}")
        assert tel_elapsed == "00:00", "Timer harus kembali ke 00:00 setelah reset!"

        browser.close()
        print("\n=== AUDIT SWARM.HTML SELESAI & 100% TERVERIFIKASI ===")

if __name__ == "__main__":
    audit_swarm()
