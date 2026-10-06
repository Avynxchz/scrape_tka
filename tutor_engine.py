# -*- coding: utf-8 -*-
"""tutor_engine.py — Mesin AI Tutor konversasional berbasis LLM.

Perubahan arsitektur vs tutor lama (get_ai_tutor_response di server.py):
  LAMA : user message -> pohon if/keyword -> teks deterministik/templat.
  BARU : KONTEKS SOAL (Layer 2) + SOLUSI REFERENSI (Layer 3) + RINGKASAN +
         RIWAYAT TERKINI + PESAN USER -> LLM -> jawaban dinamis.

Layer 3 adalah REFERENSI, bukan naskah: model boleh menjelaskan ulang,
menghitung varian hipotetik, memakai analogi, membandingkan cara — selama
tidak bertentangan dengan fakta soal dan kunci resmi.

Deteksi intent di sini HANYA untuk menyetel gaya/suhu generasi; semua konten
jawaban tetap dihasilkan LLM (bukan cabang teks yang di-stor).
"""
import json

import tutor_llm

DEFAULT_RECENT_WINDOW = 12          # pesan terakhir yang dikirim penuh
MAX_CTX_CHARS = 14000               # anggaran karakter bagian konteks statis
MAX_HISTORY_CHARS = 9000            # anggaran karakter riwayat terkini
SUMMARY_MAX_CHARS = 900

SYSTEM_PROMPT_TEMPLATE = """<role>
Kamu adalah AI Tutor TKA — guru privat yang sabar, hangat, dan ngobrol natural \
(bahasa Indonesia santai tapi jelas; "kamu"; sapaan netral). Kamu membantu siswa \
memahami SATU soal tertentu yang sedang dikerjakannya. Kamu bukan mesin kunci \
jawaban, bukan mesin pencari, dan bukan pembuku catatan.
</role>

<student_context>
Ringkasan percakapan sejauh ini (pengalaman belajar siswa pada soal ini):
{summary_block}
</student_context>

<question_context>
Soal yang sedang dibahas — SATU-SATUNYA soal yang sedang aktif:
{question_block}
</question_context>

<official_answer>
Kunci jawaban RESMI aplikasi (satu-satunya otoritas penilaian): {official_answer}
</official_answer>

<solution_reference>
Referensi solusi (hasil analisis sebelumnya; gunakan sebagai pemahaman materi, \
BUKAN naskah yang harus dibaca ulang — boleh menjelaskan dengan cara/urutan/analogi \
berbeda sesuai pertanyaan siswa):
{solution_block}
</solution_reference>

<recent_history>
Percakapan terbaru (paling baru di bawah):
{history_block}
</recent_history>

<current_message>
{current_message}
</current_message>

<behavior_rules>
1. KARAKTERISTIK SISTEM: Kamu bersifat stateless. Riwayat obrolan disuplai dari database backend. Jaga kontinuitas obrolan seolah-olah kamu entitas tunggal yang sama. Dilarang menyebutkan pergantian akun, kuota, atau masalah teknis API kepada siswa.
2. HEMAT TOKEN & LANGSUNG KE INTI: Jawaban wajib padat, ramah, dan langsung ke inti pertanyaan siswa. Buang kalimat klise yang berulang ("Tentu, mari kita bahas...", "Halo!").
3. STRUKTUR PENULISAN RAPI & BERSIH:
   • Paragraf 1: Jawaban inti yang lugas dan mudah dicerna.
   • Penjelasan bertahap: Jika ada hitungan atau alur logika, WAJIB gunakan poin bernomor (`1.`, `2.`) atau bullet (`•`) dengan baris baru agar tidak menumpuk dalam paragraf tebal.
   • Notasi matematika: Wajib gunakan `$variabel$` untuk simbol matematika inline dan `$$rumus$$` pada baris mandiri untuk rumus utama (KaTeX).
   • Trik Cepat: Bila ada jalan pintas atau cara cepat, berikan label "⚡ Tips Cepat: ...".
4. Jawab PESAN TERAKHIR siswa — bukan pertanyaan lama, bukan penjelasan umum. Pesan pendek seperti "kenapa?", "terus?", "kok bisa?" merujuk pada pembicaraan sebelumnya: hubungkan dengan konteks riwayat.
5. JANGAN mengulang seluruh langkah solusi kecuali diminta. Fokus hanya pada bagian spesifik yang ditanyakan siswa.
6. Variasikan cara penjelasan: Jika siswa belum mengerti, gunakan analogi sederhana, contoh angka kecil, atau penurunan konsep dasar.
7. Kreatif tapi jujur: Jika memakai contoh angka lain, SELALU tandai jelas sebagai "misalnya" / "contoh", agar tidak tertukar dengan soal asli.
8. Kunci resmi tidak boleh diganggu: Jika siswa menduga jawaban lain, jelaskan letak kekeliruan mereka dengan ramah dan edukatif.
9. BELAJAR AKTIF (SOKRATIS): Jangan berikan kunci jawaban atau pembahasan penuh secara langsung. Tuntun siswa menemukan jawabannya lewat pertanyaan balik/pancingan dulu (maksimal 2 putaran bimbingan). Berikan jawaban langsung hanya bila siswa sudah berusaha menjawab sendiri atau meminta eksplisit setelah dibimbing.
10. {review_note}
11. Di akhir jawaban, sertakan satu pertanyaan singkat pemeriksa pemahaman siswa bila relevan.
</behavior_rules>"""


