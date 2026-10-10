# -*- coding: utf-8 -*-
"""tests/test_ai_room.py — Unit test untuk Layanan AI Room per Mapel (FASE D2 + D3).

Menguji:
1. Perhitungan agregat performa se-mapel (calculate_mapel_aggregates):
   - Total soal, akurasi, akurasi per topik, waktu rata-rata.
   - Topik terlemah (maks 3).
   - Deteksi pola pengerjaan (soal lama, terburu-buru, ragu).
   - Memastikan raw items tidak bocor ke output klien.
2. Pengambilan 5 butir soal terakhir yang salah (get_last_wrong_questions).
3. Perakitan system prompt kontekstual se-mapel (build_ai_room_system_prompt).
4. Pemanggilan chat AI Room via LLM / fallback cerdas.
5. Handler endpoint server.py:
   - GET /api/ai-room/<mapel>/context
   - POST /api/ai-room/<mapel>/chat
   - GET /ruang/<mapel> (menyajikan ruang.html)
"""

import io
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_room
import server


class TestAIRoomAggregates(unittest.TestCase):
    """Pengujian fungsi agregasi data per mapel (D2)."""

    def test_empty_attempts(self):
        """Agregat dari 0 attempt menghasilkan nilai aman & pola awal."""
        aggr = ai_room.calculate_mapel_aggregates([], "matematika")
        self.assertEqual(aggr["mapel"], "matematika")
        self.assertEqual(aggr["total_soal"], 0)
        self.assertEqual(aggr["total_benar"], 0)
        self.assertEqual(aggr["akurasi"], 0.0)
        self.assertEqual(aggr["waktu_rata2_per_soal"], 0.0)
        self.assertEqual(aggr["topik_terlemah"], [])
        self.assertIn("Belum ada riwayat", aggr["pola"])
        self.assertNotIn("items", aggr, "Raw items tidak boleh ada di agregat!")

    def test_aggregate_calculation_and_weak_topics(self):
        """Menghitung akurasi, waktu rata-rata, dan 3 topik terlemah dengan benar."""
        # Buat dummy attempt:
        # Topik Aljabar: 2 soal, 0 benar -> 0%
        # Topik Geometri: 2 soal, 1 benar -> 50%
        # Topik Statistika: 2 soal, 2 benar -> 100%
        # Topik Trigonometri: 1 soal, 0 benar -> 0%
        items = [
            {"position": 1, "topic_id": "Aljabar", "final_answer": "A", "is_correct": False, "waktu_detik": 70},
            {"position": 2, "topic_id": "Aljabar", "final_answer": "B", "is_correct": False, "waktu_detik": 80},
            {"position": 3, "topic_id": "Geometri", "final_answer": "C", "is_correct": True, "waktu_detik": 40},
            {"position": 4, "topic_id": "Geometri", "final_answer": "D", "is_correct": False, "waktu_detik": 65},
            {"position": 5, "topic_id": "Statistika", "final_answer": "A", "is_correct": True, "waktu_detik": 30},
            {"position": 6, "topic_id": "Statistika", "final_answer": "B", "is_correct": True, "waktu_detik": 35},
            {"position": 7, "topic_id": "Trigonometri", "final_answer": "C", "is_correct": False, "waktu_detik": 90},
        ]
        attempts = [{
            "id": "att-1",
            "mapel": "matematika",
            "paket": 1,
            "items": items
        }]

        aggr = ai_room.calculate_mapel_aggregates(attempts, "matematika")
        self.assertEqual(aggr["total_soal"], 7)
        self.assertEqual(aggr["total_benar"], 3)
        self.assertEqual(aggr["akurasi"], round(3 / 7 * 100, 1))  # 42.9%
        # Total waktu = 70+80+40+65+30+35+90 = 410 -> 410/7 = 58.6s
        self.assertEqual(aggr["waktu_rata2_per_soal"], round(410 / 7, 1))

        # Topik terlemah harus memuat Aljabar dan Trigonometri (akurasi 0%)
        self.assertEqual(len(aggr["topik_terlemah"]), 3)
        self.assertIn("Aljabar", aggr["topik_terlemah"])
        self.assertIn("Trigonometri", aggr["topik_terlemah"])
        self.assertIn("Geometri", aggr["topik_terlemah"])

        # Deteksi pola: 4 dari 4 kesalahan (Aljabar 70s, 80s, Geometri 65s, Trig 90s) > 60 detik
        self.assertIn(">60 detik", aggr["pola"])

        # Keamanan privasi:
        self.assertNotIn("items", aggr)

    def test_last_wrong_questions_extraction(self):
        """Memverifikasi pengambilan maksimal 5 butir soal terakhir yang salah."""
        items = [
            {"position": i, "topic_id": f"Topik-{i}", "final_answer": "A", "is_correct": (i % 2 == 0), "waktu_detik": 45}
            for i in range(1, 15)
        ]
        # Soal ganjil (1, 3, 5, 7, 9, 11, 13) adalah salah -> total 7 soal salah
        attempts = [{"mapel": "matematika", "paket": 1, "items": items}]
        last_wrong = ai_room.get_last_wrong_questions(attempts, "matematika", limit=5)

        self.assertEqual(len(last_wrong), 5)
        self.assertEqual(last_wrong[0]["nomor"], 1)
        self.assertEqual(last_wrong[0]["user_answer"], "A")
        self.assertIn("snippet", last_wrong[0])

    def test_system_prompt_builder(self):
        """System prompt AI Room memuat ringkasan performa dan daftar soal salah."""
        aggr = {
            "display_name": "Matematika",
            "total_soal": 20,
            "total_attempt": 2,
            "akurasi": 60.0,
            "waktu_rata2_per_soal": 45.2,
            "topik_terlemah": ["Aljabar", "Kalkulus"],
            "topik_terkuat": ["Statistika"],
            "pola": "Sering salah di soal >60 detik."
        }
        last_wrong = [
            {"paket": 1, "nomor": 5, "topik": "Aljabar", "user_answer": "B", "kunci": "C", "waktu_detik": 72, "snippet": "Tentukan nilai x"}
        ]
        prompt = ai_room.build_ai_room_system_prompt(aggr, last_wrong)

        self.assertIn("RUANG MATEMATIKA", prompt)
        self.assertIn("Total soal dikerjakan: 20", prompt)
        self.assertIn("Akurasi keseluruhan: 60.0%", prompt)
        self.assertIn("Aljabar, Kalkulus", prompt)
        self.assertIn("Paket 1 Soal #5", prompt)
        self.assertIn("Tentukan nilai x", prompt)


