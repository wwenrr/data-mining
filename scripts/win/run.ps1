# run.ps1
$venvPython = ".\venv\Scripts\python.exe"

$versionOutput = & $venvPython --version
if ($versionOutput -notmatch "Python 3\.13\.7") {
    Write-Error "Warning Python version deprecated. Expected Python 3.13.7, but got: $versionOutput"
}

if (-not (Test-Path $venvPython)) {
    Write-Warning "Virtual environment not found. Please run install.ps1 first."
}

& $venvPython -B "src/run.py" @args
