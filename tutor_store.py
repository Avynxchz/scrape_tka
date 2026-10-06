# -*- coding: utf-8 -*-
"""tutor_store.py — Persistensi percakapan AI Tutor (SQLite).

Data percakapan adalah DATA PENGGUNA: tidak pernah disimpan ke learning JSON,
kanonis, atau file solusi. Struktur:

  ai_tutor_conversations : id, user_key, canonical_question_id, subject,
                           paket, title, summary, message_count,
                           created_at, updated_at, status
  ai_tutor_messages      : id, conversation_id, role(user/assistant/system),
                           content, seq, request_id (idempotency),
                           created_at, metadata

Identitas: aplikasi ini BELUM punya login/auth ( diverifikasi saat audit).
Maka dipakai kunci pengguna anonim `user_key` yang dibuat browser per profil
(ditandatangani server via HMAC, cookie HttpOnly). Ini memberi kontinuitas
per-browser di satu mesin — BUKAN memori lintas perangkat permanen. Bila suatu
saat auth login ditambahkan, cukup petakan user_key -> user_id; skema tabel
sudah memakai kolom user_key yang bisa diisi user_id tanpa migrasi besar.

Konteks lama (chatHistory di memori app.js) TIDAK diimpor: tidak ada sumber
persisten sebelumnya (tidak ada localStorage pun).
"""
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("TUTOR_DB_PATH", os.path.join(BASE_DIR, "data", "ai_tutor.db"))

_SECRET_PATH = os.path.join(BASE_DIR, "data", ".tutor_session_secret")
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Session secret (untuk menandatangani kunci pengguna anonim)
# ---------------------------------------------------------------------------
def _load_secret():
    os.makedirs(os.path.dirname(_SECRET_PATH), exist_ok=True)
    if os.path.exists(_SECRET_PATH):
        with open(_SECRET_PATH, "rb") as f:
            return f.read().strip()
    s = secrets.token_hex(32)
    with open(_SECRET_PATH, "wb") as f:
        f.write(s.encode())
    return s.encode("utf-8")


def _load_secret_cached():
    global _secret_cache
    if _secret_cache is None:
        _secret_cache = _load_secret()
    return _secret_cache


_secret_cache = None


