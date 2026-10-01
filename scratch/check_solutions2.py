import json, sys

sys.stdout.reconfigure(encoding='utf-8')

d = json.load(open('data/solution_sources/MTK_PAKET_2_SOLUTIONS_EXTRA.json', encoding='utf-8'))
for sol in d.get('solutions', []):
    no = sol.get('question_number')
    print(f"=== Q{no:02d} ===")
    print(f"  steps: {len(sol.get('steps', []))}")
    for st in sol.get('steps', []):
        title = st.get('title', '')
        expl = st.get('explanation', '')[:150]
        print(f"    step {st.get('step')}: {title} | {expl}...")
    print(f"  concept_kunci: {sol.get('concept_kunci', [])}")
    print(f"  reasoning: {repr(sol.get('reasoning', '')[:200])}")
    print(f"  tips: {sol.get('tips', [])}")
    print(f"  common_mistakes: {sol.get('common_mistakes', [])}")
    print()
