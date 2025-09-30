$venvPython = ".\venv\Scripts\python.exe"
$flake8 = ".\venv\Scripts\flake8.exe"
$black = ".\venv\Scripts\black.exe"

if (-not (Test-Path $venvPython)) {
    Write-Warning "Virtual environment not found. Please run install.ps1 first."
    exit 1
}

Write-Host "Running Black formatter..." -ForegroundColor Green
& $black src/

Write-Host "Running Flake8 linter..." -ForegroundColor Green
& $flake8 src/

if ($LASTEXITCODE -eq 0) {
    Write-Host "All checks passed!" -ForegroundColor Green
}
else {
    Write-Host "Linting issues found. Please fix them." -ForegroundColor Red
}
