import urllib.request
import json
import ssl

ctx = ssl._create_unverified_context()
url_pieces = 'https://incompetech.com/music/royalty-free/pieces.json'
req = urllib.request.Request(url_pieces, headers={'User-Agent': 'Mozilla/5.0'})
pieces = json.loads(urllib.request.urlopen(req, context=ctx).read())

print("Keys of pieces[0]:", list(pieces[0].keys()))
candidates = []
for p in pieces:
    text = " ".join([str(p.get(k) or "") for k in ['title', 'feel', 'instruments', 'description']]).lower()
    bpm_str = str(p.get('bpm') or '0')
    try:
        bpm = float(bpm_str)
    except:
        bpm = 0
    if 110 <= bpm <= 135 and any(w in text for w in ['electronic', 'techno', 'synth', 'groove', 'tech', 'digital', 'dance', 'modern', 'upbeat']):
        candidates.append((p.get('title'), bpm, p.get('feel'), p.get('filename'), p.get('isrc')))

cipher = [p for p in pieces if 'cipher' in p.get('title','').lower()]
print("Cipher:", cipher)
tech_live = [p for p in pieces if 'tech live' in p.get('title','').lower()]
print("Tech Live:", tech_live)
