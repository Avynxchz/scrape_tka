# -*- coding: utf-8 -*-
"""_build_retest_pkg.py — Re-test package for the 6 problematic MTK Paket 2 questions.

Derived ONLY from the validated NO_KEY context (no answer keys) + raw image assets.
Creates claude_input/retest/ with:
  MTK_P2_RETEST_CONTEXT_NO_KEY.json  — 6 questions, no key info, image refs -> ./images
  MTK_P2_RETEST_VISUAL.pdf           — visual rendering, NO KUNCI RESMI
  images/                            — ORIGINAL PNG files copied byte-for-byte

Validates: 6/6 questions, images exist, JSON<->PDF placement identity (pixel-hashed,
ordered), zero key info, originals untouched. NEVER writes to authoritative data.
"""
import json, os, re, sys, hashlib, shutil, copy
from collections import Counter
from PIL import Image as PILImage

BASE = os.path.dirname(os.path.abspath(__file__))
NO_JSON = os.path.join(BASE, 'claude_input', 'MTK_PAKET_2_CLAUDE_CONTEXT_NO_KEY.json')
RETEST = os.path.join(BASE, 'claude_input', 'retest')
OUT_JSON = os.path.join(RETEST, 'MTK_P2_RETEST_CONTEXT_NO_KEY.json')
OUT_PDF = os.path.join(RETEST, 'MTK_P2_RETEST_VISUAL.pdf')
IMG_DIR = os.path.join(RETEST, 'images')
WANT = [1, 2, 3, 11, 20, 25]

# snapshot originals to prove untouched afterwards
GUARDED = [NO_JSON,
           os.path.join(BASE, 'claude_input', 'MTK_PAKET_2_CLAUDE_CONTEXT.json'),
           os.path.join(BASE, 'claude_input', 'MTK_PAKET_2_CLAUDE_VISUAL.pdf'),
           os.path.join(BASE, 'claude_input', 'MTK_PAKET_2_CLAUDE_VISUAL_NO_KEY.pdf'),
           os.path.join(BASE, 'data', 'paket_2', 'matematika_paket_2.json'),
           os.path.join(BASE, 'data', 'matematika_paket_2_learning.json'),
           os.path.join(BASE, 'data', 'kunci', 'matematika_paket_2_kunci.json')]
SHA0 = {p: hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in GUARDED}

fails = []
def check(name, ok, detail=''):
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f' — {detail}' if detail else ''))
    if not ok:
        fails.append(name)

# ---------------------------------------------------------------- build JSON
src = json.load(open(NO_JSON, encoding='utf-8'))
qs = [copy.deepcopy(q) for q in src['questions'] if q['number'] in WANT]
qs.sort(key=lambda q: q['number'])
check('6/6 selected questions found', [q['number'] for q in qs] == WANT)

os.makedirs(IMG_DIR, exist_ok=True)
copied, missing = [], []
for q in qs:
    paths = ([i['rel_path'] for i in q['stimulus']['images']]
             + [i['rel_path'] for i in q['question']['images']])
    if 'statements' in q:
        paths += [s['image']['rel_path'] for s in q['statements'] if s['image']]
        paths += [o['image']['rel_path'] for o in q.get('source_table_options', []) if o.get('image')]
    else:
        paths += [o['image']['rel_path'] for o in q['options'] if o['image']]
    for rp in paths:
        full_src = os.path.join(BASE, rp)
        fn = os.path.basename(rp)
        dst = os.path.join(IMG_DIR, fn)
        if not os.path.exists(full_src):
            missing.append(rp)
            continue
        if not os.path.exists(dst):
            shutil.copy2(full_src, dst)  # byte-for-byte original quality
        copied.append((q['number'], fn, full_src, dst))
check('all referenced images found in repo', not missing, str(missing))
check('copied images byte-identical to originals',
      all(hashlib.sha256(open(s, 'rb').read()).hexdigest()
          == hashlib.sha256(open(d, 'rb').read()).hexdigest() for _, _, s, d in copied),
      f'{len({fn for _, fn, _, _ in copied})} unique files')

