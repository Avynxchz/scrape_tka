# -*- coding: utf-8 -*-
import io, re

h = io.open('home_desktop.html', encoding='utf-8').read()
print('Paket 1 count:', h.count('Paket 1'))
print('Paket 2 count:', h.count('Paket 2'))
for m in list(re.finditer(r'Paket 1', h))[:3]:
    i = m.start()
    io.open('scratch/_insp3.txt', 'a', encoding='utf-8').write(
        '=== at %d ===\n%s\n\n' % (i, h[max(0, i - 150):i + 400]))
print('selesai -> scratch/_insp3.txt')
