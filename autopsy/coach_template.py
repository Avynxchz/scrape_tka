# -*- coding: utf-8 -*-
"""autopsy/coach_template.py — Template cadangan deterministik untuk Guru Autopsi (FASE A4/A3).

Menghasilkan skema output identik (coach_output_v1 dengan sumber: "template")
secara deterministik dari evidence pack tanpa memanggil LLM.
Digunakan saat timeout, kuota habis, error provider, atau validasi AI gagal.
"""

LABEL_TO_PENYEBAB = {
    "overthinking": "overthinking",
    "terburu": "terburu",
    "yakin_salah": "konsep",
    "ragu_salah": "konsep",
    "ragu_benar": "rapuh",
    "macet": "macet",
    "waktu_habis": "kosong",
    "kosong": "kosong",
}

LEAK_COPY = {
    "terburu": {
        "judul": "Menjawab sebelum tuntas membaca soal",
        "tafsir": "Kemungkinan opsi dipilih tergesa-gesa sebelum kalimat tanya dan semua opsi dipahami.",
        "tindakan": "Di tryout berikutnya, baca ulang kalimat tanya sebelum memilih jawaban.",
    },
    "overthinking": {
        "judul": "Mengganti jawaban yang semula sudah benar",
        "tafsir": "Kemungkinan ragu pada perhitungan awal lalu berpindah ke opsi jebakan.",
        "tindakan": "Pertahankan jawaban pertama kecuali menemukan bukti kesalahan hitung yang nyata.",
    },
    "yakin_salah": {
        "judul": "Konsep dasar belum kokoh pada soal tertentu",
        "tafsir": "Kemungkinan ada rumus atau definisi konsep yang tertukar.",
        "tindakan": "Buka pembahasan Pilar 1 dan kuatkan konsep dasar topik ini.",
    },
    "ragu_salah": {
        "judul": "Ragu-ragu memilih dan jawaban akhirnya salah",
        "tafsir": "Intuisi awal belum cukup kuat untuk membedakan opsi yang mirip.",
        "tindakan": "Pelajari langkah eliminasi opsi pada pembahasan soal serupa.",
    },
    "macet": {
        "judul": "Terjebak terlalu lama pada satu soal",
        "tafsir": "Kemungkinan memaksakan menyelesaikan soal sulit sehingga kehabisan waktu.",
        "tindakan": "Lewati soal yang macet lebih dari jatah waktu dan kerjakan yang lain dulu.",
    },
    "waktu_habis": {
        "judul": "Kehabisan waktu di bagian akhir ujian",
        "tafsir": "Manajemen ritme pengerjaan di awal membuat soal akhir terlewat.",
        "tindakan": "Gunakan pembagian waktu per blok 10 soal agar tidak menumpuk di akhir.",
    },
    "kosong": {
        "judul": "Banyak soal yang belum sempat dijawab",
        "tafsir": "Pacing pengerjaan perlu dipercepat agar seluruh soal terbaca.",
        "tindakan": "Pasang target waktu maksimal per soal sesuai jatah resmi.",
    },
}


