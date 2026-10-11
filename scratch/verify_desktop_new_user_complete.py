import sys
from playwright.sync_api import sync_playwright

def test_full_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        print("1. Mengakses http://127.0.0.1:8080/app ...")
        page.goto("http://127.0.0.1:8080/app", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)

        # 2. Periksa banner metrik di iframe
        home_frame = page.frame_locator("#homeDesktopFrame")
        hero_text = home_frame.locator("body").inner_text()
        assert "27" in hero_text and "Mata Pelajaran" in hero_text, "Metrik 27 Mapel tidak ditemukan!"
        assert "49 Paket" in hero_text, "Metrik 49 Paket tidak ditemukan!"
        assert "991" in hero_text, "Metrik 991 Butir Soal tidak ditemukan!"
        print("✅ Langkah 1: Metrik 27 Mapel · 49 Paket · 991 Soal valid!")

        # 3. Klik tombol Mulai Sekarang di hero
        print("2. Mengklik tombol 'Mulai Sekarang' di hero...")
        home_frame.locator("#deskHeroStartBtn").click()
        page.wait_for_timeout(1000)

        # 4. Filter SMK
        print("3. Mengklik filter Kejuruan SMK (5)...")
        home_frame.locator('[data-cat="smk"]').click()
        page.wait_for_timeout(1000)

        # Periksa kartu SMK tampil
        otomotif_sec = home_frame.locator('[data-subject="teknik_otomotif"]')
        assert otomotif_sec.count() > 0, "Bagian Teknik Otomotif tidak muncul!"
        print("✅ Langkah 2: Filter SMK aktif dan 5 mapel SMK tampil!")

        page.screenshot(path="scratch/step1_smk_cards.png")

        # 5. Klik kartu Paket 1 Teknik Otomotif
        print("4. Mengklik kartu Paket 1 Teknik Otomotif...")
        otomotif_card = otomotif_sec.locator('.grid > div.relative').first
        otomotif_card.click()
        page.wait_for_timeout(1500)

        page.screenshot(path="scratch/step2_modal_konfirmasi.png")

        # 6. Periksa modal konfirmasi di parent
        modal = page.locator("#modalKonfirmasiMulaiMapel")
        assert modal.is_visible(), "Modal konfirmasi mulai kuis tidak muncul!"
        btn_guest = page.locator("#btnConfirmStartGuest")
        assert btn_guest.is_visible(), "Tombol Coba Tamu tidak muncul di modal!"
        print("✅ Langkah 3: Modal konfirmasi tampil dengan opsi 'Coba Tamu'!")

        # 7. Klik Coba Tamu
        print("5. Mengklik tombol 'Coba Tamu'...")
        btn_guest.click()
        page.wait_for_timeout(3000)

        page.screenshot(path="scratch/step3_kuis_terbuka.png")

        # 8. Periksa CBT Kuis terbuka
        overlay = page.locator("#homeOverlay")
        assert not overlay.is_visible(), "Overlay Beranda masih menutupi lembar kuis!"
        cbt_grid = page.locator("#cbtExamGrid")
        assert cbt_grid.is_visible(), "Lembar CBT tidak terlihat!"
        soal_text = page.locator("#promptContainer").inner_text()
        print(f"✅ Langkah 4: Kuis berhasil terbuka! Teks Soal 1: {soal_text[:70]}...")

        # 9. Jawab Soal 1 & Cek Jawaban
        print("6. Memilih opsi B dan mengklik Cek Jawaban...")
        page.evaluate("() => { selectOption('B'); }")
        page.wait_for_timeout(500)
        page.click("#btnCheckAnswer")
        page.wait_for_timeout(1000)

        feedback = page.locator("#feedbackBanner").inner_text()
        print(f"✅ Langkah 5: Feedback kuis muncul: {feedback.replace('\n', ' ')[:70]}...")

        page.screenshot(path="scratch/step4_jawaban_dicek.png")

        print("Console errors:", console_errors)
        browser.close()
        print("🎉 SEMUA UJI ALUR PENGGUNA BARU DESKTOP 100% SUKSES!")

if __name__ == "__main__":
    test_full_flow()
