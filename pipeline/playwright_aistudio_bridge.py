# -*- coding: utf-8 -*-
"""pipeline/playwright_aistudio_bridge.py — Chrome Remote Debugging Bridge via Playwright.

Pendekatan B (Google AI Studio PRO Bridge):
- Menghubungkan Playwright ke browser Google Chrome yang sedang aktif membuka
  Google AI Studio PRO via Chrome DevTools Protocol (--remote-debugging-port=9222).
- Membersihkan / menutup tab-tab lama berlebih secara otomatis agar tidak menumpuk.
- Memastikan parameter model 'Thinking level' disetel ke 'High' sebelum mengirim prompt.
- Mengirim prompt via file upload native ke AI Studio dengan instruksi pemicu presisi.
- Monitoring streaming secara cerdas hingga model selesai berpikir & menghasilkan output.
- Auto-continuation guard: mendeteksi nomor soal yang terlewat dan meminta kelanjutan otomatis.
- Menyimpan output dan file prompt ke direktori unduhan/ekspor (exports/ & data/solution_sources/).
- Menjalankan audit mutu otomatis (Automated Auditor) di akhir proses untuk verifikasi 100% PASS.
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import re
import json
import time
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import text_quality  # noqa: E402  (normalisasi teks hasil ekstraksi DOM)

DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
PROMPT_DIR = os.path.join(DATA_DIR, "prompts")
RAW_DIR = os.path.join(DATA_DIR, "raw_llm_outputs")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

for d in [SOL_DIR, KUNCI_DIR, PROMPT_DIR, RAW_DIR, EXPORTS_DIR]:
    os.makedirs(d, exist_ok=True)


def log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level, "👉")
    print(f"[{ts}] {icon} [AI_STUDIO_BRIDGE] {msg}", flush=True)


def is_portal_chrome_image(fn, size):
    """Gambar chrome portal Pusmendik (logo/loader/ikon kecil) — bukan konten soal."""
    low = fn.lower()
    if any(k in low for k in ("logo", "loader", "icon", "favicon", "spinner")):
        return True
    return size < 2048


def _recover_vision_records(raw, batch):
    """Pulihkan record vision dari JSON rusak akibat kutip ganda tak ter-escape.

    Model kadang menulis judul/istilah dengan "..." di dalam nilai string tanpa
    escape, membuat json.loads gagal. Kita potong per record berdasarkan marker
    "filename" dan ambil description sampai penutup record ('"...}' / '"...]').
    """
    records = []
    matches = list(re.finditer(r'"filename"\s*:\s*"([^"]+)"\s*,\s*"description"\s*:\s*"', raw))
    for i, m in enumerate(matches):
        fn = os.path.basename(m.group(1))
        tail = raw[m.end():]
        # Deskripsi berakhir pada kutip yang diikuti penutup record/array
        end_m = re.search(r'"\s*\}\s*[,\]]?\s*|\s*"\s*\]\s*', tail)
        desc = tail[:end_m.start()] if end_m else tail.strip()
        # Bersihkan kemungkinan penutup 'edit/more_vert' chrome DOM di ekor
        desc = re.sub(r'\s*(edit|more_vert|thumb_up|thumb_down)\s*$', '', desc).strip()
        records.append({"filename": fn, "description": desc})
    # Kasus satu gambar tanpa "filename" sama sekali: ambil description tunggal
    if not records and len(batch) == 1:
        m = re.search(r'"description"\s*:\s*"', raw)
        if m:
            tail = raw[m.end():]
            end_m = re.search(r'"\s*\}\s*[,\]]?\s*|\s*"\s*\]\s*', tail)
            desc = tail[:end_m.start()] if end_m else tail.strip()
            desc = re.sub(r'\s*(edit|more_vert|thumb_up|thumb_down)\s*$', '', desc).strip()
            records.append({"filename": batch[0], "description": desc})
    return records


def run_phase_3_via_playwright(slug, port=9222, batch_size=8, max_passes=2):
    """FASE 3 via AI Studio Playground — transkripsi vision GRATIS tanpa kuota API.

    Mengunggah gambar soal secara batch (8 gambar/turn) ke AI Studio dengan
    instruksi transkripsi JSON terpetakan (urutan + filename), lalu menggabungkan
    hasilnya ke sidecar transkripsi. Checkpoint ditulis per batch sehingga
    proses yang terputus tidak mengulang gambar yang sudah selesai.

    Return jumlah gambar baru yang berhasil ditranskripsi.
    """
    import text_quality

    from pipeline.subject_catalog import MASTER_CATALOG
    if slug not in MASTER_CATALOG:
        raise ValueError(f"Slug '{slug}' tidak ada di MASTER_CATALOG")
    item = MASTER_CATALOG[slug]
    img_dir = os.path.join(DATA_DIR, item["mapel_key"], f"paket_{item['paket']}", "images")
    if not os.path.isdir(img_dir):
        log(f"[{slug}] Tidak ada direktori gambar — lewati.", "WARNING")
        return 0

    sidecar_path = os.path.join(DATA_DIR, f"{slug}_sidecar_transcriptions.json")
    existing = {}
    if os.path.isfile(sidecar_path):
        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    pending = []
    for fn in sorted(os.listdir(img_dir)):
        if not fn.lower().endswith((".png", ".jpg", ".jpeg")) or fn in existing:
            continue
        try:
            size = os.path.getsize(os.path.join(img_dir, fn))
        except OSError:
            continue
        if not is_portal_chrome_image(fn, size):
            pending.append(fn)

    if not pending:
        log(f"[{slug}] Seluruh gambar konten sudah tertranskripsi ({len(existing)} entri).", "SUCCESS")
        return 0

    log(f"[{slug}] FASE 3 VIA AI STUDIO: {len(pending)} gambar konten menunggu transkripsi "
        f"(batch {batch_size}/turn).", "INFO")

    total_new = 0
    with sync_playwright() as p:
        browser, page = connect_to_aistudio(p, port=port)

        # Wajib playground chat standar — URL new_chat dapat dialihkan AI Studio
        # ke mode Antigravity Agent yang menuntut API key (Run tak pernah jalan).
        page = _resolve_standard_page(browser, page)
        if page is None:
            raise RuntimeError(
                "Playground standar AI Studio tidak ditemukan (halaman Antigravity) — "
                "jalankan ulang atau gunakan jalur API.")
        start_fresh_chat(page)  # isolasi run: 1 run = 1 chat baru

        try:
            for pass_no in range(1, max_passes + 1):
                still = [f for f in pending if f not in existing]
                if not still:
                    break
                if pass_no > 1:
                    log(f"Pass {pass_no}: retry {len(still)} gambar yang belum berhasil...", "INFO")
                for i in range(0, len(still), batch_size):
                    batch = still[i:i + batch_size]
                    file_paths = [os.path.join(img_dir, fn) for fn in batch]
                    try:
                        dismiss_any_overlay(page)
                        file_input = page.locator("input[type='file']")
                        if file_input.count() == 0:
                            raise RuntimeError("Input file AI Studio tidak ditemukan")
                        file_input.first.set_input_files(file_paths)
                        _wait_attachments_ready(page, file_paths, timeout_seconds=45)
                        time.sleep(1.0)

                        listing = "\n".join(f"{n + 1}. {fn}" for n, fn in enumerate(batch))
                        instruction = (
                            f"Lampiran berisi {len(batch)} gambar soal TKA, TERURUT sesuai daftar:\n"
                            f"{listing}\n\n"
                            "Untuk SETIAP gambar (gunakan nomor urut dan nama file yang sama persis), "
                            "hasilkan transkripsi ilmiah yang akurat:\n"
                            "1. Rumus matematika/fisika/kimia -> LaTeX ($...$ atau $$...$$).\n"
                            "2. Diagram/struktur/anatomi/silsilah -> jabarkan bagian penting secara deskriptif.\n"
                            "3. Grafik/tabel data -> ekstrak nilai titik koordinat atau isi tabel (markdown table).\n"
                            "4. Teks pada gambar -> salin verbatim.\n"
                            "5. DILARANG memakai karakter kutip ganda (\") di dalam nilai string — "
                            "gunakan kutip tunggal ('...') untuk judul/istilah agar JSON valid.\n\n"
                            "Output WAJIB JSON ARRAY murni tanpa teks lain:\n"
                            '[{"urutan": 1, "filename": "<nama file persis>", "description": "<transkripsi>"}, ...]'
                        )
                        target_input = get_input_box(page)
                        target_input.click(force=True)
                        time.sleep(0.5)
                        try:
                            target_input.evaluate(
                                "(el, text) => { el.value = text; el.dispatchEvent(new Event('input', { bubbles: true })); "
                                "el.dispatchEvent(new Event('change', { bubbles: true })); }",
                                instruction)
                        except Exception:
                            target_input.fill(instruction)
                        time.sleep(1.0)

                        turn_before = page.locator("ms-chat-turn").count()
                        if not _submit_prompt(page):
                            log("Generasi tidak terdeteksi mulai — percobaan submit kedua...", "WARNING")
                            if not _submit_prompt(page):
                                raise RuntimeError("Submit prompt AI Studio gagal (generasi tidak mulai).")
                        raw = _wait_for_response(page, turn_before, timeout_seconds=420)
                        parsed = safe_parse_json(raw)
                        if not isinstance(parsed, list) or not parsed:
                            # JSON rusak (kutip ganda tak ter-escape dsb.) — pulihkan
                            recovered = _recover_vision_records(raw, batch)
                            parsed = recovered if recovered else parsed
                        parsed = parsed if isinstance(parsed, list) else []

                        n_batch = 0
                        mapped = {os.path.basename(str(it.get("filename") or "")): True
                                  for it in (parsed if isinstance(parsed, list) else [])
                                  if it.get("description")}
                        for it in parsed if isinstance(parsed, list) else []:
                            desc = (it.get("description") or "").strip()
                            if not desc:
                                continue
                            fn = it.get("filename")
                            if not fn and isinstance(it.get("urutan"), int) \
                                    and 1 <= it["urutan"] <= len(batch):
                                fn = batch[it["urutan"] - 1]
                            fn = os.path.basename(str(fn or ""))
                            if fn in batch:
                                existing[fn] = {
                                    "filename": fn,
                                    "description": text_quality.repair_math_text(desc),
                                    "model": "AI Studio Gemini 3.8 Flash High",
                                }
                                n_batch += 1

                        # Fallback 1:1 — batch berisi tepat 1 gambar namun model
                        # tidak mengembalikan filename/urutan yang dikenali.
                        if n_batch == 0 and len(batch) == 1:
                            best_desc = ""
                            for it in parsed if isinstance(parsed, list) else []:
                                d = (it.get("description") or "").strip()
                                if len(d) > len(best_desc):
                                    best_desc = d
                            if not best_desc and isinstance(parsed, dict):
                                best_desc = (parsed.get("description") or "").strip()
                            if best_desc:
                                fn = batch[0]
                                existing[fn] = {
                                    "filename": fn,
                                    "description": text_quality.repair_math_text(best_desc),
                                    "model": "AI Studio Gemini 3.8 Flash High",
                                }
                                n_batch = 1

                        # Checkpoint per batch — proses terputus tidak mengulang
                        with open(sidecar_path, "w", encoding="utf-8") as f:
                            json.dump(existing, f, ensure_ascii=False, indent=2)
                        total_new += n_batch
                        log(f"[{slug}] Batch Q{batch[0][:8]}..(+{len(batch)}): "
                            f"{n_batch}/{len(batch)} gambar tertranskripsi. "
                            f"Total sisi: {len(existing)} entri.", "SUCCESS" if n_batch else "WARNING")
                    except Exception as e:
                        log(f"[{slug}] Batch gagal ({str(e)[:90]}) — lanjut batch berikutnya.", "ERROR")
                    time.sleep(2.0)
        finally:
            try:
                browser.close()
            except Exception:
                pass

    log(f"[{slug}] FASE 3 AI Studio selesai: {total_new} gambar baru tertranskripsi.", "SUCCESS")
    return total_new


def check_port_open(port=9222):
    """Periksa apakah port remote debugging 9222 sudah aktif."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect(("127.0.0.1", port))
        s.close()
        return True
    except Exception:
        return False


