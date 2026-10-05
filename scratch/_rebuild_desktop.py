# -*- coding: utf-8 -*-
# Rebuild home_desktop.html dari scratch/_desk_head.html + _desk_body.html + _desk_bridge.js
# Semua replace pakai STRING EXACT (bukan regex rakus) — pelajaran dari file corrupt.
# Hasil lapor per-item: OK / MISS. Kalau ada MISS -> tulis FAIL, jangan output setengah jadi.
import io, sys

def read(p):
    return io.open(p, encoding='utf-8').read()

head = read('scratch/_desk_head.html')
body = read('scratch/_desk_body.html')
bridge = read('scratch/_desk_bridge.js')

fails = []

# ---------- 1. HEAD: buang inline style pembunuh scroll ----------
old_html = '<html lang="id" style="width: 1280px; height: 2086px; overflow: hidden; position: relative;">'
if old_html in head:
    head = head.replace(old_html, '<html lang="id">')
    print('OK   head: inline style html dibuang')
else:
    fails.append('head: inline style html tidak ditemukan')

# ---------- 2. BODY: replace exact ----------
REPL = [
    # kartu progres (kanan atas hero statistik)
    ('<span class="font-headline-xl text-headline-xl text-primary font-extrabold">92</span>',
     '<span id="deskSoalDikerjakan" class="font-headline-xl text-headline-xl text-primary font-extrabold">0</span>'),
    ('Skor Komposit', 'Soal Dikerjakan'),
    ('<span class="font-headline-sm text-headline-sm text-text-muted">/100</span>', ''),
    ('Kategori Tinggi', 'Soal Benar'),
    ('Persentil: 96.8%', 'Ketepatan: —'),
    ('Penalaran Matematika Lanjut', 'Jawaban Benar'),
    ('>95%</span>', '>—</span>'),
    ('Literasi Sains Terapan', 'Jawaban Salah'),
    ('>89%</span>', '>—</span>'),
    ('Target: STEI-R ITB', 'Dari 961 soal TKA'),
    # judul kartu progres
    ('Hasil Diagnostik Terakhir', 'Progres Belajarmu'),
    ('Terverifikasi AI', 'Diperbarui otomatis'),
    # NOTE: chip kuota header & sub chip user sudah dibetulkan langsung di
    # scratch/_desk_body.html (seragam dengan navbar halaman lain) — bukan di sini.
    # aside: plan & kuota -> mode tamu jujur
    ('Akun Pro (Masa Beta)', 'Mode Tamu (Beta)'),
    ('Aktif s/d Mei 2025', 'Gratis selama beta'),
    ('<span class="font-label-md text-label-md text-primary font-bold">84/100</span>',
     '<span class="font-label-md text-label-md text-primary font-bold">0/5</span>'),
    ('<div class="bg-primary h-full rounded-full" style="width: 84%"></div>',
     '<div class="bg-primary h-full rounded-full" style="width: 0%"></div>'),
    ('Tersisa 84 pertanyaan', '5 pertanyaan per hari'),
    # user fiktif (nama disamakan via _desk_body.html; sub chip user juga)
    ('Rian Pratama', 'Tamu'),
    # teks kartu mapel
    ('Lihat Semua (8 Paket)', 'Lihat Semua'),
    ('>Terjadwal<', '>Tersedia<'),
    ('>Populer<', '>Tersedia<'),
    ('Mekanika Kuantum, Termodinamika &amp; Elektromagnetik', 'Mekanika, Termo &amp; Listrik — soal resmi Pusmendik'),
    ('Mikro-Makro Ekonomi, Kebijakan Fiskal &amp; Dinamika Pasar', 'Mikro-Makro &amp; Pasar — soal resmi Pusmendik'),
    ('20 Soal HOTS', '20 Soal'),
    ('26 Soal HOTS', '26 Soal'),
    ('20 Soal Analitis', '20 Soal'),
    # persen progres kartu -> span kosong diisi bridge
    ('<span class="text-primary font-bold">60% (12/20 Selesai)</span>',
     '<span class="text-primary font-bold" data-progress-pct></span>'),
    ('<span class="text-primary font-bold">40% (8/20 Selesai)</span>',
     '<span class="text-primary font-bold" data-progress-pct></span>'),
    ('<span class="text-primary font-bold">30% (6/20 Selesai)</span>',
     '<span class="text-primary font-bold" data-progress-pct></span>'),
]
for old, new in REPL:
    n = body.count(old)
    if n == 1:
        body = body.replace(old, new)
        print('OK   body: %r' % old[:60])
    else:
        fails.append('body: %r ditemukan %dx (harus 1x)' % (old[:60], n))
        print('FAIL x%d %r' % (n, old[:60]))

