# -*- coding: utf-8 -*-
"""scrape_kunci.py — Scrape kunci jawaban resmi TKA dari Pusmendik.

Mengotomasi alur simulasi resmi (sebagaimana dijalankan manual):
  pilih mapel -> login -> konfirmasi data (refresh token) -> mulai tes
  -> isi jawaban -> next di soal terakhir -> SELESAI TES -> parse review_hasil

Output : data/kunci/{mapel}_paket_{n}_kunci.json
Merge  : --merge menerapkan kunci resmi ke *_learning.json
         (soal Benar/Salah otomatis dikonversi ke tipe 'Benar-Salah')

Pemakaian:
  python scrape_kunci.py                 # scrape semua target yang belum punya kunci
  python scrape_kunci.py --target ekonomi_paket_1
  python scrape_kunci.py --merge         # terapkan semua kunci hasil scrape
  python scrape_kunci.py --show          # tampilkan ringkasan kunci yang tersimpan
"""
import os
import re
import json
import time
import argparse
import traceback
from playwright.sync_api import sync_playwright

BASE_URL = "https://pusmendik.kemendikdasmen.go.id"
SIMULASI_URL = f"{BASE_URL}/tka/simulasi_tka"
ROOT = os.path.dirname(os.path.abspath(__file__))
KUNCI_DIR = os.path.join(ROOT, "data", "kunci")

CANONICAL_LABELS = {
    "tepat": "Tepat",
    "tidak tepat": "Tidak Tepat",
    "sesuai": "Sesuai",
    "tidak sesuai": "Tidak Sesuai",
    "benar": "Benar",
    "salah": "Salah"
}

# ID mapel resmi (dropdown #mapel). Pilihan mapel dideteksi dinamis.
WAJIB_IDS = {"matematika": ["7", "82"], "bahasa_inggris": ["3", "84"]}
TARGETS = [
    # (slug, jenis_mapel, paket)
    ("matematika_paket_1", "1", 1),
    ("matematika_paket_2", "1", 2),
    ("bahasa_inggris_paket_1", "1", 1),
    ("bahasa_inggris_paket_2", "1", 2),
    ("ekonomi_paket_1", "2", 1),
    ("ekonomi_paket_2", "2", 2),
    ("kewirausahaan_paket_1", "2", 1),
    ("kewirausahaan_paket_2", "2", 2),
    ("geografi_paket_1", "2", 1),
    ("geografi_paket_2", "2", 2),
]
FILE_FOR_SLUG = {
    "matematika_paket_1": "matematika_paket_1_learning.json",
    "bahasa_inggris_paket_1": "bahasa_inggris_paket_1_learning.json",
    "bahasa_inggris_paket_2": "bahasa_inggris_paket_2_learning.json",
    "ekonomi_paket_1": "ekonomi_paket_1_learning.json",
    "ekonomi_paket_2": "ekonomi_paket_2_learning.json",
    "kewirausahaan_paket_1": "kewirausahaan_paket_1_learning.json",
    "kewirausahaan_paket_2": "kewirausahaan_paket_2_learning.json",
    "geografi_paket_1": "geografi_paket_1_learning.json",
    "geografi_paket_2": "geografi_paket_2_learning.json",
}


def kunci_path(slug):
    return os.path.join(KUNCI_DIR, f"{slug}_kunci.json")


# ============================ SCRAPING ============================

def resolve_mapel_id(page, jenis_mapel, paket, nama_mapel_hint):
    """Baca opsi mapel (select tersembunyi di balik custom dropdown) dan resolve ID."""
    page.select_option("#jenis_mapel", jenis_mapel)
    page.wait_for_timeout(1800)
    opts = page.eval_on_selector_all(
        "#mapel option",
        "els => els.map(o => ({ text: o.textContent.trim(), value: o.value }))",
    )
    opts = [o for o in opts if o["value"]]
    cands = opts
    if nama_mapel_hint:
        cands = [o for o in opts if nama_mapel_hint.lower() in o["text"].lower()] or opts
    target = cands[(paket - 1) % len(cands)] if cands else None
    if not target:
        raise RuntimeError(f"Mapel tidak ditemukan (jenis={jenis_mapel}, paket={paket}). Opsi: {opts}")
    print(f"    -> {target['text']} (ID {target['value']})")
    return target["value"]


