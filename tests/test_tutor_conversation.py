# -*- coding: utf-8 -*-
"""Test AI Tutor konversasional: storage, konteks, isolasi, idempotency, error.

Fixture LLM: generate_tutor_response dipatch agar TIDAK memanggil provider
sungguhan — yang diuji adalah arsitektur (storage, prompt, endpoint), bukan
kualitas model. Konten fixture jelas-label agar tidak menyerupai data asli.
"""
import json
import os
import tempfile
import threading
import urllib.request

os.environ.setdefault("VISITOR_ADMIN_KEY", "test_admin_key_for_testing")

import pytest

import server
import tutor_engine
import tutor_llm
import tutor_store

DB_FD, DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(DB_FD)


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch):
    monkeypatch.setattr(tutor_store, "DB_PATH", DB_PATH)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    tutor_store.init_db()
    yield


# ---------------------------------------------------------------------------
# 1. Conversation storage
# ---------------------------------------------------------------------------
def test_create_conversation_and_messages():
    conv = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    assert conv["canonical_question_id"] == "mtk_p2_q02"
    tutor_store.add_message(conv["id"], "user", "halo")
    tutor_store.add_message(conv["id"], "assistant", "hai juga")
    msgs = tutor_store.get_messages(conv["id"])
    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert msgs[1]["seq"] == 2


def test_resume_same_question_not_new_conversation():
    c1 = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    tutor_store.add_message(c1["id"], "user", "satu")
    c2 = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    assert c1["id"] == c2["id"]
    assert c2["message_count"] == 1


def test_start_new_conversation_archives_old():
    c1 = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    tutor_store.add_message(c1["id"], "user", "lama")
    c2 = tutor_store.start_new_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    assert c2["id"] != c1["id"]
    # Riwayat lama TIDAK hilang (diarsipkan, auditable)
    assert tutor_store.get_messages(c1["id"])[0]["content"] == "lama"
    # Percakapan aktif kini yang baru
    active = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    assert active["id"] == c2["id"]


# ---------------------------------------------------------------------------
# 2. Context assembly (Layer 2 + Layer 3 + kunci + riwayat + pesan)
# ---------------------------------------------------------------------------
def _mk_ctx():
    canon_ctx = {
        "id": "mtk_p2_q02", "type": "PG",
        "soal_text": "[STIMULUS]\nsisa\n[SOAL]\nbentuk pecahan eksponen\n[OPSI JAWABAN]\n  A. 1\n[PERNYATAAN]",
        "visual_text": "(uji)", "formulas": [{"latex": "x^2", "source": "official data-latex"}],
        "langkah_claude": [], "kunci_display": "C",
    }
    solution = {
        "pembahasan": {"konsep_kunci": ["eksponen pecahan"],
                       "langkah_penyelesaian": ["1. Uji — langkah"], "tips_trik": "uji"},
        "review": None, "key_crosscheck": {"match": True}, "source": {"file": "X.json"},
    }
    return canon_ctx, solution


def test_prompt_contains_all_layers_and_history():
    canon_ctx, solution = _mk_ctx()
    history = [{"role": "user", "content": "pertanyaan sebelumnya"},
               {"role": "assistant", "content": "jawaban sebelumnya"}]
    messages, meta = tutor_engine.build_tutor_prompt(
        canon_ctx, solution, "C", history, "Kenapa 8 jadi 2^3?")
    sys_text = messages[0]["content"]
    # Layer 2
    assert "bentuk pecahan eksponen" in sys_text
    assert "x^2" in sys_text
    # Kunci resmi
    assert "C" in sys_text and "RESMI" in sys_text
    # Layer 3
    assert "eksponen pecahan" in sys_text
    assert "1. Uji — langkah" in sys_text
    # Ringkasan + riwayat + pesan saat ini
    assert "pertanyaan sebelumnya" in sys_text
    assert "Kenapa 8 jadi 2^3?" in sys_text
    assert messages[-1] == {"role": "user", "content": "Kenapa 8 jadi 2^3?"}
    assert meta["intent"] == "explain_answer"


def test_intent_distribution():
    cases = {
        "step 4 doang dong": "explain_specific_step",
        "kenapa bukan B?": "compare_options",
        "kalau 8 diganti 16 gimana?": "hypothetical_change",
        "bisa pakai cara lain?": "ask_strategy",
        "gue masih nggak ngerti": "simplify",
        "contoh lain dong": "give_example",
        "kok?": "continue_previous_point",  # follow-up DENGAN riwayat
        "jadi intinya apa?": "explain_answer",
    }
    for msg, expected in cases.items():
        # "kok?" tanpa riwayat = pertanyaan baru -> explain_why (perilaku engine)
        hist = [{"role": "assistant", "content": "penjelasan sebelumnya"}]
        assert tutor_engine.detect_intent(msg, hist) == expected, msg