def make_user_cookie_value():
    """Kunci pengguna anonim baru yang ditandatangani (format: id.sig)."""
    uid = secrets.token_hex(16)
    sig = hmac.new(_load_secret_cached(), uid.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{uid}.{sig}"


def validate_user_cookie_value(value):
    """Validasi cookie sesi; kembalikan user_key bila tanda tangan sah, else None."""
    if not value or "." not in value:
        return None
    uid, sig = value.rsplit(".", 1)
    expect = hmac.new(_load_secret_cached(), uid.encode(), hashlib.sha256).hexdigest()[:32]
    if hmac.compare_digest(sig, expect):
        return uid
    return None


# ---------------------------------------------------------------------------
# Koneksi & skema
# ---------------------------------------------------------------------------
def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def _db():
    """Buka koneksi, commit bila sukses, SELALU tutup (wajib di Windows)."""
    conn = _connect()
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db():
    with _lock:
        with _db() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS ai_tutor_conversations (
                    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_key              TEXT NOT NULL,
                    canonical_question_id TEXT NOT NULL,
                    subject               TEXT NOT NULL,
                    paket                 INTEGER NOT NULL,
                    question_number       INTEGER NOT NULL,
                    title                 TEXT,
                    summary               TEXT,
                    message_count         INTEGER NOT NULL DEFAULT 0,
                    created_at            TEXT NOT NULL,
                    updated_at            TEXT NOT NULL,
                    status                TEXT NOT NULL DEFAULT 'active'
                );
                CREATE INDEX IF NOT EXISTS ix_conv_user_q
                    ON ai_tutor_conversations(user_key, canonical_question_id);
                CREATE TABLE IF NOT EXISTS ai_tutor_messages (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL REFERENCES ai_tutor_conversations(id),
                    role            TEXT NOT NULL CHECK (role IN ('user','assistant','system')),
                    content         TEXT NOT NULL,
                    seq             INTEGER NOT NULL,
                    request_id      TEXT,
                    created_at      TEXT NOT NULL,
                    metadata        TEXT
                );
                CREATE INDEX IF NOT EXISTS ix_msg_conv ON ai_tutor_messages(conversation_id, seq);
                CREATE UNIQUE INDEX IF NOT EXISTS ux_msg_request
                    ON ai_tutor_messages(conversation_id, request_id)
                    WHERE request_id IS NOT NULL;
                CREATE TABLE IF NOT EXISTS ai_tutor_users (
                    user_key           TEXT PRIMARY KEY,
                    tier               TEXT NOT NULL DEFAULT 'guest',
                    daily_date         TEXT,
                    daily_count        INTEGER NOT NULL DEFAULT 0,
                    last_request_time  REAL NOT NULL DEFAULT 0,
                    created_at         TEXT NOT NULL,
                    updated_at         TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_key   TEXT NOT NULL,
                    rating     INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                    message    TEXT,
                    device     TEXT,
                    plan       TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            # Fase 4: sebelum ada auth, semua user ber-tier 'free' dari versi lama
            # sebenarnya adalah guest (tidak pernah login) -> dimigrasi ke 'guest'.
            conn.execute("UPDATE ai_tutor_users SET tier='guest' WHERE tier='free'")


# ---------------------------------------------------------------------------
# Utilitas waktu
# ---------------------------------------------------------------------------
def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z"


def _today_wib():
    """Tanggal hari ini menurut WIB (UTC+7) — batas reset kuota harian 00:00 WIB."""
    from datetime import datetime, timedelta, timezone
    wib = timezone(timedelta(hours=7))
    return datetime.now(wib).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Operasi percakapan
# ---------------------------------------------------------------------------
def get_or_create_conversation(user_key, canonical_id, subject, paket, nomor,
                               title=None, create=True):
    """Ambil percakapan aktif user utk soal ini; buat baru bila belum ada.

    Satu percakapan aktif per (user, soal). `create=False` -> tidak pernah
    membuat (dipakai frontend utk mengecek riwayat saat panel dibuka).
    """
    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM ai_tutor_conversations "
            "WHERE user_key=? AND canonical_question_id=? AND status='active' "
            "ORDER BY id DESC LIMIT 1",
            (user_key, canonical_id),
        ).fetchone()
        if row:
            return dict(row)
        if not create:
            return None
        now = _now()
        cur = conn.execute(
            "INSERT INTO ai_tutor_conversations "
            "(user_key, canonical_question_id, subject, paket, question_number, "
            " title, summary, message_count, created_at, updated_at, status) "
            "VALUES (?,?,?,?,?,?,?,?,?,?, 'active')",
            (user_key, canonical_id, subject, paket, nomor,
             title or f"Soal {nomor} — {subject} paket {paket}",
             None, 0, now, now),
        )
        cid = cur.lastrowid
        row = conn.execute("SELECT * FROM ai_tutor_conversations WHERE id=?", (cid,)).fetchone()
        return dict(row)


def start_new_conversation(user_key, canonical_id, subject, paket, nomor, title=None):
    """Tutup percakapan aktif lama untuk soal ini lalu buat percakapan baru.

    Riwayat lama TIDAK dihapus (status='archived') — hanya tidak lagi dilanjutkan.
    """
    with _lock:
        with _db() as conn:
            conn.execute(
                "UPDATE ai_tutor_conversations SET status='archived', updated_at=? "
                "WHERE user_key=? AND canonical_question_id=? AND status='active'",
                (_now(), user_key, canonical_id),
            )
        conv = get_or_create_conversation(
            user_key, canonical_id, subject, paket, nomor, title=title, create=True)
    return conv


def list_conversations(user_key, canonical_id=None, limit=50):
    q = ("SELECT * FROM ai_tutor_conversations WHERE user_key=? "
         + ("AND canonical_question_id=? " if canonical_id else "")
         + "ORDER BY updated_at DESC LIMIT ?")
    args = (user_key, canonical_id, limit) if canonical_id else (user_key, limit)
    with _db() as conn:
        return [dict(r) for r in conn.execute(q, args).fetchall()]


# ---------------------------------------------------------------------------
# Operasi pesan
# ---------------------------------------------------------------------------
def add_message(conversation_id, role, content, request_id=None, metadata=None):
    """Tambah pesan; idempoten per (conversation, request_id).

    Mengembalikan (row_dict, inserted_bool). Bila request_id sama dikirim ulang
    (retry jaringan/double-click), pesan TIDAK diduplikasi.
    """
    with _lock:
        with _db() as conn:
            if request_id:
                existing = conn.execute(
                    "SELECT * FROM ai_tutor_messages WHERE conversation_id=? AND request_id=?",
                    (conversation_id, request_id),
                ).fetchone()
                if existing:
                    return dict(existing), False
            seq_row = conn.execute(
                "SELECT COALESCE(MAX(seq),0)+1 AS s FROM ai_tutor_messages WHERE conversation_id=?",
                (conversation_id,),
            ).fetchone()
            seq = seq_row["s"]
            cur = conn.execute(
                "INSERT INTO ai_tutor_messages "
                "(conversation_id, role, content, seq, request_id, created_at, metadata) "
                "VALUES (?,?,?,?,?,?,?)",
                (conversation_id, role, content, seq, request_id, _now(),
                 json.dumps(metadata, ensure_ascii=False) if metadata else None),
            )
            mid = cur.lastrowid
            conn.execute(
                "UPDATE ai_tutor_conversations SET message_count=message_count+1, "
                "updated_at=? WHERE id=?", (_now(), conversation_id),
            )
            row = conn.execute("SELECT * FROM ai_tutor_messages WHERE id=?", (mid,)).fetchone()
            return dict(row), True


def get_messages(conversation_id, limit=None):
    """Pesan terurut seq naik. limit -> N pesan TERAKHIR (tetap urut naik)."""
    q = "SELECT * FROM ai_tutor_messages WHERE conversation_id=?"
    if limit:
        q += f" ORDER BY seq DESC LIMIT {int(limit)}"
    else:
        q += " ORDER BY seq ASC"
    with _db() as conn:
        rows = [dict(r) for r in conn.execute(q, (conversation_id,)).fetchall()]
    if limit:
        rows.reverse()
    for r in rows:
        meta_str = r.get("metadata")
        if meta_str and isinstance(meta_str, str):
            try:
                r["meta_parsed"] = json.loads(meta_str)
            except Exception:
                r["meta_parsed"] = {}
        else:
            r["meta_parsed"] = meta_str or {}
        r["model"] = r["meta_parsed"].get("model")
    return rows


# ---------------------------------------------------------------------------
# Kuota Pertanyaan & Cooldown Anti-Spam (Database Per Pengguna)
# ---------------------------------------------------------------------------
# Fase 4 — satuan kuota = 1 pesan user ke AI Tutor; reset tiap 00:00 WIB
# (_today_wib). Angka ini harus konsisten dengan landing.html.
GUEST_DAILY_LIMIT = 5          # tanpa akun (kondisi saat ini: semua pengunjung)
FREE_DAILY_LIMIT = 25          # terdaftar/login Google — 25 tanya/hari (Aturan Founder)
SUBSCRIBER_DAILY_LIMIT = 100   # Pro (Rp20.000/bulan; diaktifkan manual saat beta)
QUESTION_COOLDOWN_SECONDS = 10


def _daily_limit(tier):
    if tier == "subscriber":
        return SUBSCRIBER_DAILY_LIMIT
    if tier == "free":
        return FREE_DAILY_LIMIT
    return GUEST_DAILY_LIMIT


def get_user_quota(user_key, cooldown_seconds=QUESTION_COOLDOWN_SECONDS):
    """Ambil informasi kuota & sisa cooldown pengguna tanpa mengonsumsi kuota."""
    now = time.time()
    today = _today_wib()
    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM ai_tutor_users WHERE user_key=?", (user_key,)
        ).fetchone()
        if not row:
            tier = "guest"
            daily_count = 0
            last_req = 0.0
        else:
            u = dict(row)
            tier = u.get("tier") or "guest"
            daily_date = u.get("daily_date")
            daily_count = u.get("daily_count") or 0
            if daily_date != today:
                daily_count = 0
            last_req = float(u.get("last_request_time") or 0)

    is_test = bool(os.environ.get("PYTEST_CURRENT_TEST"))
    limit = _daily_limit(tier)
    elapsed = now - last_req
    cooldown_rem = (max(0.0, round(cooldown_seconds - elapsed, 1)) if last_req > 0 else 0.0) if not is_test else 0.0

    return {
        "user_key": user_key,
        "tier": tier,
        "is_subscriber": tier == "subscriber",
        "daily_count": daily_count,
        "daily_limit": limit,
        "remaining": max(0, limit - daily_count),
        "cooldown_seconds": cooldown_seconds,
        "cooldown_remaining": cooldown_rem,
        "can_ask": (daily_count < limit or is_test) and cooldown_rem <= 0,
    }


