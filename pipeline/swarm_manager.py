# -*- coding: utf-8 -*-
"""pipeline/swarm_manager.py — Multi-Agent Multiplier Engine with Live State & Event Bus.

Modernized 5-Division Automated Pipeline:
  Divisi 1: Scout Swarm (Playwright Automated Ingress & Official Key Scraper)
  Divisi 2: Data Architect (Canonical Dual-Artifact Separation: Tipe A Visual & Tipe B AI Text)
  Divisi 3: Visionary Scanner (Gemini 3.8 Flash Formula & Diagram Transcription)
  Divisi 4: Reasoning Engine (Gemini 3.8 Flash 5-Pillar Solutions & Soal Serupa Generator)
  Divisi 5: Zero-Trust Quality Auditor & Registry Release
"""
import os
import re
import json
import time
import threading
import urllib.request
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import text_quality  # noqa: E402  (normalisasi teks hasil ekstraksi DOM)

from pipeline.subject_catalog import MASTER_CATALOG, get_full_catalog, get_unscraped_subjects

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KUNCI_DIR = os.path.join(DATA_DIR, "kunci")
RAW_DIR = os.path.join(DATA_DIR, "raw_html")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")
REG_PATH = os.path.join(SOL_DIR, "registry.json")

os.makedirs(KUNCI_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(SOL_DIR, exist_ok=True)

BASE_URL = "https://pusmendik.kemendikdasmen.go.id"
SIMULASI_URL = f"{BASE_URL}/tka/simulasi_tka/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

CANONICAL_LABELS = {
    "tepat": "Tepat",
    "tidak tepat": "Tidak Tepat",
    "sesuai": "Sesuai",
    "tidak sesuai": "Tidak Sesuai",
    "benar": "Benar",
    "salah": "Salah"
}


class SwarmManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.is_running = False
        self.start_time = None
        self.logs = []
        self.current_targets = []

        self.divisions = {
            "divisi_1": {
                "id": "divisi_1",
                "name": "Divisi 1: Scout Swarm (Playwright Ingress)",
                "icon": "fa-satellite-dish",
                "status": "idle",
                "progress": 0,
                "current_task": "Menunggu perintah peluncuran swarm",
                "workers": {}
            },
            "divisi_2": {
                "id": "divisi_2",
                "name": "Divisi 2: Data Architect (Dual Artifact Separation)",
                "icon": "fa-cubes-stacked",
                "status": "idle",
                "progress": 0,
                "current_task": "Menunggu data mentah dari Divisi Scout",
                "items_processed": 0
            },
            "divisi_3": {
                "id": "divisi_3",
                "name": "Divisi 3: Visionary Scanner (Gemini 3.8 Flash)",
                "icon": "fa-eye",
                "status": "idle",
                "progress": 0,
                "current_task": "Menunggu gambar untuk ditranskripsi via Gemini 3.8 Flash",
                "images_scanned": 0
            },
            "divisi_4": {
                "id": "divisi_4",
                "name": "Divisi 4: Reasoning Engine (Gemini 3.8 Flash)",
                "icon": "fa-brain",
                "status": "idle",
                "progress": 0,
                "current_task": "Menunggu data kanonis untuk pemecahan 5 Pilar & Soal Serupa",
                "prompts_generated": 0
            },
            "divisi_5": {
                "id": "divisi_5",
                "name": "Divisi 5: Zero-Trust Quality Auditor & Release",
                "icon": "fa-shield-halved",
                "status": "idle",
                "progress": 0,
                "current_task": "Standby validasi 9 checklist & hot-reload registry",
                "keys_verified": 0
            }
        }

        self.stats = {
            "total_questions_scraped": 0,
            "total_images_saved": 0,
            "total_solutions_ready": 0,
            "active_targets_count": 0,
            "active_agents": 5
        }

    def log(self, agent_tag, message, level="info"):
        timestamp = time.strftime("%H:%M:%S")
        entry = {
            "time": timestamp,
            "tag": agent_tag,
            "message": message,
            "level": level
        }
        with self.lock:
            self.logs.append(entry)
            if len(self.logs) > 400:
                self.logs.pop(0)

    def get_status(self):
        with self.lock:
            elapsed = 0
            if self.start_time:
                elapsed = int(time.time() - self.start_time)
            return {
                "is_running": self.is_running,
                "elapsed_seconds": elapsed,
                "divisions": self.divisions,
                "stats": self.stats,
                "current_targets": self.current_targets,
                "logs": self.logs[-50:]
            }

    def reset(self):
        with self.lock:
            self.is_running = False
            self.start_time = None
            for d in self.divisions.values():
                d["status"] = "idle"
                d["progress"] = 0
            self.divisions["divisi_1"]["workers"] = {}
        self.log("ORCHESTRATOR", "Status Multi-Agent Swarm direset ke kondisi awal.", "warning")

    def start_swarm_pipeline(self, targets=None):
        with self.lock:
            if self.is_running:
                return False, "Swarm sedang berjalan!"
            self.is_running = True
            self.start_time = time.time()

        # Parse & normalize targets
        target_objs = []
        if targets and isinstance(targets, list):
            for t in targets:
                if isinstance(t, str) and t in MASTER_CATALOG:
                    target_objs.append(dict(MASTER_CATALOG[t]))
                elif isinstance(t, dict) and "slug" in t:
                    slug = t["slug"]
                    info = dict(MASTER_CATALOG.get(slug, t))
                    info.update(t)
                    target_objs.append(info)
        
        # If no valid targets provided, default to unscraped subjects
        if not target_objs:
            unscraped = get_unscraped_subjects()
            target_objs = list(unscraped.values())[:2] # Default first 2 unscraped packages

        self.current_targets = [t["slug"] for t in target_objs]
        self.stats["active_targets_count"] = len(target_objs)

        # Setup sub-workers in Divisi 1
        with self.lock:
            workers = {}
            for idx, t in enumerate(target_objs):
                w_id = f"worker_{t['slug']}"
                workers[w_id] = {
                    "name": f"{t['name']} (ID: {t['val']})",
                    "status": "idle",
                    "progress": 0,
                    "details": "Standby Ingress"
                }
            self.divisions["divisi_1"]["workers"] = workers

        target_names = ", ".join([t["name"] for t in target_objs])
        self.log("ORCHESTRATOR", f"🚀 MEMULAI MISI SWARM: {len(target_objs)} Paket Target Dikonfigurasi [{target_names}]!", "success")
        self.log("ORCHESTRATOR", f"⚡ Model AI Eksklusif: Google Gemini 3.8 Flash (Vision & Reasoning)", "info")

        threading.Thread(target=self._run_swarm_thread, args=(target_objs,), daemon=True).start()
        return True, f"Swarm diluncurkan untuk {len(target_objs)} paket!"

    def _run_swarm_thread(self, target_objs):
        try:
            # Fase 1: Scout Swarm
            self._execute_divisi_1_scout_swarm(target_objs)

            # Fase 2: Data Architect
            self._execute_divisi_2_architect(target_objs)

            # Fase 3: Visionary Scanner (Gemini 3.8 Flash)
            self._execute_divisi_3_visionary(target_objs)

            # Fase 4: Reasoning Engine (Gemini 3.8 Flash)
            self._execute_divisi_4_reasoning(target_objs)

            # Fase 5: Zero-Trust Quality Auditor & Release
            self._execute_divisi_5_auditor(target_objs)

            with self.lock:
                self.is_running = False
            self.log("ORCHESTRATOR", "🎉 SIKLUS SWARM TUNTAS 100%! Seluruh materi live di CBT App.", "success")

        except Exception as e:
            with self.lock:
                self.is_running = False
            self.log("ORCHESTRATOR", f"❌ Terjadi kegagalan siklus: {str(e)}", "error")

    # =========================================================================
    # FASE 1: SCOUT SWARM (PLAYWRIGHT INGRESS)
    # =========================================================================
    def _execute_divisi_1_scout_swarm(self, targets):
        with self.lock:
            d1 = self.divisions["divisi_1"]
            d1["status"] = "active"
            d1["current_task"] = f"Scout Swarm menginfiltrasi {len(targets)} paket secara paralel/sekuensial..."
            d1["progress"] = 10

        self.log("SCOUT_DIR", f"Memulai Ingress untuk {len(targets)} target ke portal Pusmendik.", "info")

        # Execute targets sequentially to ensure rock-solid session handling
        for idx, t in enumerate(targets, 1):
            self._scrape_target(t)
            with self.lock:
                d1["progress"] = int((idx / len(targets)) * 100)

        with self.lock:
            d1["status"] = "success"
            d1["progress"] = 100
            d1["current_task"] = f"Seluruh {len(targets)} target berhasil di-scrape lengkap dengan kunci resmi!"
        self.log("SCOUT_DIR", "✅ Fase 1 Ingress tuntas 100%!", "success")

    def _scrape_target(self, t):
        slug = t["slug"]
        w_id = f"worker_{slug}"
        name = t["name"]
        mapel_key = t["mapel_key"]
        paket = t["paket"]
        jenis = t["jenis"]
        val = t["val"]

        images_dir = os.path.join(DATA_DIR, mapel_key, f"paket_{paket}", "images")
        os.makedirs(images_dir, exist_ok=True)
        kunci_out = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
        raw_html_out = os.path.join(RAW_DIR, f"{slug}.html")

        # Smart Cache Check
        if os.path.isfile(raw_html_out) and os.path.isfile(kunci_out) and os.path.getsize(raw_html_out) > 5000:
            self._update_worker(w_id, "success", 100, "Cache valid (Data & Aset Lengkap)")
            self.log(w_id.upper(), f"[{name}] Cache Hit lokal valid. Melewati scraping ulang.", "info")
            return

        self._update_worker(w_id, "active", 15, "Menghubungkan ke Pusmendik...")
        self.log(w_id.upper(), f"[{name}] Memulai sesi Playwright (Val ID: {val}, Jenis: {jenis})...", "info")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                # 1. Navigasi & Login Form
                page.goto(SIMULASI_URL, timeout=45000)
                page.wait_for_timeout(2000)

                # Select Jenjang & Jenis Mapel
                page.select_option("#jenjang", "sma")
                page.wait_for_timeout(800)
                page.select_option("#jenis_mapel", str(jenis))
                page.wait_for_timeout(1500)

                # Open Mapel dropdown
                page.click("#mapel_toggle")
                page.wait_for_timeout(1000)
                opt_loc = page.locator(f".mapel-option[data-value='{val}']")
                if opt_loc.count() > 0:
                    opt_loc.first.scroll_into_view_if_needed()
                    page.wait_for_timeout(400)
                    opt_loc.first.click()
                else:
                    page.evaluate(f"""() => {{
                        const el = document.querySelector('.mapel-option[data-value="{val}"]');
                        if (el) {{
                            el.scrollIntoView();
                            el.click();
                        }} else {{
                            const m = document.querySelector('#mapel');
                            if (m) m.value = '{val}';
                        }}
                    }}""")
                page.wait_for_timeout(800)

                # 2. Login Demo Pusmendik
                self._update_worker(w_id, "active", 25, "Menuju halaman login...")
                page.click("button.custom-btn")
                page.wait_for_url(lambda u: "login" in u or "simulasi" in u, timeout=25000)
                page.click("button:has-text('Login')")
                page.wait_for_url(lambda u: "konfirmasi_data" in u, timeout=25000)

                # Tutup modal alert jika ada
                try:
                    close_btn = page.locator(".modal.show .close, .swal2-close, button:has-text('Tutup')")
                    if close_btn.count() > 0 and close_btn.first.is_visible():
                        close_btn.first.click()
                        time.sleep(1)
                except Exception:
                    pass

                # 3. Refresh Token & Isi Form
                self._update_worker(w_id, "active", 35, "Merefresh token & mengisi formulir siswa...")
                page.locator("button:has-text('Refresh')").first.click()
                time.sleep(1.5)
                body_text = page.inner_text("body")
                m = re.search(r"Token\s*[:=]\s*([A-Z0-9]{6})", body_text, re.I)
                if not m:
                    raise RuntimeError("Gagal menemukan token 6 karakter di halaman konfirmasi data!")
                token = m.group(1).upper()

                page.fill("#nama_peserta", f"PESERTA {slug.upper()}")
                page.select_option("#tgl", "01")
                page.eval_on_selector("#bulan", "el => { el.selectedIndex = 1; el.dispatchEvent(new Event('change', {bubbles:true})); }")
                page.select_option("#tahun", "2005")
                page.fill("#input-token", token)
                time.sleep(1)

                page.locator("#btnSubmit").first.click()
                page.wait_for_url(lambda u: "konfirmasi_tes" in u, timeout=25000)
                page.click("button:has-text('Mulai')")

                # 4. Di Bilik Ujian - Ekstraksi Soal & Media
                self._update_worker(w_id, "active", 50, "Masuk ke bilik ujian... Menunggu elemen termuat...")
                page.wait_for_selector("#nextSoal", timeout=35000)
                page.wait_for_function("typeof window.lihatSoal === 'function' && typeof window.jumlah_soal !== 'undefined'", timeout=25000)
                time.sleep(2)

                total_soal = page.evaluate("() => window.jumlah_soal")
                self.log(w_id.upper(), f"[{name}] Bilik ujian aktif: terdeteksi {total_soal} butir soal.", "info")

                html_exam = page.content()
                with open(raw_html_out, "w", encoding="utf-8") as f:
                    f.write(html_exam)

                # 5. Panen Kunci Otoritatif Pusmendik
                self._update_worker(w_id, "active", 75, "Melompat ke nomor terakhir & memanen review_hasil...")
                page.evaluate(f"() => window.lihatSoal({total_soal})")
                time.sleep(1.5)

                inp = page.locator(f"#soal-no-{total_soal} input[type=radio], #soal-no-{total_soal} input[type=checkbox]")
                if inp.count() > 0:
                    inp.first.click(force=True)
                    time.sleep(1)

                page.click("#nextSoal")
                page.wait_for_url(lambda u: "finish_tes" in u, timeout=25000)
                time.sleep(1.5)

                btn_selesai = page.locator("button", has_text="SELESAI TES").first
                btn_selesai.click()
                page.wait_for_url(lambda u: "review_hasil" in u, timeout=35000)
                time.sleep(2)

                kunci_html = page.content()
                review_html_out = os.path.join(RAW_DIR, f"{slug}_review.html")
                with open(review_html_out, "w", encoding="utf-8") as f:
                    f.write(kunci_html)

                kunci_data = self._parse_review_kunci(kunci_html, slug, val)
                has_parsed_data = bool(kunci_data.get("kunci_pg") or kunci_data.get("kunci_bs") or kunci_data.get("raw_rows"))
                has_existing_valid = False
                if os.path.isfile(kunci_out):
                    try:
                        with open(kunci_out, "r", encoding="utf-8") as ef:
                            old_d = json.load(ef)
                        has_existing_valid = bool(old_d.get("kunci_pg") or old_d.get("kunci_bs"))
                    except Exception:
                        pass

                if has_parsed_data or not has_existing_valid:
                    with open(kunci_out, "w", encoding="utf-8") as f:
                        json.dump(kunci_data, f, indent=2, ensure_ascii=False)

                # Download images
                soup = BeautifulSoup(html_exam, "html.parser")
                imgs = soup.find_all("img")
                saved_imgs = 0
                for img in imgs:
                    src = img.get("src")
                    if src and not src.startswith("data:"):
                        fname = os.path.basename(src.split("?")[0])
                        dest = os.path.join(images_dir, fname)
                        if self._download_file(src, dest):
                            saved_imgs += 1

                with self.lock:
                    self.stats["total_images_saved"] += saved_imgs

                self._update_worker(w_id, "success", 100, f"Selesai! {len(kunci_data.get('raw_rows', {}))} soal & kunci resmi tersimpan.")
                self.log(w_id.upper(), f"🎉 [{name}] Ingress sukses! {len(kunci_data.get('raw_rows', {}))} soal diserap.", "success")

            except Exception as ex:
                self._update_worker(w_id, "error", 0, f"Error: {str(ex)[:50]}")
                self.log(w_id.upper(), f"❌ [{name}] Error Playwright: {str(ex)}", "error")
            finally:
                browser.close()

    def _download_file(self, rel_or_abs_url, dest_path):
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            return True
        full_url = rel_or_abs_url if rel_or_abs_url.startswith("http") else f"{BASE_URL}{rel_or_abs_url}"
        try:
            req = urllib.request.Request(full_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    with open(dest_path, "wb") as f:
                        f.write(resp.read())
                    return True
        except Exception:
            return False
        return False

    def _parse_review_kunci(self, html, slug, val):
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr")
        kunci_pg = {}
        kunci_bs = {}
        raw_rows = {}

        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) >= 3:
                no_str = re.sub(r"\D", "", tds[0].get_text(strip=True))
                if not no_str:
                    continue
                no_txt = str(int(no_str))
                kunci_cell = tds[2].get_text("\n", strip=True) if len(tds) == 3 else tds[3].get_text("\n", strip=True)
                raw_rows[no_txt] = {"kunci": kunci_cell}

                # Guard misfire: deret "(C) Danau C (D) Danau D" adalah PG
                # multi-jawaban (kunci = huruf di kurung), BUKAN matriks
                # Benar-Salah — huruf terakhir teks opsi bisa tertangkap
                # regex matriks sehingga kunci jadi {C:'D', D:'E'}.
                explicit_letters = re.findall(r"\(\s*([A-E])\s*\)", kunci_cell)
                label_pairs_strict = re.findall(
                    r"\([A-E]\)\s*(Tepat|Tidak Tepat|Sesuai|Tidak Sesuai|Benar|Salah)",
                    kunci_cell, re.I)
                if not label_pairs_strict and len(explicit_letters) >= 2:
                    kunci_pg[no_txt] = explicit_letters
                    continue

                matrix_pairs = re.findall(r"([A-E])\s*\(([^)]+)\)", kunci_cell)
                if len(matrix_pairs) >= 2:
                    kunci_bs[no_txt] = {k.upper(): CANONICAL_LABELS.get(v.strip().lower(), v.strip()) for k, v in matrix_pairs}
                else:
                    # Check for "A (Tepat)", "A (Benar)", "A (Sesuai)", etc.
                    m_pair_alt = re.findall(r"([A-E])\s*\((Tepat|Tidak Tepat|Sesuai|Tidak Sesuai|Benar|Salah)\)", kunci_cell, re.I)
                    if len(m_pair_alt) >= 1:
                        kunci_bs[no_txt] = {k.upper(): CANONICAL_LABELS.get(v.strip().lower(), v.strip()) for k, v in m_pair_alt}
                    elif any(w in kunci_cell for w in ["Benar", "Salah", "Tepat", "Sesuai"]):
                        bs_map = {}
                        for line in kunci_cell.split("\n"):
                            line = line.strip()
                            m = re.match(r"\(([A-E])\)\s*(Tepat|Tidak Tepat|Sesuai|Tidak Sesuai|Benar|Salah)", line, re.I)
                            if m:
                                bs_map[m.group(1).upper()] = CANONICAL_LABELS.get(m.group(2).strip().lower(), m.group(2).strip())
                        if bs_map:
                            kunci_bs[no_txt] = bs_map
                        else:
                            letters = re.findall(r"\(\s*([A-E])\s*\)", kunci_cell)
                            if letters:
                                kunci_pg[no_txt] = letters if len(letters) > 1 else letters[0]
                            else:
                                m_raw = re.findall(r"\b([A-E])\b", kunci_cell)
                                if m_raw:
                                    kunci_pg[no_txt] = m_raw if len(m_raw) > 1 else m_raw[0]
                    else:
                        letters = re.findall(r"\(\s*([A-E])\s*\)", kunci_cell)
                        if letters:
                            kunci_pg[no_txt] = letters if len(letters) > 1 else letters[0]
                        else:
                            m_raw = re.findall(r"\b([A-E])\b", kunci_cell)
                            if m_raw:
                                kunci_pg[no_txt] = m_raw if len(m_raw) > 1 else m_raw[0]

        return {
            "slug": slug,
            "mapel_id": val,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kunci_pg": kunci_pg,
            "kunci_bs": kunci_bs,
            "raw_rows": raw_rows
        }

    def _update_worker(self, worker_id, status, progress, details):
        with self.lock:
            w = self.divisions["divisi_1"]["workers"].get(worker_id)
            if w:
                w["status"] = status
                w["progress"] = progress
                w["details"] = details

    @staticmethod
    def _extract_block_text(el):
        """Teks blok soal yang aman terhadap tag inline (em/sup/sub/span).

        get_text("\\n") memecah rumus per karakter pada setiap batas tag inline
        (bug "pembahasan aneh": "f\\n(\\nx\\n)"). Ekstraksi ini menandai <br> dan
        tag blok sebagai baris baru, memakai pemisah spasi, lalu menormalkan
        hasilnya via text_quality.repair_math_text.
        """
        if el is None:
            return ""
        work = BeautifulSoup(str(el), "html.parser")
        for br in work.find_all("br"):
            br.replace_with("\n")
        for tag in work.find_all(["p", "div", "tr", "li", "table",
                                  "h1", "h2", "h3", "h4", "h5", "h6"]):
            tag.insert_before("\n")
            tag.insert_after("\n")
        raw = work.get_text(" ")
        raw = re.sub(r" *\n *", "\n", raw)
        return text_quality.repair_math_text(raw)

    def _load_or_reconstruct_kunci(self, slug, kunci_path=None):
        if kunci_path and os.path.isfile(kunci_path):
            try:
                with open(kunci_path, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                if doc.get("kunci_pg") or doc.get("kunci_bs"):
                    return doc
            except Exception:
                pass

        sol_file = None
        if os.path.isfile(REG_PATH):
            try:
                with open(REG_PATH, "r", encoding="utf-8") as f:
                    reg = json.load(f)
                if slug in reg and "active_source" in reg[slug]:
                    candidate = os.path.join(SOL_DIR, reg[slug]["active_source"])
                    if os.path.isfile(candidate):
                        sol_file = candidate
            except Exception:
                pass

        if not sol_file:
            candidate = os.path.join(SOL_DIR, f"{slug.upper()}_SOLUTIONS.json")
            if os.path.isfile(candidate):
                sol_file = candidate

        if not sol_file and os.path.isdir(SOL_DIR):
            for fn in os.listdir(SOL_DIR):
                if fn.lower().startswith(slug.lower()) and fn.endswith(".json"):
                    sol_file = os.path.join(SOL_DIR, fn)
                    break

        if sol_file and os.path.isfile(sol_file):
            try:
                with open(sol_file, "r", encoding="utf-8") as f:
                    sol_data = json.load(f)
                kunci_pg = {}
                kunci_bs = {}
                raw_rows = {}
                for s in sol_data.get("solutions", []):
                    q_num = str(s.get("question_number", 0))
                    oa = s.get("official_answer")
                    if not oa or not isinstance(oa, dict):
                        continue
                    fmt = oa.get("format", "")
                    corr = oa.get("correct")
                    if fmt in ("per_statement_benar_salah", "per_statement") or isinstance(corr, dict) or (isinstance(corr, list) and any(":" in str(x) for x in corr)):
                        bs_dict = {}
                        if isinstance(corr, list):
                            for item in corr:
                                if ":" in str(item):
                                    k, v = str(item).split(":", 1)
                                    bs_dict[k.strip().upper()] = CANONICAL_LABELS.get(v.strip().lower(), v.strip())
                        elif isinstance(corr, dict):
                            bs_dict = {k.strip().upper(): CANONICAL_LABELS.get(str(v).strip().lower(), str(v).strip()) for k, v in corr.items()}
                        if bs_dict:
                            kunci_bs[q_num] = bs_dict
                            raw_rows[q_num] = {"kunci": "\n".join(f"{k} ({v})" for k, v in bs_dict.items())}
                    elif fmt in ("multiple_correct", "multiple") or isinstance(corr, list):
                        arr = [str(x).strip().upper() for x in corr]
                        kunci_pg[q_num] = arr
                        raw_rows[q_num] = {"kunci": "\n".join(f"({x})" for x in arr)}
                    elif corr is not None:
                        c_str = str(corr).strip().upper()
                        kunci_pg[q_num] = c_str
                        raw_rows[q_num] = {"kunci": f"({c_str})"}

                doc = {
                    "slug": slug,
                    "mapel_id": "auto_restored",
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "kunci_pg": kunci_pg,
                    "kunci_bs": kunci_bs,
                    "raw_rows": raw_rows
                }
                if kunci_path:
                    with open(kunci_path, "w", encoding="utf-8") as f:
                        json.dump(doc, f, indent=2, ensure_ascii=False)
                self.log("ARCHITECT", f"♻️ Kunci {slug} otomatis direkonstruksi dari {os.path.basename(sol_file)}", "info")
                return doc
            except Exception as e:
                self.log("ARCHITECT", f"Gagal rekonstruksi kunci dari solusi: {e}", "warning")

        return {"slug": slug, "kunci_pg": {}, "kunci_bs": {}, "raw_rows": {}}

    # =========================================================================
    # FASE 2: DATA ARCHITECT (DUAL ARTIFACT SEPARATION)
    # =========================================================================
    def _execute_divisi_2_architect(self, targets):
        with self.lock:
            d2 = self.divisions["divisi_2"]
            d2["status"] = "active"
            d2["progress"] = 25
            d2["current_task"] = "Membangun Dual-Artifact (Tipe A Visual & Tipe B Text-Only)..."

        self.log("ARCHITECT", "Memulai parsing tabel & pemisahan artefak Tipe A (CBT) dan Tipe B (AI).", "info")

        for idx, t in enumerate(targets, 1):
            slug = t["slug"]
            mapel_key = t["mapel_key"]
            paket = t["paket"]
            raw_html_out = os.path.join(RAW_DIR, f"{slug}.html")
            kunci_out = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
            lrn_out = os.path.join(DATA_DIR, f"{slug}_learning.json")
            txt_out = os.path.join(DATA_DIR, f"{slug}_text_only.json")

            if not os.path.isfile(raw_html_out):
                continue

            with open(raw_html_out, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            kunci_doc = self._load_or_reconstruct_kunci(slug, kunci_out)

            soal_divs = soup.find_all("div", class_="soal-soal")
            tipe_a_questions = []
            tipe_b_questions = []

            # Preservasi soal_serupa dari learning JSON lama — re-scrape tidak
            # boleh menghancurkan soal serupa yang sudah ada (fase 4 yang
            # memutuskan pembuatannya ulang bila memang kosong).
            old_lrn_path = lrn_out
            old_serupa = {}
            if os.path.isfile(old_lrn_path):
                try:
                    with open(old_lrn_path, "r", encoding="utf-8") as f:
                        for _q in json.load(f).get("soal", []):
                            if _q.get("soal_serupa") and _q.get("nomor"):
                                old_serupa[_q["nomor"]] = _q["soal_serupa"]
                except Exception:
                    old_serupa = {}

            for q_idx, s in enumerate(soal_divs, start=1):
                cont = s.find("div", class_="cont-soal")
                isi = s.find("div", class_="isi-soal")
                isi_copy = BeautifulSoup(str(isi), "html.parser").find("div", class_="isi-soal") if isi else None

                # Isolate interactive table with input vs clinical data table
                interactive_table = None
                if isi_copy:
                    for tbl in isi_copy.find_all("table"):
                        if tbl.find("input"):
                            interactive_table = tbl
                            break

                # Extract options
                options = []
                pernyataan = []
                tipe_soal = "Pilihan Ganda"

                raw_rows = kunci_doc.get("raw_rows", {})
                kunci_raw = raw_rows.get(str(q_idx), {}).get("kunci", "")
                kunci_jawaban = kunci_doc.get("kunci_pg", {}).get(str(q_idx))

                # Check if it has interactive table
                if interactive_table:
                    inputs = interactive_table.find_all("input")
                    unique_names = set(inp.get("name", "") for inp in inputs if inp.get("name"))
                    has_checkbox = any(inp.get("type") == "checkbox" for inp in inputs)

                    # If multiple group names -> Benar-Salah / Matriks
                    if len(unique_names) > 1:
                        tipe_soal = "Benar-Salah"
                        table_headers = []
                        for tr in interactive_table.find_all("tr"):
                            tds = tr.find_all("td")
                            if len(tds) >= 2:
                                tr_inputs = tr.find_all("input")
                                key_td = tds[0].get_text(strip=True).replace(".", "").strip()
                                # If header row (no inputs) -> extract option column names (e.g. Tepat, Tidak Tepat)
                                if not tr_inputs or key_td == "#":
                                    if len(tds) > 2 and not table_headers:
                                        table_headers = [td.get_text(strip=True) for td in tds[2:] if td.get_text(strip=True)]
                                    continue

                                txt_td = tds[1].get_text(" ", strip=True)
                                st_img = tds[1].find("img")
                                st_img_obj = None
                                if st_img and st_img.get("src"):
                                    src = st_img.get("src")
                                    fn = os.path.basename(src.split("?")[0])
                                    st_img_obj = {"filename": fn, "rel_path": f"images/{fn}"}
                                if (txt_td or st_img_obj) and not any(h in (txt_td or "").lower() for h in ["kondisi", "pernyataan", "besaran"]):
                                    pernyataan.append({
                                        "key": key_td or f"P{len(pernyataan)+1}",
                                        "text": txt_td,
                                        "image": st_img_obj
                                    })
                        kunci_jawaban = [f"{k}:{v}" for k, v in sorted(kunci_doc.get("kunci_bs", {}).get(str(q_idx), {}).items())]
                    else:
                        table_headers = []
                        # Single radio group or checkbox list -> Pilihan Ganda / Pilihan Ganda Kompleks
                        if has_checkbox or (isinstance(kunci_jawaban, list) and all(len(k) == 1 and k.isupper() for k in kunci_jawaban)):
                            tipe_soal = "Pilihan Ganda Kompleks"
                            if isinstance(kunci_jawaban, str):
                                kunci_jawaban = [kunci_jawaban]
                            elif not kunci_jawaban:
                                kunci_jawaban = []
                        else:
                            tipe_soal = "Pilihan Ganda"

                        opt_keys = ["A", "B", "C", "D", "E"]
                        for tr_idx, tr in enumerate(interactive_table.find_all("tr")):
                            tds = tr.find_all("td")
                            if tds:
                                content_td = tds[-1]
                                txt = content_td.get_text(" ", strip=True)
                                math_img = content_td.find("img")
                                opt_img_obj = None
                                opt_latex = None
                                if math_img:
                                    src = math_img.get("src", "")
                                    fn = os.path.basename(src.split("?")[0])
                                    opt_img_obj = {"filename": fn, "rel_path": f"images/{fn}"}
                                    opt_latex = math_img.get("data-latex")

                                if txt or opt_img_obj:
                                    k_name = opt_keys[len(options)] if len(options) < len(opt_keys) else chr(65 + len(options))
                                    full_disp = f"{k_name}. {txt}" if txt else f"{k_name}."
                                    options.append({
                                        "key": k_name,
                                        "text": txt,
                                        "latex": opt_latex,
                                        "image": opt_img_obj,
                                        "full_display": full_disp
                                    })

                    interactive_table.decompose()

                # Fallback to standard labels if options still empty
                if not options and not pernyataan and isi_copy:
                    labels = isi_copy.find_all("label")
                    opt_keys = ["A", "B", "C", "D", "E"]
                    for l_idx, lbl in enumerate(labels):
                        txt = lbl.get_text(" ", strip=True)
                        math_img = lbl.find("img")
                        opt_img_obj = None
                        opt_latex = None
                        if math_img:
                            src = math_img.get("src", "")
                            fn = os.path.basename(src.split("?")[0])
                            opt_img_obj = {"filename": fn, "rel_path": f"images/{fn}"}
                            opt_latex = math_img.get("data-latex")
                        if txt or opt_img_obj:
                            k_name = opt_keys[len(options)] if len(options) < len(opt_keys) else chr(65 + len(options))
                            full_disp = f"{k_name}. {txt}" if txt else f"{k_name}."
                            options.append({
                                "key": k_name,
                                "text": txt,
                                "latex": opt_latex,
                                "image": opt_img_obj,
                                "full_display": full_disp
                            })

                # Final kunci determination — TANPA karangan: kunci yang tidak
                # ditemukan dibiarkan kosong agar auditor menandainya (fase 5),
                # bukan diisi 'A' diam-diam yang membuat penilaian salah.
                final_kunci = kunci_jawaban
                if final_kunci is None or (isinstance(final_kunci, list) and len(final_kunci) == 0):
                    self.log("ARCHITECT",
                             f"⚠️ Kunci {tipe_soal} tidak ditemukan untuk {slug} soal {q_idx} — ditandai untuk auditor",
                             "warning")
                    final_kunci = []

                # Tipe A (Visual CBT): keep original HTML & img tags intact
                q_a = {
                    "nomor": q_idx,
                    "id": f"{slug}_q{q_idx:02d}",
                    "tipe": tipe_soal,
                    "tipe_soal": tipe_soal,
                    "kunci_jawaban": final_kunci,
                    "table_headers": table_headers if "table_headers" in locals() else [],
                    "stimulus": {
                        "text": self._extract_block_text(cont),
                        "html": str(cont) if cont else "",
                        "images": [{"filename": os.path.basename(img.get("src", "").split("?")[0])} for img in (cont.find_all("img") if cont else []) if img.get("src")]
                    },
                    "pertanyaan": {
                        "text": self._extract_block_text(isi_copy),
                        "html": str(isi_copy) if isi_copy else "",
                        "images": [{"filename": os.path.basename(img.get("src", "").split("?")[0])} for img in (isi_copy.find_all("img") if isi_copy else []) if img.get("src")]
                    },
                    "pilihan_jawaban": options,
                    "pernyataan": pernyataan
                }
                tipe_a_questions.append(q_a)

                # Tipe B (Text-Only for AI Reasoning)
                q_b = {
                    "nomor": q_idx,
                    "id": f"{slug}_q{q_idx:02d}",
                    "tipe": tipe_soal,
                    "tipe_soal": tipe_soal,
                    "kunci_jawaban": final_kunci,
                    "table_headers": table_headers if "table_headers" in locals() else [],
                    "stimulus_text": self._extract_block_text(cont),
                    "pertanyaan_text": self._extract_block_text(isi_copy),
                    "options": options,
                    "pernyataan": pernyataan
                }
                if q_idx in old_serupa:
                    q_a["soal_serupa"] = old_serupa[q_idx]
                    q_b["soal_serupa"] = old_serupa[q_idx]
                tipe_b_questions.append(q_b)

            with open(lrn_out, "w", encoding="utf-8") as f:
                json.dump({"slug": slug, "name": t["name"], "total_soal": len(tipe_a_questions), "soal": tipe_a_questions}, f, indent=2, ensure_ascii=False)

            with open(txt_out, "w", encoding="utf-8") as f:
                json.dump({"slug": slug, "name": t["name"], "total_soal": len(tipe_b_questions), "soal": tipe_b_questions}, f, indent=2, ensure_ascii=False)

            with self.lock:
                self.stats["total_questions_scraped"] += len(tipe_a_questions)
                d2["items_processed"] += len(tipe_a_questions)
                d2["progress"] = int((idx / len(targets)) * 100)

        with self.lock:
            d2["status"] = "success"
            d2["progress"] = 100
            d2["current_task"] = "Dual-Artifact Tipe A (CBT Visual) & Tipe B (AI Context) berhasil dipisahkan!"
        self.log("ARCHITECT", "✅ Fase 2 Architect selesai: Tipe A & Tipe B siap.", "success")

    # =========================================================================
    # FASE 3: VISIONARY SCANNER (GEMINI 3.8 FLASH MULTIMODAL)
    # =========================================================================
    def _execute_divisi_3_visionary(self, targets, engine_mode="auto"):
        with self.lock:
            d3 = self.divisions["divisi_3"]
            d3["status"] = "active"
            d3["progress"] = 30
            d3["current_task"] = "Memindai diagram & formula matematika/kimia..."

        self.log("VISIONARY", "Memulai Transkripsi Multimodal Vision.", "info")

        import importlib
        import pipeline.playwright_aistudio_bridge
        importlib.reload(pipeline.playwright_aistudio_bridge)
        from pipeline.playwright_aistudio_bridge import (
            check_port_open, ensure_chrome_debug_open, run_phase_3_via_playwright)

        # Prioritas utama: AI Studio Playground via Playwright — vision GRATIS
        # tanpa kuota API (jalur Pendekatan B). engine_mode='api' memaksa jalur API.
        ai_studio_ok = False
        if engine_mode in ("auto", "playwright"):
            try:
                port_open = check_port_open(9222) or ensure_chrome_debug_open(9222)
                if port_open:
                    self.log("VISIONARY",
                             "🌐 Chrome AI Studio tersedia — transkripsi vision via "
                             "Playground (gratis, tanpa kuota API).", "success")
                    ai_studio_ok = True
                    for t in targets:
                        try:
                            n = run_phase_3_via_playwright(t["slug"], port=9222)
                            with self.lock:
                                d3["images_scanned"] += n
                        except Exception as e:
                            ai_studio_ok = False
                            self.log("VISIONARY",
                                     f"[{t['slug']}] Jalur AI Studio gagal: {str(e)[:80]} — "
                                     f"fallback ke API Gemini.", "warning")
                            break
                else:
                    self.log("VISIONARY",
                             "Port 9222 tidak tersedia — transkripsi vision via API Gemini.",
                             "info")
            except Exception as e:
                ai_studio_ok = False
                self.log("VISIONARY",
                         f"Bridge AI Studio error: {str(e)[:80]} — fallback ke API Gemini.",
                         "warning")

        if ai_studio_ok:
            with self.lock:
                d3["status"] = "success"
                d3["progress"] = 100
                d3["current_task"] = "Seluruh diagram & formula ditranskripsikan via AI Studio Playground!"
            self.log("VISIONARY", "✅ Fase 3 Visionary selesai (jalur AI Studio).", "success")
            return

        # Jalur cadangan: API Gemini dengan rotasi kunci (inkremental — hanya
        # gambar yang belum tertranskripsi).
        for idx, t in enumerate(targets, 1):
            slug = t["slug"]
            mapel_key = t["mapel_key"]
            paket = t["paket"]
            img_dir = os.path.join(DATA_DIR, mapel_key, f"paket_{paket}", "images")
            sidecar_path = os.path.join(DATA_DIR, f"{slug}_sidecar_transcriptions.json")

            if not os.path.isdir(img_dir):
                continue

            existing_sidecar = {}
            if os.path.isfile(sidecar_path):
                try:
                    with open(sidecar_path, "r", encoding="utf-8") as f:
                        existing_sidecar = json.load(f)
                except Exception:
                    pass

            img_files = [f for f in os.listdir(img_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            # Saring chrome portal: logo, loader, ikon kecil — bukan konten soal,
            # transkripsi hanya membuang kuota vision.
            def _is_portal_chrome(fn):
                low = fn.lower()
                if any(k in low for k in ("logo", "loader", "icon", "favicon", "spinner")):
                    return True
                try:
                    return os.path.getsize(os.path.join(img_dir, fn)) < 2048
                except OSError:
                    return False
            img_files = [f for f in img_files if not _is_portal_chrome(f)]
            new_transcriptions = dict(existing_sidecar)

            for img_name in img_files:
                if img_name in new_transcriptions:
                    continue

                img_path = os.path.join(img_dir, img_name)
                prompt = (
                    "Kamu adalah Vision OCR Specialist untuk Soal Sains TKA SMA Kemdikbud. "
                    "Analisis gambar ini dengan sangat teliti:\n"
                    "1. Jika gambar memuat rumus matematika/fisika/kimia, transkripsikan ke format LaTeX ($...$ atau $$...$$).\n"
                    "2. Jika gambar adalah diagram struktur, anatomi, atau silsilah genetik, jabarkan bagian-bagian pentingnya secara deskriptif dan akurat.\n"
                    "3. Jika gambar adalah grafik/tabel data, ekstrak nilai titik koordinat atau isi tabel ke markdown table.\n"
                    "Berikan hasil transkripsi ringkas, padat, dan ilmiah tanpa basa-basi."
                )

                try:
                    self.log("VISIONARY", f"Gemini 3.8 Flash memproses citra: {img_name}...", "info")
                    reply, model_used = tutor_llm._post_gemini(
                        messages=[{"role": "user", "content": prompt}],
                        model_choice="gemini-3.8-flash",
                        image_paths=[img_path],
                        temperature=0.2,
                        max_tokens=1024,
                        timeout=45
                    )
                    new_transcriptions[img_name] = {
                        "filename": img_name,
                        "description": reply.strip(),
                        "model": model_used
                    }
                    with self.lock:
                        d3["images_scanned"] += 1
                except Exception as ex:
                    self.log("VISIONARY", f"Warning: Transkripsi {img_name} gagal: {str(ex)[:60]}", "warning")

            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(new_transcriptions, f, indent=2, ensure_ascii=False)

            with self.lock:
                d3["progress"] = int((idx / len(targets)) * 100)

        with self.lock:
            d3["status"] = "success"
            d3["progress"] = 100
            d3["current_task"] = "Seluruh diagram & formula berhasil ditranskripsikan ke sidecar via Gemini 3.8 Flash!"
        self.log("VISIONARY", "✅ Fase 3 Visionary selesai.", "success")

    # =========================================================================
    # FASE 4: REASONING ENGINE (GEMINI 3.8 FLASH 5 PILAR + SOAL SERUPA)
    # =========================================================================
    def _execute_divisi_4_reasoning(self, targets, engine_mode="auto"):
        with self.lock:
            d4 = self.divisions["divisi_4"]
            d4["status"] = "active"
            d4["progress"] = 35
            d4["current_task"] = "Memecahkan Solusi 5 Pilar & Soal Serupa..."

        import importlib
        import pipeline.playwright_aistudio_bridge
        importlib.reload(pipeline.playwright_aistudio_bridge)
        from pipeline.playwright_aistudio_bridge import check_port_open, ensure_chrome_debug_open, run_phase_4_via_playwright
        port_open = ensure_chrome_debug_open(9222)
        use_playwright = (engine_mode == "playwright") or (engine_mode == "auto" and port_open)

        if use_playwright and port_open:
            self.log("REASONER", "🌐 Terdeteksi Chrome Remote Debugging di port 9222! Menjalankan PENDEKATAN B (Google AI Studio PRO via Playwright).", "success")
            for idx, t in enumerate(targets, 1):
                slug = t["slug"]
                name = t["name"]
                try:
                    run_phase_4_via_playwright(slug=slug, port=9222)
                    with self.lock:
                        d4["progress"] = int((idx / len(targets)) * 100)
                except Exception as e:
                    self.log("REASONER", f"[{name}] Pendekatan B gagal: {e}. Beralih ke fallback API...", "warning")
                    # Fallback to direct API if Playwright bridge encounters error
                    self._execute_divisi_4_reasoning_api([t])
            with self.lock:
                d4["status"] = "success"
                d4["progress"] = 100
                d4["current_task"] = "Solusi 5 Pilar & Soal Serupa selesai dipecahkan via Google AI Studio PRO!"
            self.log("REASONER", "✅ Fase 4 Reasoning selesai 100% (Pendekatan B).", "success")
            return

        self.log("REASONER", "Menjalankan Gemini Flash Reasoning Engine (Pendekatan A: Mega-Batch API & Dual-Engine Fallback).", "info")
        self._execute_divisi_4_reasoning_api(targets)

    def _execute_divisi_4_reasoning_api(self, targets):
        d4 = self.divisions["divisi_4"]

        import tutor_llm

        def _llm_with_fallback(prompt, images, slug, temperature, max_tokens, timeout, name):
            """Panggil Gemini; bila gagal sementara (mis. 429), fallback ke Qwen/Groq.

            Fallback teks hanya diizinkan bila SELURUH gambar batch sudah
            terwakili transkripsi sidecar (fase 3) — sehingga kualitas jawaban
            tanpa gambar tetap terjamin. Return (teks, label_model).
            """
            try:
                return tutor_llm._post_gemini(
                    messages=[{"role": "user", "content": prompt}],
                    model_choice="gemini-3.7-flash", image_paths=images,
                    temperature=temperature, max_tokens=max_tokens, timeout=timeout)
            except tutor_llm.LLMError as e:
                if e.kind not in ("rate_limit", "timeout", "connection", "provider_error"):
                    raise
                sidecar = {}
                sc_path = os.path.join(DATA_DIR, f"{slug}_sidecar_transcriptions.json")
                if os.path.isfile(sc_path):
                    try:
                        with open(sc_path, "r", encoding="utf-8") as f:
                            sidecar = json.load(f)
                    except Exception:
                        sidecar = {}
                uncovered = [os.path.basename(p) for p in (images or [])
                             if os.path.basename(p) not in sidecar]
                if uncovered:
                    self.log("REASONER",
                             f"[{name}] Gemini {e.kind} & {len(uncovered)} gambar tanpa "
                             f"transkripsi — fallback teks dilewati", "warning")
                    raise
                self.log("REASONER",
                         f"[{name}] Gemini {e.kind} — fallback ke Qwen/Groq "
                         f"(teks murni, sidecar lengkap)", "warning")
                text, meta = tutor_llm.generate(
                    messages=[{"role": "user", "content": prompt}],
                    model="qwen-groq", temperature=temperature,
                    max_tokens=max_tokens, timeout=timeout, return_meta=True)
                return text, meta.get("model", "Qwen 2.5 27B")

        for idx, t in enumerate(targets, 1):
            slug = t["slug"]
            name = t["name"]
            paket = t["paket"]
            prefix = t.get("prefix", "soal")
            mapel_key = t["mapel_key"]

            lrn_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
            kunci_path = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
            sol_out = os.path.join(SOL_DIR, f"{slug.upper()}_SOLUTIONS.json")
            img_dir = os.path.join(DATA_DIR, mapel_key, f"paket_{paket}", "images")

            if not os.path.isfile(lrn_path) or not os.path.isfile(kunci_path):
                continue

            with open(lrn_path, "r", encoding="utf-8") as f:
                lrn_data = json.load(f)
            with open(kunci_path, "r", encoding="utf-8") as f:
                kunci_data = json.load(f)

            questions = lrn_data.get("soal", [])
            total_q = len(questions)

            # Map kunci
            kunci_map = {}
            for k, v in kunci_data.get("kunci_pg", {}).items():
                kunci_map[str(k)] = v
            for k, v in kunci_data.get("kunci_bs", {}).items():
                kunci_map[str(k)] = [f"{k_}:{v_}" for k_, v_ in sorted(v.items())]

            # -------------------------------------------------------------
            # 1. Generate 5-Pillar Solutions via Mega-Batch (Dual-Engine)
            # -------------------------------------------------------------
            existing_sols_map = {}
            if os.path.isfile(sol_out):
                try:
                    with open(sol_out, "r", encoding="utf-8") as f:
                        for s in json.load(f).get("solutions", []):
                            if s.get("question_number"):
                                existing_sols_map[s["question_number"]] = s
                except Exception:
                    pass

            if len(existing_sols_map) >= total_q:
                self.log("REASONER", f"[{name}] Seluruh {total_q} solusi 5 Pilar sudah lengkap di checkpoint.", "success")
            else:
                mega_batch_attempts = 0
                max_mega_attempts = 3

                while len(existing_sols_map) < total_q and mega_batch_attempts < max_mega_attempts:
                    mega_batch_attempts += 1
                    needed_questions = [q for q in questions if q["nomor"] not in existing_sols_map]
                    if not needed_questions:
                        break

                    q_start = needed_questions[0]["nomor"]
                    q_end = needed_questions[-1]["nomor"]
                    self.log("REASONER", f"[{name}] Memproses Solusi Mega-Batch ({len(needed_questions)} butir soal: Q{q_start}-Q{q_end}) via Flash Mega-Context...", "info")

                    sc_path = os.path.join(DATA_DIR, f"{slug}_sidecar_transcriptions.json")
                    sc_keys = set()
                    if os.path.isfile(sc_path):
                        try:
                            with open(sc_path, "r", encoding="utf-8") as sc_f:
                                sc_keys = set(json.load(sc_f).keys())
                        except Exception:
                            pass

                    batch_images = []
                    for q in needed_questions:
                        for im in q.get("stimulus", {}).get("images", []) + q.get("pertanyaan", {}).get("images", []):
                            fn = im.get("filename")
                            if fn and fn not in sc_keys:
                                loc = os.path.join(img_dir, fn)
                                if os.path.isfile(loc) and loc not in batch_images:
                                    batch_images.append(loc)

                    prompt = self._build_5pillar_prompt(name, needed_questions, kunci_map, slug=slug)

                    try:
                        reply, model_used = _llm_with_fallback(
                            prompt, batch_images, slug,
                            temperature=0.2, max_tokens=32768, timeout=240, name=name)
                        parsed = self._safe_parse_json(reply)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            for item in parsed:
                                no = item.get("question_number")
                                if not no:
                                    continue
                                item["question_id"] = f"{prefix}_p{paket}_q{no:02d}"
                                item["concept_kunci"] = item.get("concept_kunci") or item.get("concept_tags") or [name]
                                raw_k = kunci_map.get(str(no), "-")
                                if isinstance(raw_k, list):
                                    if raw_k and all(":" in str(x) for x in raw_k):
                                        item["official_answer"] = {"format": "per_statement_benar_salah", "correct": [str(x) for x in raw_k]}
                                    else:
                                        item["official_answer"] = {"format": "multiple_correct", "correct": [str(x) for x in raw_k]}
                                else:
                                    item["official_answer"] = {"format": "single_choice", "correct": str(raw_k)}

                                # Sanitasi otomatis kata 'transkrip' (Bug #8)
                                for fld in ("why_correct", "reasoning", "diketahui", "ditanyakan"):
                                    if item.get(fld):
                                        item[fld] = re.sub(r"\btranskrip(?:si)?\b", "kutipan", item[fld], flags=re.I)
                                for st in item.get("steps", []):
                                    if st.get("explanation"):
                                        st["explanation"] = re.sub(r"\btranskrip(?:si)?\b", "kutipan", st["explanation"], flags=re.I)
                                    if st.get("title"):
                                        st["title"] = re.sub(r"\btranskrip(?:si)?\b", "kutipan", st["title"], flags=re.I)

                                existing_sols_map[no] = item

                            all_solutions = [existing_sols_map[k] for k in sorted(existing_sols_map.keys())]
                            with open(sol_out, "w", encoding="utf-8") as f:
                                json.dump({"slug": slug, "solutions": all_solutions}, f, indent=2, ensure_ascii=False)
                            self.log("REASONER", f"[{name}] ✅ Mega-Batch berhasil ({len(parsed)} solusi didapat, total tersimpan: {len(all_solutions)}/{total_q}) oleh {model_used}.", "success")
                        else:
                            self.log("REASONER", f"[{name}] Respons Mega-Batch bukan JSON list valid, melakukan retry...", "warning")
                    except Exception as ex:
                        self.log("REASONER", f"[{name}] Mega-Batch attempt {mega_batch_attempts} terhenti: {str(ex)[:60]}. Menunggu 4s...", "warning")
                        time.sleep(4.0)

                # Fallback: jika masih ada soal tersisa, selesaikan dalam chunk 5 soal
                needed_questions = [q for q in questions if q["nomor"] not in existing_sols_map]
                if needed_questions:
                    self.log("REASONER", f"[{name}] Fallback sub-batch untuk {len(needed_questions)} soal tersisa...", "info")
                    sub_batches = [needed_questions[i:i + 5] for i in range(0, len(needed_questions), 5)]
                    for sub_idx, sub in enumerate(sub_batches, 1):
                        prompt = self._build_5pillar_prompt(name, sub, kunci_map, slug=slug)
                        try:
                            reply, model_used = _llm_with_fallback(
                                prompt, [], slug,
                                temperature=0.2, max_tokens=16384, timeout=120, name=name)
                            parsed = self._safe_parse_json(reply)
                            if isinstance(parsed, list):
                                for item in parsed:
                                    no = item.get("question_number")
                                    if no:
                                        item["question_id"] = f"{prefix}_p{paket}_q{no:02d}"
                                        item["concept_kunci"] = item.get("concept_kunci") or item.get("concept_tags") or [name]
                                        raw_k = kunci_map.get(str(no), "-")
                                        if isinstance(raw_k, list):
                                            item["official_answer"] = {"format": "per_statement_benar_salah", "correct": [str(x) for x in raw_k]}
                                        else:
                                            item["official_answer"] = {"format": "single_choice", "correct": str(raw_k)}
                                        for fld in ("why_correct", "reasoning", "diketahui", "ditanyakan"):
                                            if item.get(fld):
                                                item[fld] = re.sub(r"\btranskrip(?:si)?\b", "kutipan", item[fld], flags=re.I)
                                        for st in item.get("steps", []):
                                            if st.get("explanation"):
                                                st["explanation"] = re.sub(r"\btranskrip(?:si)?\b", "kutipan", st["explanation"], flags=re.I)
                                            if st.get("title"):
                                                st["title"] = re.sub(r"\btranskrip(?:si)?\b", "kutipan", st["title"], flags=re.I)
                                        existing_sols_map[no] = item

                                all_solutions = [existing_sols_map[k] for k in sorted(existing_sols_map.keys())]
                                with open(sol_out, "w", encoding="utf-8") as f:
                                    json.dump({"slug": slug, "solutions": all_solutions}, f, indent=2, ensure_ascii=False)
                        except Exception as e:
                            self.log("REASONER", f"[{name}] Sub-batch {sub_idx} error: {e}", "warning")

            all_solutions = [existing_sols_map[k] for k in sorted(existing_sols_map.keys())]
            with open(sol_out, "w", encoding="utf-8") as f:
                json.dump({"slug": slug, "solutions": all_solutions}, f, indent=2, ensure_ascii=False)

            # -------------------------------------------------------------
            # 2. Generate Soal Serupa via Mega-Batch
            # -------------------------------------------------------------
            missing_sim = [q for q in questions if not q.get("soal_serupa") or not q.get("soal_serupa", {}).get("pertanyaan")]
            if not missing_sim:
                self.log("REASONER", f"[{name}] Seluruh {total_q} Soal Serupa sudah terisi di learning doc.", "success")
            else:
                sim_attempts = 0
                max_sim_attempts = 3
                while any(not q.get("soal_serupa") or not q.get("soal_serupa", {}).get("pertanyaan") for q in questions) and sim_attempts < max_sim_attempts:
                    sim_attempts += 1
                    missing = [q for q in questions if not q.get("soal_serupa") or not q.get("soal_serupa", {}).get("pertanyaan")]
                    if not missing:
                        break

                    q_start = missing[0]["nomor"]
                    q_end = missing[-1]["nomor"]
                    self.log("REASONER", f"[{name}] Memproses Soal Serupa Mega-Batch ({len(missing)} butir soal: Q{q_start}-Q{q_end})...", "info")

                    prompt_serupa = self._build_soal_serupa_prompt(name, missing, slug=slug)
                    try:
                        reply, model_used = _llm_with_fallback(
                            prompt_serupa, [], slug,
                            temperature=0.3, max_tokens=24576, timeout=200, name=name)
                        parsed_s = self._safe_parse_json(reply)
                        if isinstance(parsed_s, list) and len(parsed_s) > 0:
                            s_map = {item.get("nomor_soal"): item.get("soal_serupa") for item in parsed_s if item.get("nomor_soal")}
                            for q in questions:
                                if q["nomor"] in s_map and s_map[q["nomor"]]:
                                    q["soal_serupa"] = s_map[q["nomor"]]
                            with open(lrn_path, "w", encoding="utf-8") as f:
                                json.dump(lrn_data, f, indent=2, ensure_ascii=False)
                            self.log("REASONER", f"[{name}] ✅ Soal Serupa Mega-Batch sukses ({len(s_map)} soal tersimpan) oleh {model_used}.", "success")
                    except Exception as ex:
                        self.log("REASONER", f"[{name}] Soal Serupa attempt {sim_attempts} terhenti: {str(ex)[:60]}. Menunggu 4s...", "warning")
                        time.sleep(4.0)

                # Fallback sub-batch untuk soal serupa jika ada yang terlewat
                still_missing = [q for q in questions if not q.get("soal_serupa") or not q.get("soal_serupa", {}).get("pertanyaan")]
                if still_missing:
                    self.log("REASONER", f"[{name}] Fallback sub-batch soal serupa untuk {len(still_missing)} butir...", "info")
                    sub_sims = [still_missing[i:i + 5] for i in range(0, len(still_missing), 5)]
                    for sub in sub_sims:
                        prompt_serupa = self._build_soal_serupa_prompt(name, sub, slug=slug)
                        try:
                            reply, _ = _llm_with_fallback(
                                prompt_serupa, [], slug,
                                temperature=0.3, max_tokens=8192, timeout=90, name=name)
                            parsed_s = self._safe_parse_json(reply)
                            if isinstance(parsed_s, list):
                                for item in parsed_s:
                                    no = item.get("nomor_soal")
                                    sim = item.get("soal_serupa")
                                    if no and sim:
                                        for q in questions:
                                            if q["nomor"] == no:
                                                q["soal_serupa"] = sim
                                with open(lrn_path, "w", encoding="utf-8") as f:
                                    json.dump(lrn_data, f, indent=2, ensure_ascii=False)
                        except Exception as e:
                            self.log("REASONER", f"[{name}] Sub-batch soal serupa error: {e}", "warning")

            with open(lrn_path, "w", encoding="utf-8") as f:
                json.dump(lrn_data, f, indent=2, ensure_ascii=False)

            # Register in registry.json
            try:
                reg = {}
                if os.path.isfile(REG_PATH):
                    with open(REG_PATH, "r", encoding="utf-8") as rf:
                        reg = json.load(rf)
                reg[slug] = {"active_source": f"{slug.upper()}_SOLUTIONS.json"}
                with open(REG_PATH, "w", encoding="utf-8") as wf:
                    json.dump(reg, wf, indent=2, ensure_ascii=False)
            except Exception as reg_err:
                self.log("REASONER", f"Peringatan registrasi registry.json: {reg_err}", "warning")

            with self.lock:
                self.stats["total_solutions_ready"] += len(all_solutions)
                d4["progress"] = int((idx / len(targets)) * 100)

        with self.lock:
            d4["status"] = "success"
            d4["progress"] = 100
            d4["current_task"] = "Seluruh solusi 5 Pilar & Soal Serupa selesai dipecahkan oleh Gemini Flash Mega-Batch!"
        self.log("REASONER", "✅ Fase 4 Reasoning selesai 100%.", "success")

    def _build_5pillar_prompt(self, subject_name, batch, kunci_map, slug=None):
        sidecar_doc = {}
        if slug:
            sc_path = os.path.join(DATA_DIR, f"{slug}_sidecar_transcriptions.json")
            if os.path.isfile(sc_path):
                try:
                    with open(sc_path, "r", encoding="utf-8") as f:
                        sidecar_doc = json.load(f)
                except Exception:
                    pass

        q_texts = []
        for q in batch:
            no = q["nomor"]
            kunci = kunci_map.get(str(no), q.get("kunci_jawaban", "-"))
            stimulus = q.get("stimulus", {}).get("text", "").strip()
            soal = q.get("pertanyaan", {}).get("text", "").strip()

            items_desc = []
            if q.get("pernyataan"):
                for p in q["pernyataan"]:
                    items_desc.append(f"  - {p.get('key')}. {p.get('text')}")
            elif q.get("pilihan_jawaban"):
                for opt in q["pilihan_jawaban"]:
                    txt = opt.get("full_display") or opt.get("text") or ""
                    items_desc.append(f"  - {opt.get('key')}. {txt}")

            items_str = "\n".join(items_desc) if items_desc else "(Tidak ada pilihan terpisah)"

            # Check if there are images with sidecar descriptions
            visual_descs = []
            all_imgs = (q.get("stimulus", {}).get("images", []) or []) + (q.get("pertanyaan", {}).get("images", []) or [])
            for im in all_imgs:
                fn = im.get("filename")
                if fn and fn in sidecar_doc:
                    sc_desc = sidecar_doc[fn].get("description", "")
                    visual_descs.append(f"[Konteks Visual Gambar {fn}]:\n{sc_desc}")

            vis_str = "\n".join(visual_descs) if visual_descs else ""

            q_texts.append(f"""
---
[SOAL NO {no}]
KUNCI RESMI PUSMENDIK: {kunci}
TIPE SOAL: {q.get('tipe', 'Pilihan Ganda')}
STIMULUS:
{stimulus or '(Tidak ada stimulus teks terpisah)'}
{vis_str}
PERTANYAAN:
{soal}
OPSI / PERNYATAAN:
{items_str}
""")

        return f"""Kamu adalah Guru Besar dan Pakar Kurikulum Pembuat Soal TKA Saintek & Soshum Kemdikbudristek RI ({subject_name}).
Tugasmu adalah menghasilkan PEMBAHASAN 5 PILAR PEDAGOGIS (L3) yang mendalam, presisi, dan ilmiah untuk setiap soal berikut.

ATURAN WAJIB (ZERO-TOLERANCE QUALITY STANDARDS):
1. KUNCI RESMI PUSMENDIK ADALAH KEBENARAN MUTLAK (GROUND TRUTH). Seluruh alur penalaran harus secara ilmiah membuktikan kebenaran kunci resmi tersebut.
2. SETIAP LANGKAH HARUS SPESIFIK SOAL INI — WAJIB menyebut nilai, variabel, tokoh, tanggal, atau kutipan kata yang BENAR-BENAR ADA di soal ini. Contoh dibenarkan: "Substitusi x = 4 ke f(x)". Contoh DILARANG: "Substitusikan nilai yang diketahui ke rumus". Langkah yang berlaku untuk soal apa pun dianggap GAGAL mutu.
3. DILARANG KERAS MENGGUNAKAN KATA 'transkrip' ATAU 'transkripsi' DALAM SELURUH BIDANG TEKS (why_correct, reasoning, steps). Jika merujuk ke gambar atau stimulus, sebut langsung 'Pada kutipan teks...', 'Pada gambar terlihat...', atau 'Berdasarkan teks...'.
4. UNTUK SOAL HITUNGAN: tuliskan perhitungan nyata dari angka soal ini sampai hasil akhir (bukan deskripsi cara menghitung). Minimum 3 langkah untuk soal hitungan/analisis, minimum 2 langkah untuk soal konseptual.
5. DILARANG menyalin tempel frasa identik antar soal dalam satu paket. Dua soal berbeda tidak boleh memiliki langkah dengan kalimat pengantar yang sama.
6. 'diketahui' WAJIB mengutip data spesifik dari soal (angka, nama, istilah kunci) — bukan parafrasa generik seperti 'Data yang diketahui dari soal'.
7. GUNAKAN KATEX UNTUK SEMUA RUMUS ATAU SIMBOL MATEMATIKA/SAINS ($...$ atau $$...$$).
8. Output WAJIB berupa JSON ARRAY murni yang valid tanpa teks pengantar atau penutup, tanpa markdown di luar isi string.
9. Petakan kunci resmi ke opsi/pernyataan: untuk tipe Benar-Salah, kunci 'A:Benar' berarti pernyataan A benar — jelaskan setiap pernyataan satu per satu, jangan mengarang pernyataan yang tidak ada di soal.
10. DILARANG KERAS MENGGUNAKAN MARKDOWN HEADER (###, ##, #) DAN TABEL PIPA MARKDOWN (|...|) di dalam field 'diketahui', 'ditanyakan', maupun 'steps'. Jika data dari stimulus/gambar berbentuk tabel atau grafik, ubah menjadi daftar poin terstruktur yang rapi (gunakan bullet •) yang langsung menyebut nama kategori dan nilainya. DILARANG menulis preamble teknis seperti 'Berikut adalah analisis/ekstraksi data...' atau 'Transkripsi Rumus:'.
11. RUMUS DAN PERSAMAAN MATEMATIKA: Setiap persamaan utama atau rumus berurutan WAJIB dipisahkan oleh baris baru (newline) dan menggunakan KaTeX display ($$...$$). DILARANG menumpuk dua persamaan matematika berurutan secara inline ($a$ $b$) dalam satu baris. Matriks ordo 2x1, 2x2, atau lebih besar WAJIB menggunakan format display math $$...$$.

FORMAT JSON PER ELEMEN:
{{
  "question_number": <nomor_soal>,
  "question_title": "<Judul/Topik Spesifik Soal>",
  "difficulty": "Sedang",
  "estimated_time_seconds": 90,
  "concept_tags": ["<Tag1>", "<Tag2>"],
  "glossary": [{{"term": "<Istilah>", "meaning": "<Arti ringkas>"}}],
  "diketahui": "• Variabel/Informasi 1: $...$\n• Variabel/Informasi 2: $...$",
  "ditanyakan": "<Inti hal yang ditanyakan>",
  "reasoning": "<Penalaran ilmiah mendasar>",
  "steps": [
    {{"step": 1, "title": "<Judul Tahap 1>", "explanation": "<Penjelasan rinci dan spesifik pada soal ini>"}},
    {{"step": 2, "title": "<Judul Tahap 2>", "explanation": "<Penjelasan rinci dan spesifik pada soal ini>"}}
  ],
  "why_correct": "<Penjelasan mengapa kunci resmi tersebut adalah opsi yang benar>",
  "tips": ["<Tips cepat konsep ini>"],
  "common_mistakes": ["<Jebakan umum yang dialami siswa>"]
}}

DAFTAR SOAL:
{"".join(q_texts)}
"""

    def _build_soal_serupa_prompt(self, subject_name, batch, slug=None):
        sidecar_doc = {}
        if slug:
            sc_path = os.path.join(DATA_DIR, f"{slug}_sidecar_transcriptions.json")
            if os.path.isfile(sc_path):
                try:
                    with open(sc_path, "r", encoding="utf-8") as f:
                        sidecar_doc = json.load(f)
                except Exception:
                    pass

        items = []
        for q in batch:
            no = q["nomor"]
            stim = q.get("stimulus", {}).get("text", "").strip()
            pert = q.get("pertanyaan", {}).get("text", "").strip()
            kunci = q.get("kunci_jawaban", "-")

            # Konteks visual dari transkripsi sidecar — krusial untuk soal
            # yang isinya murni gambar (teks soal kosong).
            visual_descs = []
            all_imgs = (q.get("stimulus", {}).get("images", []) or []) + \
                       (q.get("pertanyaan", {}).get("images", []) or [])
            for im in all_imgs:
                fn = im.get("filename")
                if fn and fn in sidecar_doc:
                    sc_desc = sidecar_doc[fn].get("description", "")
                    if sc_desc:
                        visual_descs.append(f"[Isi Gambar Soal {fn}]:\n{sc_desc}")
            vis_str = ("\n".join(visual_descs) + "\n") if visual_descs else ""

            items.append(f"""---
[SOAL ACUAN NO {no}]
Kunci Resmi: {kunci}
Stimulus Teks: {stim or '(Lihat pertanyaan)'}
{vis_str}Pertanyaan: {pert}
""")

        return f"""Kamu adalah Pakar Pembuat Soal TKA SMA Kemdikbud ({subject_name}).
Buatkan SOAL SERUPA / LATIHAN MANDIRI (Text-Only, tanpa memerlukan gambar baru) untuk setiap soal acuan berikut.
Soal latihan harus menguji konsep materi yang persis sama dengan narasi/variabel baru.

ATURAN WAJIB:
1. Soal latihan HARUS TEKS MURNI (tidak memerlukan gambar/diagram baru).
2. Sediakan 5 pilihan jawaban (A, B, C, D, E).
3. Berikan 1 kunci yang pasti benar (A/B/C/D/E) dan pembahasan singkat.
4. Teks pertanyaan untuk setiap nomor HARUS UNIK, mandiri, dan tidak boleh sama atau duplikat antar nomor soal.
5. Output WAJIB berupa JSON ARRAY murni.

FORMAT JSON:
{{
  "nomor_soal": <nomor_soal_acuan>,
  "soal_serupa": {{
    "pertanyaan": "<Teks pertanyaan lengkap>",
    "pilihan": [
      {{"key": "A", "text": "<Pilihan A>"}},
      {{"key": "B", "text": "<Pilihan B>"}},
      {{"key": "C", "text": "<Pilihan C>"}},
      {{"key": "D", "text": "<Pilihan D>"}},
      {{"key": "E", "text": "<Pilihan E>"}}
    ],
    "kunci": "<A/B/C/D/E>",
    "pembahasan_singkat": "<Penjelasan ringkas>"
  }}
}}

DAFTAR SOAL ACUAN:
{"".join(items)}
"""

    def _safe_parse_json(self, text):
        text = text.strip()
        if "```" in text:
            m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
            if m:
                text = m.group(1).strip()

        for cand in [text, re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)]:
            try:
                return json.loads(cand, strict=False)
            except Exception:
                pass

        first_b = text.find('[')
        last_b = text.rfind(']')
        if first_b != -1 and last_b != -1 and last_b > first_b:
            sub = text[first_b:last_b+1]
            for cand in [sub, re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', sub)]:
                try:
                    return json.loads(cand, strict=False)
                except Exception:
                    pass

        # Partial array parser if cut off:
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

    # =========================================================================
    # FASE 5: ZERO-TRUST AUDITOR & RELEASE
    # =========================================================================
    def _execute_divisi_5_auditor(self, targets):
        with self.lock:
            d5 = self.divisions["divisi_5"]
            d5["status"] = "active"
            d5["progress"] = 50
            d5["current_task"] = "Menjalankan Auditor Otomatis 9 Checklist Anti-Bug..."

        self.log("AUDITOR", "Memulai audit deterministik 9 kriteria kualitas.", "info")

        import importlib
        auditor_mod = importlib.import_module("pipeline.05_automated_auditor")
        audit_subject_package = auditor_mod.audit_subject_package

        all_passed = True
        for t in targets:
            slug = t["slug"]
            mapel = t["mapel_key"]
            paket = t["paket"]
            prefix = t.get("prefix", "soal")

            issues, warnings = audit_subject_package(slug, mapel, paket, prefix)
            if issues:
                all_passed = False
                self.log("AUDITOR", f"❌ [{slug}] Audit Gagal: {len(issues)} isu ditemukan!", "error")
                for iss in issues:
                    self.log("AUDITOR", f"   - {iss}", "error")
            else:
                self.log("AUDITOR", f"✅ [{slug}] Audit Lolos 100%! (0 Issues, {len(warnings)} Warnings)", "success")
                with self.lock:
                    d5["keys_verified"] += 1

                # Update registry.json
                self._register_subject_release(t)

        with self.lock:
            if all_passed:
                d5["status"] = "success"
                d5["progress"] = 100
                d5["current_task"] = "🎉 Zero-Trust Audit 100% Lolos! Seluruh mapel aktif di CBT Runtime."
            else:
                d5["status"] = "error"
                d5["progress"] = 90
                d5["current_task"] = "Audit menemukan isu pada beberapa target. Periksa log detail."

    def _register_subject_release(self, t):
        slug = t["slug"]
        mapel = t["mapel_key"]
        paket = t["paket"]

        reg = {}
        if os.path.isfile(REG_PATH):
            try:
                with open(REG_PATH, "r", encoding="utf-8") as f:
                    reg = json.load(f)
            except Exception:
                reg = {}

        # Compatible with solution_loader.py (flat slug mapping)
        reg[slug] = {
            "active_source": f"{slug.upper()}_SOLUTIONS.json"
        }

        with open(REG_PATH, "w", encoding="utf-8") as f:
            json.dump(reg, f, indent=2, ensure_ascii=False)


# Singleton Engine Instance
swarm_engine = SwarmManager()
