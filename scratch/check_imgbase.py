import re, os

with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

current_subject = None
for line in lines:
    sm = re.search(r'^\s{2}(\w+):\s*\{', line)
    if sm:
        current_subject = sm.group(1)
    bm = re.search(r'1:\s*[\'"]([^\'"]+)[\'"]', line)
    if bm and current_subject:
        p1 = bm.group(1)
        p1_dir = os.path.join(p1, 'images')
        print(f"{current_subject} p1: {p1} -> images dir exists: {os.path.isdir(p1_dir)} ({len(os.listdir(p1_dir)) if os.path.isdir(p1_dir) else 0} files)")
    bm2 = re.search(r'2:\s*[\'"]([^\'"]+)[\'"]', line)
    if bm2 and current_subject:
        p2 = bm2.group(1)
        p2_dir = os.path.join(p2, 'images')
        print(f"{current_subject} p2: {p2} -> images dir exists: {os.path.isdir(p2_dir)} ({len(os.listdir(p2_dir)) if os.path.isdir(p2_dir) else 0} files)")
