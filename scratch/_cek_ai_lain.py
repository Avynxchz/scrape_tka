# -*- coding: utf-8 -*-
"""Cek hasil AI lain: modul.html & progres.html."""
import re

for f in ('workspace_modul/modul.html', 'workspace_progres/progres.html'):
    h = open(f, encoding='utf-8').read()
    print('==', f, len(h), 'bytes')
    print('  html terkunci 1280px:', 'width: 1280px' in h)
    print('  html terkunci 390px :', 'width: 390px' in h)
    print('  postMessage:', 'postMessage' in h)
    print('  open-package:', 'open-package' in h)
    ids = re.findall(r'id="(modulDesktop|modulMobile|progresDesktop|progresMobile)"', h)
    print('  wrapper responsive:', ids)
    print('  ada 900px mq:', '900px' in h)
    # angka karangan?
    for pat in ['Skor 92', '84/100', 'Rian Pratama', 'Percentil']:
        if pat in h:
            print('  ANGKA KARANGAN:', pat)