# rewrite image refs to retest-local rel_paths (keep remote_url for provenance)
def remap(ref):
    if not ref:
        return None
    return {'filename': ref['filename'],
            'rel_path': 'images/' + ref['filename'],
            'remote_url': ref.get('remote_url'),
            'source_rel_path': ref.get('rel_path')}

def remap_q(q):
    for coll in (q['stimulus']['images'], q['question']['images']):
        for i, r in enumerate(coll):
            coll[i] = remap(r)
    for key in ('statements', 'options', 'source_table_options'):
        for item in q.get(key, []):
            if item.get('image'):
                item['image'] = remap(item['image'])
    return q

qs = [remap_q(q) for q in qs]
unique_files = sorted({os.path.basename(s) for _, _, s, _ in copied})
retest = {
    'meta': {
        'subject': 'Matematika',
        'package': 2,
        'purpose': ('RE-TEST subset: the 6 problematic questions (1, 2, 3, 11, 20, 25) for an '
                    'independent Claude Web re-test. NO answer-key information is included. '
                    'Derived from MTK_PAKET_2_CLAUDE_CONTEXT_NO_KEY.json (validated).'),
        'total_questions': len(qs),
        'question_numbers': [q['number'] for q in qs],
        'origin': 'https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/',
        'visual_pdf': 'MTK_P2_RETEST_VISUAL.pdf',
        'images_dir': 'images/',
        'image_count': len(unique_files),
    },
    'questions': qs,
}
json.dump(retest, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('JSON written:', OUT_JSON)

# ---------------------------------------------------------------- build PDF
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
    full = os.path.join(RETEST, rel_path)
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

story = []
story.append(Paragraph('MATEMATIKA PAKET 2 — RE-TEST (SOAL 1, 2, 3, 11, 20, 25)', S_TITLE))
story.append(Paragraph(
    'TKA Simulasi — Pusmendik Kemendikdasmen (https://pusmendik.kemendikdasmen.go.id/tka/simulasi_tka/) '
    '&nbsp;|&nbsp; 6 soal &nbsp;|&nbsp; Ekspresi matematika pada soal asli tersaji sebagai gambar — gambar tersebut '
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
        # raw-table option images not already shown as statement images (lossless)
        extra = [o.get('image') for o in rec.get('source_table_options', [])
                 if o.get('image') and not any(
                     s['image'] and s['image']['filename'] == o['image']['filename']
                     for s in rec['statements'])]
        if extra:
            story.append(Paragraph('TABEL SUMBER (OPSI ASLI)', S_LABEL))
            story.extend(img_par_block(extra))
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

    story.append(PageBreak())

if isinstance(story[-1], PageBreak):
    story.pop()

doc = BaseDocTemplate(OUT_PDF, pagesize=A4,
                      leftMargin=MARG, rightMargin=MARG, topMargin=MARG, bottomMargin=MARG)
frame = Frame(MARG, MARG, AVAIL_W, PAGE_H - 2 * MARG, id='f')

def footer(canv, _doc):
    canv.saveState()
    canv.setFont('Segoe', 8)
    canv.setFillColor(colors.HexColor('#777777'))
    canv.drawString(MARG, 0.9 * cm, 'MTK_P2_RETEST — Matematika Paket 2 (TKA Simulasi, Pusmendik)')
    canv.drawRightString(PAGE_W - MARG, 0.9 * cm, f'Hal. {canv.getPageNumber()}')
    canv.restoreState()

doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=footer)])
doc.build(story)
print('PDF written :', OUT_PDF)

# ---------------------------------------------------------------- validation
from pypdf import PdfReader

check('RETEST JSON 6/6 questions', len(qs) == 6 and [q['number'] for q in qs] == WANT)
check('RETEST JSON images all exist in retest/images',
      all(os.path.exists(os.path.join(RETEST, p)) for q in qs
          for p in ([i['rel_path'] for i in q['stimulus']['images']]
                    + [i['rel_path'] for i in q['question']['images']]
                    + ([s['image']['rel_path'] for s in q.get('statements', []) if s['image']]
                       if 'statements' in q else
                       [o['image']['rel_path'] for o in q.get('options', []) if o['image']]))))

