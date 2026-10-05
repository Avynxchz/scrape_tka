# -*- coding: utf-8 -*-
# Inspeksi scratch/_desk_body.html: verifikasi string replace exact + batas widget tracker
import io, sys

BODY = io.open('scratch/_desk_body.html', encoding='utf-8').read()
print('body len:', len(BODY))

CHECKS = [
    # (label, string exact yang harus ada di body)
    ('92 angka headline', '<span class="font-headline-xl text-headline-xl text-primary font-extrabold">92</span>'),
    ('Skor Komposit', 'Skor Komposit'),
    ('/100', '/100'),
    ('Kategori Tinggi', 'Kategori Tinggi'),
    ('Persentil 96.8', 'Persentil: 96.8%'),
    ('Penalaran Matematika Lanjut', 'Penalaran Matematika Lanjut'),
    ('95%', '95%'),
    ('Literasi Sains Terapan', 'Literasi Sains Terapan'),
    ('89%', '89%'),
    ('Target STEI', 'Target: STEI-R ITB'),
    ('Peluang Lolos 88%', 'Peluang Lolos 88%'),
    ('Hasil Diagnostik', 'Hasil Diagnostik Terakhir'),
    ('Terverifikasi AI', 'Terverifikasi AI'),
    ('Akun Pro (Masa Beta)', 'Akun Pro (Masa Beta)'),
    ('Aktif s/d Mei 2025', 'Aktif s/d Mei 2025'),
    ('84/100 Kuota', '84/100 Kuota AI Hari Ini'),
    ('Tersisa 84', 'Tersisa 84 pertanyaan'),
    ('Rian Pratama', 'Rian Pratama'),
    ('Kelas 12 SMA', 'Kelas 12 SMA'),
    ('tracker comment', '<!-- Daily Study Tracker Widget'),
    ('Pusat Bantuan TKA', 'Pusat Bantuan TKA'),
    ('60% (12/20', '60%'),
    ('(12/20 Selesai)', '(12/20 Selesai)'),
    ('(8/20 Selesai)', '(8/20 Selesai)'),
    ('(6/20 Selesai)', '(6/20 Selesai)'),
    ('Lihat Semua (8 Paket)', 'Lihat Semua (8 Paket)'),
    ('Terjadwal', '>Terjadwal<'),
    ('Populer', '>Populer<'),
    ('Mekanika Kuantum', 'Mekanika Kuantum, Termodinamika &amp; Elektromagnetik'),
    ('Mikro-Makro', 'Mikro-Makro Ekonomi, Kebijakan Fiskal &amp; Dinamika Pasar'),
    ('20 Soal HOTS', '20 Soal HOTS'),
    ('26 Soal HOTS', '26 Soal HOTS'),
    ('20 Soal Analitis', '20 Soal Analitis'),
]
for label, s in CHECKS:
    n = BODY.count(s)
    print(('OK  ' if n > 0 else 'MISS') + ' x%d  %s' % (n, label))

i = BODY.find('<!-- Daily Study Tracker Widget')
j = BODY.find('Pusat Bantuan TKA')
print('idx tracker comment:', i, ' idx pusat bantuan:', j)
if i >= 0:
    print('--- sebelum tracker (500 char):')
    print(BODY[max(0, i-500):i])
if j >= 0:
    print('--- sekitar Pusat Bantuan (600 char):')
    print(BODY[j-400:j+200])