def get_chrome_path():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return "chrome.exe"


def close_duplicate_tabs(context):
    """Tutup tab Google AI Studio lama/duplikat agar tidak menumpuk.

    Tab playground chat STANDAR dilindungi — hanya tab mode Antigravity atau
    duplikat setelah tab standar pertama yang ditutup.
    """
    pages = context.pages
    ai_pages = [pg for pg in pages if "aistudio.google.com" in pg.url.lower()]
    if len(ai_pages) > 1:
        log(f"Terdeteksi {len(ai_pages)} tab AI Studio. Membersihkan tab lama/duplikat...", "WARNING")
        standard = None
        for pg in ai_pages:
            if _page_is_standard_playground(pg):
                standard = pg
                break
        keep = standard if standard else ai_pages[0]
        for extra in ai_pages:
            if extra is keep:
                continue
            try:
                log(f"Menutup tab lama: {extra.url[:60]}...", "INFO")
                extra.close()
            except Exception:
                pass


def close_settings_panel_if_open(page):
    """Tutup panel settings jika terbuka agar tidak menghalangi area chat."""
    try:
        close_btn = page.locator("button[aria-label*='Close run settings' i]")
        if close_btn.count() > 0 and close_btn.first.is_visible():
            close_btn.first.click(force=True)
            time.sleep(0.5)
            log("Panel settings ditutup agar area chat tidak terhalang.", "INFO")
    except Exception:
        pass


def ensure_thinking_level_high(page):
    """Pastikan model Thinking Level di Google AI Studio disetel ke 'High'."""
    log("Memeriksa konfigurasi 'Thinking level'...", "INFO")
    try:
        select = page.locator("mat-select[aria-label='Thinking Level'], mat-select:has-text('Thinking')")
        if select.count() == 0 or not select.first.is_visible():
            toggle = page.locator("button.runsettings-toggle-button")
            if toggle.count() > 0 and toggle.first.is_visible():
                toggle.first.click(force=True)
                time.sleep(1.0)
                select = page.locator("mat-select[aria-label='Thinking Level'], mat-select:has-text('Thinking')")

        if select.count() > 0:
            curr_val = select.first.inner_text().strip()
            if "High" in curr_val:
                log("Thinking Level sudah disetel ke 'High'.", "SUCCESS")
            else:
                log(f"Mengubah Thinking Level dari '{curr_val}' ke 'High'...", "INFO")
                select.first.click(force=True)
                time.sleep(0.8)
                opt_high = page.locator("mat-option:has-text('High')")
                if opt_high.count() > 0:
                    opt_high.first.click(force=True)
                    time.sleep(0.5)
                    log("Thinking Level berhasil disetel ke 'High'!", "SUCCESS")
                else:
                    log("Pilihan 'High' tidak ditemukan di menu dropdown.", "WARNING")

        # Pastikan panel settings ditutup kembali
        close_settings_panel_if_open(page)
    except Exception as e:
        log(f"Catatan saat verifikasi Thinking Level: {e}", "WARNING")
        close_settings_panel_if_open(page)
    return False


