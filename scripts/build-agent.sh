#!/bin/bash
# Agent 빌드 스크립트 (Mac/Linux)

set -e

echo "🔨 Agent 빌드 시작..."

cd "$(dirname "$0")/../agent"

# Windows x64 빌드
echo "📦 Windows x64 빌드 중..."
dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ../dist/agent-windows

# macOS x64 빌드
echo "📦 macOS x64 빌드 중..."
dotnet publish -c Release -r osx-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ../dist/agent-macos-x64

# macOS ARM64 빌드 (Apple Silicon)
echo "📦 macOS ARM64 빌드 중..."
dotnet publish -c Release -r osx-arm64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ../dist/agent-macos-arm64

echo "✅ 빌드 완료!"
echo "   Windows: dist/agent-windows/Agent.exe"
echo "   macOS x64: dist/agent-macos-x64/Agent"
echo "   macOS ARM64: dist/agent-macos-arm64/Agent"

