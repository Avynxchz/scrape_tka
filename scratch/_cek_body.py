# -*- coding: utf-8 -*-
"""Cek isi home_desktop.html: mana body & mana script. Terlihat body hilang!"""
import io

h = io.open('home_desktop.html', encoding='utf-8').read()
print('panjang:', len(h))
print('posisi <body:', h.find('<body'))
print('posisi </body:', h.find('</body'))
print('posisi <script terakhir:', h.rfind('<script>'))
print('posisi </html:', h.find('</html>'))
print('posisi <main:', h.find('<main'))
print('posisi <aside:', h.find('<aside'))
# tampilkan 300 char setelah <body
b = h.find('<body')
print(h[b:b+300])
