import urllib.request, json, sys

sys.stdout.reconfigure(encoding='utf-8')
try:
    req = urllib.request.urlopen('http://localhost:8080/api/swarm/status')
    data = json.loads(req.read().decode('utf-8'))
    print('IS_RUNNING:', data.get('is_running'))
    print('ACTIVE_TARGET:', data.get('active_target'))
    print('CURRENT_DIVISION:', data.get('current_division'))
    print('PROGRESS:', data.get('progress'))
    print('\nLAST 30 LOGS:')
    for l in data.get('logs', [])[-30:]:
        print(f"[{l.get('time', '')}] [{l.get('tag', '')}] {l.get('message', '')}")
except Exception as e:
    print('Error:', e)
