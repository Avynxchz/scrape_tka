import urllib.request
import json

BASE = "http://127.0.0.1:8080"

def test():
    print("=== PENGUJIAN OTOMATIS END-TO-END GEOGRAFI ===")
    
    # 1. Test Static Index & Files
    with urllib.request.urlopen(f"{BASE}/index.html") as r:
        assert r.status == 200
        html = r.read().decode("utf-8")
        assert 'value="geografi"' in html
        print("[PASS] index.html memuat opsi Geografi (Pilihan)")
        
    with urllib.request.urlopen(f"{BASE}/data/geografi_paket_1_learning.json") as r:
        assert r.status == 200
        lrn = json.loads(r.read().decode("utf-8"))
        assert len(lrn["soal"]) == 10
        print(f"[PASS] data/geografi_paket_1_learning.json dapat diakses publik ({len(lrn['soal'])} soal)")
        
    with urllib.request.urlopen(f"{BASE}/data/geografi/paket_1/images/soal_01_stimulus_01.png") as r:
        assert r.status == 200
        content = r.read()
        assert len(content) > 100000
        print(f"[PASS] Aset citra satelit soal_01_stimulus_01.png tersaji sempurna ({len(content)} bytes)")
        
    # 2. Test /api/solution
    req = urllib.request.Request(
        f"{BASE}/api/solution",
        data=json.dumps({"subject": "geografi", "paket": 1, "nomor": 1}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read().decode("utf-8"))
        assert data["status"] == "success"
        assert data["solution"]["key_crosscheck"]["match"] is True
        print(f"[PASS] /api/solution sukses: Kunci '{data['solution']['answer_display']}', Source: {data['solution']['source']['file']}")
        
    # 3. Test /api/ai-tutor
    tutor_req = urllib.request.Request(
        f"{BASE}/api/ai-tutor",
        data=json.dumps({
            "subject": "geografi",
            "paket": 1,
            "nomor": 1,
            "message": "Apa perbedaan utama antara banjir rob dengan banjir luapan sungai?",
            "question_data": lrn["soal"][0]
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(tutor_req, timeout=30) as r:
        tutor_data = json.loads(r.read().decode("utf-8"))
        print("[PASS] /api/ai-tutor berhasil merespons:")
        print("  -> Provider:", tutor_data.get("provider"))
        print("  -> Model:", tutor_data.get("model"))
        print("  -> Cuplikan respons:", tutor_data.get("reply", "")[:180] + "...")
        
    print("\n=== SEMUA PENGUJIAN END-TO-END 100% SUKSES ===")

if __name__ == "__main__":
    test()
