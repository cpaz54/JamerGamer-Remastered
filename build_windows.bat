@echo off
rem Builds JamerGamer for Windows (first run takes a few minutes), then starts it.
rem Needs Python 3 from python.org with "Add python.exe to PATH" ticked.
cd /d "%~dp0"
if not exist ".buildenv\Scripts\python.exe" (
    py -3 -m venv .buildenv 2>nul || python -m venv .buildenv
)
if not exist ".buildenv\Scripts\python.exe" (
    echo.
    echo Python 3 was not found. Install it from https://www.python.org/downloads/
    echo and tick "Add python.exe to PATH" during setup, then run this file again.
    pause
    exit /b 1
)
if not exist "dist\JamerGamer\JamerGamer.exe" (
    ".buildenv\Scripts\python.exe" build.py || (pause & exit /b 1)
)
start "" "dist\JamerGamer\JamerGamer.exe"
