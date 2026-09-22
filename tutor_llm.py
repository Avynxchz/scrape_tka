# -*- coding: utf-8 -*-
"""tutor_llm.py — Abstraksi provider LLM untuk AI Tutor.

Interface tunggal `generate()` sehingga logika tutor tidak pernah bergantung
pada provider konkret. Prioritas provider (pertama yang terkonfigurasi menang):

  1. OLLAMA_BASE_URL   -> server Ollama lokal (kompatibel OpenAI di /v1)
  2. OPENAI_COMPATIBLE_BASE_URL (+ LLM_API_KEY) -> cloud OpenAI-compatible
     (OpenRouter / Novita / vLLM / dll — TANPA hardcode vendor)

Tidak ada fallback diam antar provider: bila provider aktif gagal, error
dilempar apa adanya agar UI bisa menampilkan state retry yang jujur.
"""
import json
import os
import time
import urllib.error
import urllib.request

DEFAULT_TIMEOUT = 120          # detik per permintaan chat
DEFAULT_NUM_PREDICT = 1024     # batas token keluaran (lokal)


class LLMError(Exception):
    """Kegagalan pemanggilan LLM (koneksi, timeout, rate limit, respons rusak)."""

    def __init__(self, message, kind="provider_error", status=None):
        super().__init__(message)
        self.kind = kind          # timeout | rate_limit | connection | malformed | provider_error
        self.status = status


def _first_env(*names, default=None):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


import re
import threading

_key_lock = threading.Lock()
_key_rotator_index = 0
_key_cooldowns = {}  # {key: timestamp_until_cooldown_expires}


def get_api_keys():
    """Mengambil semua API key dari LLM_API_KEYS (koma/spasi/baris baru) atau LLM_API_KEY."""
    raw = _first_env("LLM_API_KEYS", "LLM_API_KEY", default="")
    if not raw:
        return []
    parts = [k.strip() for k in re.split(r"[,;\s\n\r]+", raw) if k.strip()]
    return parts


def next_api_key():
    """Memutar API key secara round-robin dan menghindari key yang sedang cooldown 429."""
    global _key_rotator_index
    keys = get_api_keys()
    if not keys:
        return None
    with _key_lock:
        now = time.time()
        for _ in range(len(keys)):
            k = keys[_key_rotator_index % len(keys)]
            _key_rotator_index += 1
            if _key_cooldowns.get(k, 0) <= now:
                return k
        _key_rotator_index += 1
        return min(keys, key=lambda k: _key_cooldowns.get(k, 0))


def mark_key_rate_limited(key, cooldown_seconds=20):
    """Tandai satu key terkena 429 agar sementara tidak dipilih dan rotasi lanjut ke key lain."""
    if key:
        with _key_lock:
            _key_cooldowns[key] = time.time() + cooldown_seconds


def active_provider_info():
    """Info provider aktif (untuk ditampilkan/diagnosa — tanpa membocorkan API key)."""
    ollama = _first_env("OLLAMA_BASE_URL", default="http://127.0.0.1:11434")
    cloud = _first_env("OPENAI_COMPATIBLE_BASE_URL", "LLM_BASE_URL")
    keys = get_api_keys()
    if cloud:
        return {
            "provider": "openai_compatible",
            "base_url": cloud,
            "model": _first_env("LLM_MODEL", default=""),
            "api_key_set": len(keys) > 0,
            "keys_count": len(keys),
        }
    return {
        "provider": "ollama",
        "base_url": ollama,
        "model": _first_env("LLM_MODEL", default=""),
        "api_key_set": False,
        "keys_count": 0,
    }


_model_cache = {"models": None, "ts": 0.0}


