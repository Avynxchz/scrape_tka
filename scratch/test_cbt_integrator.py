# -*- coding: utf-8 -*-
import json
import urllib.request

tests = [
    ('geografi', 2, 1),
    ('fisika', 1, 1),
    ('fisika', 2, 1)
]

for s, p, n in tests:
    req = urllib.request.Request(
        'http://localhost:8080/api/solution',
        data=json.dumps({'subject': s, 'paket': p, 'nomor': n}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    res = urllib.request.urlopen(req)
    d = json.loads(res.read().decode('utf-8'))
    print(f"{s} P{p} Q{n}: status={d.get('status')}")
    sol = d.get('solution') or {}
    pb = sol.get('pembahasan') or {}
    print("   Konsep:", pb.get('konsep_kunci'))
    print("   Langkah count:", len(pb.get('langkah_penyelesaian', [])))
    print("   Glosarium count:", len(pb.get('glosarium_simbol', [])))
    print("   Answer display:", sol.get('answer_display'))
