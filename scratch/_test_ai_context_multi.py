# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, ".")
import server, tutor_engine
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

test_cases = [
    ('matematika', 2, 3, 'Matematika Paket 2 Q3 (Pernyataan)'),
    ('biologi', 1, 1, 'Biologi Paket 1 Q1 (Biologi Sel/Diagram)'),
    ('fisika', 1, 2, 'Fisika Paket 1 Q2 (Fisika Mekanika)'),
    ('bahasa_indonesia', 1, 3, 'B. Indo Paket 1 Q3 (PG Kompleks)'),
    ('geografi', 1, 4, 'Geografi Paket 1 Q4 (Geografi Sosial)')
]

for subj, pkt, qnum, label in test_cases:
    ctx = server.resolve_tutor_context(subj, pkt, qnum)
    if not ctx:
        print(f"[FAIL] {label}: context is None!")
        continue
    msgs, temp = tutor_engine.build_tutor_prompt(
        ctx['canon_ctx'], ctx['solution'], ctx['official_answer'],
        history_msgs=[],
        user_message='Pertanyaan tes konteks',
        summary='',
        subject_name=ctx['subject_name']
    )
    c = msgs[0]['content']
    has_soal = '<question_context>' in c
    has_opts = ('[OPSI JAWABAN]' in c) or ('[PERNYATAAN' in c)
    has_key = '<official_answer>' in c and bool(ctx['official_answer'])
    has_sol = '[PILAR' in c or '[LANGKAH' in c or 'Konsep' in c
    has_sim = '[SOAL SERUPA' in c
    ans = ctx['official_answer']
    print(f"[PASS] {label}:")
    print(f"       Soal={has_soal} | Opsi/Stmt={has_opts} | Kunci={has_key} ({ans}) | Pilar={has_sol} | SoalSerupa={has_sim}")
