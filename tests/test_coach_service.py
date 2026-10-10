# -*- coding: utf-8 -*-
"""tests/test_coach_service.py — Unit test untuk Layanan Guru AI Coach (FASE A3).

Menguji:
1. Validasi ketat Bagian 6.3 (validate_coach_output)
   - Sukses pada skema valid
   - Tolak key asing
   - Tolak kata terlarang (bodoh, malas, pasti lolos, dll.)
   - Tolak soal tidak ada di fokus_soal
   - Tolak task_id tidak ada di kandidat_tugas
   - Tolak batas karakter terlampaui
   - Tolak angka liar di luar evidence
   - Tolak non-Bahasa Indonesia
2. Template Cadangan (coach_template)
   - Output valid skema coach_output_v1
   - Sumber = "template"
   - Lolos validasi ketat
3. Integrasi Coach Service (autopsy/coach)
   - Sukses via mock LLM -> sumber "ai"
   - Fallback otomatis saat timeout/error LLM -> sumber "template"
   - Fallback otomatis saat LLM menghasilkan JSON rusak / validasi gagal
   - Circuit breaker aktif setelah kegagalan berturut-turut
4. Keamanan & Cache Endpoint
   - Token & ownership validation
   - In-memory cache hit
"""

import copy
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autopsy import coach
from autopsy import coach_template
from autopsy import evidence
import tutor_llm


def sample_evidence():
    """Evidence pack dummy standar untuk pengujian."""
    return {
        "versi": "coach_input_v1",
        "mapel": "matematika",
        "paket": 1,
        "skor_pct": 52,
        "n_soal": 25,
        "n_dijawab": 20,
        "n_benar": 13,
        "n_kosong": 5,
        "durasi_batas_menit": 75,
        "durasi_aktif_menit": 42,
        "ended_by": "user",
        "hari_menuju_ujian": 2,
        "data_tipis": False,
        "pola": {
            "median_waktu_detik": 38,
            "jatah_detik": 180,
            "akurasi_awal_pct": 60,
            "akurasi_akhir_pct": 40,
            "fatigue": False,
        },
        "kebocoran": [
            {
                "label": "terburu",
                "soal_hilang": 7,
                "bukti": "7 soal dijawab kurang dari 36 detik dan salah",
            }
        ],
        "topik": [
            {"topik": "Barisan dan Deret", "n": 5, "benar": 3, "akurasi_pct": 60}
        ],
        "fokus_soal": [
            {
                "no": 9,
                "soal_id": "matematika:1:9",
                "topik": "Barisan dan Deret",
                "label": "overthinking",
                "kunci": "B",
                "jawaban_awal": "B",
                "jawaban_akhir": "D",
                "benar": False,
                "waktu_detik": 52,
                "ganti_jawaban": 1,
                "ragu": False,
                "jejak": [
                    {"t_detik": 14, "aksi": "pilih", "opsi": "B"},
                    {"t_detik": 52, "aksi": "ganti", "opsi": "D"},
                ],
                "ringkas_soal": "Soal barisan aritmatika mencari suku ke-10.",
                "pembahasan_ringkas": "Pakai rumus Un = a + (n-1)b.",
                "pilar_refs": ["matematika:1:9#5"],
                "serupa_refs": ["matematika:1:9-S1"],
            }
        ],
        "yang_bagus": "Pada soal yang dikerjakan tenang, jawabanmu tepat.",
        "kandidat_tugas": [
            {
                "task_id": "d1-pilar-auto",
                "judul": "Pilar 5: Trik dan Jebakan",
                "menit": 6,
                "alasan": "terburu",
            },
            {
                "task_id": "d1-soal-auto",
                "judul": "3 Soal Serupa Barisan",
                "menit": 9,
                "alasan": "latihan",
            },
        ],
    }