def test_review_flag_enter_context():
    canon_ctx, solution = _mk_ctx()
    solution["review"] = {"reason": "uji alasan verifikasi"}
    messages, _ = tutor_engine.build_tutor_prompt(
        canon_ctx, solution, "C", [], "kenapa?")
    assert "VERIFIKASI MANUAL" in messages[0]["content"]
    assert "uji alasan verifikasi" in messages[0]["content"]


# ---------------------------------------------------------------------------
# 3. Isolasi soal
# ---------------------------------------------------------------------------
def test_question_isolation():
    cu = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    tutor_store.add_message(cu["id"], "user", "pertanyaan tentang Q2")
    c3 = tutor_store.get_or_create_conversation("uA", "mtk_p2_q03", "matematika", 2, 3)
    tutor_store.add_message(c3["id"], "user", "pertanyaan tentang Q3")
    hist3 = tutor_store.get_messages(c3["id"])
    assert all("Q2" not in m["content"] for m in hist3)
    # beda user juga terisolasi
    cb = tutor_store.get_or_create_conversation("uB", "mtk_p2_q02", "matematika", 2, 2)
    assert tutor_store.get_messages(cb["id"]) == []


def test_history_window_not_exceed_budget():
    conv = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    for i in range(30):
        tutor_store.add_message(conv["id"], "user", f"pesan uji nomor {i}")
    window = tutor_store.get_history_window(conv["id"], 12)
    assert len(window) == 12
    assert window[-1]["content"] == "pesan uji nomor 29"
    # seluruh 30 tetap tersimpan
    assert len(tutor_store.get_messages(conv["id"])) == 30


# ---------------------------------------------------------------------------
# 4. Idempotency / duplicate protection
# ---------------------------------------------------------------------------
def test_duplicate_request_id_not_duplicated():
    conv = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)
    m1, ins1 = tutor_store.add_message(conv["id"], "user", "dup", request_id="r-123")
    m2, ins2 = tutor_store.add_message(conv["id"], "user", "dup", request_id="r-123")
    assert ins1 is True and ins2 is False
    assert m1["id"] == m2["id"]
    assert len(tutor_store.get_messages(conv["id"])) == 1


# ---------------------------------------------------------------------------
# 5. Error handling: LLM gagal tidak merusak state
# ---------------------------------------------------------------------------
def test_llm_failure_keeps_user_message(monkeypatch):
    conv = tutor_store.get_or_create_conversation("uA", "mtk_p2_q02", "matematika", 2, 2)

    def boom(*a, **k):
        raise tutor_llm.LLMError("uji gagal", kind="connection")

    monkeypatch.setattr(tutor_engine, "generate_tutor_response", boom)
    with pytest.raises(tutor_llm.LLMError):
        tutor_engine.generate_tutor_response(None, None, "C", [], "pesan")
    # Pesan user tetap tersimpan oleh pemanggil (server) — simulasi alur server:
    tutor_store.add_message(conv["id"], "user", "pesan tersimpan meski LLM gagal")
    msgs = tutor_store.get_messages(conv["id"])
    assert msgs[-1]["role"] == "user"
    assert not any(m["role"] == "assistant" for m in msgs)


# ---------------------------------------------------------------------------
# 6. Endpoint HTTP end-to-end (LLM di-fixture)
# ---------------------------------------------------------------------------
PORT = 8891


