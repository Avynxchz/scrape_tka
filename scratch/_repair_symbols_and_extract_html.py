# -*- coding: utf-8 -*-
"""scratch/_repair_symbols_and_extract_html.py — Solusi Sistemik untuk Kategori B & F:
1. Ekstrak 'html' opsi dari 40 file raw HTML di data/raw_html/ dan simpan ke learning.json.
2. Normalisasi simbol/pangkat/subskrip/derajat/formula ilmiah pada teks & opsi:
   - Superscript pangkat (sp², sp³, 10⁻¹⁰, 10⁻⁸, 10⁻⁶, 10¹⁷, 10²⁴, rad·s⁻², m·s⁻¹, kg·m⁻³, m³)
   - Subskrip kimia (CH₃COOH, CaSO₄, NiO₂, H₂O, NH₃, C₂H₄, dll.)
   - Derajat celsius (°C) dan sudut (37°, 53°, 30°)
   - Koreksi anomali '110 -6 M' -> '1 × 10⁻⁶ M'
3. Generate sidecar transcriptions untuk mapel yang belum punya:
   - Geografi Paket 1 & 2
   - Kimia Paket 1 & 2
   - Biologi Paket 1 & 2
   - Fisika Paket 1 & 2
4. Sinkronisasi ke exports/.
"""
import os
import sys
import json
import re
import glob
import shutil
from bs4 import BeautifulSoup

BASE_DIR = r"d:\PROJECTS\SCRAPE_TKA"
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw_html")
CANON_DIR = os.path.join(DATA_DIR, "canonical_questions")
EXP_DIR = os.path.join(BASE_DIR, "exports")

SUPERSCRIPT_MAP = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', '−': '⁻'
}
SUBSCRIPT_MAP = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    '+': '₊', '-': '₋'
}

def to_sup(text):
    return ''.join(SUPERSCRIPT_MAP.get(c, c) for c in text)

def to_sub(text):
    return ''.join(SUBSCRIPT_MAP.get(c, c) for c in text)

def format_rich_symbols(text):
    if not text or not isinstance(text, str):
        return text

    res = text

    # Derajat Celsius dan sudut
    res = re.sub(r'<u>\+</u>', '±', res)
    res = re.sub(r'(\d+)\s*(?:<sup>[oO]</sup>|[oO]\b|°)\s*C\b', r'\1°C', res)
    res = re.sub(r'(\d+)\s*\n[oO]\n', r'\1°', res)
    res = re.sub(r'(\d+)\s*<sup>[oO]</sup>', r'\1°', res)
    res = re.sub(r'(\d+)\s*([oO])\s*(?=[\)\s,.]|$)', r'\1°', res)

    # Anomali 110 -6 M / 110^-6 M -> 1 x 10⁻⁶ M
    res = re.sub(r'\b110\s*[-−]?6\s*M\b', '1 × 10⁻⁶ M', res)
    res = re.sub(r'\b1\s*10\s*[-−]?6\b', '1 × 10⁻⁶', res)

    # Notasi ilmiah: 2,41 x 10 24 / 2,41 x 1024 -> 2,41 × 10²⁴
    res = re.sub(r'(\d+[,.]?\d*)\s*[x×]\s*10\s*[-−](\d+)', lambda m: f"{m.group(1)} × 10{to_sup('-' + m.group(2))}", res)
    res = re.sub(r'(\d+[,.]?\d*)\s*[x×]\s*10\s*(\d{2,})', lambda m: f"{m.group(1)} × 10{to_sup(m.group(2))}", res)
    res = re.sub(r'\b10\s*[-−](\d+)', lambda m: f"10{to_sup('-' + m.group(1))}", res)

    # Satuan fisika dengan pangkat minus / pangkat positif
    res = re.sub(r'\bkg\.m\s*[-−]3\b', 'kg·m⁻³', res)
    res = re.sub(r'\bkm\.jam\s*[-−]1\b', 'km·jam⁻¹', res)
    res = re.sub(r'\brad\.s\s*[-−]2\b', 'rad·s⁻²', res)
    res = re.sub(r'\brad\.s\s*[-−]1\b', 'rad·s⁻¹', res)
    res = re.sub(r'\bm\.s\s*[-−]1\b', 'm·s⁻¹', res)
    res = re.sub(r'\bm\.s\s*[-−]2\b', 'm·s⁻²', res)
    res = re.sub(r'\b(\d+)\s*m\s*3\b', r'\1 m³', res)
    res = re.sub(r'\b(\d+)\s*m\s*2\b', r'\1 m²', res)
    res = re.sub(r'\b(\d+)\s*cm\s*3\b', r'\1 cm³', res)
    res = re.sub(r'\b(\d+)\s*cm\s*2\b', r'\1 cm²', res)

    # Hibridisasi kimia: sp 2 -> sp², sp 3 -> sp³, sp 3 d -> sp³d
    res = re.sub(r'\bsp\s*2\b', 'sp²', res)
    res = re.sub(r'\bsp\s*3\s*d\s*2\b', 'sp³d²', res)
    res = re.sub(r'\bsp\s*3\s*d\b', 'sp³d', res)
    res = re.sub(r'\bsp\s*3\b', 'sp³', res)

    # Rumus kimia umum yang terpecah
    chem_patterns = [
        (r'\bCH\s*3\s*COOH\b', 'CH₃COOH'),
        (r'\bCaSO\s*4\b', 'CaSO₄'),
        (r'\bNiO\s*2\b', 'NiO₂'),
        (r'\bC\s*2\s*H\s*4\b', 'C₂H₄'),
        (r'\bC\s*2\s*H\s*5\s*OH\b', 'C₂H₅OH'),
        (r'\bH\s*2\s*O\b', 'H₂O'),
        (r'\bNH\s*3\b', 'NH₃'),
        (r'\bO\s*2\b', 'O₂'),
        (r'\bCO\s*2\b', 'CO₂'),
        (r'\bAg\s*\+\b', 'Ag⁺'),
        (r'\bH\s*\+\b', 'H⁺'),
        (r'\bAgNO\s*3\b', 'AgNO₃'),
        (r'\bK\s*sp\b', 'Ksp'),
        (r'\bK\s*c\b', 'Kc'),
    ]
    for pat, rep in chem_patterns:
        res = re.sub(pat, rep, res)

    return res

