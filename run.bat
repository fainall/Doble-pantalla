@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python no esta instalado o no esta en el PATH.
    echo     Instala Python 3.10+ desde https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist .venv (
    echo [i] Creando entorno virtual...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

python server.py %*
