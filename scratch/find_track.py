import urllib.request
import re
import ssl

ctx = ssl._create_unverified_context()
url = 'https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100844'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
    import json
    url_pieces = 'https://incompetech.com/music/royalty-free/pieces.json'
    pieces = json.loads(urllib.request.urlopen(urllib.request.Request(url_pieces, headers={'User-Agent': 'Mozilla/5.0'}), context=ctx).read())
    print("Total tracks:", len(pieces))
    # Filter for Electronic / Modern / Tech
    tech_tracks = [p for p in pieces if any(k in (p.get('genre','') + p.get('feel','') + p.get('title','')).lower() for k in ['electronic', 'tech', 'groove', 'synth', 'future', 'chill', 'upbeat'])]
    print("Tech tracks count:", len(tech_tracks))
    for p in tech_tracks[:15]:
        print(f"- {p.get('title')} | BPM: {p.get('tempo')} | Feel: {p.get('feel')} | Filename: {p.get('filename')}")
except Exception as e:
    print("Error:", e)
