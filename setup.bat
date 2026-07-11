@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10 or 3.11 from python.org,
  echo enable "Add Python to PATH", then run this file again.
  pause
  exit /b 1
)

if not exist .venv (
  python -m venv .venv
  if errorlevel 1 goto :failed
)

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :failed

echo.
echo SnapTeX is ready. Double-click run.bat to start it.
pause
exit /b 0

:failed
echo.
echo Setup failed. Check the messages above for details.
pause
exit /b 1
