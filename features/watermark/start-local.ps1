$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run setup.ps1 first.' }
Set-Location -LiteralPath $PSScriptRoot
& $pythonPath -m uvicorn server:app --host 127.0.0.1 --port 8765
if ($LASTEXITCODE -ne 0) { throw 'Local server stopped with an error.' }
