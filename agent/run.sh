#!/bin/bash
# Script to run the Agent with proper setup

set -e

echo "🧹 Cleaning build artifacts..."
dotnet clean Agent.csproj --verbosity quiet 2>/dev/null || true

echo "📦 Restoring dependencies for all projects..."
# Restore all projects to ensure test project dependencies are also restored
dotnet restore

echo "🚀 Building Agent..."
dotnet build Agent.csproj --no-restore

echo "🚀 Running Agent..."
dotnet run --project Agent.csproj --no-build

