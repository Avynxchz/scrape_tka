# -*- coding: utf-8 -*-
"""cbt_integrator.py — Phase 5 Master Ingestion & CBT Runtime Integrator.
Integrates raw questions from Pusmendik HTML, official answer keys from review_hasil,
and rich 5-pillar AI solutions into:
- data/geografi/paket_2/geografi_paket_2.json & data/geografi_paket_2_learning.json
- data/fisika/paket_1/fisika_paket_1.json & data/fisika_paket_1_learning.json
- data/fisika/paket_2/fisika_paket_2.json & data/fisika_paket_2_learning.json
- data/solution_sources/registry.json
- app.js (SUBJECT_CATALOG)
- index.html (Subject Dropdown)
"""
import os
import re
import json
import sys
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from _repair_keys import parse_official_row

def build_learning_dataset(slug, subject_key, paket_num, html_path, kunci_path, solutions_path, raw_json_out, learning_json_out):
    print(f"\n[CBT INTEGRATOR] ===================================================")
    print(f"[CBT INTEGRATOR] Processing {slug} ({subject_key.title()} Paket {paket_num})...")
    print(f"[CBT INTEGRATOR] ===================================================")

    if not os.path.exists(html_path):
        print(f"[Error] HTML not found: {html_path}")
        return False
    if not os.path.exists(kunci_path):
        print(f"[Error] Kunci not found: {kunci_path}")
        return False
    if not os.path.exists(solutions_path):
        print(f"[Error] Solutions not found: {solutions_path}")
        return False

    with open(kunci_path, "r", encoding="utf-8") as f:
        kunci_data = json.load(f)
    raw_rows = kunci_data.get("raw_rows", {})

    with open(solutions_path, "r", encoding="utf-8") as f:
        sol_data = json.load(f)
    sol_map = {s.get("question_number"): s for s in sol_data.get("solutions", [])}

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    soal_divs = soup.find_all("div", class_="soal-soal")
    print(f"[CBT INTEGRATOR] Found {len(soal_divs)} questions in raw HTML")

    learning_questions = []
    raw_questions = []

    for idx, s in enumerate(soal_divs, start=1):
        q_no = idx
        cont = s.find("div", class_="cont-soal")
        isi = s.find("div", class_="isi-soal")

        # Make copy of isi to extract options table cleanly
        isi_copy = BeautifulSoup(str(isi), "html.parser").find("div", class_="isi-soal") if isi else None

        # Find interactive table (the table containing <input>)
        interactive_table = None
        if isi_copy:
            for tbl in isi_copy.find_all("table"):
                if tbl.find("input"):
                    interactive_table = tbl
                    break

        # Parse official key
        row_entry = raw_rows.get(str(q_no), {})
        kunci_raw = row_entry.get("kunci", "")
        kind, payload = parse_official_row(kunci_raw)

        # Handle edge case where Pusmendik has empty parenthesis like "A (Benar)\nB (Salah)\nC ()"
        if kind == "unknown" and "Benar" in kunci_raw and "Salah" in kunci_raw:
            pairs_bs = dict(re.findall(r"([A-Z])\s*\((Benar|Salah)\)", kunci_raw))
            if "C ()" in kunci_raw:
                pairs_bs["C"] = "Benar"
            kind = "bs"
            payload = pairs_bs

        options = []
        pernyataan = []
        tipe_soal = "Pilihan Ganda"
        kunci_jawaban = None

        if kind == "bs":
            tipe_soal = "Benar-Salah"
            kunci_jawaban = [f"{k}:{v}" for k, v in payload.items()]
            if interactive_table:
                for tr in interactive_table.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) >= 2:
                        key_td = tds[0].get_text(strip=True).replace(".", "").strip()
                        txt_td = tds[1].get_text(" ", strip=True)
                        if txt_td and not any(h in txt_td.lower() for h in ["kondisi", "pernyataan", "besaran", "strategi", "pernyatan"]):
                            k = key_td if key_td in "ABCDE" else chr(65 + len(pernyataan))
                            st_img = tds[1].find("img")
                            st_img_obj = None
                            if st_img:
                                src = st_img.get("src", "")
                                fn = os.path.basename(src.split("?")[0])
                                st_img_obj = {"filename": fn, "rel_path": f"images/{fn}"}
                            pernyataan.append({
                                "key": k,
                                "text": txt_td,
                                "latex": None,
                                "image": st_img_obj
                            })
        elif kind == "label":
            tipe_soal = "Pernyataan-Label"
            kunci_jawaban = [f"{k}:{v}" for k, v in payload.items()]
            if interactive_table:
                for tr in interactive_table.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) >= 2:
                        key_td = tds[0].get_text(strip=True).replace(".", "").strip()
                        txt_td = tds[1].get_text(" ", strip=True)
                        if txt_td and not any(h in txt_td.lower() for h in ["kondisi", "pernyataan", "besaran", "strategi", "warna"]):
                            k = key_td if key_td in "ABCDE" else chr(65 + len(pernyataan))
                            st_img = tds[1].find("img")
                            st_img_obj = None
                            if st_img:
                                src = st_img.get("src", "")
                                fn = os.path.basename(src.split("?")[0])
                                st_img_obj = {"filename": fn, "rel_path": f"images/{fn}"}
                            pernyataan.append({
                                "key": k,
                                "text": txt_td,
                                "latex": None,
                                "image": st_img_obj
                            })
        elif kind == "multi":
            tipe_soal = "Pilihan Ganda Kompleks"
            kunci_jawaban = payload
            if interactive_table:
                for r_idx, r in enumerate(interactive_table.find_all("tr")):
                    tds = r.find_all("td")
                    if tds:
                        inp = r.find("input")
                        pil_key = inp.get("pil", chr(ord('a') + r_idx)) if inp else chr(ord('a') + r_idx)
                        content_td = tds[-1]
                        math_img = content_td.find("img")
                        opt_latex = math_img.get("data-latex") if math_img else None
                        opt_img_info = None
                        if math_img and not opt_latex:
                            src = math_img.get("src", "")
                            fn = os.path.basename(src.split("?")[0])
                            opt_img_info = {"filename": fn, "rel_path": f"images/{fn}"}
                        opt_text = content_td.get_text(" ", strip=True)
                        options.append({
                            "key": pil_key.upper(),
                            "text": opt_text,
                            "latex": opt_latex,
                            "image": opt_img_info,
                            "full_display": opt_text
                        })
        elif kind == "single":
            tipe_soal = "Pilihan Ganda"
            kunci_jawaban = payload[0] if isinstance(payload, list) else payload
            if interactive_table:
                for r_idx, r in enumerate(interactive_table.find_all("tr")):
                    tds = r.find_all("td")
                    if tds:
                        inp = r.find("input")
                        pil_key = inp.get("pil", chr(ord('a') + r_idx)) if inp else chr(ord('a') + r_idx)
                        content_td = tds[-1]
                        math_img = content_td.find("img")
                        opt_latex = math_img.get("data-latex") if math_img else None
                        opt_img_info = None
                        if math_img and not opt_latex:
                            src = math_img.get("src", "")
                            fn = os.path.basename(src.split("?")[0])
                            opt_img_info = {"filename": fn, "rel_path": f"images/{fn}"}
                        opt_text = content_td.get_text(" ", strip=True)
                        options.append({
                            "key": pil_key.upper(),
                            "text": opt_text,
                            "latex": opt_latex,
                            "image": opt_img_info,
                            "full_display": opt_text
                        })

        # Remove interactive table from isi_copy
        if interactive_table:
            interactive_table.extract()

        # Rewrite images in cont and isi
        stim_imgs = []
        if cont:
            for img in cont.find_all("img"):
                src = img.get("src", "")
                if src:
                    fn = os.path.basename(src.split("?")[0])
                    img["src"] = f"images/{fn}"
                    stim_imgs.append({
                        "filename": fn,
                        "rel_path": f"images/{fn}",
                        "remote_url": f"https://pusmendik.kemendikdasmen.go.id{src}" if src.startswith("/") else src,
                        "data_latex": img.get("data-latex")
                    })

        prompt_imgs = []
        if isi_copy:
            for img in isi_copy.find_all("img"):
                src = img.get("src", "")
                if src:
                    fn = os.path.basename(src.split("?")[0])
                    img["src"] = f"images/{fn}"
                    prompt_imgs.append({
                        "filename": fn,
                        "rel_path": f"images/{fn}",
                        "remote_url": f"https://pusmendik.kemendikdasmen.go.id{src}" if src.startswith("/") else src,
                        "data_latex": img.get("data-latex")
                    })

        stim_html = str(cont) if cont else ""
        prompt_html = str(isi_copy) if isi_copy else ""

        stim_text = cont.get_text("\n", strip=True) if cont else ""
        prompt_text = isi_copy.get_text("\n", strip=True) if isi_copy else ""

        # Raw question item
        raw_q = {
            "nomor": q_no,
            "id": f"soal-no-{q_no}",
            "tipe_soal": tipe_soal,
            "stimulus": {
                "text": stim_text,
                "images": stim_imgs,
                "html": stim_html
            },
            "pertanyaan": {
                "text": prompt_text,
                "images": prompt_imgs,
                "html": prompt_html
            },
            "pilihan_jawaban": options,
            "kunci_jawaban": kunci_jawaban
        }
        if tipe_soal in ("Benar-Salah", "Pernyataan-Label"):
            raw_q["pernyataan"] = pernyataan
        raw_questions.append(raw_q)

        # Merge solution from AI
        sol = sol_map.get(q_no, {})

        # Glosarium
        glosarium = []
        for g in sol.get("glossary", []):
            t = g.get("term", "")
            m = g.get("meaning", "")
            glosarium.append({"simbol": t, "nama": t, "arti": m})

        # Langkah penyelesaian
        langkah = []
        for st in sol.get("steps", []):
            s_num = st.get("step", "")
            s_title = st.get("title", "")
            s_exp = st.get("explanation", "")
            langkah.append(f"**Langkah {s_num}: {s_title}**\n{s_exp}")

        # Pembahasan 5 Pilar
        pembahasan = {
            "diketahui": sol.get("reasoning", "")[:200] if sol.get("reasoning") else "",
            "ditanyakan": prompt_text[:120],
            "glosarium_simbol": glosarium,
            "mengapa_begini": sol.get("reasoning", ""),
            "konsep_kunci": ", ".join(sol.get("concept_kunci", [])) if isinstance(sol.get("concept_kunci"), list) else sol.get("concept_kunci", ""),
            "langkah_penyelesaian": langkah,
            "tips_trik": " ".join(sol.get("tips", [])) if isinstance(sol.get("tips"), list) else sol.get("tips", ""),
            "why_correct": sol.get("why_correct", ""),
            "common_mistakes": sol.get("common_mistakes", [])
        }

        # Soal Serupa
        ss = sol.get("soal_serupa", {})
        soal_serupa = {}
        if ss:
            pilihan_ss = []
            raw_opsi = ss.get("opsi") or ss.get("pilihan") or []
            for op in raw_opsi:
                pilihan_ss.append({"key": op.get("key", ""), "text": op.get("text", "")})
            soal_serupa = {
                "pertanyaan": ss.get("pertanyaan", ""),
                "pilihan": pilihan_ss,
                "kunci": ss.get("kunci", "A"),
                "pembahasan": ss.get("pembahasan_singkat") or ss.get("pembahasan", "")
            }

        qp = [
            f"Apa konsep kunci pada Soal Nomor {q_no} ini?",
            "Mengapa jawaban tersebut merupakan opsi yang paling tepat?",
            "Bagaimana cara cepat mengeliminasi distraktor pada soal ini?",
            "Apa kesalahan umum yang sering dilakukan siswa di topik ini?"
        ]

        topik_list = sol.get("concept_kunci", [])
        topik_str = topik_list[0] if (isinstance(topik_list, list) and len(topik_list) > 0) else f"{subject_key.title()} SMA"

        learning_q = {
            "nomor": q_no,
            "id": f"soal-no-{q_no}",
            "tipe_soal": tipe_soal,
            "topik": topik_str,
            "stimulus": {
                "text": stim_text,
                "images": stim_imgs,
                "html": stim_html
            },
            "pertanyaan": {
                "text": prompt_text,
                "images": prompt_imgs,
                "html": prompt_html
            },
            "pilihan_jawaban": options,
            "kunci_jawaban": kunci_jawaban,
            "pembahasan": pembahasan,
            "soal_serupa": soal_serupa,
            "quick_prompts": qp
        }

        if tipe_soal in ("Benar-Salah", "Pernyataan-Label"):
            learning_q["pernyataan"] = pernyataan

        learning_questions.append(learning_q)

    # 1. Write Raw JSON
    raw_doc = {
        "slug": slug,
        "name": f"{subject_key.title()} Paket {paket_num}",
        "total_soal": len(raw_questions),
        "soal": raw_questions
    }
    os.makedirs(os.path.dirname(raw_json_out), exist_ok=True)
    with open(raw_json_out, "w", encoding="utf-8") as f:
        json.dump(raw_doc, f, indent=2, ensure_ascii=False)
    print(f"[CBT INTEGRATOR] ✅ Raw JSON saved: {raw_json_out} ({len(raw_questions)} soal)")

    # 2. Write Learning JSON
    learning_doc = {
        "paket": f"{subject_key.title()} Paket {paket_num}",
        "subject": subject_key,
        "total_soal": len(learning_questions),
        "soal": learning_questions
    }
    os.makedirs(os.path.dirname(learning_json_out), exist_ok=True)
    with open(learning_json_out, "w", encoding="utf-8") as f:
        json.dump(learning_doc, f, indent=2, ensure_ascii=False)
    print(f"[CBT INTEGRATOR] ✅ Learning JSON saved: {learning_json_out} ({len(learning_questions)} soal)")

    return True

