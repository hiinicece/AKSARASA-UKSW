# # PowerShell script untuk menjalankan server
# Write-Host "================================================" -ForegroundColor Cyan
# Write-Host "Starting Museum AI Backend Server" -ForegroundColor Cyan
# Write-Host "================================================" -ForegroundColor Cyan
# Write-Host ""
# Write-Host "Backend API will run on: http://localhost:5000" -ForegroundColor Yellow
# Write-Host "Frontend will run on: http://localhost:8000" -ForegroundColor Yellow
# Write-Host ""
# Write-Host "Press Ctrl+C to stop the servers" -ForegroundColor Red
# Write-Host "================================================" -ForegroundColor Cyan
# Write-Host ""

# # Check if .env exists, if not create it
# if (-not (Test-Path .env)) {
#     "GEMINI_API_KEY=your_api_key_here" | Out-File -FilePath .env -Encoding ASCII
#     Write-Host ""
#     Write-Host "[!] File .env created. Please edit it and add your API key." -ForegroundColor Yellow
#     Write-Host "    Get free API key from: https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
#     Write-Host ""
#     pause
# }

# # Start backend server in new window
# Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python server.py"

# # Wait for backend to start
# Start-Sleep -Seconds 3

# # Start frontend server in new window
# Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m http.server 8000"

# Write-Host ""
# Write-Host "Servers started!" -ForegroundColor Green
# Write-Host ""
# Write-Host "Open your browser and go to:" -ForegroundColor Green
# Write-Host "http://localhost:8000" -ForegroundColor Cyan
# Write-Host ""
# Write-Host "Press any key to exit this window..." -ForegroundColor Gray
# $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
