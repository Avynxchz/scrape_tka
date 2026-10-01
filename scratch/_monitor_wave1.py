import urllib.request
import json
import time

for _ in range(10):
    try:
        res = json.loads(urllib.request.urlopen("http://localhost:8080/api/swarm/status").read().decode("utf-8"))
        d1 = res["divisions"]["divisi_1"]
        d2 = res["divisions"]["divisi_2"]
        d3 = res["divisions"]["divisi_3"]
        d4 = res["divisions"]["divisi_4"]
        d5 = res["divisions"]["divisi_5"]
        print(f"[{res['elapsed_seconds']}s] Running: {res['is_running']} | D1: {d1['status']} ({d1['progress']}%) | D2: {d2['status']} ({d2['progress']}%) | D3: {d3['status']} ({d3['progress']}%) | D4: {d4['status']} ({d4['progress']}%) | D5: {d5['status']} ({d5['progress']}%)")
        if res.get("logs"):
            for l in res["logs"][-3:]:
                print(f"   [{l['time']}] [{l['tag']}] {l['message']}")
        if not res["is_running"] and res["elapsed_seconds"] > 5:
            print("Swarm run finished!")
            break
    except Exception as e:
        print("Poll error:", e)
    time.sleep(5)
