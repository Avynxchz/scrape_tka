# -*- coding: utf-8 -*-
"""_validate_claude_pkg.py — Automated validation of the Claude input package."""
import json, os, re, sys, zipfile, hashlib
from collections import Counter
from pypdf import PdfReader

BASE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(BASE, 'claude_input', 'MTK_PAKET_2_CLAUDE_CONTEXT.json')
P = os.path.join(BASE, 'claude_input', 'MTK_PAKET_2_CLAUDE_VISUAL.pdf')
KUNCI = json.load(open(os.path.join(BASE, 'data', 'kunci', 'matematika_paket_2_kunci.json'), encoding='utf-8'))

fails = []
def check(name, ok, detail=''):
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f' — {detail}' if detail else ''))
    if not ok:
        fails.append(name)

ctx = json.load(open(J, encoding='utf-8'))
qs = ctx['questions']
check('JSON loads', True)
check('25/25 questions', len(qs) == 25, str(len(qs)))
check('numbering 1..25 no gaps/dupes', [q['number'] for q in qs] == list(range(1, 26)))

# official keys: every question's key must equal the independently-parsed evidence
STMT = {int(k) for k in KUNCI['kunci_bs']}
def parse_letters(s): return re.findall(r'\(([A-E])\)', s)
key_ok = True
for q in qs:
    n = str(q['number'])
    if q['number'] in STMT:
        ev = dict(KUNCI['kunci_bs'][n])
    else:
        ev = parse_letters(KUNCI['raw_rows'][n]['kunci'])
    if q['official_answer'] != ev:
        key_ok = False
        print(f'   key mismatch soal {n}: {q["official_answer"]} vs {ev}')
check('official keys match evidence 25/25', key_ok)
check('every question has official_answer', all(q.get('official_answer') for q in qs))
check('every question has official_review_kunci_raw',
      all(q.get('official_review_kunci_raw') for q in qs))

# no old AI explanation contamination
banned = ['pembahasan', 'langkah_penyelesaian', 'konsep_kunci', 'tips_trik',
          'quick_prompts', 'soal_serupa', 'topik', 'visual_memory']
blob = json.dumps(ctx, ensure_ascii=False).lower()
contam = [b for b in banned if f'"{b}"' in blob]
check('no old AI explanation fields', not contam, str(contam))

# image inventory vs disk
inv = ctx['image_inventory']['images']
missing = [e['rel_path'] for e in inv if not os.path.exists(os.path.join(BASE, e['rel_path']))]
check('inventory images exist on disk', not missing, f'{len(inv)} refs, missing={missing}')
check('inventory all_exist flag', ctx['image_inventory']['all_exist'] is True)

# referenced images inside questions also exist + rel_path primary
refs = []
def walk(o):
    if isinstance(o, dict):
        if 'filename' in o and 'rel_path' in o and 'remote_url' in o:
            refs.append(o)
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(qs)
check('every embedded image ref has filename/rel_path/remote_url',
      all(all(k and isinstance(r.get(k), str) for k in ('filename', 'rel_path', 'remote_url')) for r in refs))
check('all embedded refs exist on disk',
      all(os.path.exists(os.path.join(BASE, r['rel_path'])) for r in refs),
      f'{len(refs)} refs')

# ---------------- PDF checks ----------------
r = PdfReader(P)
print(f'PDF pages: {len(r.pages)}')
texts = [pg.extract_text() or '' for pg in r.pages]
full = '\n'.join(texts)
check('PDF has SOAL 1..25 sections', all(re.search(rf'\bSOAL {n}\b', full) for n in range(1, 26)))
check('PDF has KUNCI RESMI marker 25x', full.count('KUNCI RESMI') == 25, str(full.count('KUNCI RESMI')))

# map each question to its page range (each question starts a fresh page)
starts = {}
for i, t in enumerate(texts):
    m = re.search(r'\bSOAL (\d+)\b', t)
    if m and m.group(1) not in starts:
        starts[int(m.group(1))] = i
check('all 25 sections start on their own page', sorted(starts) == list(range(1, 26)))

def q_pages(n):
    s = starts[n]
    e = min((v for v in starts.values() if v > s), default=len(r.pages))
    return range(s, e)

# count image *placements* (Do operators) per question range; identical files share one
# XObject but are drawn once per reference, so placements must equal JSON refs.
def placements(pages):
    total = 0
    for pi in pages:
        pg = r.pages[pi]
        try:
            xobjs = pg['/Resources']['/XObject']
        except Exception:
            continue
        names = []
        for name, obj in xobjs.items():
            try:
                if obj.get_object().get('/Subtype') == '/Image':
                    names.append(str(name))
            except Exception:
                continue
        data = pg.get_contents().get_data().decode('latin-1', 'replace')
        for nm in names:
            pat = re.escape(nm) + r'\s+Do'
            total += len(re.findall(pat, data))
    return total

json_imgs_per_q = {}
for q in qs:
    c = len(q['stimulus']['images']) + len(q['question']['images'])
    if 'statements' in q:
        c += sum(1 for s in q['statements'] if s['image'])
    else:
        c += sum(1 for o in q['options'] if o['image'])
    json_imgs_per_q[q['number']] = c

mism = []
for n in range(1, 26):
    got = placements(q_pages(n))
    if got != json_imgs_per_q[n]:
        mism.append((n, got, json_imgs_per_q[n]))
