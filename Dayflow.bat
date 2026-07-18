@echo off
chcp 65001 >nul
cd /d "%~dp0"
python dayflow.py
if errorlevel 1 py -3 dayflow.py
pause
