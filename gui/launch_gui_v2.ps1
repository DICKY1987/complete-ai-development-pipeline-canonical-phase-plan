# DOC_LINK: DOC-SCRIPT-LAUNCH-GUI-V2-836
# DOC_ID: DOC-SCRIPT-LAUNCH-GUI-V2-017
# GUI v2 Launcher Script (Windows PowerShell)
# Launches the new split-terminal + panel grid interface

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SrcDir = Join-Path $ScriptDir "src"

# Add src to Python path
$env:PYTHONPATH = $SrcDir

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "AI Pipeline GUI v2.0 Launcher" -ForegroundColor Cyan
Write-Host "Split Terminal + Panel Grid Layout" -ForegroundColor Yellow
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Check if PySide6 is installed
try {
    python -c "import PySide6" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "PySide6 not found"
    }
} catch {
    Write-Host "❌ PySide6 not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    python -m pip install -r (Join-Path $ScriptDir "requirements-gui.txt")

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Dependencies OK" -ForegroundColor Green
Write-Host "📁 Working directory: $SrcDir" -ForegroundColor Cyan
Write-Host ""

# Parse arguments
$UseRealData = $true

foreach ($arg in $args) {
    if ($arg -eq "--mock" -or $arg -eq "-m") {
        $UseRealData = $false
    }
}

# Build command
$Command = "python -m gui_app_v2.main"
if (-not $UseRealData) {
    $Command += " --use-mock-data"
    Write-Host "🔧 Mode: Mock data (testing)" -ForegroundColor Yellow
} else {
    Write-Host "🔧 Mode: Real SQLite database" -ForegroundColor Yellow
}
Write-Host ""

# Launch GUI v2
Write-Host "🚀 Launching GUI v2.0..." -ForegroundColor Green
Write-Host "   ⚡ Split terminal + panel grid" -ForegroundColor Cyan
Write-Host "   📊 12 modular panels" -ForegroundColor Cyan
Write-Host "   📁 File lifecycle bar" -ForegroundColor Cyan
Write-Host ""

Set-Location $SrcDir
Invoke-Expression $Command