def sample_valid_coach_output():
    """Output valid yang lolos seluruh kriteria Bagian 6.3."""
    return {
        "versi": "coach_output_v1",
        "sapaan": "Saya sudah mengamati caramu mengerjakan tadi. Ada pola yang jelas.",
        "penilaian": "Skormu 52%. Bagian yang paling cepat dipulihkan adalah membenahi ritme membaca soal.",
        "pengamatan": [
            "Soal 9: kamu memilih B di detik 14 lalu mengganti ke D di detik 52.",
            "7 soal dijawab kurang dari 36 detik dan salah dari total 25 soal.",
            "Median waktu pengerjaanmu 38 detik berbanding jatah 180 detik.",
        ],
        "sudah_bagus": "Pada soal yang kamu kerjakan tenang, akurasimu stabil.",
        "kebocoran": [
            {
                "label": "terburu",
                "judul": "Menjawab sebelum tuntas membaca soal",
                "bukti": "7 soal dijawab terburu-buru",
                "tafsir": "Kemungkinan opsi diklik sebelum kalimat tanya dipahami.",
                "tindakan": "Baca ulang kalimat tanya sebelum mengklik pilihan.",
            }
        ],
        "per_soal": [
            {
                "no": 9,
                "penyebab": "overthinking",
                "dipelajari": "Pertahankan jawaban pertama kecuali ada salah hitung.",
                "langkah": [
                    "Hitung ulang nomor 9 tanpa melihat kunci jawaban.",
                    "Buka pembahasan pilar jika masih ragu.",
                ],
                "cek_paham": "Apa yang membuatmu mengganti opsi B ke D tadi?",
            }
        ],
        "misi": {
            "pembuka": "Misi 10 menit: latih membaca sebelum mengklik opsi.",
            "task_ids": ["d1-pilar-auto"],
        },
        "rencana": [],
        "penutup": "Mulai dari satu langkah kecil hari ini. Kita lihat kemajuannya.",
        "catatan_data": "",
    }


class TestCoachValidator(unittest.TestCase):
    """Pengujian aturan validasi ketat Bagian 6.3."""

    def setUp(self):
        self.evidence = sample_evidence()
        self.valid_out = sample_valid_coach_output()

    def test_valid_output_passes(self):
        ok, reason = coach.validate_coach_output(self.valid_out, self.evidence)
        self.assertTrue(ok, f"Seharusnya lolos validasi tapi gagal: {reason}")

    def test_reject_non_dict(self):
        ok, reason = coach.validate_coach_output("bukan dict", self.evidence)
        self.assertFalse(ok)
        self.assertIn("bukan objek JSON", reason)

    def test_reject_wrong_version(self):
        bad = copy.deepcopy(self.valid_out)
        bad["versi"] = "coach_v2"
        ok, reason = coach.validate_coach_output(bad, self.evidence)
        self.assertFalse(ok)
        self.assertIn("Versi salah", reason)

    def test_reject_unknown_root_keys(self):
        bad = copy.deepcopy(self.valid_out)
        bad["hacked_key"] = "injection"
        ok, reason = coach.validate_coach_output(bad, self.evidence)
        self.assertFalse(ok)
        self.assertIn("key tidak dikenal", reason)

    def test_reject_overlength_sapaan(self):
        bad = copy.deepcopy(self.valid_out)
        bad["sapaan"] = "Halo " * 40  # >140 chars
        ok, reason = coach.validate_coach_output(bad, self.evidence)
        self.assertFalse(ok)
        self.assertIn("Sapaan melebihi", reason)

    def test_reject_overlength_penilaian(self):
        bad = copy.deepcopy(self.valid_out)
        bad["penilaian"] = "Penilaian panjang sekali " * 15  # >260 chars
        ok, reason = coach.validate_coach_output(bad, self.evidence)
        self.assertFalse(ok)
        self.assertIn("Penilaian melebihi", reason)

    def test_reject_forbidden_words(self):
        bad_words = ["bodoh", "kamu malas", "goblok", "kamu payah", "pasti lolos"]
        for w in bad_words:
            bad = copy.deepcopy(self.valid_out)
            bad["penilaian"] = f"Skormu karena kamu {w} tadi di tes."
            ok, reason = coach.validate_coach_output(bad, self.evidence)
            self.assertFalse(ok, f"Kata '{w}' seharusnya ditolak!")
            self.assertIn("kata terlarang", reason)

    def test_reject_invalid_question_number(self):
        bad = copy.deepcopy(self.valid_out)
        bad["per_soal"][0]["no"] = 99  # Soal 99 tidak ada di evidence (hanya ada 9)
        ok, reason = coach.validate_coach_output(bad, self.evidence)
        self.assertFalse(ok)
        self.assertIn("tidak ada di fokus_soal", reason)

    def test_reject_invalid_task_id(self):
        bad = copy.deepcopy(self.valid_out)
        bad["misi"]["task_ids"] = ["task-ngarang-123"]
        ok, reason = coach.validate_coach_output(bad, self.evidence)
        self.assertFalse(ok)
        self.assertIn("tidak ada di kandidat_tugas", reason)

    def test_reject_invalid_penyebab(self):
        bad = copy.deepcopy(self.valid_out)
        bad["per_soal"][0]["penyebab"] = "ceroboh"  # bukan kategori terdaftar
        ok, reason = coach.validate_coach_output(bad, self.evidence)
        self.assertFalse(ok)
        self.assertIn("tidak dikenal", reason)

    def test_reject_excessive_unknown_numbers(self):
        bad = copy.deepcopy(self.valid_out)
        # Tambahkan banyak angka liar yang tidak ada di evidence
        bad["pengamatan"] = [
            "Ada 789 siswa lain dengan skor 888 dan nilai 999.",
            "Waktu tersisa 777 detik dengan 666 kombinasi.",
            "Jawaban nomor 9 dijawab detik 52.",
        ]
        ok, reason = coach.validate_coach_output(bad, self.evidence)
        self.assertFalse(ok)
        self.assertIn("angka tidak dikenal", reason)

    def test_reject_non_indonesian_language(self):
        english_out = {
            "versi": "coach_output_v1",
            "sapaan": "Hello student, I observed your quiz.",
            "penilaian": "Your score is low. Work on reading carefully.",
            "pengamatan": [
                "Question 9: you chose B then changed to D.",
                "Seven questions answered too quickly.",
                "Median time 38 seconds.",
            ],
            "sudah_bagus": "Good job on questions you answered calmly.",
            "kebocoran": [
                {
                    "label": "terburu",
                    "judul": "Answering too quickly",
                    "bukti": "7 questions were answered too fast",
                    "tafsir": "Likely picked before reading completely.",
                    "tindakan": "Reread the question before clicking.",
                }
            ],
            "per_soal": [
                {
                    "no": 9,
                    "penyebab": "overthinking",
                    "dipelajari": "Keep the first answer.",
                    "langkah": ["Recalculate number 9."],
                    "cek_paham": "Why did you change your answer?",
                }
            ],
            "misi": {
                "pembuka": "10-minute mission: practice reading.",
                "task_ids": ["d1-pilar-auto"],
            },
            "rencana": [],
            "penutup": "Start small today.",
            "catatan_data": "",
        }
        ok, reason = coach.validate_coach_output(english_out, self.evidence)
        self.assertFalse(ok)
        self.assertIn("bahasa Indonesia", reason)


