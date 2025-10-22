# Phase 1.5 Deployment Script
# - Frontend updates (scan demo with highlights)
# - SDK v2.0.2 (fixed reporting)
# - Documentation

Write-Host "🚀 Phase 1.5 Deployment" -ForegroundColor Cyan
Write-Host ""

# Step 1: Commit changes
Write-Host "📝 Step 1: Committing changes..." -ForegroundColor Yellow
git add .
git status

$confirm = Read-Host "Commit these changes? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 1
}

git commit -m "Phase 1.5: Frontend UI + SDK v2.0.2

✨ Frontend:
- Interactive scan demo with span highlights
- Confidence score visualization
- Multi-signal breakdown display
- Real-time threat highlighting

📦 SDK:
- Version 2.0.2 (fixed reporting bug)
- Updated CLI version string
- PyPI deployment script

📚 Documentation:
- Complete API response v2 guide
- Phase 1 deployment guide
- Migration instructions
- UI integration examples"

Write-Host "✅ Changes committed" -ForegroundColor Green
Write-Host ""

# Step 2: Push to GitHub
Write-Host "📤 Step 2: Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Push failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Pushed to GitHub" -ForegroundColor Green
Write-Host ""

# Step 3: Deploy Frontend
Write-Host "🌐 Step 3: Deploying frontend..." -ForegroundColor Yellow
Write-Host "Options:" -ForegroundColor Cyan
Write-Host "  1. Auto-deploy via Netlify (from GitHub)" -ForegroundColor White
Write-Host "  2. Manual deploy via Netlify CLI" -ForegroundColor White
Write-Host ""

$deployChoice = Read-Host "Choose option (1/2/skip)"

if ($deployChoice -eq "2") {
    Set-Location landing-page
    npm run build
    netlify deploy --prod
    Set-Location ..
    Write-Host "✅ Frontend deployed" -ForegroundColor Green
} elseif ($deployChoice -eq "1") {
    Write-Host "⏳ Waiting for Netlify auto-deploy..." -ForegroundColor Yellow
    Write-Host "   Check: https://app.netlify.com/sites/sentineldf/deploys" -ForegroundColor Cyan
    Write-Host "✅ Auto-deploy triggered" -ForegroundColor Green
} else {
    Write-Host "⏭️  Skipped frontend deployment" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Deploy SDK to PyPI
Write-Host "📦 Step 4: Deploying SDK to PyPI..." -ForegroundColor Yellow
$pypiChoice = Read-Host "Deploy SDK to PyPI? (yes/test/no)"

if ($pypiChoice -eq "yes" -or $pypiChoice -eq "test") {
    Set-Location sdk
    .\deploy-to-pypi.ps1
    Set-Location ..
} else {
    Write-Host "⏭️  Skipped PyPI deployment" -ForegroundColor Yellow
    Write-Host "   Run manually: cd sdk && .\deploy-to-pypi.ps1" -ForegroundColor Cyan
}
Write-Host ""

# Step 5: Summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🎉 Phase 1.5 Deployment Summary" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Code committed and pushed" -ForegroundColor Green
Write-Host "✅ API already deployed (Render auto-deploy from GitHub)" -ForegroundColor Green
Write-Host ""

Write-Host "🔗 URLs:" -ForegroundColor Cyan
Write-Host "  Dashboard: https://sentineldf.netlify.app/dashboard" -ForegroundColor White
Write-Host "  Test API: https://sentineldf.netlify.app/dashboard (Test API tab)" -ForegroundColor White
Write-Host "  API: https://sentineldf.onrender.com/v1/scan" -ForegroundColor White
Write-Host "  GitHub: https://github.com/varunsripad123/sentineldf" -ForegroundColor White
Write-Host ""

Write-Host "📚 New Documentation:" -ForegroundColor Cyan
Write-Host "  - PHASE_1_DEPLOYMENT.md (complete guide)" -ForegroundColor White
Write-Host "  - API_RESPONSE_V2.md (API reference)" -ForegroundColor White
Write-Host ""

Write-Host "✨ New Features Live:" -ForegroundColor Cyan
Write-Host "  ✅ Span-level highlights with character offsets" -ForegroundColor White
Write-Host "  ✅ Confidence scores (0.5-1.0)" -ForegroundColor White
Write-Host "  ✅ Multi-signal breakdown" -ForegroundColor White
Write-Host "  ✅ Interactive test UI" -ForegroundColor White
Write-Host "  ✅ SDK v2.0.2 with fixed reporting" -ForegroundColor White
Write-Host ""

Write-Host "🧪 Test Now:" -ForegroundColor Cyan
Write-Host "  1. Go to: https://sentineldf.netlify.app/dashboard" -ForegroundColor White
Write-Host "  2. Click 'Test API' tab" -ForegroundColor White
Write-Host "  3. Enter API key: sk_live_QF-2iFVEpn-3HLaJOkh_cx5qYLJaGQCz7oZ0tHMahBM" -ForegroundColor White
Write-Host "  4. Try example texts and see highlights!" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Next: Deploy SDK to PyPI if not already done" -ForegroundColor Yellow
Write-Host "   cd sdk && .\deploy-to-pypi.ps1" -ForegroundColor Cyan
Write-Host ""
