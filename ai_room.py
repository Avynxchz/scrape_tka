# -*- coding: utf-8 -*-
"""ai_room.py — Backend Layanan AI Room per Mapel (FASE D2 + D3).

Menyediakan:
1. Agregasi data performa & perilaku user di satu mapel (tanpa kirim raw items).
2. Deteksi topik terlemah, topik terkuat, dan pola belajar (waktu, ragu, ganti).
3. System prompt per mapel dengan konteks agregat + 5 soal terakhir yang salah.
4. Integrasi LLM coach via tutor_llm tanpa memotong kuota AI Tutor per-soal.
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import tutor_llm

# Peta nama tampilan mapel
MAPEL_DISPLAY_NAMES = {
    "matematika": "Matematika",
    "matematika_lanjut": "Matematika Tingkat Lanjut",
    "bahasa_indonesia": "Bahasa Indonesia",
    "bahasa_indonesia_lanjut": "Bahasa Indonesia Tingkat Lanjut",
    "bahasa_inggris": "Bahasa Inggris",
    "bahasa_inggris_lanjut": "Bahasa Inggris Tingkat Lanjut",
    "fisika": "Fisika",
    "kimia": "Kimia",
    "biologi": "Biologi",
    "ekonomi": "Ekonomi",
    "geografi": "Geografi",
    "sosiologi": "Sosiologi",
    "sejarah": "Sejarah",
    "ppkn": "PPKN",
    "antropologi": "Antropologi",
    "bahasa_arab": "Bahasa Arab",
    "bahasa_jepang": "Bahasa Jepang",
    "bahasa_jerman": "Bahasa Jerman",
    "bahasa_korea": "Bahasa Korea",
    "bahasa_mandarin": "Bahasa Mandarin",
    "bahasa_prancis": "Bahasa Prancis",
    "kewirausahaan": "Kewirausahaan",
    "akuntansi": "Akuntansi",
    "teknik_mesin": "Teknik Mesin",
    "teknik_otomotif": "Teknik Otomotif",
    "teknik_jaringan": "Teknik Jaringan Komputer",
    "manajemen_perkantoran": "Manajemen Perkantoran",
}

_KUNCI_CACHE = {}
_QUESTION_CACHE = {}


def get_mapel_display_name(mapel_slug):
    """Kembalikan nama mapel yang ramah pembaca."""
    slug = str(mapel_slug or "").strip().lower().replace("-", "_")
    if slug in MAPEL_DISPLAY_NAMES:
        return MAPEL_DISPLAY_NAMES[slug]
    return slug.replace("_", " ").title()


def load_kunci_mapel(mapel_slug, paket=1):
    """Muat kunci jawaban untuk mapel dan paket tertentu."""
    slug = str(mapel_slug or "").strip().lower().replace("-", "_")
    key = f"{slug}_{paket}"
    if key in _KUNCI_CACHE:
        return _KUNCI_CACHE[key]

    kunci_map = {}
    # Coba muat dari data/kunci/<mapel>_paket_<paket>_kunci.json
    kunci_file = os.path.join(BASE_DIR, "data", "kunci", f"{slug}_paket_{paket}_kunci.json")
    if os.path.isfile(kunci_file):
        try:
            with open(kunci_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                kunci_pg = data.get("kunci_pg") or {}
                for k, v in kunci_pg.items():
                    kunci_map[str(k)] = v
        except Exception:
            pass

    # Fallback: jika tidak ada di data/kunci, cari dari data/<mapel>_paket_<paket>_learning.json
    if not kunci_map:
        learning_file = os.path.join(BASE_DIR, "data", f"{slug}_paket_{paket}_learning.json")
        if os.path.isfile(learning_file):
            try:
                with open(learning_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for q in (data.get("soal") or []):
                        no = str(q.get("nomor") or "")
                        if no and "kunci_jawaban" in q:
                            kunci_map[no] = q.get("kunci_jawaban")
            except Exception:
                pass

    _KUNCI_CACHE[key] = kunci_map
    return kunci_map


def load_question_details(mapel_slug, paket=1, nomor=1):
    """Ambil ringkasan teks soal dan topik dari learning.json."""
    slug = str(mapel_slug or "").strip().lower().replace("-", "_")
    cache_key = f"{slug}_{paket}"
    if cache_key not in _QUESTION_CACHE:
        learning_file = os.path.join(BASE_DIR, "data", f"{slug}_paket_{paket}_learning.json")
        q_map = {}
        if os.path.isfile(learning_file):
            try:
                with open(learning_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for q in (data.get("soal") or []):
                        no = int(q.get("nomor") or 0)
                        stim = (q.get("stimulus") or {}).get("text") or ""
                        pert = (q.get("pertanyaan") or {}).get("text") or ""
                        txt = (stim + " " + pert).strip()
                        q_map[no] = {
                            "snippet": (txt[:140] + "...") if len(txt) > 140 else txt,
                            "topik": q.get("topik") or q.get("tipe_soal") or "Umum"
                        }
            except Exception:
                pass
        _QUESTION_CACHE[cache_key] = q_map

    return _QUESTION_CACHE[cache_key].get(int(nomor)) or {"snippet": "", "topik": "Umum"}


def is_answer_correct(item, mapel_slug, paket=1):
    """Evaluasi apakah jawaban user benar secara deterministik."""
    if item.get("is_correct") is not None:
        return bool(item.get("is_correct"))

    user_ans = item.get("final_answer")
    if user_ans in (None, ""):
        return False

    pos = str(item.get("position") or "")
    kunci_map = load_kunci_mapel(mapel_slug, paket)
    kunci = kunci_map.get(pos)
    if kunci is None:
        # Jika kunci tidak ditemukan di mapel_paket, return False default
        return False

    if isinstance(kunci, list):
        # PG Kompleks
        if isinstance(user_ans, list):
            return sorted(str(x).strip().upper() for x in user_ans) == sorted(str(x).strip().upper() for x in kunci)
        user_parts = [x.strip().upper() for x in str(user_ans).split(",") if x.strip()]
        return sorted(user_parts) == sorted(str(x).strip().upper() for x in kunci)

    return str(user_ans).strip().upper() == str(kunci).strip().upper()


def calculate_mapel_aggregates(attempts, mapel_slug, is_guest=False):
    """Hitung agregat performa user untuk satu mapel (D2).
    
    TIDAK mengembalikan raw items agar privasi dan bandwidth optimal.
    """
    clean_mapel = str(mapel_slug or "").strip().lower().replace("-", "_")
    total_soal = 0
    total_benar = 0
    total_waktu_s = 0

    topic_stats = {}  # topic -> { "total": int, "benar": int }

    salah_soal_lama = 0   # salah di soal > 60 detik
    salah_soal_cepat = 0  # salah di soal < 15 detik
    total_salah = 0
    ragu_salah = 0
    ganti_salah = 0

    for att in (attempts or []):
        items = att.get("items") or []
        att_paket = int(att.get("paket") or 1)
        for it in items:
            final_ans = it.get("final_answer")
            if final_ans in (None, ""):
                continue

            total_soal += 1
            waktu_detik = int(it.get("waktu_detik") if it.get("waktu_detik") is not None
                              else round((it.get("active_ms") or 0) / 1000))
            total_waktu_s += max(0, waktu_detik)

            # Topik soal
            pos = int(it.get("position") or 0)
            topic = str(it.get("topic_id") or it.get("topik") or "").strip()
            if not topic:
                q_info = load_question_details(clean_mapel, att_paket, pos)
                topic = str(q_info.get("topik") or "Umum").strip()
            if not topic:
                topic = "Umum"

            if topic not in topic_stats:
                topic_stats[topic] = {"total": 0, "benar": 0}
            topic_stats[topic]["total"] += 1

            corr = is_answer_correct(it, clean_mapel, att_paket)
            if corr:
                total_benar += 1
                topic_stats[topic]["benar"] += 1
            else:
                total_salah += 1
                if waktu_detik > 60:
                    salah_soal_lama += 1
                elif waktu_detik < 15:
                    salah_soal_cepat += 1
                if it.get("ragu") or it.get("flagged_ragu"):
                    ragu_salah += 1
                if (it.get("ganti_jawaban") or it.get("change_count") or 0) > 0:
                    ganti_salah += 1

    # Akurasi dan waktu rata-rata
    akurasi = round((total_benar / total_soal) * 100, 1) if total_soal > 0 else 0.0
    waktu_rata2 = round(total_waktu_s / total_soal, 1) if total_soal > 0 else 0.0

    # Akurasi per topik
    akurasi_per_topik = {}
    for t_name, s in topic_stats.items():
        t_acc = round((s["benar"] / s["total"]) * 100, 1) if s["total"] > 0 else 0.0
        akurasi_per_topik[t_name] = {
            "total": s["total"],
            "benar": s["benar"],
            "akurasi_pct": t_acc
        }

    # Topik terlemah (maksimal 3, urutkan akurasi naik, lalu total turun)
    sorted_weak = sorted(
        akurasi_per_topik.items(),
        key=lambda item: (item[1]["akurasi_pct"], -item[1]["total"])
    )
    topik_terlemah = [t[0] for t in sorted_weak[:3]]

    # Topik terkuat (maksimal 3)
    sorted_strong = sorted(
        akurasi_per_topik.items(),
        key=lambda item: (-item[1]["akurasi_pct"], -item[1]["total"])
    )
    topik_terkuat = [t[0] for t in sorted_strong[:3] if t[1]["akurasi_pct"] >= 50]

    # Analisis pola belajar (K3: Pesan jujur dan jelas bagi mode tamu vs akun login)
    pola = "Data belajar stabil, pertahankan konsistensi latihan."
    if is_guest:
        pola = (
            "Login untuk menyimpan riwayat dan mendapatkan analisis AI Room. "
            "Sebagai tamu, data hanya tersimpan di perangkat ini."
        )
    elif total_soal == 0:
        pola = "Belum ada riwayat pengerjaan di akun ini. Kerjakan latihan untuk memetakan performa."
    elif total_salah > 0:
        if (salah_soal_lama / total_salah) >= 0.4:
            pola = "Sering salah di soal >60 detik (indikasi kebuntuan analisa rumus/langkah)."
        elif (salah_soal_cepat / total_salah) >= 0.35:
            pola = "Cenderung terburu-buru (<15 detik) pada soal yang keliru (perlu lebih teliti membaca stimulus)."
        elif (ganti_salah / total_salah) >= 0.3:
            pola = "Sering mengganti jawaban awal ke opsi yang keliru (overthinking)."
        elif (ragu_salah / total_salah) >= 0.4:
            pola = "Tingkat keraguan tinggi pada konsep soal yang berujung salah."
        else:
            pola = f"Akurasi pengerjaan {akurasi}% dengan rata-rata {waktu_rata2}s per soal."

    return {
        "mapel": clean_mapel,
        "display_name": get_mapel_display_name(clean_mapel),
        "total_attempt": len(attempts or []),
        "total_soal": total_soal,
        "total_benar": total_benar,
        "akurasi": akurasi,
        "waktu_rata2_per_soal": waktu_rata2,
        "akurasi_per_topik": akurasi_per_topik,
        "topik_terlemah": topik_terlemah,
        "topik_terkuat": topik_terkuat,
        "pola": pola,
        "is_guest": is_guest
    }


def get_last_wrong_questions(attempts, mapel_slug, limit=5):
    """Ambil maksimal 5 butir soal terakhir yang salah dikerjakan user."""
    clean_mapel = str(mapel_slug or "").strip().lower().replace("-", "_")
    wrong_questions = []

    # Iterasi dari attempt terbaru
    for att in (attempts or []):
        items = att.get("items") or []
        att_paket = int(att.get("paket") or 1)
        kunci_map = load_kunci_mapel(clean_mapel, att_paket)

        for it in items:
            final_ans = it.get("final_answer")
            if final_ans in (None, ""):
                continue

            pos = int(it.get("position") or 0)
            if not is_answer_correct(it, clean_mapel, att_paket):
                q_info = load_question_details(clean_mapel, att_paket, pos)
                kunci = kunci_map.get(str(pos))
                waktu_s = int(it.get("waktu_detik") if it.get("waktu_detik") is not None
                              else round((it.get("active_ms") or 0) / 1000))
                wrong_questions.append({
                    "paket": att_paket,
                    "nomor": pos,
                    "topik": str(it.get("topic_id") or it.get("topik") or q_info.get("topik") or "Umum"),
                    "user_answer": str(final_ans),
                    "kunci": str(kunci if kunci is not None else "-"),
                    "waktu_detik": waktu_s,
                    "snippet": q_info.get("snippet") or f"Soal nomor {pos}"
                })
                if len(wrong_questions) >= limit:
                    return wrong_questions

    return wrong_questions


def fetch_supabase_attempts(user_id, mapel_slug, sb_url, sb_key):
    """Ambil daftar attempt user untuk mapel tertentu dari Supabase REST.
    
    Catatan (K3): Untuk pengguna berstatus TAMU (user_id kosong atau None),
    fungsi ini mengembalikan [] karena attempt tryout tamu hanya disimpan di localStorage
    perangkat pengguna dan tidak dikirimkan ke server Supabase.
    """
    if not user_id or not sb_url or not sb_key:
        return []

    clean_mapel = str(mapel_slug or "").strip().lower().replace("-", "_")
    try:
        query_url = (
            f"{sb_url}/rest/v1/attempts?user_id=eq.{urllib.parse.quote(str(user_id))}"
            f"&mapel=ilike.{urllib.parse.quote(clean_mapel)}"
            f"&order=finished_at.desc,started_at.desc"
            f"&select=id,mapel,paket,n_questions,score,items,started_at,finished_at"
        )
        req = urllib.request.Request(
            query_url,
            headers={
                "apikey": sb_key,
                "Authorization": f"Bearer {sb_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8") or "[]")
            if isinstance(data, list):
                return data
    except Exception as e:
        sys.stderr.write(f"[/api/ai-room] Gagal fetch attempts dari Supabase: {e}\n")

    return []


def build_ai_room_system_prompt(aggregates, last_wrong):
    """Rakit system prompt kontekstual se-mapel untuk Guru AI Room (D3)."""
    disp = aggregates.get("display_name") or "Mata Pelajaran"
    total_soal = aggregates.get("total_soal", 0)
    total_attempt = aggregates.get("total_attempt", 0)
    akurasi = aggregates.get("akurasi", 0.0)
    waktu_rata = aggregates.get("waktu_rata2_per_soal", 0.0)
    topik_lemah = ", ".join(aggregates.get("topik_terlemah") or []) or "Belum terdeteksi"
    topik_kuat = ", ".join(aggregates.get("topik_terkuat") or []) or "Belum terdeteksi"
    pola = aggregates.get("pola") or "Belum ada pola spesifik"

    # Format 5 soal salah
    wrong_lines = []
    if last_wrong:
        for i, w in enumerate(last_wrong, 1):
            wrong_lines.append(
                f"{i}. Paket {w['paket']} Soal #{w['nomor']} (Topik: {w['topik']}): "
                f"Jawaban Murid='{w['user_answer']}', Kunci='{w['kunci']}', Durasi={w['waktu_detik']}s. "
                f"Konteks: {w['snippet']}"
            )
        wrong_text = "\n".join(wrong_lines)
    else:
        wrong_text = "Belum ada catatan soal yang salah pada mapel ini."

    prompt = f"""Kamu adalah Guru AI Spesialis Ruang {disp} untuk persiapan Ujian TKA SMA.
