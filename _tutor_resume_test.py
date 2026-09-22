# -*- coding: utf-8 -*-
"""Uji RESUME percakapan: cookiejar sungguhan (simulasi browser).

Alur: state (sesi baru) -> chat 1 giliran (LLM nyata) -> state ulang.
Resume benar bila conversation_id SAMA dan pesan terakumulasi.
"""
import json
import time
import urllib.request
import http.cookiejar

BASE = "http://localhost:8080"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def call(path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json"},
        method="POST" if body else "GET")
    with opener.open(req, timeout=560) as r:
        return json.loads(r.read())


# 1) Sesi baru
st1 = call("/api/tutor/state?subject=matematika&paket=2&nomor=3")
print("sesi baru   : conv =", st1["conversation_id"], "| pesan =", len(st1["messages"]))
cookies = {c.name: c.value[:18] + "..." for c in cj}
print("cookie simpanan:", cookies)

# 2) Chat 1 giliran (LLM nyata)
t0 = time.time()
d = call("/api/tutor/chat", {
    "subject": "matematika", "paket": 2, "nomor": 3,
    "message": "Glosarium tadi maksudnya gimana?",
    "request_id": f"resume-{int(time.time())}"})
print(f"\nchat        : [{time.time()-t0:.0f}s | status={d.get('status')} | intent={d.get('intent')}]")
print("  balasan   :", (d.get("reply") or d.get("message", ""))[:220].replace("\n", " "))

# 3) State ulang -> harus resume conv yang sama
st2 = call("/api/tutor/state?subject=matematika&paket=2&nomor=3")
print("\nstate ulang : conv =", st2["conversation_id"], "| pesan =", len(st2["messages"]))
same = st1["conversation_id"] != st2["conversation_id"] and st2["conversation_id"] == d.get("conversation_id")
print("RESUME:", "BERHASIL (conv sama, riwayat utuh)" if same else "GAGAL")

# 4) Isolasi: soal lain dengan sesi yang sama harus conv terpisah
st3 = call("/api/tutor/state?subject=matematika&paket=2&nomor=25")
print("\nisolasi Q25 : conv =", st3["conversation_id"],
      "(harus None/berbeda dari conv Q3)")
