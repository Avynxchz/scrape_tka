import subprocess, json

script = """
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' } | ForEach-Object {
    [PSCustomObject]@{
        Id = $_.ProcessId
        CommandLine = $_.CommandLine
    }
} | ConvertTo-Json
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True, encoding="utf-8")
try:
    items = json.loads(res.stdout)
    if isinstance(items, dict):
        items = [items]
    print(f"Total Chrome processes: {len(items)}")
    for it in items:
        cmd = it.get("CommandLine") or ""
        pid = it.get("Id")
        if "9222" in cmd or ".chrome_ai_studio" in cmd:
            print(f"-> DEBUG INSTANCE PID {pid}: {cmd}")
        else:
            print(f"   Regular PID {pid}: {cmd[:80]}")
except Exception as e:
    print("Parse error:", e, res.stdout[:200])
