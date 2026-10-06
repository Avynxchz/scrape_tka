@echo off
echo ============================================================
echo   Starting CBT TKA Learning Server with AI Tutor
echo ============================================================
cd /d %~dp0

REM Load environment variables from .env if exists
if exist .env (
    echo [Config] Loading environment variables from .env ...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" set "%%a=%%b"
    )
)

echo [Config] Active LLM Provider info:
python -c "import tutor_llm; print(tutor_llm.active_provider_info())"

echo.
echo [Server] Launching server on http://localhost:8080/ ...
python server.py
pause
