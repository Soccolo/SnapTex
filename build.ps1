$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Run setup.bat before building."
}

& .venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .venv\Scripts\python.exe -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name SnapTeX `
    --paths src `
    --collect-all pix2tex `
    --collect-all timm `
    --collect-all transformers `
    src\snaptex\__main__.py

Write-Host "Built dist\SnapTeX\SnapTeX.exe"