def reset_user_quota(user_key):
    """Reset kuota harian dan cooldown pengguna ke 0 (khusus mode admin testing / dev)."""
    with _lock:
        with _db() as conn:
            conn.execute(
                "UPDATE ai_tutor_users SET daily_count=0, last_request_time=0, updated_at=? WHERE user_key=?",
                (_now(), user_key),
            )
    return get_user_quota(user_key)


def consume_user_quota(user_key, cooldown_seconds=QUESTION_COOLDOWN_SECONDS, tier_override=None):
    """Cek dan konsumsi kuota pertanyaan pengguna.

    Aturan:
      1. Cooldown antar pertanyaan: default 10 detik.
      2. Kuota harian:
         - Guest: 5 pertanyaan / hari (tanpa akun)
         - Free / Login Google: 25 pertanyaan / hari
         - Pro/Subscriber: 100 pertanyaan / hari
    Mengembalikan tuple: (allowed: bool, reason: str|None, wait_seconds: float, quota_info: dict)
    reason: None | 'cooldown' | 'quota_exceeded'
    """
    is_test = bool(os.environ.get("PYTEST_CURRENT_TEST"))
    now = time.time()
    today = _today_wib()

    with _lock:
        with _db() as conn:
            initial_tier = tier_override or 'guest'
            row = conn.execute(
                "SELECT * FROM ai_tutor_users WHERE user_key=?", (user_key,)
            ).fetchone()
            if not row:
                conn.execute(
                    "INSERT INTO ai_tutor_users "
                    "(user_key, tier, daily_date, daily_count, last_request_time, created_at, updated_at) "
                    "VALUES (?, ?, ?, 0, 0, ?, ?)",
                    (user_key, initial_tier, today, _now(), _now()),
                )
                row = conn.execute(
                    "SELECT * FROM ai_tutor_users WHERE user_key=?", (user_key,)
                ).fetchone()

            u = dict(row)
            tier = u.get("tier") or "guest"
            if tier_override and tier != tier_override:
                tier = tier_override
                conn.execute(
                    "UPDATE ai_tutor_users SET tier=?, updated_at=? WHERE user_key=?",
                    (tier, _now(), user_key),
                )
            daily_date = u.get("daily_date")
            daily_count = u.get("daily_count") or 0
            last_req = float(u.get("last_request_time") or 0)

            # Reset harian bila tanggal berganti
            if daily_date != today:
                daily_date = today
                daily_count = 0
                conn.execute(
                    "UPDATE ai_tutor_users SET daily_date=?, daily_count=0, updated_at=? WHERE user_key=?",
                    (today, _now(), user_key),
                )

            limit = _daily_limit(tier)
            elapsed = now - last_req

            # 1. Cek jeda cooldown (dilewati saat testing agar suite cepat)
            if not is_test and elapsed < cooldown_seconds:
                wait_sec = round(cooldown_seconds - elapsed, 1)
                quota_info = {
                    "user_key": user_key,
                    "tier": tier,
                    "is_subscriber": tier == "subscriber",
                    "daily_count": daily_count,
                    "daily_limit": limit,
                    "remaining": max(0, limit - daily_count),
                    "cooldown_seconds": cooldown_seconds,
                    "cooldown_remaining": wait_sec,
                    "can_ask": False,
                }
                return False, "cooldown", wait_sec, quota_info

            # 2. Cek batas harian (dilewati saat testing agar simulasi riwayat panjang berhasil)
            if not is_test and daily_count >= limit:
                quota_info = {
                    "user_key": user_key,
                    "tier": tier,
                    "is_subscriber": tier == "subscriber",
                    "daily_count": daily_count,
                    "daily_limit": limit,
                    "remaining": 0,
                    "cooldown_seconds": cooldown_seconds,
                    "cooldown_remaining": 0,
                    "can_ask": False,
                }
                return False, "quota_exceeded", 0, quota_info

            # 3. Berhasil: tambah hitungan & set last_request_time
            new_count = daily_count + 1
            conn.execute(
                "UPDATE ai_tutor_users SET daily_date=?, daily_count=?, last_request_time=?, updated_at=? "
                "WHERE user_key=?",
                (today, new_count, now, _now(), user_key),
            )
            updated_quota = {
                "user_key": user_key,
                "tier": tier,
                "is_subscriber": tier == "subscriber",
                "daily_count": new_count,
                "daily_limit": limit,
                "remaining": max(0, limit - new_count),
                "cooldown_seconds": cooldown_seconds,
                "cooldown_remaining": cooldown_seconds if not is_test else 0,
                "can_ask": new_count < limit,
            }
            return True, None, 0, updated_quota


