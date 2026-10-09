# -*- coding: utf-8 -*-
"""Smoke test HTTP: struktur + endpoint aktif.

Tes regresi 0 (AST) jalan duluan untuk cegah bug indentasi.

Diverifikasi (arsitektur tiga lapis + sumber aktif):
  - /api/solution  -> status "success" dengan konten solusi spesifik soal dari
    sumber AKTIF (EXTRA); kunci tampilan tetap otoritatif; review flag dipertahankan;
    paket tanpa sumber tetap "pending" dengan state jujur (bukan konten legacy).
"""
import ast
import json
import os
import sys
import threading
import time
import urllib.request

# --- Tes regresi 0: struktur server.py (cegah bug indentasi terulang) ---------
# Bug 2026-10-09: _verify_supabase_token nyelip di tengah class AppRequestHandler,
# bikin do_GET/do_POST jadi nested function. Server nyala tapi routing mati.
# Tes ini jalan SEBELUM import server, jadi tidak butuh dependensi.
_results0 = []
def _check0(name, cond, detail=""):
    _results0.append((name, bool(cond), detail))
    print(("PASS" if cond else "FAIL"), "-", name, ("| " + detail if detail and not cond else ""))

_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py"),
            encoding="utf-8").read()
_tree = ast.parse(_src)
_handler = None
for _node in ast.walk(_tree):
    if isinstance(_node, ast.ClassDef) and _node.name == "AppRequestHandler":
        _handler = _node
        break
_methods = [n.name for n in _handler.body if isinstance(n, ast.FunctionDef)] if _handler else []
_check0("AppRequestHandler punya do_GET", "do_GET" in _methods)
_check0("AppRequestHandler punya do_POST", "do_POST" in _methods)
_check0("AppRequestHandler punya do_OPTIONS", "do_OPTIONS" in _methods)
_modfuncs = [n.name for n in _tree.body if isinstance(n, ast.FunctionDef)]
_check0("_verify_supabase_token di level modul (bukan di dalam class)",
         "_verify_supabase_token" in _modfuncs and "_verify_supabase_token" not in _methods)
if not all(c for _, c, _ in _results0):
    print("STRUKTUR: gagal — perbaiki indentasi server.py sebelum push")
    sys.exit(1)
print("STRUKTUR: OK")
print()

sys.path.insert(0, ".")
import server  # noqa: E402

PORT = 8891
server.PORT = PORT
httpd = server.ThreadingHTTPServer(("", PORT), server.AppRequestHandler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()
time.sleep(0.5)


def post(path, body):
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS" if cond else "FAIL"), "-", name, ("| " + detail if detail and not cond else ""))


# --- 1. /api/solution: Layer 3 aktif (EXTRA) untuk Matematika Paket 2 ---------
d = post("/api/solution", {"subject": "matematika", "paket": 2, "nomor": 2})
check("mtk2 Q2: status success (sumber aktif EXTRA)", d["status"] == "success", str(d["status"]))
p = d.get("solution", {}).get("pembahasan", {})
check("mtk2 Q2: langkah = eksponen pecahan (spesifik Q2)",
      any("2^{9/2}" in s for s in p.get("langkah_penyelesaian", [])))
check("mtk2 Q2: kunci tampilan = otoritatif (C)",
      d["solution"]["answer_display"] == "C")
check("mtk2 Q2: sumber tercatat = EXTRA",
      d["solution"]["source"]["file"] == "MTK_PAKET_2_SOLUTIONS_EXTRA.json")
check("mtk2 Q2: cross-check kunci cocok",
      d["solution"]["key_crosscheck"]["match"] is True)
check("mtk2 Q2: formula Layer 2 tetap terkirim",
      any("3^{" in f["latex"] for f in d.get("formulas", [])))

d = post("/api/solution", {"subject": "matematika", "paket": 2, "nomor": 3})
p3 = d.get("solution", {}).get("pembahasan", {})
check("mtk2 Q3: langkah = operasi a⊙b (spesifik Q3)",
      any("\\odot" in s for s in p3.get("langkah_penyelesaian", [])))
check("mtk2 Q3: kunci pernyataan otoritatif tampil",
      "Benar" in d["solution"]["answer_display"] and "Salah" in d["solution"]["answer_display"])
check("mtk2 Q3: konten Q2 tidak bocor",
      all("2^{9/2}" not in s for s in p3.get("langkah_penyelesaian", [])))

d = post("/api/solution", {"subject": "matematika", "paket": 2, "nomor": 5})
check("mtk2 Q5: needs_manual_review = true dipertahankan",
      d["solution"]["review"]["needs_manual_review"] is True)
check("mtk2 Q5: konten tetap disajikan (bukan dihapus)",
      len(d["solution"]["pembahasan"]["langkah_penyelesaian"]) >= 4)

d = post("/api/solution", {"subject": "matematika", "paket": 2, "nomor": 14})
check("mtk2 Q14: review flag + konten langkah dipertahankan",
      d["solution"]["review"]["needs_manual_review"] is True
      and len(d["solution"]["pembahasan"]["langkah_penyelesaian"]) >= 3)

# --- 2. /api/solution: paket TANPA sumber -> state jujur (bukan legacy) -------
d = post("/api/solution", {"subject": "ekonomi", "paket": 1, "nomor": 1})
check("eko1 Q1: status pending (tanpa sumber aktif)", d["status"] == "pending")
check("eko1 Q1: solution = null", d["solution"] is None)
check("eko1 Q1: visual Layer 2 tetap terkirim",
      isinstance(d.get("visual_items"), list))

print()
total = len(results)
ok = sum(1 for _, c, _ in results if c)
print(f"SMOKE: {ok}/{total} PASS")
sys.exit(0 if ok == total else 1)
