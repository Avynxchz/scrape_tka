# Feature flags TKA Master (FASE 0 - T0.7).
#
# Mekanisme: tabel `feature_flags` di database SQLite yang sama dengan aplikasi
# (dibuat idempoten [dibuat bila belum ada] saat server start, lalu di-seed
# dengan 7 flag default OFF). Flag bisa diubah TANPA deploy ulang lewat
# POST /api/admin/flags (butuh kunci admin VISITOR_ADMIN_KEY).
#
# KONSEKUENSI PENTING (lihat T0.9): database SQLite di Railway saat ini
# ephemeral [sementara, hilang tiap deploy ulang] karena tidak ada Volume
# di railway.json. Jadi perubahan flag via admin HILANG setiap redeploy
# sampai database dipindah ke penyimpanan persisten (Supabase, Fase 3).
# Setelah pindah, tabel ini ikut pindah dan flag menjadi persisten.
#
# Klien membaca flag lewat GET /api/flags (satu endpoint, nilai sudah
# dihitung di server). rollout_pct dievaluasi per user di fase berikutnya;
# untuk Fase 0 yang dipakai hanya `enabled`.

import os
import sqlite3
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("TUTOR_DB_PATH", os.path.join(BASE_DIR, "data", "ai_tutor.db"))

# 7 flag awal, semua OFF (brief Bagian 4.7 / T0.7).
DEFAULT_FLAGS = {
    "autopsy_logging": True,    # Fase 3: rekam perilaku per soal
    "autopsy_preview": True,    # Fase 5: layar Autopsi (preview gratis)
    "autopsy_full": True,       # Fase 5/6: Autopsi penuh (pemegang pass)
    "paywall": False,           # Fase 6: alur beli Paket Sprint
    "ai_narrative": True,       # Fase 7: narasi AI untuk Autopsi
    "referral": False,          # Fase 6: kode referral/afiliasi
    "wa_notify": False,         # Fase 6: notifikasi WA otomatis (opsional)
}

FLAGS_VERSION = "flags_v1"

_lock = threading.RLock()


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_flags():
    """Buat tabel + seed default. Idempoten: aman dipanggil tiap start."""
    with _lock:
        conn = _db()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feature_flags (
                    name         TEXT PRIMARY KEY,
                    enabled      INTEGER NOT NULL DEFAULT 0,
                    rollout_pct  INTEGER NOT NULL DEFAULT 100,
                    updated_at   TEXT NOT NULL
                )
                """
            )
            now = time.strftime("%Y-%m-%dT%H:%M:%S")
            for name, enabled in DEFAULT_FLAGS.items():
                conn.execute(
                    "INSERT INTO feature_flags (name, enabled, rollout_pct, updated_at)"
                    " VALUES (?, ?, 100, ?)"
                    " ON CONFLICT(name) DO UPDATE SET enabled = ?, updated_at = ?",
                    (name, 1 if enabled else 0, now, 1 if enabled else 0, now),
                )
            conn.commit()
        finally:
            conn.close()


def get_all_flags():
    """Kembalikan {nama: {enabled: bool, rollout_pct: int}} untuk semua flag."""
    with _lock:
        conn = _db()
        try:
            rows = conn.execute(
                "SELECT name, enabled, rollout_pct FROM feature_flags"
            ).fetchall()
        finally:
            conn.close()
    out = {}
    for r in rows:
        out[r["name"]] = {
            "enabled": bool(r["enabled"]),
            "rollout_pct": int(r["rollout_pct"]),
        }
    # Flag default yang belum ada di tabel (mis. DB lama) tetap dilaporkan OFF.
    for name, default in DEFAULT_FLAGS.items():
        out.setdefault(name, {"enabled": bool(default), "rollout_pct": 100})
    return out


def is_enabled(name):
    """Cek satu flag (default OFF bila tidak dikenal)."""
    return bool(get_all_flags().get(name, {}).get("enabled", False))


def set_flag(name, enabled, rollout_pct=None):
    """Ubah flag. Kembalikan True bila nama dikenal, False bila tidak."""
    if name not in DEFAULT_FLAGS:
        return False
    if rollout_pct is None:
        rollout_pct = get_all_flags()[name]["rollout_pct"]
    rollout_pct = max(0, min(100, int(rollout_pct)))
    with _lock:
        conn = _db()
        try:
            conn.execute(
                "UPDATE feature_flags SET enabled = ?, rollout_pct = ?,"
                " updated_at = ? WHERE name = ?",
                (1 if enabled else 0, rollout_pct,
                 time.strftime("%Y-%m-%dT%H:%M:%S"), name),
            )
            conn.commit()
        finally:
            conn.close()
    return True
