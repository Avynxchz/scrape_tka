import json, glob

for f in glob.glob('data/*_learning.json'):
    content = open(f, encoding='utf-8').read()
    u_fffd = content.count('\ufffd')
    u_00c2 = content.count('\u00c2')
    u_00a0 = content.count('\u00a0')
    if u_fffd or u_00c2 or u_00a0:
        print(f"{f}: u_fffd={u_fffd}, u_00c2={u_00c2}, u_00a0={u_00a0}")
