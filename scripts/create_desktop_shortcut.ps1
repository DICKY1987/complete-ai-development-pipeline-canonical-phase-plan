# DOC_LINK: DOC-SCRIPT-CREATE-DESKTOP-SHORTCUT-060
# PowerShell script to create desktop shortcut for AI Pipeline TUI
# Run with: powershell -ExecutionPolicy Bypass -File scripts\create_desktop_shortcut.ps1

Write-Host "Creating AI Pipeline TUI Desktop Shortcut..." -ForegroundColor Cyan
Write-Host ""

# Get project root (parent of scripts directory)
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Get desktop path
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')

# Shortcut file path
$ShortcutPath = Join-Path $DesktopPath "AI Pipeline TUI.lnk"

# Batch launcher path
$LauncherPath = Join-Path $ProjectRoot "scripts\launch_tui.bat"

# Create WScript Shell object
$WshShell = New-Object -ComObject WScript.Shell

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $LauncherPath
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = "AI Pipeline TUI - Real-time Monitoring Dashboard"
$Shortcut.WindowStyle = 1  # Normal window

# Optional: Set icon (if icon file exists)
$IconPath = Join-Path $ProjectRoot "gui\icon.ico"
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = "$IconPath,0"
}

# Save shortcut
$Shortcut.Save()

Write-Host "✓ Desktop shortcut created:" -ForegroundColor Green
Write-Host "  $ShortcutPath" -ForegroundColor White
Write-Host ""

Write-Host "Done! You can now launch the TUI from your desktop." -ForegroundColor Cyan
Write-Host ""
Write-Host "Shortcut Details:" -ForegroundColor Yellow
Write-Host "  Target:  $LauncherPath" -ForegroundColor Gray
Write-Host "  WorkDir: $ProjectRoot" -ForegroundColor Gray
Write-Host ""

# Test launcher exists
if (-not (Test-Path $LauncherPath)) {
    Write-Host "WARNING: Launcher script not found!" -ForegroundColor Red
    Write-Host "  Expected: $LauncherPath" -ForegroundColor Gray
    Write-Host "  The shortcut may not work until you create this file." -ForegroundColor Gray
}
