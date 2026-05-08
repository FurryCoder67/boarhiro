# release_model.ps1
# Uploads boarhiro_brain.pt to a GitHub Release so users auto-download it.
# Requires: gh (GitHub CLI) — install from https://cli.github.com/
# Usage: .\release_model.ps1 -Tag v0.1.0

param(
    [string]$Tag = "v0.1.0"
)

Write-Host "BOARHIRO Model Release" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

if (!(Test-Path "boarhiro_brain.pt")) {
    Write-Host "ERROR: boarhiro_brain.pt not found. Train the model first with trainboarhiro." -ForegroundColor Red
    exit 1
}

$size = (Get-Item "boarhiro_brain.pt").Length / 1MB
Write-Host "Model size: $([math]::Round($size, 1)) MB" -ForegroundColor Yellow

# Check gh is installed
if (!(Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: GitHub CLI (gh) not installed." -ForegroundColor Red
    Write-Host "Install from: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# Create or update the release
Write-Host "Creating GitHub Release $Tag..." -ForegroundColor Yellow
gh release create $Tag boarhiro_brain.pt `
    --title "BOARHIRO $Tag" `
    --notes "Pre-trained BOARHIRO model. Downloaded automatically on first run." `
    --latest 2>&1

if ($LASTEXITCODE -ne 0) {
    # Release may already exist — try uploading asset to existing release
    Write-Host "Release exists, uploading asset..." -ForegroundColor Yellow
    gh release upload $Tag boarhiro_brain.pt --clobber
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Model uploaded! Users will auto-download it on first run." -ForegroundColor Green
    Write-Host "URL: https://github.com/FurryCoder67/boarhiro/releases/latest/download/boarhiro_brain.pt" -ForegroundColor DarkGray
} else {
    Write-Host "Upload failed. Check your GitHub CLI auth with: gh auth status" -ForegroundColor Red
}
