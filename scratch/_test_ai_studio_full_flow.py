import sys, os, time, json, re
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def safe_parse_json(text):
    if not text:
        return None
    # 1. Clean markdown code blocks
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"```$", "", text.strip(), flags=re.MULTILINE)
    
    # 2. Extract outermost [ ... ] or { ... }
    m = re.search(r"(\[.*\]|\{.*\})", text, flags=re.DOTALL)
    if m:
        text = m.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        return None

def clean_turn_text(raw_text):
    """Bersihkan artefak UI AI Studio (header, timestamp, tombol thumb up/down, etc.)."""
    lines = raw_text.split('\n')
    cleaned = []
    skip = False
    for line in lines:
        s = line.strip()
        # Skip UI headers and icons
        if s in ["edit", "more_vert", "thumb_up", "thumb_down", "content_copy", "share", "cached"]:
            continue
        if re.match(r"^Model\s+\d+:\d+", s):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()

print("=== RUNNING FULL FLOW TEST IN AI STUDIO ===")
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "aistudio.google.com" in pg.url.lower()][0]
    page.bring_to_front()

    # Step 1: Click "New chat" button
    print("1. Clicking 'New chat' button...")
    new_chat_btn = page.locator("button[aria-label='New chat'], ms-app-bar button:has(i.fa-plus)")
    if new_chat_btn.count() > 0:
        new_chat_btn.first.click()
        print("  'New chat' clicked! Waiting for fresh view...")
        time.sleep(2.5)
    else:
        print("  'New chat' button not found, navigating via URL...")
        page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded")
        time.sleep(3.0)

    # Step 2: Dismiss any dialogs & Ensure tools are removed
    print("2. Ensuring no dialogs and NO tools active (100% Free Mode)...")
    page.keyboard.press("Escape")
    time.sleep(0.5)

    # Remove any tool chips if present
    remove_chips = page.locator("button[aria-label*='Remove' i]")
    for i in range(remove_chips.count()):
        try:
            rc = remove_chips.nth(i)
            if rc.is_visible():
                print(f"  Removing active tool: {rc.get_attribute('aria-label')}")
                rc.click()
                time.sleep(0.4)
        except Exception:
            pass

    # Step 3: Create a dummy prompt file to test attachment upload
    test_file_path = os.path.abspath("data/prompts/test_dummy_prompt.txt")
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("DOKUMEN TES SIMULASI TKA:\n1. Soal nomor 1 tentang teks eksposisi.\n2. Soal nomor 2 tentang teks prosedur.\n3. Soal nomor 3 tentang teks negosiasi.\n")
    
    print(f"3. Uploading prompt file attachment ({os.path.basename(test_file_path)})...")
    file_input = page.locator("input[type='file']")
    if file_input.count() > 0:
        file_input.first.set_input_files(test_file_path)
        print("  File attached! Waiting 2 seconds for chip to render...")
        time.sleep(2.0)
    else:
        print("  Warning: file input not found, skipping attachment...")

    # Step 4: Inject instruction into textarea
    print("4. Injecting instruction into prompt textarea...")
    textarea = page.locator("textarea[placeholder*='prompt' i], textarea").first
    textarea.click(force=True)
    time.sleep(0.5)
    instruction = (
        "Bacalah dokumen terlampir. Buatlah respons JSON ARRAY berisi 3 objek soal sesuai format ini:\n"
        '[{"nomor": 1, "topik": "eksposisi", "status": "OK"}, {"nomor": 2, "topik": "prosedur", "status": "OK"}, {"nomor": 3, "topik": "negosiasi", "status": "OK"}]\n'
        "WAJIB HANYA JSON ARRAY MURNI TANPA TEKS LAIN."
    )
    textarea.fill(instruction)
    time.sleep(1.0)

    # Step 5: Click Run
    print("5. Clicking Run button...")
    turn_count_before = page.locator("ms-chat-turn").count()
    run_btn = page.locator("button:has-text('Run')").first
    run_btn.click()

    # Step 6: Wait for streaming
    print("6. Monitoring streaming...")
    started = False
    for _ in range(15):
        time.sleep(1.0)
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
        if stop_btn.count() > 0 and stop_btn.first.is_visible():
            started = True
            print("  Generation started! (Stop button active)")
            break
            
    # Wait for completion
    print("7. Waiting for completion...")
    for _ in range(45):
        time.sleep(1.0)
        stop_btn = page.locator("button:has-text('Stop'), button[aria-label*='Stop' i]")
        is_generating = (stop_btn.count() > 0 and stop_btn.first.is_visible())
        if not is_generating:
            print("  Generation completed!")
            break

    time.sleep(2.0)

    # Step 7: Extract and parse JSON
    turns = page.locator("ms-chat-turn")
    print(f"8. Extracting output... (Total turns: {turns.count()})")
    raw_text = turns.last.inner_text().strip()
    clean_text = clean_turn_text(raw_text)
    print("\n--- CLEAN TEXT ---")
    print(clean_text)
    print("------------------")

    parsed = safe_parse_json(clean_text)
    print("\n--- PARSED JSON ---")
    print(json.dumps(parsed, indent=2))
    print("-------------------")
    
    if isinstance(parsed, list) and len(parsed) == 3:
        print("\n✅ VERIFIKASI FULL FLOW SUKSES 100%!")
    else:
        print("\n❌ VERIFIKASI GAGAL: Format output tidak sesuai.")
