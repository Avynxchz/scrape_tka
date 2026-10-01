# -*- coding: utf-8 -*-
r"""_audit_math_quality.py — Deteksi & perbaikan otomatis kualitas tampilan math.

Masalah yang dibereskan (laporan boss):
  1. Kode LaTeX mentah bocor ke tampilan user (\frac, \lim, \left, \right, ^)
     tanpa delimiter $...$ sehingga tampil sebagai teks, bukan simbol.
  2. Artefak perataan KaTeX: glyph italic (ℎ), suku kata terpecah (f rac,
     r igℎt), eksponen rata (x 3 padahal harusnya x³).
  3. Diketahui ambigu seperti "Matriks,, dan." / "Matriks dan matriks." —
     isi rumus hilang; diisi dari transkripsi sidecar gambar soal.

Prinsip: teks di dalam $...$ adalah LaTeX utuh (KaTeX merendernya) — jangan
disentuh. Yang diperbaiki hanya LaTeX bocor DI LUAR $...$.
"""
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_quality  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SOL_DIR = os.path.join(DATA_DIR, "solution_sources")

# --- Deteksi -----------------------------------------------------------------
# Perintah LaTeX yang wajib dirender, kalau muncul di luar $...$ = bocor
LATEX_CMDS = re.compile(
    r"\\(?:frac|dfrac|tfrac|lim|left|right|sqrt|sum|int|prod|theta|pi|alpha|beta|"
    r"gamma|delta|cdot|times|approx|neq|leq|geq|pm|infty|rightarrow|log|sin|cos|tan)\b"
)
# Karakter/konstruksi artefak perataan KaTeX
ITALIC_H = "\u210E"                                     # ℎ (Planck h dari \right/\theta)
FLATTEN = re.compile(r"\bf\s*rac\b|\bl\s*eft\b|\br\s*i\s*g\s*h\s*t\b")
LOOSE_EXP = re.compile(r"(?<=[a-zA-Z0-9\)\]])\s(\d{1,2})(?=\s|$|[+\-<),.;])")  # "x 3" → x^3 kandidat

# Diketahui ambigu/bercagak: diawali kata pembuka tapi TANPA isi math/angka
# (menangkap "Matriks dan matriks.", "Matriks,, dan.", "Matriks \n , \n , dan .")
AMBIG_DIK = re.compile(
    r"^\s*(?:matriks|fungsi|grafik|gamb|persamaan|titik|segitiga|vektor)[a-z\s,.:;()\-]*$",
    re.I,
)

# Pembuka meta AI pada transkripsi sidecar yang tidak layak tampil ke siswa.
# Umum: baris apa pun yang memuat 'transkripsi' dan diakhiri ':' —
# "Berikut adalah transkripsi teks dan rumus matematika dari gambar:",
# "Berikut adalah analisis dan transkripsi elemen-elemen dari gambar:", dll.
META_PREAMBLE = re.compile(r"^\s*[^\n]*transkripsi[^\n:]*:\s*", re.I)


def strip_meta_preamble(text):
    """Lepas pembuka meta AI ('Berikut adalah transkripsi ...:') dari teks."""
    if not text:
        return text
    prev = None
    while prev != text:
        prev = text
        text = META_PREAMBLE.sub("", text, count=1).strip()
    return text


def _segments(text):
    r"""Pecah teks jadi [(in_math, segmen)]. $$...$$ dan $...$ = math.

    $$...$$ dicoba lebih dulu agar display math tidak salah potong.
    """
    parts = re.split(r"(\$\$[\s\S]*?\$\$|\$[^$]*?\$)", text)
    out = []
    for p in parts:
        if p.startswith("$$") and p.endswith("$$") and len(p) > 3:
            out.append((True, p))
        elif p.startswith("$") and p.endswith("$") and len(p) > 1:
            out.append((True, p))
        elif p:
            out.append((False, p))
    return out


def detect_issues(text):
    """Return dict hitungan masalah pada satu field teks."""
    if not text or not isinstance(text, str):
        return {}
    issues = {}
    for in_math, seg in _segments(text):
        if in_math:
            continue
        n_cmd = len(LATEX_CMDS.findall(seg))
        if n_cmd:
            issues["latex_mentah"] = issues.get("latex_mentah", 0) + n_cmd
        if ITALIC_H in seg:
            issues["ital_h"] = issues.get("ital_h", 0) + seg.count(ITALIC_H)
        if FLATTEN.search(seg):
            issues["flatten"] = issues.get("flatten", 0) + len(FLATTEN.findall(seg))
    return issues


def wrap_bare_latex(text):
    """Bungkus LaTeX bocor (di luar $...$) dengan $...$ agar KaTeX merendernya.

    Segmen non-math yang mengandung perintah LaTeX dipisah: potongan sebelum
    perintah pertama & sesudah perintah terakhir tetap teks; bagian berisi
    perintah dibungkus $...$.
    """
    if not text or not isinstance(text, str):
        return text
    out = []
    for in_math, seg in _segments(text):
        if in_math or not LATEX_CMDS.search(seg):
            out.append(seg)
            continue
        # Cari rentang yang berisi perintah LaTeX: dari 2 char sebelum perintah
        # pertama sampai akhir perintah terakhir, lalu bungkus.
        first = LATEX_CMDS.search(seg)
        last = None
        for last in LATEX_CMDS.finditer(seg):
            pass
        start = max(0, first.start() - 1)
        end = min(len(seg), last.end() + 1)
        pre, mid, post = seg[:start], seg[start:end], seg[end:]
        mid = re.sub(r"\s+", " ", mid).strip()
        out.append(pre + " $" + mid + "$ " + post)
    res = "".join(out)
    return re.sub(r"\s{2,}", " ", res).strip()


