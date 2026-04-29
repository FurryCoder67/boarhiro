# start_train.ps1

Write-Host "🐗 BOARHIRO: Igniting the ecosystem..." -ForegroundColor Cyan

# 1. Start the Hunter (The Factory)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python src/auto_generator.py" -WindowStyle Normal

# 2. Start the Local Watcher (The Shipper)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python src/local_watcher.py" -WindowStyle Normal

# 3. Start the BOARHIRO Interface (The Mouth)
# This stays in your current window so you can talk to it immediately
Write-Host "✅ Factory and Shipper are LIVE in the background." -ForegroundColor Green
boarhiro