class TestCoachTemplate(unittest.TestCase):
    """Pengujian Template Cadangan Deterministik (coach_template)."""

    def setUp(self):
        self.evidence = sample_evidence()

    def test_template_generation_validity(self):
        tmpl = coach_template.generate_template(self.evidence)
        self.assertEqual(tmpl["versi"], "coach_output_v1")
        self.assertEqual(tmpl["sumber"], "template")
        self.assertTrue(isinstance(tmpl["pengamatan"], list))
        self.assertTrue(2 <= len(tmpl["pengamatan"]) <= 5)
        self.assertTrue(isinstance(tmpl["per_soal"], list))
        self.assertTrue(isinstance(tmpl["misi"], dict))

        # Harus 100% lolos validasi ketat Bagian 6.3
        ok, reason = coach.validate_coach_output(tmpl, self.evidence)
        self.assertTrue(ok, f"Template harus lolos validasi! Alasan gagal: {reason}")

    def test_template_handles_data_tipis(self):
        ev_tipis = copy.deepcopy(self.evidence)
        ev_tipis["data_tipis"] = True
        tmpl = coach_template.generate_template(ev_tipis)
        self.assertTrue(len(tmpl["catatan_data"]) > 0)
        self.assertIn("sedikit", tmpl["catatan_data"].lower())
        ok, reason = coach.validate_coach_output(tmpl, ev_tipis)
        self.assertTrue(ok, f"Template data tipis harus valid: {reason}")


