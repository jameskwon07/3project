@echo off
REM Setup Git hooks for the project

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d %PROJECT_ROOT%
set GIT_HOOKS_DIR=%PROJECT_ROOT%\.git\hooks

echo 🔧 Setting up Git hooks...
echo.

REM Check if .git\hooks directory exists
if not exist "%GIT_HOOKS_DIR%" (
    echo ❌ Error: .git\hooks directory not found.
    echo    Make sure you're in a Git repository.
    exit /b 1
)

REM Setup pre-push hook
set PRE_PUSH_HOOK=%GIT_HOOKS_DIR%\pre-push
set PRE_PUSH_SCRIPT=%SCRIPT_DIR%pre-push

if exist "%PRE_PUSH_SCRIPT%" (
    REM Copy pre-push hook
    copy "%PRE_PUSH_SCRIPT%" "%PRE_PUSH_HOOK%" >nul
    echo ✅ Pre-push hook installed: %PRE_PUSH_HOOK%
) else (
    echo ⚠️  Warning: pre-push script not found: %PRE_PUSH_SCRIPT%
)

echo.
echo ✅ Git hooks setup completed!
echo.
echo The pre-push hook will now test GitHub Actions workflows locally before allowing push.
echo.
echo To skip hooks temporarily (not recommended):
echo   git push --no-verify


