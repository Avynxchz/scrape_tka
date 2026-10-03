# -*- coding: utf-8 -*-
"""Patch server.py: refactor halaman /audit menjadi _audit_collect + renderer HTML/TXT."""
import io
import re

PATH = 'server.py'
src = io.open(PATH, encoding='utf-8').read()

pattern = re.compile(r'def render_audit_page\(.*?\n\ndef _audit_join_list\(items\):', re.S)
m = pattern.search(src)
assert m, "region render_audit_page tidak ditemukan"

new_block = '''def _audit_collect(subject, paket, dari, sampai):
    """Kumpulkan soal+pembahasan sebagai data teks polos utk renderer HTML/TXT."""
    items = []
    for nomor in range(dari, sampai + 1):
        lrn_q = learning_for(subject, paket, nomor)
        canon = canonical_for(subject, paket, nomor)
        if not lrn_q and not canon:
            items.append({"nomor": nomor, "missing": True})
            continue

        tipe = (lrn_q or {}).get('tipe_soal') or (canon or {}).get('type') or 'Pilihan Ganda'
        topik = (lrn_q or {}).get('topik') or ''
        stim = ((lrn_q or {}).get('stimulus') or {}).get('text') or (canon or {}).get('stimulus') or ''
        tanya = ((lrn_q or {}).get('pertanyaan') or {}).get('text') or (canon or {}).get('question') or ''
        pilihan = (lrn_q or {}).get('pilihan_jawaban') or (canon or {}).get('options') or []
        kunci = (lrn_q or {}).get('kunci_jawaban') or (canon or {}).get('official_answer')
        pernyataan = (lrn_q or {}).get('pernyataan') or []

        pembahasan = None
        answer_display = None
        review = {}
        try:
            sol = build_solution_payload(canon, lrn_q, subject, paket)
            pembahasan = sol.get('pembahasan') or {}
            answer_display = sol.get('answer_display')
            review = sol.get('review') or {}
        except Exception:
            pembahasan = None

        if isinstance(kunci, dict):
            kunci_txt = '; '.join(f"{k}: {v}" for k, v in kunci.items())
        elif isinstance(kunci, list):
            kunci_txt = ', '.join(str(k) for k in kunci)
        else:
            kunci_txt = str(kunci or '-')
        if answer_display:
            kunci_txt += f" (answer_display: {answer_display})"

        blk = []
        if pembahasan:
            if pembahasan.get('diketahui'):
                blk.append(('Diketahui', _audit_text(pembahasan['diketahui'])))
            if pembahasan.get('ditanyakan'):
                blk.append(('Ditanyakan', _audit_text(pembahasan['ditanyakan'])))
            if pembahasan.get('konsep_kunci'):
                blk.append(('Konsep kunci', _audit_join_list(pembahasan['konsep_kunci'])))
            if pembahasan.get('mengapa_begini'):
                blk.append(('Mengapa rumus ini dipakai', _audit_text(pembahasan['mengapa_begini'])))
            langkah = pembahasan.get('langkah_penyelesaian') or []
            if langkah:
                step_txt = '\\n\\n'.join(
                    f"Langkah {i}: {_audit_text(str(s))}" for i, s in enumerate(langkah, 1))
                blk.append(('Langkah penyelesaian', step_txt))
            if pembahasan.get('glosarium_simbol'):
                glos = '\\n'.join(f"{g.get('simbol', '')} = {g.get('arti', '')}"
                                 for g in pembahasan['glosarium_simbol'])
                blk.append(('Glosarium simbol', glos))
            if pembahasan.get('tips_list'):
                blk.append(('Tips', _audit_join_list(pembahasan['tips_list'])))
            if pembahasan.get('mistakes_list'):
                blk.append(('Jebakan umum', _audit_join_list(pembahasan['mistakes_list'])))
        warn = None
        if review.get('needs_manual_review'):
            warn = str(review.get('review_reason', ''))

        items.append({
            "nomor": nomor, "missing": False, "tipe": str(tipe), "topik": str(topik),
            "stimulus": _audit_text(stim), "pertanyaan": _audit_text(tanya),
            "pernyataan": [f"{st.get('key', '')}) {_audit_text(st.get('text', ''))}"
                           for st in pernyataan],
            "opsi": [f"{(o.get('key', '?') if isinstance(o, dict) else '?')}) {_audit_option_text(o)}"
                     for o in pilihan],
            "kunci": kunci_txt, "pembahasan": blk, "warn": warn,
        })
    return items


def render_audit_text(subject, paket, dari, sampai):
    items = _audit_collect(subject, paket, dari, sampai)
    out = [
        f"AUDIT KONTEN — {subject} Paket {paket} — Nomor {dari}-{sampai}",
        "Teks di dalam $...$ adalah LaTeX matematika. [GAMBAR] = gambar soal/opsi asli",
        "yang hanya terlihat di aplikasi interaktif.",
        "=" * 60,
    ]
    for it in items:
        out.append("")
        out.append("=" * 60)
        if it.get("missing"):
            out.append(f"SOAL {it['nomor']} — (tidak ditemukan di data)")
            continue
        out.append(f"SOAL {it['nomor']} — {it['tipe']}")
        if it["topik"]:
            out.append(f"Topik: {it['topik']}")
        if it["stimulus"]:
            out.append("")
            out.append("STIMULUS:")
            out.append(it["stimulus"])
        if it["pertanyaan"]:
            out.append("")
            out.append("PERTANYAAN:")
            out.append(it["pertanyaan"])
        if it["pernyataan"]:
            out.append("")
            out.append("PERNYATAAN:")
            out.extend(it["pernyataan"])
        if it["opsi"]:
            out.append("")
            out.append("OPSI JAWABAN:")
            out.extend(it["opsi"])
        out.append("")
        out.append(f"KUNCI RESMI: {it['kunci']}")
        if it["pembahasan"]:
            out.append("")
            out.append("PEMBAHASAN (Layer 3):")
            for label, txt in it["pembahasan"]:
                out.append(f"--- {label} ---")
                out.append(txt)
        else:
            out.append("PEMBAHASAN: belum tersedia untuk soal ini.")
        if it["warn"]:
            out.append(f"PERLU VERIFIKASI MANUAL: {it['warn']}")
    return "\\n".join(out)


def render_audit_page(subject, paket, dari, sampai):
    esc = html_lib.escape
    items = _audit_collect(subject, paket, dari, sampai)
    sections = []
    for it in items:
        rows = [f"<h2 id=\\"soal-{it['nomor']}\\">SOAL {it['nomor']} — {esc(it['tipe'])}</h2>"]
        if it.get("missing"):
            sections.append(f"<section>{''.join(rows)}<p>(tidak ditemukan di data)</p></section>")
            continue
        if it["topik"]:
            rows.append(f"<p class=\\"meta\\">Topik: {esc(it['topik'])}</p>")
        if it["stimulus"]:
            rows.append(_audit_block('STIMULUS', esc(it["stimulus"])))
        if it["pertanyaan"]:
            rows.append(_audit_block('PERTANYAAN', esc(it["pertanyaan"])))
        if it["pernyataan"]:
            rows.append(_audit_block('PERNYATAAN', '<br>'.join(esc(p) for p in it["pernyataan"])))
        if it["opsi"]:
            rows.append(_audit_block('OPSI JAWABAN', '<br>'.join(esc(o) for o in it["opsi"])))
        rows.append(f"<p><strong>KUNCI RESMI:</strong> {esc(it['kunci'])}</p>")
        if it["pembahasan"]:
            rows.append("<h3>PEMBAHASAN (Layer 3)</h3>")
            for label, txt in it["pembahasan"]:
                rows.append(_audit_block(label, esc(txt)))
            if it["warn"]:
                rows.append(f"<p class=\\"warn\\">⚠ PERLU VERIFIKASI MANUAL: {esc(it['warn'])}</p>")
        else:
            rows.append("<p class=\\"warn\\">PEMBAHASAN: belum tersedia untuk soal ini.</p>")
        sections.append(f"<section>{''.join(rows)}</section>")

    title = f"Audit Konten — {esc(subject)} Paket {paket} (Nomor {dari}–{sampai})"
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="style.css?v=46">
<style>
  .audit-wrap {{ max-width: 860px; margin: 0 auto; padding: 32px 20px 72px; }}
  .audit-wrap h1 {{ font-size: 22px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }}
  .audit-note {{ font-size: 13px; color: var(--text-2); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 14px; background: var(--surface); margin: 16px 0 24px; }}
  .audit-wrap section {{ border: 1px solid var(--border); border-radius: 8px;
    padding: 18px 20px; margin-bottom: 22px; background: var(--bg-card); }}
  .audit-wrap h2 {{ font-size: 16px; font-weight: 600; color: var(--text); margin: 0 0 10px; }}
  .audit-wrap h3 {{ font-size: 13px; font-weight: 600; color: var(--text-3);
    text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 6px; }}
  .audit-wrap p, .audit-wrap .blk {{ font-size: 14.5px; line-height: 1.7; color: var(--text); }}
  .audit-wrap .blk {{ white-space: pre-wrap; }}
  .audit-wrap .meta {{ font-size: 12.5px; color: var(--text-3); }}
  .audit-wrap .warn {{ color: var(--warn); font-weight: 500; }}
</style>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script defer>
window.addEventListener('DOMContentLoaded', function () {{
  if (window.renderMathInElement) renderMathInElement(document.body, {{
    delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}],
    throwOnError: false
  }});
}});
</script>
</head>
<body>
<div class="audit-wrap">
<h1>{title}</h1>
<div class="audit-note">Halaman statis untuk reviewer otomatis — konten apa adanya dari data.
Teks di dalam <code>$...$</code> adalah LaTeX matematika. [GAMBAR] = gambar soal/opsi asli
yang hanya terlihat di aplikasi. Halaman interaktif: <code>/app</code>.</div>
{''.join(sections)}
</div>
</body>
</html>"""


def _audit_join_list(items):'''

src = pattern.sub(lambda _: new_block, src)
io.open(PATH, 'w', encoding='utf-8', newline='\n').write(src)
print("refactor OK")
