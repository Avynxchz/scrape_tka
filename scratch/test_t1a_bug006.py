from playwright.sync_api import sync_playwright

def test_t1a():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844})
        
        # 1. Buka Matematika Paket 1
        print("1. Membuka Matematika Paket 1...")
        page.goto("http://127.0.0.1:8080/app?subject=matematika&paket=1", wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        
        # Pilih opsi A di Matematika no 1
        print("2. Memilih opsi B di Matematika no 1 dan Cek Jawaban...")
        page.evaluate("() => selectOption('B')")
        page.wait_for_timeout(300)
        page.click("#btnCheckAnswer")
        page.wait_for_timeout(500)
        
        # Pastikan di Matematika no 1 opsi terkunci
        page.evaluate("() => selectOption('A')")
        ans_mtk = page.evaluate("() => (state.userAnswers[pkgKey()] || {})[1]")
        assert ans_mtk == 'B', f"Opsi Matematika berubah jadi {ans_mtk}, harusnya tetap B (terkunci)!"
        print("✅ Matematika no 1: Opsi terkunci di B.")
        
        # 2. Pindah ke Fisika Paket 1
        print("3. Berpindah ke Fisika Paket 1...")
        page.evaluate("async () => { await switchSubject('fisika'); }")
        page.wait_for_timeout(1500)
        
        # Coba pilih opsi D di Fisika no 1
        print("4. Mencoba memilih opsi D di Fisika no 1...")
        page.evaluate("() => selectOption('D')")
        ans_fisika = page.evaluate("() => (state.userAnswers[pkgKey()] || {})[1]")
        assert ans_fisika == 'D', f"Opsi Fisika no 1 TIDAK BISA DIKLIK! (Nilai: {ans_fisika})"
        print("✅ Fisika no 1: Opsi BERHASIL diklik dan terpilih D (TIDAK terpengaruh Matematika)!")
        
        # 3. Kembali ke Matematika Paket 1
        print("5. Kembali ke Matematika Paket 1...")
        page.evaluate("async () => { await switchSubject('matematika'); }")
        page.wait_for_timeout(1500)
        
        # Coba klik opsi C di Matematika no 1
        page.evaluate("() => selectOption('C')")
        ans_mtk_back = page.evaluate("() => (state.userAnswers[pkgKey()] || {})[1]")
        assert ans_mtk_back == 'B', f"Opsi Matematika no 1 berubah jadi {ans_mtk_back}, harusnya tetap B (terkunci)!"
        print("✅ Kembali ke Matematika no 1: Opsi TETAP TERKUNCI di B!")
        
        page.screenshot(path="scratch/bukti_t1a_bug006.png")
        print("Screenshot bukti disimpan di scratch/bukti_t1a_bug006.png")
        browser.close()
        print("🎉 UJI T1a (BUG-006) 100% SUKSES DAN TERVERIFIKASI!")

if __name__ == "__main__":
    test_t1a()
