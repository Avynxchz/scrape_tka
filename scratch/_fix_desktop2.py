# -*- coding: utf-8 -*-
"""Bersihkan sisa karangan + beri ID buat bridge di home_desktop.html."""
import io

h = io.open('home_desktop.html', encoding='utf-8').read()
h = h.replace('Hasil Diagnostik Terakhir', 'Progres Belajarmu')
h = h.replace('Akun Pro (Masa Beta)', 'Mode Tamu (Beta)')
h = h.replace('Aktif s/d Mei 2025', 'Gratis selama beta')

lama = '<span class="font-headline-xl text-headline-xl text-primary font-extrabold">92</span>'
baru = '<span id="deskSoalDikerjakan" class="font-headline-xl text-headline-xl text-primary font-extrabold">0</span>'
assert lama in h, 'pola 92 tidak ketemu'
h = h.replace(lama, baru)

io.open('home_desktop.html', 'w', encoding='utf-8').write(h)
print('OK, deskSoalDikerjakan terpasang:', h.count('deskSoalDikerjakan'))
