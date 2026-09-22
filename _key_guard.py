# -*- coding: utf-8 -*-
"""_key_guard.py — Invarian kunci jawaban untuk seluruh pipeline.

PRINSIP:
    AI enrichment boleh memperkaya soal (penjelasan, glosarium, tips,
    soal_serupa, metadata belajar), tetapi TIDAK BOLEH menentukan atau
    menimpa kunci jawaban otoritatif (kunci_jawaban).

Sumber kunci yang sah:
    1. kunci_jawaban yang SUDAH ADA di dataset  -> dipertahankan
    2. kunci resmi hasil scrape: data/kunci/<slug>_kunci.json
       (isian kolom KUNCI JAWABAN review_hasil Pusmendik)

Segala bentuk kunci lain (huruf hardcoded, tabel pedagogy, keluaran AI)
DILARANG dan akan ditolak dengan error yang jelas.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
KUNCI_DIR = os.path.join(ROOT, "data", "kunci")

# Classifier resmi yang sama dipakai _repair_keys.py (satu sumber kebenaran)
from _repair_keys import parse_official_row  # noqa: E402


def slug_from_output(path):
    base = os.path.basename(str(path))
    if base.endswith("_learning.json"):
        slug = base[: -len("_learning.json")]
    else:
        slug = os.path.splitext(base)[0]
    # Alias file legasi matematika: data/paket_1_learning.json & data/paket_2_learning.json
    # adalah salinan matematika_paket_1/2 (app.js tidak memuatnya langsung).
    return {"paket_1": "matematika_paket_1", "paket_2": "matematika_paket_2"}.get(slug, slug)


def _canon(k):
    """Bentuk kanonik kunci untuk perbandingan antar-format."""
    if k is None:
        return None
    if isinstance(k, str):
        s = k.strip().upper()
        if s in ("", "-"):
            return None
        return ("single", s)
    if isinstance(k, list):
        if not k:
            return None
        if all(":" in str(x) for x in k):
            return ("stmt", {str(x).split(":", 1)[0].strip().upper(): str(x).split(":", 1)[1].strip() for x in k})
        return ("multi", sorted(str(x).strip().upper() for x in k))
    return ("raw", str(k))


def official_canonical_map(slug):
    """Peta {nomor: bentuk-kanonik} dari bukti scrape resmi (raw_rows).

    Membaca raw_rows (bukan kunci_pg) karena kunci_pg hasil scraper lama
    hanya menyimpan huruf PERTAMA untuk soal multi-jawaban.
    """
    p = os.path.join(KUNCI_DIR, f"{slug}_kunci.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    if "raw_rows" not in d:
        raise SystemExit(f"[GUARD] {p} tidak memiliki raw_rows — bukan bukti resmi yang valid.")
    out = {}
    for no_str, row in d["raw_rows"].items():
        kind, payload = parse_official_row(row.get("kunci", ""))
        if kind == "single":
            out[int(no_str)] = ("single", payload[0])
        elif kind == "multi":
            out[int(no_str)] = ("multi", sorted(payload))
        elif kind in ("bs", "label"):
            out[int(no_str)] = ("stmt", {k.strip(): v.strip() for k, v in payload.items()})
        # kind 'unknown' -> dilewati; enforce akan memperlakukannya sbg tanpa kunci resmi
    return out


def _restore_official(off):
    """Bentuk kanonik -> format kunci_jawaban sesuai tipe soal."""
    kind, payload = off
    if kind == "single":
        return payload
    if kind == "multi":
        return list(payload)
    # stmt: urutkan A, B, C agar konsisten
    return [f"{k}:{payload[k]}" for k in sorted(payload)]


def enforce_answer_key_invariant(soal_list, slug, allow_missing=False, force_official=False, quiet=False):
    """Terapkan invarian kunci pada satu dataset.

    - kunci ada & cocok dgn resmi   -> dipertahankan
    - kunci ada & BERBEDA dari resmi -> GAGAL KERAS (alarm korupsi),
      kecuali force_official=True (penggantian eksplisit dgn kunci resmi)
    - kunci hilang, resmi tersedia  -> diisi dari resmi
    - kunci hilang, resmi tiada     -> GAGAL KERAS, kecuali allow_missing=True
      (soal dibiarkan TANPA kunci; tidak pernah dikarang)

    Return dict ringkasan. Tidak pernah mengarang kunci.
    """
    official = official_canonical_map(slug)
    conflicts, missing, filled, preserved, legacy = [], [], 0, 0, 0
    for q in soal_list:
        no = q.get("nomor")
        cur = _canon(q.get("kunci_jawaban"))
        off = official.get(no) if official else None

        if cur is None:
            if off is None:
                missing.append(no)
            elif off[0] == "stmt" and not isinstance(q.get("kunci_jawaban"), list):
                # butuh konversi tipe soal -> bukan ranah enrichment
                missing.append(no)
            else:
                q["kunci_jawaban"] = _restore_official(off)
                filled += 1
            continue

        if off is None:
            legacy += 1  # kunci lama tanpa bukti resmi utk slug ini: dipertahankan apa adanya
            continue
        if cur == off:
            preserved += 1
            continue
        conflicts.append((no, cur, off))

    if conflicts:
        lines = [f"[KUNCI BERTENTANGAN DGN SUMBER RESMI] {slug}: {len(conflicts)} soal"]
        for no, cur, off in conflicts[:12]:
            lines.append(f"  no={no}: dataset={cur!r} vs resmi={off!r}")
        lines.append(
            "  Enrichment tidak boleh menimpa kunci otoritatif. "
            "Jika benar-benar ingin menimpa dgn kunci resmi, jalankan ulang dengan --force-official."
        )
        raise SystemExit("\n".join(lines))

    if missing:
        msg = (
            f"[KUNCI RESMI TIDAK TERSEDIA] {slug}: {len(missing)} soal tanpa kunci "
            f"(nomor {missing[:10]}{'...' if len(missing) > 10 else ''}). "
            f"Enrichment TIDAK BOLEH mengarang kunci. Jalankan 'python scrape_kunci.py "
            f"--target {slug}' lalu merge, atau jalankan _repair_keys.py."
        )
        if allow_missing:
            if not quiet:
                print("[PERINGATAN] " + msg + " (--allow-missing-keys: soal dibiarkan tanpa kunci)")
        else:
            raise SystemExit(msg)

    summary = {
        "slug": slug,
        "preserved": preserved,
        "filled_from_official": filled,
        "legacy_without_evidence": legacy,
        "missing": len(missing),
    }
    if not quiet:
        print(f"   [GUARD:{slug}] dipertahankan={preserved} diisi-dari-resmi={filled} "
              f"legasi-tanpa-bukti={legacy} tanpa-kunci={len(missing)}")
    return summary


if __name__ == "__main__":
    print("Modul guard — import dari script enrichment, bukan dijalankan langsung.")
    sys.exit(0)
