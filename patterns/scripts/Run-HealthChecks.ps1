# Pattern Automation - Daily Health Checks
# DOC_ID: DOC-PAT-SCRIPTS-RUN-HEALTH-CHECKS-005
# Runs all health checks and generates consolidated report

param(
    [switch]$Email,
    [string]$EmailTo = "",
    [switch]$Slack,
    [string]$SlackWebhook = ""
)

$ErrorActionPreference = "Stop"

Write-Host "🏥 Pattern Automation - Daily Health Checks" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Gray
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$PatternsDir = Split-Path -Parent $PSScriptRoot
$ReportsDir = Join-Path $PatternsDir "reports\health"
New-Item -ItemType Directory -Path $ReportsDir -Force | Out-Null

# Health check results
$OverallHealth = @{
    status = "HEALTHY"
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    checks = @()
    critical_failures = 0
    warnings = 0
}

# Check 1: Run infrastructure health check
Write-Host "📋 [1/5] Infrastructure Health Check..." -ForegroundColor Yellow
try {
    $healthCheckScript = Join-Path $PatternsDir "automation\monitoring\health_check.ps1"
    $healthResult = & $healthCheckScript -Json

    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Infrastructure: HEALTHY" -ForegroundColor Green
        $OverallHealth.checks += @{name="Infrastructure"; status="PASS"}
    } else {
        Write-Host "   ❌ Infrastructure: FAILED" -ForegroundColor Red
        $OverallHealth.checks += @{name="Infrastructure"; status="FAIL"}
        $OverallHealth.critical_failures++
        $OverallHealth.status = "UNHEALTHY"
    }
} catch {
    Write-Host "   ❌ Infrastructure check error: $_" -ForegroundColor Red
    $OverallHealth.checks += @{name="Infrastructure"; status="ERROR"; error=$_.Exception.Message}
    $OverallHealth.critical_failures++
    $OverallHealth.status = "UNHEALTHY"
}

# Check 2: Database integrity
Write-Host "`n📋 [2/5] Database Integrity..." -ForegroundColor Yellow
try {
    $dbPath = Join-Path $PatternsDir "metrics\pattern_automation.db"

    if (Test-Path $dbPath) {
        # Check for corruption
        $integrityCheck = sqlite3 $dbPath "PRAGMA integrity_check;" 2>&1

        if ($integrityCheck -eq "ok") {
            Write-Host "   ✅ Database: HEALTHY" -ForegroundColor Green
            $OverallHealth.checks += @{name="Database"; status="PASS"}

            # Get size
            $dbSize = (Get-Item $dbPath).Length / 1MB
            Write-Host "   📊 Size: $([math]::Round($dbSize, 2)) MB" -ForegroundColor Gray
        } else {
            Write-Host "   ❌ Database: CORRUPTED" -ForegroundColor Red
            $OverallHealth.checks += @{name="Database"; status="FAIL"; error="Integrity check failed"}
            $OverallHealth.critical_failures++
            $OverallHealth.status = "UNHEALTHY"
        }
    } else {
        Write-Host "   ⚠️  Database: NOT FOUND" -ForegroundColor Yellow
        $OverallHealth.checks += @{name="Database"; status="WARN"; error="Database file missing"}
        $OverallHealth.warnings++
    }
} catch {
    Write-Host "   ❌ Database check error: $_" -ForegroundColor Red
    $OverallHealth.checks += @{name="Database"; status="ERROR"; error=$_.Exception.Message}
    $OverallHealth.warnings++
}

# Check 3: Python dependencies
Write-Host "`n📋 [3/5] Python Dependencies..." -ForegroundColor Yellow
try {
    $pythonCheck = python -c "import yaml, sqlite3; print('OK')" 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Python: HEALTHY" -ForegroundColor Green
        $OverallHealth.checks += @{name="Python"; status="PASS"}
    } else {
        Write-Host "   ❌ Python: MISSING DEPENDENCIES" -ForegroundColor Red
        $OverallHealth.checks += @{name="Python"; status="FAIL"; error="Missing required packages"}
        $OverallHealth.warnings++
    }
} catch {
    Write-Host "   ❌ Python check error: $_" -ForegroundColor Red
    $OverallHealth.checks += @{name="Python"; status="ERROR"; error=$_.Exception.Message}
    $OverallHealth.warnings++
}

# Check 4: Disk space
Write-Host "`n📋 [4/5] Disk Space..." -ForegroundColor Yellow
try {
    $drive = (Get-Item $PatternsDir).PSDrive
    $freeSpace = (Get-PSDrive $drive.Name).Free / 1GB
    $usedSpace = (Get-PSDrive $drive.Name).Used / 1GB
    $totalSpace = $freeSpace + $usedSpace
    $percentFree = ($freeSpace / $totalSpace) * 100

    Write-Host "   📊 Free: $([math]::Round($freeSpace, 1)) GB ($([math]::Round($percentFree, 1))%)" -ForegroundColor Gray

    if ($percentFree -lt 10) {
        Write-Host "   ❌ Disk Space: CRITICAL" -ForegroundColor Red
        $OverallHealth.checks += @{name="DiskSpace"; status="FAIL"; free_pct=$percentFree}
        $OverallHealth.critical_failures++
        $OverallHealth.status = "UNHEALTHY"
    } elseif ($percentFree -lt 20) {
        Write-Host "   ⚠️  Disk Space: LOW" -ForegroundColor Yellow
        $OverallHealth.checks += @{name="DiskSpace"; status="WARN"; free_pct=$percentFree}
        $OverallHealth.warnings++
    } else {
        Write-Host "   ✅ Disk Space: HEALTHY" -ForegroundColor Green
        $OverallHealth.checks += @{name="DiskSpace"; status="PASS"; free_pct=$percentFree}
    }
} catch {
    Write-Host "   ⚠️  Disk space check error: $_" -ForegroundColor Yellow
    $OverallHealth.checks += @{name="DiskSpace"; status="ERROR"; error=$_.Exception.Message}
}

