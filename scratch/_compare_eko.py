import json
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOL_DIR = os.path.join(ROOT, "data", "solution_sources")

p1 = os.path.join(SOL_DIR, "EKONOMI_PAKET_1_SOLUTIONS.json")
p1_old = os.path.join(SOL_DIR, "EKO_PAKET_1_SOLUTIONS.json")

print("Checking EKONOMI_PAKET_1_SOLUTIONS.json (new file):")
if os.path.exists(p1):
    doc1 = json.load(open(p1, encoding="utf-8"))
    sols = doc1.get("solutions", [])
    print(f"  Total solutions: {len(sols)}")
    if sols:
        print(f"  Q1 reasoning: {sols[0].get('reasoning')[:150]}...")
        if len(sols) > 1:
            print(f"  Q2 reasoning: {sols[1].get('reasoning')[:150]}...")
            print(f"  Are Q1 and Q2 reasoning identical? {sols[0].get('reasoning') == sols[1].get('reasoning')}")

print("\nChecking EKO_PAKET_1_SOLUTIONS.json (old file):")
if os.path.exists(p1_old):
    doc_old = json.load(open(p1_old, encoding="utf-8"))
    sols_old = doc_old.get("solutions", [])
    print(f"  Total solutions: {len(sols_old)}")
    if sols_old:
        print(f"  Q1 reasoning: {sols_old[0].get('reasoning')[:150]}...")
        if len(sols_old) > 1:
            print(f"  Q2 reasoning: {sols_old[1].get('reasoning')[:150]}...")
            print(f"  Are Q1 and Q2 reasoning identical? {sols_old[0].get('reasoning') == sols_old[1].get('reasoning')}")