class TestAIRoomEndpoints(unittest.TestCase):
    """Pengujian endpoint server.py untuk AI Room."""

    def setUp(self):
        self.handler = server.AppRequestHandler.__new__(server.AppRequestHandler)
        self.handler.headers = {}
        self.handler.wfile = io.BytesIO()

    def _get_json_response(self):
        val = self.handler.wfile.getvalue().decode("utf-8")
        if "\r\n\r\n" in val:
            body = val.split("\r\n\r\n", 1)[1]
        elif "\n\n" in val:
            body = val.split("\n\n", 1)[1]
        else:
            body = val
        return json.loads(body)

    def test_get_ai_room_context_guest(self):
        """GET /api/ai-room/matematika/context untuk guest mengembalikan 200 dan is_guest=True."""
        self.handler.headers = {}
        self.handler.path = "/api/ai-room/matematika/context"
        with patch.object(self.handler, "send_response"):
            with patch.object(self.handler, "send_header"):
                with patch.object(self.handler, "end_headers"):
                    self.handler._handle_get_ai_room_context("matematika")

        res = self._get_json_response()
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_guest"])
        self.assertIn("context", res)
        self.assertEqual(res["context"]["mapel"], "matematika")
        self.assertEqual(res["context"]["total_soal"], 0)

    @patch("ai_room.fetch_supabase_attempts")
    @patch("server._verify_supabase_token")
    def test_get_ai_room_context_authenticated(self, mock_vtok, mock_fetch):
        """GET /api/ai-room/matematika/context untuk user login menghitung agregat attempt."""
        mock_vtok.return_value = (True, {"id": "user-d2-test"})
        mock_fetch.return_value = [{
            "mapel": "matematika",
            "paket": 1,
            "items": [
                {"position": 1, "topic_id": "Aljabar", "final_answer": "A", "is_correct": True, "waktu_detik": 35},
                {"position": 2, "topic_id": "Aljabar", "final_answer": "B", "is_correct": False, "waktu_detik": 50}
            ]
        }]
        self.handler.headers = {"Authorization": "Bearer valid_token_123"}
        self.handler.path = "/api/ai-room/matematika/context"

        with patch.object(self.handler, "send_response"):
            with patch.object(self.handler, "send_header"):
                with patch.object(self.handler, "end_headers"):
                    self.handler._handle_get_ai_room_context("matematika")

        res = self._get_json_response()
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["is_guest"])
        self.assertEqual(res["context"]["total_soal"], 2)
        self.assertEqual(res["context"]["total_benar"], 1)
        self.assertEqual(res["context"]["akurasi"], 50.0)

    def test_post_ai_room_chat_empty_message(self):
        """POST /api/ai-room/matematika/chat dengan pesan kosong menghasilkan 400 Bad Request."""
        self.handler.headers = {"Content-Length": "15"}
        self.handler.rfile = io.BytesIO(json.dumps({"message": ""}).encode("utf-8"))
        self.handler.path = "/api/ai-room/matematika/chat"

        with patch.object(self.handler, "send_response"):
            with patch.object(self.handler, "send_header"):
                with patch.object(self.handler, "end_headers"):
                    self.handler._handle_post_ai_room_chat("matematika")

        res = self._get_json_response()
        self.assertEqual(res["status"], "error")
        self.assertIn("tidak boleh kosong", res["message"])

    @patch("ai_room.chat_ai_room")
    def test_post_ai_room_chat_success(self, mock_chat):
        """POST /api/ai-room/matematika/chat berhasil memanggil chat dan mengembalikan respons."""
        mock_chat.return_value = {
            "reply": "Strategi terbaik untuk aljabar adalah memahami faktorisasi suku dua.",
            "model": "mock-coach-llm"
        }
        req_body = json.dumps({"message": "Bagaimana cara cepat aljabar?"}).encode("utf-8")
        self.handler.headers = {"Content-Length": str(len(req_body))}
        self.handler.rfile = io.BytesIO(req_body)
        self.handler.path = "/api/ai-room/matematika/chat"

        with patch.object(self.handler, "send_response"):
            with patch.object(self.handler, "send_header"):
                with patch.object(self.handler, "end_headers"):
                    self.handler._handle_post_ai_room_chat("matematika")

        res = self._get_json_response()
        self.assertEqual(res["status"], "success")
        self.assertIn("faktorisasi suku dua", res["reply"])

    def test_get_ruang_page_serves_html(self):
        """GET /ruang/matematika menyajikan ruang.html dengan status 200 dan text/html."""
        self.handler.path = "/ruang/matematika"
        sent_status = []
        sent_headers = {}

        def mock_send_body(code, ctype, body, headers=None):
            sent_status.append(code)
            sent_headers["Content-Type"] = ctype
            self.handler.wfile.write(body)

        self.handler._send_body = mock_send_body
        self.handler.do_GET()

        self.assertEqual(sent_status, [200])
        self.assertIn("text/html", sent_headers["Content-Type"])
        body = self.handler.wfile.getvalue().decode("utf-8")
        self.assertIn("Ruang Mapel - AI Coach", body)
        self.assertIn("chatInput", body)


if __name__ == "__main__":
    unittest.main()