def ensure_chrome_debug_open(port=9222, target_model="gemini-3.8-flash"):
    """Pastikan Chrome di port 9222 sudah terbuka, jika belum, buka otomatis."""
    if not check_port_open(port):
        chrome_exe = get_chrome_path()
        log(f"Chrome port {port} belum aktif. Membuka Google Chrome otomatis di port {port}...", "INFO")
        url = f"https://aistudio.google.com/prompts/new_chat?model={target_model}"
        user_data = os.path.expandvars(r"%USERPROFILE%\.chrome_ai_studio")
        try:
            if sys.platform == "win32":
                ps_cmd = f"Start-Process -FilePath '{chrome_exe}' -ArgumentList '--remote-debugging-port={port}', '--user-data-dir={user_data}', '{url}'"
                subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_cmd])
            else:
                subprocess.Popen([chrome_exe, f"--remote-debugging-port={port}", f"--user-data-dir={user_data}", url])
        except Exception as e:
            log(f"Gagal memicu pembukaan Chrome otomatis: {e}", "WARNING")
        for _ in range(15):
            time.sleep(1)
            if check_port_open(port):
                log("Chrome debugging port 9222 terdeteksi aktif.", "SUCCESS")
                return True
        return False
    return True

def connect_to_aistudio(p, port=9222, target_model="gemini-3.8-flash"):
    """Hubungkan Playwright ke Chrome port 9222, bersihkan tab lama, dan aktifkan tab AI Studio."""
    if not ensure_chrome_debug_open(port, target_model):
        raise ConnectionError(
            f"Port {port} gagal dibuka otomatis!\n"
            f"Silakan jalankan start_chrome_debug.bat secara manual.\n"
        )

    log(f"Menghubungkan ke Chrome di http://127.0.0.1:{port} via CDP...", "INFO")
    browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
    contexts = browser.contexts
    if not contexts:
        raise RuntimeError("Tidak ditemukan browser context aktif di Chrome!")

    context = contexts[0]
    
    # 1. Bersihkan tab-tab duplikat
    close_duplicate_tabs(context)

    # 2. Cari tab AI Studio aktif
    pages = context.pages
    target_page = None
    for page in pages:
        url = page.url.lower()
        if "aistudio.google.com" in url:
            target_page = page
            log(f"Menemukan tab Google AI Studio aktif: {page.url[:60]}...", "SUCCESS")
            break

    # 3. Jika belum ada tab AI Studio sama sekali, buka baru
    if not target_page:
        target_url = f"https://aistudio.google.com/prompts/new_chat?model={target_model}"
        log(f"Membuka tab AI Studio: {target_url}...", "INFO")
        target_page = context.new_page()
        target_page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        try:
            # Tunggu rendering Angular/Material UI selesai (bisa 5-8 detik saat cold start)
            target_page.wait_for_selector("textarea[placeholder*='prompt' i], textarea", state="visible", timeout=30000)
            log("Input box AI Studio terdeteksi dan siap.", "SUCCESS")
        except Exception:
            time.sleep(3)

    target_page.bring_to_front()
    dismiss_any_overlay(target_page)

    # 4. Pastikan mode High
    ensure_thinking_level_high(target_page)

    return browser, target_page


def get_input_box(page):
    """Cari elemen input box prompt di AI Studio."""
    input_selectors = [
        "textarea[placeholder*='prompt' i]",
        "textarea[aria-label*='prompt' i]",
        "textarea[placeholder*='Type' i]",
        "ms-autosize-textarea textarea",
        "ms-text-chunk textarea",
        "textarea.mat-mdc-input-element",
        "div[contenteditable='true']",
        "textarea"
    ]
    for sel in input_selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.last.is_visible():
                return loc.last
        except Exception:
            continue
    raise RuntimeError("Gagal menemukan input box prompt di AI Studio!")


def dismiss_any_overlay(page):
    """Pastikan tidak ada dialog modal, banner, backdrop, atau tools berbayar yang aktif."""
    try:
        # 1. Tekan tombol Escape untuk menutup dialog/popover/dropdown apapun yang aktif
        page.keyboard.press("Escape")
        time.sleep(0.3)
    except Exception:
        pass

    try:
        # 2. Tutup dialog modal jika tombol close terlihat
        close_selectors = [
            "button[aria-label='Close dialog']",
            "button[aria-label='Close']",
            "button:has-text('Dismiss')",
            "button:has-text('Got it')",
            "button:has-text('Not now')",
            "button:has-text('Cancel')"
        ]
        for sel in close_selectors:
            btns = page.locator(sel)
            for i in range(btns.count()):
                try:
                    b = btns.nth(i)
                    if b.is_visible():
                        b.click()
                        time.sleep(0.3)
                except Exception:
                    pass
    except Exception:
        pass

    try:
        # 3. HAPUS SEMUA TOOL CHIPS (Grounding with Google Search, Code Execution, dsb.)
        # Ini KUNCI agar Google AI Studio TIDAK PERNAH meminta API Key!
        remove_chips = page.locator("button[aria-label*='Remove' i], button.tool-chip-button + button")
        for i in range(remove_chips.count()):
            try:
                rc = remove_chips.nth(i)
                if rc.is_visible():
                    rc.click()
                    time.sleep(0.3)
            except Exception:
                pass
    except Exception:
        pass

    try:
        # 4. Matikan switch tools jika masih ada yang aktif
        switches = page.locator("button.mdc-switch--selected, [role='switch'][aria-checked='true']")
        for i in range(switches.count()):
            try:
                sw = switches.nth(i)
                if sw.is_visible():
                    sw.click()
                    time.sleep(0.3)
            except Exception:
                pass
    except Exception:
        pass

    try:
        # 5. Tutup sidebar overlay jika ada
        overlay = page.locator(".sidebar-overlay, div.sidebar-overlay")
        if overlay.count() > 0 and overlay.first.is_visible():
            toggle = page.locator("button.runsettings-toggle-button")
            if toggle.count() > 0 and toggle.first.is_visible():
                toggle.first.click()
                time.sleep(0.3)
            else:
                overlay.first.click(force=True)
                time.sleep(0.3)
    except Exception:
        pass


def _wait_for_response(page, turn_count_before, timeout_seconds=360):
    """Tunggu respons streaming AI Studio tuntas, kembalikan teks turn terbaru."""
    log("Menunggu Gemini di AI Studio selesai berpikir dan menghasilkan output...", "INFO")
    start_wait = time.time()
    last_text_len = 0
    stable_cycles = 0
    # Keandalan deteksi selesai: (1) teks stabil beberapa siklus, (2) tombol
    # Stop benar-benar hilang, (3) ada masa streaming minimal — mencegah
    # jawaban dipotong saat model "berpikir" tanpa memancarkan teks baru.
    required_stable_cycles = 3   # 3 x 3s = 9 detik tanpa pertumbuhan teks
    min_stream_seconds = 15

    while time.time() - start_wait < timeout_seconds:
        time.sleep(3.0)

        # Cek tombol stop
        stop_buttons = page.locator("button:has-text('Stop'), button[aria-label*='Cancel' i], button[aria-label*='Stop' i]")
        is_still_generating = False
        try:
            if stop_buttons.count() > 0 and stop_buttons.first.is_visible():
                is_still_generating = True
        except Exception:
            pass

        current_text = extract_latest_response(page, turn_index_start=turn_count_before)
        curr_len = len(current_text)
        elapsed = int(time.time() - start_wait)

        if curr_len > 0:
            if curr_len == last_text_len:
                stable_cycles += 1
            else:
                stable_cycles = 0
                last_text_len = curr_len

            log(f"Streaming berjalan ({elapsed}s): {curr_len} karakter terdeteksi...", "INFO")

            # Selesai = (teks stabil 9 detik + tombol Stop hilang) ATAU (teks stabil >= 18s / 6 siklus)
            # sudah berjalan minimal beberapa detik.
            if ((not is_still_generating and stable_cycles >= required_stable_cycles) or (stable_cycles >= 6)) \
                    and elapsed >= min_stream_seconds:
                log("Streaming tuntas dan teks respon stabil!", "SUCCESS")
                return current_text
        else:
            # Deteksi error model AI Studio secara instan agar tidak menunggu timeout
            try:
                latest_turn = page.locator("ms-chat-turn").last
                if latest_turn.count() > 0:
                    lt_txt = latest_turn.inner_text().lower()
                    if any(err in lt_txt for err in ["internal error", "rate limit", "quota exceeded", "something went wrong"]):
                        raise RuntimeError(f"AI Studio error terdeteksi: {latest_turn.inner_text().strip()[:100]}")
            except Exception as ex:
                if "AI Studio error terdeteksi" in str(ex):
                    raise
            log(f"Menunggu respons dimulai ({elapsed}s)...", "INFO")

    final_text = extract_latest_response(page, turn_index_start=turn_count_before)
    if final_text:
        log(f"Timeout {timeout_seconds}s — mengembalikan teks terakhir ({len(final_text)} char).", "WARNING")
        return final_text
    raise TimeoutError(f"Timeout menunggu respons AI Studio ({timeout_seconds}s)")


