import urllib.request
import json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
payload = json.dumps({
    'subject': 'matematika',
    'paket': 2,
    'nomor': 1,
    'message': 'Gimana cara termudah ngerjain soal nomor 1 ini?'
}).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8080/api/tutor/chat',
    data=payload,
    headers={'Content-Type': 'application/json'}
)

print("Calling Chat 1...")
res = opener.open(req)
data = json.loads(res.read().decode('utf-8'))
print('CHAT 1 HTTP 200 SUCCESS!')
print('MODEL DIGUNAKAN:', data.get('model'))
print('QUOTA TERSISA:', data.get('quota'))
print('JAWABAN AI TUTOR:')
print('----------------------------------------')
print(data.get('reply'))
print('----------------------------------------')

print("\nCalling Chat 2 segera (uji cooldown 10 detik)...")
try:
    res2 = opener.open(req)
    data2 = json.loads(res2.read().decode('utf-8'))
    print("CHAT 2 response:", data2)
except urllib.error.HTTPError as e:
    err_body = json.loads(e.read().decode('utf-8'))
    print(f'CHAT 2 COOLDOWN TERDETEKSI: HTTP {e.code}')
    print('Reason:', err_body.get('reason'))
    print('Wait Seconds:', err_body.get('wait_seconds'))
    print('Message:', err_body.get('message'))
