# -*- coding: utf-8 -*-
"""Smoke test HTTP: integrasi Layer 3 aktif (registry solusi Claude) end-to-end.

Diverifikasi (arsitektur tiga lapis + sumber aktif):
  - /api/solution  -> status "success" dengan konten solusi spesifik soal dari
    sumber AKTIF (EXTRA); kunci tampilan tetap otoritatif; review flag dipertahankan;
    paket tanpa sumber tetap "pending" dengan state jujur (bukan konten legacy).
  - /api/ai-tutor  -> menerima Layer 2 (kanonis) + Layer 3 aktif; balasan spesifik
    soal; konten legacy dalam question_data TIDAK pernah bocor.
"""
import json
import sys
import threading
import time
import urllib.request

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

# --- 3. /api/ai-tutor: Layer 2 + Layer 3 aktif --------------------------------
r = post("/api/ai-tutor", {
    "subject": "matematika", "paket": 2, "nomor": 2,
    "message": "kenapa jawabannya C?",
    "question_data": {
        "topik": "Eksponen", "subject": "matematika",
        "pembahasan": {"mengapa_begini": "LEGACY-ALASAN-GENERIK",
                       "tips_trik": "LEGACY-TIPS-GENERIK",
                       "konsep_kunci": "LEGACY-KONSEP-GENERIK"},
    },
})
reply = r["reply"]
check("tutor Q2 'kenapa C': konten spesifik (basis prima)",
      "basis" in reply.lower() and "8" in reply)
check("tutor Q2: TIDAK ada kebocoran legacy", "LEGACY" not in reply)

r = post("/api/ai-tutor", {
    "subject": "matematika", "paket": 2, "nomor": 3,
    "message": "jelasin langkah penyelesaiannya",
    "question_data": {"topik": "Operasi", "subject": "matematika"},
})
check("tutor Q3 'langkah': langkah spesifik a⊙b", "\\odot" in r["reply"])

r = post("/api/ai-tutor", {
    "subject": "matematika", "paket": 2, "nomor": 3,
    "message": "apa arti simbolnya?",
    "question_data": {"topik": "Operasi", "subject": "matematika"},
})
check("tutor Q3 'simbol': glosarium spesifik dari Layer 3",
      "operasi biner" in r["reply"].lower() and "odot" in r["reply"])

r = post("/api/ai-tutor", {
    "subject": "matematika", "paket": 2, "nomor": 5,
    "message": "kenapa jawabannya B?",
    "question_data": {"topik": "Fungsi", "subject": "matematika"},
})
check("tutor Q5 (review): catatan verifikasi manual disertakan",
      "verifikasi manual" in r["reply"])

r = post("/api/ai-tutor", {
    "subject": "matematika", "paket": 2, "nomor": 1,
    "message": "konsep apa yang dipakai?",
    "question_data": {"topik": "Himpunan", "subject": "matematika"},
})
check("tutor Q1 'konsep': konsep kunci spesifik (irisan/gabungan)",
      "irisan" in r["reply"].lower())

r = post("/api/ai-tutor", {
    "subject": "ekonomi", "paket": 1, "nomor": 1,
    "message": "bagaimana langkah pengerjaannya?",
    "question_data": {"topik": "Ekonomi", "subject": "ekonomi"},
})
check("tutor eko1 Q1 (tanpa Layer 3): jujur belum tersedia",
      "belum tersedia" in r["reply"])

print()
total = len(results)
ok = sum(1 for _, c, _ in results if c)
print(f"SMOKE: {ok}/{total} PASS")
sys.exit(0 if ok == total else 1)
