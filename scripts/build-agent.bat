@echo off
REM Agent 빌드 스크립트 (Windows)

echo 🔨 Agent 빌드 시작...

cd /d %~dp0\..\agent

REM Windows x64 빌드
echo 📦 Windows x64 빌드 중...
dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ..\dist\agent-windows

REM macOS x64 빌드 (크로스 컴파일)
echo 📦 macOS x64 빌드 중...
dotnet publish -c Release -r osx-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ..\dist\agent-macos-x64

REM macOS ARM64 빌드 (크로스 컴파일)
echo 📦 macOS ARM64 빌드 중...
dotnet publish -c Release -r osx-arm64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ..\dist\agent-macos-arm64

echo.
echo ✅ 빌드 완료!
echo    Windows: dist\agent-windows\Agent.exe
echo    macOS x64: dist\agent-macos-x64\Agent
echo    macOS ARM64: dist\agent-macos-arm64\Agent
pause

