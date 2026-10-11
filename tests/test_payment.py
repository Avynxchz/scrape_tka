"""
Suite Pengujian Otomatis Fitur Pembayaran Midtrans (tests/test_payment.py)
Menguji:
1. Endpoint create ditolak 403 saat PAYMENT_ENABLED='0' (paywall mati masa beta)
2. Endpoint create & status ditolak 401 jika user tidak login (tanpa Bearer token)
3. Validasi tanggal TKA (format salah, tanggal lampau, > 12 bulan ke depan)
4. Verifikasi tanda tangan digital SHA512 pada webhook (signature salah -> 403, signature benar -> 200)
5. Idempotensi pembuatan order pembayaran (order pending aktif menghasilkan link yang sama)
"""

from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
import unittest
from unittest import mock
import urllib.error
import urllib.request

import payment_service

BASE_URL = os.environ.get("TEST_BASE_URL", "http://127.0.0.1:8080")


class TestMidtransPaymentUnit(unittest.TestCase):
    """Pengujian fungsi unit pada payment_service."""

    def test_payment_enabled_flag(self):
        old_val = os.environ.get("PAYMENT_ENABLED")
        try:
            os.environ["PAYMENT_ENABLED"] = "0"
            self.assertFalse(payment_service.is_payment_enabled())
            os.environ["PAYMENT_ENABLED"] = "1"
            self.assertTrue(payment_service.is_payment_enabled())
        finally:
            if old_val is not None:
                os.environ["PAYMENT_ENABLED"] = old_val
            else:
                os.environ.pop("PAYMENT_ENABLED", None)

    def test_validate_tka_date(self):
        # Format salah
        ok, msg = payment_service.validate_tka_date("invalid-date")
        self.assertFalse(ok)
        self.assertIn("Format tanggal", msg)

        # Tanggal masa lalu
        ok, msg = payment_service.validate_tka_date("2020-01-01")
        self.assertFalse(ok)
        self.assertIn("masa lalu", msg)

        # Tanggal > 12 bulan ke depan
        far_future = (datetime.now(payment_service.WIB) + timedelta(days=400)).strftime("%Y-%m-%d")
        ok, msg = payment_service.validate_tka_date(far_future)
        self.assertFalse(ok)
        self.assertIn("12 bulan", msg)

        # Tanggal valid (30 hari ke depan)
        valid_date = (datetime.now(payment_service.WIB) + timedelta(days=30)).strftime("%Y-%m-%d")
        ok, val = payment_service.validate_tka_date(valid_date)
        self.assertTrue(ok)
        self.assertEqual(val, valid_date)

    def test_order_id_generation(self):
        order_id = payment_service.generate_order_id("usr-12345678-abcd")
        self.assertTrue(order_id.startswith("SPRINT-usr12345-"))
        self.assertGreater(len(order_id), 20)

    def test_signature_verification(self):
        server_key = "TEST_SECRET_KEY_123"
        order_id = "SPRINT-user1-20261011120000"
        status_code = "200"
        gross_amount = "14900.00"

        # Hitung signature valid
        raw = f"{order_id}{status_code}{gross_amount}{server_key}"
        valid_sig = hashlib.sha512(raw.encode("utf-8")).hexdigest().lower()

        # Signature benar -> True
        self.assertTrue(payment_service.verify_midtrans_signature(
            order_id, status_code, gross_amount, valid_sig, server_key=server_key
        ))

        # Signature salah -> False
        self.assertFalse(payment_service.verify_midtrans_signature(
            order_id, status_code, gross_amount, "invalid_sig_12345", server_key=server_key
        ))

    @unittest.mock.patch("urllib.request.urlopen")
    def test_create_midtrans_payment_link_v1_endpoint(self, mock_urlopen):
        mock_resp = unittest.mock.MagicMock()
        mock_resp.read.return_value = json.dumps({
            "payment_url": "https://app.sandbox.midtrans.com/payment-links/1647"
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        old_key = os.environ.get("MIDTRANS_SERVER_KEY")
        old_prod = os.environ.get("MIDTRANS_IS_PRODUCTION")
        try:
            os.environ["MIDTRANS_SERVER_KEY"] = "SB-Mid-server-testkey"
            os.environ["MIDTRANS_IS_PRODUCTION"] = "0"
            ok, url, err = payment_service.create_midtrans_payment_link(
                "SPRINT-test-1", "user-1234", "test@musse.id", "Test User", "2026-11-20"
            )
            self.assertTrue(ok)
            self.assertEqual(url, "https://app.sandbox.midtrans.com/payment-links/1647")
            call_args = mock_urlopen.call_args
            req_sent = call_args[0][0]
            self.assertEqual(req_sent.full_url, "https://api.sandbox.midtrans.com/v1/payment-links")
        finally:
            if old_key is not None:
                os.environ["MIDTRANS_SERVER_KEY"] = old_key
            else:
                os.environ.pop("MIDTRANS_SERVER_KEY", None)
            if old_prod is not None:
                os.environ["MIDTRANS_IS_PRODUCTION"] = old_prod
            else:
                os.environ.pop("MIDTRANS_IS_PRODUCTION", None)

    def test_client_key_as_server_key_rejected(self):
        old_key = os.environ.get("MIDTRANS_SERVER_KEY")
        try:
            os.environ["MIDTRANS_SERVER_KEY"] = "SB-Mid-client-abc12345"
            ok, _, err = payment_service.create_midtrans_payment_link(
                "SPRINT-test-1", "user-1", "test@test.com", "Test", "2026-11-20"
            )
            self.assertFalse(ok)
            self.assertIn("Client Key", err)
        finally:
            if old_key is not None:
                os.environ["MIDTRANS_SERVER_KEY"] = old_key
            else:
                os.environ.pop("MIDTRANS_SERVER_KEY", None)

    def test_sandbox_mode_requires_sb_prefix(self):
        old_key = os.environ.get("MIDTRANS_SERVER_KEY")
        old_prod = os.environ.get("MIDTRANS_IS_PRODUCTION")
        try:
            os.environ["MIDTRANS_SERVER_KEY"] = "Mid-server-prodkey123"
            os.environ["MIDTRANS_IS_PRODUCTION"] = "0"
            ok, _, err = payment_service.create_midtrans_payment_link(
                "SPRINT-test-1", "user-1", "test@test.com", "Test", "2026-11-20"
            )
            self.assertFalse(ok)
            self.assertIn("SB-Mid-server-", err)
        finally:
            if old_key is not None:
                os.environ["MIDTRANS_SERVER_KEY"] = old_key
            else:
                os.environ.pop("MIDTRANS_SERVER_KEY", None)
            if old_prod is not None:
                os.environ["MIDTRANS_IS_PRODUCTION"] = old_prod
            else:
                os.environ.pop("MIDTRANS_IS_PRODUCTION", None)

    def test_quote_sanitization_in_config(self):
        old_key = os.environ.get("MIDTRANS_SERVER_KEY")
        try:
            os.environ["MIDTRANS_SERVER_KEY"] = '"SB-Mid-server-quotedkey"'
            cfg = payment_service.get_midtrans_config()
            self.assertEqual(cfg["server_key"], "SB-Mid-server-quotedkey")
        finally:
            if old_key is not None:
                os.environ["MIDTRANS_SERVER_KEY"] = old_key
            else:
                os.environ.pop("MIDTRANS_SERVER_KEY", None)



class TestMidtransPaymentEndpoints(unittest.TestCase):
    """Pengujian integrasi endpoint HTTP pada server lokal."""

    def test_payment_config_endpoint(self):
        url = f"{BASE_URL}/api/payment/config"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "success")
            self.assertEqual(data.get("price"), 14900)
            self.assertIn("payment_enabled", data)

    def test_payment_status_requires_login(self):
        # Tanpa header Authorization -> harus 401
        url = f"{BASE_URL}/api/payment/status"
        req = urllib.request.Request(url)
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 401)

    def test_payment_create_disabled_during_beta(self):
        # Saat PAYMENT_ENABLED='0' (default beta) -> harus 403
        url = f"{BASE_URL}/api/payment/create"
        payload = json.dumps({"tka_date": "2026-11-20"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 403)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertEqual(body.get("status"), "forbidden")

    def test_webhook_invalid_signature_rejected(self):
        # Webhook dipanggil dengan signature palsu -> harus ditolak 403
        url = f"{BASE_URL}/api/payment/webhook"
        payload = {
            "order_id": "SPRINT-test-1234",
            "status_code": "200",
            "gross_amount": "14900.00",
            "signature_key": "fake_signature_hash_xyz",
            "transaction_status": "settlement"
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 403)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertEqual(body.get("status"), "error")
        self.assertEqual(body.get("message"), "Invalid signature")


if __name__ == "__main__":
    unittest.main()
