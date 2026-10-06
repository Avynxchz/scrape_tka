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
import hashlib
import json
import os
import sqlite3
import sys
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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _looks_like_placeholder(value):
    """True bila nilai tampak seperti placeholder .env.example (bukan key asli).

    Nilai seperti 'gsk_AKUN_1_DISINI' harus dilewati agar tidak dianggap
    API key valid (menghindari error 401 berulang). Case-insensitive.
    """
    marker = value.upper()
    return "DISINI" in marker or "EXAMPLE" in marker


def _auto_load_env():
    if "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST"):
        return
    for fname in [".env", ".env.example"]:
        fpath = os.path.join(BASE_DIR, fname)
        if os.path.isfile(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip()
                            if k and k not in os.environ and v and not _looks_like_placeholder(v):
                                os.environ[k] = v
            except Exception:
                pass

_auto_load_env()


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


_gemini_key_lock = threading.Lock()
_gemini_rotator_index = 0
_gemini_cooldowns = {}


def get_gemini_api_keys():
    """Mengambil semua Gemini API key dari GEMINI_API_KEYS (koma/spasi/baris baru) serta GEMINI_TUTOR_API_KEY & GEMINI_API_KEY."""
    keys = []
    raw = _first_env("GEMINI_API_KEYS", default="")
    if raw:
        keys.extend([k.strip() for k in re.split(r"[,;\s\n\r]+", raw) if k.strip()])
    for env_name in ("GEMINI_TUTOR_API_KEY", "GEMINI_API_KEY"):
        val = os.environ.get(env_name)
        if val and val.strip() and val.strip() not in keys:
            keys.append(val.strip())
    return keys


def next_gemini_api_key():
    """Rotasi Gemini API key round-robin dengan deteksi cooldown 429."""
    global _gemini_rotator_index
    keys = get_gemini_api_keys()
    if not keys:
        return None
    with _gemini_key_lock:
        now = time.time()
        for _ in range(len(keys)):
            k = keys[_gemini_rotator_index % len(keys)]
            _gemini_rotator_index += 1
            if _gemini_cooldowns.get(k, 0) <= now:
                return k
        _gemini_rotator_index += 1
        return min(keys, key=lambda k: _gemini_cooldowns.get(k, 0))


def mark_gemini_key_rate_limited(key, cooldown_seconds=45):
    """Tandai satu key Gemini terkena 429 agar sementara tidak dipilih dan rotasi lanjut ke key lain."""
    if key:
        with _gemini_key_lock:
            _gemini_cooldowns[key] = time.time() + cooldown_seconds


def get_gemini_api_key():
    """Mengambil Google Gemini API key aktif."""
    return next_gemini_api_key()


def active_provider_info():
    """Info provider aktif (untuk ditampilkan/diagnosa — tanpa membocorkan API key)."""
    gemini_key = get_gemini_api_key()
    keys = get_api_keys()
    cloud = _first_env("OPENAI_COMPATIBLE_BASE_URL", "LLM_BASE_URL")
    ollama = _first_env("OLLAMA_BASE_URL", default="http://127.0.0.1:11434")

    model_options = []
    if cloud and keys:
        model_options.append({
            "id": "qwen-groq",
            "name": "Qwen 2.5 27B (Groq Fast)",
            "tier": "cloud",
            "default": not bool(gemini_key)
        })
    if gemini_key:
        model_options.append({
            "id": "gemini-flash",
            "name": "Gemini 3.8 Flash (Vision Multimodal)",
            "tier": "paid",
            "default": not model_options
        })
        model_options.append({
            "id": "gemini-pro",
            "name": "Gemini Pro (Advanced)",
            "tier": "paid",
            "default": False
        })

    if gemini_key:
        return {
            "provider": "google_gemini",
            "base_url": cloud or ollama,
            "model": "gemini-3.8-flash",
            "api_key_set": True,
            "has_gemini": True,
            "has_groq": bool(cloud and keys),
            "model_options": model_options,
        }
    if cloud:
        return {
            "provider": "openai_compatible",
            "base_url": cloud,
            "model": _first_env("LLM_MODEL", default=""),
            "api_key_set": len(keys) > 0,
            "keys_count": len(keys),
            "has_gemini": False,
            "has_groq": True,
            "model_options": model_options,
        }
    return {
        "provider": "ollama",
        "base_url": ollama,
        "model": _first_env("LLM_MODEL", default=""),
        "api_key_set": False,
        "keys_count": 0,
        "has_gemini": False,
        "has_groq": False,
        "model_options": model_options,
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


def generate(messages, *, model=None, image_paths=None, temperature=0.7, max_tokens=None,
             timeout=None, return_meta=False, cache_canonical_id=None,
             cache_intent=None, use_cache=True):
    """Kirim daftar pesan {role, content} ke provider aktif, balas teks murni.

    Bila return_meta=True, kembalikan tuple (text, {"model": actual_model, "provider": provider}).
    Melempar LLMError dengan `kind` yang jelas agar pemanggil bisa
    menampilkan pesan retry yang tepat tanpa mengorupsi riwayat.

    Cache: sebelum memanggil API, jawaban dicari di cache SQLite berdasarkan
    kunci (canonical_id, intent, hash_pesan). Bila hit & belum kedaluwarsa
    (TTL 24 jam), jawaban dikembalikan langsung tanpa API call. Hanya jawaban
    SUKSES yang di-cache; error tidak pernah disimpan. Set use_cache=False
    untuk melewati cache. cache_canonical_id/cache_intent bersifat opsional —
    bila tidak diisi, kunci tetap unik dari hash pesan + parameter.

    Failover lintas-provider: bila rute utama gagal karena kesalahan sementara
    (rate_limit / timeout / connection / provider_error), rute cadangan
    dikonfigurasi akan dicoba. Gemini 429 -> Qwen/Groq (chat teks tetap
    tersedia), Qwen/Groq 429 -> Gemini (sekaligus membawa gambar vision).
    Gambar hanya dapat dikirim ke rute multimodal; fallback tanpa gambar
    tetap berfungsi karena konteks gambar sudah terwakili transkripsi teks.
    """
    timeout = timeout or _first_env("LLM_TIMEOUT", default=DEFAULT_TIMEOUT)
    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT

    # --- Cek cache dulu (tanpa API call bila hit) ---
    cache_key = None
    if use_cache:
        _llm_cache_init()
        cache_key = _llm_cache_key(cache_canonical_id, cache_intent, model,
                                   temperature, max_tokens, messages, image_paths)
        cached = _llm_cache_get(cache_key)
        if cached is not None:
            text, c_model, c_provider = cached
            if return_meta:
                return text, {"model": c_model, "provider": c_provider, "cached": True}
            return text

    gemini_key = get_gemini_api_key()
    cloud = _first_env("OPENAI_COMPATIBLE_BASE_URL", "LLM_BASE_URL")
    cloud_keys = get_api_keys()

    want_gemini = (model and "gemini" in model.lower()) or (not model and gemini_key)
    want_qwen = ((model and "qwen" in model.lower())
                 or (not model and not gemini_key and cloud and cloud_keys))

    routes = []
    if want_gemini and gemini_key:
        routes.append("gemini")
    if (want_qwen or (cloud and cloud_keys)) and cloud:
        routes.append("qwen")
    if "gemini" not in routes and gemini_key:
        routes.append("gemini")

    last_err = None
    for i, route in enumerate(routes):
        try:
            if route == "gemini":
                model_choice = model or "gemini-flash"
                text, actual_model = _post_gemini(messages, model_choice=model_choice,
                                                  image_paths=image_paths,
                                                  temperature=temperature,
                                                  max_tokens=max_tokens, timeout=timeout)
                provider = "google_gemini"
            else:
                # Rute openai-compatible (Qwen/Groq) — teks murni, gambar tidak terkirim
                if image_paths:
                    print(f"[tutor_llm] Catatan: fallback ke provider teks — {len(image_paths)} "
                          f"gambar tidak dikirim (konteks gambar terwakili transkripsi).")
                info = {"provider": "openai_compatible", "base_url": cloud,
                        "model": _first_env("LLM_MODEL", default="qwen/qwen3.8-27b")}
                text, actual_model = _post_openai_compatible(messages, info, temperature,
                                                             max_tokens, timeout)
                provider = "openai_compatible"
            # --- Simpan jawaban sukses ke cache ---
            if cache_key:
                _llm_cache_set(cache_key, text, actual_model, provider)
            if return_meta:
                return text, {"model": actual_model, "provider": provider, "cached": False}
            return text
        except LLMError as e:
            last_err = e
            # Gagal fatal (malformed / pesan tidak layak) tidak dicoba ke provider lain
            if e.kind not in ("rate_limit", "timeout", "connection", "provider_error"):
                raise
            if i < len(routes) - 1:
                print(f"[tutor_llm] Rute {route} gagal ({e.kind}) — mencoba rute cadangan...",
                      flush=True)
            continue
    raise last_err or LLMError("Tidak ada provider LLM yang terkonfigurasi.", kind="provider_error")


def generate_with_meta(messages, **kwargs):
    """Kembalikan tuple (text, metadata) termasuk nama model yang sebenarnya merespons."""
    kwargs["return_meta"] = True
    return generate(messages, **kwargs)


# ---------------------------------------------------------------------------
# Cache jawaban LLM (SQLite, TTL 24 jam)
#
# Tiap pertanyaan identik = 1 API call penuh (mahal & lambat). Cache ini
# menyimpan jawaban sukses per kunci unik sehingga pertanyaan yang sama
# (soal + intent + pesan yang sama) dijawab instan tanpa memanggil API lagi.
# ---------------------------------------------------------------------------
LLM_CACHE_TTL_SECONDS = 24 * 3600  # 24 jam
LLM_CACHE_PATH = os.path.join(BASE_DIR, "data", "llm_cache.db")
_llm_cache_lock = threading.Lock()


def _llm_cache_key(canonical_id, intent, model, temperature, max_tokens,
                   messages, image_paths):
    """Kunci cache = SHA-256 dari (canonical_id, intent, hash_pesan, ...).

    Selain tiga komponen wajib audit (canonical_id, intent, hash_pesan),
    model/temperature/max_tokens/image_paths ikut di-hash agar kunci unik per
    konfigurasi pemanggilan penuh — mencegah cache hit yang salah (misal
    model berbeda mengembalikan jawaban dari model lain).
    """
    try:
        pesan_json = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        pesan_json = repr(messages)
    parts = [
        str(canonical_id or ""),
        str(intent or ""),
        str(model or ""),
        str(temperature),
        str(max_tokens or ""),
        pesan_json,
        json.dumps(sorted(image_paths or [])),
    ]
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def _llm_cache_init():
    """Buat file & tabel cache bila belum ada (idempoten, thread-safe)."""
    with _llm_cache_lock:
        os.makedirs(os.path.dirname(LLM_CACHE_PATH), exist_ok=True)
        conn = sqlite3.connect(LLM_CACHE_PATH, timeout=10)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS llm_cache ("
                "key TEXT PRIMARY KEY, response TEXT, created_at REAL)"
            )
            conn.commit()
        finally:
            conn.close()


def _llm_cache_delete(key):
    with _llm_cache_lock:
        try:
            conn = sqlite3.connect(LLM_CACHE_PATH, timeout=10)
            try:
                conn.execute("DELETE FROM llm_cache WHERE key=?", (key,))
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error:
            pass


def _llm_cache_get(key):
    """Ambil dari cache; kembalikan (text, model, provider) bila hit & segar.

    Entri kedaluwarsa (> TTL 24 jam) atau rusak dihapus & dianggap miss.
    """
    with _llm_cache_lock:
        try:
            conn = sqlite3.connect(LLM_CACHE_PATH, timeout=10)
            try:
                row = conn.execute(
                    "SELECT response, created_at FROM llm_cache WHERE key=?",
                    (key,),
                ).fetchone()
            finally:
                conn.close()
        except sqlite3.Error:
            return None
    if not row:
        return None
    response_json, created_at = row
    if not created_at or (time.time() - created_at) > LLM_CACHE_TTL_SECONDS:
        _llm_cache_delete(key)
        return None
    try:
        data = json.loads(response_json)
        text = data["text"]
        if not text or not text.strip():
            raise ValueError("respons kosong")
        return text, data.get("model", ""), data.get("provider", "")
    except (ValueError, KeyError, TypeError):
        _llm_cache_delete(key)
        return None


def _llm_cache_set(key, text, model, provider):
    """Simpan jawaban sukses ke cache. Kegagalan tulis TIDAK boleh menggagalkan
    pemanggilan LLM (cache bersifat best-effort)."""
    payload = json.dumps(
        {"text": text, "model": model, "provider": provider},
        ensure_ascii=False,
    )
    with _llm_cache_lock:
        try:
            conn = sqlite3.connect(LLM_CACHE_PATH, timeout=10)
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO llm_cache (key, response, created_at) "
                    "VALUES (?,?,?)",
                    (key, payload, time.time()),
                )
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error:
            pass


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
    actual_model = data.get("model") or info.get("model") or "ollama"
    return text, actual_model


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
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CBT-TKA-Tutor/1.0"}
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
            elif e.code == 404:
                # Model tidak ditemukan / tidak tersedia di provider: otomatis fallback
                for fallback_m in ("qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"):
                    if fallback_m != payload.get("model"):
                        payload["model"] = fallback_m
                        body = json.dumps(payload).encode("utf-8")
                        break
                else:
                    raise LLMError(f"Provider HTTP 404 (Model tidak ditemukan): {e.reason}", kind="provider_error", status=404)
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
    raw_m = str(data.get("model") or payload.get("model") or info.get("model") or "qwen").lower()
    actual_model = "Qwen 2.5 27B" if "qwen" in raw_m else (data.get("model") or payload.get("model") or "AI Model")
    return text, actual_model


GEMINI_FLASH_CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]

