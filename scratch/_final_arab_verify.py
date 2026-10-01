import asyncio
import os
from playwright.async_api import async_playwright

OUT_DIR = r"d:\PROJECTS\SCRAPE_TKA\scratch\arab_verification_final"
os.makedirs(OUT_DIR, exist_ok=True)

targets = [
    # Paket 1
    (1, 2, "p1_q02"),
    (1, 3, "p1_q03"),
    (1, 4, "p1_q04"),
    (1, 5, "p1_q05"),
    (1, 6, "p1_q06"),
    (1, 7, "p1_q07"),
    (1, 8, "p1_q08"),
    (1, 9, "p1_q09"),
    (1, 10, "p1_q10"),
    # Paket 2
    (2, 1, "p2_q01"),
    (2, 2, "p2_q02"),
    (2, 3, "p2_q03"),
    (2, 4, "p2_q04"),
    (2, 5, "p2_q05"),
    (2, 6, "p2_q06"),
    (2, 7, "p2_q07"),
    (2, 8, "p2_q08"),
    (2, 9, "p2_q09"),
    (2, 10, "p2_q10"),
    (2, 11, "p2_q11"),
    (2, 27, "p2_q27"),
    (2, 28, "p2_q28"),
    (2, 29, "p2_q29"),
]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 850})
        await page.goto("http://localhost:8080/?subject=bahasa_arab&paket=1", wait_until="networkidle")
        
        for pkg, no, name in targets:
            await page.evaluate(f"""async () => {{
                if (state.currentSubject !== 'bahasa_arab') await switchSubject('bahasa_arab');
                if (state.currentPkg !== {pkg}) await switchPackage({pkg});
                const idx = state.pkgData[pkgKey()]?.soal?.findIndex(s => s.nomor === {no});
                if (idx !== undefined && idx >= 0) {{
                    state.currentIndex = idx;
                    renderQuestion();
                }}
            }}""")
            await page.wait_for_timeout(700)
            card = page.locator(".cbt-question-card")
            out_path = os.path.join(OUT_DIR, f"{name}.png")
            if await card.count() > 0:
                await card.screenshot(path=out_path)
            else:
                await page.screenshot(path=out_path)
            print(f"Saved: {out_path}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