# ---------------------------------------------------------------------------
# Deteksi intent (internal — menyetel gaya, bukan menghasilkan konten)
# ---------------------------------------------------------------------------
def detect_intent(message, history=None):
    m = (message or "").strip().lower()
    history = history or []

    def _has(*words):
        return any(w in m for w in words)

    if _has("step", "langkah ke", "langkah no", "langkah nomor", "poin ke") or \
       (m.startswith("step") and any(c.isdigit() for c in m[:12])):
        return "explain_specific_step"
    if _has("kok bukan", "kenapa bukan", "kok nggak", "kenapa tidak", "lho kok bukan",
            "kenapa bukan"):
        return "compare_options"
    if _has("kalau", "kalo", "gimana kalo", "bagaimana jika", "misal", "seandainya") and \
       _has("diganti", "ganti", "jadi", "naik", "turun", "tambah", "dikurang", "doubel", "lebih"):
        return "hypothetical_change"
    if _has("cara lain", "alternatif", "cara pendek", "cara cepat lain", "metode lain"):
        return "ask_strategy"
    if _has("gampang", "sederhanakan", "simplify", "bahasa awam", "paling dasar",
            "dari awal", "dari nol", "basic", "dasarnya") or _has("nggak ngerti", "gak ngerti",
            "ga ngerti", "belum ngerti", "bingung", "gatau", "gak paham", "nggak paham"):
        return "simplify"
    if _has("contoh", "analogi"):
        return "give_example"
    if _has("cek", "verify", "bener nggak", "apakah benar", "udah bener"):
        return "verify_calculation"
    if _has("apa itu", "arti", "maksud dari", "definisi", "istilah") and len(m) < 90:
        return "ask_definition"
    if _has("kenapa jawaban", "kok jawaban", "kenapa opsi"):
        return "explain_why"
    if m in ("kenapa?", "kok?", "kok", "kenapa", "kok bisa", "kok bisa?"):
        return "continue_previous_point" if history else "explain_why"
    if _has("intinya", "inti soal", "ringkas", "kesimpulan", "gimana kerjanya"):
        return "explain_answer"
    if m in ("terus?", "terus", "lanjut", "lanjutan", "kenapa", "kok", "kok bisa",
             "maksudnya?", "maksudnya", "kenapa?", "kok bisa?", "why?") or len(m) <= 6:
        if history:
            return "continue_previous_point"
        return "explain_answer"
    return "explain_answer"


# Profil gaya per intent: (temperature, suffix perintah gaya)
_INTENT_PROFILE = {
    "explain_specific_step": (0.35, "Fokus HANYA pada langkah yang diminta siswa; "
                                    "jangan menyebut langkah lain kecuali satu kalimat pengantar."),
    "compare_options": (0.4, "Bandingkan penalaran dengan pilihan yang diragukan siswa; "
                             "tunjukkan di mana penalarannya berbeda sehingga pilihan itu tidak tepat."),
    "hypothetical_change": (0.5, "Hitung varian hipotetik selangkah demi selangkah bila memungkinkan, "
                                 "dan tegaskan ini contoh/eksplorasi, bukan bagian soal asli."),
    "ask_strategy": (0.6, "Tawarkan cara/metode alternatif yang valid untuk soal ini; "
                          "jelasin kenapa cara itu bekerja."),
    "simplify": (0.55, "Ganti pendekatan: pakai contoh angka kecil atau analogi; "
                       "mulai dari konsep paling dasar yang relevan; jangan parafrase kalimat lama."),
    "give_example": (0.7, "Buat contoh sejenis yang kecil dan jelas bedakan dari soal asli."),
    "verify_calculation": (0.3, "Telusuri ulang hitungan yang diragukan, tulis tiap langkah hitungnya."),
    "ask_definition": (0.4, "Definisikan istilahnya dengan bahasa sederhana + hubungkan ke soal ini."),
    "explain_why": (0.45, "Jelaskan alasan kausal/langkah demi langkah yang membuat jawaban itu benar."),
    "continue_previous_point": (0.5, "Lanjutkan/elaborasi titik terakhir yang kamu jelaskan; "
                                     "jangan mulai pembahasan dari awal."),
    "explain_answer": (0.6, "Jawab langsung pertanyaannya dengan konteks soal aktif."),
}


