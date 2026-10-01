import asyncio
import os
from playwright.async_api import async_playwright

OUT_DIR = r"d:\PROJECTS\SCRAPE_TKA\scratch\custom_size_verification"
os.makedirs(OUT_DIR, exist_ok=True)

test_targets = [
    ("matematika", 1, 9, "mat_p1_q9"),
    ("matematika", 1, 11, "mat_p1_q11"),
    ("matematika", 1, 19, "mat_p1_q19"),
    ("matematika", 2, 8, "mat_p2_q8"),
    ("matematika_lanjut", 1, 16, "mtl_p1_q16"),
    ("matematika_lanjut", 1, 18, "mtl_p1_q18"),
    ("matematika_lanjut", 1, 20, "mtl_p1_q20"),
    ("matematika_lanjut", 2, 1, "mtl_p2_q1"),
    ("matematika_lanjut", 2, 4, "mtl_p2_q4"),
    ("matematika_lanjut", 2, 16, "mtl_p2_q16"),
    ("matematika_lanjut", 2, 21, "mtl_p2_q21"),
    ("matematika_lanjut", 2, 23, "mtl_p2_q23"),
    ("matematika_lanjut", 2, 25, "mtl_p2_q25"),
]

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        for subj, pkt, no, name in test_targets:
            url = f"http://localhost:8080/?subject={subj}&paket={pkt}#soal-{no}"
            await page.goto(url, wait_until="networkidle")
            
            # Select subject and package via UI if needed
            await page.evaluate(f"""async () => {{
                if (state.currentSubject !== '{subj}') {{
                    await switchSubject('{subj}');
                }}
                if (state.currentPkg !== {pkt}) {{
                    await switchPackage({pkt});
                }}
                const idx = state.pkgData[pkgKey()]?.soal?.findIndex(s => s.nomor === {no});
                if (idx !== undefined && idx >= 0) {{
                    state.currentIndex = idx;
                    renderQuestion();
                }}
            }}""")
            
            await asyncio.sleep(0.5)
            
            card = page.locator(".cbt-question-card")
            out_path = os.path.join(OUT_DIR, f"{name}.png")
            if await card.count() > 0:
                await card.screenshot(path=out_path)
            else:
                await page.screenshot(path=out_path)
            print(f"[OK] Saved screenshot: {name}.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
