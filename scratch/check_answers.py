import json, sys, re

sys.stdout.reconfigure(encoding='utf-8')

d = json.load(open('data/solution_sources/MTK_PAKET_2_SOLUTIONS_EXTRA.json', encoding='utf-8'))
for sol in d.get('solutions', []):
    no = sol.get('question_number')
    print(f"Q{no:02d}: answer={sol.get('official_answer')}")
