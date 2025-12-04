# DOC_LINK: DOC-SCRIPT-SCHEDULE-ZEROTOUCHAUTOMATION-115
# Zero-Touch Pattern Automation - Windows Task Scheduler Setup
# Runs nightly to mine AI logs and auto-generate patterns

param(
    [string]$Action = "install",  # install, uninstall, run-now, status
    [string]$Time = "02:00",      # Default: 2 AM daily
    [string]$UserHome = $env:USERPROFILE
)

$ErrorActionPreference = "Stop"

# Paths
$PatternsDir = "$PSScriptRoot\.."
$PythonScript = Join-Path $PatternsDir "automation\runtime\zero_touch_workflow.py"
$TaskName = "UET_PatternAutomation_ZeroTouch"
$TaskDescription = "Zero-Touch Pattern Automation: Mines AI logs (Claude/Copilot/Codex) and auto-generates patterns"

function Install-ScheduledTask {
    Write-Host "Installing Zero-Touch Automation Scheduled Task..." -ForegroundColor Cyan

    # Check if Python is available
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
        Write-Host "Install Python or ensure it's in PATH" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "  ✓ Python found: $($pythonCmd.Source)"

    # Check if script exists
    if (-not (Test-Path $PythonScript)) {
        Write-Host "ERROR: Script not found: $PythonScript" -ForegroundColor Red
        exit 1
    }

    Write-Host "  ✓ Script found: $PythonScript"

    # Create scheduled task action
    $action = New-ScheduledTaskAction `
        -Execute "python.exe" `
        -Argument "`"$PythonScript`"" `
        -WorkingDirectory $PatternsDir

    # Create trigger (daily at specified time)
    $trigger = New-ScheduledTaskTrigger `
        -Daily `
        -At $Time

    # Create settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable:$false `
        -ExecutionTimeLimit (New-TimeSpan -Hours 2)

    # Create principal (run as current user)
    $principal = New-ScheduledTaskPrincipal `
        -UserId "$env:USERDOMAIN\$env:USERNAME" `
        -LogonType Interactive `
        -RunLevel Limited

    # Register task
    try {
        # Unregister if already exists
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

        Register-ScheduledTask `
            -TaskName $TaskName `
            -Description $TaskDescription `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Principal $principal `
            -Force | Out-Null

        Write-Host "`n✅ Scheduled Task Installed Successfully!" -ForegroundColor Green
        Write-Host "   Name: $TaskName" -ForegroundColor Gray
        Write-Host "   Schedule: Daily at $Time" -ForegroundColor Gray
        Write-Host "   Script: $PythonScript" -ForegroundColor Gray

        # Show next run time
        $task = Get-ScheduledTask -TaskName $TaskName
        $info = Get-ScheduledTaskInfo -TaskName $TaskName

        Write-Host "`n📅 Next Run: $($info.NextRunTime)" -ForegroundColor Cyan
        Write-Host "   Status: $($task.State)" -ForegroundColor Cyan

        Write-Host "`n💡 To run manually: .\Schedule-ZeroTouchAutomation.ps1 -Action run-now" -ForegroundColor Yellow

    } catch {
        Write-Host "`n❌ Failed to install scheduled task" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Uninstall-ScheduledTask {
    Write-Host "Uninstalling Zero-Touch Automation Scheduled Task..." -ForegroundColor Cyan

    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ Scheduled task removed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Task not found or already removed" -ForegroundColor Yellow
    }
}

function Run-TaskNow {
    Write-Host "Running Zero-Touch Automation immediately..." -ForegroundColor Cyan

    # Check if task exists
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

    if ($task) {
        Write-Host "  ✓ Starting via scheduled task..." -ForegroundColor Gray
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "  ✓ Task started" -ForegroundColor Green
        Write-Host "`n💡 Check logs at: $PatternsDir\reports\zero_touch\" -ForegroundColor Yellow
    } else {
        Write-Host "  ⚠️  Scheduled task not installed, running directly..." -ForegroundColor Yellow

        Push-Location $PatternsDir
        try {
            python $PythonScript
        } finally {
            Pop-Location
        }
    }
}

