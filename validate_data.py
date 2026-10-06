# -*- coding: utf-8 -*-
"""validate_data.py — Audit invarian data otoritatif untuk seluruh paket.

Memverifikasi (dengan bukti resmi di data/kunci/):
  1. Identitas paket   : setiap dataset dipetakan ke bukti resmi slug yang sama
  2. Nomor soal        : 1..N berurutan, tanpa duplikat/gap
  3. Tipe soal         : terisi & dikenal; struktur cocok dengan tipe (opsi/pernyataan)
  4. Kunci jawaban     : SAMA persis dengan bukti resmi (bentuk kanonik) per soal
  5. PGK               : seluruh opsi benar dipertahankan (tidak pernah direduksi
                         dari '(A;D)' menjadi 'A')
  6. Benar-Salah       : tiap pernyataan memiliki nilai resmi Benar/Salah
  7. Pernyataan-Label  : tiap pernyataan memiliki label resmi yang sama
  8. Gambar            : setiap referensi gambar ada di folder paketnya
  9. Duplikat          : tidak ada dua soal ber-isi identik dalam satu paket
                         (pelajaran: kewirausahaan_paket_2 no 8 = no 9)
 10. Pernyataan vs kunci: kunci pernyataan merujuk tepat ke pernyataan yang ada;
                         nilai B/S hanya Benar/Salah (pelajaran 4 soal Fase 1)
 11. Ringkasan jumlah  : soal / PG / PGK / BS / Label / graded items (reconciled)

Cakupan: SELURUH file data/*_learning.json (46 paket), bukan hanya 9.
Paket tanpa bukti resmi (kunci) -> cek bukti dilewati, cek struktur tetap jalan.

Catatan bukti tak lengkap: bila baris bukti resmi tak ter-parse ('X ()' kosong,
kasus nyata fisika_paket_1 q3 & BI p1 q4), soal itu dikecualikan dari cek
kesetaraan kunci-vs-bukti (dicatat di notes, bukan masalah) — polanya sudah
disanksi: kunci boleh lebih sedikit entri, tiap entri harus merujuk pernyataan
yang ada dan bernilai valid.

Exit code 0 = semua lolos; 1 = ada pelanggaran. Dijalankan ulang kapan saja:
  python validate_data.py
"""
import glob
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from _key_guard import official_canonical_map, _canon  # noqa: E402
from _repair_keys import parse_official_row  # noqa: E402

TIPE_VALID = ("Pilihan Ganda", "Pilihan Ganda Kompleks", "Benar-Salah", "Pernyataan-Label",
                # 'Matriks': varian pernyataan-label (nilai label, mis. Tepat/Tidak Tepat)
                "Matriks")
# Tipe yang strukturnya pernyataan A/B/C(/D) dengan kunci "X:label"
TIPE_PERNYATAAN = ("Benar-Salah", "Pernyataan-Label", "Matriks")

_AR_TASHKEEL_RE = re.compile(r"[ً-ٰٟ]")


def norm_bs_value(v):
    """Normalisasi kosakata Benar/Salah multibahasa ke bentuk kanonik.

    Ditemukan di dataset: Jerman R(esichtig)/F(alsch), Korea O/X,
    Arab الصحيح/الخطأ (harakat opsional). Nilai tak dikenal dikembalikan
    apa adanya (akan ditolak oleh cek).
    """
    s = (v or "").strip()
    if s in ("Benar", "R", "O"):
        return "Benar"
    if s in ("Salah", "F", "X"):
        return "Salah"
    ar = _AR_TASHKEEL_RE.sub("", s)
    if ar == "الصحيح":
        return "Benar"
    if ar == "الخطأ":
        return "Salah"
    return s


def discover_packages():
    """Seluruh slug yang memiliki file data/<slug>_learning.json."""
    out = []
    for p in glob.glob(os.path.join(BASE, "data", "*_learning.json")):
        out.append(os.path.basename(p)[:-len("_learning.json")])
    return sorted(out)


