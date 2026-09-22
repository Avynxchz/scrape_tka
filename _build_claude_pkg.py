# -*- coding: utf-8 -*-
"""_build_claude_pkg.py — Build the Claude Web input package for Matematika Paket 2.

Outputs (claude_input/):
  MTK_PAKET_2_CLAUDE_CONTEXT.json  — structured, lossless question data + official keys
  MTK_PAKET_2_CLAUDE_VISUAL.pdf    — visual rendering of the same 25 questions (all images)

Sources (read-only):
  data/paket_2/matematika_paket_2.json          (raw scraped questions)
  data/matematika_paket_2_learning.json         (repaired authoritative representation)
  data/kunci/matematika_paket_2_kunci.json      (official answer-key evidence)

This script NEVER writes to the authoritative datasets.
"""
import json, os, re, sys, hashlib
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Image, Table, TableStyle, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

BASE = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE, 'data', 'paket_2', 'matematika_paket_2.json')
LRN_PATH = os.path.join(BASE, 'data', 'matematika_paket_2_learning.json')
KUNCI_PATH = os.path.join(BASE, 'data', 'kunci', 'matematika_paket_2_kunci.json')
IMG_ROOT = os.path.join(BASE, 'data', 'paket_2')
OUT_DIR = os.path.join(BASE, 'claude_input')
JSON_OUT = os.path.join(OUT_DIR, 'MTK_PAKET_2_CLAUDE_CONTEXT.json')
PDF_OUT = os.path.join(OUT_DIR, 'MTK_PAKET_2_CLAUDE_VISUAL.pdf')

# ---------------------------------------------------------------- load sources
raw = json.load(open(RAW_PATH, encoding='utf-8'))
lrn = json.load(open(LRN_PATH, encoding='utf-8'))
kun = json.load(open(KUNCI_PATH, encoding='utf-8'))
raw_soal = raw['soal']
lrn_soal = lrn['soal'] if isinstance(lrn, dict) and 'soal' in lrn else lrn
lrn_by_no = {q['nomor']: q for q in lrn_soal}
assert len(raw_soal) == 25, f'raw count {len(raw_soal)}'

STMT_NOS = sorted(int(n) for n in kun.get('kunci_bs', {}))

def parse_letters(kunci_str):
    return re.findall(r'\(([A-E])\)', kunci_str)

def official_answer(n):
    """Return (format, answer) derived ONLY from official evidence."""
    if str(n) in kun.get('kunci_bs', {}):
        return 'per_statement_benar_salah', dict(kun['kunci_bs'][str(n)])
    letters = parse_letters(kun['raw_rows'][str(n)]['kunci'])
    return 'single_choice' if len(letters) == 1 else 'multiple_correct', letters

# ------------------------------------------------- build question records (JSON)
def img_ref(im):
    if not im:
        return None
    return {'filename': im.get('filename'),
            'rel_path': 'data/paket_2/' + im['rel_path'],
            'remote_url': im.get('remote_url')}

questions, inventory, problems = [], [], []
seen_files = {}

def add_img(im, where, n):
    if not im:
        return
    r = img_ref(im)
    full = os.path.join(BASE, r['rel_path'])
    ok = os.path.exists(full)
    status = 'ok'
    if not ok:
        status = 'MISSING'
        problems.append(f'soal {n}: missing image {r["rel_path"]}')
    else:
        try:
            with PILImage.open(full) as p:
                p.verify()
        except Exception as e:
            status = 'UNREADABLE'
            problems.append(f'soal {n}: unreadable image {r["rel_path"]}: {e}')
    key = r['rel_path']
    if key in seen_files and seen_files[key] != f'soal-{n}':
        pass  # same asset reused by another question is fine; recorded once in inventory
    seen_files.setdefault(key, f'soal-{n}')
    entry = dict(r); entry['used_by'] = f'soal {n} ({where})'; entry['status'] = status
    inventory.append(entry)
    return r

