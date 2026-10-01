import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from pipeline.playwright_aistudio_bridge import extract_latest_response, safe_parse_json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url and "prompts" in pg.url][0]

    print("Testing extract_latest_response (NEW logic)...")
    txt = extract_latest_response(page)
    print(f"Extracted length: {len(txt)}")
    print(f"Contains 'question_number': {'question_number' in txt}")
    print(f"First 200 chars: {txt[:200]}")
    print(f"Last 100 chars: {txt[-100:]}")

    print("\nTesting safe_parse_json...")
    parsed = safe_parse_json(txt)
    if parsed and isinstance(parsed, list):
        print(f"Parsed {len(parsed)} solutions!")
        for sol in parsed[:3]:
            print(f"  Q{sol.get('question_number')}: {sol.get('question_title', '?')[:60]}")
        for sol in parsed[-3:]:
            print(f"  Q{sol.get('question_number')}: {sol.get('question_title', '?')[:60]}")
        all_nos = sorted([s.get("question_number") for s in parsed if s.get("question_number")])
        print(f"Question numbers: {all_nos}")
        missing = sorted(set(range(1, 26)) - set(all_nos))
        print(f"Missing: {missing}")
    else:
        print(f"Parse FAILED! parsed type: {type(parsed)}")
