# -*- coding: utf-8 -*-
"""autopsy/coach.py — Layanan Guru Autopsi AI (FASE A3).

Alur:
1. Evidence pack (coach_input_v1) -> Rakit prompt dengan persona coach_prompt_v1.txt.
2. Panggil LLM via tutor_llm dengan timeout ketat (25s), model COACH_MODEL, 1 retry.
3. Circuit breaker sederhana saat provider gagal berturut-turut.
4. Validasi ketat Bagian 6.3.
5. Jika valid -> sumber: "ai". Jika gagal di mana pun -> fallback ke coach_template (sumber: "template").
6. Catat metrik (latensi, token, sumber, alasan gagal) tanpa data pribadi.
"""

import json
import os
import re
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import tutor_llm
from autopsy import coach_template

PROMPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coach_prompt_v1.txt")

FORBIDDEN_WORDS = [
    "bodoh", "malas", "goblok", "payah", "pasti lolos", "pasti naik",
    "sombong", "hopeless", "tidak mampu", "tolol"
]

ALLOWED_ROOT_KEYS = {
    "versi", "sapaan", "penilaian", "pengamatan", "sudah_bagus",
    "kebocoran", "per_soal", "misi", "rencana", "penutup", "catatan_data"
}

ALLOWED_PENYEBAB = {"overthinking", "terburu", "konsep", "rapuh", "macet", "kosong"}

# Circuit breaker state
_circuit_failures = 0
_circuit_open_until = 0.0