# ---------- 3. Peluang Lolos 88%: hapus seluruh span (index, bukan regex) ----------
i88 = body.find('Peluang Lolos 88%')
if i88 < 0:
    fails.append('Peluang Lolos 88% tidak ditemukan')
else:
    start = body.rfind('<span', 0, i88)
    end1 = body.find('</span>', i88)                 # tutup inner span trending_up
    end2 = body.find('</span>', end1 + len('</span>'))  # tutup span luar
    chunk = body[start:end2 + len('</span>')]
    if start < 0 or end2 < 0 or 'Peluang Lolos' not in chunk or 'trending_up' not in chunk:
        fails.append('Potongan span Peluang Lolos tidak valid')
    else:
        body = body[:start] + body[end2 + len('</span>'):]
        print('OK   body: badge Peluang Lolos dihapus (%d char)' % len(chunk))

# ---------- 4. Widget Daily Study Tracker -> kartu jujur (potong index) ----------
t0 = body.find('<!-- Daily Study Tracker Widget')
t1 = body.find('<!-- Quick Help / Pusat Bantuan Card -->')
if t0 < 0 or t1 < 0 or t1 <= t0:
    fails.append('Batas widget tracker / kartu bantuan tidak ketemu (t0=%d t1=%d)' % (t0, t1))
else:
    cut = body[t0:t1]
    if cut.count('<div') != cut.count('</div>'):
        fails.append('Region tracker tidak seimbang div: %d vs %d' % (cut.count('<div'), cut.count('</div>')))
    else:
        honest = (
            '<!-- Kartu Estimasi (jujur, tanpa data karangan) -->\n'
            '<div class="bg-surface-card rounded-2xl p-space-md shadow-sm flex flex-col gap-space-sm">\n'
            '<div class="flex items-center gap-space-xs">\n'
            '<span class="material-symbols-outlined text-primary text-[20px]">schedule</span>\n'
            '<h3 class="font-headline-sm text-headline-sm text-on-surface">Estimasi Waktu Pengerjaan</h3>\n'
            '</div>\n'
            '<p class="font-body-sm text-body-sm text-text-muted leading-relaxed">'
            '&#177;45 menit untuk 46 soal &#8212; disarankan 1 paket per hari.</p>\n'
            '</div>\n'
        )
        body = body[:t0] + honest + body[t1:]
        print('OK   body: widget tracker diganti kartu jujur (buang %d char)' % len(cut))

# ---------- 5. Sanity sisa angka fiktif ----------
for sisa in ['92</span>', '96.8%', 'Peluang Lolos', 'Rian Pratama', '84/100', 'STEI-R',
             'Kategori Tinggi', 'Skor Komposit', 'Soal HOTS', 'Soal Analitis', 'Terjadwal', '>Populer<',
             'Hasil Diagnostik', 'Terverifikasi AI']:
    if sisa in body:
        fails.append('SISA ANGKA FIKTIF: %r masih ada' % sisa)

# ---------- 6. Rapikan penutup body ----------
b = body.rstrip()
if b.endswith('</html>'):
    b = b[:b.rfind('</html>')].rstrip()
if b.endswith('</body>'):
    b = b[:b.rfind('</body>')].rstrip()
body = b
print('OK   body tail:', body[-80:].replace('\n', ' '))

# ---------- 7. Susun final ----------
final = head + '\n' + body + '\n<script>\n' + bridge + '\n</script>\n</body>\n</html>\n'
if fails:
    print('\n=== GAGAL, file TIDAK ditulis ===')
    for f in fails:
        print(' -', f)
    sys.exit(1)

io.open('home_desktop.html', 'w', encoding='utf-8', newline='\n').write(final)
print('\n=== OK: home_desktop.html ditulis, %d bytes ===' % len(final.encode('utf-8')))
