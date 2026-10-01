# -*- coding: utf-8 -*-
"""_fix_render_data_20260929.py — pembersihan idempoten field user-visible di data aktif.

Prinsip:
- Backup dulu (data/backup_render_fix_20260929_v2/, struktur relatif dipertahankan).
- Hanya string yang TERDETEKSI kotor yang diubah (diff minimal).
- Field 'data_latex' (atribut LaTeX milik gambar) tidak disentuh.
- Field 'html' hanya perbaikan ringan (mojibake + unicode math italic), tanpa full repair
  supaya markup tidak rusak.
- Full repair (text_quality.repair_math_text) untuk field teks biasa.
- Setelah tulis: json.load() ulang semua file yang diubah (validitas JSON).
"""
import io
import json
import os
import re
import shutil
import sys

sys.path.insert(0, r"D:\PROJECTS\SCRAPE_TKA")
import text_quality

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA = r"D:\PROJECTS\SCRAPE_TKA\data"
BACKUP = os.path.join(DATA, "backup_render_fix_20260929_v2")

MATH_ITALIC = re.compile(r"[\U0001D400-\U0001D7FF\u210E\u210F\u2113]")
MOJIBAKE_DEG = "\u00c2\u00b0"          # Â°
WORD_SYMBOLS = re.compile(
    r"(?<![\w\\])(rightarrow|leftarrow|tfrac|dfrac|cdot|pm(?![a-z])|neq|leq|geq|approx)(?![\w])"
)
TOKEN_ECHO = re.compile(r"(\b\w[\w°×±≠≤≥≈·/]{0,30}\b) ?\1")


def is_dirty_html(s):
    return bool(MOJIBAKE_DEG in s or MATH_ITALIC.search(s))


def is_dirty_text(s):
    if MOJIBAKE_DEG in s or MATH_ITALIC.search(s):
        return True
    # pola kata-LaTeX di luar segmen $...$
    parts = re.split(r"(\$\$[\s\S]*?\$\$|\$[^$\n]*?\$)", s)
    for i, p in enumerate(parts):
        if i % 2 == 1:
            continue
        if WORD_SYMBOLS.search(p):
            return True
    if TOKEN_ECHO.search(s):
        return True
    return False


def fix_light(s):
    """Untuk field html: mojibake + unicode italic -> ASCII."""
    s = s.replace(MOJIBAKE_DEG, "\u00b0")
    s = text_quality.map_math_unicode(s)
    return s


def fix_full(s):
    s = s.replace(MOJIBAKE_DEG, "\u00b0")
    return text_quality.repair_math_text(s)


changed_files = {}


def backup(path):
    rel = os.path.relpath(path, DATA)
    dst = os.path.join(BACKUP, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        shutil.copy2(path, dst)


def process_file(path, is_solution):
    rel = os.path.relpath(path, DATA)
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    stats = {"light": 0, "full": 0, "skipped_latex": 0}

    def walk(o, key=None):
        if isinstance(o, str):
            return o  # diganti lewat dict/list handler
        if isinstance(o, list):
            return [walk(v, key) for v in o]
        if isinstance(o, dict):
            out = {}
            for k, v in o.items():
                if k == "data_latex" and isinstance(v, str):
                    stats["skipped_latex"] += 1
                    out[k] = v
                elif isinstance(v, str):
                    if k == "html":
                        if is_dirty_html(v):
                            nv = fix_light(v)
                            if nv != v:
                                stats["light"] += 1
                            out[k] = nv
                        else:
                            out[k] = v
                    else:
                        if is_dirty_text(v):
                            nv = fix_full(v)
                            if nv != v:
                                stats["full"] += 1
                            out[k] = nv
                        else:
                            out[k] = v
                else:
                    out[k] = walk(v, k)
            return out
        return o

    nd = walk(d)
    if stats["light"] or stats["full"]:
        backup(path)
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(nd, f, ensure_ascii=False, indent=2)
        json.load(io.open(path, encoding="utf-8"))  # validasi
        changed_files[rel] = stats
        print(f"[FIXED] {rel}: full={stats['full']} light={stats['light']} skipped_latex={stats['skipped_latex']}")
    else:
        print(f"[clean] {rel}")


# 1) Semua learning JSON aktif
learning = sorted(
    f for f in os.listdir(DATA)
    if f.endswith("_learning.json") and os.path.isfile(os.path.join(DATA, f))
)
for f in learning:
    process_file(os.path.join(DATA, f), False)

# 2) File solusi aktif dari registry
reg_path = os.path.join(DATA, "solution_sources", "registry.json")
reg = json.load(io.open(reg_path, encoding="utf-8"))
seen = set()
for key, meta in reg.items():
    if key.startswith("_") or not isinstance(meta, dict):
        continue
    fn = meta.get("active_source")
    if not fn or fn in seen:
        continue
    seen.add(fn)
    p = os.path.join(DATA, "solution_sources", fn)
    if os.path.isfile(p):
        process_file(p, True)

print()
print(f"TOTAL file diubah: {len(changed_files)}")
for rel, st in changed_files.items():
    print(f"  {rel}: full={st['full']} light={st['light']}")