def _load_system_prompt():
    if os.path.isfile(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "Kamu adalah Guru Autopsi: guru privat kelas atas persiapan TKA SMA."


def _extract_numbers_from_obj(obj):
    """Kumpulkan semua angka dari objek JSON evidence."""
    numbers = set()
    s = json.dumps(obj)
    for m in re.findall(r"\b\d+\b", s):
        numbers.add(int(m))
    return numbers


def validate_coach_output(data, evidence):
    """Validasi ketat keluaran Guru AI sesuai Bagian 6.3.

    Return (ok: bool, reason: str).
    """
    if not isinstance(data, dict):
        return False, "Output bukan objek JSON"

    # 1. Cek versi
    if data.get("versi") != "coach_output_v1":
        return False, f"Versi salah: {data.get('versi')}"

    # 2. Cek key asing
    extra_keys = set(data.keys()) - ALLOWED_ROOT_KEYS - {"sumber"}
    if extra_keys:
        return False, f"Terdapat key tidak dikenal: {extra_keys}"

    # 3. Batas panjang string utama
    if len(str(data.get("sapaan") or "")) > 140:
        return False, "Sapaan melebihi 140 karakter"
    if len(str(data.get("penilaian") or "")) > 260:
        return False, "Penilaian melebihi 260 karakter"
    if len(str(data.get("sudah_bagus") or "")) > 160:
        return False, "Sudah_bagus melebihi 160 karakter"
    if len(str(data.get("penutup") or "")) > 140:
        return False, "Penutup melebihi 140 karakter"
    if len(str(data.get("catatan_data") or "")) > 160:
        return False, "Catatan_data melebihi 160 karakter"

    # 4. Pengamatan (2-5 butir, masing-masing <= 220)
    pengamatan = data.get("pengamatan")
    if not isinstance(pengamatan, list) or not (2 <= len(pengamatan) <= 5):
        return False, f"Pengamatan harus 2-5 butir (aktual: {len(pengamatan) if isinstance(pengamatan, list) else 'bukan list'})"
    for p in pengamatan:
        if len(str(p)) > 220:
            return False, f"Butir pengamatan melebihi 220 karakter: {p[:30]}..."

    # 5. Kebocoran (maks 3)
    kebocoran = data.get("kebocoran")
    if not isinstance(kebocoran, list) or len(kebocoran) > 3:
        return False, "Kebocoran harus list maks 3 item"
    for k in kebocoran:
        if not isinstance(k, dict):
            return False, "Item kebocoran bukan dict"
        if len(str(k.get("judul") or "")) > 60:
            return False, "Judul kebocoran melebihi 60 karakter"
        if len(str(k.get("bukti") or "")) > 200:
            return False, "Bukti kebocoran melebihi 200 karakter"
        if len(str(k.get("tafsir") or "")) > 200:
            return False, "Tafsir kebocoran melebihi 200 karakter"
        if len(str(k.get("tindakan") or "")) > 160:
            return False, "Tindakan kebocoran melebihi 160 karakter"

    # 6. Fokus soal & per_soal (maks 6)
    valid_no = {q["no"] for q in (evidence.get("fokus_soal") or [])}
    per_soal = data.get("per_soal")
    if not isinstance(per_soal, list) or len(per_soal) > 6:
        return False, "Per_soal harus list maks 6 item"
    for ps in per_soal:
        if not isinstance(ps, dict):
            return False, "Item per_soal bukan dict"
        q_no = ps.get("no")
        if valid_no and q_no not in valid_no:
            return False, f"Nomor soal {q_no} tidak ada di fokus_soal {valid_no}"
        if ps.get("penyebab") not in ALLOWED_PENYEBAB:
            return False, f"Penyebab '{ps.get('penyebab')}' tidak dikenal"
        if len(str(ps.get("dipelajari") or "")) > 160:
            return False, f"Dipelajari soal {q_no} melebihi 160 karakter"
        langkah = ps.get("langkah")
        if not isinstance(langkah, list) or not (1 <= len(langkah) <= 3):
            return False, f"Langkah soal {q_no} harus 1-3 butir"
        for l in langkah:
            if len(str(l)) > 120:
                return False, f"Butir langkah soal {q_no} melebihi 120 karakter"
        if len(str(ps.get("cek_paham") or "")) > 140:
            return False, f"Cek_paham soal {q_no} melebihi 140 karakter"

    # 7. Misi & kandidat tugas
    misi = data.get("misi")
    if not isinstance(misi, dict):
        return False, "Misi harus objek dict"
    if len(str(misi.get("pembuka") or "")) > 140:
        return False, "Pembuka misi melebihi 140 karakter"
    valid_tasks = {t["task_id"] for t in (evidence.get("kandidat_tugas") or [])}
    task_ids = misi.get("task_ids") or []
    if not isinstance(task_ids, list) or not task_ids:
        return False, "Task_ids misi harus list tidak kosong"
    for tid in task_ids:
        if valid_tasks and tid not in valid_tasks:
            return False, f"Task_id '{tid}' tidak ada di kandidat_tugas {valid_tasks}"

    # 8. Rencana (harus list)
    rencana = data.get("rencana")
    if rencana is not None and not isinstance(rencana, list):
        return False, "Rencana harus berupa list"

    # 8. Kata terlarang
    all_text = json.dumps(data, ensure_ascii=False).lower()
    for bad in FORBIDDEN_WORDS:
        if bad in all_text:
            return False, f"Mengandung kata terlarang '{bad}'"

    # 9. Bahasa Indonesia (cek indikator kata umum)
    indo_markers = {"kamu", "soal", "di", "dan", "untuk", "yang", "jawaban", "detik", "pada", "ini"}
    words = set(re.findall(r"[a-zA-Z]+", all_text.lower()))
    if len(words.intersection(indo_markers)) < 3:
        return False, "Teks tidak terdeteksi sebagai bahasa Indonesia yang wajar"

    # 10. Angka tak dikenal (toleransi maksimal 2 angka di luar evidence)
    ev_numbers = _extract_numbers_from_obj(evidence)
    # Toleransi angka urutan kecil (1 s.d. 5)
    ev_numbers.update({1, 2, 3, 4, 5, 10, 15})
    output_numbers = set(int(m) for m in re.findall(r"\b\d+\b", all_text))
    unknown_numbers = output_numbers - ev_numbers
    if len(unknown_numbers) > 2:
        return False, f"Terlalu banyak angka tidak dikenal di luar data: {unknown_numbers}"

    # 11. Validasi Halusinasi Skor & Jumlah Soal Benar/Salah (K1)
    ev_skor_pct = evidence.get("skor_pct")
    ev_n_benar = evidence.get("n_benar")
    ev_n_salah = evidence.get("n_salah")
    if ev_n_salah is None and evidence.get("n_soal") is not None and ev_n_benar is not None:
        try:
            ev_n_salah = int(evidence.get("n_soal")) - int(ev_n_benar)
        except (ValueError, TypeError):
            pass

    if ev_skor_pct is not None:
        try:
            ev_skor_pct = int(round(float(ev_skor_pct)))
        except (ValueError, TypeError):
            ev_skor_pct = None

    if ev_n_benar is not None:
        try:
            ev_n_benar = int(ev_n_benar)
        except (ValueError, TypeError):
            ev_n_benar = None

    if ev_n_salah is not None:
        try:
            ev_n_salah = int(ev_n_salah)
        except (ValueError, TypeError):
            ev_n_salah = None

    narrative_parts = []
    for k in ["sapaan", "penilaian", "sudah_bagus", "penutup", "catatan_data"]:
        if data.get(k):
            narrative_parts.append(str(data[k]))
    for p in (data.get("pengamatan") or []):
        narrative_parts.append(str(p))
    for kb in (data.get("kebocoran") or []):
        if isinstance(kb, dict):
            for f in ["judul", "bukti", "tafsir", "tindakan"]:
                if kb.get(f):
                    narrative_parts.append(str(kb[f]))
    for ps in (data.get("per_soal") or []):
        if isinstance(ps, dict):
            for f in ["dipelajari", "cek_paham"]:
                if ps.get(f):
                    narrative_parts.append(str(ps[f]))
            for l in (ps.get("langkah") or []):
                narrative_parts.append(str(l))
    if isinstance(data.get("misi"), dict) and data["misi"].get("pembuka"):
        narrative_parts.append(str(data["misi"]["pembuka"]))

    narrative_text = " ".join(narrative_parts).lower()

    # 11a. Cek pola "Skor X%" atau "skor X%"
    if ev_skor_pct is not None:
        for sm in re.finditer(r"\bskor(?:mu)?\b[^\d%]{0,15}(\d+)\s*%", narrative_text):
            claimed_skor = int(sm.group(1))
            if claimed_skor != ev_skor_pct:
                return False, f"Halusinasi skor: output menyebut Skor {claimed_skor}% padahal evidence skor_pct={ev_skor_pct}"

    # 11b. Cek pola "Y soal salah" atau "Y salah"
    if ev_n_salah is not None:
        for sm in re.finditer(r"\b(\d+)\s+(?:butir\s+|nomor\s+)?(?:soal\s+)?salah\b", narrative_text):
            claimed_salah = int(sm.group(1))
            if claimed_salah != ev_n_salah:
                return False, f"Halusinasi jumlah salah: output menyebut {claimed_salah} salah padahal evidence n_salah={ev_n_salah}"
        for sm in re.finditer(r"(?:jawaban\s+)?salah\s*:\s*(\d+)\b", narrative_text):
            claimed_salah = int(sm.group(1))
            if claimed_salah != ev_n_salah:
                return False, f"Halusinasi jumlah salah: output menyebut {claimed_salah} salah padahal evidence n_salah={ev_n_salah}"

    # 11c. Cek pola "Z soal benar" atau "Z benar"
    if ev_n_benar is not None:
        for bm in re.finditer(r"\b(\d+)\s+(?:butir\s+|nomor\s+)?(?:soal\s+)?benar\b", narrative_text):
            claimed_benar = int(bm.group(1))
            if claimed_benar != ev_n_benar:
                return False, f"Halusinasi jumlah benar: output menyebut {claimed_benar} benar padahal evidence n_benar={ev_n_benar}"
        for bm in re.finditer(r"(?:jawaban\s+)?benar\s*:\s*(\d+)\b", narrative_text):
            claimed_benar = int(bm.group(1))
            if claimed_benar != ev_n_benar:
                return False, f"Halusinasi jumlah benar: output menyebut {claimed_benar} benar padahal evidence n_benar={ev_n_benar}"

    return True, ""


def _parse_llm_json(raw_text):
    """Bersihkan dan parse output JSON dari LLM."""
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    # Buang markdown codeblock
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # Cari kurung kurawal pertama dan terakhir jika ada teks pembungkus
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1:
        cleaned = cleaned[first_brace:last_brace + 1]

    try:
        return json.loads(cleaned)
    except Exception:
        return None


def generate_coach(evidence, model=None, timeout=None, max_tokens=None):
    """Panggil LLM Guru Autopsi dengan retry, timeout, dan fallback template.

    Return (output: dict, meta: dict).
    """
    global _circuit_failures, _circuit_open_until

    start_time = time.time()
    coach_model = model or os.environ.get("COACH_MODEL") or os.environ.get("LLM_MODEL")
    coach_timeout = float(timeout or os.environ.get("COACH_TIMEOUT_S") or 25.0)
    coach_max_tokens = int(max_tokens or os.environ.get("COACH_MAX_OUTPUT_TOKENS") or 1000)

    # 1. Cek circuit breaker
    now = time.time()
    if now < _circuit_open_until:
        tmpl = coach_template.generate_template(evidence)
        tmpl["sumber"] = "template"
        return tmpl, {
            "latensi_ms": round((time.time() - start_time) * 1000),
            "sumber": "template",
            "alasan": "circuit_breaker_active",
            "model": "template",
        }

    system_prompt = _load_system_prompt()
    user_payload_str = json.dumps(evidence, ensure_ascii=False)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Input data murid:\n{user_payload_str}"},
    ]

    llm_out = None
    actual_model = coach_model or "unknown"
    error_reason = ""

    # Panggilan LLM dengan 1 retry
    for attempt_idx in range(2):
        try:
            raw_text, meta = tutor_llm.generate_with_meta(
                messages,
                model=coach_model,
                temperature=0.3,
                max_tokens=coach_max_tokens,
                timeout=coach_timeout,
            )
            actual_model = meta.get("model") or actual_model
            parsed = _parse_llm_json(raw_text)
            if not parsed:
                error_reason = "json_parse_error"
                continue

            # Validasi output
            is_valid, val_reason = validate_coach_output(parsed, evidence)
            if is_valid:
                parsed["sumber"] = "ai"
                _circuit_failures = 0  # reset circuit breaker
                latency_ms = round((time.time() - start_time) * 1000)
                return parsed, {
                    "latensi_ms": latency_ms,
                    "sumber": "ai",
                    "model": actual_model,
                    "alasan": "",
                }
            else:
                error_reason = f"validation_error: {val_reason}"
        except tutor_llm.LLMError as e:
            error_reason = f"llm_error_{e.kind}"
        except Exception as ex:
            error_reason = f"exception_{type(ex).__name__}"

    # Jika gagal 2x -> catat kegagalan ke circuit breaker
    _circuit_failures += 1
    if _circuit_failures >= 3:
        _circuit_open_until = time.time() + 60.0  # buka circuit breaker 60 detik

    # Fallback ke template cadangan
    tmpl = coach_template.generate_template(evidence)
    tmpl["sumber"] = "template"
    latency_ms = round((time.time() - start_time) * 1000)
    return tmpl, {
        "latensi_ms": latency_ms,
        "sumber": "template",
        "alasan": error_reason,
        "model": actual_model,
    }
