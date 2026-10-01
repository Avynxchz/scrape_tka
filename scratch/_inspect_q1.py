import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/raw_llm_outputs/bahasa_inggris_lanjut_paket_1_5pillar_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

q1_start = text.find('"question_number": 1')
q2_start = text.find('"question_number": 2')
print(text[q1_start:q2_start])
