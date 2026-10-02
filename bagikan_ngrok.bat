@echo off
title TKA Master - Bagikan Online (ngrok, ramah AI crawler)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bagikan_online.ps1" -Tunnel ngrok
pause