def pick_mapel_via_dropdown(page, mapel_id):
    """Pilih mapel lewat custom dropdown UI (select native tersembunyi)."""
    page.click("#mapel_toggle")
    page.wait_for_timeout(500)
    sel = f".mapel-option[data-value='{mapel_id}']"
    page.wait_for_selector(sel, timeout=10000)
    page.click(sel)
    page.wait_for_timeout(500)


def scrape_slug(page, slug, jenis_mapel, paket, nama_mapel_hint=None):
    print(f"\n=== Scraping {slug} ===")
    page.goto(SIMULASI_URL, timeout=60000)
    page.wait_for_timeout(2500)

    # 1. Pilih jenjang & mapel
    page.select_option("#jenjang", "sma")
    page.wait_for_timeout(800)
    mapel_id = resolve_mapel_id(page, jenis_mapel, paket, nama_mapel_hint)
    pick_mapel_via_dropdown(page, mapel_id)

    # 2. Mulai Simulasi -> Login
    page.get_by_role("button", name="Mulai Simulasi").click()
    page.wait_for_url(lambda u: "konfirmasi" in u or "login" in u, timeout=30000)
    page.wait_for_timeout(2000)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url(lambda u: "konfirmasi_data" in u, timeout=30000)
    page.wait_for_timeout(1500)

    # Tutup popup Google (change password dsb) bila muncul
    for ctx_page in page.context.pages:
        if ctx_page != page and "accounts.google.com" in ctx_page.url:
            ctx_page.close()

    # 3. Konfirmasi data: refresh token 1x, isi form, submit
    page.get_by_role("button", name="Refresh").click()
    page.wait_for_timeout(1500)
    body_text = page.inner_text("body")
    token_match = re.search(r"Token\s*[:=]\s*([A-Z0-9]{6})", body_text)
    if not token_match:
        raise RuntimeError("Token baru tidak ditemukan di halaman konfirmasi")
    token = token_match.group(1)
    print(f"    -> token baru: {token}")

    page.fill("#nama_peserta", "PESERTA TKA")
    page.select_option("#tgl", "01")
    bulan_sel = page.eval_on_selector(
        "#bulan", "el => { el.selectedIndex = 1; el.dispatchEvent(new Event('change', {bubbles:true})); }"
    )
    page.select_option("#tahun", "2008")
    page.fill("#input-token", token)
    # Jeda singkat agar AJAX refresh token selesai diproses server sebelum submit
    page.wait_for_timeout(1500)
    page.screenshot(path=os.path.join(ROOT, "debug_before_submit.png"), full_page=True)
    page.click("#btnSubmit")
    # Navigasi setelah submit kadang tidak menyelesaikan event 'load' (transient)
    # -> tunggu sampai 'domcontentloaded' & retry maksimal 3x
    last_err = None
    for attempt in range(3):
        try:
            page.wait_for_url(
                lambda u: "konfirmasi_tes" in str(u),
                timeout=20000,
                wait_until="domcontentloaded",
            )
            last_err = None
            break
        except Exception as e:
            last_err = e
            print(f"    -> submit wait gagal (percobaan {attempt + 1}/3): {type(e).__name__} url={page.url}")
            still_on_form = "konfirmasi_data" in page.url
            if still_on_form:
                try:
                    page.click("#btnSubmit", timeout=5000)
                    page.wait_for_timeout(1000)
                except Exception as ce:
                    print(f"    -> re-click submit gagal: {type(ce).__name__}")
    if last_err:
        page.screenshot(path=os.path.join(ROOT, "debug_submit.png"))
        body = page.inner_text("body")[:600]
        raise RuntimeError(f"Submit gagal navigasi. URL: {page.url}\nBody: {body}")
    page.wait_for_timeout(2500)
    page.wait_for_selector("button:has-text('Mulai')", timeout=15000)

    # 4. Mulai tes -> tunggu UI soal benar2 terender (#nextSoal), bukan hanya URL
    for attempt in range(2):
        try:
            page.get_by_role("button", name="Mulai", exact=True).click()
            page.wait_for_url(lambda u: "proses_tes" in str(u), timeout=45000, wait_until="domcontentloaded")
            page.wait_for_selector("#nextSoal", timeout=45000)
            break
        except Exception as e:
            print(f"    -> mulai tes gagal (percobaan {attempt + 1}/2): {type(e).__name__} url={page.url}")
            if attempt == 1:
                raise
            page.wait_for_timeout(2000)
    page.wait_for_timeout(2500)

    # 5. Isi semua jawaban (radio: pilihan pertama; checkbox kompleks: centang satu)
    page.evaluate(
        """() => {
        const groups = [...new Set([...document.querySelectorAll('input[type=radio]')].map(r => r.name))];
        groups.forEach(g => {
            const r = document.querySelector(`input[name="${CSS.escape(g)}"]`);
            r.checked = true;
            r.dispatchEvent(new Event('change', {bubbles: true}));
        });
        const cbGroups = [...new Set([...document.querySelectorAll('input[type=checkbox]')].map(c => c.name))];
        cbGroups.forEach(g => {
            const c = document.querySelector(`input[name="${CSS.escape(g)}"]`);
            if (c && !c.checked) { c.checked = true; c.dispatchEvent(new Event('change', {bubbles: true})); }
        });
    }"""
    )
    page.wait_for_timeout(800)

    # 6. Next sampai soal terakhir -> halaman finish_tes
    #    Sambil navigasi, simpan snapshot teks soal per nomor (bukti pemetaan paket)
    question_snapshots = {}
    for _ in range(60):
        if "finish_tes" in page.url:
            break
        try:
            snap = page.evaluate(
                """() => {
                const t = document.body.innerText || '';
                const m = t.match(/Soal\\s+(\\d+)/);
                const card = document.querySelector('.card-body, #soal, .content-soal, .box-body');
                return { no: m ? parseInt(m[1]) : null, text: ((card ? card.innerText : t) || '').slice(0, 300) };
            }"""
            )
            if snap and snap.get("no"):
                question_snapshots[snap["no"]] = snap["text"]
        except Exception:
            pass
        next_btn = page.query_selector("#nextSoal")
        if not next_btn or next_btn.is_disabled():
            break
        next_btn.click()
        page.wait_for_timeout(250)
    page.wait_for_url(lambda u: "finish_tes" in str(u), timeout=20000, wait_until="domcontentloaded")
    page.wait_for_timeout(1500)

    # 7. SELESAI TES -> review_hasil
    #    PENTING: halaman finish memuat SPAN dekoratif "SELESAI TES" di dalam
    #    paragraf instruksi DAN tombol <button> yang sebenarnya. get_by_text()
    #    mengembalikan keduanya dan .first mengarah ke SPAN (no-op saat klik).
    #    Klik elemen <button> yang mengandung teks tersebut.
    selesai_btn = page.locator("button", has_text="SELESAI TES").first
    try:
        selesai_btn.click(timeout=10000)
    except Exception as e:
        print(f"    -> klik tombol SELESAI TES gagal: {type(e).__name__}")
        page.screenshot(path=os.path.join(ROOT, "debug_review.png"), full_page=True)
        raise RuntimeError(f"Tombol SELESAI TES tidak ditemukan. URL: {page.url}")
    try:
        page.wait_for_url(lambda u: "review_hasil" in str(u), timeout=30000, wait_until="domcontentloaded")
    except Exception:
        # Fallback: klik ulang bila navigasi pertama tidak terjadi
        try:
            selesai_btn.click(timeout=5000)
            page.wait_for_url(lambda u: "review_hasil" in str(u), timeout=20000, wait_until="domcontentloaded")
        except Exception:
            page.screenshot(path=os.path.join(ROOT, "debug_review.png"), full_page=True)
            body = page.inner_text("body")[:600]
            raise RuntimeError(f"Gagal mencapai review_hasil. URL: {page.url}\nBody: {body}")
    if "review_hasil" not in page.url:
        page.screenshot(path=os.path.join(ROOT, "debug_review.png"))
        body = page.inner_text("body")[:600]
        raise RuntimeError(f"Gagal mencapai review_hasil. URL: {page.url}\nBody: {body}")
    page.wait_for_timeout(2500)

    # 8. Parse tabel reviu: NO | JAWABAN ANDA | KUNCI JAWABAN
    rows = page.evaluate(
        """() => {
        const table = document.querySelector('table');
        if (!table) return [];
        return [...table.querySelectorAll('tr')].slice(1).map(tr => {
            const tds = tr.querySelectorAll('td');
            if (tds.length < 3) return null;
            return { no: tds[0].innerText.trim(), anda: tds[1].innerText, kunci: tds[2].innerText };
        }).filter(Boolean);
    }"""
    )

    kunci_pg = {}
    kunci_bs = {}
    bs_stmt_counts = {}
    raw_rows = {}
    for r in rows:
        no = int(re.sub(r"\D", "", r["no"]))
        kunci_cell = r["kunci"].strip()
        raw_rows[no] = {"anda": r["anda"].strip(), "kunci": kunci_cell}

        matrix_pairs = re.findall(r"([A-E])\s*\(([^)]+)\)", kunci_cell)
        m_pair_alt = re.findall(r"([A-E])\s*\((Tepat|Tidak Tepat|Sesuai|Tidak Sesuai|Benar|Salah)\)", kunci_cell, re.I)
        if len(matrix_pairs) >= 2:
            kunci_bs[no] = {k.upper(): CANONICAL_LABELS.get(v.strip().lower(), v.strip()) for k, v in matrix_pairs}
            bs_stmt_counts[no] = len(matrix_pairs)
        elif len(m_pair_alt) >= 1:
            kunci_bs[no] = {k.upper(): CANONICAL_LABELS.get(v.strip().lower(), v.strip()) for k, v in m_pair_alt}
            bs_stmt_counts[no] = len(m_pair_alt)
        elif any(w in kunci_cell for w in ["Benar", "Salah", "Tepat", "Sesuai"]):
            bs_map = {}
            for line in kunci_cell.split("\n"):
                line = line.strip()
                m = re.match(r"\(([A-E])\)\s*(Tepat|Tidak Tepat|Sesuai|Tidak Sesuai|Benar|Salah)", line, re.I)
                if m:
                    bs_map[m.group(1).upper()] = CANONICAL_LABELS.get(m.group(2).strip().lower(), m.group(2).strip())
            if bs_map:
                kunci_bs[no] = bs_map
                bs_stmt_counts[no] = len(bs_map)
            else:
                letters = re.findall(r"\(\s*([A-E])\s*\)", kunci_cell)
                if letters:
                    kunci_pg[no] = letters if len(letters) > 1 else letters[0]
                else:
                    m_raw = re.findall(r"\b([A-E])\b", kunci_cell)
                    if m_raw:
                        kunci_pg[no] = m_raw if len(m_raw) > 1 else m_raw[0]
        else:
            letters = re.findall(r"\(\s*([A-E])\s*\)", kunci_cell)
            if letters:
                kunci_pg[no] = letters if len(letters) > 1 else letters[0]
            else:
                m_raw = re.findall(r"\b([A-E])\b", kunci_cell)
                if m_raw:
                    kunci_pg[no] = m_raw if len(m_raw) > 1 else m_raw[0]

    result = {
        "slug": slug,
        "mapel_id": mapel_id,
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kunci_pg": kunci_pg,
        "kunci_bs": {str(k): v for k, v in kunci_bs.items()},
        "bs_statement_count": {str(k): v for k, v in bs_stmt_counts.items()},
        # Teks mentah kolom JAWABAN ANDA & KUNCI JAWABAN (untuk verifikasi manual
        # dan deteksi soal multi-jawaban yang tidak tertangkap regex di atas)
        "raw_rows": {str(k): v for k, v in raw_rows.items()},
        # Snapshot teks soal per nomor (bukti kunci dipetakan ke paket yang benar)
        "question_snapshots": {str(k): v for k, v in question_snapshots.items()},
    }
    os.makedirs(KUNCI_DIR, exist_ok=True)
    with open(kunci_path(slug), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"    -> tersimpan: {len(kunci_pg)} kunci PG, {len(kunci_bs)} soal Benar/Salah")
    return result


