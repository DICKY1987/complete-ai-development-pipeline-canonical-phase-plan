# DOC_LINK: DOC-SCRIPT-SETUP-SCHEDULED-TASK-080
# Setup Scheduled Task for Daily Log Aggregation
# Runs aggregate-logs.ps1 automatically every day at midnight

[CmdletBinding()]
param(
    [string]$TaskName = "AI-Logs-Daily-Aggregation",
    [string]$Time = "00:00",  # Midnight
    [switch]$Remove
)

$scriptPath = "$HOME\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\ai-logs-analyzer\scripts\aggregate-logs.ps1"

if ($Remove) {
    Write-Host "Removing scheduled task '$TaskName'..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Task removed." -ForegroundColor Green
    exit 0
}

# Check if script exists
if (-not (Test-Path $scriptPath)) {
    Write-Host "Error: aggregate-logs.ps1 not found at $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "Setting up scheduled task for daily log aggregation..." -ForegroundColor Cyan
Write-Host ""

# Create action
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -Compress"

# Create trigger (daily at specified time)
$trigger = New-ScheduledTaskTrigger -Daily -At $Time

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Automatically aggregates AI coding assistant logs daily" `
        -Force

    Write-Host "Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName"
    Write-Host "  Schedule: Daily at $Time"
    Write-Host "  Script: $scriptPath"
    Write-Host "  User: $env:USERNAME"
    Write-Host ""
    Write-Host "To view task: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
    Write-Host "To remove task: ./setup-scheduled-task.ps1 -Remove" -ForegroundColor Gray

} catch {
    Write-Host "Error creating scheduled task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}
