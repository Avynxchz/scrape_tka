# -*- coding: utf-8 -*-
"""_build_nokey_pkg.py — Build + validate the NO_KEY derivative package.

Purpose: independent-solving phase. Claude Web must solve the 25 questions
WITHOUT seeing the official answer key. This tool:

  1. Derives MTK_PAKET_2_CLAUDE_CONTEXT_NO_KEY.json from the validated
     MTK_PAKET_2_CLAUDE_CONTEXT.json by stripping ALL answer-key fields.
  2. Rebuilds MTK_PAKET_2_CLAUDE_VISUAL_NO_KEY.pdf from that stripped JSON
     with identical rendering (images, order, layout) minus every
     "KUNCI RESMI" section.
  3. Validates: 25/25 questions, numbering, no key fields/strings remain,
     image placement + pixel identity vs source PNGs, JSON<->PDF ordering
     identical to the authoritative package, originals untouched.

NEVER modifies the authoritative datasets or the WITH-KEY package files.
"""
import json, os, re, sys, hashlib, copy
from collections import Counter
from PIL import Image as PILImage

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'claude_input')
WITH_JSON = os.path.join(OUT, 'MTK_PAKET_2_CLAUDE_CONTEXT.json')
WITH_PDF = os.path.join(OUT, 'MTK_PAKET_2_CLAUDE_VISUAL.pdf')
NO_JSON = os.path.join(OUT, 'MTK_PAKET_2_CLAUDE_CONTEXT_NO_KEY.json')
NO_PDF = os.path.join(OUT, 'MTK_PAKET_2_CLAUDE_VISUAL_NO_KEY.pdf')

KEY_FIELDS = ('official_answer', 'official_answer_format', 'official_review_kunci_raw')
# field names that must NOT exist anywhere in the NO_KEY JSON (case-insensitive)
FORBIDDEN_NAMES = {'official_answer', 'official_answer_format', 'official_review_kunci_raw',
                   'official_answer_key', 'kunci_jawaban', 'kunci', 'kunci_resmi', 'kunci_bs'}
WHITELISTED = {'answer_instruction'}  # instruction text only; contains no answer data

# snapshot the authoritative (with-key) files BEFORE anything else; compared at the end
WITH_KEY_SHA0 = {os.path.basename(p): hashlib.sha256(open(p, 'rb').read()).hexdigest()
                 for p in (WITH_JSON, WITH_PDF)}

fails, notes = [], []
def check(name, ok, detail=''):
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f' — {detail}' if detail else ''))
    if not ok:
        fails.append(name)

# ---------------------------------------------------------------- 1. derive JSON
withkey = json.load(open(WITH_JSON, encoding='utf-8'))
nokey = copy.deepcopy(withkey)
nokey['meta'].pop('official_answer_key', None)
nokey['meta']['visual_pdf'] = 'MTK_PAKET_2_CLAUDE_VISUAL_NO_KEY.pdf'
nokey['meta']['purpose'] = ('NO_KEY variant for the independent-solving phase: all official '
                            'answer-key fields removed. Content is otherwise identical to '
                            'MTK_PAKET_2_CLAUDE_CONTEXT.json.')
for q in nokey['questions']:
    for f in KEY_FIELDS:
        q.pop(f, None)
json.dump(nokey, open(NO_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('JSON written:', NO_JSON)

# deep-equality proof: stripping the with-key copy must reproduce the no-key file exactly
stripped = copy.deepcopy(withkey)
stripped['meta'].pop('official_answer_key', None)
stripped['meta']['visual_pdf'] = 'MTK_PAKET_2_CLAUDE_VISUAL_NO_KEY.pdf'
stripped['meta']['purpose'] = nokey['meta']['purpose']
for q in stripped['questions']:
    for f in KEY_FIELDS:
        q.pop(f, None)
check('NO_KEY JSON == with-key JSON minus key fields (deep-equal)', stripped == nokey)

# ---------------------------------------------------------------- 2. build PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Image, Table, TableStyle, PageBreak)
from reportlab.lib.styles import ParagraphStyle

pdfmetrics.registerFont(TTFont('Segoe', 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('Segoe-B', 'C:/Windows/Fonts/segoeuib.ttf'))
pdfmetrics.registerFont(TTFont('SegoeSym', 'C:/Windows/Fonts/seguisym.ttf'))

def xml(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('\xa0', ' '))

def rich(t):
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
    w = pw * 72.0 / 96.0 * 0.62
    h = ph * 72.0 / 96.0 * 0.62
    scale = min(1.0, MAX_IMG_W / w, MAX_IMG_H / h)
    return Image(full, width=w * scale, height=h * scale)

def img_par_block(refs):
    out = []
    for im in refs:
        if im:
            out.append(scaled_image(im['rel_path']))
            out.append(Spacer(1, 4))
    return out

def flow_text(t, style=S_TEXT):
    t = (t or '').replace('\xa0', ' ').strip()
    return Paragraph(rich(t), style) if t else None

qs = nokey['questions']
story = []
story.append(Paragraph('MATEMATIKA PAKET 2', S_TITLE))
story.append(Paragraph(
    'TKA Simulasi — Pusmendik Kemendikdasmen (https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/) '
    '&nbsp;|&nbsp; 25 soal &nbsp;|&nbsp; Sumber data: data/paket_2/matematika_paket_2.json '
    '&nbsp;|&nbsp; Ekspresi matematika pada soal asli tersaji sebagai gambar — gambar tersebut '
    'menyandikan informasi matematis dan tidak boleh diabaikan.', S_META))
story.append(Spacer(1, 8))

for rec in qs:
    n = rec['number']
    story.extend([Paragraph(f"SOAL {n}", S_SOAL),
                  Paragraph(f"Tipe: {rec['type']}", S_META), Spacer(1, 3)])

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

    story.append(PageBreak())  # each question starts a fresh page (same as authoritative PDF)

if isinstance(story[-1], PageBreak):
    story.pop()

doc = BaseDocTemplate(NO_PDF, pagesize=A4,
                      leftMargin=MARG, rightMargin=MARG, topMargin=MARG, bottomMargin=MARG)
frame = Frame(MARG, MARG, AVAIL_W, PAGE_H - 2 * MARG, id='f')

def footer(canv, _doc):
    canv.saveState()
    canv.setFont('Segoe', 8)
    canv.setFillColor(colors.HexColor('#777777'))
    canv.drawString(MARG, 0.9 * cm,
                    'MTK_PAKET_2_CLAUDE_VISUAL_NO_KEY — Matematika Paket 2 (TKA Simulasi, Pusmendik)')
    canv.drawRightString(PAGE_W - MARG, 0.9 * cm, f'Hal. {canv.getPageNumber()}')
    canv.restoreState()

doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=footer)])
doc.build(story)
print('PDF written :', NO_PDF)

