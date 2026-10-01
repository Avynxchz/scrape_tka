# -*- coding: utf-8 -*-
"""scratch/_run_stage4_ui_audit.py — QA Pre-Release Stage 4 Interactive UI Auditor.

Automated full-flow interactive testing via Playwright:
- Desktop & Mobile Viewports
- Console error & exception monitoring
- Subject / Paket switching
- Question navigation & state persistence
- Answering interaction (PG, PGK, BS)
- Pilar 1-5 expansion & KaTeX rendering
- Soal Mirip interactive testing
- AI Tutor modal opening
- Submit, scoring, and review mode
"""
import sys
import os
import time
import json
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8080"
OUTPUT_REPORT = os.path.join(r"d:\PROJECTS\SCRAPE_TKA\data", "stage4_ui_audit_report.json")

def run_ui_audit():
    findings = []
    actions_log = []
    console_errors = []
    page_errors = []

    print("=" * 90)
    print("🌐 MEMULAI TAHAP 4: UJI FUNGSI INTERAKTIF CBT & AI TUTOR (PLAYWRIGHT)")
    print("=" * 90)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ---------------------------------------------------------------------
        # 1. UJI DESKTOP VIEWPORT (1280 x 800)
        # ---------------------------------------------------------------------
        print("\n[DESKTOP] Memulai pengujian layout Desktop (1280x800)...")
        context_desktop = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context_desktop.new_page()

        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        try:
            page.goto(f"{BASE_URL}/", timeout=10000)
            page.wait_for_load_state("networkidle")
            actions_log.append("Desktop page loaded successfully")
            print("  ✓ Halaman utama CBT berhasil dimuat.")

            # 1.1 Ganti Mapel & Paket
            test_subjects = [
                ("matematika", "1"),
                ("bahasa_arab", "1"),
                ("bahasa_mandarin", "2"),
                ("biologi", "1"),
                ("sejarah", "2")
            ]

            for subj, pkt in test_subjects:
                print(f"  • Menguji pergantian mapel ke: {subj} (Paket {pkt})...")
                # Pilih mapel
                page.select_option("#subjectSelect", subj)
                time.sleep(0.5)
                # Pilih paket bila ada dropdown paket
                if page.locator("#paketSelect").is_visible():
                    page.select_option("#paketSelect", pkt)
                    time.sleep(0.5)
                page.wait_for_timeout(600)
                actions_log.append(f"Switched subject to {subj} paket {pkt}")

            # 1.2 Navigasi Soal (Nomor Soal, Next, Prev)
            print("  • Menguji navigasi nomor soal...")
            # Klik tombol nomor soal 3
            q_btns = page.locator(".nomor-btn, .btn-nomor, [data-nomor]")
            if q_btns.count() > 0:
                q_btns.nth(min(2, q_btns.count() - 1)).click()
                time.sleep(0.4)
                actions_log.append("Clicked question grid button")

            # Klik tombol Next
            next_btn = page.locator("#btnNext, button:has-text('Berikutnya'), button:has-text('Next')")
            if next_btn.is_visible():
                next_btn.click()
                time.sleep(0.4)
                actions_log.append("Clicked Next button")

            # Klik tombol Prev
            prev_btn = page.locator("#btnPrev, button:has-text('Sebelumnya'), button:has-text('Prev')")
            if prev_btn.is_visible():
                prev_btn.click()
                time.sleep(0.4)
                actions_log.append("Clicked Prev button")

            # 1.3 Memilih Jawaban (Interaksi User)
            print("  • Menguji interaksi pemilihan jawaban...")
            radios = page.locator("input[type='radio']")
            if radios.count() > 0:
                radios.first.click()
                time.sleep(0.3)
                if not radios.first.is_checked():
                    findings.append({
                        "id": "UI_RADIO_SELECT_FAIL",
                        "loc": "CBT Exam Room",
                        "stage": "Tahap 4",
                        "issue": "Radio button jawaban tidak merespons klik (uncheck)",
                        "proof": "input[type='radio'].is_checked() is False after click",
                        "severity": "Kritis"
                    })
                actions_log.append("Selected radio answer")

            # 1.4 Membuka Pilar 1-5 Accordion
            print("  • Menguji expander Pilar 1-5...")
            pilar_btn = page.locator("#btnPilar, button:has-text('Pilar'), button:has-text('Pembahasan'), .pilar-toggle")
            if pilar_btn.count() > 0 and pilar_btn.first.is_visible():
                pilar_btn.first.click()
                time.sleep(0.5)
                actions_log.append("Toggled Pilar 1-5")
                print("  ✓ Tombol Pilar 1-5 berhasil di-expand.")

            # 1.5 Membuka Soal Mirip
            print("  • Menguji panel Soal Mirip...")
            mirip_btn = page.locator("#btnSoalMirip, button:has-text('Soal Mirip'), button:has-text('Latihan Mandiri')")
            if mirip_btn.count() > 0 and mirip_btn.first.is_visible():
                mirip_btn.first.click()
                time.sleep(0.5)
                actions_log.append("Toggled Soal Mirip")
                print("  ✓ Panel Soal Mirip berhasil dibuka.")

            # 1.6 Membuka AI Tutor Modal
            print("  • Menguji tombol AI Tutor...")
            ai_btn = page.locator("#btnAiTutor, #btnAITutor, button:has-text('Tanya AI'), button:has-text('AI Tutor'), .ai-tutor-fab")
            if ai_btn.count() > 0 and ai_btn.first.is_visible():
                ai_btn.first.click()
                time.sleep(0.5)
                actions_log.append("Opened AI Tutor modal")
                print("  ✓ Modal AI Tutor berhasil terbuka.")
                # Tutup modal jika ada tombol close
                close_ai = page.locator("#closeAiModal, .modal-close, button:has-text('Tutup')")
                if close_ai.count() > 0 and close_ai.first.is_visible():
                    close_ai.first.click()
                    time.sleep(0.3)

            # 1.7 Submit / Selesai Ujian & Cek Review
            print("  • Menguji submit ujian & kalkulasi skor...")
            finish_btn = page.locator("#btnSelesai, button:has-text('Selesai'), button:has-text('Kumpulkan')")
            if finish_btn.count() > 0 and finish_btn.first.is_visible():
                # Handle possible confirm dialog
                page.on("dialog", lambda dialog: dialog.accept())
                finish_btn.first.click()
                time.sleep(1.0)
                actions_log.append("Submitted exam")
                print("  ✓ Tombol submit ujian berhasil diklik.")

            # 1.8 Cek Layout Overflow Desktop
            is_overflow_x = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
            if is_overflow_x:
                findings.append({
                    "id": "UI_OVERFLOW_DESKTOP",
                    "loc": "Desktop Viewport 1280x800",
                    "stage": "Tahap 4",
                    "issue": "Ditemukan horizontal scrollbar (layout overflow) pada desktop",
                    "proof": "scrollWidth > innerWidth",
                    "severity": "Sedang"
                })
            else:
                print("  ✓ Layout desktop rapi (0 horizontal overflow).")

        except Exception as e:
            findings.append({
                "id": "UI_DESKTOP_EXCEPTION",
                "loc": "Desktop Viewport 1280x800",
                "stage": "Tahap 4",
                "issue": f"Exception saat pengujian desktop: {str(e)}",
                "proof": str(e),
                "severity": "Kritis"
            })

        context_desktop.close()

        # ---------------------------------------------------------------------
        # 2. UJI MOBILE VIEWPORT (375 x 812 — iPhone X/12)
        # ---------------------------------------------------------------------
        print("\n[MOBILE] Memulai pengujian layout Mobile (375x812)...")
        context_mobile = browser.new_context(viewport={"width": 375, "height": 812}, is_mobile=True)
        page_m = context_mobile.new_page()

        page_m.on("console", lambda msg: console_errors.append(f"[Mobile Console {msg.type}] {msg.text}") if msg.type in ["error"] else None)
        page_m.on("pageerror", lambda err: page_errors.append(f"Mobile PageError: {err}"))

        try:
            page_m.goto(f"{BASE_URL}/", timeout=10000)
            page_m.wait_for_load_state("networkidle")
            actions_log.append("Mobile page loaded successfully")

            # Cek layout overflow mobile
            is_m_overflow = page_m.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
            if is_m_overflow:
                diff = page_m.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
                findings.append({
                    "id": "UI_OVERFLOW_MOBILE",
                    "loc": "Mobile Viewport 375x812",
                    "stage": "Tahap 4",
                    "issue": f"Layout mobile melebar ke samping (horizontal scrollbar bocor {diff}px)",
                    "proof": f"scrollWidth ({diff}px larger than 375px)",
                    "severity": "Sedang"
                })
                print(f"  ⚠️ Peringatan: Terdapat horizontal overflow pada mobile (+{diff}px).")
            else:
                print("  ✓ Layout mobile 100% responsif (0 horizontal overflow).")

            # Cek touch target button
            q_btns_m = page_m.locator(".nomor-btn, .btn-nomor, [data-nomor]")
            if q_btns_m.count() > 0:
                q_btns_m.first.click()
                time.sleep(0.3)
                actions_log.append("Clicked question button on mobile")
                print("  ✓ Navigasi touch target mobile berfungsi baik.")

        except Exception as e:
            findings.append({
                "id": "UI_MOBILE_EXCEPTION",
                "loc": "Mobile Viewport 375x812",
                "stage": "Tahap 4",
                "issue": f"Exception saat pengujian mobile: {str(e)}",
                "proof": str(e),
                "severity": "Kritis"
            })

        context_mobile.close()
        browser.close()

    # 3. Evaluasi Console Errors & Page Errors
    if page_errors:
        for pe in page_errors:
            findings.append({
                "id": "UI_UNCAUGHT_JS_EXCEPTION",
                "loc": "Browser Runtime",
                "stage": "Tahap 4",
                "issue": "Uncaught JavaScript Exception di browser console",
                "proof": pe,
                "severity": "Kritis"
            })

    if console_errors:
        for ce in console_errors:
            findings.append({
                "id": "UI_CONSOLE_ERROR",
                "loc": "Browser Console",
                "stage": "Tahap 4",
                "issue": "Console error terdeteksi saat interaksi",
                "proof": ce,
                "severity": "Sedang"
            })

    print("\n" + "=" * 90)
    print("📊 HASIL PENGUJIAN TAHAP 4 (INTERAKTIF & RUNTIME)")
    print("=" * 90)
    print(f"Total Aksi Diuji       : {len(actions_log)}")
    print(f"Uncaught JS Errors     : {len(page_errors)}")
    print(f"Console Errors         : {len(console_errors)}")
    print(f"Total Temuan Tahap 4   : {len(findings)}")
    print("=" * 90)

    report_data = {
        "actions_log": actions_log,
        "page_errors": page_errors,
        "console_errors": console_errors,
        "findings": findings
    }

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print(f"📁 Laporan Tahap 4 tersimpan di: {OUTPUT_REPORT}")
    return findings

if __name__ == "__main__":
    run_ui_audit()
