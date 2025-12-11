# PowerShell 초기화 스크립트
# Windows 환경 설정 및 의존성 확인

Write-Host "🔧 프로젝트 초기화 중..." -ForegroundColor Cyan

# Python 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 설치됨: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python이 설치되어 있지 않습니다." -ForegroundColor Red
    exit 1
}

# Git 확인
try {
    $gitVersion = git --version 2>&1
    Write-Host "✓ Git 설치됨: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Git이 설치되어 있지 않습니다. 버전 태깅이 작동하지 않을 수 있습니다." -ForegroundColor Yellow
}

# 디렉토리 생성
$directories = @("config", "scripts", "build", "dist")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✓ 디렉토리 생성: $dir" -ForegroundColor Green
    }
}

Write-Host "`n✅ 초기화 완료!" -ForegroundColor Green

