
@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Paperlane Local PDF

echo ========================================
echo  Paperlane Local PDF - Windows Launcher
echo ========================================
echo.

where py >nul 2>&1
if not errorlevel 1 goto use_py
where python >nul 2>&1
if not errorlevel 1 goto use_python
echo ERROR: Python was not found.
echo Install Python 3.10 or newer from https://www.python.org/downloads/
echo Enable Add Python to PATH during installation.
goto fail

:use_py
set "PYTHON=py -3"
goto check_venv

:use_python
set "PYTHON=python"

:check_venv
if exist ".venv\Scripts\python.exe" goto launch

echo [1/2] Creating the local Python environment...
%PYTHON% -m venv .venv
if errorlevel 1 goto fail

:install
echo [2/2] Installing required packages. Internet is needed on first launch.
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail

:launch
echo Starting Paperlane at http://127.0.0.1:8765
".venv\Scripts\python.exe" app.py
if errorlevel 1 goto fail

echo.
echo Paperlane has stopped.
pause
exit /b 0

:fail
echo.
echo ERROR: Paperlane could not start. Read the error message above.
pause
exit /b 1
