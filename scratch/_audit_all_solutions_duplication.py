import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json
import glob
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOL_DIR = os.path.join(ROOT, "data", "solution_sources")

print(f"{'='*80}")
print("🔍 AUDITING ALL SOLUTION SOURCES FOR BOILERPLATE / TEMPLATE / DUPLICATE PILLARS")
print(f"{'='*80}")

solution_files = glob.glob(os.path.join(SOL_DIR, "*_SOLUTIONS*.json"))

report = {}

for sfile in sorted(solution_files):
    fname = os.path.basename(sfile)
    try:
        with open(sfile, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading {fname}: {e}")
        continue
    
    solutions = data.get("solutions", [])
    if isinstance(data, list):
        solutions = data
    elif not solutions and isinstance(data, dict):
        # maybe keyed by question id or number
        solutions = [v for k, v in data.items() if isinstance(v, dict) and "steps" in v]
    
    total = len(solutions)
    if total == 0:
        continue
        
    reasonings = []
    step_texts = []
    concepts = []
    
    for s in solutions:
        r = (s.get("reasoning") or "").strip()
        reasonings.append(r)
        
        c = tuple(s.get("concept_kunci") or [])
        concepts.append(c)
        
        # Combined step explanations
        steps = s.get("steps") or []
        st_text = " || ".join([f"{st.get('title')}: {st.get('explanation')}" for st in steps if isinstance(st, dict)])
        step_texts.append(st_text)
        
    r_counts = Counter(reasonings)
    s_counts = Counter(step_texts)
    c_counts = Counter(concepts)
    
    # Check if more than 2 questions share the exact same reasoning or steps
    max_r_dup = max(r_counts.values()) if r_counts else 0
    max_s_dup = max(s_counts.values()) if s_counts else 0
    max_c_dup = max(c_counts.values()) if c_counts else 0
    
    is_fake_template = (max_r_dup > total * 0.4 and total > 3) or (max_s_dup > total * 0.4 and total > 3)
    
    status = "🚨 FAKE / BOILERPLATE TEMPLATE" if is_fake_template else "✅ UNIQUE & AUTHENTIC"
    print(f"\n📁 {fname:<45} Total: {total:>2} Soal | Status: {status}")
    print(f"   • Max Duplicate Reasoning: {max_r_dup}/{total}")
    print(f"   • Max Duplicate Steps    : {max_s_dup}/{total}")
    print(f"   • Max Duplicate Concepts : {max_c_dup}/{total}")
    
    if is_fake_template:
        most_common_r = r_counts.most_common(1)[0]
        most_common_s = s_counts.most_common(1)[0]
        print(f"   ⚠️ Contoh Reasoning Duplikat ({most_common_r[1]}x): {most_common_r[0][:100]}...")
        print(f"   ⚠️ Contoh Steps Duplikat ({most_common_s[1]}x): {most_common_s[0][:100]}...")
