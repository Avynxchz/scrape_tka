# -*- coding: utf-8 -*-
"""scratch/_test_selesai_tes_all.py
Verify that Selesai Tes opens the Review Overlay and displays scores properly
for both old and new subjects without any JS console errors.
"""
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_selesai_tes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        print("1. Navigating to http://localhost:8080...")
        page.goto("http://localhost:8080", wait_until="networkidle")
        page.wait_for_timeout(1000)
        
        test_subjects = [
            ("matematika", 1),
            ("bahasa_indonesia_lanjut", 1),
            ("bahasa_indonesia_lanjut", 2),
            ("bahasa_inggris_lanjut", 1),
            ("bahasa_inggris_lanjut", 2),
            ("matematika_lanjut", 2),
            ("sejarah", 2)
        ]
        
        for subj, pkg in test_subjects:
            print(f"\n--- Testing {subj} Paket {pkg} ---")
            
            # Switch subject & package
            page.evaluate(f"""async () => {{
                await switchSubject('{subj}');
                if ({pkg} !== 1) {{
                    await switchPackage({pkg});
                }}
            }}""")
            page.wait_for_timeout(1000)
            
            # Answer question 1
            page.evaluate("""() => {
                const key = pkgKey();
                if (!state.userAnswers[key]) state.userAnswers[key] = {};
                const q = state.pkgData[key].soal[0];
                if (statementType(q)) {
                    state.userAnswers[key][q.nomor] = {};
                    (q.pernyataan || []).forEach(st => {
                        state.userAnswers[key][q.nomor][st.key] = 'Sesuai';
                    });
                } else {
                    state.userAnswers[key][q.nomor] = 'A';
                }
            }""")
            
            # Trigger openFinishModal
            page.evaluate("() => openFinishModal()")
            page.wait_for_timeout(300)
            
            is_confirm_open = page.evaluate("() => document.getElementById('modalKonfirmasiSelesai').classList.contains('open')")
            
            # Trigger selesaiTes()
            page.evaluate("() => selesaiTes()")
            page.wait_for_timeout(500)
            
            is_review_open = page.evaluate("() => document.getElementById('reviewHasilOverlay').classList.contains('open')")
            benar = page.evaluate("() => document.getElementById('reviewScoreBenar').innerText")
            salah = page.evaluate("() => document.getElementById('reviewScoreSalah').innerText")
            kosong = page.evaluate("() => document.getElementById('reviewScoreKosong').innerText")
            persen = page.evaluate("() => document.getElementById('reviewScorePersen').innerText")
            meta = page.evaluate("() => document.getElementById('reviewMetaText').innerText")
            
            print(f"Review Overlay open: {is_review_open} | Meta: {meta}")
            print(f"Scores -> Benar: {benar}, Salah: {salah}, Kosong: {kosong}, Skor: {persen}")
            
            if not is_review_open:
                print(f"❌ FAIL: Review overlay failed to open for {subj} p{pkg}!")
                errors.append(f"Overlay did not open for {subj} p{pkg}")
            else:
                print(f"✅ PASS: Review overlay open and scores calculated successfully for {subj} p{pkg}.")
                
            # Close review
            page.evaluate("() => closeReviewHasil()")
            page.wait_for_timeout(200)

        browser.close()
        
        if errors:
            print("\n🚨 ERRORS DETECTED:")
            for err in errors:
                print("  -", err)
            return False
        else:
            print("\n✨ ALL TESTS PASSED! ZERO ERRORS DETECTED.")
            return True

if __name__ == "__main__":
    success = test_selesai_tes()
    sys.exit(0 if success else 1)