function Show-TaskStatus {
    Write-Host "Zero-Touch Automation Status" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Gray

    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

    if ($task) {
        $info = Get-ScheduledTaskInfo -TaskName $TaskName

        Write-Host "Status:         " -NoNewline
        Write-Host $task.State -ForegroundColor $(if ($task.State -eq 'Ready') { 'Green' } else { 'Yellow' })

        Write-Host "Next Run:       $($info.NextRunTime)"
        Write-Host "Last Run:       $($info.LastRunTime)"
        Write-Host "Last Result:    $($info.LastTaskResult) " -NoNewline
        Write-Host $(if ($info.LastTaskResult -eq 0) { '(Success)' } else { '(Failed)' }) -ForegroundColor $(if ($info.LastTaskResult -eq 0) { 'Green' } else { 'Red' })
        Write-Host "Trigger:        Daily at $Time"

        # Check recent reports
        $reportsDir = Join-Path $PatternsDir "reports\zero_touch"
        if (Test-Path $reportsDir) {
            $latestReport = Get-ChildItem $reportsDir -Filter "*.md" -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1

            if ($latestReport) {
                Write-Host "`nLatest Report:  $($latestReport.Name)"
                Write-Host "Report Time:    $($latestReport.LastWriteTime)"
            }
        }

    } else {
        Write-Host "Status:         " -NoNewline
        Write-Host "NOT INSTALLED" -ForegroundColor Red
        Write-Host "`n💡 Install with: .\Schedule-ZeroTouchAutomation.ps1 -Action install" -ForegroundColor Yellow
    }

    Write-Host "`nLog Directories:" -ForegroundColor Cyan
    @(
        @{Name="Claude"; Path="$UserHome\.claude\file-history"},
        @{Name="Copilot"; Path="$UserHome\.copilot\session-state"},
        @{Name="Codex"; Path="$UserHome\.codex\log"}
    ) | ForEach-Object {
        $exists = Test-Path $_.Path
        $icon = if ($exists) { "✓" } else { "✗" }
        $color = if ($exists) { "Green" } else { "Red" }

        Write-Host "  $icon $($_.Name): " -NoNewline -ForegroundColor $color
        Write-Host $_.Path -ForegroundColor Gray

        if ($exists) {
            $count = (Get-ChildItem $_.Path -File -ErrorAction SilentlyContinue | Measure-Object).Count
            Write-Host "    Files: $count" -ForegroundColor Gray
        }
    }
}

# Main execution
switch ($Action.ToLower()) {
    "install" {
        Install-ScheduledTask
    }
    "uninstall" {
        Uninstall-ScheduledTask
    }
    "run-now" {
        Run-TaskNow
    }
    "status" {
        Show-TaskStatus
    }
    default {
        Write-Host "Zero-Touch Pattern Automation - Task Scheduler" -ForegroundColor Cyan
        Write-Host "="*60 -ForegroundColor Gray
        Write-Host "`nUsage:"
        Write-Host "  .\Schedule-ZeroTouchAutomation.ps1 -Action install    # Install nightly task (default 2 AM)"
        Write-Host "  .\Schedule-ZeroTouchAutomation.ps1 -Action status     # Show task status"
        Write-Host "  .\Schedule-ZeroTouchAutomation.ps1 -Action run-now    # Run immediately"
        Write-Host "  .\Schedule-ZeroTouchAutomation.ps1 -Action uninstall  # Remove task"
        Write-Host "`nOptions:"
        Write-Host "  -Time '02:00'        # Set daily run time (default: 2 AM)"
        Write-Host "  -UserHome 'C:\...'   # Set user home directory"
        exit 1
    }
}
