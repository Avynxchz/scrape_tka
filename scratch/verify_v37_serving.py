import urllib.request

html = urllib.request.urlopen('http://localhost:8080/index.html').read().decode('utf-8')
print('style.css?v=37 in html:', 'style.css?v=37' in html)
print('app.js?v=37 in html:', 'app.js?v=37' in html)

css = urllib.request.urlopen('http://localhost:8080/style.css?v=37').read().decode('utf-8')
print('\nTargeted CSS rules present in style.css:')
rules = [
    'data-nomor="9"',
    'data-nomor="11"',
    'data-nomor="19"',
    'data-nomor="8"',
    'data-nomor="16"',
    'data-nomor="18"',
    'data-nomor="20"',
    'data-nomor="1"',
    'data-nomor="4"',
    'data-nomor="21"',
    'data-nomor="23"',
    'data-nomor="25"',
]
all_ok = True
for r in rules:
    present = r in css
    if not present: all_ok = False
    print(f'  {r}: {present}')

print(f'\nAll target rules verified: {all_ok}')
