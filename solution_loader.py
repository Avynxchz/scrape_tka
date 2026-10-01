# -*- coding: utf-8 -*-
"""solution_loader.py — Loader sumber Layer 3 (solusi Claude) per paket.

Aturan yang dijaga modul ini:
  1. Kunci jawaban OTORITATIF (canonical/kunci evidence) TETAP satu-satunya
     kebenaran untuk grading. Field `official_answer` pada file solusi Claude
     hanya untuk CROSS-CHECK: cocok -> integrasi normal; beda -> kunci
     otoritatif dipertahankan dan mismatch di-flag (tidak pernah direkonsiliasi
     diam-diam, tidak pernah menimpa kunci).
  2. `needs_manual_review` dari file sumber dipertahankan apa adanya.
  3. Sumber solusi dapat diganti cukup dengan mengubah registry.json — tanpa
     mengubah kode frontend, tanpa menggabungkan isi sumber.
  4. Konten solusi TIDAK pernah diedit/diregenerasi di sini — murni dibaca.
"""

import json
import os
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOLUTION_DIR = os.path.join(BASE_DIR, "data", "solution_sources")
REGISTRY_PATH = os.path.join(SOLUTION_DIR, "registry.json")

_lock = threading.Lock()
_registry_cache = None
_source_cache = {}


def _normalize_slug(subject, paket):
    slug_map = {
        ("matematika", 1): "mtk_paket_1",
        ("matematika", 2): "mtk_paket_2",
        ("bahasa_inggris", 1): "bing_paket_1",
        ("bahasa_inggris", 2): "bing_paket_2",
        ("ekonomi", 1): "eko_paket_1",
        ("ekonomi", 2): "eko_paket_2",
        ("kewirausahaan", 1): "pkw_paket_1",
        ("kewirausahaan", 2): "pkw_paket_2",
        ("geografi", 1): "geo_paket_1",
        ("geografi", 2): "geo_paket_2",
        ("fisika", 1): "fisika_paket_1",
        ("fisika", 2): "fisika_paket_2",
        ("kimia", 1): "kim_paket_1",
        ("kimia", 2): "kim_paket_2",
        ("biologi", 1): "bio_paket_1",
        ("biologi", 2): "bio_paket_2",
    }
    p = int(paket) if paket is not None else 1
    if (subject, p) in slug_map:
        return slug_map[(subject, p)]
    return f"{subject}_paket_{p}"


def load_registry():
    """Baca registry.json (dengan cache; reload otomatis bila file berubah)."""
    global _registry_cache
    with _lock:
        try:
            mtime = os.path.getmtime(REGISTRY_PATH)
        except OSError:
            return {}
        if _registry_cache is None or _registry_cache.get("_mtime") != mtime:
            with open(REGISTRY_PATH, encoding="utf-8") as f:
                data = json.load(f)
            data["_mtime"] = mtime
            _registry_cache = data
    # jangan bocorkan kunci internal '_mtime'
    return {k: v for k, v in _registry_cache.items() if not k.startswith("_")}


def set_active_source(subject, paket, filename):
    """Ganti sumber aktif untuk satu paket (menulis registry.json)."""
    slug = _normalize_slug(subject, paket)
    p = int(paket) if paket is not None else 1
    canonical_slug = f"{subject}_paket_{p}"
    if not slug:
        raise ValueError(f"Subject/paket tidak dikenal: {subject} paket {paket}")
    if not os.path.isfile(os.path.join(SOLUTION_DIR, filename)):
        raise FileNotFoundError(f"File sumber tidak ada: {filename}")
    with _lock:
        try:
            with open(REGISTRY_PATH, encoding="utf-8") as f:
                reg = json.load(f)
        except FileNotFoundError:
            reg = {}
        reg.setdefault(slug, {})["active_source"] = filename
        reg.setdefault(canonical_slug, {})["active_source"] = filename
        tmp = REGISTRY_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
        os.replace(tmp, REGISTRY_PATH)
        global _registry_cache
        _registry_cache = None
        _source_cache.pop((subject, int(paket)), None)
    return load_registry()


def resolve_active_source(subject, paket):
    """Kembalikan path file sumber aktif utk paket, atau None bila tidak ada."""
    slug = _normalize_slug(subject, paket)
    p = int(paket) if paket is not None else 1
    canonical_slug = f"{subject}_paket_{p}"
    if not slug and not canonical_slug:
        return None
    reg = load_registry()
    entry = reg.get(slug) or reg.get(canonical_slug) or {}
    fname = entry.get("active_source")
    if not fname:
        return None
    path = os.path.join(SOLUTION_DIR, fname)
    return path if os.path.isfile(path) else None


def validate_solution_doc(doc):
    """Validasi struktur file sumber solusi. Raise ValueError bila tidak sah."""
    if not isinstance(doc, dict):
        raise ValueError("File solusi harus objek JSON")
    if "solutions" not in doc or not isinstance(doc["solutions"], list):
        raise ValueError("File solusi harus punya array 'solutions'")
    seen = set()
    for s in doc["solutions"]:
        qid = s.get("question_id")
        qnum = s.get("question_number")
        if not qid or qnum is None:
            raise ValueError(f"Solusi tanpa question_id/question_number: {s}")
        if qid in seen:
            raise ValueError(f"Duplikat question_id: {qid}")
        seen.add(qid)
        for field in ("concept_kunci", "glossary", "reasoning", "steps",
                      "why_correct", "tips", "common_mistakes"):
            if field not in s:
                raise ValueError(f"{qid}: field Layer 3 '{field}' hilang")
    return True