Tugasmu adalah membimbing murid secara komprehensif untuk mata pelajaran {disp}, menganalisis rekam jejak performanya, serta memberikan konsultasi konsep dan strategi belajar yang taktis.

REKAM JEJAK BELAJAR MURID DI RUANG {disp.upper()}:
- Total soal dikerjakan: {total_soal} butir (dari {total_attempt} sesi tryout)
- Akurasi keseluruhan: {akurasi}%
- Rata-rata waktu per soal: {waktu_rata} detik
- Topik terlemah yang butuh penguatan: {topik_lemah}
- Topik terkuat: {topik_kuat}
- Pola pengerjaan terdeteksi: {pola}

5 SOAL TERAKHIR YANG SALAH DIKERJAKAN MURID:
{wrong_text}

PANDUAN MENJAWAB:
1. Bersikaplah ramah, empatik, suportif, dan solutif layaknya mentor privat kelas atas.
2. Ketika menjawab pertanyaan murid, hubungkan dengan profil performanya (terutama topik terlemah atau pola pengerjaannya) jika relevan.
3. Berikan tips terapan, langkah matematis/analitis yang jelas, atau trik cepat untuk menuntaskan tipe soal yang sering menyulitkannya.
4. Gunakan format Markdown yang mudah dibaca di layar HP (gunakan poin-poin tebal dan ringkas).
5. Jangan gunakan bahasa yang merendahkan atau bertele-tele. Jawab secara padat dan berbobot.
"""
    return prompt.strip()


def chat_ai_room(aggregates, last_wrong, user_message, chat_history=None, model=None):
    """Panggil LLM untuk AI Room (D3) tanpa memotong kuota per-soal."""
    system_prompt = build_ai_room_system_prompt(aggregates, last_wrong)

    messages = [{"role": "system", "content": system_prompt}]

    # Tambah riwayat obrolan (maksimal 6 giliran terakhir)
    if chat_history and isinstance(chat_history, list):
        for h in chat_history[-6:]:
            if isinstance(h, dict) and h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": str(h["content"])[:1000]})

    messages.append({"role": "user", "content": str(user_message or "").strip()})

    reply_text = ""
    meta_info = {}

    try:
        reply_text, meta_info = tutor_llm.generate_with_meta(
            messages,
            model=model or os.environ.get("COACH_MODEL") or os.environ.get("LLM_MODEL"),
            temperature=0.4,
            max_tokens=800,
            timeout=25.0
        )
    except Exception as e:
        sys.stderr.write(f"[/api/ai-room/chat] LLM call error: {e}. Menggunakan fallback terarah.\n")
        # Cerdas fallback berbasis agregat
        disp = aggregates.get("display_name") or "Mapel ini"
        lemah = ", ".join(aggregates.get("topik_terlemah") or []) or "konsep dasar"
        pola = aggregates.get("pola") or ""
        reply_text = (
            f"Halo! Untuk mengoptimalkan belajarmu di **{disp}**, fokus utama kita adalah membedah topik **{lemah}**. "
            f"Catatan performamu menunjukkan pola: *{pola}*. "
            f"Cobalah mengulang latihan soal pada topik tersebut dengan alokasi waktu tenang tanpa terburu-buru, "
            f"lalu perhatikan setiap langkah pembahasannya secara seksama!"
        )
        meta_info = {"model": "fallback_advisor", "provider": "system"}

    return {
        "reply": reply_text.strip(),
        "model": meta_info.get("model") or "AI Room Coach",
        "provider": meta_info.get("provider") or "system"
    }