GEMINI_PRO_CANDIDATES = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]


def _gemini_default_max_tokens():
    """Batas token keluaran default Gemini: 2048 (hemat biaya/latensi).

    Default lama 16384 terlalu boros untuk jawaban tutor yang ringkas.
    Dapat dioverride via env LLM_GEMINI_MAX_TOKENS; argumen max_tokens
    eksplisit selalu menang.
    """
    try:
        return int(os.environ.get("LLM_GEMINI_MAX_TOKENS", "2048"))
    except ValueError:
        return 2048


def _post_gemini(messages, model_choice="gemini-3.8-flash", image_paths=None, temperature=0.7, max_tokens=None, timeout=120):
    """Kirim percakapan + gambar diagram visual ke Google Gemini API dengan auto-failover multi-model & key rotation."""
    import base64
    import mimetypes

    keys = get_gemini_api_keys()
    if not keys:
        raise LLMError("GEMINI_API_KEY belum dikonfigurasi di .env", kind="provider_error")

    parts = []

    # 1. Lampirkan gambar visual diagram lokal (multimodal)
    if image_paths:
        for p in image_paths:
            if os.path.isfile(p):
                try:
                    mime, _ = mimetypes.guess_type(p)
                    mime = mime or "image/png"
                    with open(p, "rb") as img_f:
                        img_b64 = base64.b64encode(img_f.read()).decode("utf-8")
                    parts.append({
                        "inline_data": {
                            "mime_type": mime,
                            "data": img_b64
                        }
                    })
                except Exception as ex:
                    print(f"[tutor_llm] Warning: Gagal membaca gambar {p}: {ex}")

    # 2. Susun prompt teks lengkap
    full_prompt_chunks = []
    for m in messages:
        role = m.get("role", "user")
        content = (m.get("content") or "").strip()
        if not content:
            continue
        if role == "system":
            full_prompt_chunks.append(f"{content}\n")
        elif role == "user":
            full_prompt_chunks.append(f"Siswa: {content}")
        elif role == "assistant":
            full_prompt_chunks.append(f"Tutor: {content}")

    full_prompt = "\n\n".join(full_prompt_chunks).strip()
    parts.append({"text": full_prompt})

    out_tokens = max_tokens or _gemini_default_max_tokens()
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": float(temperature),
            "maxOutputTokens": out_tokens,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }
    req_body = json.dumps(payload).encode("utf-8")

    models_to_try = [model_choice] if model_choice else []
    for m in GEMINI_FLASH_CANDIDATES:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        max_attempts = max(3, len(keys))

        for attempt in range(max_attempts):
            gemini_key = next_gemini_api_key()
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": gemini_key,
                "User-Agent": "CBT-TKA-Tutor/1.0"
            }
            req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")

            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    cands = data.get("candidates", [])
                    if not cands:
                        raise LLMError(f"Gemini ({model_name}) tidak memberikan respons.", kind="provider_error")

                    cand = cands[0]
                    content_parts = cand.get("content", {}).get("parts", [])
                    text_pieces = [p.get("text", "") for p in content_parts if "text" in p]
                    text = "".join(text_pieces).strip()
                    text = _clean_think(text)
                    if not text:
                        raise LLMError(f"Gemini ({model_name}) mengembalikan respons teks kosong.", kind="malformed")

                    human_model_name = f"Gemini {model_name.replace('gemini-', '').replace('-', ' ').title()}"
                    return text, human_model_name
            except urllib.error.HTTPError as e:
                last_error = e
                err_body = ""
                try:
                    err_body = e.read().decode("utf-8", errors="ignore")
                except Exception:
                    pass

                if e.code in (429, 503):
                    delay = 3.0
                    m_delay = re.search(r'"retryDelay":\s*"(\d+)s"', err_body)
                    if m_delay:
                        delay = float(m_delay.group(1))
                    mark_gemini_key_rate_limited(gemini_key, cooldown_seconds=int(delay) + 2)
                    # Jika 429 quota habis permanen untuk model ini, langsung coba model berikutnya
                    if "exceeded your current quota" in err_body:
                        break
                    time.sleep(min(delay, 5.0))
                    continue
                elif e.code == 404:
                    # Model tidak tersedia, coba kandidat model berikutnya
                    break
                else:
                    raise LLMError(f"Gemini API HTTP {e.code}: {e.reason}", kind="provider_error", status=e.code)
            except urllib.error.URLError as e:
                raise LLMError(f"Tidak dapat menghubungi Google Gemini API: {e.reason}", kind="connection")
            except TimeoutError:
                raise LLMError("Permintaan ke Google Gemini API timeout.", kind="timeout")
            except json.JSONDecodeError:
                raise LLMError("Respons Google Gemini API bukan JSON valid.", kind="malformed")

    if last_error:
        if last_error.code == 429:
            raise LLMError("Batas kecepatan Google Gemini API tercapai sementara pada semua model.", kind="rate_limit", status=429)
        raise LLMError(f"Google Gemini gagal ({last_error.code}): {last_error.reason}", kind="provider_error", status=last_error.code)
    raise LLMError("Seluruh model Google Gemini Flash gagal merespons.", kind="provider_error")


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
