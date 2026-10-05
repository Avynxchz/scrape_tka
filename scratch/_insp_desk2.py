# -*- coding: utf-8 -*-
# Inspeksi konteks persis untuk replace yang ambigu
import io

BODY = io.open('scratch/_desk_body.html', encoding='utf-8').read()

def ctx(needle, before=120, after=160, n=1):
    out = []
    start = 0
    for _ in range(n):
        i = BODY.find(needle, start)
        if i < 0:
            break
        out.append('--- idx %d ---' % i)
        out.append(BODY[max(0, i-before):i+len(needle)+after])
        start = i + 1
    return '\n'.join(out)

print('== 92 headline span (sekitar) ==')
print(ctx('>92</span>', 260, 320))
print()
print('== /100 semua kemunculan ==')
print(ctx('/100', 150, 80, 3))
print()
print('== Persentil ==')
print(ctx('Persentil: 96.8%', 150, 100))
print()
print('== Peluang Lolos ==')
print(ctx('Peluang Lolos 88%', 250, 150))
print()
print('== 95% ==')
print(ctx('95%', 130, 60))
print()
print('== Kelas 12 ==')
print(ctx('Kelas 12 SMA', 80, 80))
print()
print('== (12/20 Selesai) ==')
print(ctx('(12/20 Selesai)', 220, 120))
print()
print('== (8/20 Selesai) ==')
print(ctx('(8/20 Selesai)', 180, 80))
print()
print('== (6/20 Selesai) ==')
print(ctx('(6/20 Selesai)', 180, 80))
print()
print('== Menit di kartu ==')
print(ctx('Menit', 120, 60, 8))
print()
print('== gradient card start sebelum Pusat Bantuan ==')
j = BODY.find('Pusat Bantuan TKA')
k = BODY.rfind('bg-gradient-to-br from-surface-card to-surface-subtle', 0, j)
print('idx gradient:', k)
print(BODY[k-30:k+120])
print()
print('== awal widget tracker (400 char) ==')
i = BODY.find('<!-- Daily Study Tracker Widget')
print(BODY[i:i+500])
print()
print('== akhir widget tracker: 600 char sebelum gradient card ==')
print(BODY[k-700:k])
