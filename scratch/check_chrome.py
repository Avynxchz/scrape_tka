import subprocess

cmd = 'powershell "Get-Process chrome | Select-Object Id, MainWindowTitle"'
p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(p.stdout)
