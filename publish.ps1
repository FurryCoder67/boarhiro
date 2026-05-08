# publish.ps1 — Build and upload BOARHIRO to PyPI
# Usage: .\publish.ps1
# First time: you'll be prompted for your PyPI API token

Write-Host "BOARHIRO Publisher" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

# 1. Clean old builds
Write-Host "Cleaning old builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# 2. Install build tools if needed
Write-Host "Checking build tools..." -ForegroundColor Yellow
pip install --upgrade build twine --quiet

# 3. Build
Write-Host "Building package..." -ForegroundColor Yellow
python -m build
if ($LASTEXITCODE -ne 0) { Write-Host "Build failed." -ForegroundColor Red; exit 1 }

# 4. Upload to PyPI
Write-Host "Uploading to PyPI..." -ForegroundColor Yellow
Write-Host "(You'll need your PyPI API token. Get one at https://pypi.org/manage/account/token/)" -ForegroundColor DarkGray
twine upload dist/*

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Published! Anyone can now install with:" -ForegroundColor Green
    Write-Host "  pip install boarhiro" -ForegroundColor White
} else {
    Write-Host "Upload failed. Check your API token." -ForegroundColor Red
}