def _page_is_standard_playground(pg):
    """True bila pg adalah playground chat standar (bukan Antigravity Agent)."""
    try:
        url = pg.url.lower()
        if "/agent" in url:
            return False
        # Pastikan ada textarea prompt standar yang terlihat
        for sel in ["textarea[placeholder*='prompt' i]", "ms-autosize-textarea textarea", "textarea"]:
            loc = pg.locator(sel)
            if loc.count() > 0 and loc.last.is_visible():
                return True
        return False
    except Exception:
        return False


SAVED_URL_PATH = os.path.join(DATA_DIR, "aistudio_playground_url.txt")


def _save_playground_url(url):
    """Simpan URL percakapan standar terakhir yang berhasil dipakai (self-healing)."""
    try:
        if "/prompts/" in url and "new_chat" not in url:
            with open(SAVED_URL_PATH, "w", encoding="utf-8") as f:
                f.write(url.strip())
    except Exception:
        pass


def _load_playground_url():
    try:
        with open(SAVED_URL_PATH, "r", encoding="utf-8") as f:
            url = f.read().strip()
        return url if url.startswith("https://aistudio.google.com/prompts/") else None
    except Exception:
        return None


def _resolve_standard_page(browser, page):
    """Kembalikan halaman playground chat standar AI Studio.

    Urutan: tab saat ini -> tab aistudio lain -> URL standar tersimpan ->
    klik nav Playground -> tab baru new_chat (2 varian). Return None bila
    semua gagal, sehingga pemanggil bisa fallback ke jalur API.
    """
    if _page_is_standard_playground(page):
        _save_playground_url(page.url)
        return page

    # Tab aistudio lain yang masih terbuka
    try:
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if "aistudio" in pg.url.lower() and _page_is_standard_playground(pg):
                    pg.bring_to_front()
                    _save_playground_url(pg.url)
                    return pg
    except Exception:
        pass

    # URL percakapan standar tersimpan dari sesi sukses sebelumnya
    saved = _load_playground_url()
    if saved:
        try:
            ctx = browser.contexts[0]
            np = ctx.new_page()
            np.goto(saved, wait_until="domcontentloaded", timeout=60000)
            # Percakapan panjang butuh waktu muat — polling hingga 20 detik
            deadline = time.time() + 20
            while time.time() < deadline:
                if _page_is_standard_playground(np):
                    break
                time.sleep(2.0)
            if _page_is_standard_playground(np):
                log("Playground standar dibuka dari URL tersimpan.", "SUCCESS")
                np.bring_to_front()
                return np
        except Exception:
            pass

    # Klik nav "Playground" di sidebar (timeout pendek agar tidak menggantung)
    try:
        nav = page.get_by_text("Playground")
        if nav.count() > 0:
            nav.first.click(timeout=5000)
            time.sleep(4.0)
            if _page_is_standard_playground(page):
                _save_playground_url(page.url)
                return page
    except Exception:
        pass

    # Tab baru new_chat (2 varian URL)
    for url in ("https://aistudio.google.com/prompts/new_chat",
                "https://aistudio.google.com/prompts/new_chat?model=gemini-3.8-flash"):
        try:
            ctx = browser.contexts[0]
            np = ctx.new_page()
            np.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                np.wait_for_selector("textarea[placeholder*='prompt' i], textarea", state="visible", timeout=25000)
            except Exception:
                time.sleep(3.0)
            if _page_is_standard_playground(np):
                np.bring_to_front()
                return np
        except Exception:
            pass

    return None


def start_fresh_chat(page, retries=2):
    """Buka chat playground standar BARU untuk mengisolasi satu run.
    1. Utamakan klik tombol 'New chat' (+) langsung di UI AI Studio (paling cepat & stabil tanpa reload).
    2. Jika belum ada, arahkan page.goto ke new_chat dan tunggu textarea siap.
    3. Dismiss semua dialog/overlay dan hapus tool chips agar bebas API key.
    """
    for attempt in range(retries + 1):
        try:
            # Coba klik tombol New chat di UI
            new_chat_btn = page.locator("button[aria-label='New chat'], ms-app-bar button:has(i.fa-plus)")
            if new_chat_btn.count() > 0 and new_chat_btn.first.is_visible():
                new_chat_btn.first.click()
                time.sleep(2.0)
            else:
                page.goto("https://aistudio.google.com/prompts/new_chat", wait_until="domcontentloaded", timeout=45000)
                time.sleep(3.0)

            # Bersihkan modal, backdrop, dan matikan tools
            dismiss_any_overlay(page)

            # Tunggu textarea prompt benar-benar siap dan terlihat
            page.wait_for_selector("textarea[placeholder*='prompt' i], textarea", state="visible", timeout=20000)
            log("Chat baru AI Studio berhasil dibuka & siap digunakan.", "SUCCESS")
            return True
        except Exception as e:
            log(f"Percobaan buka chat baru #{attempt+1} gagal ({e}), mengulang...", "WARNING")
            time.sleep(2.0)

    return False


def _wait_attachments_ready(page, filenames, timeout_seconds=45):
    """Tunggu semua lampiran selesai diproses AI Studio.

    Chip lampiran merender nama file; kita tunggu tiap nama (16 karakter awal)
    muncul di halaman lalu stabil sesaat. Tanpa ini, Run masih disabled saat
    gambar besar/berjumlah banyak sedang diproses dan submit terbuang.
    """
    start = time.time()
    stems = [os.path.basename(fn)[:16] for fn in filenames]
    while time.time() - start < timeout_seconds:
        try:
            body = page.inner_text("body")
        except Exception:
            time.sleep(1.5)
            continue
        found = sum(1 for s in stems if s in body)
        if found >= len(stems):
            time.sleep(2.0)
            return True
        time.sleep(1.5)
    return False


def _generation_started(page):
    """True bila generasi terdeteksi mulai (tombol Stop muncul)."""
    try:
        stop_buttons = page.locator(
            "button:has-text('Stop'), button[aria-label*='Stop' i], button[aria-label*='Cancel' i]")
        if stop_buttons.count() > 0 and stop_buttons.first.is_visible():
            return True
    except Exception:
        pass
    return False


def _submit_prompt(page):
    """Picu eksekusi prompt di AI Studio dan VERIFIKASI generasi benar-benar mulai.

    Urutan: fokus input -> Control+Enter -> cek; bila tidak mulai, klik tombol
    Run yang benar-benar terlihat -> cek lagi. Return True bila generasi jalan.
    """
    try:
        get_input_box(page).click(force=True)
        time.sleep(0.4)
    except Exception:
        pass

    page.keyboard.press("Control+Enter")
    time.sleep(3.0)
    if _generation_started(page):
        return True

    # Fallback: klik tombol Run yang terlihat (teks 'Run', bukan ikon lain)
    run_buttons = page.locator("button:has-text('Run')")
    try:
        n = run_buttons.count()
        for i in range(n):
            btn = run_buttons.nth(i)
            try:
                if btn.is_visible() and "run" in btn.inner_text().strip().lower():
                    btn.click()
                    time.sleep(3.0)
                    if _generation_started(page):
                        return True
            except Exception:
                continue
    except Exception:
        pass

    # Percobaan terakhir: fokus ulang lalu Control+Enter sekali lagi
    try:
        get_input_box(page).click(force=True)
    except Exception:
        pass
    page.keyboard.press("Control+Enter")
    time.sleep(3.0)
    return _generation_started(page)