def repair_text(text):
    """Perbaikan lengkap satu field: pangkat rata + LaTeX bocor dibungkus $."""
    if not text or not isinstance(text, str):
        return text
    text = text_quality.repair_math_text(text)
    text = wrap_bare_latex(text)
    return text


def repair_solution_doc(doc, sidecar_lookup=None):
    """Perbaiki seluruh field teks dokumen solusi. Return jumlah perbaikan."""
    n = 0
    for s in doc.get("solutions", []):
        for fld in ("question_title", "diketahui", "ditanyakan", "reasoning", "why_correct"):
            if s.get(fld):
                s[fld] = repair_text(s[fld])
                n += 1
        for st in s.get("steps") or []:
            for fld in ("title", "explanation"):
                if st.get(fld):
                    st[fld] = repair_text(st[fld])
                    n += 1
        for k in ("tips", "common_mistakes"):
            s[k] = [repair_text(x) if isinstance(x, str) else x for x in (s.get(k) or [])]

        # Diketahui ambigu → isi dari transkripsi sidecar gambar soal.
        # Ambigu = diawali kata pembuka tapi TANPA angka/rumus/LaTeX sama sekali.
        dik = (s.get("diketahui") or "").strip()
        dik_core = re.sub(r"\$[^$]*\$", "RUMUS", dik)  # buang LaTeX valid dari hitungan
        if sidecar_lookup and len(dik_core) < 60 and AMBIG_DIK.match(dik_core):
            qno = s.get("question_number")
            texts = sidecar_lookup.get(qno) or []
            pick = None
            for t in texts:
                if t and (LATEX_CMDS.search(t) or re.search(r"\d", t)):
                    pick = t
                    break
            if pick:
                s["diketahui"] = text_quality.repair_math_text(strip_meta_preamble(pick))
                n += 1
        elif sidecar_lookup and dik and "transkripsi" in dik.lower()[:40]:
            # sudah diisi sidecar sebelumnya tapi pembuka metanya masih menempel
            cleaned = strip_meta_preamble(dik)
            if cleaned != dik:
                s["diketahui"] = cleaned
                n += 1
    return n


def build_sidecar_lookup(slug, learning_path):
    """Map nomor soal -> daftar deskripsi sidecar gambar-gambar soal itu."""
    lookup = {}
    try:
        lrn = json.load(open(learning_path, encoding="utf-8"))
    except Exception:
        return lookup
    sc_path = os.path.join(DATA_DIR, f"{slug}_sidecar_transcriptions.json")
    try:
        sidecar = json.load(open(sc_path, encoding="utf-8"))
    except Exception:
        return lookup
    for q in lrn.get("soal", []):
        imgs = (q.get("stimulus", {}).get("images") or []) + (q.get("pertanyaan", {}).get("images") or [])
        descs = []
        for im in imgs:
            fn = im.get("filename")
            if fn and fn in sidecar:
                descs.append(sidecar[fn].get("description", ""))
        if descs:
            lookup[q["nomor"]] = descs
    return lookup


def main():
    print("=== AUDIT & REPAIR KUALITAS MATH ===")
    total_repaired = 0
    for fn in sorted(os.listdir(SOL_DIR)):
        if not fn.endswith(".json") or fn == "registry.json":
            continue
        path = os.path.join(SOL_DIR, fn)
        d = json.load(open(path, encoding="utf-8"))
        slug = d.get("slug") or fn.replace("_SOLUTIONS.json", "").lower()
        # slug learning: cari file learning yang cocok via registry key mapping terbalik
        lrn_path = os.path.join(DATA_DIR, f"{_guess_slug(fn)}_learning.json")
        lookup = build_sidecar_lookup(_guess_slug(fn), lrn_path) if os.path.isfile(lrn_path) else {}

        # hitung issue sebelum repair
        n_issue = 0
        for s in d.get("solutions", []):
            blob = " | ".join([str(s.get("diketahui") or ""), str(s.get("ditanyakan") or ""),
                               str(s.get("reasoning") or ""), str(s.get("why_correct") or "")] +
                              [str(x.get("explanation") or "") for x in s.get("steps", [])])
            n_issue += sum(detect_issues(blob).values())

        n = repair_solution_doc(d, lookup)
        if n:
            json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        total_repaired += n
        flag = "REPAIR" if n else ("ISSUE" if n_issue else "clean ")
        print(f"[{flag}] {fn}: issue={n_issue}, repaired={n}")
    print(f"\nSELESAI. Total field diperbaiki: {total_repaired}")


def _guess_slug(solution_fn):
    """MATEMATIKA_LANJUT_PAKET_1_SOLUTIONS.json -> matematika_lanjut_paket_1."""
    base = solution_fn.replace("_SOLUTIONS.json", "").lower()
    return base


if __name__ == "__main__":
    main()
