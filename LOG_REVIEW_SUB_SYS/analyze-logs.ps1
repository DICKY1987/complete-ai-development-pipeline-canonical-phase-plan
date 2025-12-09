# DOC_LINK: DOC-SCRIPT-ANALYZE-LOGS-PS1-001
# AI Tools Log Analyzer
# Analyzes aggregated logs and generates insights

[CmdletBinding()]
param(
    [string]$LogFile = (Get-ChildItem "$HOME\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\ai-logs-analyzer\aggregated\aggregated-*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName,
    [ValidateSet("summary", "code-changes", "patterns", "full-report", "usage-metrics")]
    [string]$Type = "summary",
    [string]$OutputDir = "$HOME\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\ai-logs-analyzer\analysis"
)

$ErrorActionPreference = "Stop"

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

if (-not $LogFile -or -not (Test-Path $LogFile)) {
    Write-Host "Error: No log file found. Run aggregate-logs.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "AI Tools Log Analyzer" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "Analyzing: $LogFile"
Write-Host "Analysis Type: $Type"
Write-Host ""

# Load logs
Write-Host "Loading logs..." -ForegroundColor Yellow
$logs = Get-Content $LogFile | ForEach-Object {
    try {
        $_ | ConvertFrom-Json
    } catch {
        $null
    }
} | Where-Object { $_ -ne $null }

Write-Host "Loaded $($logs.Count) log entries" -ForegroundColor Gray
Write-Host ""

# Analysis functions
function Get-UsageMetrics {
    param($logs)

    $metrics = @{}
    $tools = $logs | Select-Object -ExpandProperty tool -Unique

    foreach ($tool in $tools) {
        $toolLogs = $logs | Where-Object { $_.tool -eq $tool }
        $sessions = $toolLogs | Select-Object -ExpandProperty sessionId -Unique | Where-Object { $_ }

        $metrics[$tool] = @{
            totalEntries = $toolLogs.Count
            sessions = $sessions.Count
            types = ($toolLogs | Group-Object type | ForEach-Object { @{ $_.Name = $_.Count } })
            firstEntry = ($toolLogs | Select-Object -First 1).timestamp
            lastEntry = ($toolLogs | Select-Object -Last 1).timestamp
        }
    }

    return $metrics
}

function Get-SessionSummary {
    param($logs)

    $sessions = $logs | Where-Object { $_.sessionId } | Group-Object sessionId

    $summary = $sessions | ForEach-Object {
        $sessionLogs = $_.Group
        @{
            sessionId = $_.Name
            tool = ($sessionLogs | Select-Object -First 1).tool
            entryCount = $sessionLogs.Count
            startTime = ($sessionLogs | Select-Object -First 1).timestamp
            endTime = ($sessionLogs | Select-Object -Last 1).timestamp
            duration = if ($sessionLogs.Count -gt 1) {
                ([datetime]($sessionLogs | Select-Object -Last 1).timestamp) - ([datetime]($sessionLogs | Select-Object -First 1).timestamp)
            } else {
                [timespan]::Zero
            }
        }
    } | Sort-Object startTime -Descending

    return $summary
}

function Get-ActivityPatterns {
    param($logs)

    $patterns = @{
        hourly = @{}
        daily = @{}
        toolComparison = @{}
    }

    foreach ($log in $logs) {
        $timestamp = [datetime]$log.timestamp
        $hour = $timestamp.Hour.ToString()
        $day = $timestamp.DayOfWeek.ToString()

        if (-not $patterns.hourly[$hour]) { $patterns.hourly[$hour] = 0 }
        if (-not $patterns.daily[$day]) { $patterns.daily[$day] = 0 }
        if (-not $patterns.toolComparison[$log.tool]) { $patterns.toolComparison[$log.tool] = 0 }

        $patterns.hourly[$hour]++
        $patterns.daily[$day]++
        $patterns.toolComparison[$log.tool]++
    }

    return $patterns
}

function Get-CodeChangesAnalysis {
    param($logs)

    $codeChanges = @{
        conversations = 0
        totalEntries = 0
        toolBreakdown = @{}
    }

    $convLogs = $logs | Where-Object { $_.type -match "conversation|chat|session" }
    $codeChanges.conversations = $convLogs.Count
    $codeChanges.totalEntries = $logs.Count

    foreach ($tool in ($logs | Select-Object -ExpandProperty tool -Unique)) {
        $toolConvs = $convLogs | Where-Object { $_.tool -eq $tool }
        $codeChanges.toolBreakdown[$tool] = $toolConvs.Count
    }

    return $codeChanges
}

# Perform analysis based on type
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = "$OutputDir\$Type-report-$timestamp.json"

switch ($Type) {
    "summary" {
        Write-Host "Generating Summary Report..." -ForegroundColor Cyan

        $report = @{
            timestamp = Get-Date -Format "o"
            logFile = $LogFile
            totalEntries = $logs.Count
            usageMetrics = Get-UsageMetrics $logs
            sessions = Get-SessionSummary $logs
            patterns = Get-ActivityPatterns $logs
        }

        $report | ConvertTo-Json -Depth 10 | Out-File $reportFile -Encoding utf8

        # Display summary
        Write-Host ""
        Write-Host "=== Usage Metrics ===" -ForegroundColor Green
        foreach ($tool in $report.usageMetrics.Keys) {
            $metrics = $report.usageMetrics[$tool]
            Write-Host "  $tool`: $($metrics.totalEntries) entries, $($metrics.sessions) sessions"
        }

        Write-Host ""
        Write-Host "=== Activity Patterns ===" -ForegroundColor Green
        Write-Host "  Peak Hours:"
        $report.patterns.hourly.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 5 | ForEach-Object {
            Write-Host "    $($_.Key):00 - $($_.Value) entries"
        }

        Write-Host ""
        Write-Host "  Most Active Days:"
        $report.patterns.daily.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
            Write-Host "    $($_.Key) - $($_.Value) entries"
        }

        Write-Host ""
        Write-Host "=== Recent Sessions ===" -ForegroundColor Green
        $report.sessions | Select-Object -First 10 | ForEach-Object {
            $durationStr = if ($_.duration.TotalMinutes -gt 0) {
                "$([math]::Round($_.duration.TotalMinutes, 1)) min"
            } else {
                "< 1 min"
            }
            Write-Host "  [$($_.tool)] $($_.sessionId.Substring(0, 8))... - $durationStr - $($_.entryCount) entries"
        }
    }

    "usage-metrics" {
        Write-Host "Generating Usage Metrics Report..." -ForegroundColor Cyan

        $report = Get-UsageMetrics $logs
        $report | ConvertTo-Json -Depth 10 | Out-File $reportFile -Encoding utf8

        foreach ($tool in $report.Keys) {
            Write-Host ""
            Write-Host "=== $tool ===" -ForegroundColor Green
            Write-Host "  Total Entries: $($report[$tool].totalEntries)"
            Write-Host "  Sessions: $($report[$tool].sessions)"
            Write-Host "  First Entry: $($report[$tool].firstEntry)"
            Write-Host "  Last Entry: $($report[$tool].lastEntry)"
            Write-Host "  Types:"
            $report[$tool].types | ForEach-Object {
                $_.GetEnumerator() | ForEach-Object {
                    Write-Host "    $($_.Key): $($_.Value)"
                }
            }
        }
    }

    "code-changes" {
        Write-Host "Generating Code Changes Report..." -ForegroundColor Cyan

        $report = Get-CodeChangesAnalysis $logs
        $report | ConvertTo-Json -Depth 10 | Out-File $reportFile -Encoding utf8

        Write-Host ""
        Write-Host "=== Code Changes Analysis ===" -ForegroundColor Green
        Write-Host "  Total Conversations: $($report.conversations)"
        Write-Host "  Total Log Entries: $($report.totalEntries)"
        Write-Host ""
        Write-Host "  Breakdown by Tool:"
        foreach ($tool in $report.toolBreakdown.Keys) {
            Write-Host "    $tool`: $($report.toolBreakdown[$tool]) conversations"
        }
    }

    "patterns" {
        Write-Host "Generating Activity Patterns Report..." -ForegroundColor Cyan

        $report = Get-ActivityPatterns $logs
        $report | ConvertTo-Json -Depth 10 | Out-File $reportFile -Encoding utf8

        Write-Host ""
        Write-Host "=== Hourly Activity ===" -ForegroundColor Green
        $report.hourly.GetEnumerator() | Sort-Object {[int]$_.Key} | ForEach-Object {
            $bar = "=" * [math]::Min(50, [math]::Round($_.Value / ($report.hourly.Values | Measure-Object -Maximum).Maximum * 50))
            Write-Host "  $($_.Key.ToString().PadLeft(2)):00 [$bar] $($_.Value)"
        }

        Write-Host ""
        Write-Host "=== Daily Activity ===" -ForegroundColor Green
        $report.daily.GetEnumerator() | Sort-Object Key | ForEach-Object {
            $bar = "=" * [math]::Min(50, [math]::Round($_.Value / ($report.daily.Values | Measure-Object -Maximum).Maximum * 50))
            Write-Host "  $($_.Key.ToString().PadRight(10)) [$bar] $($_.Value)"
        }

        Write-Host ""
        Write-Host "=== Tool Usage Comparison ===" -ForegroundColor Green
        $total = ($report.toolComparison.Values | Measure-Object -Sum).Sum
        $report.toolComparison.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
            $percent = [math]::Round($_.Value / $total * 100, 1)
            $bar = "=" * [math]::Min(50, [math]::Round($percent))
            Write-Host "  $($_.Key.PadRight(10)) [$bar] $($_.Value) ($percent%)"
        }
    }

    "full-report" {
        Write-Host "Generating Full Report..." -ForegroundColor Cyan

        $report = @{
            timestamp = Get-Date -Format "o"
            logFile = $LogFile
            totalEntries = $logs.Count
            usageMetrics = Get-UsageMetrics $logs
            sessions = Get-SessionSummary $logs
            patterns = Get-ActivityPatterns $logs
            codeChanges = Get-CodeChangesAnalysis $logs
        }

        $report | ConvertTo-Json -Depth 10 | Out-File $reportFile -Encoding utf8

        Write-Host "Full report with all metrics generated."
    }
}

Write-Host ""
Write-Host "Report saved: $reportFile" -ForegroundColor Cyan
Write-Host ""

# Generate markdown report
$mdFile = $reportFile -replace '\.json$', '.md'
Write-Host "Generating markdown report..." -ForegroundColor Yellow

$mdContent = @"
# AI Tools Analysis Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Source
Log File: ``$LogFile``
Analysis Type: **$Type**

## Summary
- Total Log Entries: **$($logs.Count)**
- Tools Analyzed: **$(($logs | Select-Object -ExpandProperty tool -Unique).Count)**
- Date Range: $(([datetime]($logs | Select-Object -First 1).timestamp).ToString("yyyy-MM-dd")) to $(([datetime]($logs | Select-Object -Last 1).timestamp).ToString("yyyy-MM-dd"))

---
*Full JSON report: $reportFile*
"@

$mdContent | Out-File $mdFile -Encoding utf8
Write-Host "Markdown report: $mdFile" -ForegroundColor Gray