# ---------------------------------------------------------------------------
# Blok konteks
# ---------------------------------------------------------------------------
def _fmt_question_block(canon_ctx, subject_name):
    lines = [f"Mata pelajaran: {subject_name}",
             f"ID soal kanonis: {canon_ctx.get('id', '?')}",
             f"Tipe soal: {canon_ctx.get('type', '?')}",
             "", canon_ctx.get("soal_text", "(soal tidak tersedia)")]
    formulas = canon_ctx.get("formulas") or []
    if formulas:
        fl = "\n".join(f"  - ${f.get('latex','')}$ (sumber: {f.get('source','')})"
                       for f in formulas[:14])
        lines += ["", "[DAFTAR FORMULA SOAL INI]", fl]
    return "\n".join(lines)


def _fmt_solution_block(sol):
    """Layer 3 sebagai referensi — berlabel PILAR 1-5 persis seperti panel UI,
    sehingga siswa bisa bertanya 'apa isi pilar 3?' dan tutor tahu persis."""
    if not sol:
        return "(belum tersedia — jelaskan dari konteks soal; jangan mengarang kunci)"
    p = sol.get("pembahasan") or {}
    parts = []

    if p.get("diketahui") or p.get("ditanyakan") or p.get("konsep_kunci"):
        pil1 = []
        if p.get("diketahui"):
            pil1.append("Data diketahui: " + str(p["diketahui"]))
        if p.get("ditanyakan"):
            pil1.append("Ditanyakan: " + str(p["ditanyakan"]))
        if p.get("konsep_kunci"):
            pil1.append("Konsep kunci: " + "; ".join(p["konsep_kunci"]))
        parts.append("[PILAR 1 · IDENTIFIKASI MASALAH & FONDASI TEORI]\n" + "\n".join(pil1))

    if p.get("glosarium_simbol"):
        g = "; ".join(f"{g_['simbol']} = {g_.get('arti','')}" for g_ in p["glosarium_simbol"][:8])
        parts.append("[PILAR 2 · NOTASI MATEMATIKA & GLOSARIUM]\n" + g)

    if p.get("mengapa_begini"):
        parts.append("[PILAR 3 · INTUISI BERPIKIR (MENGAPA CARA INI DIPAKAI)]\n" + p["mengapa_begini"])

    if p.get("langkah_penyelesaian"):
        parts.append("[PILAR 4 · LANGKAH SISTEMATIS]\n" +
                     "\n".join(f"  {s}" for s in p["langkah_penyelesaian"]))

    pil5 = []
    for t in p.get("tips_list") or []:
        pil5.append("• " + t)
    for m in p.get("mistakes_list") or []:
        pil5.append("⚠️ Jebakan umum: " + m)
    if not pil5 and p.get("tips_trik"):
        pil5.append(p["tips_trik"])
    if pil5:
        parts.append("[PILAR 5 · TRIK UJIAN & JEBAKAN]\n" + "\n".join(pil5))

    # Soal serupa (latihan pemantapan) — siswa dapat bertanya tentang ini,
    # jadi tutor wajib tahu isinya: pertanyaan, pilihan, kunci, pembahasan.
    sim = sol.get("soal_serupa") or {}
    if sim.get("pertanyaan"):
        sim_parts = ["Pertanyaan: " + str(sim["pertanyaan"])]
        opts = sim.get("pilihan") or []
        if opts:
            sim_parts.append("Pilihan: " + "; ".join(
                f"{o.get('key','')}. {(o.get('text') or '').strip()}" for o in opts))
        if sim.get("kunci"):
            sim_parts.append("Kunci soal serupa: " + str(sim["kunci"]))
        if sim.get("pembahasan_singkat"):
            sim_parts.append("Pembahasan singkat soal serupa: " + str(sim["pembahasan_singkat"]))
        parts.append("[SOAL SERUPA · LATIHAN PEMANTAPAN]\n" + "\n".join(sim_parts))

    return "\n\n".join(parts) if parts else "(solusi tersedia namun kosong)"


def _truncate(text, limit):
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit - 1] + "…"


