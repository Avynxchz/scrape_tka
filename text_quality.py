# -*- coding: utf-8 -*-
"""text_quality.py — Normalisasi teks hasil ekstraksi DOM soal Pusmendik.

Bug yang dibereskan ("pembahasan aneh"): ekstraksi lama memakai
get_text("\\n", strip=True) yang menyisipkan baris baru di SETIAP batas tag
inline (em, sup, sub, span), sehingga rumus pecah vertikal per karakter:
    "Diketahui fungsi trigonometri\\nf\\n(\\nx\\n) = –3 sin (2x – 30\\nO\\n) + 4"
Model AI pada fase 4 menerima teks rusak ini dalam prompt, meniru gayanya, dan
menambahkan duplikat gaya KaTeX (huruf matematika italic unicode + gema teks
polos), mis. "𝑑\\n𝑒\\n𝑡\\n(\\n𝑃\\n+\\n𝑄\\n)\\ndet(P+Q)".

Pipeline perbaikan (idempoten — teks yang sudah bersih tidak berubah):
  1. Petakan huruf/angka matematika unicode (U+1D400–U+1D7FF) ke ASCII.
  2. Gabungkan rangkaian baris pendek / fragmen matematika jadi satu token.
  3. Normalisasi simbol kata (times/neq/leq/...) per baris.
  4. Buang gema duplikat (baris / rangkaian token yang mengulang sebelumnya).
  5. Susun ulang baris menjadi kalimat dengan aturan "glue" tanda matematika.
  6. Rapikan simbol sisa, derajat terpecah, dan spasi berlebih.
"""
import re
import unicodedata

# Blok Unicode Mathematical Alphanumeric Symbols (huruf/angka italic 𝑑𝑒𝑡 dll.)
_MATH_ALNUM = re.compile(r"[\U0001D400-\U0001D7FF]")

# Simbol kata hasil pecahan KaTeX yang menempel di antara operand
# (tanpa \b: '2times2' tidak punya word boundary antara digit dan huruf)
_WORD_SYMBOLS = [
    (re.compile(r"(?<=[\d\)\}])\s*times\s*(?=[\d\(\{\$])"), "×"),
    (re.compile(r"(?<![\w])(?:times|×)(?=[\d\(])"), "×"),
    (re.compile(r"(?<![\w])neq(?![\w])"), "≠"),
    (re.compile(r"(?<![\w])leq(?![\w])"), "≤"),
    (re.compile(r"(?<![\w])geq(?![\w])"), "≥"),
    (re.compile(r"(?<![\w])pm(?![\w])"), "±"),
    (re.compile(r"(?<![\w])cdot(?![\w])"), "·"),
    (re.compile(r"(?<![\w])approx(?![\w])"), "≈"),
    (re.compile(r"(?<![\w])rightarrow(?![\w])"), "→"),
    (re.compile(r"(?<![\w])leftarrow(?![\w])"), "←"),
]

# Fragmen matematika pendek yang boleh diserap ke dalam run per karakter
# (harus memuat digit/simbol; mencegah kata seperti "sin"/"det" ikut tersedot)
_MATH_FRAGMENT = re.compile(
    r"^(?=.*[\d×±≠≤≥≈·=+\-−()])([\da-zA-Z×±≠≤≥≈·()\[\]{}=+\-−.,:;$°^/\s]{1,8})$"
)

# Gema rumus pendek dalam satu token: "2×22×2" -> "2×2"
_INTRA_ECHO = re.compile(r"(\d+[×±≠≤≥≈·]\d+)\1")

_NO_GLUE_END = set("([{-–—=+/×·≠≤≥≈→±")          # baris sebelumnya diakhiri ini -> tanpa spasi
_NO_GLUE_START = set(")]}-–—=+/×·≠≤≥≈→±,.;:!?%")  # baris berikutnya diawali ini -> tanpa spasi


def map_math_unicode(text):
    """Huruf matematika italic/bold unicode -> ASCII biasa (NFKC per karakter)."""
    if not text:
        return text
    return "".join(
        unicodedata.normalize("NFKC", c) if _MATH_ALNUM.match(c) else c
        for c in text
    )


def _is_run_member(line):
    """Baris pendek / fragmen matematika yang termasuk anggota run pecahan."""
    s = line.strip()
    if 0 < len(s) <= 2:
        return True
    return bool(_MATH_FRAGMENT.match(s))


def _norm_frag(s):
    n = re.sub(r"[\s\$]+", "", s).lower()
    for pat, rep in _WORD_SYMBOLS:
        n = pat.sub(rep, n)
    return n


def merge_fragmented_lines(text):
    """Gabungkan rangkaian baris pecahan jadi satu token utuh per run.

    Contoh: ['2', 't', 'i', 'm', 'e', 's', '2', '2', 'times2', ':']
    -> ['2times22times2:']

    Fragmen yang merupakan pengulangan isi run (gema) tidak diserap —
    dibiarkan jadi baris sendiri supaya dedupe_echo yang membuangnya.
    """
    out_lines = []
    buf = []

    def flush_buf():
        if not buf:
            return
        merged = "".join(x.strip() for x in buf)
        buf.clear()
        if merged:
            out_lines.append(merged)

    for raw in text.split("\n"):
        s = raw.strip()
        if not s:
            flush_buf()
            out_lines.append("")
        elif _is_run_member(s):
            if buf:
                merged = "".join(x.strip() for x in buf)
                # Gema: incoming mengulang isi run (atau sebaliknya) -> jangan serap
                if merged and s and (_norm_frag(s) in _norm_frag(merged)
                                     or _norm_frag(merged) in _norm_frag(s)):
                    flush_buf()
                    out_lines.append(s)
                    continue
            buf.append(s)
        else:
            flush_buf()
            out_lines.append(s)
    flush_buf()
    return out_lines


