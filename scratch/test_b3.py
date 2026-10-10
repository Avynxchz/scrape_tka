"""
Test verifikasi B3: Soal 1 tidak terkunci di opsi A.
Menguji:
1. Klik setiap opsi (A, B, C, D, E) di Soal 1.
2. Pemilihan opsi via keyboard (A, B, C, D, E).
3. Pindah soal (Soal 1 -> Soal 2) dan kembali lagi (Soal 2 -> Soal 1).
4. Penggantian opsi setelah kembali ke Soal 1.
5. Simpan screenshot after + log assertion di evidence/B3/soal1_opsi-after.png
"""

import sys
sys.path.insert(0, 'scratch')
from test_harness import TKATestHarness, LOCAL_URL

def test_b3():
    print("Running B3 verification test...")
    with TKATestHarness(LOCAL_URL) as harness:
        p = harness.page
        # Buka kuis matematika paket 1 langsung
        p.goto(f"{LOCAL_URL}/app?subject=matematika&paket=1")
        p.wait_for_timeout(1000)

        curr_q = p.evaluate("getCurrentQuestion().nomor")
        assert curr_q == 1, f"Expected Soal 1, got {curr_q}"
        print("PASS: Berada di Soal 1.")

        # 1. Klik tiap opsi di Soal 1 (klik pada indicator atau option item)
        for opt_key in ['A', 'B', 'C', 'D', 'E']:
            opt_locator = p.locator(f'.option-item[data-key="{opt_key}"] .opt-indicator')
            opt_locator.click()
            p.wait_for_timeout(200)
            selected_in_state = p.evaluate(f"state.userAnswers[pkgKey()]['1']")
            assert selected_in_state == opt_key, f"Opsi {opt_key} gagal dipilih via klik! State: {selected_in_state}"
            opt_parent = p.locator(f'.option-item[data-key="{opt_key}"]')
            assert 'selected' in (opt_parent.get_attribute('class') or ''), f"Class 'selected' tidak ada pada opsi {opt_key}!"
            print(f"PASS: Opsi {opt_key} berhasil dipilih via klik (state: {selected_in_state}).")

        # 2. Pemilihan via keyboard di Soal 1
        for key in ['a', 'b', 'c', 'd', 'e']:
            p.keyboard.press(key)
            p.wait_for_timeout(200)
            opt_key = key.upper()
            selected_in_state = p.evaluate(f"state.userAnswers[pkgKey()]['1']")
            assert selected_in_state == opt_key, f"Opsi {opt_key} gagal dipilih via keyboard key '{key}'! State: {selected_in_state}"
            opt_parent = p.locator(f'.option-item[data-key="{opt_key}"]')
            assert 'selected' in (opt_parent.get_attribute('class') or ''), f"Class 'selected' tidak ada pada opsi {opt_key} via keyboard!"
            print(f"PASS: Opsi {opt_key} berhasil dipilih via keyboard key '{key}'.")

        # Set opsi Soal 1 ke 'B'
        p.keyboard.press('b')
        p.wait_for_timeout(200)

        # 3. Pindah soal (Soal 1 -> Soal 2) via keyboard ArrowRight
        p.keyboard.press('ArrowRight')
        p.wait_for_timeout(500)
        curr_q = p.evaluate("getCurrentQuestion().nomor")
        assert curr_q == 2, f"Gagal pindah ke soal 2, current_q: {curr_q}"
        print("PASS: Berhasil pindah ke Soal 2.")

        # Pilih opsi C di Soal 2
        p.keyboard.press('c')
        p.wait_for_timeout(200)
        opt_s2 = p.locator('.option-item[data-key="C"]')
        assert 'selected' in (opt_s2.get_attribute('class') or ''), "Opsi C di soal 2 gagal dipilih"
        print("PASS: Opsi C di Soal 2 berhasil dipilih.")

        # 4. Kembali ke Soal 1 via ArrowLeft
        p.keyboard.press('ArrowLeft')
        p.wait_for_timeout(500)
        curr_q = p.evaluate("getCurrentQuestion().nomor")
        assert curr_q == 1, f"Gagal kembali ke soal 1, current_q: {curr_q}"
        print("PASS: Berhasil kembali ke Soal 1.")

        # Verifikasi bahwa di Soal 1 opsi 'B' masih terpilih
        opt_b_s1 = p.locator('.option-item[data-key="B"]')
        assert 'selected' in (opt_b_s1.get_attribute('class') or ''), "Pilihan B di soal 1 hilang setelah bolak-balik!"
        print("PASS: Pilihan B di Soal 1 tetap bertahan setelah navigasi bolak-balik.")

        # Ganti ke opsi D di Soal 1 via klik
        p.locator('.option-item[data-key="D"] .opt-indicator').click()
        p.wait_for_timeout(200)
        opt_d_s1 = p.locator('.option-item[data-key="D"]')
        assert 'selected' in (opt_d_s1.get_attribute('class') or ''), "Gagal mengubah opsi ke D di soal 1!"
        selected_final = p.evaluate("state.userAnswers[pkgKey()]['1']")
        assert selected_final == 'D', f"Expected D, got {selected_final}"
        print("PASS: Berhasil mengubah opsi dari B ke D di Soal 1.")

        # 5. Simpan evidence AFTER
        harness.save_evidence(
            "evidence/B3/soal1_opsi-after",
            "B3 AFTER: Opsi Soal 1 dapat diganti bebas via klik dan keyboard, serta bertahan saat bolak-balik",
            {
                "status": "PASS",
                "soal_1_final_selected": "D",
                "keyboard_navigation_verified": True,
                "switching_questions_verified": True,
                "all_options_tested": ["A", "B", "C", "D", "E"]
            }
        )

    print("\nALL B3 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_b3()
