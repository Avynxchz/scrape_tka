# -*- coding: utf-8 -*-
"""autopsy/quota.py — Pelacakan kuota dan anggaran Guru Autopsi (FASE A5).

Aturan A5:
- Env:
  COACH_ENABLED: "1" (default)
  COACH_DAILY_PER_USER: 3 (default)
  COACH_DAILY_GLOBAL: 150 (default)
- Hitung kuota dari JUMLAH BARIS DI DATABASE Supabase (bukan counter SQLite),
  karena counter file/SQLite hilang saat server redeploy.
- Baris dihitung dari tabel attempts di mana coach_result IS NOT NULL dan dibuat hari ini.
- Tamu tidak mendapat Guru AI (mendapat analisis berbasis aturan + ajakan login Google).
- Jika kuota atau anggaran habis atau COACH_ENABLED=0 -> fallback ke template deterministik tanpa pesan error mentah.
"""

import datetime
import json
import logging
import os
import urllib.parse
import urllib.request

logger = logging.getLogger("autopsy.quota")


def is_coach_enabled():
    """Periksa apakah fitur Guru AI aktif via environment variable."""
    val = os.environ.get("COACH_ENABLED", "1").strip().lower()
    return val in ("1", "true", "yes", "on")


def get_quota_limits():
    """Ambil konfigurasi limit harian per user dan global."""
    try:
        user_limit = int(os.environ.get("COACH_DAILY_PER_USER", 3))
    except Exception:
        user_limit = 3

    try:
        global_limit = int(os.environ.get("COACH_DAILY_GLOBAL", 150))
    except Exception:
        global_limit = 150

    return {
        "enabled": is_coach_enabled(),
        "daily_per_user": max(1, user_limit),
        "daily_global": max(1, global_limit),
    }


def get_today_iso_utc():
    """Kembalikan awal hari UTC hari ini dalam format ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    today_start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=datetime.timezone.utc)
    return today_start.strftime("%Y-%m-%dT%H:%M:%SZ")


def count_today_coach_attempts(sb_url, sb_svc, user_id=None, timeout=6):
    """Hitung baris di Supabase attempts yang memiliki coach_result pada hari ini.

    Jika user_id diberikan, hitung untuk user tersebut.
    Jika user_id None, hitung global.
    """
    if not sb_url or not sb_svc:
        return 0

    today_iso = get_today_iso_utc()
    endpoint = sb_url.rstrip("/") + "/rest/v1/attempts?coach_result=not.is.null"
    # Cek created_at atau started_at
    endpoint += f"&created_at=gte.{urllib.parse.quote(today_iso)}"
    if user_id:
        endpoint += f"&user_id=eq.{urllib.parse.quote(str(user_id))}"
    endpoint += "&select=id"

    req = urllib.request.Request(
        endpoint,
        headers={
            "apikey": sb_svc,
            "Authorization": f"Bearer {sb_svc}",
            "Prefer": "count=exact",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_range = resp.headers.get("Content-Range")
            if content_range and "/" in content_range:
                try:
                    total_count = int(content_range.split("/")[1])
                    return total_count
                except Exception:
                    pass
            body = resp.read().decode("utf-8")
            rows = json.loads(body or "[]")
            return len(rows) if isinstance(rows, list) else 0
    except urllib.error.HTTPError as e:
        # Jika kolom created_at tidak ada atau nama kolom berbeda, coba started_at
        if e.code in (400, 404):
            try:
                alt_endpoint = sb_url.rstrip("/") + f"/rest/v1/attempts?coach_result=not.is.null&started_at=gte.{urllib.parse.quote(today_iso)}"
                if user_id:
                    alt_endpoint += f"&user_id=eq.{urllib.parse.quote(str(user_id))}"
                alt_endpoint += "&select=id"
                req_alt = urllib.request.Request(
                    alt_endpoint,
                    headers={"apikey": sb_svc, "Authorization": f"Bearer {sb_svc}"},
                )
                with urllib.request.urlopen(req_alt, timeout=timeout) as resp_alt:
                    rows_alt = json.loads(resp_alt.read().decode("utf-8") or "[]")
                    return len(rows_alt) if isinstance(rows_alt, list) else 0
            except Exception:
                pass
        logger.warning(f"Gagal menghitung kuota attempts dari Supabase: HTTP {e.code}")
        return 0
    except Exception as ex:
        logger.warning(f"Gagal menghubungi Supabase untuk cek kuota: {ex}")
        return 0


def check_quota(user_id, sb_url, sb_svc):
    """Periksa apakah permintaan Guru AI diizinkan berdasarkan kuota.

    Mengembalikan (allowed: bool, reason: str, usage: dict).
    Jika allowed == False: alasan berisi 'disabled' / 'user_limit_exceeded' / 'global_limit_exceeded'.
    """
    limits = get_quota_limits()

    # 1. Cek feature flag env
    if not limits["enabled"]:
        return False, "coach_disabled", {"enabled": False}

    # 2. Cek apakah user_id valid (tamu tidak dapat memanggil AI)
    if not user_id:
        return False, "guest_user", {"user_id": None}

    # 3. Hitung dari database Supabase
    user_count = count_today_coach_attempts(sb_url, sb_svc, user_id=user_id)
    if user_count >= limits["daily_per_user"]:
        return False, "kuota_harian_user_habis", {
            "user_used": user_count,
            "user_limit": limits["daily_per_user"],
            "global_limit": limits["daily_global"],
        }

    global_count = count_today_coach_attempts(sb_url, sb_svc, user_id=None)
    if global_count >= limits["daily_global"]:
        return False, "kuota_harian_global_habis", {
            "user_used": user_count,
            "global_used": global_count,
            "user_limit": limits["daily_per_user"],
            "global_limit": limits["daily_global"],
        }

    return True, "", {
        "user_used": user_count,
        "global_used": global_count,
        "user_limit": limits["daily_per_user"],
        "global_limit": limits["daily_global"],
    }
