import sys, os
sys.path.insert(0, '.')
import server

class DummyHandler(server.AppRequestHandler):
    def __init__(self, headers, path, client_ip='127.0.0.1'):
        self.headers = headers
        self.path = path
        self.client_address = (client_ip, 12345)

# Test 1: with Cookie active_subject=kimia
h1 = DummyHandler({'Cookie': 'active_subject=kimia; active_paket=1'}, '/images/soal_02_stimulus_01.png')
res1 = h1.translate_path('/images/soal_02_stimulus_01.png')
print('Test 1 (Cookie kimia):', res1)
assert 'kimia' in res1, f"Expected kimia in {res1}"

# Test 2: with Referer subject=kimia
h2 = DummyHandler({'Referer': 'http://localhost:8080/?subject=kimia&paket=1'}, '/images/soal_02_stimulus_01.png')
res2 = h2.translate_path('/images/soal_02_stimulus_01.png')
print('Test 2 (Referer kimia):', res2)
assert 'kimia' in res2, f"Expected kimia in {res2}"

# Test 3: with client context
server._client_active_context['127.0.0.1'] = {'subject': 'kimia', 'paket': 1}
h3 = DummyHandler({}, '/images/soal_02_stimulus_01.png')
res3 = h3.translate_path('/images/soal_02_stimulus_01.png')
print('Test 3 (Client context kimia):', res3)
assert 'kimia' in res3, f"Expected kimia in {res3}"

# Test 4: without any context, should NOT return ekonomi for generic soal_XX
server._client_active_context.clear()
h4 = DummyHandler({}, '/images/soal_02_stimulus_01.png')
res4 = h4.translate_path('/images/soal_02_stimulus_01.png')
print('Test 4 (No context):', res4)
assert 'ekonomi' not in res4, f"Cross-subject pollution detected: {res4}"

print("\nALL 4 TRANSLATE_PATH TESTS PASSED!")
