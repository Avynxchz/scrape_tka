import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]

    # 1. Check all ms-chat-turn elements and their roles
    turns = page.locator("ms-chat-turn")
    print(f"Total ms-chat-turn: {turns.count()}")
    for i in range(turns.count()):
        t = turns.nth(i)
        role = t.get_attribute("data-turn-role") or "unknown"
        txt = t.inner_text()
        print(f"Turn {i}: role={role}, len={len(txt)}, head={txt[:100].replace(chr(10), ' ').strip()}")

    # 2. Check markdown-viewer elements
    print("\n--- markdown-viewer ---")
    mvs = page.locator("markdown-viewer")
    print(f"Total markdown-viewer: {mvs.count()}")
    for i in range(mvs.count()):
        mv = mvs.nth(i)
        txt = mv.inner_text()
        print(f"MV {i}: len={len(txt)}, head={txt[:100].replace(chr(10), ' ').strip()}")

    # 3. Check code blocks
    print("\n--- pre / code blocks ---")
    pres = page.locator("pre")
    print(f"Total pre: {pres.count()}")
    for i in range(pres.count()):
        txt = pres.nth(i).inner_text()
        has_json = "{" in txt and "question_number" in txt
        print(f"Pre {i}: len={len(txt)}, has_json={has_json}, head={txt[:80].replace(chr(10), ' ').strip()}")

    # 4. Evaluate to find largest text block containing JSON
    print("\n--- JS evaluate for largest JSON block ---")
    result = page.evaluate("""() => {
        const candidates = [
            ...document.querySelectorAll('pre code'),
            ...document.querySelectorAll('pre'),
            ...document.querySelectorAll('markdown-viewer'),
            ...document.querySelectorAll('ms-chat-turn'),
        ];
        let best = {tag: '', len: 0, head: '', hasJson: false};
        for (const el of candidates) {
            const txt = el.innerText || '';
            const isJson = txt.includes('question_number') && txt.includes('{');
            if (txt.length > best.len || (isJson && !best.hasJson)) {
                best = {tag: el.tagName, len: txt.length, head: txt.substring(0, 150), hasJson: isJson};
            }
        }
        return best;
    }""")
    print(f"Best block: tag={result['tag']}, len={result['len']}, hasJson={result['hasJson']}")
    print(f"Head: {result['head'][:150]}")
