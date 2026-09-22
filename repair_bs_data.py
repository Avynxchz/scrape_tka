# -*- coding: utf-8 -*-
"""[RETIRED / TIDAK DIPAKAI LAGI]

Repair satu kali untuk matematika_paket_2 (18 Sep 2026), SEBELUM ada
scrape_kunci.py + _repair_keys.py. Skrip ini TIDAK idempoten:\nmenjalankannya lagi pada data yang sudah dikonversi akan MENGHANCURKAN
pernyataan Benar/Salah (membangun ulang dari pilihan_jawaban yang sudah
tidak ada) dan menimpa kunci PGK multi-jawaban dengan huruf pertama saja.

Ganti fungsi skrip ini:
    python scrape_kunci.py --target matematika_paket_2   # ambil kunci resmi
    python _repair_keys.py --apply                       # terapkan (idempoten)

Invariant proyek: kunci_jawaban hanya boleh berasal dari bukti resmi
(data/kunci/) — lihat _key_guard.py. Skrip ini dibiarkan hanya sebagai
rekam jejak historis dan MENOLAK dijalankan.
"""
import sys

print(
    "[DITOLAK] repair_bs_data.py sudah pensiun dan TIDAK idempoten.\n"
    "Menjalankannya lagi akan merusak data yang sudah diperbaiki.\n\n"
    "Gunakan proses resmi yang idempoten:\n"
    "  python scrape_kunci.py --target matematika_paket_2\n"
    "  python _repair_keys.py --apply\n\n"
    "Lihat _key_guard.py untuk invarian kunci jawaban proyek."
)
sys.exit(1)

raise SystemExit  # unreachable — blok di bawah hanya arsip

import json  # noqa: E402

F = r"D:\PROJECTS\SCRAPE_TKA\data\matematika_paket_2_learning.json"

# Kunci resmi hasil ekstraksi review_hasil (sesi resmi Pusmendik, 18 Sep 2026)
KUNCI_RESMI = {
    1: "C", 2: "C", 4: "D", 5: "B", 6: "C", 7: "C", 8: "B", 9: "D",
    10: "C", 11: "B", 12: "B", 14: "B", 15: "B", 16: "D", 17: "C",
    18: "B", 19: "D", 21: "A", 22: "B", 24: "C", 25: "D",
}

# Kunci resmi per pernyataan untuk soal Benar/Salah
BS_KUNCI = {
    3:  {"A": "Benar", "B": "Salah", "C": "Benar"},
    13: {"A": "Salah", "B": "Benar", "C": "Salah"},
    20: {"A": "Salah", "B": "Salah", "C": "Benar"},
    23: {"A": "Salah", "B": "Benar", "C": "Benar"},
}

d = json.load(open(F, encoding="utf-8"))

for s in d["soal"]:
    no = s["nomor"]

    if no in BS_KUNCI:
        # Opsi B/C/D hasil scrape = Pernyataan A/B/C (opsi A = header tabel rusak)
        opts = {o["key"]: o for o in s["pilihan_jawaban"]}
        pernyataan = []
        for stmt_key, opt_key in [("A", "B"), ("B", "C"), ("C", "D")]:
            o = opts.get(opt_key, {})
            pernyataan.append({
                "key": stmt_key,
                "text": o.get("text", "") or "",
                "latex": o.get("latex"),
                "image": o.get("image"),
            })
        s["tipe_soal"] = "Benar-Salah"
        s["pernyataan"] = pernyataan
        s["kunci_jawaban"] = [f"{k}:{BS_KUNCI[no][k]}" for k in ["A", "B", "C"]]
        # Opsi lama tidak lagi dipakai untuk tipe B/S
        s.pop("pilihan_jawaban", None)
    else:
        s["kunci_jawaban"] = KUNCI_RESMI[no]

# Soal 3: pertanyaan kehilangan gambar a^b -> tambahkan kembali
soal3 = d["soal"][2]
soal3["pertanyaan"]["images"] = [{
    "filename": "soal_03_opsi_b.png",
    "rel_path": "images/soal_03_opsi_b.png",
    "remote_url": "https://pusmendik.kemendikdasmen.go.id/tka/cbt_images/95623_2bb1a52fded3d42e12a66544a01e07db.png"
}]

json.dump(d, open(F, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# Verifikasi
d2 = json.load(open(F, encoding="utf-8"))
for s in d2["soal"]:
    if s["tipe_soal"] == "Benar-Salah":
        print(f"Soal {s['nomor']} [B/S]: {s['kunci_jawaban']}")
kunci_pg = {s["nomor"]: s["kunci_jawaban"] for s in d2["soal"] if s["tipe_soal"] != "Benar-Salah"}
print("PG keys:", kunci_pg)
