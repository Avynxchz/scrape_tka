# -*- coding: utf-8 -*-
"""Patch app.js (CRLF-safe):
1. Tambah homeProgressSummary() - ringkasan progres nyata dari localStorage.
2. Kirim progress di postMessage ke iframe desktop."""
import io

h = io.open('app.js', encoding='utf-8', newline='').read()
CRLF = '\r\n'

marker1 = '// Kirim data nyata ke iframe desktop (home_desktop.html)'
assert marker1 in h, 'marker1 tidak ketemu'
summary_fn = (
    '// Ringkasan progres nyata dari localStorage tka_progress' + CRLF +
    'function homeProgressSummary() {' + CRLF +
    '  try {' + CRLF +
    "    const raw = localStorage.getItem('tka_progress');" + CRLF +
    '    const store = raw ? JSON.parse(raw) : {};' + CRLF +
    '    let dikerjakan = 0, benar = 0;' + CRLF +
    '    Object.values(store || {}).forEach(pkgs => {' + CRLF +
    '      Object.values(pkgs || {}).forEach(soal => {' + CRLF +
    '        Object.values(soal || {}).forEach(ans => {' + CRLF +
    '          dikerjakan++;' + CRLF +
    '          if (ans && ans.benar) benar++;' + CRLF +
    '        });' + CRLF +
    '      });' + CRLF +
    '    });' + CRLF +
    "    return { dikerjakan, benar, tepat: dikerjakan ? Math.round((benar / dikerjakan) * 100) : 0 };" + CRLF +
    '  } catch (e) { return { dikerjakan: 0, benar: 0, tepat: 0 }; }' + CRLF +
    '}' + CRLF + CRLF
)
h = h.replace(marker1, summary_fn + marker1, 1)

old_send = "try { frame.contentWindow.postMessage({ type: 'home-desktop-data', subjects }, '*'); } catch (e) {}"
new_send = "try { frame.contentWindow.postMessage({ type: 'home-desktop-data', subjects, progress: homeProgressSummary() }, '*'); } catch (e) {}"
assert old_send in h, 'marker send tidak ketemu'
h = h.replace(old_send, new_send, 1)

io.open('app.js', 'w', encoding='utf-8', newline='').write(h)
print('app.js patched OK')
