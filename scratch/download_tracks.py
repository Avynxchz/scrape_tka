import requests
import os
import urllib.parse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

tracks = ['Tech Live.mp3', 'Realizer.mp3']
base_url = 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/'
os.makedirs('scratch/music', exist_ok=True)

for t in tracks:
    url = base_url + urllib.parse.quote(t)
    dest = os.path.join('scratch/music', t)
    print(f"Downloading {t}...")
    r = requests.get(url, verify=False, timeout=30, stream=True)
    if r.status_code == 200:
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
        print(f"Saved {dest} ({os.path.getsize(dest)} bytes)")
    else:
        print(f"Failed with status {r.status_code}")
