$ErrorActionPreference = "Stop"
$cliPath = Join-Path $PSScriptRoot "cli.py"
$pythonPath = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $pythonPath) {
    & $pythonPath $cliPath @args
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $cliPath @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $cliPath @args
} else {
    Write-Error "Python was not found. Install Python and add it to PATH."
    exit 1
}

exit $LASTEXITCODE
