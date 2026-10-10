# -*- coding: utf-8 -*-
"""tests/test_quota.py — Unit test untuk Pelacakan Kuota dan Anggaran Guru AI (FASE A5).

Menguji:
1. Konfigurasi Environment & Limit Default
2. Perhitungan Kuota Database Supabase (hari ini, per user, dan global)
3. Logika check_quota (disabled, user limit, global limit, guest)
4. Fallback instan ke template saat kuota habis tanpa error mentah ke user
5. Endpoint GET /api/autopsy/quota dan proteksi tamu
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autopsy import quota
from autopsy import coach_template
import server


class TestQuotaModule(unittest.TestCase):
    """Pengujian fungsi unit di autopsy/quota.py."""

    def setUp(self):
        # Reset env
        os.environ.pop("COACH_ENABLED", None)
        os.environ.pop("COACH_DAILY_PER_USER", None)
        os.environ.pop("COACH_DAILY_GLOBAL", None)

    def test_default_limits(self):
        limits = quota.get_quota_limits()
        self.assertTrue(limits["enabled"])
        self.assertEqual(limits["daily_per_user"], 3)
        self.assertEqual(limits["daily_global"], 150)

    def test_custom_env_limits(self):
        os.environ["COACH_ENABLED"] = "0"
        os.environ["COACH_DAILY_PER_USER"] = "5"
        os.environ["COACH_DAILY_GLOBAL"] = "200"

        limits = quota.get_quota_limits()
        self.assertFalse(limits["enabled"])
        self.assertEqual(limits["daily_per_user"], 5)
        self.assertEqual(limits["daily_global"], 200)

    def test_check_quota_when_disabled(self):
        os.environ["COACH_ENABLED"] = "0"
        allowed, reason, usage = quota.check_quota("user-123", "http://sb.fake", "key-fake")
        self.assertFalse(allowed)
        self.assertEqual(reason, "coach_disabled")

    def test_check_quota_guest(self):
        allowed, reason, usage = quota.check_quota(None, "http://sb.fake", "key-fake")
        self.assertFalse(allowed)
        self.assertEqual(reason, "guest_user")

    @patch("autopsy.quota.count_today_coach_attempts")
    def test_check_quota_allowed(self, mock_count):
        # User 1 kali, Global 10 kali
        mock_count.side_effect = lambda sb_url, sb_svc, user_id=None: 1 if user_id else 10
        allowed, reason, usage = quota.check_quota("user-123", "http://sb.fake", "key-fake")
        self.assertTrue(allowed)
        self.assertEqual(reason, "")
        self.assertEqual(usage["user_used"], 1)
        self.assertEqual(usage["global_used"], 10)

    @patch("autopsy.quota.count_today_coach_attempts")
    def test_check_quota_user_exhausted(self, mock_count):
        # User sudah 3 kali (batas 3)
        mock_count.side_effect = lambda sb_url, sb_svc, user_id=None: 3 if user_id else 25
        allowed, reason, usage = quota.check_quota("user-123", "http://sb.fake", "key-fake")
        self.assertFalse(allowed)
        self.assertEqual(reason, "kuota_harian_user_habis")
        self.assertEqual(usage["user_used"], 3)

    @patch("autopsy.quota.count_today_coach_attempts")
    def test_check_quota_global_exhausted(self, mock_count):
        # User 1 kali, Global sudah 150 kali (batas 150)
        mock_count.side_effect = lambda sb_url, sb_svc, user_id=None: 1 if user_id else 150
        allowed, reason, usage = quota.check_quota("user-123", "http://sb.fake", "key-fake")
        self.assertFalse(allowed)
        self.assertEqual(reason, "kuota_harian_global_habis")
        self.assertEqual(usage["global_used"], 150)

    @patch("urllib.request.urlopen")
    def test_count_today_coach_attempts_parses_content_range(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Range": "0-2/42"}
        mock_resp.read.return_value = b"[]"
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        count = quota.count_today_coach_attempts("http://sb.fake", "key-fake", user_id="u1")
        self.assertEqual(count, 42)

    @patch("urllib.request.urlopen")
    def test_count_today_coach_attempts_graceful_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Network down")
        count = quota.count_today_coach_attempts("http://sb.fake", "key-fake", user_id="u1")
        # Tidak melempar exception, kembalikan 0
        self.assertEqual(count, 0)


class TestServerCoachQuotaEndpoints(unittest.TestCase):
    """Pengujian integrasi endpoint server saat kuota habis dan proteksi tamu."""

    def setUp(self):
        server._COACH_CACHE.clear()
        server._COACH_RATE_LIMIT.clear()

    @patch("autopsy.quota.check_quota")
    @patch("server._verify_supabase_token")
    def test_post_coach_falls_back_to_template_when_quota_exhausted(self, mock_verify, mock_check_quota):
        # Setup user login
        mock_verify.return_value = (True, {"id": "user-agus-01"})
        # Kuota user habis
        mock_check_quota.return_value = (False, "kuota_harian_user_habis", {"user_used": 3, "user_limit": 3})

        handler = server.AppRequestHandler.__new__(server.AppRequestHandler)
        handler.headers = {
            "Authorization": "Bearer valid_token",
            "Content-Length": "0",
        }
        handler.path = "/api/autopsy/coach"

        attempt_dummy = {
            "n_questions": 25,
            "duration_limit_s": 4500,
            "ended_by": "user",
            "items": [{"soal_id": "1", "position": 1, "is_correct": False, "waktu_detik": 20}],
        }

        # Simulasikan post payload
        import io
        payload_bytes = json.dumps({"attempt": attempt_dummy}).encode("utf-8")
        handler.headers["Content-Length"] = str(len(payload_bytes))
        handler.rfile = io.BytesIO(payload_bytes)

        with patch.object(handler, "_send_json") as mock_send:
            with patch.object(handler, "_is_valid_admin", return_value=False):
                handler._handle_post_autopsy_coach()

                mock_send.assert_called_once()
                status = mock_send.call_args[0][0]
                body = mock_send.call_args[0][1]

                # HTTP 200, BUKAN ERROR 429/500 (Aturan Bagian 7 A5)
                self.assertEqual(status, 200)
                self.assertEqual(body["status"], "success")
                self.assertEqual(body["coach"]["sumber"], "template")
                self.assertEqual(body["meta"]["sumber"], "template")
                self.assertEqual(body["meta"]["alasan"], "kuota_harian_user_habis")
                self.assertEqual(body["meta"]["kuota"]["user_used"], 3)

    def test_post_coach_guest_returns_invitation(self):
        handler = server.AppRequestHandler.__new__(server.AppRequestHandler)
        handler.headers = {"Content-Length": "0"}  # Tanpa header Authorization
        handler.path = "/api/autopsy/coach"

        with patch.object(handler, "_send_json") as mock_send:
            handler._handle_post_autopsy_coach()
            mock_send.assert_called_once()
            status = mock_send.call_args[0][0]
            body = mock_send.call_args[0][1]

            self.assertEqual(status, 401)
            self.assertTrue(body.get("is_guest"))
            self.assertIn("Login Google", body.get("message"))

    def test_get_quota_guest(self):
        handler = server.AppRequestHandler.__new__(server.AppRequestHandler)
        handler.headers = {}
        handler.path = "/api/autopsy/quota"

        with patch.object(handler, "_send_json") as mock_send:
            handler._handle_get_autopsy_quota()
            mock_send.assert_called_once()
            status = mock_send.call_args[0][0]
            body = mock_send.call_args[0][1]

            self.assertEqual(status, 200)
            self.assertEqual(body["status"], "guest")
            self.assertTrue(body["is_guest"])
            self.assertEqual(body["limits"]["daily_per_user"], 3)

    @patch("autopsy.quota.check_quota")
    @patch("server._verify_supabase_token")
    def test_get_quota_logged_in_user(self, mock_verify, mock_check_quota):
        mock_verify.return_value = (True, {"id": "user-agus-01"})
        mock_check_quota.return_value = (True, "", {"user_used": 1, "global_used": 10})

        handler = server.AppRequestHandler.__new__(server.AppRequestHandler)
        handler.headers = {"Authorization": "Bearer valid_token"}
        handler.path = "/api/autopsy/quota"

        with patch.object(handler, "_send_json") as mock_send:
            handler._handle_get_autopsy_quota()
            mock_send.assert_called_once()
            status = mock_send.call_args[0][0]
            body = mock_send.call_args[0][1]

            self.assertEqual(status, 200)
            self.assertEqual(body["status"], "success")
            self.assertTrue(body["allowed"])
            self.assertEqual(body["usage"]["user_used"], 1)


if __name__ == "__main__":
    unittest.main()
