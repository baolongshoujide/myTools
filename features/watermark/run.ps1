param([string]$InputImage, [ValidateSet('auto','cpu','cuda')][string]$Device = 'auto')
$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run setup.ps1 first.' }
if (-not $InputImage) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Filter = 'Images|*.png;*.jpg;*.jpeg;*.webp;*.bmp'
    if ($dialog.ShowDialog() -ne 'OK') { exit 0 }
    $InputImage = $dialog.FileName
}
$outputFolder = Join-Path $PSScriptRoot ('outputs\' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
& $pythonPath "$PSScriptRoot\pipeline.py" $InputImage --output $outputFolder --device $Device
if ($LASTEXITCODE -ne 0) { throw 'Processing failed. See the error above.' }
Invoke-Item -LiteralPath $outputFolder