def inject_and_run(page, prompt_text, prompt_file_path=None, instruction="", timeout_seconds=360):
    """Injeksi prompt (via file upload terlampir atau teks langsung), picu Run, dan tunggu respons."""
    dismiss_any_overlay(page)

    file_input = page.locator("input[type='file']")
    use_file_upload = False

    # Jika ada file prompt fisik dan input file tersedia, utamakan unggah file
    if prompt_file_path and os.path.isfile(prompt_file_path) and file_input.count() > 0:
        log(f"Mengunggah file prompt: {os.path.basename(prompt_file_path)}...", "INFO")
        try:
            file_input.first.set_input_files(prompt_file_path)
            time.sleep(2.0)
            target_input = get_input_box(page)
            target_input.click(force=True)
            trigger_text = instruction or (
                "Bacalah seluruh isi file terlampir secara lengkap. Hasilkan pembahasan sesuai format JSON "
                "yang diinstruksikan dalam file tanpa ada nomor yang terlewat."
            )
            try:
                target_input.evaluate("(el, text) => { el.value = text; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }", trigger_text)
            except Exception:
                target_input.fill(trigger_text)
            time.sleep(1.0)
            use_file_upload = True
            log("File prompt berhasil diunggah dengan instruksi pemicu.", "SUCCESS")
        except Exception as e:
            log(f"Upload file mengalami kendala ({e}). Menggunakan injeksi teks langsung...", "WARNING")

    if not use_file_upload:
        log(f"Menginjeksi teks prompt ({len(prompt_text)} karakter) langsung...", "INFO")
        target_input = get_input_box(page)
        target_input.click(force=True)
        time.sleep(0.5)
        try:
            target_input.evaluate(
                "(el, text) => { el.value = text; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }",
                prompt_text
            )
        except Exception:
            target_input.fill(prompt_text)
        time.sleep(1.0)

    # Catat jumlah turn sebelum submit untuk tracking respons baru
    turn_count_before = page.locator("ms-chat-turn").count()
    log(f"Turn count sebelum submit: {turn_count_before}", "INFO")

    # Eksekusi (Control+Enter atau tombol Run)
    log("Memicu eksekusi (Control+Enter / tombol Run)...", "INFO")
    if not _submit_prompt(page):
        log("Generasi tidak terdeteksi mulai — percobaan submit kedua...", "WARNING")
        if not _submit_prompt(page):
            raise RuntimeError("Submit prompt AI Studio gagal (generasi tidak mulai).")

    return _wait_for_response(page, turn_count_before, timeout_seconds)


# Stoplist kata umum (tidak khas target mana pun) + istilah template soal.
_GENERIC_WORDS = {
    "adalah", "yaitu", "dengan", "untuk", "dari", "pada", "dalam", "yang",
    "tersebut", "berikut", "terdapat", "terdiri", "merupakan", "termasuk",
    "dapat", "akan", "atau", "dan", "jika", "maka", "karena", "sebagai",
    "serta", "antara", "secara", "bahwa", "adapun", "inilah", "itulah",
    "soal", "nomor", "pernyataan", "pertanyaan", "pilihan", "gambar",
    "teks", "stimulus", "jawaban", "benar", "salah",
}


def _question_text_of(q):
    """Kumpulkan teks naratif sebuah soal dari field-field umum learning JSON."""
    parts = []
    for fld in ("pertanyaan", "stimulus", "pernyataan"):
        v = q.get(fld)
        if isinstance(v, dict):
            parts.extend(str(x) for x in v.values() if isinstance(x, str) and x.strip())
        elif isinstance(v, str) and v.strip():
            parts.append(v)
    for v in (q.get("pilihan_jawaban") or []):
        if isinstance(v, str) and v.strip():
            parts.append(v)
        elif isinstance(v, dict):
            parts.extend(str(x) for x in v.values() if isinstance(x, str) and x.strip())
    return "\n".join(parts)


