import json, re

with open('data/raw_llm_outputs/bahasa_inggris_lanjut_paket_1_5pillar_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'^edit\s*more_vert\s*', '', text.strip())
m = re.search(r'\[.*\]', text, flags=re.DOTALL)
if m:
    text = m.group(0)

# Replace invalid backslashes (like \) or \% or \,)
cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)

try:
    data = json.loads(cleaned, strict=False)
    print('Cleaned json.loads SUCCESS! Items:', len(data))
except Exception as e:
    print('Failed:', e)
    # let's find the error location
    import traceback
    print('Context around 736 in cleaned:')
    print(repr(cleaned[710:760]))
