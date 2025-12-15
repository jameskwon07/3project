# PowerShell initialization script
# Windows environment setup and dependency check

Write-Host "🔧 Initializing project..." -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed." -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = git --version 2>&1
    Write-Host "✓ Git installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Git is not installed. Version tagging may not work." -ForegroundColor Yellow
}

# Create directories
$directories = @("config", "scripts", "build", "dist")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✓ Directory created: $dir" -ForegroundColor Green
    }
}

Write-Host "`n✅ Initialization completed!" -ForegroundColor Green

