$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot

try {
    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            & py -3 -m venv .venv
        } elseif (Get-Command python -ErrorAction SilentlyContinue) {
            & python -m venv .venv
        } else {
            throw "Python was not found. Install Python and add it to PATH."
        }
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    & .\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    New-Item -ItemType Directory -Path build -Force | Out-Null
    & .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --console --name GithubUserActivity --specpath build cli.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "Created dist\GithubUserActivity.exe"
} finally {
    Pop-Location
}