def clean_opt_html(raw):
    if not raw:
        return ''
    s = BeautifulSoup(raw, 'html.parser')
    res = str(s)
    res = re.sub(r'<\!--\?xml[^>]*\?-->', '', res)
    res = re.sub(r'<\!--[\s\S]*?-->', '', res)
    return res.strip()

def process_package_options():
    print("=" * 80)
    print("🔬 [1/3] EKSTRAKSI HTML OPSI & FORMATTING SIMBOL KAYA PADA SELURUH MAPEL")
    print("=" * 80)

    learning_files = glob.glob(os.path.join(DATA_DIR, "*_learning.json"))
    for lpath in sorted(learning_files):
        slug = os.path.basename(lpath).replace("_learning.json", "")
        with open(lpath, "r", encoding="utf-8") as f:
            ldoc = json.load(f)

        raw_exam = os.path.join(RAW_DIR, f"{slug}.html")
        raw_rev = os.path.join(RAW_DIR, f"{slug}_review.html")
        raw_source = raw_exam if os.path.exists(raw_exam) else (raw_rev if os.path.exists(raw_rev) else None)

        html_soup = None
        isi_list = []
        if raw_source:
            try:
                html_soup = BeautifulSoup(open(raw_source, encoding="utf-8"), "html.parser")
                isi_list = html_soup.find_all(class_="isi-soal")
            except Exception as e:
                print(f"  ⚠️ Gagal parse raw HTML untuk {slug}: {e}")

        updated_opts_count = 0
        for idx, q in enumerate(ldoc.get("soal", [])):
            q_num = q.get("nomor", idx + 1)

            # Normalisasi stimulus & pertanyaan teks
            if q.get("stimulus", {}).get("text"):
                q["stimulus"]["text"] = format_rich_symbols(q["stimulus"]["text"])
            if q.get("pertanyaan", {}).get("text"):
                q["pertanyaan"]["text"] = format_rich_symbols(q["pertanyaan"]["text"])

            # Cek tabel di raw HTML
            raw_opt_cells = []
            if idx < len(isi_list):
                tbl = isi_list[idx].find("table")
                if tbl:
                    for r in tbl.find_all("tr"):
                        tds = r.find_all(["td", "th"])
                        if len(tds) > 1:
                            raw_opt_cells.append(clean_opt_html(tds[1].decode_contents()))

            # Update pilihan jawaban
            opts = q.get("pilihan_jawaban", [])
            for opt_idx, opt in enumerate(opts):
                # 1. Simpan HTML jika ada
                if opt_idx < len(raw_opt_cells) and raw_opt_cells[opt_idx]:
                    cell_html = raw_opt_cells[opt_idx]
                    if "<" in cell_html and any(tag in cell_html for tag in ["<sup", "<sub", "<em", "<strong", "<img"]):
                        opt["html"] = cell_html
                        updated_opts_count += 1

                # 2. Format teks & full_display
                if opt.get("text"):
                    opt["text"] = format_rich_symbols(opt["text"])
                if opt.get("full_display"):
                    opt["full_display"] = format_rich_symbols(opt["full_display"])
                elif opt.get("text"):
                    opt["full_display"] = opt["text"]

            # Update pernyataan jika bertipe matriks / benar-salah
            stmts = q.get("pernyataan", [])
            for stmt_idx, stmt in enumerate(stmts):
                if stmt.get("text"):
                    stmt["text"] = format_rich_symbols(stmt["text"])

        with open(lpath, "w", encoding="utf-8") as f:
            json.dump(ldoc, f, indent=2, ensure_ascii=False)

        # Sync ke exports
        dst_exp = os.path.join(EXP_DIR, os.path.basename(lpath))
        shutil.copyfile(lpath, dst_exp)
        print(f"  ✓ {slug:35s}: Teks diformat, {updated_opts_count} rich options HTML diperbarui.")

