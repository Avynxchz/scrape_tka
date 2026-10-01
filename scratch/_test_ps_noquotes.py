import subprocess, os, time, sys
sys.path.insert(0, ".")
from pipeline.playwright_aistudio_bridge import check_port_open

exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = os.path.expandvars(r"%USERPROFILE%\.chrome_ai_studio")
url = "https://aistudio.google.com/prompts/new_chat?model=gemini-3.8-flash"

# Notice: NO inner quotes around user_data in ArgumentList
ps_cmd = f"Start-Process -FilePath '{exe}' -ArgumentList '--remote-debugging-port=9222', '--user-data-dir={user_data}', '{url}'"
print("Command:", ps_cmd)
subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)

print("Checking port 9222 for 10 seconds...")
for i in range(10):
    time.sleep(1)
    status = check_port_open(9222)
    print(f"Second {i+1}: port open = {status}")