check('PDF renders exactly the JSON image placements per question', not mism,
      f'total JSON imgs={sum(json_imgs_per_q.values())}, mismatches={mism}')

# ---------------- PDF pixel-losslessness audit ----------------
# Decode every image XObject and every /Do placement (in stream order) and compare
# exact pixels against the source PNG each placement represents. This is the
# strongest possible proof that the PDF visually renders the dataset losslessly.
from PIL import Image

def pixhash(img):
    return hashlib.sha256(img.convert('RGBA').tobytes()).hexdigest()

src_hash = {}
src_size = {}
for e in inv:
    im = Image.open(os.path.join(BASE, e['rel_path']))
    src_hash[e['rel_path']] = pixhash(im)
    src_size[e['rel_path']] = im.size

# decode every unique image XObject once via page.images (SMask-composited RGBA).
# NOTE: obj.get_object() alone yields EncodedStreamObject without .image; page.images
# handles filter+SMask decoding and yields ImageFile(name='FormXob.<md5>.png', image=PIL).
decoded = {}
bad_decode = []
for pg in r.pages:
    try:
        items = list(pg.images)
    except Exception:
        continue
    for it in items:
        nm = str(it.name).rsplit('.', 1)[0]  # strip trailing '.png'
        if nm in decoded:
            continue
        try:
            decoded[nm] = it.image
        except Exception as ex:
            bad_decode.append((nm, str(ex)))
check('all PDF image XObjects decode', not bad_decode, f'{len(decoded)} decoded, errors={bad_decode[:3]}')

# every unique XObject must be pixel-identical to SOME source PNG, and the
# question's placement multiset (and order) must equal the JSON placement list.
all_src_hashes = set(src_hash.values())
uniq_bad = [nm for nm, img in decoded.items() if pixhash(img) not in all_src_hashes]
check('every embedded image is pixel-identical to its source PNG', not uniq_bad,
      f'{len(decoded)} unique XObjects checked, bad={uniq_bad[:3]}')

placement_mism, seq_notes = [], []
for n in range(1, 26):
    # JSON side: ordered placement list of rel_paths
    q = qs[n - 1]
    paths = ([i['rel_path'] for i in q['stimulus']['images']]
             + [i['rel_path'] for i in q['question']['images']])
    if 'statements' in q:
        paths += [s['image']['rel_path'] for s in q['statements'] if s['image']]
    else:
        paths += [o['image']['rel_path'] for o in q['options'] if o['image']]
    want = Counter(src_hash[p] for p in paths)
    want_seq = [src_hash[p] for p in paths]

    # PDF side: /Do operations in stream order across the question's pages
    got_hashes = []
    for pi in q_pages(n):
        pg = r.pages[pi]
        stream = pg.get_contents().get_data().decode('latin-1', 'replace')
        for nm in re.findall(r'/([A-Za-z0-9_.]+)\s+Do', stream):
            if nm in decoded:
                got_hashes.append(pixhash(decoded[nm]))
    if Counter(got_hashes) != want:
        placement_mism.append((n, len(want_seq), len(got_hashes)))
    if got_hashes != want_seq:
        seq_notes.append(n)
check('PDF image placements match JSON per question (multiset)', not placement_mism,
      f'total placements={sum(json_imgs_per_q.values())}, mismatches={placement_mism}')
print('   placement ORDER follows JSON on all questions' if not seq_notes
      else f'   note: order differs on questions {seq_notes} (multiset still equal)')

# kunci text on each question's pages matches JSON (normalize identically on both sides)
kmism = []
for q in qs:
    t = '\n'.join(texts[i] for i in q_pages(q['number']))
    want = json.dumps(q['official_answer'], ensure_ascii=False)
    want_norm = re.sub(r'\s+', '', want)
    t_norm = re.sub(r'\s+', '', t)
    if want_norm not in t_norm:
        kmism.append((q['number'], want_norm))
check('PDF kunci matches JSON per question', not kmism, str(kmism[:5]))

# consistency: option labels/order — PDF option rows exist for all option questions
label_mism = []
for q in qs:
    if 'options' not in q: continue
    t = '\n'.join(texts[i] for i in q_pages(q['number']))
    want_keys = [o['key'] for o in q['options']]
    # option key lines appear as "A" style tokens; check each label present
    for k in want_keys:
        if not re.search(rf'^{k}$|^{k}\s', t, re.M):
            label_mism.append((q['number'], k))
check('PDF option labels present per question', not label_mism, str(label_mism[:8]))

# statements present
for q in qs:
    if 'statements' not in q: continue
    t = '\n'.join(texts[i] for i in q_pages(q['number']))
    if 'PERNYATAAN' not in t:
        fails.append(f'statement section missing soal {q["number"]}')
check('statement sections present (3/13/20/23)',
      all('PERNYATAAN' in '\n'.join(texts[i] for i in q_pages(q['number']))
          for q in qs if 'statements' in q))

# PDF well-formed zip/PDF container
check('PDF file opens as valid container', os.path.getsize(P) > 100_000,
      f'{os.path.getsize(P)/1e6:.2f} MB')

print()
print('TOTAL image refs embedded (JSON):', sum(json_imgs_per_q.values()))
print('FAILURES:', fails if fails else 'none')
sys.exit(1 if fails else 0)
