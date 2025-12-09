# DOC_LINK: DOC-SCRIPT-WATCH-LOGS-PS1-001
# Real-time AI Tools Log Monitor
# Watches all AI tool logs and displays updates in real-time

[CmdletBinding()]
param(
    [string[]]$Tools = @("claude", "codex", "copilot", "aider"),
    [int]$RefreshSeconds = 2
)

$logPaths = @{
    claude = "$HOME\.claude\debug\latest"
    codex = "$HOME\.codex\log\codex-tui.log"
    copilot_latest = (Get-ChildItem "$HOME\.copilot\logs\session-*.log" -ErrorAction SilentlyContinue |
                     Sort-Object LastWriteTime -Descending |
                     Select-Object -First 1).FullName
    aider = "$HOME\Documents\aider-config\history\.aider.chat.history.md"
}

$lastSizes = @{}
foreach ($tool in $Tools) {
    if ($logPaths[$tool] -and (Test-Path $logPaths[$tool])) {
        $lastSizes[$tool] = (Get-Item $logPaths[$tool]).Length
    }
}

Write-Host "AI Tools Real-Time Log Monitor" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "Monitoring: $($Tools -join ', ')"
Write-Host "Refresh Rate: $RefreshSeconds seconds"
Write-Host "Press Ctrl+C to stop"
Write-Host ""

while ($true) {
    $hasUpdates = $false

    foreach ($tool in $Tools) {
        $path = $logPaths[$tool]

        if (-not $path -or -not (Test-Path $path)) {
            continue
        }

        $currentSize = (Get-Item $path).Length

        if ($lastSizes[$tool] -ne $currentSize) {
            $hasUpdates = $true
            $newContent = Get-Content $path -Tail 10

            Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $tool - New Activity" -ForegroundColor Green
            $newContent | Select-Object -Last 3 | ForEach-Object {
                Write-Host "  $_" -ForegroundColor Gray
            }
            Write-Host ""

            $lastSizes[$tool] = $currentSize
        }
    }

    if (-not $hasUpdates) {
        Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] No updates..." -ForegroundColor DarkGray
    }

    Start-Sleep -Seconds $RefreshSeconds
}
