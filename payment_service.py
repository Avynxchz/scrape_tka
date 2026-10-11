"""
Modul Layanan Pembayaran Midtrans (payment_service.py)
Terintegrasi untuk produk Sprint Pass Rp14.900 (Sekali bayar aktif s/d tanggal TKA).

Fitur:
- Validasi status pembayaran aktif / paywall flag (PAYMENT_ENABLED)
- Pembuatan Midtrans Payment Link (Sandbox/Production) dengan idempotensi order pending
- Verifikasi tanda tangan digital (SHA512 Signature Key) pada Webhook Midtrans
- Sinkronisasi status order & tanggal kedaluwarsa pass (pass_expires_at) ke Supabase
"""

import base64
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request

WIB = timezone(timedelta(hours=7))


def is_payment_enabled():
    """Periksa apakah sistem pembayaran aktif (PAYMENT_ENABLED='1')."""
    return os.environ.get("PAYMENT_ENABLED", "0").strip() == "1"


def get_midtrans_config():
    """Ambil konfigurasi Midtrans dari environment variable."""
    server_key = os.environ.get("MIDTRANS_SERVER_KEY", "").strip().strip('"\'').strip()
    client_key = os.environ.get("MIDTRANS_CLIENT_KEY", "").strip().strip('"\'').strip()
    is_prod_raw = os.environ.get("MIDTRANS_IS_PRODUCTION", "0").strip().strip('"\'').strip().lower()
    is_prod = is_prod_raw in ("1", "true", "yes")
    base_url = "https://api.midtrans.com" if is_prod else "https://api.sandbox.midtrans.com"
    return {
        "server_key": server_key,
        "client_key": client_key,
        "is_prod": is_prod,
        "base_url": base_url,
    }


def verify_midtrans_signature(order_id, status_code, gross_amount, signature_key, server_key=None):
    """
    Verifikasi tanda tangan digital (signature key) notifikasi webhook Midtrans.
    Rumus: SHA512(order_id + status_code + gross_amount + ServerKey)
    """
    if not signature_key:
        return False
    key = server_key or os.environ.get("MIDTRANS_SERVER_KEY", "").strip().strip('"\'').strip()
    if not key:
        return False
    raw_str = f"{order_id}{status_code}{gross_amount}{key}"
    calculated_hash = hashlib.sha512(raw_str.encode("utf-8")).hexdigest().lower()
    return calculated_hash == str(signature_key).strip().lower()


