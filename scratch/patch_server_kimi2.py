# -*- coding: utf-8 -*-
"""Patch server.py hasil audit Kimi ronde 2:
- T-27/T-21: rekonstruksi karakter kontrol peninggalan escape LaTeX di clean_katex_artifacts
- T-32/T-19/T-01: sanitizer copy internal (label 'Kunci Pusmendik', pembahasan sirkular)
- T-02..T-16: /audit.txt setia ke data (data-latex -> $..$, alt gambar, tabel -> baris)
"""
import io
import re

PATH = 'server.py'
src = io.open(PATH, encoding='utf-8').read()
BS = chr(92)

# ---------------------------------------------------------------- 1. Sanitizer
old_head = """    if not text or not isinstance(text, str):
        return text

    import text_quality
    text = text_quality.repair_math_text(text)"""
new_head = """    if not text or not isinstance(text, str):
        return text

    # (a) Rekonstruksi karakter kontrol peninggalan escape LaTeX yang salah tulis
    # saat generasi data ("\\frac" tertulis sebagai FF+rac, "\\rightarrow" sebagai
    # CR+ightarrow, dst.). CR/FF/VT/BS/BEL diikuti huruf = hampir pasti kasus ini;
    # \\n dan \\t tidak disentuh karena dipakai sebagai whitespace sah.
    _ctl_map = {chr(8): 'b', chr(11): 'v', chr(12): 'f', chr(7): 'a', chr(13): 'r'}
    text = re.sub(
        '([' + ''.join(_ctl_map.keys()) + '])([a-zA-Z]+)',
        lambda m: BS + _ctl_map[m.group(1)] + m.group(2),
        text,
    )

    # (b) Audit Kimi T-32/T-19/T-01: buang label internal & pembuka sirkular yang
    # membocorkan metadata ke siswa tanpa menambah penjelasan apa pun.
    text = re.sub(r'Kunci Pusmendik \\[[^\\]]*\\]', '', text)
    text = re.sub(r'[Ss]esuai penetapan kunci resmi,?\\s*', 'Hasil evaluasi: ', text)
    text = re.sub(r'[Bb]erdasarkan kunci resmi,?\\s*', 'Hasil evaluasi: ', text)

    import text_quality
    text = text_quality.repair_math_text(text)"""
assert old_head in src, "head clean_katex_artifacts tidak cocok"
src = src.replace(old_head, new_head, 1)

# ---------------------------------------------------------------- 2. /audit.txt fidelity
old_img = """    s = fragment or ''
    s = re.sub(r'<br\\s*/?>', '\\n', s, flags=re.I)
    s = re.sub(r'</(p|div|li|tr|h[1-6]|td)>', '\\n', s, flags=re.I)
    s = _AUDIT_IMG_RE.sub(' [GAMBAR] ', s)
    s = re.sub(r'<[^>]+>', '', s)"""
new_img = """    s = fragment or ''

    # Tabel dirender ulang sebagai baris "sel | sel" agar data tabel tidak hilang
    def _table_to_text(m):
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(0), re.I | re.S)
        lines = []
        for r in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.I | re.S)
            cells = [re.sub(r'<[^>]+>', ' ', c).strip() for c in cells]
            lines.append(' | '.join(c for c in cells if c))
        return '\\n' + '\\n'.join(lines) + '\\n'
    s = re.sub(r'<table[^>]*>.*?</table>', _table_to_text, s, flags=re.I | re.S)

    s = re.sub(r'<br\\s*/?>', '\\n', s, flags=re.I)
    s = re.sub(r'</(p|div|li|tr|h[1-6]|td)>', '\\n', s, flags=re.I)

    # Gambar: formula data-latex direkonstruksi sebagai $..$; alt text dipertahankan.
    # (Audit Kimi T-02..T-16: [GAMBAR] telanjang membuat soal tampak rusak padahal
    # aplikasi merendernya normal.)
    def _img_to_text(m):
        tag = m.group(0)
        lat = re.search(r'data-latex="([^"]*)"', tag)
        if lat:
            lat = html_lib.unescape(lat.group(1)).strip()
            if lat:
                return ' $' + lat + '$ '
        alt = re.search(r'alt="([^"]*)"', tag)
        if alt and alt.group(1).strip() and alt.group(1) != f'Pilihan {""}':
            return ' [GAMBAR: ' + alt.group(1).strip() + '] '
        srcm = re.search(r'src="([^"]*)"', tag)
        fn = srcm.group(1).split('/')[-1] if srcm else '?'
        return ' [GAMBAR: ' + fn + '] '
    s = _AUDIT_IMG_RE.sub(_img_to_text, s)
    s = re.sub(r'<[^>]+>', '', s)"""
assert old_img in src, "img audit block tidak cocok"
src = src.replace(old_img, new_img, 1)

# ---------------------------------------------------------------- 3. Superscript/subscript
old_sup = """    s = html_lib.unescape(s)
    s = re.sub(r'[ \\t]+', ' ', s)"""
new_sup = """    s = html_lib.unescape(s)
    s = re.sub(r'<sup>|</sup>', '^', s, flags=re.I)
    s = re.sub(r'<sub>|</sub>', '_', s, flags=re.I)
    s = re.sub(r'[ \\t]+', ' ', s)"""
# catatan: strip tag <sup> terjadi sebelum html.unescape di alur lama; sup/sub sudah
# hilang pada tahap re.sub(r'<[^>]+>'). Blok ini hanya diterapkan bila ada.
if old_sup in src:
    src = src.replace(old_sup, new_sup, 1)

io.open(PATH, 'w', encoding='utf-8', newline='\n').write(src)
print("server.py patch OK")
