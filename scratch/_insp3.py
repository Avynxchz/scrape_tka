# -*- coding: utf-8 -*-
import io, re

h = io.open('home_desktop.html', encoding='utf-8').read()
out = []
for m in re.finditer(r'<h3[^>]*>[^<]*Paket 1', h):
    i = m.start()
    out.append('=== h3 at %d ===' % i)
    out.append(h[i:i + 1600])
io.open('scratch/_insp2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ketemu:', len(out))
