import json, re
js = open('app.js', encoding='utf-8').read()
# Nama mapel dari dropdown index.html biar 100% sinkron
html = open('index.html', encoding='utf-8').read()
pairs = re.findall(r'<option value="(\w+)">([^<]+)</option>', html)
print(len(pairs), 'mapel')
out = {k: v for k, v in pairs}
print(json.dumps(out, ensure_ascii=False, indent=0))
