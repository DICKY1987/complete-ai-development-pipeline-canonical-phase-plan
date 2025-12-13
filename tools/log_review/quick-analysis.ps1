# Quick Analysis Script - Generate summary from aggregated logs
# Usage: .\quick-analysis.ps1 [LogFile]

param(
    [string]$LogFile
)

# Find latest log file if not specified
if (-not $LogFile) {
    $LogFile = Get-ChildItem ".\aggregated\aggregated-*.jsonl" -ErrorAction SilentlyContinue | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -First 1 -ExpandProperty FullName
}

if (-not $LogFile -or -not (Test-Path $LogFile)) {
    Write-Host "Error: No log file found" -ForegroundColor Red
    exit 1
}

Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              AI TOOLS LOG ANALYSIS SUMMARY                        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Analyzing: $(Split-Path -Leaf $LogFile)" -ForegroundColor Gray
Write-Host ""

# Load and parse logs
$logs = Get-Content $LogFile | ForEach-Object {
    try { $_ | ConvertFrom-Json } catch { $null }
} | Where-Object { $_ -ne $null }

Write-Host "📊 OVERALL STATISTICS" -ForegroundColor Yellow
Write-Host "═══════════════════════" -ForegroundColor Gray
Write-Host "Total Entries: $($logs.Count)"

# Group by tool
$byTool = $logs | Group-Object tool
Write-Host ""
Write-Host "By Tool:" -ForegroundColor White
foreach ($group in $byTool) {
    $percentage = [math]::Round(($group.Count / $logs.Count) * 100, 1)
    Write-Host "  $($group.Name.PadRight(10)) : $($group.Count.ToString().PadLeft(6)) ($percentage%)" -ForegroundColor Gray
}

# Group by type
$byType = $logs | Group-Object type
Write-Host ""
Write-Host "By Type:" -ForegroundColor White
foreach ($group in $byType | Sort-Object Count -Descending) {
    Write-Host "  $($group.Name.PadRight(20)) : $($group.Count.ToString().PadLeft(6))" -ForegroundColor Gray
}

# Time range
$timestamps = $logs | ForEach-Object { 
    try { [datetime]::Parse($_.timestamp) } catch { $null } 
} | Where-Object { $_ -ne $null } | Sort-Object

if ($timestamps.Count -gt 0) {
    Write-Host ""
    Write-Host "⏱️  TIME RANGE" -ForegroundColor Yellow
    Write-Host "═══════════════════════" -ForegroundColor Gray
    Write-Host "First Entry: $($timestamps[0].ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Host "Last Entry:  $($timestamps[-1].ToString('yyyy-MM-dd HH:mm:ss'))"
    $duration = $timestamps[-1] - $timestamps[0]
    Write-Host "Duration:    $($duration.Days) days, $($duration.Hours) hours"
}

# Sessions
$sessions = $logs | Where-Object { $_.sessionId } | 
    Select-Object -ExpandProperty sessionId -Unique

if ($sessions.Count -gt 0) {
    Write-Host ""
    Write-Host "👥 SESSIONS" -ForegroundColor Yellow
    Write-Host "═══════════════════════" -ForegroundColor Gray
    Write-Host "Unique Sessions: $($sessions.Count)"
    
    # Session activity
    $sessionStats = $logs | Where-Object { $_.sessionId } | 
        Group-Object sessionId | 
        ForEach-Object {
            @{
                sessionId = $_.Name
                count = $_.Count
                tool = ($_.Group | Select-Object -First 1).tool
            }
        } | Sort-Object count -Descending
    
    Write-Host ""
    Write-Host "Top 5 Most Active Sessions:" -ForegroundColor White
    $sessionStats | Select-Object -First 5 | ForEach-Object {
        $shortId = $_.sessionId.Substring(0, [Math]::Min(16, $_.sessionId.Length))
        Write-Host "  $shortId... ($($_.tool)): $($_.count) entries" -ForegroundColor Gray
    }
}

# Most recent activity
Write-Host ""
Write-Host "🔥 RECENT ACTIVITY" -ForegroundColor Yellow
Write-Host "═══════════════════════" -ForegroundColor Gray

$recentLogs = $logs | 
    ForEach-Object {
        try {
            $_ | Add-Member -NotePropertyName parsedTime -NotePropertyValue ([datetime]::Parse($_.timestamp)) -PassThru
        } catch {
            $null
        }
    } |
    Where-Object { $_ -ne $null } |
    Sort-Object parsedTime -Descending |
    Select-Object -First 5

Write-Host "Last 5 Events:" -ForegroundColor White
foreach ($log in $recentLogs) {
    $time = $log.parsedTime.ToString("MM/dd HH:mm")
    $displayText = ""
    if ($log.data.display) {
        $displayText = $log.data.display.Substring(0, [Math]::Min(40, $log.data.display.Length))
    } elseif ($log.data.message) {
        $displayText = $log.data.message.Substring(0, [Math]::Min(40, $log.data.message.Length))
    }
    Write-Host "  [$time] $($log.tool)/$($log.type): $displayText..." -ForegroundColor Gray
}

# File info
Write-Host ""
Write-Host "📁 FILE INFORMATION" -ForegroundColor Yellow
Write-Host "═══════════════════════" -ForegroundColor Gray
$fileInfo = Get-Item $LogFile
Write-Host "File: $($fileInfo.Name)"
Write-Host "Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB"
Write-Host "Created: $($fileInfo.CreationTime.ToString('yyyy-MM-dd HH:mm:ss'))"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Analysis complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════`n" -ForegroundColor Gray
