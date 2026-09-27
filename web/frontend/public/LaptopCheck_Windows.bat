@echo off
title LaptopCheck - Local Hardware Diagnostic Collector
echo ======================================================================
echo   LaptopCheck - Hardware Diagnostic & Provenance Collector
echo ======================================================================
echo   Collecting system, CPU, RAM, storage, and battery telemetry...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scan.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Collector finished or script error encountered.
    pause
)