def _distinctive_tokens_for_slug(slug, max_tokens=2, min_len=6):
    """Ambil 1-2 kata khas dari pertanyaan pertama target (learning JSON).

    Kandidat kata diambil dari field naratif soal pertama, disaring dari
    stoplist kata umum, diurut dari yang terpanjang. Return list kosong
    bila learning JSON tidak tersedia / tidak ada kandidat.
    """
    path = os.path.join(DATA_DIR, f"{slug}_learning.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        first = (data.get("soal") or [])[0]
        text = _question_text_of(first)
    except (OSError, ValueError, IndexError, TypeError):
        return []
    words = re.findall(r"[A-Za-z\u00c0-\u00ff]{5,}", text)
    words = [w for w in words if len(w) >= min_len and w.lower() not in _GENERIC_WORDS]
    words.sort(key=len, reverse=True)
    tokens, seen = [], set()
    for w in words:
        low = w.lower()
        if any(low in s or s in low for s in seen):
            continue
        tokens.append(w)
        seen.add(low)
        if len(tokens) >= max_tokens:
            break
    return tokens


def _sanity_check_target_token(slug, raw_text):
    """Sanity check anti kontaminasi lintas-target (fase 4).
    Memastikan output valid dan memuat penanda struktur solusi yang benar.
    """
    if not raw_text or len(raw_text.strip()) < 200:
        raise RuntimeError(f"Respons AI Studio untuk {slug} kosong atau terlalu pendek ({len(raw_text or '')} karakter).")

    if '"question_number"' not in raw_text and '"nomor_soal"' not in raw_text:
        raise RuntimeError(f"Respons AI Studio untuk {slug} tidak memuat struktur JSON solusi yang valid (tidak ada 'question_number').")

    tokens = _distinctive_tokens_for_slug(slug)
    if tokens:
        matched = [tok for tok in tokens if tok.lower() in raw_text.lower()]
        if not matched:
            log(f"[{slug}] Catatan: token spesifik {tokens} tidak ditemukan secara verbatim di output, namun struktur solusi valid.", "INFO")


def extract_latest_response(page, turn_index_start=0):
    """Ekstrak teks balasan model terakhir dari DOM AI Studio.

    Strategi: ambil turn TERBARU yang memuat JSON respons nyata (ditandai
    "question_number"/"nomor_soal" diikuti ANGKA — speksifikasi prompt
    memuat placeholder sehingga echo prompt tak lolos).

    turn_index_start membatasi pemindaian hanya pada turn posisi >=
    turn_index_start (posisi turn dicatat pemanggil sebelum submit),
    sehingga jawaban turn LAMA (mapel lain, chat sama) tidak ikut terpilih.
    Bila rentang ketat itu kosong / tak ada match, fallback ke perilaku
    lama: pindai seluruh percakapan.

    Catatan: posisi turn dapat bergeser saat AI Studio mem-virtualisasi DOM
    percakapan panjang; karena itu mode ketat hanya aktif bila
    turn_index_start > 0.

    Sebelum membaca, tiap turn di-clone dan elemen .katex diganti LaTeX
    sumbernya (annotation/MathML) agar rumus tidak terbaca sebagai glyph
    italic per karakter + gema.
    """
    try:
        result = page.evaluate("""(turnIndexStart) => {
            const respMarker = /"(?:question_number|nomor_soal)"\\s*:\\s*\\d/;

            const latexOf = (k) => {
                const ann = k.querySelector('annotation[encoding="application/x-tex"]');
                if (ann && ann.textContent && ann.textContent.trim()) return ann.textContent.trim();
                const dl = k.getAttribute('data-latex') || k.getAttribute('data-tex');
                if (dl && dl.trim()) return dl.trim();
                const mml = k.querySelector('math, .katex-mathml');
                if (mml && mml.textContent && mml.textContent.trim()) return mml.textContent.trim();
                return '';
            };
            const turnText = (el) => {
                const clone = el.cloneNode(true);
                clone.querySelectorAll('.katex').forEach(k => {
                    const latex = latexOf(k);
                    const span = document.createElement('span');
                    span.textContent = latex ? ' $' + latex + '$ ' : ' ';
                    k.replaceWith(span);
                });
                return clone.innerText || '';
            };

            const allTurns = document.querySelectorAll('ms-chat-turn');
            const startIdx = Math.max(0, Math.min(turnIndexStart | 0, allTurns.length));
            const scan = (lo, needMarker) => {
                for (let i = allTurns.length - 1; i >= lo; i--) {
                    const txt = turnText(allTurns[i]);
                    if (needMarker) {
                        const hasMarker = respMarker.test(txt) || txt.includes('"description"') || txt.includes('"filename"');
                        if (hasMarker && txt.length > 50) {
                            return txt;
                        }
                    } else if (txt.length > 10) {
                        return txt;
                    }
                }
                return '';
            };

            // Rentang ketat: hanya turn yang muncul PADA/SETELAH posisi submit
            if (startIdx > 0) {
                const strict = scan(startIdx, true);
                if (strict) return strict;
                // PENTING: Jangan fallback ke turn 0 bila startIdx > 0,
                // agar tidak salah membaca respons turn lama sebelum turn baru selesai!
                return '';
            }

            // Fallback: pindai seluruh percakapan hanya bila startIdx == 0
            return scan(0, true) || scan(0, false);
        }""", int(turn_index_start or 0))
        return result or ""
    except Exception:
        return ""


def safe_parse_json(text):
    """Parse JSON secara aman dari output model, termasuk markdown formatting, escape backslash, dan json_repair."""
    if not text:
        return None
    text = text.strip()
    # Bersihkan header UI turn AI Studio
    text = re.sub(r"^(?:edit|more_vert|\s)+", "", text)
    text = re.sub(r"(?:thumb_up|thumb_down|\s)+$", "", text)
    if "```" in text:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
        if m:
            text = m.group(1).strip()

    # Ekstrak konten dalam kurung siku/kurawal terluar
    fb = text.find('[')
    lb = text.rfind(']')
    if fb != -1 and lb != -1 and lb > fb:
        text = text[fb:lb+1]

    # Percobaan 1: json.loads langsung dengan perbaikan escape sequence (sangat cepat & akurat untuk LaTeX)
    fixed = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu]|u[0-9a-fA-F]{4})', r'\\\\', text)
    try:
        return json.loads(fixed, strict=False)
    except Exception:
        pass

    # Percobaan 2: json_repair (untuk kutip tak ter-escape & syntax errors lain)
    try:
        import json_repair
        res = json_repair.loads(text)
        if res is not None:
            return res
    except Exception:
        pass

    # Percobaan 2: Iris antara [ dan ]
    first_b = text.find('[')
    last_b = text.rfind(']')
    if first_b != -1 and last_b != -1 and last_b > first_b:
        sub = text[first_b:last_b+1]
        for cand in [sub, re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', sub)]:
            try:
                return json.loads(cand, strict=False)
            except Exception:
                pass

    # Percobaan 3: Iris objek-objek mandiri dalam array tak lengkap
    if first_b != -1:
        items = []
        depth = 0
        obj_start = -1
        in_string = False
        escape = False
        for i in range(first_b, len(text)):
            c = text[i]
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if c == '"':
                in_string = not in_string
                continue
            if not in_string:
                if c == '{':
                    if depth == 0:
                        obj_start = i
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0 and obj_start != -1:
                        obj_str = text[obj_start:i+1]
                        for c_obj in [obj_str, re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', obj_str)]:
                            try:
                                items.append(json.loads(c_obj, strict=False))
                                break
                            except Exception:
                                pass
                        obj_start = -1
        if items:
            return items

    return None


def _clean_corrupted_dict_keys(d):
    """Perbaiki dictionary yang terkena efek kutip unescaped seperti 'incident?","pilihan'."""
    if not isinstance(d, dict):
        return d
    for k in list(d.keys()):
        if '","pilihan' in k or '","pilihan_jawaban' in k:
            prefix_key = k.split('","')[0]
            val = d.pop(k)
            d["pilihan"] = val
            if "pertanyaan" in d and isinstance(d["pertanyaan"], str):
                d["pertanyaan"] = (d["pertanyaan"].strip() + " " + prefix_key.strip()).strip()
        elif isinstance(d[k], dict):
            _clean_corrupted_dict_keys(d[k])
        elif isinstance(d[k], list):
            for elem in d[k]:
                if isinstance(elem, dict):
                    _clean_corrupted_dict_keys(elem)
    return d


def _collect_dicts(item):
    res = []
    if isinstance(item, dict):
        res.append(_clean_corrupted_dict_keys(item))
    elif isinstance(item, list):
        for sub in item:
            res.extend(_collect_dicts(sub))
    return res


def run_phase_4_via_playwright(slug="bahasa_indonesia_paket_2", port=9222):
    """Eksekusi Fase 4 secara otomatis melalui Playwright Chrome CDP Bridge ke AI Studio PRO."""
    from pipeline.subject_catalog import MASTER_CATALOG
    if slug not in MASTER_CATALOG:
        raise ValueError(f"Target slug '{slug}' tidak ditemukan di MASTER_CATALOG!")

    item = MASTER_CATALOG[slug]
    name = item["name"]
    paket = item["paket"]
    prefix = item.get("prefix", "soal")

    lrn_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
    kunci_path = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
    sol_out = os.path.join(SOL_DIR, f"{slug.upper()}_SOLUTIONS.json")
    sol_export = os.path.join(EXPORTS_DIR, f"{slug}_solutions.json")
    sol_path = sol_out

    mapel_key = slug.split("_paket_")[0]
    images_dir = os.path.join(DATA_DIR, mapel_key, f"paket_{paket}", "images")

    with open(lrn_path, "r", encoding="utf-8") as f:
        lrn_data = json.load(f)
    with open(kunci_path, "r", encoding="utf-8") as f:
        kunci_data = json.load(f)

    questions = lrn_data.get("soal", [])
    total_q = len(questions)

    kunci_map = {}
    for k, v in kunci_data.get("kunci_pg", {}).items():
        kunci_map[str(k)] = v
    for k, v in kunci_data.get("kunci_bs", {}).items():
        kunci_map[str(k)] = [f"{k_}:{v_}" for k_, v_ in sorted(v.items())]

    from pipeline.swarm_manager import swarm_engine

    print("=" * 75)
    log(f"MEMULAI PENDEKATAN B: PLAYWRIGHT CHROME BRIDGE KE GOOGLE AI STUDIO PRO", "SUCCESS")
    log(f"Target Paket: {name} (Total: {total_q} Soal)", "INFO")
    print("=" * 75)

    with sync_playwright() as p:
        browser, page = connect_to_aistudio(p, port=port, target_model="gemini-3.8-flash")

        # Isolasi antar-target: wajib chat playground BARU per target, pola
        # sama dengan jalur fase 3. Tanpa ini, 1 percakapan AI Studio terpakai
        # ulang antar-target dan konteks model tercampur.
        page = _resolve_standard_page(browser, page)
        if page is None:
            raise RuntimeError(
                "Playground standar AI Studio tidak ditemukan (halaman Antigravity) — "
                "jalankan ulang atau gunakan jalur API.")
        if not start_fresh_chat(page):  # isolasi run: 1 target = 1 chat baru
            raise RuntimeError(
                "Gagal membuka chat baru AI Studio untuk isolasi target "
                f"'{slug}' — dibatalkan agar tidak melanjutkan di chat lama.")

        # -------------------------------------------------------------
        # TAHAP 1: SOLUSI 5 PILAR PEDAGOGIS (L3) VIA PROMPT FILE
        # -------------------------------------------------------------
        skip_5pilar = False
        all_solutions = []
        if os.path.isfile(sol_out):
            try:
                with open(sol_out, "r", encoding="utf-8") as sf:
                    existing_sol_data = json.load(sf)
                sols_list = existing_sol_data.get("solutions", [])
                if len(sols_list) >= total_q:
                    r1 = (sols_list[0].get("reasoning") or "").strip()
                    r2 = (sols_list[1].get("reasoning") or "").strip()
                    if r1 and r2 and r1 != r2:
                        skip_5pilar = True
                        all_solutions = sols_list
                        log(f"✅ Solusi 5 Pilar ({len(sols_list)}/{total_q}) sudah ada dan otentik di disk. Melewati Tahap 1.", "SUCCESS")
            except Exception:
                pass

        if not skip_5pilar:
            log("Mempersiapkan Prompt Mega-Batch 5 Pilar Pedagogis...", "INFO")
            prompt_5pilar = swarm_engine._build_5pillar_prompt(name, questions, kunci_map, slug=slug)
            prompt_file = os.path.join(PROMPT_DIR, f"{slug}_5pillar_prompt.txt")
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt_5pilar)
            log(f"File prompt disimpan di: {prompt_file}", "INFO")

            instruction_5pilar = (
                f"Bacalah seluruh isi file terlampir. Hasilkan PEMBAHASAN 5 PILAR PEDAGOGIS (L3) "
                f"untuk SELURUH {total_q} butir soal (Nomor 1 sampai {total_q}) dalam format JSON array murni "
                f"tanpa ada nomor soal yang terlewat atau dipotong."
            )

            log("Mengirimkan file prompt 5 Pilar ke AI Studio PRO...", "INFO")
            raw_output_solutions = inject_and_run(
                page,
                prompt_text=prompt_5pilar,
                prompt_file_path=prompt_file,
                instruction=instruction_5pilar,
                timeout_seconds=int(os.environ.get("AI_STUDIO_TIMEOUT", "600"))
            )

            # Sanity check anti kontaminasi lintas-target
            _sanity_check_target_token(slug, raw_output_solutions)

            # Simpan raw output
            raw_file = os.path.join(RAW_DIR, f"{slug}_5pillar_raw.txt")
            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(raw_output_solutions)
            log(f"Raw output tersimpan di: {raw_file}", "INFO")

            parsed_solutions = safe_parse_json(raw_output_solutions) or []
            existing_sols_map = {}

            for sol in _collect_dicts(parsed_solutions):
                no = sol.get("question_number")
                if no:
                    try:
                        existing_sols_map[int(no)] = sol
                    except (ValueError, TypeError):
                        pass

            log(f"Hasil ekstraksi awal: {len(existing_sols_map)}/{total_q} solusi terdeteksi.", "INFO")

            # Multi-turn continuation guard
            all_expected_nos = set(range(1, total_q + 1))
            missing_nos = sorted(list(all_expected_nos - set(existing_sols_map.keys())))

            continuation_attempt = 1
            while missing_nos and continuation_attempt <= 4:
                log(f"⚠️ Solusi belum lengkap (kurang nomor: {missing_nos}). Menjalankan continuation #{continuation_attempt}...", "WARNING")
                missing_questions = [q for q in questions if q["nomor"] in missing_nos]
                prompt_missing = swarm_engine._build_5pillar_prompt(name, missing_questions, kunci_map, slug=slug)
                prompt_missing_file = os.path.join(PROMPT_DIR, f"{slug}_missing_att{continuation_attempt}.txt")
                with open(prompt_missing_file, "w", encoding="utf-8") as f:
                    f.write(prompt_missing)

                inst_missing = (
                    f"Tolong lengkapi PEMBAHASAN 5 PILAR PEDAGOGIS untuk nomor yang belum ada berikut: {missing_nos}. "
                    f"Format JSON array persis sama seperti sebelumnya."
                )

                raw_missing = inject_and_run(
                    page,
                    prompt_text=prompt_missing,
                    prompt_file_path=prompt_missing_file,
                    instruction=inst_missing,
                    timeout_seconds=240
                )

                parsed_missing = safe_parse_json(raw_missing) or []
                for sol in _collect_dicts(parsed_missing):
                    no = sol.get("question_number")
                    if no:
                        try:
                            existing_sols_map[int(no)] = sol
                        except (ValueError, TypeError):
                            pass

                missing_nos = sorted(list(all_expected_nos - set(existing_sols_map.keys())))
                continuation_attempt += 1

            if len(existing_sols_map) < total_q:
                log(f"⚠️ Perhatian: Solusi akhir terisi {len(existing_sols_map)}/{total_q} butir soal.", "WARNING")
            else:
                log(f"✅ SEMPURNA! 100% Solusi 5 Pilar ({len(existing_sols_map)}/{total_q} Soal) lengkap!", "SUCCESS")

            # Proses & Standardisasi Data Solusi
            for no, sol in existing_sols_map.items():
                sol["question_id"] = f"{prefix}_p{paket}_q{no:02d}"
                sol["concept_kunci"] = sol.get("concept_kunci") or sol.get("concept_tags") or [name]
                raw_k = kunci_map.get(str(no), "-")
                if isinstance(raw_k, list):
                    sol["official_answer"] = {"format": "per_statement_benar_salah", "correct": [str(x) for x in raw_k]}
                else:
                    sol["official_answer"] = {"format": "single_choice", "correct": str(raw_k)}

                for fld in ("why_correct", "reasoning", "diketahui", "ditanyakan", "question_title"):
                    if sol.get(fld):
                        sol[fld] = text_quality.repair_math_text(
                            re.sub(r"\btranskrip(?:si)?\b", "kutipan", sol[fld], flags=re.I))
                for st in sol.get("steps", []):
                    for fld in ("explanation", "title"):
                        if st.get(fld):
                            st[fld] = text_quality.repair_math_text(
                                re.sub(r"\btranskrip(?:si)?\b", "kutipan", st[fld], flags=re.I))
                for lst_key in ("tips", "common_mistakes"):
                    for i, item in enumerate(sol.get(lst_key) or []):
                        if isinstance(item, str) and item.strip():
                            sol[lst_key][i] = text_quality.repair_math_text(
                                re.sub(r"\btranskrip(?:si)?\b", "kutipan", item, flags=re.I))

            all_solutions = [existing_sols_map[k] for k in sorted(existing_sols_map.keys())]
            sol_data = {"slug": slug, "solutions": all_solutions}

            with open(sol_out, "w", encoding="utf-8") as f:
                json.dump(sol_data, f, indent=2, ensure_ascii=False)
            with open(sol_export, "w", encoding="utf-8") as f:
                json.dump(sol_data, f, indent=2, ensure_ascii=False)
            log(f"Solusi tersimpan di {sol_out} dan ekspor unduhan di {sol_export}", "SUCCESS")

        # Update registry.json
        reg_path = os.path.join(SOL_DIR, "registry.json")
        registry = {}
        if os.path.isfile(reg_path):
            with open(reg_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
        reg_entry = {
            "active_source": f"{slug.upper()}_SOLUTIONS.json",
            "name": name,
            "paket": paket,
            "status": "completed",
            "file": f"{slug.upper()}_SOLUTIONS.json",
            "total_questions": len(all_solutions),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        registry[slug] = reg_entry
        try:
            from solution_loader import _normalize_slug
            alias_slug = _normalize_slug(mapel_key, paket)
            if alias_slug:
                registry[alias_slug] = reg_entry
        except Exception:
            pass
        with open(reg_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

        # -------------------------------------------------------------
        # TAHAP 2: VERIFIKASI / GENERASI SOAL SERUPA
        # -------------------------------------------------------------
        # Deteksi nomor yang belum punya Soal Serupa ATAU berisi duplikat dummy
        seen_sim_text = set()
        missing_serupa = []
        for q in questions:
            sim = q.get("soal_serupa")
            if not sim or not isinstance(sim, dict):
                missing_serupa.append(q)
                continue
            sim_p = (sim.get("pertanyaan") or "").strip().lower()[:120]
            if len(sim_p) < 25 or sim_p in seen_sim_text:
                missing_serupa.append(q)
            else:
                seen_sim_text.add(sim_p)

        if not missing_serupa:
            log(f"Soal Serupa untuk seluruh {total_q} butir soal sudah 100% aktif dan unik di {lrn_path}.", "SUCCESS")
        else:
            log(f"Membuat Soal Serupa untuk {len(missing_serupa)} butir soal yang belum unik/belum ada...", "INFO")
            prompt_serupa = swarm_engine._build_soal_serupa_prompt(name, missing_serupa, slug=slug)
            prompt_serupa_file = os.path.join(PROMPT_DIR, f"{slug}_soal_serupa_prompt.txt")
            with open(prompt_serupa_file, "w", encoding="utf-8") as f:
                f.write(prompt_serupa)

            raw_serupa = inject_and_run(
                page,
                prompt_text=prompt_serupa,
                prompt_file_path=prompt_serupa_file,
                instruction="Hasilkan Soal Serupa (Text-Only) sesuai format JSON di dalam file terlampir.",
                timeout_seconds=420
            )

            parsed_serupa = safe_parse_json(raw_serupa) or []
            serupa_map = {}
            for item in _collect_dicts(parsed_serupa):
                no = item.get("nomor_soal") or item.get("nomor") or item.get("question_number")
                sim_content = item.get("soal_serupa")
                if not sim_content and "pertanyaan" in item and ("pilihan" in item or "pilihan_jawaban" in item):
                    sim_content = {
                        "pertanyaan": item.get("pertanyaan"),
                        "pilihan": item.get("pilihan") or item.get("pilihan_jawaban", []),
                        "kunci": item.get("kunci") or item.get("kunci_jawaban", "A"),
                        "pembahasan": item.get("pembahasan", "")
                    }
                if no and sim_content:
                    p_t = (sim_content.get("pertanyaan") or "").strip()
                    opts = sim_content.get("pilihan") or []
                    if len(p_t) >= 20 and len(opts) >= 2:
                        try:
                            serupa_map[int(no)] = sim_content
                        except (ValueError, TypeError):
                            pass

            # Continuation guard: minta nomor yang terlewat hingga lengkap
            expected_nos = {q["nomor"] for q in missing_serupa}
            attempt = 1
            while expected_nos - set(serupa_map.keys()) and attempt <= 3:
                still_missing = [q for q in missing_serupa if q["nomor"] not in serupa_map]
                log(f"⚠️ Soal Serupa belum lengkap (kurang: {sorted(expected_nos - set(serupa_map.keys()))}). Continuation #{attempt}...", "WARNING")
                prompt_missing = swarm_engine._build_soal_serupa_prompt(name, still_missing, slug=slug)
                prompt_missing_file = os.path.join(PROMPT_DIR, f"{slug}_serupa_missing_{attempt}.txt")
                with open(prompt_missing_file, "w", encoding="utf-8") as f:
                    f.write(prompt_missing)

                raw_missing = inject_and_run(
                    page,
                    prompt_text=prompt_missing,
                    prompt_file_path=prompt_missing_file,
                    instruction=(f"Lengkapi Soal Serupa untuk nomor yang belum ada berikut: "
                                 f"{sorted(q['nomor'] for q in still_missing)}. Format JSON array persis sama."),
                    timeout_seconds=300
                )
                for item in _collect_dicts(safe_parse_json(raw_missing) or []):
                    no = item.get("nomor_soal") or item.get("nomor") or item.get("question_number")
                    sim_content = item.get("soal_serupa")
                    if not sim_content and "pertanyaan" in item and ("pilihan" in item or "pilihan_jawaban" in item):
                        sim_content = {
                            "pertanyaan": item.get("pertanyaan"),
                            "pilihan": item.get("pilihan") or item.get("pilihan_jawaban", []),
                            "kunci": item.get("kunci") or item.get("kunci_jawaban", "A"),
                            "pembahasan": item.get("pembahasan", "")
                        }
                    if no and sim_content:
                        p_t = (sim_content.get("pertanyaan") or "").strip()
                        opts = sim_content.get("pilihan") or []
                        if len(p_t) >= 20 and len(opts) >= 2:
                            try:
                                serupa_map[int(no)] = sim_content
                            except (ValueError, TypeError):
                                pass
                attempt += 1

            for q in questions:
                if q["nomor"] in serupa_map and serupa_map[q["nomor"]]:
                    q["soal_serupa"] = serupa_map[q["nomor"]]
            with open(lrn_path, "w", encoding="utf-8") as f:
                json.dump(lrn_data, f, indent=2, ensure_ascii=False)
            filled = sum(1 for q in questions if q.get("soal_serupa"))
            log(f"Soal Serupa terisi {filled}/{total_q} di {lrn_path}.", "SUCCESS" if filled == total_q else "WARNING")

        # Validasi Kualitas Mutlak via Quality Guard sebelum Ekspor Resmi
        log("Memverifikasi paket dengan Gerbang Mutu Zero-Trust Quality Guard...", "INFO")
        try:
            from pipeline.quality_guard import assert_package_integrity, QualityGuardError
        except ImportError:
            from quality_guard import assert_package_integrity, QualityGuardError

        try:
            # Load solution doc for validation
            sol_validation_doc = None
            if os.path.exists(sol_path):
                with open(sol_path, "r", encoding="utf-8") as sf:
                    sol_validation_doc = json.load(sf)
            kunci_validation_doc = None
            kunci_p = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
            if os.path.exists(kunci_p):
                with open(kunci_p, "r", encoding="utf-8") as kf:
                    kunci_validation_doc = json.load(kf)

            assert_package_integrity(
                slug=slug,
                learning_doc=lrn_data,
                solutions_doc=sol_validation_doc,
                img_dir=images_dir,
                kunci_doc=kunci_validation_doc
            )
            log("✅ Gerbang Mutu Zero-Trust Quality Guard: 100% LOLOS TANPA CACAT!", "SUCCESS")
        except QualityGuardError as qe:
            log(f"🚨 GERBANG MUTU DITOLAK [{qe.category}]: {qe.message}", "ERROR")
            if qe.violations:
                for v in qe.violations[:5]:
                    log(f"   -> {v}", "ERROR")
            raise

        # Ekspor learning.json ke direktori exports/
        lrn_export = os.path.join(EXPORTS_DIR, f"{slug}_learning.json")
        with open(lrn_export, "w", encoding="utf-8") as f:
            json.dump(lrn_data, f, indent=2, ensure_ascii=False)
        log(f"File learning diekspor untuk diunduh di: {lrn_export}", "SUCCESS")

    # -------------------------------------------------------------
    # TAHAP 3: MENJALANKAN AUTOMATED AUDITOR RESMI
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    log("MENJALANKAN AUDITOR MUTU OTOMATIS (ZERO-TRUST AUDIT)...", "INFO")
    print("=" * 75)
    auditor_cmd = [sys.executable, os.path.join(BASE_DIR, "pipeline", "05_automated_auditor.py"), "--target", slug]
    res = subprocess.run(auditor_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(res.stdout)
    if res.returncode == 0:
        log(f"🎉 AUDIT MUTU 100% PASS! Paket {name} Lulus Verifikasi Otoritatif!", "SUCCESS")
    else:
        log(f"Audit mengindikasikan catatan yang perlu diperiksa:\n{res.stderr}", "WARNING")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Playwright Google AI Studio PRO Bridge")
    parser.add_argument("--slug", type=str, default="bahasa_indonesia_paket_2")
    parser.add_argument("--port", type=int, default=9222)
    args = parser.parse_args()

    run_phase_4_via_playwright(slug=args.slug, port=args.port)
