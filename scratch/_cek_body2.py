# -*- coding: utf-8 -*-
"""Inspeksi _desk_body.html: apakah ada <script> di tengah yang memotong body?"""
import io, re

b = io.open('scratch/_desk_body.html', encoding='utf-8').read()
print('panjang body sumber:', len(b))
for m in re.finditer(r'<script', b):
    print('script di', m.start())
for m in re.finditer(r'</script>', b):
    print('/script di', m.start())
# cek apakah ada </body> di tengah
print('</body> di', b.find('</body>'))
print('</html> di', b.find('</html>'))
# struktur: apakah bagian setelah script kedua masih ada konten?
