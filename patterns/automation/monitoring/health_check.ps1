# DOC_LINK: DOC-PAT-HEALTH-CHECK-342
# Pattern Automation - Health Check Script
# DOC_ID: DOC-PAT-MONITORING-HEALTH-CHECK-001
# Validates pattern automation system health and generates status report

param(
    [switch]$Detailed,
    [switch]$Json,
    [string]$OutputPath = ".\reports\health_check_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
)

$ErrorActionPreference = "Continue"

# Paths
$PatternsDir = Split-Path -Parent $PSScriptRoot | Split-Path -Parent
$DbPath = Join-Path $PatternsDir "metrics\pattern_automation.db"
$ConfigPath = Join-Path $PatternsDir "automation\config\detection_config.yaml"

# Health check results
$Health = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    overall_status = "UNKNOWN"
    checks = @()
    metrics = @{}
    recommendations = @()
}

function Test-Component {
    param($Name, $Check, $Critical = $true)

    try {
        $result = & $Check
        $status = if ($result) { "PASS" } else { "FAIL" }
        $Health.checks += @{
            name = $Name
            status = $status
            critical = $Critical
            message = if ($result) { "OK" } else { "Check failed" }
        }
        return $result
    } catch {
        $Health.checks += @{
            name = $Name
            status = "ERROR"
            critical = $Critical
            message = $_.Exception.Message
        }
        return $false
    }
}

Write-Host "🔍 Pattern Automation Health Check" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Gray
Write-Host "Timestamp: $($Health.timestamp)" -ForegroundColor Gray
Write-Host ""

# Check 1: Database exists and accessible
Write-Host "[1/10] Database Connectivity..." -NoNewline
$dbOk = Test-Component "Database" {
    Test-Path $DbPath
}
Write-Host " $(if($dbOk){'✅'}else{'❌'})"

# Check 2: Database tables
if ($dbOk) {
    Write-Host "[2/10] Database Schema..." -NoNewline
    $tablesOk = Test-Component "Tables" {
        $tables = sqlite3 $DbPath ".tables" 2>$null
        ($tables -match "execution_logs") -and
        ($tables -match "pattern_candidates") -and
        ($tables -match "anti_patterns")
    }
    Write-Host " $(if($tablesOk){'✅'}else{'❌'})"

    # Get metrics
    if ($tablesOk) {
        $execCount = sqlite3 $DbPath "SELECT COUNT(*) FROM execution_logs;" 2>$null
        $candCount = sqlite3 $DbPath "SELECT COUNT(*) FROM pattern_candidates;" 2>$null
        $antiCount = sqlite3 $DbPath "SELECT COUNT(*) FROM anti_patterns;" 2>$null

        $Health.metrics.executions_logged = [int]$execCount
        $Health.metrics.pattern_candidates = [int]$candCount
        $Health.metrics.anti_patterns = [int]$antiCount
    }
} else {
    $Health.checks += @{name="Tables"; status="SKIP"; critical=$true; message="Database not found"}
}

# Check 3: Configuration
Write-Host "[3/10] Configuration..." -NoNewline
$configOk = Test-Component "Config" {
    Test-Path $ConfigPath
}
Write-Host " $(if($configOk){'✅'}else{'❌'})"

# Check 4: Detectors
Write-Host "[4/10] Detector Modules..." -NoNewline
$detectorsOk = Test-Component "Detectors" {
    $detectorPath = Join-Path $PatternsDir "automation\detectors"
    $required = @("execution_detector.py", "anti_pattern_detector.py", "file_pattern_miner.py")
    $existing = Get-ChildItem $detectorPath -Filter "*.py" | Select-Object -ExpandProperty Name
    ($required | ForEach-Object { $existing -contains $_ }) -notcontains $false
}
Write-Host " $(if($detectorsOk){'✅'}else{'❌'})"

# Check 5: Integration hooks
Write-Host "[5/10] Integration Hooks..." -NoNewline
$hooksOk = Test-Component "Hooks" {
    Test-Path (Join-Path $PatternsDir "automation\integration\orchestrator_hooks.py")
}
Write-Host " $(if($hooksOk){'✅'}else{'❌'})"

# Check 6: Executors
Write-Host "[6/10] Pattern Executors..." -NoNewline
$executorsOk = Test-Component "Executors" {
    $executorPath = Join-Path $PatternsDir "executors"
    $executors = Get-ChildItem $executorPath -Filter "*_executor.ps1"
    $executors.Count -ge 7  # Core patterns
}
$Health.metrics.executor_count = (Get-ChildItem (Join-Path $PatternsDir "executors") -Filter "*_executor.ps1").Count
Write-Host " $(if($executorsOk){'✅'}else{'❌'}) ($($Health.metrics.executor_count) executors)"

# Check 7: Recent activity
Write-Host "[7/10] Recent Activity..." -NoNewline
$activityOk = Test-Component "Activity" {
    if (-not $dbOk) { return $false }
    $recent = sqlite3 $DbPath "SELECT COUNT(*) FROM execution_logs WHERE timestamp > datetime('now', '-7 days');" 2>$null
    [int]$recent -gt 0
} -Critical $false
$Health.metrics.recent_executions = if ($dbOk) { [int](sqlite3 $DbPath "SELECT COUNT(*) FROM execution_logs WHERE timestamp > datetime('now', '-7 days');" 2>$null) } else { 0 }
Write-Host " $(if($activityOk){'✅'}else{'⚠️ '}) ($($Health.metrics.recent_executions) in last 7 days)"

