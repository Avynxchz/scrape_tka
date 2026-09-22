# -*- coding: utf-8 -*-
"""Lanjutan acceptance AI Tutor — RESUME percakapan yang sama (bukan baru).

Memakai cookie sesi dari run pertama sehingga giliran lanjutan masuk ke
percakapan yang tersimpan di DB (uji resume + kontinuitas konteks).
"""
import json
import time
import urllib.request

BASE = "http://localhost:8080"
COOKIE = "tutor_uid=a9b7bf034fc6f4fad558dacf65ca4743"  # sesi run pertama

Q2_REMAINING = [
    "Kalau 8 diganti 16 gimana?",
    "Kenapa jawaban akhirnya C?",
    "Step 3 tadi maksudnya apa?",
    "Kalau gue pakai cara lain?",
]
Q25_CONTINUE = [
    "Kenapa harus diubah ke basis prima?",
    "Kalau 8 jadi 32?",
]


def call(path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json", "Cookie": COOKIE},
        method="POST" if body else "GET")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=560) as r:
        d = json.loads(r.read())
    return time.time() - t0, d


def chat(subject, nomor, msg, i, tag):
    dt, d = call("/api/tutor/chat", {
        "subject": subject, "paket": 2, "nomor": nomor,
        "message": msg, "request_id": f"{tag}-{i}-{int(time.time())}"})
    print(f"\n--- {tag} giliran: {msg}")
    print(f"[HTTP 200 | status={d.get('status')} | intent={d.get('intent','-')} | {dt:.0f}s]")
    print((d.get("reply") or ("!! ERROR: " + d.get("message", "?")))[:420])
    return d.get("status") == "success"


def main():
    ok = 0
    total = 0
    print("=" * 70)
    print("RESUME Q2 (mtk_p2_q02) — giliran 5-8 dari sekuens acceptance")
    print("=" * 70)
    for i, m in enumerate(Q2_REMAINING, 5):
        total += 1
        ok += chat("matematika", 2, m, i, "Q2")
    print("\n" + "=" * 70)
    print("RESUME Q25 (mtk_p2_q25) — long-conversation lanjutan")
    print("=" * 70)
    for i, m in enumerate(Q25_CONTINUE, 13):
        total += 1
        ok += chat("matematika", 25, m, i, "Q25")

    print("\n" + "=" * 70)
    print("VERIFIKASI STATE + ISOLASI")
    print("=" * 70)
    for nomor, expect in ((2, "mtk_p2_q02"), (25, "mtk_p2_q25")):
        dt, st = call(f"/api/tutor/state?subject=matematika&paket=2&nomor={nomor}")
        msgs = st.get("messages", [])
        roles = [m["role"] for m in msgs]
        n_user, n_asst = roles.count("user"), roles.count("assistant")
        leak = "eksponen" if nomor == 25 else ""
        txt = " ".join(m["content"] for m in msgs).lower()
        print(f"Q{nomor}: conv={st['conversation_id']} | pesan tersimpan={len(msgs)} "
              f"(user {n_user}, assistant {n_asst}) | ringkasan={'ADA' if st.get('summary') else 'BELUM'}")
        if st.get("summary"):
            print("   ringkasan:", st["summary"][:200].replace("\n", " "))
        if leak and leak in txt:
            print("   !! KEBOCORAN: konten eksponen muncul di percakapan Q25")
    print(f"\nSelesai: {ok}/{total} giliran sukses")


if __name__ == "__main__":
    main()
