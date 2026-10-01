import asyncio
import os
from playwright.async_api import async_playwright

OUT_DIR = r"d:\PROJECTS\SCRAPE_TKA\scratch\arab_p1_verified"
os.makedirs(OUT_DIR, exist_ok=True)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 850})
        await page.goto("http://localhost:8080/?subject=bahasa_arab&paket=1", wait_until="networkidle")
        
        for no in range(1, 11):
            await page.evaluate(f"""async () => {{
                if (state.currentSubject !== 'bahasa_arab') await switchSubject('bahasa_arab');
                if (state.currentPkg !== 1) await switchPackage(1);
                const idx = state.pkgData[pkgKey()]?.soal?.findIndex(s => s.nomor === {no});
                if (idx !== undefined && idx >= 0) {{
                    state.currentIndex = idx;
                    renderQuestion();
                }}
            }}""")
            # Wait for all images inside the card to load
            await page.wait_for_function("""() => {
                const cardImgs = Array.from(document.querySelectorAll('.cbt-question-card img'));
                if (cardImgs.length === 0) return true;
                return cardImgs.every(img => img.complete && img.naturalWidth > 0);
            }""", timeout=10000)
            await page.wait_for_timeout(400)
            
            card = page.locator(".cbt-question-card")
            out_path = os.path.join(OUT_DIR, f"p1_q{no:02d}.png")
            await card.screenshot(path=out_path)
            print(f"Captured: {out_path}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