def field_names(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.add(str(k))
            field_names(v, acc)
    elif isinstance(o, list):
        for v in o:
            field_names(v, acc)
    return acc

names = field_names(retest, set())
bad_names = sorted(nm for nm in names if 'kunci' in nm.lower() or 'official' in nm.lower())
check('RETEST JSON has no answer-key field names', not bad_names, str(bad_names))
blob = json.dumps(retest, ensure_ascii=False)
leak_words = ['KUNCI RESMI', 'kunci_jawaban', 'official_answer', 'review simulasi resmi']
leaks = [w for w in leak_words if w in blob]
check('RETEST JSON contains no key strings', not leaks, str(leaks))

r = PdfReader(OUT_PDF)
texts = [pg.extract_text() or '' for pg in r.pages]
full = '\n'.join(texts)
check('RETEST PDF has SOAL 1,2,3,11,20,25 sections',
      all(re.search(rf'\bSOAL {n}\b', full) for n in WANT))
check('RETEST PDF contains zero "KUNCI"', 'KUNCI' not in full.upper())
starts = {}
for i, t in enumerate(texts):
    m = re.search(r'\bSOAL (\d+)\b', t)
    if m and int(m.group(1)) not in starts:
        starts[int(m.group(1))] = i
check('RETEST PDF: each of the 6 sections starts on own page',
      sorted(starts) == WANT)

def q_pages(n):
    s = starts[n]
    e = min((v for v in starts.values() if v > s), default=len(r.pages))
    return range(s, e)

def pixhash(img):
    return hashlib.sha256(img.convert('RGBA').tobytes()).hexdigest()

src_hash = {}
for fn in unique_files:
    im = PILImage.open(os.path.join(IMG_DIR, fn))
    src_hash['images/' + fn] = pixhash(im)

decoded = {}
for pg in r.pages:
    for it in pg.images:
        nm = str(it.name).rsplit('.', 1)[0]
        decoded.setdefault(nm, it.image)
uniq_bad = [nm for nm, img in decoded.items() if pixhash(img) not in set(src_hash.values())]
check('RETEST PDF: every embedded image pixel-identical to copied original', not uniq_bad,
      f'{len(decoded)} XObjects, bad={uniq_bad[:3]}')

def json_seq(q):
    seq = ([i['rel_path'] for i in q['stimulus']['images']]
           + [i['rel_path'] for i in q['question']['images']])
    if 'statements' in q:
        seq += [s['image']['rel_path'] for s in q['statements'] if s['image']]
        seq += [o['image']['rel_path'] for o in q.get('source_table_options', [])
                if o.get('image') and not any(
                    s['image'] and s['image']['filename'] == o['image']['filename']
                    for s in q['statements'])]
    else:
        seq += [o['image']['rel_path'] for o in q['options'] if o['image']]
    return seq

mism, order_bad = [], []
for q in qs:
    want = [src_hash[p] for p in json_seq(q)]
    got = []
    for pi in q_pages(q['number']):
        stream = r.pages[pi].get_contents().get_data().decode('latin-1', 'replace')
        for nm in re.findall(r'/([A-Za-z0-9_.]+)\s+Do', stream):
            if nm in decoded:
                got.append(pixhash(decoded[nm]))
    if Counter(got) != Counter(want):
        mism.append((q['number'], len(want), len(got)))
    elif got != want:
        order_bad.append(q['number'])
check('RETEST PDF placements match JSON per question (multiset)', not mism, str(mism))
check('RETEST PDF placement ORDER follows JSON on all 6', not order_bad, str(order_bad))

total_refs = sum(len(json_seq(q)) for q in qs)
check('RETEST JSON<->PDF<->images consistency (placement count)', True,
      f'{total_refs} placements, {len(unique_files)} unique files in images/')

# originals untouched
SHA1 = {p: hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in GUARDED}
check('authoritative + existing package files untouched', SHA0 == SHA1)

print()
print('FAILURES:', fails if fails else 'none')
sys.exit(1 if fails else 0)
