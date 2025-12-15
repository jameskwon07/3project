#!/bin/bash
# Agent build script (Mac/Linux)

set -e

echo "🔨 Starting Agent build..."

cd "$(dirname "$0")/../agent"

# Build Windows x64
echo "📦 Building Windows x64..."
dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ../dist/agent-windows

# Build macOS x64
echo "📦 Building macOS x64..."
dotnet publish -c Release -r osx-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ../dist/agent-macos-x64

# Build macOS ARM64 (Apple Silicon)
echo "📦 Building macOS ARM64..."
dotnet publish -c Release -r osx-arm64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o ../dist/agent-macos-arm64

echo "✅ Build completed!"
echo "   Windows: dist/agent-windows/Agent.exe"
echo "   macOS x64: dist/agent-macos-x64/Agent"
echo "   macOS ARM64: dist/agent-macos-arm64/Agent"

