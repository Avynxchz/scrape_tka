# Verifikasi login Supabase di server (FASE 2 - T2.11).
#
# Latar: /api/tutor/sync_user selama ini percaya klaim `logged_in` dari klien,
# sehingga siapa saja bisa mengklaim tier 'free'. Modul ini memverifikasi
# JWT [token identitas] Supabase langsung di server memakai HMAC-SHA256
# (stdlib murni, tanpa library baru).
#
# Saklar env: AUTH_VERIFY (default "0" = MATI → perilaku lama, klien dipercaya).
#   Nyalakan ("1") hanya setelah SUPABASE_JWT_SECRET diisi di Railway.
#   Selama OFF, user tidak akan terkunci walau env belum diisi.
#
# Secret: SUPABASE_JWT_SECRET — ambil dari Supabase Dashboard → Project
#   Settings → API → "JWT Secret".

import base64
import hashlib
import hmac
import json
import os
import time


def _b64url_decode(data):
    """Decode base64url tanpa padding menjadi bytes."""
    if isinstance(data, str):
        data = data.encode("ascii")
    data += b"=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data)


def verify_token(token, secret):
    """Verifikasi JWT HS256. Kembalikan (ok: bool, claims: dict|None)."""
    try:
        if not token or not secret:
            return False, None
        parts = token.split(".")
        if len(parts) != 3:
            return False, None
        header_b64, payload_b64, sig_b64 = parts
        signing_input = (header_b64 + "." + payload_b64).encode("ascii")
        expected = hmac.new(secret.encode("utf-8"), signing_input,
                            hashlib.sha256).digest()
        actual = _b64url_decode(sig_b64)
        if not hmac.compare_digest(expected, actual):
            return False, None
        claims = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        # Kadaluarsa: tolak bila lewat (toleransi 60 detik).
        exp = claims.get("exp")
        if exp is not None and float(exp) < time.time() - 60:
            return False, None
        return True, claims
    except Exception:
        return False, None


def verify_request(headers):
    """Ambil Bearer token dari header dan verifikasi.

    Kembalikan (ok, claims). ok=False bila: tidak ada header, secret belum
    diisi, signature salah, atau token kadaluarsa.
    """
    try:
        auth = headers.get("Authorization", "") or ""
    except Exception:
        auth = ""
    if not auth.startswith("Bearer "):
        return False, None
    token = auth[len("Bearer "):].strip()
    secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    return verify_token(token, secret)


def auth_verify_enabled():
    """Saklar fitur. Default OFF."""
    return os.environ.get("AUTH_VERIFY", "0") == "1"
