import json, os, re, sys
sys.path.insert(0, '.')

from pipeline.playwright_aistudio_bridge import safe_parse_json, text_quality, log

slug = 'bahasa_inggris_lanjut_paket_1'
raw_file = f'data/raw_llm_outputs/{slug}_5pillar_raw.txt'
kunci_path = f'data/kunci/{slug}_kunci.json'
sol_out = f'data/solution_sources/{slug.upper()}_SOLUTIONS.json'
sol_export = f'exports/{slug}_solutions.json'

with open(raw_file, 'r', encoding='utf-8') as f:
    raw_text = f.read()

with open(kunci_path, 'r', encoding='utf-8') as f:
    kunci_data = json.load(f)

kunci_map = {}
for k, v in kunci_data.get('kunci_pg', {}).items():
    kunci_map[str(k)] = v
for k, v in kunci_data.get('kunci_bs', {}).items():
    kunci_map[str(k)] = [f'{k_}:{v_}' for k_, v_ in sorted(v.items())]

parsed_solutions = safe_parse_json(raw_text) or []
print(f'Parsed solutions count: {len(parsed_solutions)}')

existing_sols_map = {}
for sol in parsed_solutions:
    if isinstance(sol, dict):
        no = sol.get('question_number')
        if no:
            existing_sols_map[int(no)] = sol

print(f'Extracted questions: {sorted(list(existing_sols_map.keys()))}')

for no, sol in existing_sols_map.items():
    sol['question_id'] = f'soal_p1_q{no:02d}'
    sol['concept_kunci'] = sol.get('concept_kunci') or sol.get('concept_tags') or ['Bahasa Inggris Tingkat Lanjut']
    raw_k = kunci_map.get(str(no), '-')
    if isinstance(raw_k, list):
        sol['official_answer'] = {'format': 'per_statement_benar_salah', 'correct': [str(x) for x in raw_k]}
    else:
        sol['official_answer'] = {'format': 'single_choice', 'correct': str(raw_k)}

    for fld in ('why_correct', 'reasoning', 'diketahui', 'ditanyakan', 'question_title'):
        if sol.get(fld):
            sol[fld] = text_quality.repair_math_text(
                re.sub(r'\btranskrip(?:si)?\b', 'kutipan', sol[fld], flags=re.I))
    for st in sol.get('steps', []):
        for fld in ('explanation', 'title'):
            if st.get(fld):
                st[fld] = text_quality.repair_math_text(
                    re.sub(r'\btranskrip(?:si)?\b', 'kutipan', st[fld], flags=re.I))
    for lst_key in ('tips', 'common_mistakes'):
        for i, item in enumerate(sol.get(lst_key) or []):
            if isinstance(item, str) and item.strip():
                sol[lst_key][i] = text_quality.repair_math_text(
                    re.sub(r'\btranskrip(?:si)?\b', 'kutipan', item, flags=re.I))

all_solutions = [existing_sols_map[k] for k in sorted(existing_sols_map.keys())]
sol_data = {'slug': slug, 'solutions': all_solutions}

with open(sol_out, 'w', encoding='utf-8') as f:
    json.dump(sol_data, f, indent=2, ensure_ascii=False)
with open(sol_export, 'w', encoding='utf-8') as f:
    json.dump(sol_data, f, indent=2, ensure_ascii=False)

print(f'Successfully re-saved {len(all_solutions)} solutions into {sol_out}!')
