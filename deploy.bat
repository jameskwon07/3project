@echo off
REM Windows 배포 배치 스크립트
REM 사용법: deploy.bat [version] [--skip-tests] [--skip-build]

setlocal enabledelayedexpansion

set VERSION=%1
set SKIP_TESTS=0
set SKIP_BUILD=0

REM 인자 파싱
if "%2"=="--skip-tests" set SKIP_TESTS=1
if "%2"=="--skip-build" set SKIP_BUILD=1
if "%3"=="--skip-tests" set SKIP_TESTS=1
if "%3"=="--skip-build" set SKIP_BUILD=1

if "%VERSION%"=="" (
    echo 오류: 버전을 지정해주세요.
    echo 사용법: deploy.bat [version] [--skip-tests] [--skip-build]
    exit /b 1
)

echo ========================================
echo 배포 시작: 버전 %VERSION%
echo ========================================

REM Python 배포 스크립트 실행
python deploy.py --version %VERSION% ^
    %2 %3

if errorlevel 1 (
    echo.
    echo ❌ 배포 실패
    exit /b 1
)

echo.
echo ✅ 배포 완료!
pause