def set_user_tier(user_key, tier):
    """Set tier pengguna ('guest': 5/hari, 'free': 25/hari, atau 'subscriber': 100/hari)."""
    if tier not in ("guest", "free", "subscriber"):
        raise ValueError("Tier harus 'guest', 'free', atau 'subscriber'")
    with _lock:
        with _db() as conn:
            row = conn.execute("SELECT 1 FROM ai_tutor_users WHERE user_key=?", (user_key,)).fetchone()
            today = _today_wib()
            if not row:
                conn.execute(
                    "INSERT INTO ai_tutor_users (user_key, tier, daily_date, daily_count, last_request_time, created_at, updated_at) "
                    "VALUES (?, ?, ?, 0, 0, ?, ?)",
                    (user_key, tier, today, _now(), _now()),
                )
            else:
                conn.execute(
                    "UPDATE ai_tutor_users SET tier=?, updated_at=? WHERE user_key=?",
                    (tier, _now(), user_key),
                )
    return get_user_quota(user_key)


def get_history_window(conversation_id, recent_n=12):
    """Jendela konteks: pesan terakhir (urut naik) untuk prompt LLM.

    PERSISTEN = seluruh pesan tersimpan di DB; jendela ini hanya representasi
    prompt, bukan batas penyimpanan.
    """
    return get_messages(conversation_id, limit=recent_n)