def img_base_for(slug):
    """Direktori raw (untuk cek keberadaan gambar) dari slug."""
    if "_paket_" in slug:
        subj, pkg = slug.rsplit("_paket_", 1)
    else:  # agregat lawas paket_1/paket_2 (= matematika)
        subj, pkg = "paket", slug.split("_")[-1]
    if subj in ("matematika", "paket"):  # paket_1/2 = agregat lawas matematika
        return os.path.join(BASE, "data", f"paket_{pkg}")
    return os.path.join(BASE, "data", subj, f"paket_{pkg}")


def load_official(slug):
    """Kembalikan (official_map | None, unparseable: {nomor: cuplikan}, n_rows | None).

    official_map: peta {nomor: bentuk-kanonik} dari _key_guard (baris tak
    ter-parse dilewati di sana). unparseable: nomor yang baris buktinya ada
    tetapi tak ter-parse ('unknown') — pola celah bukti resmi.
    """
    kpath = os.path.join(BASE, "data", "kunci", f"{slug}_kunci.json")
    if not os.path.exists(kpath):
        return None, {}, None
    official = official_canonical_map(slug)
    rows = json.load(open(kpath, encoding="utf-8")).get("raw_rows", {})
    unparseable = {}
    for no_str, row in rows.items():
        if parse_official_row(row.get("kunci", ""))[0] == "unknown":
            unparseable[int(no_str)] = (row.get("kunci", "") or "")[:80]
    return official, unparseable, len(rows)


def img_path(img_base, img):
    """Path file gambar: pakai rel_path bila ada, sonst images/<filename>."""
    rel = img.get("rel_path") or os.path.join("images", img.get("filename", ""))
    return os.path.join(img_base, rel)


def content_key(soal):
    """Kunci konten satu soal untuk deteksi duplikat (abaikan identitas)."""
    return json.dumps(
        {k: v for k, v in soal.items() if k not in ("nomor", "id")},
        ensure_ascii=False, sort_keys=True,
    )


