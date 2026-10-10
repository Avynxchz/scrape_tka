# -*- coding: utf-8 -*-
"""pipeline/subject_catalog.py — Master Subject & Package Catalog for Pusmendik TKA.

Contains all official subject definitions, Jenjang, Jenis Mapel, and Value IDs
extracted directly from Pusmendik Simulasi TKA dropdown.
Provides dynamic detection of 'live' vs 'unscraped' packages.
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

MASTER_CATALOG = {
    # =========================================================================
    # WAJIB (JENIS MAPEL: 1)
    # =========================================================================
    "matematika_paket_1": {
        "slug": "matematika_paket_1", "mapel_key": "matematika", "paket": 1, "prefix": "mtk",
        "name": "Matematika (Paket 1)", "jenis": "1", "val": "7", "kategori": "Wajib"
    },
    "matematika_paket_2": {
        "slug": "matematika_paket_2", "mapel_key": "matematika", "paket": 2, "prefix": "mtk",
        "name": "Matematika (Paket 2)", "jenis": "1", "val": "82", "kategori": "Wajib"
    },
    "bahasa_indonesia_paket_1": {
        "slug": "bahasa_indonesia_paket_1", "mapel_key": "bahasa_indonesia", "paket": 1, "prefix": "ind",
        "name": "Bahasa Indonesia (Paket 1)", "jenis": "1", "val": "2", "kategori": "Wajib"
    },
    "bahasa_indonesia_paket_2": {
        "slug": "bahasa_indonesia_paket_2", "mapel_key": "bahasa_indonesia", "paket": 2, "prefix": "ind",
        "name": "Bahasa Indonesia (Paket 2)", "jenis": "1", "val": "83", "kategori": "Wajib"
    },
    "bahasa_inggris_paket_1": {
        "slug": "bahasa_inggris_paket_1", "mapel_key": "bahasa_inggris", "paket": 1, "prefix": "ing",
        "name": "Bahasa Inggris (Paket 1)", "jenis": "1", "val": "3", "kategori": "Wajib"
    },
    "bahasa_inggris_paket_2": {
        "slug": "bahasa_inggris_paket_2", "mapel_key": "bahasa_inggris", "paket": 2, "prefix": "ing",
        "name": "Bahasa Inggris (Paket 2)", "jenis": "1", "val": "84", "kategori": "Wajib"
    },

    # =========================================================================
    # SAINTEK PILIHAN (JENIS MAPEL: 2)
    # =========================================================================
    "matematika_lanjut_paket_1": {
        "slug": "matematika_lanjut_paket_1", "mapel_key": "matematika_lanjut", "paket": 1, "prefix": "mtkl",
        "name": "Matematika Tingkat Lanjut (Paket 1)", "jenis": "2", "val": "4", "kategori": "Saintek Pilihan"
    },
    "matematika_lanjut_paket_2": {
        "slug": "matematika_lanjut_paket_2", "mapel_key": "matematika_lanjut", "paket": 2, "prefix": "mtkl",
        "name": "Matematika Tingkat Lanjut (Paket 2)", "jenis": "2", "val": "85", "kategori": "Saintek Pilihan"
    },
    "fisika_paket_1": {
        "slug": "fisika_paket_1", "mapel_key": "fisika", "paket": 1, "prefix": "fis",
        "name": "Fisika (Paket 1)", "jenis": "2", "val": "8", "kategori": "Saintek Pilihan"
    },
    "fisika_paket_2": {
        "slug": "fisika_paket_2", "mapel_key": "fisika", "paket": 2, "prefix": "fis",
        "name": "Fisika (Paket 2)", "jenis": "2", "val": "88", "kategori": "Saintek Pilihan"
    },
    "kimia_paket_1": {
        "slug": "kimia_paket_1", "mapel_key": "kimia", "paket": 1, "prefix": "kim",
        "name": "Kimia (Paket 1)", "jenis": "2", "val": "9", "kategori": "Saintek Pilihan"
    },
    "kimia_paket_2": {
        "slug": "kimia_paket_2", "mapel_key": "kimia", "paket": 2, "prefix": "kim",
        "name": "Kimia (Paket 2)", "jenis": "2", "val": "89", "kategori": "Saintek Pilihan"
    },
    "biologi_paket_1": {
        "slug": "biologi_paket_1", "mapel_key": "biologi", "paket": 1, "prefix": "bio",
        "name": "Biologi (Paket 1)", "jenis": "2", "val": "10", "kategori": "Saintek Pilihan"
    },
    "biologi_paket_2": {
        "slug": "biologi_paket_2", "mapel_key": "biologi", "paket": 2, "prefix": "bio",
        "name": "Biologi (Paket 2)", "jenis": "2", "val": "90", "kategori": "Saintek Pilihan"
    },

    # =========================================================================
    # SOSHUM PILIHAN (JENIS MAPEL: 2)
    # =========================================================================
    "ekonomi_paket_1": {
        "slug": "ekonomi_paket_1", "mapel_key": "ekonomi", "paket": 1, "prefix": "eko",
        "name": "Ekonomi (Paket 1)", "jenis": "2", "val": "12", "kategori": "Soshum Pilihan"
    },
    "ekonomi_paket_2": {
        "slug": "ekonomi_paket_2", "mapel_key": "ekonomi", "paket": 2, "prefix": "eko",
        "name": "Ekonomi (Paket 2)", "jenis": "2", "val": "92", "kategori": "Soshum Pilihan"
    },
    "geografi_paket_1": {
        "slug": "geografi_paket_1", "mapel_key": "geografi", "paket": 1, "prefix": "geo",
        "name": "Geografi (Paket 1)", "jenis": "2", "val": "13", "kategori": "Soshum Pilihan"
    },
    "geografi_paket_2": {
        "slug": "geografi_paket_2", "mapel_key": "geografi", "paket": 2, "prefix": "geo",
        "name": "Geografi (Paket 2)", "jenis": "2", "val": "93", "kategori": "Soshum Pilihan"
    },
    "sosiologi_paket_1": {
        "slug": "sosiologi_paket_1", "mapel_key": "sosiologi", "paket": 1, "prefix": "sos",
        "name": "Sosiologi (Paket 1)", "jenis": "2", "val": "14", "kategori": "Soshum Pilihan"
    },
    "sosiologi_paket_2": {
        "slug": "sosiologi_paket_2", "mapel_key": "sosiologi", "paket": 2, "prefix": "sos",
        "name": "Sosiologi (Paket 2)", "jenis": "2", "val": "94", "kategori": "Soshum Pilihan"
    },
    "sejarah_paket_1": {
        "slug": "sejarah_paket_1", "mapel_key": "sejarah", "paket": 1, "prefix": "sej",
        "name": "Sejarah (Paket 1)", "jenis": "2", "val": "15", "kategori": "Soshum Pilihan"
    },
    "sejarah_paket_2": {
        "slug": "sejarah_paket_2", "mapel_key": "sejarah", "paket": 2, "prefix": "sej",
        "name": "Sejarah (Paket 2)", "jenis": "2", "val": "95", "kategori": "Soshum Pilihan"
    },
    "antropologi_paket_1": {
        "slug": "antropologi_paket_1", "mapel_key": "antropologi", "paket": 1, "prefix": "ant",
        "name": "Antropologi (Paket 1)", "jenis": "2", "val": "16", "kategori": "Soshum Pilihan"
    },
    "antropologi_paket_2": {
        "slug": "antropologi_paket_2", "mapel_key": "antropologi", "paket": 2, "prefix": "ant",
        "name": "Antropologi (Paket 2)", "jenis": "2", "val": "96", "kategori": "Soshum Pilihan"
    },
    "ppkn_paket_1": {
        "slug": "ppkn_paket_1", "mapel_key": "ppkn", "paket": 1, "prefix": "ppk",
        "name": "Pendidikan Pancasila & Kewarganegaraan (Paket 1)", "jenis": "2", "val": "11", "kategori": "Lintas Minat"
    },
    "ppkn_paket_2": {
        "slug": "ppkn_paket_2", "mapel_key": "ppkn", "paket": 2, "prefix": "ppk",
        "name": "Pendidikan Pancasila & Kewarganegaraan (Paket 2)", "jenis": "2", "val": "91", "kategori": "Lintas Minat"
    },

    # =========================================================================
    # BAHASA TINGKAT LANJUT & BAHASA ASING (JENIS MAPEL: 2)
    # =========================================================================
    "bahasa_indonesia_lanjut_paket_1": {
        "slug": "bahasa_indonesia_lanjut_paket_1", "mapel_key": "bahasa_indonesia_lanjut", "paket": 1, "prefix": "indl",
        "name": "Bahasa Indonesia Tingkat Lanjut (Paket 1)", "jenis": "2", "val": "5", "kategori": "Bahasa Tingkat Lanjut"
    },
    "bahasa_indonesia_lanjut_paket_2": {
        "slug": "bahasa_indonesia_lanjut_paket_2", "mapel_key": "bahasa_indonesia_lanjut", "paket": 2, "prefix": "indl",
        "name": "Bahasa Indonesia Tingkat Lanjut (Paket 2)", "jenis": "2", "val": "86", "kategori": "Bahasa Tingkat Lanjut"
    },
    "bahasa_inggris_lanjut_paket_1": {
        "slug": "bahasa_inggris_lanjut_paket_1", "mapel_key": "bahasa_inggris_lanjut", "paket": 1, "prefix": "ingl",
        "name": "Bahasa Inggris Tingkat Lanjut (Paket 1)", "jenis": "2", "val": "6", "kategori": "Bahasa Tingkat Lanjut"
    },
    "bahasa_inggris_lanjut_paket_2": {
        "slug": "bahasa_inggris_lanjut_paket_2", "mapel_key": "bahasa_inggris_lanjut", "paket": 2, "prefix": "ingl",
        "name": "Bahasa Inggris Tingkat Lanjut (Paket 2)", "jenis": "2", "val": "87", "kategori": "Bahasa Tingkat Lanjut"
    },
    "bahasa_arab_paket_1": {
        "slug": "bahasa_arab_paket_1", "mapel_key": "bahasa_arab", "paket": 1, "prefix": "ara",
        "name": "Bahasa Arab (Paket 1)", "jenis": "2", "val": "22", "kategori": "Bahasa Asing"
    },
    "bahasa_arab_paket_2": {
        "slug": "bahasa_arab_paket_2", "mapel_key": "bahasa_arab", "paket": 2, "prefix": "ara",
        "name": "Bahasa Arab (Paket 2)", "jenis": "2", "val": "102", "kategori": "Bahasa Asing"
    },
    "bahasa_jepang_paket_1": {
        "slug": "bahasa_jepang_paket_1", "mapel_key": "bahasa_jepang", "paket": 1, "prefix": "jpn",
        "name": "Bahasa Jepang (Paket 1)", "jenis": "2", "val": "19", "kategori": "Bahasa Asing"
    },
    "bahasa_jepang_paket_2": {
        "slug": "bahasa_jepang_paket_2", "mapel_key": "bahasa_jepang", "paket": 2, "prefix": "jpn",
        "name": "Bahasa Jepang (Paket 2)", "jenis": "2", "val": "99", "kategori": "Bahasa Asing"
    },
    "bahasa_jerman_paket_1": {
        "slug": "bahasa_jerman_paket_1", "mapel_key": "bahasa_jerman", "paket": 1, "prefix": "ger",
        "name": "Bahasa Jerman (Paket 1)", "jenis": "2", "val": "18", "kategori": "Bahasa Asing"
    },
    "bahasa_jerman_paket_2": {
        "slug": "bahasa_jerman_paket_2", "mapel_key": "bahasa_jerman", "paket": 2, "prefix": "ger",
        "name": "Bahasa Jerman (Paket 2)", "jenis": "2", "val": "98", "kategori": "Bahasa Asing"
    },
    "bahasa_prancis_paket_1": {
        "slug": "bahasa_prancis_paket_1", "mapel_key": "bahasa_prancis", "paket": 1, "prefix": "fra",
        "name": "Bahasa Prancis (Paket 1)", "jenis": "2", "val": "17", "kategori": "Bahasa Asing"
    },
    "bahasa_prancis_paket_2": {
        "slug": "bahasa_prancis_paket_2", "mapel_key": "bahasa_prancis", "paket": 2, "prefix": "fra",
        "name": "Bahasa Prancis (Paket 2)", "jenis": "2", "val": "97", "kategori": "Bahasa Asing"
    },
    "bahasa_mandarin_paket_1": {
        "slug": "bahasa_mandarin_paket_1", "mapel_key": "bahasa_mandarin", "paket": 1, "prefix": "man",
        "name": "Bahasa Mandarin (Paket 1)", "jenis": "2", "val": "20", "kategori": "Bahasa Asing"
    },
    "bahasa_mandarin_paket_2": {
        "slug": "bahasa_mandarin_paket_2", "mapel_key": "bahasa_mandarin", "paket": 2, "prefix": "man",
        "name": "Bahasa Mandarin (Paket 2)", "jenis": "2", "val": "100", "kategori": "Bahasa Asing"
    },
    "bahasa_korea_paket_1": {
        "slug": "bahasa_korea_paket_1", "mapel_key": "bahasa_korea", "paket": 1, "prefix": "kor",
        "name": "Bahasa Korea (Paket 1)", "jenis": "2", "val": "21", "kategori": "Bahasa Asing"
    },
    "bahasa_korea_paket_2": {
        "slug": "bahasa_korea_paket_2", "mapel_key": "bahasa_korea", "paket": 2, "prefix": "kor",
        "name": "Bahasa Korea (Paket 2)", "jenis": "2", "val": "101", "kategori": "Bahasa Asing"
    },

    # =========================================================================
    # KEWIRAUSAHAAN & KEJURUAN SMK (JENIS MAPEL: 2)
    # =========================================================================
    "kewirausahaan_paket_1": {
        "slug": "kewirausahaan_paket_1", "mapel_key": "kewirausahaan", "paket": 1, "prefix": "pkk",
        "name": "Kewirausahaan / PKK (Paket 1)", "jenis": "2", "val": "23", "kategori": "Kejuruan SMK"
    },
    "kewirausahaan_paket_2": {
        "slug": "kewirausahaan_paket_2", "mapel_key": "kewirausahaan", "paket": 2, "prefix": "pkk",
        "name": "Kewirausahaan / PKK (Paket 2)", "jenis": "2", "val": "103", "kategori": "Kejuruan SMK"
    },
    "teknik_mesin_paket_1": {
        "slug": "teknik_mesin_paket_1", "mapel_key": "teknik_mesin", "paket": 1, "prefix": "tms",
        "name": "SMK - Teknik Mesin", "jenis": "2", "val": "33", "kategori": "Kejuruan SMK"
    },
    "teknik_otomotif_paket_1": {
        "slug": "teknik_otomotif_paket_1", "mapel_key": "teknik_otomotif", "paket": 1, "prefix": "tot",
        "name": "SMK - Teknik Otomotif", "jenis": "2", "val": "34", "kategori": "Kejuruan SMK"
    },
    "teknik_jaringan_paket_1": {
        "slug": "teknik_jaringan_paket_1", "mapel_key": "teknik_jaringan", "paket": 1, "prefix": "tkj",
        "name": "SMK - Teknik Jaringan dan Telekomunikasi", "jenis": "2", "val": "49", "kategori": "Kejuruan SMK"
    },
    "akuntansi_paket_1": {
        "slug": "akuntansi_paket_1", "mapel_key": "akuntansi", "paket": 1, "prefix": "akl",
        "name": "SMK - Akuntansi dan Keuangan Lembaga", "jenis": "2", "val": "66", "kategori": "Kejuruan SMK"
    },
    "manajemen_perkantoran_paket_1": {
        "slug": "manajemen_perkantoran_paket_1", "mapel_key": "manajemen_perkantoran", "paket": 1, "prefix": "mplb",
        "name": "SMK - Manajemen Perkantoran dan Layanan Bisnis", "jenis": "2", "val": "65", "kategori": "Kejuruan SMK"
    }
}


def check_is_live(slug):
    """Checks if a learning JSON exists and has valid questions."""
    lrn_path = os.path.join(DATA_DIR, f"{slug}_learning.json")
    if os.path.isfile(lrn_path) and os.path.getsize(lrn_path) > 500:
        try:
            with open(lrn_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                return len(d.get("soal", [])) > 0
        except Exception:
            return False
    return False


def get_full_catalog():
    """Returns the master catalog with live statuses and question counts."""
    catalog = {}
    live_count = 0
    unscraped_count = 0

    for slug, item in MASTER_CATALOG.items():
        is_live = check_is_live(slug)
        entry = dict(item)
        entry["status"] = "live" if is_live else "unscraped"
        if is_live:
            live_count += 1
            # Read question count
            try:
                lrn_p = os.path.join(DATA_DIR, f"{slug}_learning.json")
                with open(lrn_p, "r", encoding="utf-8") as f:
                    entry["question_count"] = len(json.load(f).get("soal", []))
            except Exception:
                entry["question_count"] = 0
        else:
            unscraped_count += 1
            entry["question_count"] = 0

        catalog[slug] = entry

    return {
        "summary": {
            "total_packages": len(catalog),
            "live_packages": live_count,
            "unscraped_packages": unscraped_count,
            "categories": sorted(list(set(x["kategori"] for x in catalog.values())))
        },
        "subjects": catalog
    }


def get_unscraped_subjects():
    """Returns only unscraped subjects."""
    full = get_full_catalog()
    return {k: v for k, v in full["subjects"].items() if v["status"] == "unscraped"}
