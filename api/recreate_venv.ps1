# Recreate venv after project move (fixes broken pip/python paths)
# Run from: C:\Users\johnk\Workspace\Capstone\api

Write-Host "Deactivating current venv if active..." -ForegroundColor Yellow
# If venv is active, deactivate first (run 'deactivate' in your terminal before running this)

Write-Host "Removing old venv..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Remove-Item -Recurse -Force venv
}

Write-Host "Creating new virtual environment..." -ForegroundColor Green
python -m venv venv

Write-Host "Activating and installing dependencies..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Done. Your venv is ready at $(Get-Location)\venv" -ForegroundColor Green