def validate_tka_date(tka_date_str):
    """
    Validasi tanggal ujian TKA:
    1. Format YYYY-MM-DD
    2. Tidak di masa lalu (>= hari ini WIB)
    3. Maksimal 12 bulan ke depan (<= hari ini + 365 hari)
    """
    if not tka_date_str or not isinstance(tka_date_str, str):
        return False, "Tanggal TKA wajib diisi."

    clean_str = tka_date_str.strip()[:10]
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", clean_str):
        return False, "Format tanggal harus YYYY-MM-DD."

    try:
        tka_date = datetime.strptime(clean_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Format tanggal tidak valid."

    today_wib = datetime.now(WIB).date()
    if tka_date < today_wib:
        return False, "Tanggal TKA tidak boleh di masa lalu."

    max_date = today_wib + timedelta(days=365)
    if tka_date > max_date:
        return False, "Tanggal TKA maksimal 12 bulan ke depan."

    return True, clean_str


def generate_order_id(user_id):
    """
    Format order_id sesuai spesifikasi:
    SPRINT-<8 char user>-<YYYYMMDDHHMMSS>
    """
    clean_uid = re.sub(r"[^a-zA-Z0-9]", "", str(user_id))[:8]
    if len(clean_uid) < 8:
        clean_uid = clean_uid.ljust(8, "0")
    ts = datetime.now(WIB).strftime("%Y%m%d%H%M%S")
    return f"SPRINT-{clean_uid}-{ts}"


def get_supabase_headers(sb_svc=None):
    """Dapatkan header otentikasi REST Supabase dengan service key."""
    key = sb_svc or os.environ.get("SUPABASE_SERVICE_KEY", "") or os.environ.get("SUPABASE_ANON_KEY", "")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def find_active_pending_payment(user_id, sb_url=None, sb_svc=None):
    """
    Cari order 'pending' yang masih aktif (dibuat kurang dari 55 menit lalu)
    untuk idempotensi (mencegah link pembayaran ganda).
    """
    url = (sb_url or os.environ.get("SUPABASE_URL", "")).rstrip("/")
    if not url:
        return None

    try:
        endpoint = (
            f"{url}/rest/v1/payments"
            f"?user_id=eq.{urllib.parse.quote(str(user_id))}"
            f"&status=eq.pending"
            f"&order=created_at.desc&limit=1"
        )
        req = urllib.request.Request(endpoint, headers=get_supabase_headers(sb_svc))
        with urllib.request.urlopen(req, timeout=5) as resp:
            rows = json.loads(resp.read().decode("utf-8") or "[]")
            if not rows or not isinstance(rows, list):
                return None
            order = rows[0]
            # Validasi waktu kedaluwarsa link (Midtrans link default 60 menit)
            created_at_str = order.get("created_at")
            payment_url = order.get("payment_url")
            if created_at_str and payment_url:
                try:
                    # Parse timestamp ISO (mis. 2026-10-11T12:00:00+00:00)
                    dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    now_utc = datetime.now(timezone.utc)
                    age_seconds = (now_utc - dt).total_seconds()
                    # Bila belum lewat 55 menit, gunakan link yang sama
                    if 0 <= age_seconds < (55 * 60):
                        return order
                except Exception:
                    return order
            return None
    except Exception:
        return None


def create_midtrans_payment_link(order_id, user_id, user_email, user_name, tka_date, gross_amount=14900):
    """
    Panggil API Midtrans Create Payment Link (/v1/payment-links).
    Mengembalikan (ok: bool, payment_url: str|None, error_msg: str|None)
    """
    cfg = get_midtrans_config()
    server_key = cfg["server_key"]
    if not server_key:
        return False, None, "MIDTRANS_SERVER_KEY belum dikonfigurasi di server."

    # Validasi awal tipe dan lingkungan kredensial
    if "-client-" in server_key.lower():
        return False, None, "Kredensial keliru: MIDTRANS_SERVER_KEY yang dipasang adalah Client Key. Harap gunakan Server Key dari Midtrans Dashboard (Settings > Access Keys)."

    if not cfg["is_prod"] and not server_key.startswith("SB-"):
        return False, None, "Kredensial tidak cocok: Mode Sandbox aktif (MIDTRANS_IS_PRODUCTION=0), tetapi MIDTRANS_SERVER_KEY tidak diawali 'SB-'. Harap gunakan Server Key Sandbox (diawali 'SB-Mid-server-')."

    if cfg["is_prod"] and server_key.startswith("SB-"):
        return False, None, "Kredensial tidak cocok: Mode Production aktif (MIDTRANS_IS_PRODUCTION=1), tetapi MIDTRANS_SERVER_KEY menggunakan kunci Sandbox ('SB-...')."

    endpoint = f"{cfg['base_url']}/v1/payment-links"
    auth_bytes = f"{server_key}:".encode("utf-8")
    basic_auth = base64.b64encode(auth_bytes).decode("utf-8")

    clean_name = (user_name or "").strip() or "Siswa musse"
    clean_email = (user_email or "").strip() or "siswa@musse.id"

    payload = {
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": int(gross_amount),
        },
        "customer_details": {
            "first_name": clean_name,
            "email": clean_email,
        },
        "item_details": [
            {
                "id": "sprint-pass",
                "price": int(gross_amount),
                "quantity": 1,
                "name": "Sprint Pass TKA",
            }
        ],
        "expiry": {
            "duration": 60,
            "unit": "minutes",
        },
        "enabled_payments": ["qris", "gopay", "bank_transfer"],
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8") or "{}")
            payment_url = data.get("payment_url") or data.get("payment_link_url") or data.get("redirect_url")
            if payment_url:
                return True, payment_url, None
            return False, None, "Midtrans tidak mengembalikan payment_url."
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        if e.code == 401:
            return False, None, (
                f"HTTP 401 Midtrans: Kunci MIDTRANS_SERVER_KEY ditolak oleh Midtrans Sandbox. "
                f"Pastikan menyalin 'Server Key' (diawali SB-Mid-server-...) dari menu Settings > Access Keys di dashboard Midtrans Sandbox, "
                f"dan pastikan tidak ada tanda kutip di environment variable Railway."
            )
        return False, None, f"HTTP {e.code} Midtrans: {err_body}"
    except Exception as e:
        return False, None, f"Gagal menghubungi Midtrans: {str(e)}"


def save_payment_to_db(order_id, user_id, tka_date, amount, payment_url, sb_url=None, sb_svc=None):
    """Simpan riwayat pembayaran baru ke tabel payments di Supabase."""
    url = (sb_url or os.environ.get("SUPABASE_URL", "")).rstrip("/")
    if not url:
        return False, "SUPABASE_URL belum dikonfigurasi."

    endpoint = f"{url}/rest/v1/payments"
    payload = {
        "order_id": order_id,
        "user_id": str(user_id),
        "tka_date": str(tka_date),
        "amount": int(amount),
        "status": "pending",
        "payment_url": payment_url,
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=get_supabase_headers(sb_svc),
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5):
            pass
        return True, None
    except Exception as e:
        return False, str(e)


def handle_webhook_notification(payload, sb_url=None, sb_svc=None):
    """
    Proses payload notifikasi webhook dari Midtrans:
    1. Verifikasi tanda tangan digital (SHA512)
    2. Bila sukses (settlement/capture):
       - payments.status = 'paid'
       - users.pass_expires_at = tka_date pk 23:59:59 WIB (+07:00)
    3. Bila gagal/batal/kedaluwarsa (expire/cancel/deny/failure):
       - payments.status = transaction_status
    """
    order_id = payload.get("order_id", "")
    status_code = str(payload.get("status_code", ""))
    gross_amount = str(payload.get("gross_amount", ""))
    signature_key = payload.get("signature_key", "")
    transaction_status = payload.get("transaction_status", "")
    fraud_status = payload.get("fraud_status", "")

    # 1. Verifikasi signature
    if not verify_midtrans_signature(order_id, status_code, gross_amount, signature_key):
        return False, 403, "Invalid signature"

    url = (sb_url or os.environ.get("SUPABASE_URL", "")).rstrip("/")
    if not url:
        return True, 200, "Supabase tidak aktif, status dicatat secara lokal."

    headers = get_supabase_headers(sb_svc)

    # 2. Cari order pembayaran di DB
    order_row = None
    try:
        find_endpoint = f"{url}/rest/v1/payments?order_id=eq.{urllib.parse.quote(order_id)}&select=*&limit=1"
        req = urllib.request.Request(find_endpoint, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            rows = json.loads(resp.read().decode("utf-8") or "[]")
            if rows:
                order_row = rows[0]
    except Exception:
        pass

    now_iso = datetime.now(timezone.utc).isoformat()

    # 3. Evaluasi status transaksi
    is_settled = (transaction_status in ("settlement", "capture")) and (fraud_status != "deny")

    if is_settled:
        new_status = "paid"
        # Update payments
        try:
            p_patch = json.dumps({"status": "paid", "paid_at": now_iso}).encode("utf-8")
            req = urllib.request.Request(
                f"{url}/rest/v1/payments?order_id=eq.{urllib.parse.quote(order_id)}",
                data=p_patch,
                headers=headers,
                method="PATCH",
            )
            with urllib.request.urlopen(req, timeout=5):
                pass
        except Exception:
            pass

        # Update pass_expires_at di users jika order ditemukan
        if order_row and order_row.get("user_id"):
            u_id = order_row["user_id"]
            tka_date = order_row.get("tka_date") or ""
            # Format jam 23:59:59 WIB pada hari tanggal TKA
            if re.match(r"^\d{4}-\d{2}-\d{2}$", tka_date):
                pass_expires_at = f"{tka_date}T23:59:59+07:00"
            else:
                # Fallback: 30 hari ke depan bila tka_date kosong
                pass_expires_at = (datetime.now(WIB) + timedelta(days=30)).strftime("%Y-%m-%dT23:59:59+07:00")

            try:
                u_patch = json.dumps({
                    "pass_expires_at": pass_expires_at,
                    "tka_date": tka_date or None,
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{url}/rest/v1/users?id=eq.{urllib.parse.quote(str(u_id))}",
                    data=u_patch,
                    headers=headers,
                    method="PATCH",
                )
                with urllib.request.urlopen(req, timeout=5):
                    pass
            except Exception:
                pass
    else:
        # Status selain settlement (expire, cancel, deny, failure)
        new_status = transaction_status or "failed"
        try:
            p_patch = json.dumps({"status": new_status}).encode("utf-8")
            req = urllib.request.Request(
                f"{url}/rest/v1/payments?order_id=eq.{urllib.parse.quote(order_id)}",
                data=p_patch,
                headers=headers,
                method="PATCH",
            )
            with urllib.request.urlopen(req, timeout=5):
                pass
        except Exception:
            pass

    return True, 200, "OK"


def check_user_pass_status(user_id, sb_url=None, sb_svc=None):
    """
    Periksa apakah user memiliki Sprint Pass aktif (pass_expires_at > now).
    Mengembalikan dict {active: bool, pass_expires_at: str|None, tka_date: str|None}
    """
    url = (sb_url or os.environ.get("SUPABASE_URL", "")).rstrip("/")
    if not url or not user_id:
        return {"active": False, "pass_expires_at": None, "tka_date": None}

    headers = get_supabase_headers(sb_svc)
    try:
        endpoint = f"{url}/rest/v1/users?id=eq.{urllib.parse.quote(str(user_id))}&select=pass_expires_at,tka_date&limit=1"
        req = urllib.request.Request(endpoint, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            rows = json.loads(resp.read().decode("utf-8") or "[]")
            if not rows:
                return {"active": False, "pass_expires_at": None, "tka_date": None}
            u = rows[0]
            expires_str = u.get("pass_expires_at")
            tka_date = u.get("tka_date")
            if not expires_str:
                return {"active": False, "pass_expires_at": None, "tka_date": tka_date}

            # Parse tanggal kedaluwarsa dan bandingkan dengan waktu sekarang
            exp_dt = datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
            now_utc = datetime.now(timezone.utc)
            is_active = exp_dt > now_utc
            return {
                "active": is_active,
                "pass_expires_at": expires_str,
                "tka_date": tka_date,
            }
    except Exception:
        return {"active": False, "pass_expires_at": None, "tka_date": None}
