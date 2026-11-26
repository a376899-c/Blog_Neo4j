@echo off
REM Abre la aplicacion del Blog (doble clic sobre este archivo)
cd /d "%~dp0"
python app.py
if errorlevel 1 pause
