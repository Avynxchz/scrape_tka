# -*- coding: utf-8 -*-
"""Pasang home overlay versi Stitch (dari kode yang di-paste user) ke index.html.
Mengganti blok <div id="homeOverlay"> ... sebelum <!-- Sticky Modern App Header -->.
"""
import io
import sys

SRC_HTML = 'index.html'
BLOK = '''  <div id="homeOverlay" class="home-overlay" role="dialog" aria-label="Beranda TKA Master">
<!--HO_CONTENT-->
  </div>

'''

def build():
    html = io.open(SRC_HTML, encoding='utf-8').read()
    a = html.index('<div id="homeOverlay"')
    b = html.index('<!-- Sticky Modern App Header -->')
    new_html = html[:a] + BLOK + html[b:]
    io.open(SRC_HTML, 'w', encoding='utf-8').write(new_html)
    print('index.html: blok homeOverlay diganti (panjang blok lama', b - a, ')')

if __name__ == '__main__':
    build()