def run_scrape(targets, headless=True):
    # Browser FRESH per target: sesi sebelumnya yang gagal dapat mengganggu
    # sesi berikutnya di sisi server, dan navigasi submit lebih stabil di sesi baru.
    for slug, jenis, paket in targets:
        for attempt in range(1, 4):
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                page = browser.new_page()

                def _on_dialog(d):
                    # Playwright auto-dismiss (= batal) bila tak ada handler,
                    # yang bisa membatalkan langkah 'SELESAI TES'. Terima semua.
                    print(f"    -> dialog JS: {str(d.message)[:80]}")
                    d.accept()

                page.on("dialog", _on_dialog)
                try:
                    hint = None
                    if slug.startswith("ekonomi"):
                        hint = "ekonomi"
                    elif slug.startswith("kewirausahaan"):
                        hint = "kewirausahaan"
                    elif slug.startswith("bahasa_inggris"):
                        hint = "inggris"
                    elif slug.startswith("geografi"):
                        hint = "geografi"
                    scrape_slug(page, slug, jenis, paket, hint)
                    break  # sukses -> lanjut target berikutnya
                except Exception as e:
                    print(f"    [GAGAL] {slug} (percobaan {attempt}/3): {e}")
                    traceback.print_exc()
                finally:
                    browser.close()


