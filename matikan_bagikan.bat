@echo off
title TKA Master - Matikan Bagikan Online
echo Mematikan tunnel & server demo...
taskkill /IM cloudflared.exe /F >nul 2>&1
taskkill /IM ngrok.exe /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8081 ^| findstr LISTENING') do taskkill /PID %%p /F >nul 2>&1
echo Selesai. Link publik sudah mati. Server utama kamu (8080) tidak terganggu.
pause