for q in raw_soal:
    n = q['nomor']
    lq = lrn_by_no[n]
    fmt, ans = official_answer(n)
    rec = {
        'number': n,
        'id': q['id'],
        'type': q['tipe_soal'],
        'stimulus': {
            'text': q['stimulus'].get('text') or '',
            'images': [img_ref(im) for im in (q['stimulus'].get('images') or [])],
        },
        'question': {
            'text': q['pertanyaan'].get('text') or '',
            'images': [img_ref(im) for im in (q['pertanyaan'].get('images') or [])],
        },
        'official_answer': ans,
        'official_answer_format': fmt,
        'official_review_kunci_raw': kun['raw_rows'][str(n)]['kunci'],
    }
    for im in q['stimulus'].get('images') or []:
        add_img(im, 'stimulus', n)
    for im in q['pertanyaan'].get('images') or []:
        add_img(im, 'question', n)

    if n in STMT_NOS:
        # statement-table question: repaired pernyataan (A/B/C aligned with official key)
        stmts = []
        for s in lq['pernyataan']:
            stmts.append({'key': s['key'], 'text': s.get('text') or '',
                          'latex': s.get('latex'), 'image': img_ref(s.get('image'))})
            if s.get('image'):
                add_img(s['image'], 'statement', n)
        rec['statements'] = stmts
        rec['answer_instruction'] = ('Tandai Benar atau Salah pada setiap pernyataan. '
                                     'Kunci resmi dinilai per pernyataan.')
        # lossless raw table (option A is the scrape's 'Pernyataan' column header)
        rec['source_table_options'] = [
            {'key': o['key'], 'text': o.get('text') or '', 'latex': o.get('latex'),
             'image': img_ref(o.get('image'))}
            for o in q['pilihan_jawaban']]
        for o in q['pilihan_jawaban']:
            if o.get('image'):
                add_img(o['image'], 'statement(raw-table)', n)
    else:
        opts = []
        for o in q['pilihan_jawaban']:
            opts.append({'key': o['key'], 'text': o.get('text') or '',
                         'latex': o.get('latex'), 'image': img_ref(o.get('image'))})
            if o.get('image'):
                add_img(o['image'], 'option', n)
        rec['options'] = opts
    # cross-check official key vs repaired learning representation
    if n in STMT_NOS:
        lrn_ans = {kv.split(':', 1)[0]: kv.split(':', 1)[1] for kv in lq['kunci_jawaban']}
        if lrn_ans != ans:
            problems.append(f'soal {n}: kunci mismatch evidence={ans} learning={lrn_ans}')
    else:
        if sorted(lq['kunci_jawaban']) != sorted(ans):
            problems.append(f'soal {n}: kunci mismatch evidence={ans} learning={lq["kunci_jawaban"]}')
    questions.append(rec)

questions.sort(key=lambda r: r['number'])
nums = [r['number'] for r in questions]
assert nums == list(range(1, 26)), f'numbering problem: {nums}'

# PGK expected multi-letter consistency
for r in questions:
    if r['official_answer_format'] == 'multiple_correct' and len(r['official_answer']) < 2:
        problems.append(f"soal {r['number']}: PGK with <2 letters")
    if r['official_answer_format'] == 'single_choice' and r['type'] == 'Pilihan Ganda Kompleks':
        problems.append(f"soal {r['number']}: typed PGK but single-letter key")

# ------------------------------------------------------------------ context JSON
kunci_meta = {
    'source_file': 'data/kunci/matematika_paket_2_kunci.json',
    'origin': 'Official TKA simulation review table (KUNCI JAWABAN column), '
              'https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/',
    'scraped_at': kun.get('scraped_at'),
}
context = {
    'meta': {
        'subject': 'Matematika',
        'package': 2,
        'package_name': raw.get('paket'),
        'total_questions': len(questions),
        'source_file': 'data/paket_2/matematika_paket_2.json',
        'origin': 'https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/',
        'note': ('Question text and images are preserved verbatim from the official TKA '
                 'simulation scrape. Inline mathematical expressions that appear as '
                 'images in the original CBT are carried by the referenced PNG files; '
                 'option/statement "latex" fields hold the source LaTeX when available. '
                 'No AI-generated educational content (pembahasan etc.) is included.'),
        'question_type_counts': {},
        'official_answer_key': kunci_meta,
        'visual_pdf': 'MTK_PAKET_2_CLAUDE_VISUAL.pdf',
    },
    'image_inventory': {
        'count': len({e['rel_path'] for e in inventory}),
        'all_exist': all(e['status'] == 'ok' for e in inventory),
        'images': sorted({e['rel_path']: e for e in inventory}.values(),
                         key=lambda e: e['rel_path']),
    },
    'questions': questions,
}
tc = {}
for r in questions:
    tc[r['type']] = tc.get(r['type'], 0) + 1
