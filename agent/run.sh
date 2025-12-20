#!/bin/bash
# Script to run the Agent with proper setup

set -e

echo "🧹 Cleaning build artifacts..."
dotnet clean Program/Agent.csproj --verbosity quiet 2>/dev/null || true

echo "📦 Restoring dependencies for all projects..."
# Restore all projects to ensure test project dependencies are also restored
dotnet restore Program/Agent.csproj

echo "🚀 Building Agent..."
dotnet build Program/Agent.csproj --no-restore

echo "🚀 Running Agent..."
dotnet run --project Program/Agent.csproj --no-build

