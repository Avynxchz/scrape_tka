@echo off
echo ======================================================================
echo 🌐 MEMBUKA GOOGLE CHROME UNTUK PENDEKATAN B (PORT 9222)
echo ======================================================================
echo.
echo Membuka Chrome khusus AI Studio tanpa bentrok dengan tab yang sudah ada...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\.chrome_ai_studio" https://aistudio.google.com/prompts/new_chat?model=gemini-3.8-flash
echo.
echo ✅ Chrome berhasil dibuka di port 9222!
echo Pastikan Anda sudah login Google di jendela Chrome tersebut.
echo.
pause