def generate_template(evidence):
    """Menghasilkan output coach_output_v1 deterministik dari evidence pack."""
    data_tipis = bool(evidence.get("data_tipis", False))
    skor_pct = int(evidence.get("skor_pct") or 0)
    pola = evidence.get("pola") or {}
    median_w = int(pola.get("median_waktu_detik") or 0)
    jatah_w = int(pola.get("jatah_detik") or 180)

    # 1. Sapaan (<= 140)
    if data_tipis:
        sapaan = "Saya melihat kamu baru mengerjakan sebagian soal. Ini awal yang baik untuk memetakan kebiasaan belajarmu."[:140]
    else:
        sapaan = "Saya sudah mengamati caramu mengerjakan tadi. Ada pola yang jelas dan bisa kita perbaiki dalam beberapa hari ke depan."[:140]

    # 2. Penilaian (<= 260)
    penilaian = (
        f"Skormu {skor_pct}%. Bagian yang paling cepat dipulihkan adalah membenahi ritme dan tidak terburu-buru di soal yang terasa mudah. "
        "Fokus pada peningkatan bertahap setiap sesi latihan."
    )[:260]

    # 3. Pengamatan (3-5 butir, masing-masing <= 220)
    pengamatan = []
    # Butir kebocoran #1
    raw_leaks = evidence.get("kebocoran") or []
    if raw_leaks:
        pengamatan.append(f"Kebocoran utama: {raw_leaks[0].get('bukti', 'terdapat pola salah berulang')}."[:220])

    # Butir nomor soal nyata
    fokus = evidence.get("fokus_soal") or []
    for q in fokus[:2]:
        no = q.get("no")
        waktu = q.get("waktu_detik", 0)
        lbl = q.get("label", "soal")
        if q.get("jawaban_awal") and q.get("jawaban_akhir") and q.get("jawaban_awal") != q.get("jawaban_akhir"):
            pengamatan.append(
                f"Soal {no}: kamu memilih {q['jawaban_awal']} lalu mengganti ke {q['jawaban_akhir']} dengan waktu {waktu} detik."[:220]
            )
        else:
            pengamatan.append(
                f"Soal {no} ({lbl}): dijawab dalam {waktu} detik dari jatah {q.get('jatah_detik', jatah_w)} detik."[:220]
            )

    # Butir median waktu
    if len(pengamatan) < 3:
        pengamatan.append(f"Median waktu pengerjaanmu {median_w} detik per soal, berbanding jatah {jatah_w} detik."[:220])
    if len(pengamatan) < 3:
        pengamatan.append(f"Tingkat akurasi di awal {pola.get('akurasi_awal_pct', 0)}% dan di akhir {pola.get('akurasi_akhir_pct', 0)}%."[:220])
    pengamatan = pengamatan[:5]

    # 4. Sudah bagus (<= 160)
    sudah_bagus = str(evidence.get("yang_bagus") or "Kamu memiliki konsistensi yang baik saat menghadapi soal-soal terarah.")[:160]

    # 5. Kebocoran (maks 3)
    kebocoran = []
    for k in raw_leaks[:3]:
        lbl = k.get("label", "terburu")
        copy = LEAK_COPY.get(lbl, LEAK_COPY["terburu"])
        kebocoran.append({
            "label": lbl,
            "judul": copy["judul"][:60],
            "bukti": str(k.get("bukti") or f"{k.get('soal_hilang', 1)} soal terpengaruh")[:200],
            "contoh": k.get("contoh") or [],
            "tafsir": copy["tafsir"][:200],
            "tindakan": copy["tindakan"][:160],
        })

    # 6. Per soal (maks 6)
    per_soal = []
    for q in fokus[:6]:
        no = q.get("no", 1)
        lbl = q.get("label", "terburu")
        penyebab = LABEL_TO_PENYEBAB.get(lbl, "konsep")
        topik = q.get("topik", "Matematika")

        dipelajari = f"Kuatkan pemahaman topik {topik}. Perhatikan langkah kunci perhitungan."[:160]
        langkah = [
            f"Buka pembahasan nomor {no} pada tab Pilar."[:120],
            f"Kerjakan ulang soal {no} secara mandiri tanpa melihat kunci."[:120],
        ]
        cek_paham = f"Bagian mana dari konsep {topik} yang membuatmu ragu tadi?"[:140]

        per_soal.append({
            "no": no,
            "penyebab": penyebab,
            "dipelajari": dipelajari,
            "langkah": langkah,
            "cek_paham": cek_paham,
        })

    # 7. Misi
    candidates = evidence.get("kandidat_tugas") or []
    task_ids = [candidates[0]["task_id"]] if candidates else ["d1-pilar-auto"]
    misi = {
        "pembuka": "Misi 10 menit hari ini: latih ketelitian membaca sebelum memilih opsi."[:140],
        "task_ids": task_ids,
    }

    # 8. Rencana
    rencana = []

    # 9. Penutup (<= 140)
    penutup = "Mulai dari satu langkah kecil hari ini. Kita evaluasi kemajuannya di tryout berikutnya."[:140]

    # 10. Catatan data (<= 160)
    catatan_data = "Jumlah soal yang dikerjakan masih sedikit, jadi anggap analisis ini sebagai gambaran awal."[:160] if data_tipis else ""

    return {
        "versi": "coach_output_v1",
        "sumber": "template",
        "sapaan": sapaan,
        "penilaian": penilaian,
        "pengamatan": pengamatan,
        "sudah_bagus": sudah_bagus,
        "kebocoran": kebocoran,
        "per_soal": per_soal,
        "misi": misi,
        "rencana": rencana,
        "penutup": penutup,
        "catatan_data": catatan_data,
    }
