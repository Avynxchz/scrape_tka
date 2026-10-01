import subprocess, os

exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = os.path.expandvars(r"%USERPROFILE%\.chrome_ai_studio")

res = subprocess.run([exe, "--remote-debugging-port=9222", f"--user-data-dir={user_data}", "--enable-logging=stderr"], capture_output=True, text=True, timeout=10)
print("Exit code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)