# ============================ MERGE ============================

def merge_slug(slug):
    kp = kunci_path(slug)
    if not os.path.exists(kp):
        print(f"[skip] {slug}: file kunci belum ada")
        return
    kdata = json.load(open(kp, encoding="utf-8"))
    fname = FILE_FOR_SLUG.get(slug)
    if not fname:
        print(f"[skip] {slug}: tidak dipetakan ke file data")
        return
    fpath = os.path.join(ROOT, "data", fname)
    d = json.load(open(fpath, encoding="utf-8"))
    soal_list = d["soal"]
    if len(soal_list) != len(kdata["kunci_pg"]) + len(kdata["kunci_bs"]):
        print(f"[warning] {slug}: jumlah soal JSON ({len(soal_list)}) != kunci scrape "
              f"({len(kdata['kunci_pg']) + len(kdata['kunci_bs'])}) — merge dibatalkan")
        return

    pg_fixed, bs_fixed = 0, 0
    for s in soal_list:
        no = s["nomor"]
        if str(no) in kdata["kunci_bs"]:
            kunci_stmt = kdata["kunci_bs"][str(no)]
            # Konversi ke tipe Benar-Salah bila struktur opsi memenuhi pola resmi
            # (opsi A = header rusak, B/C/D = pernyataan A/B/C)
            opts = s.get("pilihan_jawaban", [])
            if s.get("tipe_soal") != "Benar-Salah":
                if len(opts) == 4:
                    pernyataan = []
                    for stmt_key, opt_key in [("A", "B"), ("B", "C"), ("C", "D")]:
                        o = opts[{"A": 1, "B": 2, "C": 3}[stmt_key]]
                        pernyataan.append({
                            "key": stmt_key,
                            "text": o.get("text", "") or "",
                            "latex": o.get("latex"),
                            "image": o.get("image"),
                        })
                    s["tipe_soal"] = "Benar-Salah"
                    s["pernyataan"] = pernyataan
                    s.pop("pilihan_jawaban", None)
                else:
                    print(f"[warning] {slug} soal {no}: pola opsi B/S tidak dikenali "
                          f"({len(opts)} opsi) — hanya kunci yang di-update")
            stmt_keys = [p["key"] for p in s.get("pernyataan", [])] or list(kunci_stmt.keys())
            s["kunci_jawaban"] = [f"{k}:{kunci_stmt[k]}" for k in stmt_keys if k in kunci_stmt]
            bs_fixed += 1
        elif no in kdata["kunci_pg"]:
            if s.get("kunci_jawaban") != kdata["kunci_pg"][no]:
                pg_fixed += 1
            s["kunci_jawaban"] = kdata["kunci_pg"][no]

    json.dump(d, open(fpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[merge] {slug}: {pg_fixed} kunci PG diperbaiki, {bs_fixed} soal B/S diset")


def run_merge():
    for slug, _, _ in TARGETS:
        merge_slug(slug)
    # MTK Paket 2 sudah direpair manual dengan kunci resmi — tidak lewat TARGETS


def show_summary():
    for slug, _, _ in TARGETS:
        kp = kunci_path(slug)
        if os.path.exists(kp):
            d = json.load(open(kp, encoding="utf-8"))
            print(f"{slug}: PG={len(d['kunci_pg'])} BS={len(d['kunci_bs'])} "
                  f"(scraped {d['scraped_at']})")
        else:
            print(f"{slug}: BELUM ADA")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape kunci jawaban resmi TKA Pusmendik")
    parser.add_argument("--target", type=str, default=None, help="slug target tunggal, mis. ekonomi_paket_1")
    parser.add_argument("--merge", action="store_true", help="Terapkan kunci hasil scrape ke learning JSON")
    parser.add_argument("--show", action="store_true", help="Tampilkan ringkasan kunci tersimpan")
    parser.add_argument("--headless", action="store_true", default=True)
    args = parser.parse_args()

    if args.show:
        show_summary()
    elif args.merge:
        run_merge()
    else:
        targets = TARGETS
        if args.target:
            targets = [t for t in TARGETS if t[0] == args.target]
            if not targets:
                print(f"Target '{args.target}' tidak dikenal. Pilihan: {[t[0] for t in TARGETS]}")
                raise SystemExit(1)
        run_scrape(targets, headless=args.headless)