def fix_word_symbols(text):
    r"""'3times(−2)' -> '3×(−2)', 'a neq b' -> 'a ≠ b', '2×22×2' -> '2×2'.

    Segmen LaTeX di dalam $...$ DILEWATI — \cdot/\times dsb. di sana harus
    utuh karena KaTeX yang merendernya.
    """
    parts = re.split(r"(\$[^$]*\$)", text)
    out = []
    for seg in parts:
        if seg.startswith("$") and seg.endswith("$") and len(seg) > 1:
            out.append(seg)
            continue
        for pat, rep in _WORD_SYMBOLS:
            seg = pat.sub(rep, seg)
        out.append(_INTRA_ECHO.sub(r"\1", seg))
    return "".join(out)


def _norm_for_dedupe(line):
    return _norm_frag(line)


def dedupe_echo(lines):
    """Buang baris yang mengulang ekor baris/rangkaian sebelumnya (gema KaTeX)."""
    out = []
    for line in lines:
        cur = _norm_for_dedupe(line)
        if cur and len(cur) <= 80 and out:
            prev = _norm_for_dedupe(out[-1])
            if cur == prev or (len(prev) >= len(cur) and prev[-len(cur):] == cur):
                continue
        out.append(line)
    return out


def _glue(prev, nxt):
    """Rakit sambungan antar baris: tanpa spasi bila menyambung secara matematis."""
    if not prev or not nxt:
        return ""
    if prev[-1] in _NO_GLUE_END or nxt[0] in _NO_GLUE_START:
        return ""
    return " "


def rebuild_sentences(lines):
    """Susun baris menjadi kalimat; baris kosong = pemisah paragraf."""
    paragraphs = []
    cur = []
    for line in lines:
        if not line.strip():
            if cur:
                paragraphs.append(cur)
                cur = []
            continue
        if cur:
            cur[-1] = cur[-1] + _glue(cur[-1], line) + line
        else:
            cur.append(line)
    if cur:
        paragraphs.append(cur)
    return "\n\n".join(" ".join(p) for p in paragraphs)


def _drop_token_echo(paragraph):
    """Buang salinan PERTAMA yang mengulang salinan berikutnya (gema KaTeX).

    Pola gema: versi kacau lebih dulu ('det=a d −bc', '(3) (−2) − (7) ...'),
    lalu versi bersih ('det=ad−bc', '(3)(−2)−(7)(−2)=−6+14=8'). Yang dipertahankan
    adalah salinan terakhir (bersih); tanda baca diabaikan saat membandingkan.

    Normalisasi token dihitung sekali (memoisasi) dan jendela pencocokan
    dibatasi 12 token agar tetap O(n) — bukan O(n^3) — pada paragraf panjang.
    """
    tokens = paragraph.split(" ")
    n = len(tokens)
    if n < 4:
        return paragraph

    def _tok_norm(t):
        x = re.sub(r"[\s.,;:!?\$\(\)\[\]]", "", t)
        for pat, rep in _WORD_SYMBOLS:
            x = pat.sub(rep, x)
        return x

    norms = [_tok_norm(t) for t in tokens]

    MAX_WINDOW = 12
    best = None  # (panjang_norm, i, j) — window PERTAMA [i:j) yang dihapus
    for i in range(n):
        head_len = 0
        for j in range(i + 1, min(n, i + MAX_WINDOW) + 1):
            head_len = sum(len(x) for x in norms[i:j])
            if head_len < 8:
                continue
            head = "".join(norms[i:j])
            for k in range(j + 1, min(n, j + MAX_WINDOW) + 1):
                if head_len != sum(len(x) for x in norms[j:k]):
                    continue
                if "".join(norms[j:k]) == head:
                    if best is None or (j - i) > (best[2] - best[1]):
                        best = (head_len, i, j)
                    break
    if best:
        _, i, j = best
        tokens = tokens[:i] + tokens[j:]
    return " ".join(tokens)


def tidy_spaces(text):
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" +([.,;:!?])", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def repair_math_text(text):
    """Pipeline lengkap perbaikan teks rusak hasil ekstraksi DOM/LLM. Idempoten."""
    if not text or not isinstance(text, str):
        return text
    text = map_math_unicode(text)
    lines = merge_fragmented_lines(text)
    lines = [fix_word_symbols(l) for l in lines]
    lines = dedupe_echo(lines)
    text = rebuild_sentences(lines)
    paragraphs = [_drop_token_echo(p) for p in text.split("\n\n")]
    text = "\n\n".join(paragraphs)
    text = fix_word_symbols(text)
    # Derajat yang terpecah: "30 O)" / "30 O )" / "30O)" -> "30°)"
    text = re.sub(r"(?<=\d) ?([Oo]) ?(?=[\)\s])", "°", text)
    return tidy_spaces(text)