class TestCoachService(unittest.TestCase):
    """Pengujian layanan Guru AI (autopsy/coach.py) dengan mock LLM."""

    def setUp(self):
        self.evidence = sample_evidence()
        coach._circuit_failures = 0
        coach._circuit_open_until = 0.0

    def test_json_parser_robustness(self):
        # 1. Bersih
        raw = '{"versi": "coach_output_v1"}'
        self.assertEqual(coach._parse_llm_json(raw), {"versi": "coach_output_v1"})

        # 2. Dalam markdown codeblock
        raw_md = '```json\n{"versi": "coach_output_v1"}\n```'
        self.assertEqual(coach._parse_llm_json(raw_md), {"versi": "coach_output_v1"})

        # 3. Ada teks sebelum dan sesudah
        raw_surround = 'Berikut hasil analisis:\n{"versi": "coach_output_v1"}\nSemoga bermanfaat!'
        self.assertEqual(coach._parse_llm_json(raw_surround), {"versi": "coach_output_v1"})

        # 4. JSON cacat
        raw_bad = '{"versi": "coach_output_v1'
        self.assertIsNone(coach._parse_llm_json(raw_bad))

    @patch("tutor_llm.generate_with_meta")
    def test_generate_coach_success_ai(self, mock_gen):
        valid_out = sample_valid_coach_output()
        mock_gen.return_value = (json.dumps(valid_out), {"model": "mock-gpt-4o"})

        result, meta = coach.generate_coach(self.evidence)
        self.assertEqual(result["sumber"], "ai")
        self.assertEqual(meta["sumber"], "ai")
        self.assertEqual(meta["model"], "mock-gpt-4o")
        self.assertEqual(meta["alasan"], "")
        self.assertEqual(result["versi"], "coach_output_v1")

    @patch("tutor_llm.generate_with_meta")
    def test_generate_coach_fallback_on_llm_error(self, mock_gen):
        mock_gen.side_effect = tutor_llm.LLMError(kind="timeout", message="Request timed out")

        result, meta = coach.generate_coach(self.evidence)
        self.assertEqual(result["sumber"], "template")
        self.assertEqual(meta["sumber"], "template")
        self.assertIn("timeout", meta["alasan"])
        self.assertEqual(result["versi"], "coach_output_v1")

    @patch("tutor_llm.generate_with_meta")
    def test_generate_coach_fallback_on_validation_failure(self, mock_gen):
        bad_out = sample_valid_coach_output()
        bad_out["penilaian"] = "Kamu bodoh sekali tidak bisa mengerjakan ini."
        mock_gen.return_value = (json.dumps(bad_out), {"model": "mock-llm"})

        result, meta = coach.generate_coach(self.evidence)
        self.assertEqual(result["sumber"], "template")
        self.assertEqual(meta["sumber"], "template")
        self.assertIn("validation_error", meta["alasan"])
        self.assertNotIn("bodoh", json.dumps(result))

    @patch("tutor_llm.generate_with_meta")
    def test_circuit_breaker_tripping(self, mock_gen):
        mock_gen.side_effect = tutor_llm.LLMError(kind="server_error", message="500 Internal Error")

        # Panggilan 1 & 2 & 3 gagal
        for _ in range(3):
            coach.generate_coach(self.evidence)

        # Panggilan ke-4: circuit breaker harus langsung aktif tanpa memanggil LLM lagi
        mock_gen.reset_mock()
        res, meta = coach.generate_coach(self.evidence)
        self.assertEqual(res["sumber"], "template")
        self.assertEqual(meta["alasan"], "circuit_breaker_active")
        mock_gen.assert_not_called()


class TestServerCoachEndpoint(unittest.TestCase):
    """Pengujian handler endpoint /api/autopsy/coach di server.py."""

    def test_cache_and_security(self):
        import server

        # Simpan di cache
        test_att_id = "test-att-12345"
        server._COACH_CACHE[test_att_id] = {
            "versi": "coach_output_v1",
            "sumber": "ai",
            "_user_id": "user-agus-01",
            "sapaan": "Halo murid.",
        }

        # Mock handler instance
        handler = server.AppRequestHandler.__new__(server.AppRequestHandler)
        handler.headers = {"Authorization": "Bearer fake_token"}

        # Patch _verify_supabase_token agar mengembalikan user lain
        with patch.object(server, "_verify_supabase_token", return_value=(True, {"id": "user-other-99"})):
            with patch.object(handler, "_is_valid_admin", return_value=False):
                with patch.object(handler, "_send_json") as mock_send:
                    handler.path = f"/api/autopsy/coach?attempt_id={test_att_id}"
                    handler._handle_get_autopsy_coach()
                    # User lain tidak boleh melihat attempt orang lain (403 Forbidden)
                    mock_send.assert_called_once()
                    status_code = mock_send.call_args[0][0]
                    self.assertEqual(status_code, 403)

        # Pemilik asli melihat attemptnya (200 OK dari memory cache)
        with patch.object(server, "_verify_supabase_token", return_value=(True, {"id": "user-agus-01"})):
            with patch.object(handler, "_is_valid_admin", return_value=False):
                with patch.object(handler, "_send_json") as mock_send:
                    handler.path = f"/api/autopsy/coach?attempt_id={test_att_id}"
                    handler._handle_get_autopsy_coach()
                    mock_send.assert_called_once()
                    status_code = mock_send.call_args[0][0]
                    body = mock_send.call_args[0][1]
                    self.assertEqual(status_code, 200)
                    self.assertEqual(body["coach"]["sapaan"], "Halo murid.")
                    self.assertNotIn("_user_id", body["coach"])  # Internal field disembunyikan


if __name__ == "__main__":
    unittest.main()