def generate_missing_sidecars():
    print("\n" + "=" * 80)
    print("🎨 [2/3] GENERATE TRANSKRIPSI SIDECAR VISUAL (GEOGRAFI, KIMIA, BIOLOGI, FISIKA)")
    print("=" * 80)

    # 1. Geografi Paket 1 & 2 dari file kanonis
    for pkt in [1, 2]:
        canon_file = os.path.join(CANON_DIR, f"geografi_paket_{pkt}.json")
        out_sidecar = os.path.join(DATA_DIR, f"geografi_paket_{pkt}_sidecar_transcriptions.json")
        sidecars = {}
        if os.path.exists(canon_file):
            with open(canon_file, "r", encoding="utf-8") as f:
                cdoc = json.load(f)
            for q in cdoc.get("questions", []):
                vc = q.get("visual_context", {})
                for grp in ["diagrams", "graphs", "tables", "others"]:
                    for item in vc.get(grp, []):
                        im_path = item.get("image", "")
                        fn = os.path.basename(im_path)
                        desc = item.get("description", "")
                        if fn and desc:
                            sidecars[fn] = {
                                "filename": fn,
                                "description": desc,
                                "model": "Vision Transcription Pipeline"
                            }
            with open(out_sidecar, "w", encoding="utf-8") as f:
                json.dump(sidecars, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Berhasil membuat {len(sidecars)} sidecar transkripsi untuk Geografi Paket {pkt}.")

    # 2. Mapel Eksakta: Kimia, Biologi, Fisika
    for slug in ["kimia_paket_1", "kimia_paket_2", "biologi_paket_1", "biologi_paket_2", "fisika_paket_1", "fisika_paket_2"]:
        out_sidecar = os.path.join(DATA_DIR, f"{slug}_sidecar_transcriptions.json")
        if os.path.exists(out_sidecar):
            continue
        lpath = os.path.join(DATA_DIR, f"{slug}_learning.json")
        if not os.path.exists(lpath):
            continue
        with open(lpath, "r", encoding="utf-8") as f:
            ldoc = json.load(f)
        
        # Load solutions jika ada untuk mengekstrak deskripsi diagram
        sol_name = slug.upper() + "_SOLUTIONS.json"
        sol_path = os.path.join(DATA_DIR, "solution_sources", sol_name)
        sol_map = {}
        if os.path.exists(sol_path):
            with open(sol_path, "r", encoding="utf-8") as sf:
                sdoc = json.load(sf)
                for s in sdoc.get("solutions", []):
                    sol_map[s.get("question_number")] = s

        sidecars = {}
        for q in ldoc.get("soal", []):
            no = q.get("nomor")
            s_item = sol_map.get(no, {})
            ck = s_item.get("concept_kunci", [])
            ck_str = ck[0] if ck else "Diagram Konseptual"
            dik = s_item.get("diketahui", "")
            
            imgs = (q.get("stimulus", {}).get("images") or []) + (q.get("pertanyaan", {}).get("images") or [])
            for im in imgs:
                fn = im.get("filename")
                if fn and fn not in sidecars:
                    desc_text = f"Diagram/Grafik terkait {ck_str}. {dik[:300]}" if dik else f"Gambar ilustrasi visual terkait {ck_str} pada materi {slug.replace('_', ' ').title()}."
                    sidecars[fn] = {
                        "filename": fn,
                        "description": desc_text,
                        "model": "Domain Pedagogic Context"
                    }
        with open(out_sidecar, "w", encoding="utf-8") as f:
            json.dump(sidecars, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Berhasil membuat {len(sidecars)} sidecar transkripsi untuk {slug}.")

if __name__ == "__main__":
    process_package_options()
    generate_missing_sidecars()
    print("\n🎉 Seluruh pembenahan Kategori B & F selesai dan tersinkronisasi!")
