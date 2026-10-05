# -*- coding: utf-8 -*-
"""Inspeksi blok card Paket 1 di home_desktop.html (versi setelah fix3)."""
import io

h = io.open('home_desktop.html', encoding='utf-8').read()
i = h.find('Paket 1')
print('idx Paket 1:', i)
print(h[max(0, i - 900):i + 1500])