def load_solution_doc(subject, paket):
    """Muat dokumen sumber aktif utk paket. Return (doc, meta) atau (None, alasan)."""
    path = resolve_active_source(subject, paket)
    if not path:
        return None, "tidak ada sumber aktif di registry"
    key = (subject, int(paket))
    mtime = os.path.getmtime(path)
    cached = _source_cache.get(key)
    if cached and cached.get("_path") == path and cached["_mtime"] == mtime:
        return cached["doc"], cached["meta"]
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    validate_solution_doc(doc)
    meta = {
        "source_file": os.path.basename(path),
        "package": doc.get("package"),
        "subject": doc.get("subject"),
        "provider": "Claude",          # metadata dinormalisasi di registry level
        "model": doc.get("model"),     # hanya diisi bila file sumber memang memuatnya
    }
    _source_cache[key] = {"doc": doc, "meta": meta, "_mtime": mtime, "_path": path}
    return doc, meta


def _extract_normalized_answer_set(val):
    """Mengekstraksi himpunan string terstandarisasi dari format string, list, atau dict."""
    if val is None:
        return set()
    if isinstance(val, dict):
        if "correct" in val:
            return _extract_normalized_answer_set(val["correct"])
        return {f"{k.upper()}:{str(v).upper()}" for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        res = set()
        for x in val:
            res.update(_extract_normalized_answer_set(x))
        return res
    s = str(val).strip()
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
        try:
            import ast
            parsed = ast.literal_eval(s)
            return _extract_normalized_answer_set(parsed)
        except Exception:
            pass
    import re
    parts = [p.strip().upper() for p in re.split(r"[,;\n]+", s) if p.strip()]
    cleaned = set()
    for p in parts:
        p = re.sub(r"[\(\)\[\]\'\"]", "", p).strip()
        # Normalisasi variasi 'A (Benar)' -> 'A:BENAR'
        if " " in p and not (":" in p):
            subparts = p.split()
            if len(subparts) == 2 and subparts[1] in ("BENAR", "SALAH", "TEPAT", "TIDAK_TEPAT"):
                p = f"{subparts[0]}:{subparts[1]}"
        if p and p not in ("-", ""):
            cleaned.add(p)
    return cleaned


def cross_check_keys(solution_entry, authoritative):
    """Bandingkan kunci Claude vs kunci otoritatif.

    Return dict: match (bool), detail (str), authoritative (selalu nilai otoritatif).
    TIDAK pernah mengubah kunci otoritatif — hasil hanya untuk flag/audit.
    """
    oa = solution_entry.get("official_answer")
    claude_set = _extract_normalized_answer_set(oa)
    auth_set = _extract_normalized_answer_set(authoritative)

    if not auth_set:
        return {"match": True, "authoritative": authoritative, "detail": "kunci otoritatif kosong/tidak dicek"}

    # Normalisasi format jika satu sisi pakai 'A:BENAR' dan sisi lain format per_statement
    # Bandingkan himpunan
    if claude_set != auth_set:
        return {
            "match": False,
            "authoritative": authoritative,
            "detail": f"kunci otoritatif {sorted(auth_set)} vs Claude {sorted(claude_set)}"
        }
    return {"match": True, "authoritative": authoritative, "detail": "kunci cocok"}


def get_solution(subject, paket, nomor, authoritative_display=None):
    """Ambil solusi Layer 3 satu soal dari sumber aktif.

    Return None bila sumber/soal tidak ada. Field hasil:
      question_id, question_number, fields..., review{needs_manual_review,
      review_reason}, key_crosscheck{match, detail, authoritative}, source{...}
    """
    doc, _meta = load_solution_doc(subject, paket)
    if not doc:
        return None
    for s in doc.get("solutions", []):
        if s.get("question_number") == nomor or s.get("question_id", "").endswith(f"_q{nomor:02d}"):
            cc = None
            if authoritative_display is not None:
                cc = cross_check_keys(s, authoritative_display)
            return {
                "question_id": s["question_id"],
                "question_number": s["question_number"],
                "diketahui": s.get("diketahui"),
                "ditanyakan": s.get("ditanyakan"),
                "concept_kunci": s.get("concept_kunci") or [],
                "glossary": s.get("glossary") or [],
                "reasoning": s.get("reasoning") or "",
                "steps": s.get("steps") or [],
                "why_correct": s.get("why_correct") or "",
                "common_mistakes": s.get("common_mistakes") or [],
                "tips": s.get("tips") or [],
                "review": {
                    "needs_manual_review": bool(s.get("needs_manual_review")),
                    "review_reason": s.get("review_reason"),
                },
                "key_crosscheck": cc,
                "source": {
                    "file": _meta.get("source_file"),
                    "provider": _meta.get("provider"),
                    "model": _meta.get("model"),
                },
            }
    return None


def list_available_sources():
    """Daftar file sumber yang tersimpan (untuk audit/switch manual)."""
    if not os.path.isdir(SOLUTION_DIR):
        return []
    return sorted(
        f for f in os.listdir(SOLUTION_DIR)
        if f.endswith(".json") and f != "registry.json"
    )
