@echo off
REM LaptopCheck Windows Packaging Script
REM Builds standalone LaptopCheck.exe without requiring Python installed on target machine.

echo ============================================================
echo  Packaging LaptopCheck for Windows (Standalone Executable)  
echo ============================================================

REM 1. Build Frontend
cd web\frontend
call npm run build
cd ..\..

REM 2. Run PyInstaller
pyinstaller ^
    --name LaptopCheck ^
    --noconfirm ^
    --clean ^
    --add-data "web\frontend\dist;web\frontend\dist" ^
    --hidden-import=uvicorn.logging ^
    --hidden-import=uvicorn.loops ^
    --hidden-import=uvicorn.loops.auto ^
    --hidden-import=uvicorn.protocols ^
    --hidden-import=uvicorn.protocols.http ^
    --hidden-import=uvicorn.protocols.http.auto ^
    --hidden-import=uvicorn.lifespan ^
    --hidden-import=uvicorn.lifespan.on ^
    --hidden-import=matplotlib ^
    --hidden-import=reportlab ^
    --hidden-import=psutil ^
    --hidden-import=numpy ^
    run.py

echo Packaging Complete!
echo Standalone executable located at: dist\LaptopCheck\LaptopCheck.exe
