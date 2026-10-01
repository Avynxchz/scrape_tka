import subprocess, sys

targets = [
    'bahasa_indonesia_lanjut_paket_1',
    'bahasa_indonesia_lanjut_paket_2',
    'bahasa_inggris_lanjut_paket_1',
    'bahasa_inggris_lanjut_paket_2'
]

results = {}
for t in targets:
    res = subprocess.run([sys.executable, 'pipeline/05_automated_auditor.py', '--target', t], capture_output=True, text=True, encoding='utf-8')
    passed = 'PASSED' in res.stdout and 'STATUS AUDIT: 100% LOLOS' in res.stdout
    results[t] = passed
    status_str = "PASSED 100%" if passed else "FAILED"
    print(f"=== AUDIT {t}: {status_str} ===")
    if not passed:
        print(res.stdout)

print("\n================ FINAL WAVE 1 RECAP ================")
for t, p in results.items():
    res_str = "PASSED (0 BUGS)" if p else "FAILED"
    print(f"  • {t:35}: {res_str}")
print("=====================================================")
