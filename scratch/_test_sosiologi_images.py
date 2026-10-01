import asyncio
import os
from playwright.async_api import async_playwright

OUT_DIR = r"d:\PROJECTS\SCRAPE_TKA\scratch\sosiologi_verification"
os.makedirs(OUT_DIR, exist_ok=True)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("http://localhost:8080/?subject=sosiologi&paket=1", wait_until="networkidle")
        
        for no in [13, 14, 15]:
            await page.evaluate(f"""async () => {{
                if (state.currentSubject !== 'sosiologi') {{
                    await switchSubject('sosiologi');
                }}
                if (state.currentPkg !== 1) {{
                    await switchPackage(1);
                }}
                const idx = state.pkgData[pkgKey()]?.soal?.findIndex(s => s.nomor === {no});
                if (idx !== undefined && idx >= 0) {{
                    state.currentIndex = idx;
                    renderQuestion();
                }}
            }}""")
            
            await asyncio.sleep(0.5)
            
            # Check img details in stimulus
            info = await page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('#stimulusContainer img'));
                return imgs.map(im => ({
                    className: im.className,
                    src: im.src,
                    naturalWidth: im.naturalWidth,
                    naturalHeight: im.naturalHeight,
                    offsetWidth: im.offsetWidth,
                    offsetHeight: im.offsetHeight,
                    computedMaxHeight: window.getComputedStyle(im).maxHeight,
                    computedHeight: window.getComputedStyle(im).height,
                    computedDisplay: window.getComputedStyle(im).display
                }));
            }""")
            
            print(f"=== Q{no} IMGS ===")
            for item in info:
                print(" ", item)
                
            card = page.locator(".cbt-question-card")
            out_path = os.path.join(OUT_DIR, f"sosiologi_p1_q{no}.png")
            if await card.count() > 0:
                await card.screenshot(path=out_path)
            else:
                await page.screenshot(path=out_path)
            print(f"Saved: {out_path}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