# Check 5: Scheduled task status
Write-Host "`n📋 [5/5] Scheduled Task..." -ForegroundColor Yellow
try {
    $task = Get-ScheduledTask -TaskName "UET_PatternAutomation_ZeroTouch" -ErrorAction SilentlyContinue

    if ($task) {
        $taskInfo = Get-ScheduledTaskInfo -TaskName $task.TaskName

        if ($task.State -eq "Ready") {
            Write-Host "   ✅ Scheduled Task: HEALTHY" -ForegroundColor Green
            Write-Host "   📅 Next Run: $($taskInfo.NextRunTime)" -ForegroundColor Gray
            $OverallHealth.checks += @{name="ScheduledTask"; status="PASS"}
        } else {
            Write-Host "   ⚠️  Scheduled Task: $($task.State)" -ForegroundColor Yellow
            $OverallHealth.checks += @{name="ScheduledTask"; status="WARN"; state=$task.State}
            $OverallHealth.warnings++
        }

        # Check last run result
        if ($taskInfo.LastTaskResult -ne 0) {
            Write-Host "   ⚠️  Last run failed: $($taskInfo.LastTaskResult)" -ForegroundColor Yellow
            $OverallHealth.warnings++
        }
    } else {
        Write-Host "   ⚠️  Scheduled Task: NOT CONFIGURED" -ForegroundColor Yellow
        $OverallHealth.checks += @{name="ScheduledTask"; status="WARN"; error="Not scheduled"}
        $OverallHealth.warnings++
    }
} catch {
    Write-Host "   ⚠️  Scheduled task check error: $_" -ForegroundColor Yellow
    $OverallHealth.checks += @{name="ScheduledTask"; status="ERROR"; error=$_.Exception.Message}
}

# Generate summary
Write-Host "`n" + "="*80 -ForegroundColor Gray
Write-Host "📊 SUMMARY" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Gray

$statusIcon = switch ($OverallHealth.status) {
    "HEALTHY" { "✅" }
    "UNHEALTHY" { "❌" }
    default { "⚠️ " }
}

$statusColor = switch ($OverallHealth.status) {
    "HEALTHY" { "Green" }
    "UNHEALTHY" { "Red" }
    default { "Yellow" }
}

Write-Host "`nOverall Status: $statusIcon " -NoNewline
Write-Host $OverallHealth.status -ForegroundColor $statusColor
Write-Host "Critical Failures: $($OverallHealth.critical_failures)"
Write-Host "Warnings: $($OverallHealth.warnings)"
Write-Host "Total Checks: $($OverallHealth.checks.Count)"

# Save report
$reportFile = Join-Path $ReportsDir "health_check_$(Get-Date -Format 'yyyyMMdd').json"
$OverallHealth | ConvertTo-Json -Depth 5 | Out-File $reportFile -Encoding UTF8

Write-Host "`n📄 Report saved: $reportFile" -ForegroundColor Gray

# Notifications (if requested)
if ($Email -and $EmailTo) {
    Write-Host "`n📧 Sending email notification..." -ForegroundColor Yellow
    # TODO: Implement email notification
    Write-Host "   ⚠️  Email notification not yet implemented" -ForegroundColor Yellow
}

if ($Slack -and $SlackWebhook) {
    Write-Host "`n💬 Sending Slack notification..." -ForegroundColor Yellow

    $slackMessage = @{
        text = "Pattern Automation Health Check"
        attachments = @(
            @{
                color = if ($OverallHealth.status -eq "HEALTHY") { "good" } elseif ($OverallHealth.status -eq "UNHEALTHY") { "danger" } else { "warning" }
                fields = @(
                    @{title="Status"; value=$OverallHealth.status; short=$true}
                    @{title="Critical"; value=$OverallHealth.critical_failures; short=$true}
                    @{title="Warnings"; value=$OverallHealth.warnings; short=$true}
                    @{title="Timestamp"; value=$OverallHealth.timestamp; short=$false}
                )
            }
        )
    } | ConvertTo-Json -Depth 5

    try {
        Invoke-RestMethod -Uri $SlackWebhook -Method Post -Body $slackMessage -ContentType "application/json"
        Write-Host "   ✅ Slack notification sent" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Failed to send Slack notification: $_" -ForegroundColor Red
    }
}

Write-Host "`n✨ Health check complete" -ForegroundColor Green

# Exit with appropriate code
exit $(if ($OverallHealth.critical_failures -eq 0) { 0 } else { 1 })
