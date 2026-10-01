import subprocess, os, time, sys
sys.path.insert(0, ".")
from pipeline.playwright_aistudio_bridge import check_port_open

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = os.path.expandvars(r"%USERPROFILE%\.chrome_ai_studio")
url = "https://aistudio.google.com/prompts/new_chat?model=gemini-3.8-flash"

print("1. Launching Chrome via start cmd...")
cmd = f'start "" "{chrome_exe}" --remote-debugging-port=9222 --user-data-dir="{user_data}" "{url}"'
subprocess.Popen(cmd, shell=True)

print("2. Checking port 9222 for 15 seconds...")
for i in range(15):
    time.sleep(1)
    if check_port_open(9222):
        print(f"✅ SUCCESS: Port 9222 open at {i+1}s!")
        break
else:
    print("❌ FAILED: Port 9222 not open after 15s")
