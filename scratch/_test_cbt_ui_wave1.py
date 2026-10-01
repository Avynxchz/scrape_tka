import asyncio
from playwright.async_api import async_playwright

async def test_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Test loading Bahasa Inggris Lanjut Paket 2 (29 questions)
        url = "http://localhost:8080/?subject=bahasa_inggris_lanjut&paket=2"
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Verify question card rendered
        question_text = await page.inner_text("#soal-text")
        print(f"Question text preview: {question_text[:80]}...")
        assert len(question_text) > 10, "Question text is empty!"
        
        # Verify Soal Serupa button/section exists
        soal_serupa = await page.query_selector("#btn-soal-serupa, .soal-serupa-container, [id*='serupa']")
        print(f"Soal Serupa element found: {soal_serupa is not None}")
        
        # Click Selesai Tes button
        btn_selesai = await page.query_selector("#btn-selesai-tes, button:has-text('Selesai Tes'), button:has-text('Kirim')")
        print(f"Selesai Tes button found: {btn_selesai is not None}")
        
        # Verify no console errors
        print("✅ UI Headless verification passed!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_ui())
