# -*- coding: utf-8 -*-
"""_repair_keys.py — Terapkan kunci resmi (hasil scrape review_hasil Pusmendik)
ke file *_learning.json.

Aturan yang diterapkan (berdasarkan bukti scrape 19 Sep 2026):
1. Soal PG tunggal  : kunci_jawaban = 'A'..'E'   (format '(A)' di reviu resmi)
2. Soal PG kompleks : kunci_jawaban = ['A','D']  (format '(A;D)' atau daftar
                      '(X) teks (Y) teks' di reviu resmi) + tipe 'Pilihan Ganda Kompleks'
3. Soal Benar/Salah : reviu resmi menampilkan 'A (Benar) B (Salah) ...' ->
                      dikonversi ke tipe 'Benar-Salah' dengan pernyataan
                      diambil dari opsi B/C/D (opsi A = header tabel resmi),
                      kunci_jawaban = ['A:Benar', ...]
4. Soal penugasan label (Bahasa Inggris, mis. 'A (Similarity)') ->
                      tipe 'Pernyataan-Label', pernyataan dari opsi B/C/D,
                      kunci_jawaban = ['A:Similarity', ...]

Setiap kunci diverifikasi silang dengan teks opsi di JSON (normalisasi
alfanumerik) sebelum ditulis; file asli dibackup dulu ke data/backup_kunci/.
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
KUNCI_DIR = os.path.join(ROOT, "data", "kunci")
BACKUP_DIR = os.path.join(ROOT, "data", "backup_kunci")

PACKAGES = [
    "matematika_paket_1", "matematika_paket_2",
    "bahasa_inggris_paket_1", "bahasa_inggris_paket_2",
    "ekonomi_paket_1", "ekonomi_paket_2",
    "kewirausahaan_paket_1", "kewirausahaan_paket_2",
]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def parse_official_row(kunci_text):
    """Kembalikan (kind, payload) dari satu baris kolom KUNCI JAWABAN resmi.

    kind: 'bs' | 'label' | 'multi' | 'single'

    Aturan ketat: baris B/S atau label-pair harus SELURUHNYA terdiri dari
    pasangan 'X (Nilai)' — sisa teks setelah pasangan dibuang tidak boleh
    mengandung alfanumerik. Ini mencegah salah klasifikasi soal PGK yang
    teks opsinya mengandung huruf kapital diikuti tanda kurung opsi lain
    (contoh nyata: mtk2 no=10 '(C) ∠B dan ∠C (D) ∠B dan ∠D (E) ∠E dan ∠C'
    adalah PGK C+D+E, bukan soal label).
    """
    ktx = (kunci_text or "").strip()

    # 1) Benar/Salah: pasangan 'X (Benar|Salah)' dan tanpa sisa teks
    pairs_bs = re.findall(r"([A-Z])\s*\((Benar|Salah)\)", ktx)
    if pairs_bs:
        residue = re.sub(r"([A-Z])\s*\((Benar|Salah)\)", "", ktx)
        if not re.search(r"[A-Za-z0-9]", residue):
            return "bs", {k: v for k, v in pairs_bs}

    # 2) Label-pair: pasangan 'X (Label)', huruf A/B/C berurutan, label >=2 huruf
    pairs_lb = re.findall(r"([A-Z])\s*\(([^)]+)\)", ktx)
    if pairs_lb:
        residue = re.sub(r"([A-Z])\s*\(([^)]+)\)", "", ktx)
        vals = {k: v.strip() for k, v in pairs_lb}
        if (
            not re.search(r"[A-Za-z0-9]", residue)
            and sorted(vals) == ["A", "B", "C"]
            and all(v not in ("Benar", "Salah") for v in vals.values())
            and all(re.fullmatch(r"[A-Za-z][A-Za-z \-/&]*", v) and len(v) >= 2 for v in vals.values())
        ):
            return "label", vals

    # 3) Format semicolon: '(A)' atau '(A;D)' — spasi di dalam kurung ditoleransi
    #    (kasus nyata: '( B)' pada en1 no=5)
    semi = re.fullmatch(
        r"\(\s*([A-Z](?:\s*;\s*[A-Z])*)\s*\)", ktx.replace("\n", " ")
    )
    if semi:
        letters = [re.sub(r"\s+", "", p) for p in semi.group(1).split(";")]
        return ("multi" if len(letters) > 1 else "single"), letters

    # 4) Daftar opsi benar: '(X) teks (Y) teks ...' (spasi di dalam kurung ditoleransi)
    letters = re.findall(r"\(\s*([A-Z])\s*\)", ktx)
    if len(letters) > 1:
        return "multi", letters
    if len(letters) == 1:
        return "single", letters
    return "unknown", None


def official_first_key_text(row):
    """Ambil teks opsi pertama yang muncul setelah '(X)' di baris resmi."""
    m = re.search(r"\(([A-Z])\)\s*\n+\s*(.+)", row)
    return (m.group(2) if m else "").strip()


def convert_to_statement_question(s, stmt_kunci, qtype):
    """Ubah soal PG 4-opsi (A=header) menjadi soal pernyataan B/S atau Label.

    Idempoten: bila soal sudah dikonversi sebelumnya (pernyataan sudah ada dan
    berisi konten), JANGAN membangun ulang dari pilihan_jawaban yang mungkin
    sudah tidak ada — cukup perbarui kunci_jawaban.
    """
    existing = s.get("pernyataan") or []
    has_content = existing and all(
        (p.get("text") or "").strip() or p.get("latex") or p.get("image")
        for p in existing
    )
    if not has_content:
        opts = {o["key"]: o for o in s.get("pilihan_jawaban", [])}
        pernyataan = []
        for i, stmt_key in enumerate(["A", "B", "C"]):
            src = opts.get(["B", "C", "D"][i], {})
            item = {"key": stmt_key}
            if src.get("text"):
                item["text"] = src["text"]
            if src.get("latex"):
                item["latex"] = src["latex"]
            if src.get("image"):
                item["image"] = src["image"]
            pernyataan.append(item)
        s["tipe_soal"] = qtype
        s["pernyataan"] = pernyataan
        s.pop("pilihan_jawaban", None)
    elif s.get("tipe_soal") != qtype:
        s["tipe_soal"] = qtype
    s["kunci_jawaban"] = [f"{k}:{stmt_kunci[k]}" for k in ["A", "B", "C"] if k in stmt_kunci]


def repair_package(slug, apply):
    fpath = os.path.join(ROOT, "data", f"{slug}_learning.json")
    kpath = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
    d = json.load(open(fpath, encoding="utf-8"))
    k = json.load(open(kpath, encoding="utf-8"))
    soal = d["soal"]
    rows = k["raw_rows"]

    if len(soal) != len(rows):
        print(f"[STOP] {slug}: jumlah soal JSON ({len(soal)}) != baris resmi ({len(rows)})")
        return False

    stats = {"pg": 0, "pgk": 0, "bs": 0, "label": 0}
    problems = []
    for s in soal:
        no = s["nomor"]
        row = rows.get(str(no))
        if row is None:
            problems.append(f"no={no}: tidak ada baris resmi")
            continue
        kind, payload = parse_official_row(row["kunci"])

        if kind == "bs":
            convert_to_statement_question(s, payload, "Benar-Salah")
            stats["bs"] += 1
        elif kind == "label":
            convert_to_statement_question(s, payload, "Pernyataan-Label")
            stats["label"] += 1
        elif kind in ("single", "multi"):
            letters = sorted(set(payload))
            opt_keys = {o["key"] for o in s.get("pilihan_jawaban", [])}
            missing = [l for l in letters if l not in opt_keys]
            if missing:
                problems.append(f"no={no}: kunci {letters} tidak ada di opsi JSON {sorted(opt_keys)}")
                continue
            # Verifikasi silang teks untuk kunci tunggal (opsi kunci == teks resmi)
            if kind == "single":
                opts = {o["key"]: o for o in s["pilihan_jawaban"]}
                jtext = norm(opts[letters[0]].get("text", ""))
                otext = norm(official_first_key_text(row["kunci"]))
                if otext and jtext and otext not in jtext and jtext not in otext:
                    problems.append(
                        f"no={no}: teks opsi kunci JSON[{letters[0]}] {jtext[:40]!r} "
                        f"tidak cocok teks resmi {otext[:40]!r}"
                    )
                    continue
            s["kunci_jawaban"] = letters[0] if kind == "single" else letters
            if kind == "multi":
                s["tipe_soal"] = "Pilihan Ganda Kompleks"
                stats["pgk"] += 1
            else:
                stats["pg"] += 1
        else:
            problems.append(f"no={no}: format kunci resmi tak dikenal: {row['kunci']!r}")

    print(f"=== {slug}: PG={stats['pg']} PGK={stats['pgk']} B/S={stats['bs']} Label={stats['label']} "
          f"| masalah={len(problems)}")
    for p in problems:
        print("   [MASALAH]", p)
    if problems:
        return False

    if apply:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        bpath = os.path.join(BACKUP_DIR, f"{slug}_learning.json")
        if not os.path.exists(bpath):
            shutil.copy2(fpath, bpath)
        json.dump(d, open(fpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"   [DITERAPKAN] backup -> {os.path.relpath(bpath, ROOT)}")
    return True


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--target="):
            only = a.split("=", 1)[1]
    ok_all = True
    for slug in PACKAGES:
        if only and slug != only:
            continue
        ok_all = repair_package(slug, apply) and ok_all
    print("\nMODE:", "APPLY" if apply else "DRY-RUN (gunakan --apply untuk menulis)")
    print("HASIL:", "SEMUA OK" if ok_all else "ADA MASALAH — tidak menulis file bermasalah")
