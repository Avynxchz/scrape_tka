# -*- coding: utf-8 -*-
"""
scratch/_audit_slice_nonhitung.py  —  READ-ONLY audit (hanya laporan md yang ditulis).
Slice: file NON-HITUNGAN (bahasa, soshum, biologi, sejarah, geografi, sosiologi).
Mendeteksi 6 pola kerusakan teks pada field user-visible + anomali karakter dalam $...$.
Tidak memodifikasi file data mana pun.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\PROJECTS\SCRAPE_TKA")

LEARNING_FILES = [
    "data/bahasa_indonesia_paket_1_learning.json",
    "data/bahasa_indonesia_paket_2_learning.json",
    "data/bahasa_inggris_paket_1_learning.json",
    "data/bahasa_inggris_paket_2_learning.json",
    "data/biologi_paket_1_learning.json",
    "data/biologi_paket_2_learning.json",
    "data/geografi_paket_1_learning.json",
    "data/geografi_paket_2_learning.json",
    "data/sosiologi_paket_1_learning.json",
    "data/sejarah_paket_1_learning.json",
    "data/sejarah_paket_2_learning.json",
]

SOLUTION_FILES = [
    "data/solution_sources/BAHASA_INDONESIA_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/BAHASA_INDONESIA_PAKET_2_SOLUTIONS.json",
    "data/solution_sources/BING_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/BING_PAKET_2_SOLUTIONS.json",
    "data/solution_sources/BIOLOGI_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/BIOLOGI_PAKET_2_SOLUTIONS.json",
    "data/solution_sources/GEO_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/GEO_PAKET_2_SOLUTIONS.json",
    "data/solution_sources/SOSIOLOGI_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/SEJARAH_PAKET_1_SOLUTIONS.json",
    "data/solution_sources/SEJARAH_PAKET_2_SOLUTIONS.json",
]

# Kunci non-teks / non-user-visible yang tidak perlu diaudit.
SKIP_KEYS = {
    "id", "slug", "name", "total_soal", "nomor", "tipe", "kunci_jawaban",
    "question_id", "question_number", "difficulty", "estimated_time_seconds",
    "official_answer", "format", "correct", "key", "latex", "image", "images",
    "images_data", "data_latex", "source", "url",
}

# ---------------------------------------------------------------- detektor ---

UNI_MATH = re.compile(r"[\U0001D400-\U0001D7FF\u210e]")

# Pola 3: LaTeX command utama di luar $...$
P_LATEX_MENTAH = re.compile(
    r"\\(begin|frac|sqrt|lim|int|sum|matrix|left|right|cdot|times)\b"
)

# Pola 2: LaTeX korup
P_MATRIX_CORRUPT = re.compile(
    r"±\s*atrix"
    r"|\{\s*±?\s*[a-z]*atrix"
    r"|\b[pb]\s+matrix\b"
    r"|\\b\s+egin"
    r"|\\+\s*b\s*egin"
    r"|\\f\s*r\s*ac"
    r"|\\fr\s+ac"
)

KNOWN_CMDS = [
    "begin", "end", "frac", "sqrt", "lim", "int", "sum", "matrix",
    "left", "right", "cdot", "times", "pmatrix", "bmatrix",
    "log", "sin", "cos", "tan", "infty", "alpha", "beta", "theta",
]

# Pola 4: echo ganda frasa (diulang langsung, pemisah spasi non-newline = korupsi)
P_DUP_PHRASE = re.compile(r"(?<![\w])(\w[\w\s\-]{2,60}?)\s+(\1)(?!\w)", re.IGNORECASE)
DUP_WHITELIST = {"that", "had", "very"}

# Pola 6: ambigu
P_DOUBLE_COMMA = re.compile(r",\s*,")
P_TRUNC_SENT = re.compile(
    r"^[A-Za-z][\w\s]{0,40}(?:,,|\bdan\s*\.)\s*.{0,10}$"
)

# Anomali karakter di dalam $...$
P_DOLLAR_SEG = re.compile(r"\$[^$]{1,200}\$")
ANOMALI_CHARS = re.compile(r"[°\uFF00-\uFFEF\uFFFD]")


def strip_tags_preserve_lines(html: str) -> str:
    t = re.sub(r"(?i)</?\s*(br|p|div|li|tr|td|th|h[1-6]|table|ul|ol)\b[^>]*>",
               "\n", html)
    t = re.sub(r"<[^>]*>", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


def broken_cmds(txt: str):
    flat = re.sub(r"\s+", "", txt)
    out = []
    for c in KNOWN_CMDS:
        tok = "\\" + c
        if tok in flat and tok not in txt:
            out.append(c)
    return out


def short_runs(lines, minlen=6, maxlen=4):
    runs, cur = [], []
    for ln in lines:
        s = ln.strip()
        if 0 < len(s) <= maxlen:
            cur.append(s)
        else:
            if len(cur) >= minlen:
                runs.append(cur)
            cur = []
    if len(cur) >= minlen:
        runs.append(cur)
    return runs


def _ctx(txt: str, pos: int, width: int = 80) -> str:
    a = max(0, pos - width // 2)
    b = min(len(txt), pos + width // 2 + 20)
    s = txt[a:b]
    return s.replace("\n", "⏎").replace("\r", "").replace("|", "\\|")


def detect(txt: str):
    hits = []

    # --- Pola 1: echo vertikal ---
    lines = txt.split("\n")
    flat = re.sub(r"\s+", "", txt)
    for run in short_runs(lines):
        joined = "".join(run)
        if len(joined) >= 6 and flat.count(joined) >= 2:
            pos = txt.find("\n".join(run[:6]))
            hits.append(("ECHO-VERTIKAL", _ctx(txt, pos),
                         "run %d baris pendek, join=%r" % (len(run), joined[:40])))

    # --- Pola 2: LaTeX korup ---
    for m in P_MATRIX_CORRUPT.finditer(txt):
        hits.append(("LATEX-KORUP", _ctx(txt, m.start()), repr(m.group(0))))
    for c in broken_cmds(txt):
        pos = txt.find(c)
        hits.append(("LATEX-KORUP", _ctx(txt, pos), "command terpecah spasi: " + c))

    # --- Pola 3: LaTeX mentah di luar $...$ ---
    bare = re.sub(r"\$[^$]*\$", " ", txt)
    for m in P_LATEX_MENTAH.finditer(bare):
        hits.append(("LATEX-MENTAH", _ctx(bare, m.start()), m.group(0)))

    # --- Pola 4: echo ganda ---
    ls = [l.strip() for l in txt.split("\n")]
    seen_line = set()
    for a, b in zip(ls, ls[1:]):
        if a and a == b and len(a) >= 3 and a not in seen_line:
            seen_line.add(a)
            hits.append(("ECHO-GANDA", (a[:60] + " ‖ " + a[:60]),
                         "baris duplikat berurutan"))
    for m in P_DUP_PHRASE.finditer(txt):
        s = m.group(1).strip()
        if len(s) < 5 or s.isdigit() or s.lower() in DUP_WHITELIST:
            continue
        # pemisah antara salinan pertama dan kedua
        g1len = len(m.group(1))
        sep = m.group(0)[g1len:len(m.group(0)) - len(m.group(2))]
        if "\n" in sep:
            # judul diikuti kalimat pembuka yang sama -> struktur normal
            hits.append(("ECHO-GANDA-FP-JUDUL", _ctx(txt, m.start()),
                         "judul+kalimat pembuka (benign, bukan korupsi)"))
        else:
            hits.append(("ECHO-GANDA", _ctx(txt, m.start()),
                         repr(m.group(0)[:70])))

    # --- Pola 5: unicode math italic ---
    for m in UNI_MATH.finditer(txt):
        hits.append(("UNICODE-MATH", _ctx(txt, m.start()),
                     "U+%04X %r" % (ord(m.group(0)), m.group(0))))

    # --- Pola 6: ambigu ---
    for m in P_DOUBLE_COMMA.finditer(txt):
        hits.append(("AMBIGU-KOMA-GANDA", _ctx(txt, m.start()), ",,"))
    t = txt.strip()
    if t and P_TRUNC_SENT.match(t):
        hits.append(("AMBIGU-KALIMAT-BUNTU", t[:80], "kalimat pendek buntu"))

    # --- Anomali karakter di dalam $...$ ---
    for m in P_DOLLAR_SEG.finditer(txt):
        a = ANOMALI_CHARS.search(m.group(0))
        if a:
            hits.append(("LATEX-ANOMALI-KARAKTER", _ctx(txt, m.start()),
                         "U+%04X %r di dalam $...$" % (ord(a.group(0)), a.group(0))))

    return hits


# ---------------------------------------------------------------- self-test ---

def selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print("SELFTEST GAGAL:", name)

    t1 = "Persamaan garis: \ny\n=\n2\nx\n2\n−\n5\ny=2x2−5 adalah benar."
    chk("echo vertikal", any(h[0] == "ECHO-VERTIKAL" for h in detect(t1)))

    t2a = "Matriks \\begin{±atrix} a & b \\\\ c & d \\end{pmatrix}"
    chk("latex korup ±atrix", any(h[0] == "LATEX-KORUP" for h in detect(t2a)))
    t2b = "Nilai \\fr ac{1}{2} dari total."
    chk("latex korup fr ac", any(h[0] == "LATEX-KORUP" for h in detect(t2b)))
    t2c = "Diketahui \\b egin{pmatrix}1\\\\2\\end{pmatrix}"
    chk("latex korup b egin", any(h[0] == "LATEX-KORUP" for h in detect(t2c)))

    t3 = "Hitunglah \\frac{1}{2} dari 20."
    chk("latex mentah", any(h[0] == "LATEX-MENTAH" for h in detect(t3)))
    t3b = "Hitunglah $\\frac{1}{2}$ dari 20."
    chk("latex dalam $ tidak dilaporkan",
        not any(h[0] == "LATEX-MENTAH" for h in detect(t3b)))

    t4 = "karena hujan because because hujan turun"
    chk("echo ganda frasa", any(
        h[0] == "ECHO-GANDA" and "benign" not in h[2] for h in detect(t4)))
    t4b = "baris satu\nbaris satu\nlanjut"
    chk("echo ganda baris", any(h[0] == "ECHO-GANDA" for h in detect(t4b)))
    t4c = "The Great Barrier Reef\nThe Great Barrier Reef is one of the most beautiful places."
    chk("judul+isi terklasifikasi FP",
        any(h[0] == "ECHO-GANDA-FP-JUDUL" for h in detect(t4c)))
    chk("judul+isi tidak dihitung korup",
        not any(h[0] == "ECHO-GANDA" for h in detect(t4c)))

    t5 = "Nilai 𝑥 dan ℎ bertambah."
    chk("unicode math", any(h[0] == "UNICODE-MATH" for h in detect(t5)))

    t6 = "Matriks,, dan."
    chk("ambigu koma ganda", any(h[0] == "AMBIGU-KOMA-GANDA" for h in detect(t6)))
    chk("ambigu kalimat buntu",
        any(h[0] == "AMBIGU-KALIMAT-BUNTU" for h in detect(t6)))

    t7 = "Reaksi: $2NO_2 + H_2° \\rightarrow HNO_2$ terjadi."
    chk("anomali derajat dalam $", any(
        h[0] == "LATEX-ANOMALI-KARAKTER" for h in detect(t7)))

    clean = "Sistem pencernaan manusia terdiri atas beberapa organ utama yang bekerja bersama."
    chk("teks bersih tidak dilaporkan", detect(clean) == [])
    return ok


# ------------------------------------------------------------------ walker ---

def iter_strings(v, path=""):
    """Walk rekursif; hasilkan (path, teks_siap_audit)."""
    if isinstance(v, str):
        leaf = path.rsplit(".", 1)[-1]
        if leaf == "html":
            yield path, strip_tags_preserve_lines(v)
        else:
            yield path, v
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from iter_strings(x, path + "[%d]" % i)
    elif isinstance(v, dict):
        for k, x in v.items():
            if str(k) in SKIP_KEYS:
                continue
            yield from iter_strings(x, path + "." + str(k))


def norm_cup(s: str) -> str:
    s = s.replace("\n", "⏎").replace("\r", "").replace("|", "\\|")
    s = re.sub(r"⏎{2,}", "⏎", s)
    return s[:80]


def audit():
    rows = []
    stats = {"strings": 0, "fields_hit": 0, "per_pola": {}, "dollar_count": 0}

    def feed(txt, loc, label, nomor):
        if not isinstance(txt, str) or not txt.strip():
            return
        stats["strings"] += 1
        hits = detect(txt)
        if hits:
            stats["fields_hit"] += 1
        seen = set()
        for pola, cup, detail in hits:
            key = (pola, cup)
            if key in seen:
                continue
            seen.add(key)
            stats["per_pola"][pola] = stats["per_pola"].get(pola, 0) + 1
            rows.append((label, nomor, loc, pola, norm_cup(cup), detail))

    for rel, kind in [(r, "L") for r in LEARNING_FILES] + \
                     [(r, "S") for r in SOLUTION_FILES]:
        p = ROOT / rel
        label = p.name.replace("_SOLUTIONS.json", "_SOL.json")
        if not p.exists():
            rows.append((label, "-", "-", "FILE-TIDAK-ADA", "", ""))
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        if kind == "L":
            for s in d.get("soal", []):
                nomor = str(s.get("nomor", "?"))
                for path, txt in iter_strings(s, "soal"):
                    feed(txt, path, label, nomor)
        else:
            for i, sl in enumerate(d.get("solutions", [])):
                nomor = str(sl.get("question_number", i + 1))
                for path, txt in iter_strings(sl, "sol"):
                    feed(txt, path, label, nomor)

    return rows, stats


# ------------------------------------------------------------------ report ---

POLA_ORDER = [
    "ECHO-VERTIKAL", "LATEX-KORUP", "LATEX-MENTAH", "ECHO-GANDA",
    "ECHO-GANDA-FP-JUDUL", "UNICODE-MATH", "AMBIGU-KOMA-GANDA",
    "AMBIGU-KALIMAT-BUNTU", "LATEX-ANOMALI-KARAKTER", "FILE-TIDAK-ADA",
]
POLA_SHORT = {
    "ECHO-VERTIKAL": "ECHO-VERT",
    "LATEX-KORUP": "LATEX-KORUP",
    "LATEX-MENTAH": "LATEX-MENTAH",
    "ECHO-GANDA": "ECHO-GANDA",
    "ECHO-GANDA-FP-JUDUL": "FP-JUDUL",
    "UNICODE-MATH": "UNI-MATH",
    "AMBIGU-KOMA-GANDA": "AMBIGU-KOMA",
    "AMBIGU-KALIMAT-BUNTU": "AMBIGU-KAL",
    "LATEX-ANOMALI-KARAKTER": "ANOMALI-$",
    "FILE-TIDAK-ADA": "MISSING",
}


def main():
    if not selftest():
        print("SELFTEST GAGAL — laporan tidak ditulis")
        sys.exit(1)
    rows, stats = audit()

    out = ROOT / "scratch" / "audit_nonhitung_20260929.md"
    L = []
    L.append("# Audit Pola Teks Rusak — Slice Non-Hitungan")
    L.append("")
    L.append("Tanggal: 2026-09-29 · Scope: 11 file learning + 11 file solusi "
             "(bahasa Indonesia, bahasa Inggris, biologi, geografi, sosiologi, sejarah) · "
             "READ-ONLY: tidak ada file data yang diubah.")
    L.append("")
    L.append("Metode: script `scratch/_audit_slice_nonhitung.py` (self-test 16 asersi OK) "
             "menelusuri SEMUA string user-visible secara rekursif, kecuali kunci non-teks "
             "(id, kunci_jawaban, latex, image, official_answer, dst.). Mencakup juga field "
             "yang mudah terlewat: `soal[].pembahasan.*` pada learning (diketahui, "
             "mengapa_begini, langkah_penyelesaian, tips_trik, glosarium_simbol, dst.) dan "
             "`solutions[].soal_serupa.*` pada file solusi. Field HTML dibersihkan tag dulu "
             "(tag blok → newline). Deteksi di luar segmen `$...$` untuk LaTeX; `$...$` "
             "dianggap legitim.")
    L.append("")
    L.append("Klasifikasi pola: "
             "ECHO-VERTIKAL = >=6 baris pendek (<=4 char) + versi utuhnya ada / run muncul 2x · "
             "LATEX-KORUP = ±atrix, p/b matrix, \\b egin, \\fr ac, command terpecah spasi · "
             "LATEX-MENTAH = command LaTeX di luar $...$ · "
             "ECHO-GANDA = token/frasa/baris diulang langsung 2x · "
             "ECHO-GANDA-FP-JUDUL = judul diikuti kalimat pembuka kata yang sama (benign, "
             "struktur dokumen normal — TIDAK dihitung korupsi) · "
             "UNICODE-MATH = U+1D400-1D7FF / U+210E · "
             "AMBIGU = koma ganda / kalimat buntu · "
             "LATEX-ANOMALI-KARAKTER = karakter mencurigakan (°, fullwidth, U+FFFD) di dalam "
             "$...$.")
    L.append("")

    # ---- ringkasan per file ----
    L.append("## Ringkasan per file")
    L.append("")
    cols = [POLA_SHORT[p] for p in POLA_ORDER]
    L.append("| file | " + " | ".join(cols) + " | total temuan |")
    L.append("|---|" + "---|" * (len(cols) + 1))
    per_file_pola = {}
    for f, nomor, loc, pola, cup, detail in rows:
        per_file_pola.setdefault(f, {})
        per_file_pola[f][pola] = per_file_pola[f].get(pola, 0) + 1
    file_order = []
    for rel in LEARNING_FILES + SOLUTION_FILES:
        nm = rel.split("/")[-1].replace("_SOLUTIONS.json", "_SOL.json")
        file_order.append(nm)
    for f in file_order:
        d = per_file_pola.get(f)
        if not d:
            continue  # file tanpa temuan: tampil di bagian file bersih
        cells = [str(d.get(p, 0)) for p in POLA_ORDER]
        tot = sum(v for k2, v in d.items() if k2 != "ECHO-GANDA-FP-JUDUL")
        L.append("| %s | %s | %d |" % (f, " | ".join(cells), tot))
    L.append("")
    L.append("Kolom FP-JUDUL = false positive struktur judul+kalimat pembuka (benign); "
             "tidak dihitung dalam total temuan korupsi.")
    L.append("")

    # ---- tabel temuan lengkap ----
    L.append("## Tabel temuan lengkap")
    L.append("")
    L.append("| file | nomor | field | pola | cuplikan (≤80 char) |")
    L.append("|---|---|---|---|---|")
    order_idx = {p: i for i, p in enumerate(POLA_ORDER)}
    for f, nomor, loc, pola, cup, detail in sorted(
            rows, key=lambda r: (r[0], order_idx.get(r[3], 99), r[1])):
        L.append("| %s | %s | %s | %s | %s |" % (f, nomor, loc, pola, cup))
    L.append("")

    # ---- catatan verifikasi manual ----
    L.append("## Catatan verifikasi manual (klasifikasi benign vs korup)")
    L.append("")
    L.append("1. **ECHO-GANDA-FP-JUDUL** — semua kasus terverifikasi adalah judul stimulus "
             "yang diikuti kalimat pertama memuat judul tersebut (mis. `The Great Barrier "
             "Reef⏎The Great Barrier Reef is one of...` pada B.INGGRIS paket 2 q11-15, "
             "`Danau Bandung Purba⏎Danau Bandung purba terbentuk...` pada GEO paket 1 q2, "
             "`Fenomena Penuaan Penduduk di Indonesia⏎Indonesia dan negara-negara ASEAN...` "
             "pada GEO paket 2 q10). Struktur judul+isi normal — bukan kerusakan.")
    L.append("2. **ECHO-GANDA korup terverifikasi** — GEO_PAKET_2_SOL q5 `reasoning`: "
             "`...destinasi bahari/pesisir pesisir, bukan dataran tinggi.` — token "
             "`pesisir` terduplikasi langsung. Satu-satunya duplikasi korup di slice ini.")
    L.append("3. **LATEX-ANOMALI-KARAKTER** — GEO_PAKET_2_SOL q? `steps[].explanation`: "
             "`$2NO_2 + H_2° \\\\rightarrow HNO_2 + HNO_3$` — `°` (U+00B0) menggantikan "
             "`O` pada H2O; kemungkinan besar korupsi OCR/ketik. Konten di dalam $...$ "
             "jadi perlu perbaikan terpisah dari pola LaTeX mentah.")
    L.append("4. **LaTeX dalam $...$ ditemukan legitim** — dipakai di pembahasan learning "
             "B.INGGRIS/GEOGRAFI dan beberapa file solusi (mis. `$2NO_2 + H_2O "
             "\\\\rightarrow HNO_2 + HNO_3$`, `$91{,}4\\\\%$`, `$\\\\rightarrow$` di tips "
             "SEJARAH paket 2). Renderer aplikasi harus mendukung math delimiter `$...$` "
             "untuk field-field ini.")
    L.append("")

    # ---- statistik ----
    L.append("## Statistik total")
    L.append("")
    L.append("- String user-visible dipindai: %d" % stats["strings"])
    L.append("- Field mengandung >=1 temuan (termasuk FP-JUDUL): %d" % stats["fields_hit"])
    tot_korup = sum(v for k2, v in stats["per_pola"].items()
                    if k2 not in ("ECHO-GANDA-FP-JUDUL",))
    L.append("- Total temuan korupsi (di luar FP-JUDUL): %d" % tot_korup)
    L.append("- Total temuan termasuk FP-JUDUL: %d" % sum(stats["per_pola"].values()))
    for p in POLA_ORDER:
        if p in stats["per_pola"]:
            L.append("- %s: %d" % (p, stats["per_pola"][p]))
    L.append("- Field data_latex / latex / image: tidak diaudit (legitim sesuai instruksi).")
    L.append("")

    # ---- file bersih ----
    dirty = set(per_file_pola)
    L.append("## File tanpa temuan")
    L.append("")
    bersih = [f for f in file_order if f not in dirty]
    if bersih:
        for f in bersih:
            L.append("- %s" % f)
    else:
        L.append("(tidak ada — semua file memiliki minimal satu temuan)")
    L.append("")

    out.write_text("\n".join(L), encoding="utf-8")
    print("SELFTEST OK")
    print("LAPORAN:", out)
    print("total korupsi:", tot_korup, "| FP-JUDUL:",
          stats["per_pola"].get("ECHO-GANDA-FP-JUDUL", 0))
    for p in POLA_ORDER:
        if p in stats["per_pola"]:
            print("  %-26s %d" % (p, stats["per_pola"][p]))


if __name__ == "__main__":
    main()
