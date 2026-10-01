import subprocess, os, time, sys
sys.path.insert(0, ".")
from pipeline.playwright_aistudio_bridge import check_port_open

exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = os.path.expandvars(r"%USERPROFILE%\.chrome_ai_studio")
url = "https://aistudio.google.com/prompts/new_chat?model=gemini-3.8-flash"

ps_cmd = f"""Start-Process -FilePath '{exe}' -ArgumentList '--remote-debugging-port=9222', '--user-data-dir="{user_data}"', '{url}'"""
print("Running PowerShell Start-Process...")
subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)

for i in range(10):
    time.sleep(1)
    if check_port_open(9222):
        print(f"✅ SUCCESS: Port 9222 is open at {i+1}s!")
        break
else:
    print("❌ FAILED: Port 9222 not open after 10s")
