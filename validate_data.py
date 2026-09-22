# -*- coding: utf-8 -*-
"""validate_data.py — Audit invarian data otoritatif untuk seluruh paket.

Memverifikasi (dengan bukti resmi di data/kunci/):
  1. Identitas paket   : setiap dataset dipetakan ke bukti resmi slug yang sama
  2. Nomor soal        : 1..N berurutan, tanpa duplikat/gap
  3. Tipe soal         : struktur cocok dengan tipe (opsi/pernyataan)
  4. Kunci jawaban     : SAMA persis dengan bukti resmi (bentuk kanonik) per soal
  5. PGK               : seluruh opsi benar dipertahankan (tidak pernah direduksi
                         dari '(A;D)' menjadi 'A')
  6. Benar-Salah       : tiap pernyataan memiliki nilai resmi Benar/Salah
  7. Pernyataan-Label  : tiap pernyataan memiliki label resmi yang sama
  8. Gambar            : setiap referensi gambar ada di folder paketnya
  9. Ringkasan jumlah  : soal / PG / PGK / BS / Label / graded items (reconciled)

Exit code 0 = semua lolos; 1 = ada pelanggaran. Dijalankan ulang kapan saja:
  python validate_data.py
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from _key_guard import official_canonical_map, _canon  # noqa: E402
from _repair_keys import parse_official_row  # noqa: E402

IMG_BASE = {
    ("matematika", 1): "data/paket_1", ("matematika", 2): "data/paket_2",
    ("bahasa_inggris", 1): "data/bahasa_inggris/paket_1", ("bahasa_inggris", 2): "data/bahasa_inggris/paket_2",
    ("ekonomi", 1): "data/ekonomi/paket_1", ("ekonomi", 2): "data/ekonomi/paket_2",
    ("kewirausahaan", 1): "data/kewirausahaan/paket_1", ("kewirausahaan", 2): "data/kewirausahaan/paket_2",
}

PKGS = [
    "matematika_paket_1", "matematika_paket_2",
    "bahasa_inggris_paket_1", "bahasa_inggris_paket_2",
    "ekonomi_paket_1", "ekonomi_paket_2",
    "kewirausahaan_paket_1", "kewirausahaan_paket_2",
]

OFFICIAL_BS_COUNT = {  # dari bukti scrape (kunci_bs), untuk cross-check konversi
    "matematika_paket_1": 7, "matematika_paket_2": 4,
    "bahasa_inggris_paket_1": 0, "bahasa_inggris_paket_2": 0,
    "ekonomi_paket_1": 3, "ekonomi_paket_2": 2,
    "kewirausahaan_paket_1": 3, "kewirausahaan_paket_2": 3,
}


def audit(slug):
    problems, notes = [], []

    subj, pkg = slug.rsplit("_paket_", 1)
    img_base = IMG_BASE[(subj, int(pkg))]
    fpath = os.path.join(BASE, "data", f"{slug}_learning.json")
    d = json.load(open(fpath, encoding="utf-8"))
    soal = d["soal"]
    official = official_canonical_map(slug)

    # --- 2. nomor soal berurutan tanpa duplikat/gap ---
    nos = [s["nomor"] for s in soal]
    if nos != list(range(1, len(soal) + 1)):
        problems.append(f"nomor soal tidak berurutan: {nos[:10]}...")

    # --- identitas paket: jumlah soal == jumlah baris bukti resmi ---
    if official is not None and len(official) != len(soal):
        problems.append(f"jumlah soal {len(soal)} != bukti resmi {len(official)}")

    counts = {"Pilihan Ganda": 0, "Pilihan Ganda Kompleks": 0, "Benar-Salah": 0, "Pernyataan-Label": 0}
    n_items = 0
    n_img_refs = 0

    for s in soal:
        no = s["nomor"]
        tipe = s.get("tipe_soal")
        kunci = s.get("kunci_jawaban")

        # --- 4. kunci == bukti resmi (kanonik) ---
        if official is not None:
            off = official.get(no)
            if off is None:
                problems.append(f"#{no}: tidak ada bukti resmi")
            else:
                cur = _canon(kunci)
                if cur != off:
                    problems.append(f"#{no}: kunci {cur!r} != resmi {off!r}")

        # --- 3./5./6./7. struktur per tipe + hitung graded items ---
        if tipe == "Pilihan Ganda":
            counts["Pilihan Ganda"] += 1
            n_items += 1
            opts = [o["key"] for o in s.get("pilihan_jawaban", [])]
            if len(opts) < 4 or len(set(opts)) != len(opts):
                problems.append(f"#{no} PG: opsi tidak valid {opts}")
            if not (isinstance(kunci, str) and kunci in opts):
                problems.append(f"#{no} PG: kunci {kunci!r} tidak merujuk opsi")
        elif tipe == "Pilihan Ganda Kompleks":
            counts["Pilihan Ganda Kompleks"] += 1
            n_items += 1
            opts = [o["key"] for o in s.get("pilihan_jawaban", [])]
            if not (isinstance(kunci, list) and len(kunci) >= 2 and all(x in opts for x in kunci)):
                problems.append(f"#{no} PGK: kunci {kunci!r} tidak valid utk opsi {opts}")
        elif tipe in ("Benar-Salah", "Pernyataan-Label"):
            counts[tipe] += 1
            per = s.get("pernyataan")
            stmt_keys = [p["key"] for p in (per or [])]
            if not per or len(per) != 3 or stmt_keys != ["A", "B", "C"]:
                problems.append(f"#{no} {tipe}: pernyataan tidak valid ({stmt_keys})")
            if not (isinstance(kunci, list) and len(kunci) == 3
                    and all(re.fullmatch(r"[A-C]:[^:]+", str(x)) for x in kunci)):
                problems.append(f"#{no} {tipe}: format kunci {kunci!r} tidak valid")
            else:
                n_items += 3
                kmap = {str(x).split(":", 1)[0]: str(x).split(":", 1)[1] for x in kunci}
                # tiap pernyataan harus punya nilai resmi yang sama
                if official is not None:
                    off = official.get(no)
                    if off and off[0] == "stmt":
                        for k, v in kmap.items():
                            if off[1].get(k) != v:
                                problems.append(f"#{no} {tipe}: pernyataan {k}={v!r} != resmi {off[1].get(k)!r}")
            # tiap pernyataan harus punya konten
            for p in (per or []):
                if not ((p.get("text") or "").strip() or p.get("latex") or p.get("image")):
                    problems.append(f"#{no} {tipe}: pernyataan {p.get('key')} kosong")
        else:
            problems.append(f"#{no}: tipe tak dikenal {tipe!r}")

        # --- 8. gambar ---
        for p in (s.get("pernyataan") or []):
            if p.get("image"):
                n_img_refs += 1
                if not os.path.exists(os.path.join(img_base, p["image"]["rel_path"])):
                    problems.append(f"#{no}: gambar pernyataan hilang {p['image']['rel_path']}")
        for o in s.get("pilihan_jawaban", []):
            if o.get("image"):
                n_img_refs += 1
                if not os.path.exists(os.path.join(img_base, o["image"]["rel_path"])):
                    problems.append(f"#{no}: gambar opsi hilang {o['image']['rel_path']}")
        for i in (s.get("pertanyaan", {}).get("images") or []):
            n_img_refs += 1
            if not os.path.exists(os.path.join(img_base, i["rel_path"])):
                problems.append(f"#{no}: gambar pertanyaan hilang {i['rel_path']}")
        for i in (s.get("stimulus", {}).get("images") or []):
            n_img_refs += 1
            if not os.path.exists(os.path.join(img_base, i["rel_path"])):
                problems.append(f"#{no}: gambar stimulus hilang {i['rel_path']}")

    # --- konversi BS sesuai bukti (stmt dgn nilai Benar/Salah = B/S; lainnya = label) ---
    if official is not None:
        n_bs_official = sum(
            1 for v in official.values()
            if v[0] == "stmt" and set(v[1].values()) <= {"Benar", "Salah"}
        )
        if n_bs_official != counts["Benar-Salah"]:
            problems.append(f"B/S: dataset {counts['Benar-Salah']} != resmi {n_bs_official}")

    summary = {
        "slug": slug, "soal": len(soal), "items": n_items,
        "PG": counts["Pilihan Ganda"], "PGK": counts["Pilihan Ganda Kompleks"],
        "BS": counts["Benar-Salah"], "Label": counts["Pernyataan-Label"],
        "img_refs": n_img_refs, "problems": problems,
    }
    return summary


def main():
    all_ok = True
    T = {"soal": 0, "items": 0, "PG": 0, "PGK": 0, "BS": 0, "Label": 0, "img": 0}
    for slug in PKGS:
        r = audit(slug)
        T["soal"] += r["soal"]; T["items"] += r["items"]
        T["PG"] += r["PG"]; T["PGK"] += r["PGK"]; T["BS"] += r["BS"]; T["Label"] += r["Label"]
        T["img"] += r["img_refs"]
        status = "OK" if not r["problems"] else f"{len(r['problems'])} MASALAH"
        print(f"{slug:28s} soal={r['soal']:3d} (PG={r['PG']:3d} PGK={r['PGK']:2d} "
              f"BS={r['BS']} Label={r['Label']}) items={r['items']:3d} img={r['img_refs']:3d} -> {status}")
        for p in r["problems"][:10]:
            print("   [MASALAH]", p)
        all_ok = all_ok and not r["problems"]

    print()
    print(f"TOTAL  : soal={T['soal']} | PG={T['PG']} PGK={T['PGK']} BS={T['BS']} Label={T['Label']}")
    print(f"         graded items = {T['PG'] + T['PGK']} choice + 3*{T['BS'] + T['Label']} statement "
          f"= {T['items']}")
    print(f"         image refs = {T['img']}")
    print("HASIL :", "SEMUA LOLOS" if all_ok else "GAGAL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
