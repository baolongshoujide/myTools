param([switch]$SkipModels, [switch]$UseCuda)
$ErrorActionPreference = 'Stop'
$featureRoot = $PSScriptRoot
$env:UV_PYTHON_INSTALL_DIR = Join-Path $featureRoot '.runtime\python'
$env:UV_CACHE_DIR = Join-Path $featureRoot '.runtime\uv-cache'
$uvPath = Join-Path $featureRoot '.runtime\uv\uv.exe'
$pythonPath = Join-Path $featureRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $uvPath)) {
    New-Item -ItemType Directory -Force -Path "$featureRoot\.runtime" | Out-Null
    $archivePath = Join-Path $featureRoot '.runtime\uv.zip'
    curl.exe -fL --retry 2 'https://github.com/astral-sh/uv/releases/download/0.13.8/uv-x86_64-pc-windows-msvc.zip' -o $archivePath
    if ($LASTEXITCODE -ne 0) { throw 'uv download failed.' }
    $expectedHash = '529E78A9CEC6CD7E3E014F7ECD8BDA0C113969D4ED0F2EFEEDB85C30943325B8'
    if ((Get-FileHash -LiteralPath $archivePath).Hash -ne $expectedHash) { throw 'uv checksum mismatch.' }
    Expand-Archive -LiteralPath $archivePath -DestinationPath "$featureRoot\.runtime\uv" -Force
}
if (-not (Test-Path -LiteralPath $pythonPath)) {
    & $uvPath --system-certs python install 3.12
    if ($LASTEXITCODE -ne 0) { throw 'Python installation failed.' }
    & $uvPath venv --python 3.12 "$featureRoot\.venv"
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
$torchIndex = if ($UseCuda) { 'https://download.pytorch.org/whl/cu128' } else { 'https://download.pytorch.org/whl/cpu' }
& $uvPath --system-certs pip install --python $pythonPath torch==2.9.1 torchvision==0.24.1 --index-url $torchIndex --reinstall-package torch --reinstall-package torchvision
if ($LASTEXITCODE -ne 0) { throw 'PyTorch installation failed.' }
& $uvPath --system-certs pip install --python $pythonPath -r "$featureRoot\requirements.txt"
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if (-not $SkipModels) {
    & $pythonPath "$featureRoot\download_models.py"
    if ($LASTEXITCODE -ne 0) { throw 'Model download failed. Rerun setup.ps1 to resume.' }
    & $pythonPath "$featureRoot\pipeline.py" --prepare
    if ($LASTEXITCODE -ne 0) { throw 'Model preparation failed. Check the network and rerun setup.ps1.' }
}
Write-Host 'Setup complete.'