def _review_note(sol):
    review = (sol or {}).get("review") or {}
    if not review.get("needs_manual_review"):
        return "Soal ini tidak menandai kebutuhan verifikasi manual."
    reason = review.get("review_reason") or ""
    note = ("Soal ini menandai PERLU VERIFIKASI MANUAL karena sebagian informasi "
            "sumber belum pasti. JANGAN mengarang bagian yang belum pasti; sampaikan "
            "ketidakpastian itu hanya KALAU relevan dengan pertanyaan siswa saat ini.")
    if reason:
        note += " Detail sumber: " + _truncate(reason, 500)
    return note


# ---------------------------------------------------------------------------
# Perakitan prompt (beranggar karakter)
# ---------------------------------------------------------------------------
def build_tutor_prompt(canon_ctx, solution, official_answer, history_msgs,
                       user_message, summary=None, subject_name="Matematika"):
    """Susun pesan [{role, content}] untuk LLM.

    history_msgs: list dict {role, content} TERURUT lama->baru (dari store).
    """
    solution_block = _truncate(_fmt_solution_block(solution), MAX_CTX_CHARS // 2)
    question_block = _truncate(_fmt_question_block(canon_ctx, subject_name),
                               MAX_CTX_CHARS // 2)
    summary_block = _truncate(summary or "(percakapan masih pendek — belum ada ringkasan)",
                              SUMMARY_MAX_CHARS)

    # Riwayat: ambil dari belakang sampai habis anggaran (lalu urutkan ulang).
    history_block_parts = []
    used = 0
    picked = []
    for msg in reversed(history_msgs):
        tag = "Siswa" if msg.get("role") == "user" else "Tutor"
        line = f"{tag}: {_truncate(msg.get('content',''), 1500)}"
        if used + len(line) > MAX_HISTORY_CHARS and picked:
            break
        picked.append(line)
        used += len(line)
    history_block = "\n\n".join(reversed(picked)) or "(belum ada percakapan sebelumnya)"

    intent = detect_intent(user_message, history_msgs)
    temp, style_hint = _INTENT_PROFILE.get(intent, (0.6, ""))

    system = SYSTEM_PROMPT_TEMPLATE.format(
        summary_block=summary_block,
        question_block=question_block,
        official_answer=official_answer,
        solution_block=solution_block,
        history_block=history_block,
        current_message=user_message,
        review_note=_review_note(solution),
    )
    if style_hint:
        system += f"\n\n<focus_hint>{style_hint}</focus_hint>"

    messages = [{"role": "system", "content": system}]
    # Giliran penutup riwayat (2 terakhir) sebagai chat turns agar model
    # memahami alur dialog, lalu pesan user saat ini sebagai turn terakhir.
    for msg in history_msgs[-2:]:
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": _truncate(msg.get("content", ""), 1200)})
    messages.append({"role": "user", "content": user_message})
    return messages, {"intent": intent, "temperature": temp}


def summarize_older(older_msgs, existing_summary):
    """Ringkasan bergulir: gabung ringkasan lama + pesan yang keluar dari jendela.

    Deterministik & murah — TIDAK memanggil LLM (menghindari biaya/ketergantungan
    tambahan); cukup untuk menjaga kontinuitas konteks jendela pendek.
    """
    keep = []
    for m in older_msgs:
        who = "Siswa" if m.get("role") == "user" else "Tutor"
        t = (m.get("content") or "").replace("\n", " ").strip()
        if t:
            keep.append(f"{who}: {t[:160]}")
    if not keep:
        return existing_summary or None
    lines = []
    if existing_summary:
        lines.append(existing_summary)
    lines.append("Awal percakapan (dirangkum): " + " | ".join(keep[-10:]))
    text = "\n".join(lines)
    if len(text) > SUMMARY_MAX_CHARS:
        text = "…(ringkasan dipangkas)…\n" + text[-SUMMARY_MAX_CHARS:]
    return text


def generate_tutor_response(canon_ctx, solution, official_answer, history_msgs,
                            user_message, summary=None, subject_name="Matematika",
                            model=None, image_paths=None):
    """Panggil LLM dengan konteks lengkap. Melempar tutor_llm.LLMError saat gagal."""
    messages, meta = build_tutor_prompt(canon_ctx, solution, official_answer,
                                        history_msgs, user_message, summary, subject_name)
    reply_or_tuple = tutor_llm.generate(messages, model=model, image_paths=image_paths,
                                        temperature=meta["temperature"], return_meta=True)
    if isinstance(reply_or_tuple, tuple):
        reply, llm_meta = reply_or_tuple
        meta["model"] = llm_meta.get("model", "")
        meta["provider"] = llm_meta.get("provider", "")
    else:
        reply = reply_or_tuple
        meta["model"] = ""
        meta["provider"] = ""
    return reply, meta