def audit(slug):
    problems, notes = [], []

    fpath = os.path.join(BASE, "data", f"{slug}_learning.json")
    d = json.load(open(fpath, encoding="utf-8"))
    soal = d["soal"]
    official, unparseable, n_rows = load_official(slug)
    if unparseable:
        notes.append("bukti resmi tak lengkap/tak ter-parse: soal "
                     + ", ".join(f"#{n}" for n in sorted(unparseable)))

    # --- 2. nomor soal berurutan tanpa duplikat/gap ---
    nos = [s["nomor"] for s in soal]
    if nos != list(range(1, len(soal) + 1)):
        problems.append(f"nomor soal tidak berurutan: {nos[:12]}...")

    # --- 9. tidak ada soal ber-isi identik dalam satu paket ---
    seen = {}
    for s in soal:
        ck = content_key(s)
        if ck in seen:
            problems.append(f"duplikat isi: soal #{seen[ck]} = soal #{s['nomor']}")
        else:
            seen[ck] = s["nomor"]

    # --- identitas paket: jumlah soal == jumlah baris bukti resmi ---
    if n_rows is not None and n_rows != len(soal):
        problems.append(f"jumlah soal {len(soal)} != baris bukti resmi {n_rows}")

    counts = {"Pilihan Ganda": 0, "Pilihan Ganda Kompleks": 0, "Benar-Salah": 0,
              "Pernyataan-Label": 0, "Matriks": 0}
    n_items = 0
    n_img_refs = 0
    img_base = img_base_for(slug)
    if not os.path.isdir(img_base):
        notes.append(f"direktori gambar tidak ada: {img_base} (cek gambar dilewati)")

    for s in soal:
        no = s["nomor"]
        tipe = s.get("tipe_soal")
        kunci = s.get("kunci_jawaban")

        # --- 3a. tipe_soal wajib terisi ---
        if not (tipe or "").strip():
            problems.append(f"#{no}: tipe_soal kosong")
            continue

        # --- 4. kunci == bukti resmi (kanonik); kecuali bukti tak ter-parse ---
        # Tipe pernyataan: perbandingan per-butir dengan normalisasi kosakata
        # B/S dilakukan di bawah (lebih presisi daripada _canon mentah).
        if official is not None and no not in unparseable:
            off = official.get(no)
            if off is None:
                problems.append(f"#{no}: tidak ada bukti resmi")
            elif tipe not in TIPE_PERNYATAAN:
                cur = _canon(kunci)
                if cur != off:
                    problems.append(f"#{no}: kunci {cur!r} != resmi {off!r}")

        # --- 3b./5./6./7. struktur per tipe + hitung graded items ---
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
        elif tipe in TIPE_PERNYATAAN:
            counts[tipe] += 1
            per = s.get("pernyataan")
            stmt_keys = [p["key"] for p in (per or [])]
            # kunci pernyataan berurutan dari A (3-6 butir; kasus nyata: 4 butir)
            expect_keys = [chr(ord("A") + i) for i in range(len(stmt_keys))]
            if len(set(stmt_keys)) != len(stmt_keys):
                problems.append(f"#{no} {tipe}: kunci pernyataan ganda {stmt_keys}")
            gap = no in unparseable  # bukti tak lengkap: longgarkan cek jumlah
            if not gap:
                if not per or not (3 <= len(per) <= 6) or stmt_keys != expect_keys:
                    problems.append(f"#{no} {tipe}: pernyataan tidak valid ({stmt_keys})")
            if not (isinstance(kunci, list)
                    and all(re.fullmatch(r"[A-Z]:[^:]+", str(x)) for x in kunci)
                    and (gap or len(kunci) == len(per or []))):
                problems.append(f"#{no} {tipe}: format kunci {kunci!r} tidak valid")
            else:
                n_items += len(per or [])
                kmap = {str(x).split(":", 1)[0]: str(x).split(":", 1)[1] for x in kunci}
                # --- 10. pernyataan vs kunci cocok (pelajaran Fase 1) ---
                if sorted(kmap) != sorted(set(stmt_keys)):
                    # kecuali pola celah bukti resmi: kunci boleh subset pernyataan
                    if not (gap and set(kmap) <= set(stmt_keys)):
                        problems.append(
                            f"#{no} {tipe}: kunci {sorted(kmap)} != pernyataan {sorted(set(stmt_keys))}"
                        )
                if tipe == "Benar-Salah":
                    bad = [k for k, v in kmap.items()
                           if norm_bs_value(v) not in ("Benar", "Salah")]
                    if bad:
                        problems.append(f"#{no} B/S: nilai bukan Benar/Salah: {bad}")
                # tiap pernyataan harus punya nilai resmi yang sama
                # (kosakata B/S multibahasa dinormalisasi di kedua sisi)
                if official is not None and not gap:
                    off = official.get(no)
                    if off and off[0] == "stmt":
                        for k, v in kmap.items():
                            if norm_bs_value(off[1].get(k)) != norm_bs_value(v):
                                problems.append(f"#{no} {tipe}: pernyataan {k}={v!r} != resmi {off[1].get(k)!r}")
            # tiap pernyataan harus punya konten
            for p in (per or []):
                if not ((p.get("text") or "").strip() or p.get("latex") or p.get("image")):
                    problems.append(f"#{no} {tipe}: pernyataan {p.get('key')} kosong")
        else:
            problems.append(f"#{no}: tipe tak dikenal {tipe!r}")

        # --- 8. gambar ---
        if os.path.isdir(img_base):
            for p in (s.get("pernyataan") or []):
                if p.get("image"):
                    n_img_refs += 1
                    if not os.path.exists(img_path(img_base, p["image"])):
                        problems.append(f"#{no}: gambar pernyataan hilang {img_path(img_base, p['image'])}")
            for o in s.get("pilihan_jawaban", []):
                if o.get("image"):
                    n_img_refs += 1
                    if not os.path.exists(img_path(img_base, o["image"])):
                        problems.append(f"#{no}: gambar opsi hilang {img_path(img_base, o['image'])}")
            for i in (s.get("pertanyaan", {}).get("images") or []):
                n_img_refs += 1
                if not os.path.exists(img_path(img_base, i)):
                    problems.append(f"#{no}: gambar pertanyaan hilang {img_path(img_base, i)}")
            for i in (s.get("stimulus", {}).get("images") or []):
                n_img_refs += 1
                if not os.path.exists(img_path(img_base, i)):
                    problems.append(f"#{no}: gambar stimulus hilang {img_path(img_base, i)}")

    # --- konversi BS sesuai bukti (stmt dgn nilai Benar/Salah = B/S; lainnya = label) ---
    # Baris bukti tak ter-parse yang jelas B/S ('X (Benar)' terbaca, nilai lain
    # kosong — pola 'C ()') ikut dihitung agar tidak false-positive.
    if official is not None:
        n_bs_official = sum(
            1 for v in official.values()
            if v[0] == "stmt" and set(v[1].values()) <= {"Benar", "Salah"}
        )
        n_bs_gap = sum(
            1 for snippet in unparseable.values()
            if re.search(r"\((Benar|Salah)\s*\)", snippet)
        )
        if n_bs_official + n_bs_gap != counts["Benar-Salah"]:
            problems.append(f"B/S: dataset {counts['Benar-Salah']} != resmi {n_bs_official}+gap{n_bs_gap}")

    summary = {
        "slug": slug, "soal": len(soal), "items": n_items,
        "PG": counts["Pilihan Ganda"], "PGK": counts["Pilihan Ganda Kompleks"],
        "BS": counts["Benar-Salah"], "Label": counts["Pernyataan-Label"],
        "Matriks": counts["Matriks"],
        "img_refs": n_img_refs, "problems": problems, "notes": notes,
    }
    return summary


