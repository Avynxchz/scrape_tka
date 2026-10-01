import glob
import json

req = ['concept_kunci', 'glossary', 'reasoning', 'steps', 'why_correct', 'tips', 'common_mistakes']
findings = []

for p in glob.glob('data/solution_sources/*.json'):
    if 'registry.json' in p:
        continue
    try:
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        for s in d.get('solutions', []):
            missing = [f for f in req if f not in s]
            if missing:
                findings.append((p, s.get('question_number'), s.get('question_id'), missing))
    except Exception as e:
        print(f"Error reading {p}: {e}")

if findings:
    print(f"Found {len(findings)} solutions with missing required Layer 3 fields:")
    for f in findings:
        print(f" - {f[0]} | Q{f[1]} ({f[2]}): missing {f[3]}")
else:
    print("ALL solutions have 100% of required Layer 3 fields!")
