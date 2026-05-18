@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

REM ============================================================
REM   Construye el APK de la app Android desde la terminal de
REM   Windows sin necesidad de Android Studio.
REM   Requiere: JDK 17 instalado y en PATH.
REM   Lo demas (SDK Android + Gradle) se baja la primera vez en
REM   %USERPROFILE%\.doblepantalla-build (~2 GB).
REM ============================================================

where java >nul 2>nul
if errorlevel 1 (
    echo [!] No encuentro Java en el PATH.
    echo     Instala JDK 17 (Temurin/Adoptium) desde:
    echo     https://adoptium.net/temurin/releases/?version=17
    pause
    exit /b 1
)

set "TOOLS_DIR=%USERPROFILE%\.doblepantalla-build"
set "SDK_DIR=%TOOLS_DIR%\android-sdk"
set "GRADLE_VERSION=8.10.2"
set "GRADLE_DIR=%TOOLS_DIR%\gradle-%GRADLE_VERSION%"
set "ANDROID_HOME=%SDK_DIR%"
set "ANDROID_SDK_ROOT=%SDK_DIR%"
set "PATH=%GRADLE_DIR%\bin;%SDK_DIR%\cmdline-tools\latest\bin;%SDK_DIR%\platform-tools;%PATH%"

if not exist "%TOOLS_DIR%" mkdir "%TOOLS_DIR%"

if not exist "%SDK_DIR%\cmdline-tools\latest\bin\sdkmanager.bat" (
    echo [i] Descargando Android command-line tools...
    if not exist "%SDK_DIR%\cmdline-tools" mkdir "%SDK_DIR%\cmdline-tools"
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip' -OutFile '%TOOLS_DIR%\cmdline-tools.zip'"
    if errorlevel 1 ( echo [!] Fallo la descarga de cmdline-tools. & pause & exit /b 1 )
    powershell -NoProfile -Command "Expand-Archive -Path '%TOOLS_DIR%\cmdline-tools.zip' -DestinationPath '%SDK_DIR%\cmdline-tools' -Force"
    move "%SDK_DIR%\cmdline-tools\cmdline-tools" "%SDK_DIR%\cmdline-tools\latest" >nul
    del "%TOOLS_DIR%\cmdline-tools.zip"
)

echo [i] Aceptando licencias del SDK...
(for /l %%i in (1,1,20) do @echo y) | call sdkmanager.bat --licenses >nul

echo [i] Instalando paquetes del SDK (puede tardar varios minutos)...
call sdkmanager.bat "platform-tools" "platforms;android-34" "build-tools;34.0.0"
if errorlevel 1 ( echo [!] Fallo sdkmanager. & pause & exit /b 1 )

if not exist "%GRADLE_DIR%\bin\gradle.bat" (
    echo [i] Descargando Gradle %GRADLE_VERSION%...
    powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://services.gradle.org/distributions/gradle-%GRADLE_VERSION%-bin.zip' -OutFile '%TOOLS_DIR%\gradle.zip'"
    if errorlevel 1 ( echo [!] Fallo la descarga de Gradle. & pause & exit /b 1 )
    powershell -NoProfile -Command "Expand-Archive -Path '%TOOLS_DIR%\gradle.zip' -DestinationPath '%TOOLS_DIR%' -Force"
    del "%TOOLS_DIR%\gradle.zip"
)

cd android

if not exist gradlew.bat (
    echo [i] Generando gradle wrapper...
    call gradle.bat wrapper --gradle-version %GRADLE_VERSION%
    if errorlevel 1 ( echo [!] No se pudo generar el wrapper. & pause & exit /b 1 )
)

echo [i] Compilando el APK (la primera vez tarda; descarga dependencias)...
call gradlew.bat assembleDebug --no-daemon
if errorlevel 1 ( echo [!] Compilacion fallida. & pause & exit /b 1 )

set "APK=app\build\outputs\apk\debug\app-debug.apk"
if not exist "%APK%" (
    echo [!] No se encontro el APK donde se esperaba.
    pause
    exit /b 1
)

echo.
echo [OK] APK generado:
echo      %CD%\%APK%
echo.
echo Copialo a la tablet (USB, Drive, etc.) y abrelo para instalar.
pause
