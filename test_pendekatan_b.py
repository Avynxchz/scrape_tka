# -*- coding: utf-8 -*-
"""test_pendekatan_b.py — 1-Click Interactive Test for Approach B (Playwright + Google AI Studio).
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import time
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from pipeline.playwright_aistudio_bridge import (
    check_port_open,
    get_chrome_path,
    run_phase_4_via_playwright,
    log
)

print("=" * 75)
print("🚀 UJI COBA INTERAKTIF PENDEKATAN B (PLAYWRIGHT -> GOOGLE AI STUDIO PRO)")
print("=" * 75)
print("Misi: Menyambungkan Playwright ke Google Chrome Anda, menginjeksi prompt,")
print("dan mengekstrak jawaban langsung dari tab AI Studio di layar Anda.")
print("=" * 75)

port = 9222
target_slug = "bahasa_indonesia_paket_2"

# 1. Cek atau buka Chrome otomatis
if not check_port_open(port):
    chrome_exe = get_chrome_path()
    log(f"Chrome port {port} belum aktif. Membuka Google Chrome otomatis di port {port}...", "INFO")
    url = "https://aistudio.google.com/prompts/new_chat?model=gemini-3.8-flash"
    user_data = os.path.expandvars(r"%USERPROFILE%\.chrome_ai_studio")

    # Jalankan Chrome dengan remote debugging port + profile terisolasi agar 100% selalu berhasil membuka port
    subprocess.Popen([chrome_exe, f"--remote-debugging-port={port}", f"--user-data-dir={user_data}", url])

    # Tunggu beberapa detik sampai port terbuka
    opened = False
    for _ in range(12):
        time.sleep(1)
        if check_port_open(port):
            opened = True
            break

    if not opened:
        log("Port 9222 belum terdeteksi. Silakan jalankan start_chrome_debug.bat manual.", "WARNING")

import argparse
parser = argparse.ArgumentParser(description="Test Pendekatan B")
parser.add_argument("--auto", action="store_true", help="Langsung jalankan tanpa menunggu tekan Enter")
parser.add_argument("--slug", type=str, default="bahasa_indonesia_paket_2")
cli_args, _ = parser.parse_known_args()

target_slug = cli_args.slug

print("\n" + "-" * 75)
print("✅ Chrome dengan Port Debugging 9222 siap!")
print("Pastikan di jendela Chrome tersebut:")
print("  1. Halaman Google AI Studio sudah tampil.")
print("  2. Anda sudah login dengan akun Google AI PRO Anda.")
print("-" * 75)
if not cli_args.auto:
    input("👉 Tekan [ENTER] di sini jika Anda sudah siap memulai otomasi Playwright... ")

print("\n" + "=" * 75)
log(f"Memulai otomasi Playwright untuk target: {target_slug}...", "INFO")
print("=" * 75)

try:
    run_phase_4_via_playwright(slug=target_slug, port=port)
    print("\n" + "=" * 75)
    print("🎉 SUKSES BESAR! PENDEKATAN B BERHASIL 100%!")
    print("File solusi telah diperbarui langsung dari Google AI Studio PRO.")
    print("=" * 75)
except Exception as e:
    print("\n" + "!" * 75)
    log(f"Terjadi kendala saat otomasi: {e}", "ERROR")
    print("!" * 75)