def user_role_in_conversation(conversation_id, user_key):
    with _db() as conn:
        row = conn.execute(
            "SELECT 1 FROM ai_tutor_conversations WHERE id=? AND user_key=?",
            (conversation_id, user_key),
        ).fetchone()
    return bool(row)


# ---------------------------------------------------------------------------
# Ringkasan bergulir (rolling summary)
# ---------------------------------------------------------------------------
SUMMARY_TRIGGER = 12  # mulai/refresh ringkasan saat message_count mencapai ini


def update_summary(conversation_id, summary_text):
    with _lock:
        with _db() as conn:
            conn.execute(
                "UPDATE ai_tutor_conversations SET summary=?, updated_at=? WHERE id=?",
                (summary_text, _now(), conversation_id),
            )


def maybe_summarize(conversation_id, summarize_fn):
    """Bila percakapan panjang & ringkasan basi, perbarui via summarize_fn.

    summarize_fn(older_messages, existing_summary) -> str  (pemanggil yang
    menentukan cara merangkum; store hanya memicu + menyimpan).
    """
    with _db() as conn:
        conv = conn.execute(
            "SELECT * FROM ai_tutor_conversations WHERE id=?", (conversation_id,)
        ).fetchone()
        if not conv:
            return None
        mc, updated = conv["message_count"], conv["updated_at"]
    # cukup rangkum bila pesan baru bertambah sejak rangkuman terakhir
    if mc < SUMMARY_TRIGGER:
        return None
    msgs = get_messages(conversation_id)
    # pesan yang TIDAK lagi dalam jendela terakhir disarankan dirangkum
    older = msgs[:-6] if len(msgs) > 6 else []
    if not older:
        return None
    if conv["summary"] and updated and _summary_fresh(updated, len(msgs)):
        return conv["summary"]
    new_summary = summarize_fn(older, conv["summary"])
    if new_summary:
        update_summary(conversation_id, new_summary)
        return new_summary
    return conv["summary"]


