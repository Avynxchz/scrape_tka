import urllib.request, json, sys

sys.stdout.reconfigure(encoding='utf-8')
try:
    req = urllib.request.urlopen('http://127.0.0.1:9222/json')
    tabs = json.loads(req.read().decode('utf-8'))
    print(f'Total targets in Chrome 9222: {len(tabs)}')
    for i, t in enumerate(tabs):
        print(f"{i+1}. [{t.get('type')}] {t.get('title', '')[:50]} | {t.get('url', '')[:80]}")
except Exception as e:
    print('Error connecting to 9222:', e)
