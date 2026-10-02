@echo off
title TKA Master - Bagikan Online
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bagikan_online.ps1"
pause