# Check 8: Pattern registry
Write-Host "[8/10] Pattern Registry..." -NoNewline
$registryOk = Test-Component "Registry" {
    Test-Path (Join-Path $PatternsDir "registry\PATTERN_INDEX.yaml")
}
Write-Host " $(if($registryOk){'✅'}else{'❌'})"

# Check 9: Auto-generated patterns
Write-Host "[9/10] Auto-Generated Patterns..." -NoNewline
$autoGenOk = Test-Component "AutoGen" {
    $drafts = Join-Path $PatternsDir "drafts"
    if (Test-Path $drafts) {
        (Get-ChildItem $drafts -Filter "AUTO-*.yaml" -ErrorAction SilentlyContinue).Count -gt 0
    } else {
        $false
    }
} -Critical $false
$Health.metrics.auto_generated = if (Test-Path (Join-Path $PatternsDir "drafts")) {
    (Get-ChildItem (Join-Path $PatternsDir "drafts") -Filter "AUTO-*.yaml" -ErrorAction SilentlyContinue).Count
} else { 0 }
Write-Host " $(if($autoGenOk){'✅'}else{'⚠️ '}) ($($Health.metrics.auto_generated) patterns)"

# Check 10: Scheduled task
Write-Host "[10/10] Scheduled Automation..." -NoNewline
$scheduleOk = Test-Component "Schedule" {
    $task = Get-ScheduledTask -TaskName "UET_PatternAutomation_ZeroTouch" -ErrorAction SilentlyContinue
    $null -ne $task
} -Critical $false
Write-Host " $(if($scheduleOk){'✅'}else{'⚠️ '})"

# Calculate overall status
Write-Host ""
Write-Host "="*80 -ForegroundColor Gray

$criticalChecks = $Health.checks | Where-Object { $_.critical -eq $true }
$failedCritical = $criticalChecks | Where-Object { $_.status -ne "PASS" }
$warnings = $Health.checks | Where-Object { $_.critical -eq $false -and $_.status -ne "PASS" }

if ($failedCritical.Count -eq 0) {
    if ($warnings.Count -eq 0) {
        $Health.overall_status = "HEALTHY"
        $statusColor = "Green"
        $statusIcon = "✅"
    } else {
        $Health.overall_status = "HEALTHY_WITH_WARNINGS"
        $statusColor = "Yellow"
        $statusIcon = "⚠️ "
    }
} else {
    $Health.overall_status = "UNHEALTHY"
    $statusColor = "Red"
    $statusIcon = "❌"
}

Write-Host "Overall Status: $statusIcon $($Health.overall_status)" -ForegroundColor $statusColor
Write-Host ""

# Metrics summary
Write-Host "📊 Metrics:" -ForegroundColor Cyan
$Health.metrics.Keys | Sort-Object | ForEach-Object {
    Write-Host "   $($_): $($Health.metrics[$_])"
}
Write-Host ""

# Recommendations
if ($Health.metrics.recent_executions -eq 0) {
    $Health.recommendations += "No recent activity detected - verify orchestrator integration"
}
if ($Health.metrics.pattern_candidates -gt 10) {
    $Health.recommendations += "High number of pattern candidates ($($Health.metrics.pattern_candidates)) - review and approve"
}
if ($Health.metrics.auto_generated -eq 0) {
    $Health.recommendations += "No auto-generated patterns - system may need tuning or more executions"
}
if (-not $scheduleOk) {
    $Health.recommendations += "Scheduled task not found - run: .\scripts\Schedule-ZeroTouchAutomation.ps1 -Action install"
}

if ($Health.recommendations.Count -gt 0) {
    Write-Host "💡 Recommendations:" -ForegroundColor Yellow
    $Health.recommendations | ForEach-Object {
        Write-Host "   • $_"
    }
    Write-Host ""
}

# Output formats
if ($Json) {
    $Health | ConvertTo-Json -Depth 5 | Out-File "$OutputPath.json" -Encoding UTF8
    Write-Host "📄 JSON report: $OutputPath.json" -ForegroundColor Gray
}

# Markdown report
$md = @"
# Pattern Automation Health Check

**Generated**: $($Health.timestamp)
**Status**: $($Health.overall_status)

## Summary

| Metric | Value |
|--------|-------|
$(($Health.metrics.Keys | Sort-Object | ForEach-Object { "| $_ | $($Health.metrics[$_]) |" }) -join "`n")

## Checks

| Check | Status | Critical | Message |
|-------|--------|----------|---------|
$(($Health.checks | ForEach-Object { "| $($_.name) | $($_.status) | $(if($_.critical){'Yes'}else{'No'}) | $($_.message) |" }) -join "`n")

## Recommendations

$(if ($Health.recommendations.Count -gt 0) {
    ($Health.recommendations | ForEach-Object { "- $_" }) -join "`n"
} else {
    "_No recommendations - system is healthy_"
})

---
*Generated by health_check.ps1*
"@

$md | Out-File $OutputPath -Encoding UTF8
Write-Host "📄 Report saved: $OutputPath" -ForegroundColor Gray

# Exit code based on health
exit $(if ($failedCritical.Count -eq 0) { 0 } else { 1 })
