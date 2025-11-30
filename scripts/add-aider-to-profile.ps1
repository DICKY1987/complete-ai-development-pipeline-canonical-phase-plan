# DOC_LINK: DOC-SCRIPT-ADD-AIDER-TO-PROFILE-050
# Add Aider environment variables to PowerShell profile
# This makes the settings permanent across all PowerShell sessions

$profilePath = $PROFILE

Write-Host "Adding Aider environment variables to PowerShell profile..." -ForegroundColor Cyan
Write-Host "Profile: $profilePath" -ForegroundColor Gray
Write-Host ""

# Create profile if it doesn't exist
if (-not (Test-Path $profilePath)) {
    New-Item -Path $profilePath -ItemType File -Force | Out-Null
    Write-Host "Created new PowerShell profile" -ForegroundColor Yellow
}

# Check if already configured
$profileContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
if ($profileContent -match "AIDER_MODEL") {
    Write-Host "Aider configuration already exists in profile!" -ForegroundColor Yellow
    Write-Host "Skipping to avoid duplicates." -ForegroundColor Gray
    Write-Host ""
    Write-Host "To update manually, edit: $profilePath" -ForegroundColor Cyan
    exit 0
}

# Add configuration to profile
$config = @"

# ===== Aider + Ollama Configuration =====
# Added by add-aider-to-profile.ps1

# Fix Windows Unicode encoding issues
`$env:PYTHONIOENCODING = "utf-8"
`$env:PYTHONUTF8 = "1"

# Ollama configuration
`$env:OLLAMA_API_BASE = "http://127.0.0.1:11434"

# Default to DeepSeek-R1 model
`$env:AIDER_MODEL = "ollama_chat/deepseek-r1:latest"

# ===== End Aider Configuration =====
"@

Add-Content -Path $profilePath -Value $config

Write-Host "✓ Added Aider configuration to PowerShell profile" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration added:" -ForegroundColor Yellow
Write-Host $config
Write-Host ""
Write-Host "To activate in current session, run:" -ForegroundColor Cyan
Write-Host "  . `$PROFILE" -ForegroundColor White
Write-Host ""
Write-Host "Or open a new PowerShell window." -ForegroundColor Cyan
