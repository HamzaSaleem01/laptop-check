#!/bin/bash
# LaptopCheck Linux Packaging Script
# Builds standalone executable without requiring target machine to have Python installed.

set -e

PROJECT_ROOT="/home/hamza/laptop_check"

echo "============================================================"
echo " Packaging LaptopCheck for Linux (Standalone Executable)     "
echo "============================================================"

# 1. Build frontend distribution
echo "[1/3] Building Web Frontend assets..."
npm --prefix "$PROJECT_ROOT/web/frontend" run build

# 2. Run PyInstaller
echo "[2/3] Bundling Python runtime and dependencies with PyInstaller..."
"$PROJECT_ROOT/venv/bin/pyinstaller" \
    --name LaptopCheck \
    --noconfirm \
    --clean \
    --add-data "$PROJECT_ROOT/web/frontend/dist:web/frontend/dist" \
    --hidden-import=uvicorn.logging \
    --hidden-import=uvicorn.loops \
    --hidden-import=uvicorn.loops.auto \
    --hidden-import=uvicorn.protocols \
    --hidden-import=uvicorn.protocols.http \
    --hidden-import=uvicorn.protocols.http.auto \
    --hidden-import=uvicorn.lifespan \
    --hidden-import=uvicorn.lifespan.on \
    --hidden-import=matplotlib \
    --hidden-import=reportlab \
    --hidden-import=psutil \
    --hidden-import=numpy \
    "$PROJECT_ROOT/run.py"

echo "[3/3] Packaging Complete!"
echo "Standalone executable located at: $PROJECT_ROOT/dist/LaptopCheck/LaptopCheck"
echo "To run without Python: ./dist/LaptopCheck/LaptopCheck --cli"