# ---------------------------------------------------------------- 3. validation
from pypdf import PdfReader

# --- JSON structure
nq = nokey['questions']
check('NO_KEY JSON 25/25 questions', len(nq) == 25, str(len(nq)))
check('NO_KEY JSON numbering 1..25', [q['number'] for q in nq] == list(range(1, 26)))

def field_names(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.add(str(k))
            field_names(v, acc)
    elif isinstance(o, list):
        for v in o:
            field_names(v, acc)
    return acc

names = field_names(nokey, set())
bad_names = sorted(nm for nm in names
                   if nm.lower() in FORBIDDEN_NAMES or 'official' in nm.lower()
                   or 'kunci' in nm.lower())
check('NO_KEY JSON has no answer-key field names', not bad_names,
      f'bad={bad_names}' + (f' (whitelisted: {sorted(WHITELISTED & names)})'
                            if WHITELISTED & names else ''))

# leak probes: exact serialized key strings from the authoritative package must be absent
blob = json.dumps(nokey, ensure_ascii=False)
leaks = []
for q in withkey['questions']:
    probes = [json.dumps(q['official_answer'], ensure_ascii=False),
              str(q['official_review_kunci_raw'])]
    if 'statements' in q:
        pass  # per-statement keys live inside official_answer already
    for p in probes:
        if p and p in blob:
            leaks.append((q['number'], p))
check('NO_KEY JSON contains no serialized key strings', not leaks, str(leaks[:5]))

# completeness: everything needed to solve must remain
def q_images(q):
    p = [i['rel_path'] for i in q['stimulus']['images']] + \
        [i['rel_path'] for i in q['question']['images']]
    if 'statements' in q:
        p += [s['image']['rel_path'] for s in q['statements'] if s['image']]
    else:
        p += [o['image']['rel_path'] for o in q['options'] if o['image']]
    return p

complete = all(
    q.get('id') and q.get('type') and q['stimulus'].get('text') is not None
    and q['question'].get('text') is not None
    and (('statements' in q and q['statements']) or q.get('options'))
    for q in nq)
check('NO_KEY JSON retains id/type/stimulus/question/options|statements for all', complete)
check('NO_KEY JSON image refs identical to authoritative package (ordered)',
      [q_images(q) for q in nq] == [q_images(q) for q in withkey['questions']])
check('NO_KEY JSON image files all exist on disk',
      all(os.path.exists(os.path.join(BASE, p)) for q in nq for p in q_images(q)),
      f'{sum(len(q_images(q)) for q in nq)} refs')

# --- PDF checks
r_no, r_with = PdfReader(NO_PDF), PdfReader(WITH_PDF)
check('NO_KEY PDF page count == authoritative PDF', len(r_no.pages) == len(r_with.pages),
      f'{len(r_no.pages)} vs {len(r_with.pages)}')
texts_no = [pg.extract_text() or '' for pg in r_no.pages]
full_no = '\n'.join(texts_no)
check('NO_KEY PDF has SOAL 1..25 sections',
      all(re.search(rf'\bSOAL {n}\b', full_no) for n in range(1, 26)))
check('NO_KEY PDF contains zero "KUNCI" occurrences', 'KUNCI' not in full_no.upper())
starts = {}
for i, t in enumerate(texts_no):
    m = re.search(r'\bSOAL (\d+)\b', t)
    if m and int(m.group(1)) not in starts:
        starts[int(m.group(1))] = i
check('NO_KEY PDF: all 25 sections start on own page', sorted(starts) == list(range(1, 26)))

def q_pages(reader, texts, n):
    s = starts[n]
    e = min((v for v in starts.values() if v > s), default=len(reader.pages))
    return range(s, e)

# same starts for the with-key PDF (layout identical)
starts_w = {}
for i, t in enumerate(pg.extract_text() or '' for pg in r_with.pages):
    m = re.search(r'\bSOAL (\d+)\b', t)
    if m and int(m.group(1)) not in starts_w:
        starts_w[int(m.group(1))] = i
check('section page layout identical in both PDFs', starts == starts_w,
      f'{len(starts)} sections mapped')

# per-question text equality (authoritative minus its KUNCI RESMI lines == NO_KEY).
# The with-key PDF's page-1 header carries the extra provenance clause
# "Kunci resmi: data/kunci/..." which NO_KEY intentionally omits; strip it too.
HEADER_KUNCI_CLAUSE = 'Kunci resmi: data/kunci/matematika_paket_2_kunci.json (tabel review simulasi resmi)'

def norm(t):
    t = t.replace(HEADER_KUNCI_CLAUSE, '')
    lines = [ln for ln in t.splitlines()
             if 'KUNCI RESMI' not in ln
             and not ln.startswith('MTK_PAKET_2_CLAUDE_VISUAL')
             and not ln.startswith('Hal.')]
    return '\n'.join(lines)

text_mism = []
def squash(t):
    return re.sub(r'\s+', ' ', t).strip()
for n in range(1, 26):
    tn = norm('\n'.join(texts_no[i] for i in q_pages(r_no, texts_no, n)))
    tw = norm('\n'.join((r_with.pages[i].extract_text() or '')
                        for i in q_pages(r_with, None, n)))
    if squash(tn) != squash(tw):   # whitespace-insensitive: extraction wraps lines differently
        text_mism.append(n)
check('NO_KEY PDF text == authoritative PDF text minus KUNCI lines (per question)',
      not text_mism, str(text_mism))

# pixel-losslessness + placement identity for the NO_KEY PDF
def pixhash(img):
    return hashlib.sha256(img.convert('RGBA').tobytes()).hexdigest()

src_hash = {}
for e in nokey['image_inventory']['images']:
    im = PILImage.open(os.path.join(BASE, e['rel_path']))
    src_hash[e['rel_path']] = pixhash(im)

decoded = {}
for pg in r_no.pages:
    for it in pg.images:
        nm = str(it.name).rsplit('.', 1)[0]
        decoded.setdefault(nm, it.image)
uniq_bad = [nm for nm, img in decoded.items() if pixhash(img) not in set(src_hash.values())]
check('NO_KEY PDF: every embedded image pixel-identical to source PNG', not uniq_bad,
      f'{len(decoded)} unique XObjects, bad={uniq_bad[:3]}')

def pdf_seq(reader, n):
    seq = []
    for pi in q_pages(reader, None, n):
        stream = reader.pages[pi].get_contents().get_data().decode('latin-1', 'replace')
        for nm in re.findall(r'/([A-Za-z0-9_.]+)\s+Do', stream):
            if nm in decoded:
                seq.append(pixhash(decoded[nm]))
    return seq

mism, order_bad = [], []
for q in nq:
    want = [src_hash[p] for p in q_images(q)]
    got = pdf_seq(r_no, q['number'])
    if Counter(got) != Counter(want):
        mism.append((q['number'], len(want), len(got)))
    elif got != want:
        order_bad.append(q['number'])
check('NO_KEY PDF placements match NO_KEY JSON per question (multiset)', not mism, str(mism))
check('NO_KEY PDF placement ORDER follows JSON on all questions', not order_bad, str(order_bad))

# ordering identity vs authoritative PDF: same per-question placement sequences
decoded_w = {}
for pg in r_with.pages:
    for it in pg.images:
        nm = str(it.name).rsplit('.', 1)[0]
        decoded_w.setdefault(nm, it.image)
seq_no = {n: pdf_seq(r_no, n) for n in range(1, 26)}
def pdf_seq_w(n):
    seq = []
    for pi in q_pages(r_with, None, n):
        stream = r_with.pages[pi].get_contents().get_data().decode('latin-1', 'replace')
        for nm in re.findall(r'/([A-Za-z0-9_.]+)\s+Do', stream):
            if nm in decoded_w:
                seq.append(pixhash(decoded_w[nm]))
    return seq
seq_w = {n: pdf_seq_w(n) for n in range(1, 26)}
check('image placement sequences identical: NO_KEY PDF == authoritative PDF', seq_no == seq_w)

# --- originals untouched (in-script before/after hash comparison)
WITH_KEY_SHA1 = {os.path.basename(p): hashlib.sha256(open(p, 'rb').read()).hexdigest()
                 for p in (WITH_JSON, WITH_PDF)}
check('authoritative package files untouched (sha256 before/after)',
      WITH_KEY_SHA0 == WITH_KEY_SHA1, str(WITH_KEY_SHA1))

print()
print('FAILURES:', fails if fails else 'none')
sys.exit(1 if fails else 0)