def main():
    all_ok = True
    T = {"soal": 0, "items": 0, "PG": 0, "PGK": 0, "BS": 0, "Label": 0, "Matriks": 0, "img": 0}
    n_notes = 0
    for slug in discover_packages():
        r = audit(slug)
        T["soal"] += r["soal"]; T["items"] += r["items"]
        T["PG"] += r["PG"]; T["PGK"] += r["PGK"]; T["BS"] += r["BS"]; T["Label"] += r["Label"]
        T["Matriks"] += r["Matriks"]
        T["img"] += r["img_refs"]; n_notes += len(r["notes"])
        status = "OK" if not r["problems"] else f"{len(r['problems'])} MASALAH"
        if r["notes"]:
            status += f" (+{len(r['notes'])} catatan)"
        print(f"{slug:32s} soal={r['soal']:3d} (PG={r['PG']:3d} PGK={r['PGK']:2d} "
              f"BS={r['BS']:2d} Label={r['Label']:2d} Mtx={r['Matriks']:2d}) "
              f"items={r['items']:3d} img={r['img_refs']:4d} -> {status}")
        for p in r["problems"][:10]:
            print("   [MASALAH]", p)
        for n in r["notes"][:4]:
            print("   (catatan)", n)
        all_ok = all_ok and not r["problems"]

    print()
    print(f"TOTAL  : {len(discover_packages())} paket | soal={T['soal']} | "
          f"PG={T['PG']} PGK={T['PGK']} BS={T['BS']} Label={T['Label']} Matriks={T['Matriks']}")
    print(f"         graded items = {T['items']} "
          f"({T['PG'] + T['PGK']} choice + {T['items'] - T['PG'] - T['PGK']} statement)")
    print(f"         image refs = {T['img']} | catatan = {n_notes}")
    print("HASIL :", "SEMUA LOLOS" if all_ok else "GAGAL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
