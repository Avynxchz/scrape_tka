# -*- coding: utf-8 -*-
"""Ganti isi Home overlay di index.html:
mobile (stitch inline) tetap; tambah iframe desktop untuk layar >=900px.
Backup blok lama dulu."""
import io

h = io.open('index.html', encoding='utf-8').read()
mulai = h.find('<div id="homeOverlay"')
akhir = h.find('<!-- Sticky Modern App Header -->')
assert mulai != -1 and akhir != -1, 'marker tidak ketemu'
blok_lama = h[mulai:akhir]
io.open('backup_audit_fix_20261003/index_home_overlay_backup.html', 'w', encoding='utf-8').write(blok_lama)

# sisipkan iframe desktop SEBELUM </div> penutup overlay
penutup = blok_lama.rstrip()
assert penutup.endswith('</div>'), 'penutup overlay tidak terdeteksi: ' + penutup[-30:]
iframe = ('    <!-- Desktop (>=900px): dashboard versi Stitch desktop via iframe -->\n'
          '    <iframe id="homeDesktopFrame" class="home-desktop-frame" src="/home_desktop.html" title="Beranda TKA Master (Desktop)"></iframe>\n')
blok_baru = penutup[:-len('</div>')] + iframe + '  </div>\n\n'
h_baru = h[:mulai] + blok_baru + h[akhir:]
io.open('index.html', 'w', encoding='utf-8').write(h_baru)
print('OK: iframe desktop disisipkan. Backup overlay lama tersimpan.')
