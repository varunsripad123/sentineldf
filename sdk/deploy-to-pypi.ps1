# Deploy SentinelDF SDK to PyPI
# Version: 2.0.2
# Phase 1: Span highlights, confidence scores, and advanced security

Write-Host "🚀 Deploying SentinelDF SDK v2.0.2 to PyPI" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "setup.py")) {
    Write-Host "❌ Error: Not in SDK directory. Run from sentineldf/sdk/" -ForegroundColor Red
    exit 1
}

# Check for required tools
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
$tools = @("python", "pip", "twine")
foreach ($tool in $tools) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Error: $tool not found. Please install it first." -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ All dependencies found" -ForegroundColor Green
Write-Host ""

# Clean previous builds
Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force dist, build, sentineldf.egg-info -ErrorAction SilentlyContinue
Write-Host "✅ Cleaned" -ForegroundColor Green
Write-Host ""

# Install/upgrade build tools
Write-Host "📦 Installing build tools..." -ForegroundColor Yellow
pip install --upgrade setuptools wheel twine
Write-Host "✅ Build tools ready" -ForegroundColor Green
Write-Host ""

# Build distributions
Write-Host "🔨 Building distribution packages..." -ForegroundColor Yellow
python setup.py sdist bdist_wheel

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build successful" -ForegroundColor Green
Write-Host ""

# Check package
Write-Host "🔍 Checking package..." -ForegroundColor Yellow
twine check dist/*

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Package check failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Package looks good" -ForegroundColor Green
Write-Host ""

# Ask for confirmation
Write-Host "📋 Package contents:" -ForegroundColor Cyan
Get-ChildItem dist | Format-Table Name, Length -AutoSize
Write-Host ""

$confirm = Read-Host "Deploy to PyPI? (yes/no/test)"

if ($confirm -eq "test") {
    Write-Host "📤 Uploading to TestPyPI..." -ForegroundColor Yellow
    twine upload --repository testpypi dist/*
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Upload to TestPyPI successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🧪 Test installation with:" -ForegroundColor Cyan
        Write-Host "pip install --index-url https://test.pypi.org/simple/ sentineldf==2.0.2" -ForegroundColor White
    } else {
        Write-Host "❌ Upload failed!" -ForegroundColor Red
        exit 1
    }
}
elseif ($confirm -eq "yes") {
    Write-Host "📤 Uploading to PyPI..." -ForegroundColor Yellow
    twine upload dist/*
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Successfully deployed to PyPI!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📦 Users can now install with:" -ForegroundColor Cyan
        Write-Host "pip install --upgrade sentineldf" -ForegroundColor White
        Write-Host ""
        Write-Host "🔗 Package URL:" -ForegroundColor Cyan
        Write-Host "https://pypi.org/project/sentineldf/2.0.2/" -ForegroundColor White
    } else {
        Write-Host "❌ Upload failed!" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✨ Phase 1 Features:" -ForegroundColor Cyan
Write-Host "  - Span-level highlights" -ForegroundColor White
Write-Host "  - Confidence scores" -ForegroundColor White
Write-Host "  - Multi-signal detection" -ForegroundColor White
Write-Host "  - SHA-256 hashed API keys" -ForegroundColor White
Write-Host "  - 10x faster pattern matching" -ForegroundColor White