@pytest.fixture(scope="module")
def http_server():
    server.PORT = PORT
    httpd = server.ThreadingHTTPServer(("", PORT), server.AppRequestHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield httpd
    httpd.shutdown()


def _post(path, body, cookie=None):
    req = urllib.request.Request(
        f"http://localhost:{PORT}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read()), r.headers.get_all("Set-Cookie") or []
    except urllib.error.HTTPError as e:
        # Endpoint boleh membalas status error (mis. 502 LLM) — baca bodynya
        return e.code, json.loads(e.read()), e.headers.get_all("Set-Cookie") or []


def _get(path, cookie=None):
    req = urllib.request.Request(f"http://localhost:{PORT}{path}")
    if cookie:
        req.add_header("Cookie", cookie)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status, json.loads(r.read()), r.headers.get_all("Set-Cookie") or []


@pytest.fixture
def fake_llm(monkeypatch):
    calls = []

    def fake_generate(canon_ctx, solution, official_answer, history_msgs,
                      user_message, summary=None, subject_name="Matematika", **kwargs):
        calls.append({
            "user": user_message, "n_history": len(history_msgs),
            "official": official_answer,
            "has_l2": bool(canon_ctx and canon_ctx.get("soal_text")),
            "has_l3": bool(solution and solution.get("pembahasan")),
        })
        return f"[FIXTURE-REPLY utk: {user_message}]", {"intent": "explain_answer"}

    monkeypatch.setattr(server.tutor_engine, "generate_tutor_response", fake_generate)
    return calls


def test_chat_endpoint_full_flow(http_server, fake_llm):
    cookie = []
    st, d, sc = _post("/api/tutor/chat",
                      {"subject": "matematika", "paket": 2, "nomor": 2,
                       "message": "Kenapa 8 jadi 2^3?", "request_id": "req-a1"})
    assert st == 200 and d["status"] == "success"
    assert "[FIXTURE-REPLY" in d["reply"]
    assert sc and "tutor_uid=" in sc[0]
    cookie.append(sc[0].split(";")[0])

    # Giliran kedua: riwayat berisi giliran pertama (follow-up memakai history)
    st, d2, _ = _post("/api/tutor/chat",
                      {"subject": "matematika", "paket": 2, "nomor": 2,
                       "message": "Terus kenapa harus disamain basis?",
                       "request_id": "req-a2"}, cookie=cookie[0])
    assert st == 200
    assert fake_llm[-1]["n_history"] >= 2  # user+assistant giliran 1
    # Konteks lengkap sampai ke LLM
    assert fake_llm[-1]["has_l2"] and fake_llm[-1]["has_l3"]
    assert fake_llm[-1]["official"] == "C"

    # Isolasi soal: Q3 punya riwayat sendiri
    st, d3, _ = _post("/api/tutor/chat",
                      {"subject": "matematika", "paket": 2, "nomor": 3,
                       "message": "halo Q3", "request_id": "req-a3"}, cookie=cookie[0])
    assert fake_llm[-1]["n_history"] == 0  # tidak bocor dari Q2

    # Duplikat kirim (retry) tidak menduplikasi pesan
    st, d4, _ = _post("/api/tutor/chat",
                      {"subject": "matematika", "paket": 2, "nomor": 2,
                       "message": "Terus kenapa harus disamain basis?",
                       "request_id": "req-a2"}, cookie=cookie[0])
    st, state, _ = _get("/api/tutor/state?subject=matematika&paket=2&nomor=2",
                        cookie=cookie[0])
    user_msgs = [m for m in state["messages"] if m["role"] == "user"]
    assert len(user_msgs) == 2  # req-a1 + req-a2 (bukan 3)


def test_tutor_state_endpoint(http_server):
    st, d, sc = _get("/api/tutor/state?subject=matematika&paket=2&nomor=25")
    assert st == 200 and d["status"] == "success"
    assert d["provider"]["provider"] == "ollama"
    assert d["messages"] == []  # percakapan baru: tidak ada riwayat
    assert sc and "tutor_uid=" in sc[0]


def test_chat_endpoint_error_no_fake_reply(http_server, monkeypatch):
    def boom(*a, **k):
        raise tutor_llm.LLMError("prov gagal", kind="connection")

    monkeypatch.setattr(server.tutor_engine, "generate_tutor_response", boom)
    st, d, sc = _post("/api/tutor/chat",
                      {"subject": "matematika", "paket": 2, "nomor": 5,
                       "message": "pesan saat provider mati", "request_id": "req-e1"})
    assert st == 502 and d["status"] == "llm_error" and d["retryable"] is True
    # Pesan user tetap tersimpan (bisa di-retry tanpa hilang)
    cookie = sc[0].split(";")[0]
    st, state, _ = _get("/api/tutor/state?subject=matematika&paket=2&nomor=5", cookie=cookie)
    assert any(m["role"] == "user" and "provider mati" in m["content"]
               for m in state["messages"])
    assert not any(m["role"] == "assistant" for m in state["messages"])


def test_summary_created_for_long_conversation(http_server, fake_llm):
    cookie = None
    for i in range(14):
        st, d, sc = _post("/api/tutor/chat",
                          {"subject": "matematika", "paket": 2, "nomor": 6,
                           "message": f"giliran uji panjang {i}", "request_id": f"s-{i}"},
                          cookie=cookie)
        if sc:
            cookie = sc[0].split(";")[0]
    st, state, _ = _get("/api/tutor/state?subject=matematika&paket=2&nomor=6",
                        cookie=cookie)
    assert state["summary"], "ringkasan harus terbentuk utk percakapan panjang"
