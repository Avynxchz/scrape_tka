# -*- coding: utf-8 -*-
"""Bersihkan SEMUA angka karangan di card home_desktop.html:
- '60% (12/20 Selesai)' dst -> span diberi id agar bridge isi angka nyata
- '8 Paket' di Lihat Semua -> dihapus
- chart durasi mingguan karangan -> dibuang, ganti teks target statis jujur
- label Terjadwal/Populer -> Netral (biar nggak nipu)
Bridge di-update supaya mengisi id-id baru tersebut.
"""
import io, re

h = io.open('home_desktop.html', encoding='utf-8').read()

# 1. Semua label persen karangan: "<span class="text-primary font-bold">NN% (X/Y Selesai)</span>"
h = re.sub(
    r'<span class="text-primary font-bold">\d+% \(\d+/\d+ Selesai\)</span>',
    '<span class="text-primary font-bold" data-progress-pct>0% (0/0 Selesai)</span>',
    h,
)

# 2. 'Lihat Semua (8 Paket)' -> 'Lihat Semua'
h = re.sub(r'Lihat Semua \(\d+ Paket\)', 'Lihat Semua', h)

# 3. Chart durasi mingguan (karangan) -> kartu teks jujur sederhana
m = re.search(r'<!-- [^\n]*Rata-rata Durasi[\s\S]*?(?=<div class="flex items-center justify-between[^"]*">\s*<span class="material-symbols-outlined[^>]*>help|Pusat Bantuan)', h)
# fallback: ganti konten kartu Target Ritme: cari bagian bar chart
chart = re.search(r'(<div class="flex items-center justify-between[^"]*">\s*<span class="font-label-md[^"]*">Minggu Ini</span>[\s\S]{0,2200}?)(<div class="[^"]*">\s*<span class="material-symbols-outlined[^>]*>(?:help|support_agent|headset)</span>)', h)
if chart:
    pengganti = (
        '<div class="flex items-center justify-between mb-space-xs"><span class="font-label-md text-label-md text-text-muted">Per Paket</span></div>'
        '<div class="rounded-xl bg-surface-subtle p-space-sm text-body-sm text-secondary">'
        '±45 menit untuk 46 soal — disarankan 1 paket per hari.</div>'
    )
    h = h.replace(chart.group(1), pengganti)
else:
    # buang grafik bar mingguan dengan cara regex umum (div berisi Sen..Min)
    h = re.sub(r'<div class="flex items-end justify-between[\s\S]*?Target tercapai[\s\S]*?</div>\s*</div>',
               '<div class="rounded-xl bg-surface-subtle p-space-sm text-body-sm text-secondary mb-space-xs">±45 menit untuk 46 soal — disarankan 1 paket per hari.</div>', h, count=1)
    h = h.replace('Target tercapai 4 dari 7 hari', 'Konsisten itu penting!')
    h = h.replace('57%', '')

# 4. badge karangan
h = h.replace('>Terjadwal<', '>Tersedia<')
h = h.replace('>Populer<', '>Tersedia<')

# 5. deskripsi fisika karangan
h = h.replace('Mekanika Kuantum, Termodinamika &amp; Elektromagnetik', 'Mekanika, Termo &amp; Listrik — soal resmi Pusmendik')
h = h.replace('Mikro-Makro Ekonomi, Kebijakan Fiskal &amp; Dinamika Pasar', 'Mikro-Makro &amp; Pasar — soal resmi Pusmendik')

io.open('home_desktop.html', 'w', encoding='utf-8').write(h)
n_pct = h.count('data-progress-pct')
print('data-progress-pct slots:', n_pct, '(harusnya 3)')
print('sisa 12/20:', h.count('12/20'), '| 8 Paket:', h.count('8 Paket'), '| Sen:', h.count('>Sen<'))
