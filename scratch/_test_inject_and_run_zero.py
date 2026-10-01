# -*- coding: utf-8 -*-
"""scratch/_test_inject_and_run_zero.py
Test inject_and_run on a fresh new_chat page from 0.
"""
import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, ".")
from pipeline.playwright_aistudio_bridge import (
    inject_and_run,
    safe_parse_json,
    dismiss_any_overlay
)

def test_inject():
    print("=== TESTING INJECT AND RUN PADA FRESH NEW CHAT ===")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        page.bring_to_front()
        print(f"Halaman aktif: {page.url}")
        
        test_prompt = """
Kamu adalah AI Pengajar TKA Saintek & Soshum.
Hasilkan JSON ARRAY solusi untuk 1 soal berikut:
[
  {
    "question_number": 1,
    "concept_kunci": ["Pilar 1", "Pilar 2"],
    "glossary": [{"term": "TKA", "meaning": "Tes Kemampuan Akademik"}],
    "diketahui": "Diketahui soal uji coba dari nol",
    "ditanyakan": "Apakah sistem bekerja?",
    "reasoning": "Sistem bekerja secara otomatis dan stabil.",
    "steps": [{"step": 1, "title": "Langkah 1", "explanation": "Verifikasi integrasi"}],
    "why_correct": "Karena semua pengujian lolos 100%.",
    "tips": ["Tips pengujian otomatis"],
    "common_mistakes": ["Lupa dismiss overlay"]
  }
]
Keluarkan HANYA JSON array tersebut di dalam code block ```json ... ``` tanpa teks pengantar.
"""
        print("1. Memanggil inject_and_run()...")
        t0 = time.time()
        raw_resp = inject_and_run(page, prompt_text=test_prompt, timeout_seconds=90)
        elapsed = time.time() - t0
        print(f"2. inject_and_run selesai dalam {elapsed:.1f} detik! Panjang respon: {len(raw_resp)} karakter.")
        print(f"Cuplikan respon:\n{raw_resp[:300]}...\n")
        
        print("3. Memvalidasi parsing JSON...")
        parsed = safe_parse_json(raw_resp)
        if isinstance(parsed, list) and len(parsed) > 0 and parsed[0].get("question_number") == 1:
            print("✅ SUKSES BESAR! JSON solusi valid:")
            print(f"   question_number: {parsed[0]['question_number']}")
            print(f"   concept_kunci: {parsed[0]['concept_kunci']}")
            print(f"   why_correct: {parsed[0]['why_correct']}")
            return True
        else:
            print("❌ GAGAL memparse JSON solusi:", parsed)
            return False

if __name__ == "__main__":
    ok = test_inject()
    sys.exit(0 if ok else 1)
