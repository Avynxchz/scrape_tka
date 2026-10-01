# -*- coding: utf-8 -*-
import json, glob, re, ast

def normalize_ans(val):
    if val is None:
        return set()
    if isinstance(val, dict):
        if 'correct' in val:
            return normalize_ans(val['correct'])
        return {f"{k.upper()}:{str(v).upper()}" for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        res = set()
        for x in val:
            res.update(normalize_ans(x))
        return res
    s = str(val).strip()
    if (s.startswith('[') and s.endswith(']')) or (s.startswith('{') and s.endswith('}')):
        try:
            parsed = ast.literal_eval(s)
            return normalize_ans(parsed)
        except Exception:
            pass
    parts = [p.strip().upper() for p in re.split(r'[,;\n]+', s) if p.strip()]
    cleaned = set()
    for p in parts:
        p = re.sub(r'[\(\)\[\]\'\"]', '', p).strip()
        if p and p != '-':
            cleaned.add(p)
    return cleaned

print("Test normalization:")
print("List of letters:", normalize_ans(['A', 'E']))
print("String representation:", normalize_ans("['A', 'E']"))
print("Per statement list:", normalize_ans(['A:Salah', 'B:Benar']))
print("Per statement dict:", normalize_ans({'format': 'per_statement', 'correct': {'A': 'SALAH', 'B': 'BENAR'}}))
print("Single dict:", normalize_ans({'format': 'single', 'correct': ['C']}))
