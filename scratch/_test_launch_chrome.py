import os, time, sys
sys.path.insert(0, ".")
from pipeline.playwright_aistudio_bridge import check_port_open

bat = os.path.abspath("start_chrome_debug.bat")
print("Starting bat:", bat)
os.system(f'start "" "{bat}"')
for i in range(10):
    time.sleep(1)
    if check_port_open(9222):
        print(f"Port 9222 open at {i+1}s!")
        break
else:
    print("Port 9222 failed to open within 10s")
