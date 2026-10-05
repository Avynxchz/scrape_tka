# -*- coding: utf-8 -*-
"""Susun home_desktop.html: head Stitch desktop + body desktop + bridge data.
Kode Stitch desktop TIDAK diubah desainnya; hanya dipisah bagian script
bawaannya, lalu ditambah bridge postMessage + update angka real."""
import re

kode = open('scratch/_stitch_desktop_raw.html', encoding='utf-8').read()

head = kode[:kode.find('</head>') + 7]
body = kode[kode.find('<body'):]
# buang script bawaan stitch terakhir (interaksi modal dsb) — kita punya bridge sendiri
last_script = body.rfind('<script>')
body_static = body[:last_script]
print('head:', len(head), '| body statis:', len(body_static))

# tulis bagian yang akan digabung manual
open('scratch/_desk_head.html', 'w', encoding='utf-8').write(head)
open('scratch/_desk_body.html', 'w', encoding='utf-8').write(body_static)
print('OK: _desk_head.html & _desk_body.html disimpan')
