@echo off
REM Windows deployment batch script
REM Usage: deploy.bat [version] [--skip-tests] [--skip-build]

setlocal enabledelayedexpansion

set VERSION=%1
set SKIP_TESTS=0
set SKIP_BUILD=0

REM Parse arguments
if "%2"=="--skip-tests" set SKIP_TESTS=1
if "%2"=="--skip-build" set SKIP_BUILD=1
if "%3"=="--skip-tests" set SKIP_TESTS=1
if "%3"=="--skip-build" set SKIP_BUILD=1

if "%VERSION%"=="" (
    echo Error: Please specify version.
    echo Usage: deploy.bat [version] [--skip-tests] [--skip-build]
    exit /b 1
)

echo ========================================
echo Starting deployment: Version %VERSION%
echo ========================================

REM Run Python deployment script
python deploy.py --version %VERSION% ^
    %2 %3

if errorlevel 1 (
    echo.
    echo ❌ Deployment failed
    exit /b 1
)

echo.
echo ✅ Deployment completed!
pause

