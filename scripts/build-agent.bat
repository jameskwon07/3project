@echo off
REM Agent build script (Windows)

echo 🔨 Starting Agent build...

cd /d %~dp0\..\agent\Program

REM Build Windows x64
echo 📦 Building Windows x64...
dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ..\..\dist\agent-windows

REM Build macOS x64 (cross-compile)
echo 📦 Building macOS x64...
dotnet publish -c Release -r osx-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ..\..\dist\agent-macos-x64

REM Build macOS ARM64 (cross-compile)
echo 📦 Building macOS ARM64...
dotnet publish -c Release -r osx-arm64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ..\..\dist\agent-macos-arm64

echo.
echo ✅ Build completed!
echo    Windows: dist\agent-windows\Agent.exe
echo    macOS x64: dist\agent-macos-x64\Agent
echo    macOS ARM64: dist\agent-macos-arm64\Agent
pause