def _available_ollama_models(base_url, timeout=4):
    """Daftar model Ollama terinstal (cache 30 dtk supaya tidak spam endpoint)."""
    now = time.time()
    if _model_cache["models"] is not None and now - _model_cache["ts"] < 30:
        return _model_cache["models"]
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/api/tags", timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
        models = [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        models = []
    _model_cache["models"] = models
    _model_cache["ts"] = now
    return models


def resolve_ollama_model():
    """Tentukan model Ollama: env LLM_MODEL -> kandidat kecil cepat -> apa pun
    yang terinstal. CPU-only host butuh model kecil agar interaktif (~token/s).
    Return (model, None) bila OK, atau (None, pesan) bila tidak ada model."""
    models = _available_ollama_models(_first_env("OLLAMA_BASE_URL", default="http://127.0.0.1:11434"))
    if not models:
        return None, ("Ollama berjalan tetapi tidak ada model terinstal. "
                      "Instal model, mis.: `ollama pull qwen3:1.7b`, atau "
                      "konfigurasi provider cloud via OPENAI_COMPATIBLE_BASE_URL.")
    preferred = os.environ.get("LLM_MODEL", "") or "qwen3:1.7b"
    for cand in (preferred, "qwen3:1.7b", "qwen3:4b", "qwen3:8b", "deepseek-r1:8b"):
        if cand in models:
            return cand, None
    return models[0], None


def generate(messages, *, temperature=0.7, max_tokens=None, timeout=None):
    """Kirim daftar pesan {role, content} ke provider aktif, balas teks murni.

    Melempar LLMError dengan `kind` yang jelas agar pemanggil bisa
    menampilkan pesan retry yang tepat tanpa mengorupsi riwayat.
    """
    timeout = timeout or _first_env("LLM_TIMEOUT", default=DEFAULT_TIMEOUT, )
    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT

    info = active_provider_info()
    if info["provider"] == "openai_compatible":
        return _post_openai_compatible(messages, info, temperature, max_tokens, timeout)
    model, err = resolve_ollama_model()
    if err:
        raise LLMError(err, kind="provider_error")
    info["model"] = model
    return _post_ollama(messages, info, temperature, max_tokens, timeout)


# ---------------------------------------------------------------------------
# Implementasi per provider
# ---------------------------------------------------------------------------
def _clean_think(text):
    """Buang blok penalaran internal <think>…</think> bila provider memancarkannya."""
    if not text:
        return text
    out, rest = [], text
    while True:
        s = rest.find("<think>")
        if s == -1:
            out.append(rest)
            break
        e = rest.find("</think>", s)
        if e == -1:
            # blok tak tertutup: buang dari <think> sampai akhir
            out.append(rest[:s])
            break
        out.append(rest[:s])
        rest = rest[e + len("</think>"):]
    return "".join(out).strip()


def _post_ollama(messages, info, temperature, max_tokens, timeout):
    url = info["base_url"].rstrip("/") + "/api/chat"
    # num_ctx eksplisit: default Ollama (4096) dapat memotong prompt konteks
    # tutor (soal + solusi + riwayat). 8192 aman utk prompt penuh.
    try:
        num_ctx = int(os.environ.get("LLM_NUM_CTX", "8192"))
    except ValueError:
        num_ctx = 8192
    if max_tokens is None:
        try:
            max_tokens = int(os.environ.get("LLM_NUM_PREDICT", str(DEFAULT_NUM_PREDICT)))
        except ValueError:
            max_tokens = DEFAULT_NUM_PREDICT
    payload = {
        "model": info["model"],
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens or DEFAULT_NUM_PREDICT,
            "num_ctx": num_ctx,
        },
    }
    # qwen3: matikan mode berpikir agar jawaban tutor langsung & ringkas.
    if "qwen3" in info["model"].lower():
        payload["think"] = False
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise LLMError(f"Ollama HTTP {e.code}: {e.reason}", kind="provider_error", status=e.code)
    except urllib.error.URLError as e:
        raise LLMError(f"Tidak dapat menghubungi Ollama ({info['base_url']}): {e.reason}",
                       kind="connection")
    except TimeoutError:
        raise LLMError("Permintaan ke Ollama timeout.", kind="timeout")
    except json.JSONDecodeError:
        raise LLMError("Respons Ollama bukan JSON valid.", kind="malformed")

    text = (data.get("message") or {}).get("content") or ""
    text = _clean_think(text)
    if not text.strip():
        raise LLMError("Ollama mengembalikan konten kosong.", kind="malformed")
    return text


def _post_openai_compatible(messages, info, temperature, max_tokens, timeout):
    url = info["base_url"].rstrip("/") + "/chat/completions"
    payload = {
        "model": info["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens or DEFAULT_NUM_PREDICT,
    }
    body = json.dumps(payload).encode("utf-8")
    keys = get_api_keys()
    max_attempts = max(3, len(keys) * 2 if keys else 3)
    data = None
    last_err = None

    for attempt in range(max_attempts):
        key = next_api_key()
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                mark_key_rate_limited(key, cooldown_seconds=25)
                last_err = LLMError(f"Provider HTTP 429 (Rate Limit): {e.reason}", kind="rate_limit", status=429)
                if attempt < max_attempts - 1:
                    time.sleep(0.3)
                    continue
            kind = "rate_limit" if e.code == 429 else "provider_error"
            raise LLMError(f"Provider HTTP {e.code}: {e.reason}", kind=kind, status=e.code)
        except urllib.error.URLError as e:
            raise LLMError(f"Tidak dapat menghubungi provider ({info['base_url']}): {e.reason}",
                           kind="connection")
        except TimeoutError:
            raise LLMError("Permintaan ke provider timeout.", kind="timeout")
        except json.JSONDecodeError:
            raise LLMError("Respons provider bukan JSON valid.", kind="malformed")
    else:
        if last_err:
            raise last_err
        raise LLMError("Semua API key sedang padat/mencapai batas. Coba lagi sebentar.", kind="rate_limit")

    try:
        text = data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        raise LLMError("Struktur respons provider tidak dikenali.", kind="malformed")
    text = _clean_think(text)
    if not text.strip():
        raise LLMError("Provider mengembalikan konten kosong.", kind="malformed")
    return text


def wait_until_ready(wait_seconds=10, poll=0.5):
    """Tunggu provider aktif siap (dipakai smoke test; bukan jalur runtime)."""
    info = active_provider_info()
    if info["provider"] != "ollama":
        return True
    url = info["base_url"].rstrip("/") + "/api/version"
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2):
                return True
        except Exception:
            time.sleep(poll)
    return False
