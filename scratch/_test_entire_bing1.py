import json, re

with open('data/raw_llm_outputs/bahasa_inggris_lanjut_paket_1_5pillar_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'^edit\s*more_vert\s*', '', text.strip())
m = re.search(r'\[.*\]', text, flags=re.DOTALL)
if m:
    text = m.group(0)

def fix_json_escapes(s):
    return re.sub(r'(?<!\\)\\(?!["\\/bfnrtu]|u[0-9a-fA-F]{4})', r'\\\\', s)

fixed = fix_json_escapes(text)
print('Testing json.loads on entire fixed text...')
try:
    data = json.loads(fixed, strict=False)
    print('SUCCESS! Total items:', len(data))
    for q in data:
        no = q.get('question_number')
        steps = len(q.get('steps', []))
        why = len(q.get('why_correct', ''))
        print(f'  Q{no}: steps={steps}, why_correct={why} chars, title={q.get("question_title")[:40]}')
except Exception as e:
    print('Failed:', e)
