@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python no esta instalado o no esta en el PATH.
    pause
    exit /b 1
)

if not exist .venv (
    echo [i] Creando entorno virtual...
    python -m venv .venv
)
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
del /Q DoblePantalla.spec 2>nul

pyinstaller --noconfirm --onefile --name DoblePantalla ^
    --collect-submodules mss ^
    --hidden-import input_win ^
    --console ^
    server.py

if errorlevel 1 (
    echo [!] PyInstaller fallo.
    pause
    exit /b 1
)

echo.
echo [OK] Ejecutable generado en dist\DoblePantalla.exe
echo     Doble-click para arrancar el servidor.
echo.
pause
