import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import requests

BASE_URL = "http://localhost:8080"
packages = [
    ("bahasa_indonesia_lanjut", 1, 10),
    ("bahasa_indonesia_lanjut", 2, 29),
    ("bahasa_inggris_lanjut", 1, 10),
    ("bahasa_inggris_lanjut", 2, 29),
]

all_ok = True
print("Verifying CBT Web Server API for Wave 1:")
for subject, paket, expected_count in packages:
    # 1. Check questions endpoint
    q_url = f"{BASE_URL}/data/{subject}_paket_{paket}_learning.json"
    res_q = requests.get(q_url)
    q_status = res_q.status_code
    q_len = len(res_q.json().get("soal", [])) if q_status == 200 else 0
    
    # 2. Check solution endpoint (POST)
    sol_url = f"{BASE_URL}/api/solution"
    res_s = requests.post(sol_url, json={"subject": subject, "paket": paket, "nomor": 1})
    sol_status = res_s.status_code
    sol_json = res_s.json() if sol_status == 200 else {}
    sol_ok = sol_json.get("status") == "success"
    sol_type = sol_json.get("source", "unknown") if sol_ok else sol_json.get("status", "err")

    # 3. Check Soal Serupa on Q1
    soal_serupa_ok = bool(res_q.json().get("soal", [])[0].get("soal_serupa")) if q_len > 0 else False

    status_str = "✅ OK" if (q_status == 200 and q_len == expected_count and sol_ok and soal_serupa_ok) else "❌ FAIL"
    print(f"  • {subject} (P{paket}): {status_str} | Soal: {q_len}/{expected_count} | Solusi Q1: {sol_type} | Soal Serupa Q1: {soal_serupa_ok}")
    if status_str != "✅ OK":
        all_ok = False

if all_ok:
    print("\n🎉 ALL 4 WAVE 1 PACKAGES ARE FULLY INTEGRATED & LIVE ON CBT RUNTIME!")
else:
    print("\n❌ Integration issues detected!")
