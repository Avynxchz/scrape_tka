# -*- coding: utf-8 -*-
"""scratch/verify_e2e_fixes.py — End-to-end browser test for Guru Autopsi score & AI Room integration."""

import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

EVIDENCE_DIR = "evidence/FIX"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # ====================================================================
        # TEST 1: MOBILE 390px — TRYOUT FINISH & GURU AUTOPSI CARD SCORE ACCURACY
        # ====================================================================
        print("\n--- 1. Testing Mobile 390px: Finish Tryout & Guru Autopsi Card ---")
        context_mob = await browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True
        )

        # Set logged-in user in localStorage persistently
        dummy_user = {
            "loggedIn": True,
            "id": "usr_test_12345",
            "email": "murid_tka@example.com",
            "name": "Murid TKA",
            "avatar": ""
        }
        dummy_token = {
            "access_token": "dummy_jwt_token_for_user_test_12345",
            "user": dummy_user
        }

        await context_mob.add_init_script(f"""() => {{
            window.localStorage.setItem('tka_user', JSON.stringify({json.dumps(dummy_user)}));
            window.localStorage.setItem('tka_supabase_auth_token', JSON.stringify({json.dumps(dummy_token)}));
        }}""")

        page_mob = await context_mob.new_page()
        await page_mob.goto("http://127.0.0.1:8080/app?subject=bahasa_indonesia&paket=1")
        await page_mob.wait_for_timeout(2000)

        # Set user answers: 3 correct, 17 wrong (accuracy 15%)
        eval_res = await page_mob.evaluate("""() => {
            const curKey = pkgKey();
            const pkg = state.pkgData[curKey];
            if (!pkg || !pkg.soal) return { error: 'no pkg' };

            if (!state.userAnswers) state.userAnswers = {};
            state.userAnswers[curKey] = {};

            // Pastikan AttemptRecorder aktif untuk merekam tryout
            AttemptRecorder.start('bahasa_indonesia', 1, pkg.soal.length, 1800);

            // Record answers in state and in AttemptRecorder
            pkg.soal.forEach((item, idx) => {
                const no = item.nomor;
                const k = item.kunci_jawaban;
                // 3 correct (no 1..3), 17 wrong (no 4..20)
                let userAns;
                if (idx < 3) {
                    userAns = (Array.isArray(k)) ? k : (item.pernyataan ? 'A' : (k || 'A'));
                } else {
                    userAns = (k === 'B' ? 'C' : 'B');
                }
                state.userAnswers[curKey][no] = userAns;
                AttemptRecorder.onVisit(no, item.topik || null);
                AttemptRecorder.onAnswer(no, userAns);
            });

            // Call selesaiTes
            selesaiTes();

            // Return evaluation stats
            const att = window._lastFinishedAttempt;
            return {
                curKey: curKey,
                totalSoal: pkg.soal.length,
                lastAttemptScore: att ? att.score : null,
                lastAttemptNCorrect: att ? att.n_correct : null
            };
        }""")
        print(f"Evaluasi setelah selesaiTes: {eval_res}")

        # Tunggu renderAutopsiSection menyelesaikan fetch/analisis
        await page_mob.wait_for_timeout(3500)

        # Periksa kartu Guru Autopsi di DOM
        card_text = await page_mob.evaluate("""() => {
            const sec = document.getElementById('autopsiSection');
            return sec ? sec.innerText : '';
        }""")

        print(f"Cuplikan teks Guru Autopsi di Mobile:\n{card_text[:350]}...")
        
        # Validasi: Guru Autopsi TIDAK boleh mengatakan 'Skor 0% karena semua jawaban salah'
        has_zero_error = "Skor 0% karena semua jawaban salah" in card_text
        print(f"Apakah ada error 'Skor 0% karena semua jawaban salah'? {has_zero_error}")
        assert not has_zero_error, "FAIL: Guru Autopsi masih menampilkan Skor 0% karena semua jawaban salah!"
        
        # Screenshot Review Hasil + Guru Autopsi di Mobile
        await page_mob.screenshot(path=f"{EVIDENCE_DIR}/mobile_390_guru_autopsi_15pct.png")
        print(f"Screenshot tersimpan: {EVIDENCE_DIR}/mobile_390_guru_autopsi_15pct.png")

        # ====================================================================
        # TEST 2: RUANG AI MAPEL (/ruang/bahasa_indonesia)
        # ====================================================================
        print("\n--- 2. Testing Ruang AI Mapel (/ruang/bahasa_indonesia) ---")
        # Gunakan tab yang sama (page_mob) agar localStorage dan sesi tersambung mulus
        await page_mob.goto("http://127.0.0.1:8080/ruang/bahasa_indonesia")
        await page_mob.wait_for_timeout(2500)

        room_debug = await page_mob.evaluate("""() => {
            return {
                currentMapelSlug: currentMapelSlug,
                localAttsLen: (typeof getLocalMapelAttempts === 'function' ? getLocalMapelAttempts(currentMapelSlug).length : -1),
                recentLen: (JSON.parse(localStorage.getItem('tka_recent_attempts') || '[]')).length,
                queueLen: (JSON.parse(localStorage.getItem('tka_attempt_queue') || '[]')).length,
                token: (typeof getAuthToken === 'function' ? getAuthToken() : null),
                roomContext: roomContext
            };
        }""")
        print(f"DEBUG RUANG: {room_debug}")
        room_headline = await page_mob.evaluate("""() => {
            const h = document.getElementById('summaryHeadline');
            const w = document.getElementById('valWaktu');
            const k = document.getElementById('valKuat');
            const p = document.getElementById('txtPola');
            return {
                headline: h ? h.innerText : '',
                valWaktu: w ? w.innerText : '',
                valKuat: k ? k.innerText : '',
                pola: p ? p.innerText : ''
            };
        }""")
        print(f"Ringkasan Ruang AI: {room_headline}")

        # Validasi: Total soal yang terbaca adalah 20 soal dan Akurasi 15%
        print(f"Headline Ruang AI: '{room_headline['headline']}'")
        assert "20" in room_headline['headline'], f"Expected '20' in headline, got: {room_headline['headline']}"
        assert "15%" in room_headline['headline'], f"Expected '15%' in headline, got: {room_headline['headline']}"

        # Test kirim pesan ke AI Coach di Ruang Mapel
        await page_mob.fill("#chatInput", "Bagaimana strategi paling efektif untuk menaikkan akurasi saya dari 15%?")
        await page_mob.click("#btnSend")
        
        # Tunggu respons AI
        await page_mob.wait_for_timeout(5000)

        last_coach_msg = await page_mob.evaluate("""() => {
            const msgs = document.querySelectorAll('.msg-row.coach .msg-bubble');
            if (msgs.length > 0) {
                return msgs[msgs.length - 1].innerText;
            }
            return '';
        }""")
        print(f"Respons Guru AI di Ruang Mapel:\n{last_coach_msg[:250]}...")
        assert len(last_coach_msg) > 20, "Coach response should not be empty"

        # Screenshot Ruang AI di Mobile
        await page_mob.screenshot(path=f"{EVIDENCE_DIR}/mobile_390_ruang_bahasa_indonesia.png")
        print(f"Screenshot tersimpan: {EVIDENCE_DIR}/mobile_390_ruang_bahasa_indonesia.png")

        # ====================================================================
        # TEST 3: DESKTOP 1280px — BERANDA & RUANG AI INTEGRATION
        # ====================================================================
        print("\n--- 3. Testing Desktop 1280px Beranda ---")
        context_desk = await browser.new_context(viewport={"width": 1280, "height": 850})
        await context_desk.add_init_script(f"""() => {{
            window.localStorage.setItem('tka_user', JSON.stringify({json.dumps(dummy_user)}));
            window.localStorage.setItem('tka_supabase_auth_token', JSON.stringify({json.dumps(dummy_token)}));
        }}""")
        page_desk = await context_desk.new_page()
        await page_desk.goto("http://127.0.0.1:8080/app")
        await page_desk.wait_for_timeout(3000)

        # Scroll iframe desktop untuk menangkap sidebar & kartu Autopsi
        await page_desk.evaluate("""() => {
            const f = document.getElementById('homeDesktopFrame');
            if (f && f.contentWindow) {
                f.contentWindow.scrollTo({ top: 400, behavior: 'instant' });
            }
        }""")
        await page_desk.wait_for_timeout(1000)

        await page_desk.screenshot(path=f"{EVIDENCE_DIR}/desktop_1280_beranda_autopsi.png")
        print(f"Screenshot tersimpan: {EVIDENCE_DIR}/desktop_1280_beranda_autopsi.png")

        print("\n=== ALL BROWSER E2E TESTS PASSED WITH 100% ACCURACY ===")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
