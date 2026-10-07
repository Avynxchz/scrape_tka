# ============================================================
# VISITOR LOG — pencatat pengunjung ringan (tanpa dependensi).
# Dipanggil otomatis dari server.py untuk tiap request GET/POST.
# - File log : data/visitors_<PORT>.jsonl (satu baris JSON per kunjungan)
# - ID perangkat: cookie `tka_did` (unik per browser, 12 hex).
#   Jauh lebih akurat dari hash(IP+UA) karena teman satu WiFi +
#   UA sama tidak lagi tertukar. Fallback ke hash(IP+UA) bila
#   cookie tidak didukung.
# - Identitas login: frontend memanggil /api/tutor/sync_user
#   dengan email+nama -> dicatat di data/device_users.json,
#   dashboard menampilkan nama user bukan cuma "Android · Chrome".
# - Dashboard : buka /pengunjung di server utama (butuh ?key=)
# ============================================================
import glob
import hashlib
import json
import os
import re
import threading
import time
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = os.environ.get("PORT", "8080")
ADMIN_KEY = os.environ.get("VISITOR_ADMIN_KEY")  # wajib diset; server.py fail-fast bila kosong
LOG_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(LOG_DIR, f"visitors_{PORT}.jsonl")
USERS_PATH = os.path.join(LOG_DIR, "device_users.json")
COOKIE_NAME = "tka_did"
ONLINE_WINDOW = 300  # detik; aktivitas < ini = "online"

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

_DID_RE = re.compile(r'^[0-9a-f]{12}$')


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


def _legacy_device_id(ip, ua):
    """Fallback lama bila browser tidak mengirim cookie."""
    return hashlib.sha1(f"{ip}|{ua}".encode('utf-8', 'ignore')).hexdigest()[:8]


def _new_did():
    return uuid.uuid4().hex[:12]


def _cookie_did(handler):
    """Baca cookie tka_did dari request; kembalikan None bila tidak valid."""
    try:
        raw = handler.headers.get('Cookie', '') or ''
    except Exception:
        return None
    for part in raw.split(';'):
        part = part.strip()
        if part.startswith(COOKIE_NAME + '='):
            val = part.split('=', 1)[1].strip().strip('"').lower()
            if _DID_RE.match(val):
                return val
            return None
    return None


def cookie_header_value(did):
    """Nilai header Set-Cookie untuk perangkat baru."""
    return (f"{COOKIE_NAME}={did}; Path=/; Max-Age=31536000; "
            f"SameSite=Lax; HttpOnly")


def record(handler):
    """Catat satu request.

    Mengembalikan (did, perlu_set_cookie). Aman dipanggil untuk semua
    request; aset statis dilewati (mengembalikan (None, False)).
    """
    try:
        path = (handler.path or '/').split('?', 1)[0] or '/'
        if path in _SKIP_PATHS:
            return None, False
        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return None, False
        if path.lower().endswith(_SKIP_EXT):
            return None, False
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
        did = _cookie_did(handler)
        need_cookie = False
        if not did:
            # Browser baru: buat ID unik, catat dengan ID itu, dan minta
            # browser menyimpannya via cookie agar request berikutnya
            # tetap memakai ID yang sama (tidak tergantung IP lagi).
            did = _new_did()
            need_cookie = True
        now = time.time()
        entry = {
            "t": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(now)),
            "ts": int(now),
            "ip": ip,
            "dev": _device(ua),
            "did": did,
            "method": getattr(handler, 'command', '?'),
            "path": path,
        }
        os.makedirs(LOG_DIR, exist_ok=True)
        with _LOCK:
            with open(LOG_PATH, 'a', encoding='utf-8') as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
        return did, need_cookie
    except Exception:
        pass  # logging tidak boleh bikin server gagal
    return None, False


def _load_users():
    try:
        with open(USERS_PATH, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def identify(did, email, name):
    """Tautkan perangkat ke identitas login (dipanggil saat sync_user)."""
    try:
        if not did or not _DID_RE.match(str(did)):
            return False
        email = (email or '').strip()[:120]
        name = (name or '').strip()[:80]
        if not email and not name:
            return False
        os.makedirs(LOG_DIR, exist_ok=True)
        with _LOCK:
            users = _load_users()
            users[str(did)] = {
                "email": email,
                "name": name or email.split('@')[0],
                "updated": time.strftime('%Y-%m-%dT%H:%M:%S'),
            }
            tmp = USERS_PATH + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                json.dump(users, fh, ensure_ascii=False)
            os.replace(tmp, USERS_PATH)
        return True
    except Exception:
        return False


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
    entries.sort(key=lambda e: e.get('ts', 0) or 0)
    return entries


def summary():
    """Agregasi untuk dashboard /api/admin/visitors."""
    entries = _load_all()
    users = _load_users()
    now = time.time()
    today = time.strftime('%Y-%m-%d')
    todays = [e for e in entries if str(e.get('t', '')).startswith(today)]

    devices = {}
    for e in todays:
        did = e.get('did', '?')
        d = devices.setdefault(did, {
            "did": did, "dev": e.get('dev', '?'), "ip": e.get('ip', '?'),
            "hits": 0, "first": e.get('t', ''), "last": e.get('t', ''),
            "last_ts": 0, "paths": {},
        })
        d['hits'] += 1
        d['last'] = e.get('t', d['last'])
        if e.get('ts'):
            d['last_ts'] = max(d['last_ts'], int(e['ts']))
        p = e.get('path', '?')
        d['paths'][p] = d['paths'].get(p, 0) + 1
    dev_list = []
    for d in devices.values():
        top = sorted(d.pop('paths').items(), key=lambda kv: -kv[1])[:5]
        d['top_paths'] = [f"{k} ({v}x)" for k, v in top]
        u = users.get(d['did']) or {}
        d['user_name'] = u.get('name') or ''
        d['user_email'] = u.get('email') or ''
        d['logged_in'] = bool(u)
        # online bila aktivitas < ONLINE_WINDOW detik dari "sekarang" server
        d['online'] = bool(d['last_ts'] and (now - d['last_ts']) < ONLINE_WINDOW)
        d['last_seen_sec'] = int(now - d['last_ts']) if d['last_ts'] else -1
        dev_list.append(d)
    dev_list.sort(key=lambda d: d['last_ts'], reverse=True)

    recent = []
    for e in reversed(entries[-60:]):
        u = users.get(e.get('did', '')) or {}
        recent.append({
            "t": e.get('t', ''), "ts": e.get('ts', 0),
            "dev": e.get('dev', '?'), "did": e.get('did', '?'),
            "method": e.get('method', '?'), "path": e.get('path', '?'),
            "user_name": u.get('name') or '',
            "logged_in": bool(u),
        })

    return {
        "now": int(now),
        "hari_ini": {"kunjungan": len(todays), "perangkat": len(dev_list)},
        "total_semua": {
            "kunjungan": len(entries),
            "perangkat": len({e.get('did', '?') for e in entries}),
        },
        "perangkat_hari_ini": dev_list,
        "aktivitas_terakhir": recent,
    }
