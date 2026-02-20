@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>nul

REM Betigin bulundugu klasore git
cd /d "%~dp0"
set "PROJECT_ROOT=%CD%"

echo ========================================
echo WinnerTrade Build
echo ========================================
echo Proje klasoru: %PROJECT_ROOT%
python --version 2>nul
echo.

REM Python 3.11 veya 3.12 onerilir; 3.13/3.14 ve Turkce karakterli kullanici yolu build hatalarina yol acabilir
python -c "import sys; sys.exit(0 if sys.version_info < (3,13) else 1)" 2>nul
if errorlevel 1 (
    echo UYARI: Python 3.13+ tespit edildi. Build icin Python 3.11 veya 3.12 kullanmaniz onerilir.
    echo Ornek: "py -3.12 -m venv backend\venv_build" sonra "backend\venv_build\Scripts\activate" ve tekrar build-windows.bat
    echo Devam etmek istiyorsaniz bir tusa basin.
    pause
)

REM Kontrol: backend ve frontend var mi?
if not exist "%PROJECT_ROOT%\backend\winnertrade.spec" (
    echo HATA: backend\winnertrade.spec bulunamadi. Bu dosyayi proje kokunden calistirin.
    pause
    exit /b 1
)
if not exist "%PROJECT_ROOT%\frontend\package.json" (
    echo HATA: frontend\package.json bulunamadi.
    pause
    exit /b 1
)

echo.
echo [1/4] Backend exe - PyInstaller...
cd /d "%PROJECT_ROOT%\backend"

if not exist "dist\winnertrade-backend.exe" (
    echo Pip ile requirements-build.txt yukleniyor...
    python -m pip install -r requirements-build.txt
    if errorlevel 1 (
        echo HATA: pip install basarisiz. Python 3.10+ kurulu ve PATH te mi? python --version deneyin.
        pause
        exit /b 1
    )
    echo PyInstaller calistiriliyor...
    python -m PyInstaller winnertrade.spec
    if errorlevel 1 (
        echo HATA: PyInstaller build basarisiz.
        pause
        exit /b 1
    )
) else (
    echo Backend exe zaten var, atlaniyor.
)

if not exist "dist\winnertrade-backend.exe" (
    echo HATA: dist\winnertrade-backend.exe olusmadi.
    pause
    exit /b 1
)

echo.
echo [2/4] Frontend build...
cd /d "%PROJECT_ROOT%\frontend"
call npm run build
if errorlevel 1 (
    echo HATA: npm run build basarisiz. Once npm install calistirdiniz mi?
    pause
    exit /b 1
)

echo.
echo [3/4] Electron installer...
call npm run electron:build
if errorlevel 1 (
    echo HATA: electron-builder basarisiz.
    pause
    exit /b 1
)

echo.
echo [4/4] Tamamlandi.
echo Cikti: %PROJECT_ROOT%\frontend\release\
dir /b "%PROJECT_ROOT%\frontend\release\*.exe" 2>nul
echo.
pause