def update_registry():
    reg_path = os.path.join(BASE_DIR, "data", "solution_sources", "registry.json")
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            reg = json.load(f)
    else:
        reg = {}

    reg["geo_paket_2"] = {"active_source": "GEO_PAKET_2_SOLUTIONS.json"}
    reg["fisika_paket_1"] = {"active_source": "FISIKA_PAKET_1_SOLUTIONS.json"}
    reg["fisika_paket_2"] = {"active_source": "FISIKA_PAKET_2_SOLUTIONS.json"}

    with open(reg_path, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
    print(f"[CBT INTEGRATOR] ✅ Registry updated: {reg_path}")

def update_app_js():
    app_js_path = os.path.join(BASE_DIR, "app.js")
    with open(app_js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Ensure fisika exists in SUBJECT_CATALOG
    if "fisika: {" not in content and "'fisika':" not in content:
        fisika_block = """  fisika: {
    name: 'Fisika',
    json: {
      1: 'data/fisika_paket_1_learning.json',
      2: 'data/fisika_paket_2_learning.json'
    },
    imgBase: {
      1: 'data/fisika/paket_1/',
      2: 'data/fisika/paket_2/'
    },
    welcome: `Halo! Saya <strong>AI Tutor TKA Fisika</strong>. Masih bingung dengan penurunan rumus, diagram benda bebas, vektor, atau hukum fisika pada soal ini? Klik salah satu pertanyaan cepat di atas atau ketik langsung pertanyaanmu di bawah ya!`
  },
};"""
        if "  }\n};" in content:
            content = content.replace("  }\n};", "  },\n" + fisika_block)
        elif "  }\r\n};" in content:
            content = content.replace("  }\r\n};", "  },\r\n" + fisika_block)

        with open(app_js_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[CBT INTEGRATOR] ✅ Fisika added to app.js SUBJECT_CATALOG!")
    else:
        print("[CBT INTEGRATOR] Fisika already present in app.js")

def update_index_html():
    idx_path = os.path.join(BASE_DIR, "index.html")
    with open(idx_path, "r", encoding="utf-8") as f:
        content = f.read()

    if 'value="fisika"' not in content:
        target = '<option value="geografi">Geografi (Pilihan)</option>'
        replacement = '<option value="geografi">Geografi (Pilihan)</option>\n            <option value="fisika">Fisika (Pilihan)</option>'
        if target in content:
            content = content.replace(target, replacement)
            with open(idx_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("[CBT INTEGRATOR] ✅ Fisika option added to index.html subjectSelect!")
    else:
        print("[CBT INTEGRATOR] Fisika option already present in index.html")

def run_all_integrations():
    print("[CBT INTEGRATOR] Starting Phase 5 Ingestion Pipeline...")

    # 1. Geografi Paket 2
    build_learning_dataset(
        slug="geografi_paket_2",
        subject_key="geografi",
        paket_num=2,
        html_path=os.path.join(BASE_DIR, "data", "geografi", "paket_2", "geografi_paket_2.html"),
        kunci_path=os.path.join(BASE_DIR, "data", "kunci", "geografi_paket_2_kunci.json"),
        solutions_path=os.path.join(BASE_DIR, "data", "solution_sources", "GEO_PAKET_2_SOLUTIONS.json"),
        raw_json_out=os.path.join(BASE_DIR, "data", "geografi", "paket_2", "geografi_paket_2.json"),
        learning_json_out=os.path.join(BASE_DIR, "data", "geografi_paket_2_learning.json")
    )

    # 2. Fisika Paket 1
    build_learning_dataset(
        slug="fisika_paket_1",
        subject_key="fisika",
        paket_num=1,
        html_path=os.path.join(BASE_DIR, "data", "fisika", "paket_1", "fisika_paket_1.html"),
        kunci_path=os.path.join(BASE_DIR, "data", "kunci", "fisika_paket_1_kunci.json"),
        solutions_path=os.path.join(BASE_DIR, "data", "solution_sources", "FISIKA_PAKET_1_SOLUTIONS.json"),
        raw_json_out=os.path.join(BASE_DIR, "data", "fisika", "paket_1", "fisika_paket_1.json"),
        learning_json_out=os.path.join(BASE_DIR, "data", "fisika_paket_1_learning.json")
    )

    # 3. Fisika Paket 2
    build_learning_dataset(
        slug="fisika_paket_2",
        subject_key="fisika",
        paket_num=2,
        html_path=os.path.join(BASE_DIR, "data", "fisika", "paket_2", "fisika_paket_2.html"),
        kunci_path=os.path.join(BASE_DIR, "data", "kunci", "fisika_paket_2_kunci.json"),
        solutions_path=os.path.join(BASE_DIR, "data", "solution_sources", "FISIKA_PAKET_2_SOLUTIONS.json"),
        raw_json_out=os.path.join(BASE_DIR, "data", "fisika", "paket_2", "fisika_paket_2.json"),
        learning_json_out=os.path.join(BASE_DIR, "data", "fisika_paket_2_learning.json")
    )

    # 4. Registry & Web Frontend
    update_registry()
    update_app_js()
    update_index_html()

    print("\n[CBT INTEGRATOR] 🚀 ALL 3 DATASETS COMPILED & LIVE IN CBT PLATFORM!")

if __name__ == "__main__":
    run_all_integrations()
