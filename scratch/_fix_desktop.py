# -*- coding: utf-8 -*-
"""Fix bug home_desktop.html:
1. <html style="width:1280px;height:2086px;overflow:hidden"> -> hapus inline style
   (menyebabkan tidak bisa scroll + layout terkunci di iframe).
2. header/nav fixed tidak scoped: biarkan (iframe standalone, aman).
3. Angka karangan: Skor 92/100, Percentil 96.8%, Peluang Lolos 88%,
   84/100 kuota, Rian Pratama, Rata-rata Durasi -> diganti data jujur/dihapus.
"""
import io, re

h = io.open('home_desktop.html', encoding='utf-8').read()

# 1. buka kunci html
h = h.replace(
    '<html lang="id" style="width: 1280px; height: 2086px; overflow: hidden; position: relative;">',
    '<html lang="id">'
)
h = h.replace('style="width: 1280px; height: 2086px; overflow: hidden; position: relative;"', '')

# pastikan body bisa discroll dalam iframe
if 'body {' not in h:
    pass
h = h.replace('</head>', '<style>html,body{width:100%;height:auto;overflow-x:hidden}body{min-height:100vh}</style></head>')

# 2. kartu diagnostik karangan -> kartu progres jujur (diganti via JS bridge juga, tapi teks statis dibersihkan)
h = h.replace('HASIL DIAGNOSTIK TERAKHIR', 'PROGRES BELAJARMU')
h = h.replace('Terverifikasi AI', 'Diperbarui otomatis')
h = h.replace('Skor Komposit', 'Soal Dikerjakan')
h = h.replace('92<span', '0<span')  # angka besar
h = h.replace('/100', '')
h = h.replace('Kategori Tinggi', 'Soal Benar')
h = h.replace('Persentil: 96.8%', 'Ketepatan: —')
h = h.replace('Penalaran Matematika Lanjut', 'Jawaban Benar')
h = h.replace('Literasi Sains Terapan', 'Jawaban Salah')
h = h.replace('95%', '—')
h = h.replace('89%', '—')
h = h.replace('Target: STEI-R ITB', 'Dari 961 soal TKA')
h = h.replace('Peluang Lolos 88%', 'Semangat belajar!')

# 3. profil karangan
h = h.replace('Rian Pratama', 'Tamu')
h = h.replace('Kelas 12 SMA •', 'Tanpa login ·')
h = h.replace('Saintek', 'Beta')

# 4. kuota karangan
h = h.replace('84/100 Kuota AI', 'Kuota AI Tamu')
h = h.replace('Tersisa 84 pertanyaan', '5 pertanyaan per hari')
h = h.replace('84/100', '5/hari')

# 5. durasi belajar karangan
h = h.replace('Rata-rata Durasi Belajar', 'Target Ritme Belajar')
h = h.replace('Minggu Ini', 'Per Paket')
# bar chart durasi: biarkan (ilustrasi netral) tapi ganti angka menit besar
h = h.replace('>50m<', '>45m<').replace('>40m<', '>45m<').replace('>45m<\n', '>45m<\n')

# 6. body angka di stat bar (22/44/960+/45) sudah benar - biarkan

io.open('home_desktop.html', 'w', encoding='utf-8').write(h)
print('home_desktop.html diperbaiki:', len(h), 'bytes')

# verifikasi tidak ada karangan tersisa
for pat in ['Skor 92', '96.8', 'Rian Pratama', '84/100', 'Peluang Lolos', 'STEI-R']:
    if pat in h:
        print('MASIH ADA:', pat)
