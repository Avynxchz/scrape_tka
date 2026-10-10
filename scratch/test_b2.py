"""
Test verifikasi B2: Timer berjalan akurat dengan selisih timestamp (Date.now())
dan waktu per soal terekam saat Selesai Tes.
Menguji:
1. Timer tidak macet di 00:00:00 saat kuis dibuka.
2. Timer benar-benar berjalan (berkurang) seiring waktu nyata.
3. Dua screenshot timer diambil dengan jeda waktu untuk membuktikan timer bergerak.
4. Waktu per soal terekam di AttemptRecorder items dengan waktu_detik > 0.
5. Screenshot after + log assertion di evidence/B2/
"""

import sys
import time
sys.path.insert(0, 'scratch')
from test_harness import TKATestHarness, LOCAL_URL

def parse_timer_to_seconds(timer_str):
    parts = [int(p) for p in timer_str.strip().split(':')]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return int(parts[0])

def test_b2():
    print("Running B2 verification test (SimTimer Date.now delta)...")
    with TKATestHarness(LOCAL_URL) as harness:
        p = harness.page
        p.goto(f"{LOCAL_URL}/app?subject=matematika&paket=1")
        p.wait_for_timeout(1000)

        # 1. Cek timer text awal
        timer_el = p.locator('#timerText')
        assert timer_el.is_visible(), "Timer element tidak terlihat!"
        t0_str = timer_el.inner_text().strip()
        print(f"Timer awal t0: {t0_str}")
        assert t0_str != "00:00:00", f"ERROR: Timer macet di 00:00:00! Nilai: {t0_str}"
        t0_sec = parse_timer_to_seconds(t0_str)
        assert t0_sec > 0, "Durasi timer harus lebih dari 0 detik"

        # Simpan bukti timer t1
        harness.save_evidence(
            "evidence/B2/timer_running_t1-after",
            "B2 AFTER: Cuplikan timer pertama saat kuis berjalan",
            {"timer_t0": t0_str, "seconds_t0": t0_sec}
        )

        # 2. Tunggu 3 detik di Soal 1
        print("Menunggu 3 detik untuk memverifikasi timer berkurang...")
        time.sleep(3)
        p.wait_for_timeout(500)

        t1_str = timer_el.inner_text().strip()
        print(f"Timer setelah 3 detik t1: {t1_str}")
        t1_sec = parse_timer_to_seconds(t1_str)
        assert t1_sec < t0_sec, f"ERROR: Timer tidak berjalan! t0={t0_str} ({t0_sec}s), t1={t1_str} ({t1_sec}s)"
        print(f"PASS: Timer berkurang dari {t0_str} ke {t1_str} (selisih: {t0_sec - t1_sec} detik).")

        # Simpan bukti timer t2 (bukti kedua berjarak beberapa detik)
        harness.save_evidence(
            "evidence/B2/timer_running_t2-after",
            "B2 AFTER: Cuplikan timer kedua berjarak 3 detik (membuktikan timer bergerak)",
            {"timer_t1": t1_str, "seconds_t1": t1_sec, "delta_seconds": t0_sec - t1_sec}
        )

        # 3. Kunjungi Soal 2 dan Soal 3 untuk merekam waktu per soal
        # Jawab opsi A di Soal 1
        p.keyboard.press('a')
        p.wait_for_timeout(200)

        # Pindah ke Soal 2
        p.keyboard.press('ArrowRight')
        p.wait_for_timeout(500)
        print("Berada di Soal 2, menunggu 2 detik...")
        time.sleep(2)
        p.keyboard.press('b')
        p.wait_for_timeout(200)

        # Pindah ke Soal 3
        p.keyboard.press('ArrowRight')
        p.wait_for_timeout(500)
        print("Berada di Soal 3, menunggu 2 detik...")
        time.sleep(2)
        p.keyboard.press('c')
        p.wait_for_timeout(200)

        # 4. Selesaikan tes
        print("Menyelesaikan tes...")
        p.evaluate("() => selesaiTes()")
        p.wait_for_timeout(1000)

        # Verifikasi AttemptRecorder payload items
        attempt_data = p.evaluate("() => window._lastFinishedAttempt")
        assert attempt_data is not None, "ERROR: window._lastFinishedAttempt bernilai null!"
        items = attempt_data.get('items', [])
        assert len(items) > 0, "ERROR: items di rekaman attempt kosong!"

        # Periksa waktu soal 1, 2, 3
        item1 = next((it for it in items if it['position'] == 1), None)
        item2 = next((it for it in items if it['position'] == 2), None)
        item3 = next((it for it in items if it['position'] == 3), None)

        assert item1 is not None and item1.get('waktu_detik', 0) >= 2, f"Waktu soal 1 tidak terekam! Data: {item1}"
        assert item2 is not None and item2.get('waktu_detik', 0) >= 1, f"Waktu soal 2 tidak terekam! Data: {item2}"
        assert item3 is not None and item3.get('waktu_detik', 0) >= 1, f"Waktu soal 3 tidak terekam! Data: {item3}"

        print(f"PASS: Waktu per soal terekam sempurna: Q1={item1['waktu_detik']}s, Q2={item2['waktu_detik']}s, Q3={item3['waktu_detik']}s.")

        # Simpan bukti final waktu per soal terekam
        harness.save_evidence(
            "evidence/B2/timer_per_soal_recorded-after",
            "B2 AFTER: Rekaman waktu per soal tersimpan akurat saat Selesai Tes",
            {
                "status": "PASS",
                "soal_1_waktu_detik": item1['waktu_detik'],
                "soal_2_waktu_detik": item2['waktu_detik'],
                "soal_3_waktu_detik": item3['waktu_detik'],
                "total_items_recorded": len(items)
            }
        )

    print("\nALL B2 VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_b2()
