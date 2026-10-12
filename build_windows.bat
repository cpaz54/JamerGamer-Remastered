@echo off
rem Builds dist\JamerGamer-windows.zip. Needs Python 3 from python.org (tick "Add to PATH").
cd /d "%~dp0"
if not exist .buildenv py -3 -m venv .buildenv || python -m venv .buildenv
.buildenv\Scripts\python build.py
pause
