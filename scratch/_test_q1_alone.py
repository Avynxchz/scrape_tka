import json_repair, json

with open('data/raw_llm_outputs/bahasa_inggris_lanjut_paket_1_5pillar_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect Q1 text specifically
q1_text = text[text.find('{"question_number": 1'):text.find('{"question_number": 2')]
print('Length of Q1 text:', len(q1_text))
print('Running json_repair on Q1 text alone...')
res = json_repair.loads(q1_text)
print('Result type:', type(res))
import re
def fix_json_escapes(s):
    return re.sub(r'(?<!\\)\\(?!["\\/bfnrtu]|u[0-9a-fA-F]{4})', r'\\\\', s)

fixed_q1 = fix_json_escapes(q1_text.rstrip(', \n'))
print('Testing json.loads on fixed Q1...')
try:
    obj = json.loads(fixed_q1, strict=False)
    print('json.loads on fixed Q1 SUCCESS!')
    print('Keys:', list(obj.keys()))
    print('Steps:', len(obj.get('steps', [])))
    print('Why correct len:', len(obj.get('why_correct', '')))
except Exception as e:
    print('json.loads error:', e)
    print('Char 735 area:', repr(fixed_q1[720:750]))