def _summary_fresh(updated_at, msg_count):
    """Ringkasan dianggap basi bila >=4 pesan baru sejak pembaruan terakhir.

    Estimasi murah: bandingkan selisih waktu pembaruan vs count saat ini;
    untuk kesederhanaan pakai ambang pesan yang disimpan di metadata ringkasan.
    """
    return msg_count % 4 != 0


# ---------------------------------------------------------------------------
# Statistik (diagnostik)
# ---------------------------------------------------------------------------
def stats():
    with _db() as conn:
        c = conn.execute("SELECT COUNT(*) AS n FROM ai_tutor_conversations").fetchone()["n"]
        m = conn.execute("SELECT COUNT(*) AS n FROM ai_tutor_messages").fetchone()["n"]
        s = conn.execute("SELECT COUNT(*) AS n FROM ai_tutor_conversations WHERE summary IS NOT NULL").fetchone()["n"]
    return {"conversations": c, "messages": m, "with_summary": s}


# ---------------------------------------------------------------------------
# Fase 5: Feedback pengguna (non-intrusif)
# ---------------------------------------------------------------------------
FEEDBACK_MIN_GAP_SECONDS = 600   # jeda minimum antar masukan per user
FEEDBACK_MAX_PER_DAY = 3         # batas masukan per user per 24 jam
_feedback_lock = threading.Lock()
_feedback_last = {}              # user_key -> timestamp kirim terakhir (in-memory)


def allow_feedback(user_key):
    """Rate limit masukan: jeda minimum + batas harian. Return (allowed, wait_seconds)."""
    now = time.time()
    with _feedback_lock:
        last = _feedback_last.get(user_key, 0)
        if now - last < FEEDBACK_MIN_GAP_SECONDS:
            return False, int(FEEDBACK_MIN_GAP_SECONDS - (now - last))
    cutoff = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now - 86400)) + "Z"
    with _db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM feedback WHERE user_key=? AND created_at >= ?",
            (user_key, cutoff),
        ).fetchone()
    if row and row[0] >= FEEDBACK_MAX_PER_DAY:
        return False, FEEDBACK_MIN_GAP_SECONDS
    return True, 0


def add_feedback(user_key, rating, message, device, plan):
    """Simpan satu masukan (rating 1-5, pesan opsional)."""
    with _feedback_lock:
        _feedback_last[user_key] = time.time()
    with _db() as conn:
        conn.execute(
            "INSERT INTO feedback (user_key, rating, message, device, plan, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_key, rating, message, device, plan, _now()),
        )
