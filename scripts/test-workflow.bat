@echo off
REM Test GitHub Actions workflows locally using act
REM Install act: https://github.com/nektos/act

set WORKFLOW_FILE=.github\workflows\ci.yml

echo 🔍 Testing GitHub Actions workflow locally...
echo.

REM Check if act is installed
where act >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: 'act' is not installed.
    echo.
    echo Please install act to test workflows locally:
    echo   Windows: https://github.com/nektos/act#installation
    echo.
    echo Documentation: https://github.com/nektos/act
    exit /b 1
)

REM Check if workflow file exists
if not exist "%WORKFLOW_FILE%" (
    echo ❌ Error: Workflow file not found: %WORKFLOW_FILE%
    exit /b 1
)

echo 📋 Available jobs:
echo   - master-backend: Test backend build and tests
echo   - master-frontend: Test frontend build
echo.
echo 💡 Usage examples:
echo   Run all jobs: scripts\test-workflow.bat
echo   Run specific job: act -j master-backend
echo   List jobs: act -l
echo.

REM Run act
if "%1"=="" (
    REM Run all jobs
    echo 🚀 Running all jobs...
    echo    (Note: Some jobs may require platform-specific runners)
    act
) else (
    REM Run specific job if provided
    echo 🚀 Running job: %1
    act -j %1
)

echo.
echo ✅ Workflow test completed!
echo.
echo 📝 Note: Some jobs (e.g., agent-windows, agent-macos) require platform-specific
echo    runners and may not run on Windows. Use 'act -j ^<job-name^>' to test specific jobs.


