@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\pythonw.exe (
  echo Run setup.bat first.
  pause
  exit /b 1
)
start "SnapTeX" .venv\Scripts\pythonw.exe -m snaptex
