# ============================================================
# VISITOR LOG — pencatat pengunjung ringan (tanpa dependensi).
# Dipanggil otomatis dari server.py untuk tiap request GET/POST.
# - File log : data/visitors_<PORT>.jsonl (satu baris JSON per kunjungan)
# - Perangkat dideteksi dari User-Agent (HP/laptop + browser)
# - ID perangkat = hash(IP + User-Agent) -> stabil selama sesi
# - Dashboard : buka /pengunjung di server utama (butuh ?key=)
# Catatan: pengunjung lewat tunnel (cloudflared/ngrok) akan tercatat
# dengan IP 127.0.0.1 karena trafik datang dari tunnel lokal —
# perangkat tetap bisa dibedakan lewat User-Agent.
# ============================================================
import glob
import hashlib
import json
import os
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = os.environ.get("PORT", "8080")
ADMIN_KEY = os.environ.get("VISITOR_ADMIN_KEY")  # wajib diset; server.py fail-fast bila kosong
LOG_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(LOG_DIR, f"visitors_{PORT}.jsonl")

_LOCK = threading.Lock()

# Aset statis & polling yang tidak perlu dicatat (biar log bersih)
_SKIP_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico',
             '.css', '.js', '.woff', '.woff2', '.ttf', '.map', '.json',
             '.txt', '.xml', '.webmanifest')
_SKIP_PATHS = (
    '/api/tutor/state',        # polling kuota tutor, terlalu sering
    '/api/swarm/status',       # polling dashboard app
    '/api/swarm/subjects',     # polling dashboard app
)
_SKIP_PREFIXES = (
    '/api/admin/',             # dashboard pemantauan: JANGAN catat diri sendiri
    '/pengunjung',
)


def _device(ua):
    """Ringkasan perangkat dari User-Agent, mis. 'Android · Chrome'."""
    ua = ua or ''
    if not ua:
        return 'Tidak diketahui'
    if 'Windows' in ua:
        os_ = 'Windows'
    elif 'Android' in ua:
        os_ = 'Android'
    elif 'iPhone' in ua or 'iPad' in ua:
        os_ = 'iPhone/iPad'
    elif 'Macintosh' in ua or 'Mac OS' in ua:
        os_ = 'Mac'
    elif 'Linux' in ua:
        os_ = 'Linux'
    else:
        os_ = 'Lainnya'
    if 'Edg/' in ua:
        br = 'Edge'
    elif 'OPR/' in ua or 'Opera' in ua:
        br = 'Opera'
    elif 'Firefox' in ua:
        br = 'Firefox'
    elif 'Chrome' in ua:
        br = 'Chrome'
    elif 'Safari' in ua:
        br = 'Safari'
    else:
        br = 'Lainnya'
    return f"{os_} · {br}"


def _device_id(ip, ua):
    return hashlib.sha1(f"{ip}|{ua}".encode('utf-8', 'ignore')).hexdigest()[:8]


def record(handler):
    """Catat satu request. Aman dipanggil untuk semua request; aset statis dilewati."""
    try:
        path = (handler.path or '/').split('?', 1)[0] or '/'
        if path in _SKIP_PATHS:
            return
        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return
        if path.lower().endswith(_SKIP_EXT):
            return
        ip = '127.0.0.1'
        try:
            if handler.client_address:
                ip = handler.client_address[0]
        except Exception:
            pass
        ua = ''
        try:
            ua = handler.headers.get('User-Agent', '') or ''
        except Exception:
            pass
        entry = {
            "t": time.strftime('%Y-%m-%dT%H:%M:%S'),
            "ip": ip,
            "dev": _device(ua),
            "did": _device_id(ip, ua),
            "method": getattr(handler, 'command', '?'),
            "path": path,
        }
        os.makedirs(LOG_DIR, exist_ok=True)
        with _LOCK:
            with open(LOG_PATH, 'a', encoding='utf-8') as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass  # logging tidak boleh bikin server gagal


def _load_all():
    entries = []
    for fp in glob.glob(os.path.join(LOG_DIR, 'visitors_*.jsonl')):
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            continue
    entries.sort(key=lambda e: e.get('t', ''))
    return entries


def summary():
    """Agregasi untuk dashboard /api/admin/visitors."""
    entries = _load_all()
    today = time.strftime('%Y-%m-%d')
    todays = [e for e in entries if str(e.get('t', '')).startswith(today)]

    devices = {}
    for e in todays:
        did = e.get('did', '?')
        d = devices.setdefault(did, {
            "did": did, "dev": e.get('dev', '?'), "ip": e.get('ip', '?'),
            "hits": 0, "first": e.get('t', ''), "last": e.get('t', ''),
            "paths": {},
        })
        d['hits'] += 1
        d['last'] = e.get('t', d['last'])
        p = e.get('path', '?')
        d['paths'][p] = d['paths'].get(p, 0) + 1
    dev_list = []
    for d in devices.values():
        top = sorted(d.pop('paths').items(), key=lambda kv: -kv[1])[:5]
        d['top_paths'] = [f"{k} ({v}x)" for k, v in top]
        dev_list.append(d)
    dev_list.sort(key=lambda d: d['last'], reverse=True)

    return {
        "hari_ini": {"kunjungan": len(todays), "perangkat": len(dev_list)},
        "total_semua": {
            "kunjungan": len(entries),
            "perangkat": len({e.get('did', '?') for e in entries}),
        },
        "perangkat_hari_ini": dev_list,
        "aktivitas_terakhir": list(reversed(entries[-60:])),
    }
