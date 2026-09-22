# -*- coding: utf-8 -*-
"""Acceptance penuh: sekuens 8 giliran Q2 dalam SATU percakapan (cookiejar)."""
import json
import time
import urllib.request
import http.cookiejar

BASE = "http://localhost:8080"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

TURNS = [
    "Kenapa 8 jadi 2^3?",
    "Terus kenapa harus disamain basis?",
    "Gue masih nggak ngerti.",
    "Jelasin dari paling dasar.",
    "Kalau 8 diganti 16 gimana?",
    "Kenapa jawaban akhirnya C?",
    "Step 3 tadi maksudnya apa?",
    "Kalau gue pakai cara lain?",
]


def call(path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json"},
        method="POST" if body else "GET")
    with opener.open(req, timeout=560) as r:
        return json.loads(r.read())


def main():
    print("=" * 70)
    print("SEKUENS ACCEPTANCE 8 GILIRAN — MTK Paket 2 Q2 — SATU percakapan")
    print("=" * 70)
    ok = 0
    for i, t in enumerate(TURNS, 1):
        t0 = time.time()
        try:
            d = call("/api/tutor/chat", {
                "subject": "matematika", "paket": 2, "nomor": 2,
                "message": t, "request_id": f"full-{i}-{int(time.time())}"})
            dt = time.time() - t0
            status = d.get("status")
            print(f"\n--- GILIRAN {i}: {t}")
            print(f"[{dt:.0f}s | status={status} | intent={d.get('intent', '-')}]")
            if status == "success":
                ok += 1
                print(d["reply"][:400])
            else:
                print("!! ERROR:", d.get("message"))
        except Exception as e:
            print(f"\n--- GILIRAN {i}: {t}\n!! EXC: {e}")
    st = call("/api/tutor/state?subject=matematika&paket=2&nomor=2")
    print("\n" + "=" * 70)
    print(f"SELESAI: {ok}/8 sukses | conv={st['conversation_id']} | "
          f"pesan tersimpan={len(st['messages'])}")
    print("=" * 70)


if __name__ == "__main__":
    main()
