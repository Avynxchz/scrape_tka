# -*- coding: utf-8 -*-
"""Acceptance manual AI Tutor via HTTP sungguhan (server live + LLM nyata).

Jalankan: PYTHONIOENCODING=utf-8 python _tutor_acceptance.py [chat|long|both]
"""
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = "http://localhost:8080"
_opener = urllib.request.build_opener()
_cookie = None


def call(path, body=None, timeout=600):
    global _cookie
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data,
        method="POST" if body is not None else "GET",
        headers={"Content-Type": "application/json"})
    if _cookie:
        req.add_header("Cookie", _cookie)
    try:
        r = _opener.open(req, timeout=timeout)
        code = r.status
    except urllib.error.HTTPError as e:
        r, code = e, e.code
    sc = r.headers.get_all("Set-Cookie") or []
    if sc:
        _cookie = sc[0].split(";")[0]
    payload = json.loads(r.read())
    return code, payload


CHAT_TURNS = [
    "Kenapa 8 jadi 2^3?",
    "Terus kenapa harus disamain basis?",
    "Gue masih nggak ngerti.",
    "Jelasin dari paling dasar.",
    "Kalau 8 diganti 16 gimana?",
    "Kenapa jawaban akhirnya C?",
    "Step 3 tadi maksudnya apa?",
    "Kalau gue pakai cara lain?",
]

LONG_TURNS = [
    "Jadi inti soal ini apa?", "Kenapa pangkatnya pecahan?",
    "Maksudnya basis itu apa sih?", "Terus?",
    "Kalau 9 diganti 27 gimana?", "Cek dulu langkah 2 bener nggak",
    "Analogi dong biar gampang", "Kok bisa dapat 4/3?",
    "Kalau hasilnya dibalik jadi 3/4 bisa?", "Langkah 4 doang deh",
    "Kenapa bukan A?", "Itung lagi pelan-pelan boleh?",
    "Kenapa harus diubah ke basis prima?", "Kalau 8 jadi 32?",
    "Apa bedanya pangkat pecahan sama akar?", "Ringkes semuanya dong",
    "Gue masih bingung bagian pengurangan pangkatnya",
    "Coba dari paling dasar soal pangkat", "Oke lanjut",
    "Kalau ada angka 5 di pembilang gimana?", "Terus kenapa C?",
    "Contoh soal serupa dong",
]


def run_chat():
    print("=" * 70)
    print("ACCEPTANCE: 8 giliran percakapan MTK Paket 2 Q2 (LLM nyata)")
    print("=" * 70)
    for i, t in enumerate(CHAT_TURNS, 1):
        t0 = time.time()
        code, d = call("/api/tutor/chat", {
            "subject": "matematika", "paket": 2, "nomor": 2,
            "message": t, "request_id": f"acc-{uuid.uuid4().hex[:10]}"})
        dt = time.time() - t0
        print(f"\n--- GILIRAN {i}: {t}")
        print(f"[HTTP {code} | status={d.get('status')} | intent={d.get('intent','-')} | {dt:.0f}s]")
        if d.get("reply"):
            print(d["reply"][:500])
        else:
            print("!! ERROR:", d.get("message"))
            if code != 200:
                return False
    return True


def run_long():
    print("\n" + "=" * 70)
    print("LONG-CONVERSATION: 22 giliran MTK Paket 2 Q25 (LLM nyata)")
    print("=" * 70)
    ok = 0
    for i, t in enumerate(LONG_TURNS, 1):
        t0 = time.time()
        code, d = call("/api/tutor/chat", {
            "subject": "matematika", "paket": 2, "nomor": 25,
            "message": t, "request_id": f"long-{uuid.uuid4().hex[:10]}"})
        dt = time.time() - t0
        status = d.get("status")
        print(f"[{i:02d}] {dt:5.0f}s HTTP {code} {status:8s} {t[:44]}")
        if status == "success":
            ok += 1
    code, st = call("/api/tutor/state?subject=matematika&paket=2&nomor=25")
    n = len(st.get("messages", []))
    print(f"\nTersimpan: {n} pesan | ringkasan: {'ADA' if st.get('summary') else 'BELUM'}")
    if st.get("summary"):
        print("Ringkasan (awal):", st["summary"][:220].replace("\n", " "))
    print(f"Berhasil {ok}/{len(LONG_TURNS)} giliran")
    return ok == len(LONG_TURNS)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    results = {}
    if mode in ("chat", "both"):
        results["chat"] = run_chat()
    if mode in ("long", "both"):
        results["long"] = run_long()
    print("\nHASIL:", results)
    sys.exit(0 if all(results.values()) else 1)
