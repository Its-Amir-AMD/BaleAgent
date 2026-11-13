@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 goto error
)
echo [2/3] Installing / updating requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo [3/3] Starting Bale Agent Desktop v2.1.0...
".venv\Scripts\python.exe" app.py
if errorlevel 1 goto error
goto end
:error
echo.
echo Something went wrong. Check the error above.
pause
:end
