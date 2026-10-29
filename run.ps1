$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $project

$preferredPython = Join-Path $env:LOCALAPPDATA "Python\pythoncore-3.15-64\python.exe"
if (Test-Path $preferredPython) {
    $python = $preferredPython
} else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python was not found. Install Python 3.13+ and select it in VS Code."
    }
    $python = $pythonCommand.Source
}

$venvPython = Join-Path $project ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating project environment with $python"
    & $python -m venv (Join-Path $project ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create the virtual environment." }
}

Write-Host "Installing/updating project dependencies..."
& $venvPython -m pip install -r (Join-Path $project "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed. See the error above." }

Write-Host "Starting Papertrail. Press Ctrl+C to stop it."
& $venvPython -m streamlit run (Join-Path $project "app.py")
exit $LASTEXITCODE