context['meta']['question_type_counts'] = tc

os.makedirs(OUT_DIR, exist_ok=True)
json.dump(context, open(JSON_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# ---------------------------------------------------------------------- PDF build
pdfmetrics.registerFont(TTFont('Segoe', 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('Segoe-B', 'C:/Windows/Fonts/segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('SegoeSym', 'C:/Windows/Fonts/seguisym.ttf'))

def xml(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('\xa0', ' '))

def rich(t):
    """escape + angle-symbol font fallback"""
    return xml(t).replace('∠', '<font name="SegoeSym">∠</font>')

S_TITLE = ParagraphStyle('t', fontName='Segoe-B', fontSize=15, leading=20, spaceAfter=4)
S_META = ParagraphStyle('m', fontName='Segoe', fontSize=8.5, leading=12,
                        textColor=colors.HexColor('#444444'))
S_SOAL = ParagraphStyle('s', fontName='Segoe-B', fontSize=13, leading=16,
                        textColor=colors.HexColor('#0b3d91'))
S_LABEL = ParagraphStyle('l', fontName='Segoe-B', fontSize=9, leading=12,
                         textColor=colors.HexColor('#555555'), spaceBefore=4)
S_TEXT = ParagraphStyle('p', fontName='Segoe', fontSize=10.5, leading=15)
S_OPT = ParagraphStyle('o', fontName='Segoe', fontSize=10.5, leading=14)
S_OPTKEY = ParagraphStyle('ok', fontName='Segoe-B', fontSize=10.5, leading=14,
                          textColor=colors.HexColor('#0b3d91'))

PAGE_W, PAGE_H = A4
MARG = 1.7 * cm
AVAIL_W = PAGE_W - 2 * MARG
MAX_IMG_W = AVAIL_W
MAX_IMG_H = 19 * cm

def scaled_image(rel_path):
    full = os.path.join(BASE, rel_path)
    with PILImage.open(full) as p:
        pw, ph = p.size
    w = pw * 72.0 / 96.0 * 0.62      # CBT screenshots are 2x; 0.62 keeps glyphs crisp & readable
    h = ph * 72.0 / 96.0 * 0.62
    scale = min(1.0, MAX_IMG_W / w, MAX_IMG_H / h)
    return Image(full, width=w * scale, height=h * scale)

def img_par_block(refs, texts=None):
    """flowables for a list of image refs"""
    out = []
    for im in refs:
        if im:
            out.append(scaled_image(im['rel_path']))
            out.append(Spacer(1, 4))
    return out

def flow_text(t, style=S_TEXT):
    t = (t or '').replace('\xa0', ' ').strip()
    return Paragraph(rich(t), style) if t else None

story = []
story.append(Paragraph('MATEMATIKA PAKET 2', S_TITLE))
story.append(Paragraph(
    'TKA Simulasi — Pusmendik Kemendikdasmen (https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/)'
    ' &nbsp;|&nbsp; 25 soal &nbsp;|&nbsp; Sumber data: data/paket_2/matematika_paket_2.json'
    ' &nbsp;|&nbsp; Kunci resmi: data/kunci/matematika_paket_2_kunci.json (tabel review simulasi resmi)'
    ' &nbsp;|&nbsp; Ekspresi matematika pada soal asli tersaji sebagai gambar — gambar tersebut '
    'menyandikan informasi matematis dan tidak boleh diabaikan.', S_META))
story.append(Spacer(1, 8))

def add_if_space(flowables, needed=5 * cm):
    """start new page when the block would not fit comfortably"""
    global _frame_h
    if _frame_h < needed:
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
    story.extend(flowables)

_frame_h = PAGE_H - 2 * MARG

for rec in questions:
    n = rec['number']
    head = [Paragraph(f"SOAL {n}", S_SOAL),
            Paragraph(f"Tipe: {rec['type']}", S_META), Spacer(1, 3)]
    story.extend(head)
    _frame_h -= 46

    stim_txt = flow_text(rec['stimulus']['text'])
    if stim_txt or rec['stimulus']['images']:
        story.append(Paragraph('STIMULUS', S_LABEL))
        if stim_txt:
            story.append(stim_txt)
        story.extend(img_par_block(rec['stimulus']['images']))

    q_txt = flow_text(rec['question']['text'])
    if q_txt or rec['question']['images']:
        story.append(Paragraph('PERTANYAAN', S_LABEL))
        if q_txt:
            story.append(q_txt)
        story.extend(img_par_block(rec['question']['images']))

    if 'statements' in rec:
        story.append(Paragraph('PERNYATAAN — tandai Benar / Salah untuk setiap pernyataan', S_LABEL))
        rows = [[Paragraph('Pernyataan', S_OPT), Paragraph('Benar', S_OPT), Paragraph('Salah', S_OPT)]]
        for s in rec['statements']:
            cell = []
            if s['image']:
                cell.append(scaled_image(s['image']['rel_path']))
            if s['text']:
                cell.append(Paragraph(rich(s['text']), S_OPT))
            if s['latex'] and not s['image']:
                cell.append(Paragraph(xml(str(s['latex'])), S_OPT))
            rows.append([cell, '', ''])
        t = Table(rows, colWidths=[AVAIL_W - 4.4 * cm, 2.2 * cm, 2.2 * cm])
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.6, colors.HexColor('#999999')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef7')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.extend(img_par_block([o.get('image') for o in rec.get('source_table_options', [])
                                    if o.get('image') and not any(
                                        s['image'] and s['image']['filename'] == o['image']['filename']
                                        for s in rec['statements'])]))
    else:
        story.append(Paragraph('PILIHAN JAWABAN', S_LABEL))
        opt_rows = []
        for o in rec['options']:
            cell = []
            if o['image']:
                cell.append(scaled_image(o['image']['rel_path']))
            if o['text']:
                cell.append(Paragraph(rich(o['text']), S_OPT))
            if o['latex'] and not o['image'] and not o['text']:
                cell.append(Paragraph(xml(str(o['latex'])), S_OPT))
            opt_rows.append([Paragraph(o['key'], S_OPTKEY), cell])
        t = Table(opt_rows, colWidths=[1.1 * cm, AVAIL_W - 1.1 * cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#dddddd')),
        ]))
        story.append(t)

    story.append(Paragraph(
        f"KUNCI RESMI: {json.dumps(rec['official_answer'], ensure_ascii=False)}"
        f" &nbsp;({rec['official_answer_format']})", S_LABEL))
    _frame_h = PAGE_H - 2 * MARG  # each question starts a fresh page for clean boundaries
    from reportlab.platypus import PageBreak
    story.append(PageBreak())
    if story[-1] is story[-1]:
        pass

# drop trailing page break
if isinstance(story[-1], PageBreak):
    story.pop()

doc = BaseDocTemplate(PDF_OUT, pagesize=A4,
                      leftMargin=MARG, rightMargin=MARG, topMargin=MARG, bottomMargin=MARG)
frame = Frame(MARG, MARG, AVAIL_W, PAGE_H - 2 * MARG, id='f')

def footer(canv, _doc):
    canv.saveState()
    canv.setFont('Segoe', 8)
    canv.setFillColor(colors.HexColor('#777777'))
    canv.drawString(MARG, 0.9 * cm, 'MTK_PAKET_2_CLAUDE_VISUAL — Matematika Paket 2 (TKA Simulasi, Pusmendik)')
    canv.drawRightString(PAGE_W - MARG, 0.9 * cm, f'Hal. {canv.getPageNumber()}')
    canv.restoreState()

doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=footer)])
doc.build(story)

print('JSON written:', JSON_OUT)
print('PDF written :', PDF_OUT)
print('inventory images:', context['image_inventory']['count'],
      'all_exist:', context['image_inventory']['all_exist'])
print('PROBLEMS:' if problems else 'no problems')
for p in problems:
    print(' -', p)
