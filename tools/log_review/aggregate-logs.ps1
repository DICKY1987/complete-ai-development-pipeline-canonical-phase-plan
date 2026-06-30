# DOC_LINK: DOC-SCRIPT-AGGREGATE-LOGS-PS1-001
# AI Tools Log Aggregator
# Collects logs from all AI coding assistants into a centralized location

[CmdletBinding()]
param(
    [string]$StartDate = (Get-Date).ToString("yyyy-MM-dd"),
    [string]$EndDate = (Get-Date).ToString("yyyy-MM-dd"),
    [string[]]$Tools = @("claude", "codex", "copilot", "gemini", "aider"),
    [string]$OutputDir = "$HOME\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\ai-logs-analyzer\aggregated",
    [switch]$Compress
)

$ErrorActionPreference = "Continue"

# Parse date range
try {
    $startDateTime = [datetime]::Parse($StartDate)
    $endDateTime = [datetime]::Parse($EndDate)
} catch {
    Write-Host "Error: Invalid date format. Use yyyy-MM-dd" -ForegroundColor Red
    exit 1
}

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path "$OutputDir\temp" | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$aggregatedLog = "$OutputDir\aggregated-$timestamp.jsonl"

Write-Host "AI Tools Log Aggregator" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host "Date Range: $StartDate to $EndDate"
Write-Host "Tools: $($Tools -join ', ')"
Write-Host "Output: $aggregatedLog"
Write-Host "Privacy Redaction: Enabled"
Write-Host ""

# Initialize counters
$stats = @{
    claude = 0
    codex = 0
    copilot = 0
    gemini = 0
    aider = 0
    total = 0
    errors = 0
    skipped = 0
}

# Helper function to convert timestamp
function ConvertTo-ISOTimestamp {
    param([datetime]$Date)
    return $Date.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
}

# Helper function to apply privacy redaction
function Invoke-PrivacyRedaction {
    param([string]$Text)
    
    # Redact API keys
    $Text = $Text -replace 'sk-[a-zA-Z0-9]{32,}', '[REDACTED_API_KEY]'
    $Text = $Text -replace '[a-zA-Z0-9]{32,}-[a-zA-Z0-9]{8,}', '[REDACTED_API_KEY]'
    
    # Redact GitHub tokens
    $Text = $Text -replace 'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'
    $Text = $Text -replace 'gho_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'
    
    # Redact passwords
    $Text = $Text -replace '(password|passwd|pwd)\s*[=:]\s*[''"]?([^''"\\s]+)', '$1=[REDACTED]'
    
    # Redact email addresses
    $Text = $Text -replace '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'
    
    return $Text
}

# Helper function to check if timestamp is in date range
function Test-InDateRange {
    param(
        [datetime]$Timestamp,
        [datetime]$Start,
        [datetime]$End
    )
    return ($Timestamp -ge $Start) -and ($Timestamp -le $End.AddDays(1))
}

# Helper function to write aggregated log entry
function Write-AggregatedLog {
    param(
        [string]$Tool,
        [string]$Type,
        [datetime]$Timestamp,
        [object]$Data,
        [string]$SessionId = ""
    )

    # Apply privacy redaction to data
    $jsonData = $Data | ConvertTo-Json -Compress -Depth 10
    $jsonData = Invoke-PrivacyRedaction -Text $jsonData
    $redactedData = $jsonData | ConvertFrom-Json

    $entry = @{
        tool = $Tool
        type = $Type
        timestamp = ConvertTo-ISOTimestamp $Timestamp
        sessionId = $SessionId
        data = $redactedData
    } | ConvertTo-Json -Compress -Depth 10

    Add-Content -Path $aggregatedLog -Value $entry
    $stats[$Tool]++
    $stats.total++
}

# Process Claude Code logs
if ($Tools -contains "claude") {
    Write-Host "[Claude] Processing logs..." -ForegroundColor Green
    try {
        # Process main history
        if (Test-Path "$HOME\.claude\history.jsonl") {
            Get-Content "$HOME\.claude\history.jsonl" | ForEach-Object {
                try {
                    $entry = $_ | ConvertFrom-Json
                    
                    # Convert Unix timestamp (milliseconds) to DateTime
                    $entryTimestamp = [DateTimeOffset]::FromUnixTimeMilliseconds($entry.timestamp).DateTime
                    
                    # Check date range
                    if (Test-InDateRange -Timestamp $entryTimestamp -Start $startDateTime -End $endDateTime) {
                        Write-AggregatedLog -Tool "claude" -Type "conversation" `
                            -Timestamp $entryTimestamp `
                            -SessionId $entry.sessionId `
                            -Data @{
                                display = $entry.display
                                project = $entry.project
                            }
                    } else {
                        $stats.skipped++
                    }
                } catch {
                    $stats.errors++
                }
            }
        }

        # Process debug logs
        Get-ChildItem "$HOME\.claude\debug\*.txt" -ErrorAction SilentlyContinue | ForEach-Object {
            $fileTime = $_.LastWriteTime
            if (Test-InDateRange -Timestamp $fileTime -Start $startDateTime -End $endDateTime) {
                $content = Get-Content $_.FullName -Raw
                $sessionId = $_.BaseName
                Write-AggregatedLog -Tool "claude" -Type "debug" `
                    -Timestamp $fileTime -SessionId $sessionId `
                    -Data @{ 
                        content = $content.Substring(0, [Math]::Min(1000, $content.Length))  # Truncate large debug logs
                        file = $_.Name 
                        full_size = $_.Length
                    }
            } else {
                $stats.skipped++
            }
        }

        Write-Host "  Processed: $($stats.claude) entries" -ForegroundColor Gray
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
        $stats.errors++
    }
}

# Process Codex logs
if ($Tools -contains "codex") {
    Write-Host "[Codex] Processing logs..." -ForegroundColor Green
    try {
        # Process history
        if (Test-Path "$HOME\.codex\history.jsonl") {
            Get-Content "$HOME\.codex\history.jsonl" | ForEach-Object {
                try {
                    $entry = $_ | ConvertFrom-Json
                    Write-AggregatedLog -Tool "codex" -Type "conversation" `
                        -Timestamp ([datetime]$entry.timestamp) -Data $entry
                } catch {
                    $stats.errors++
                }
            }
        }

        # Process application log (sample recent entries)
        if (Test-Path "$HOME\.codex\log\codex-tui.log") {
            Get-Content "$HOME\.codex\log\codex-tui.log" -Tail 1000 | ForEach-Object {
                if ($_ -match '(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})') {
                    try {
                        $entryTimestamp = [datetime]::ParseExact($Matches[1], "yyyy-MM-dd HH:mm:ss", $null)
                        Write-AggregatedLog -Tool "codex" -Type "application" `
                            -Timestamp $entryTimestamp -Data @{ log = $_ }
                    } catch {
                        $stats.errors++
                    }
                }
            }
        }

        Write-Host "  Processed: $($stats.codex) entries" -ForegroundColor Gray
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
        $stats.errors++
    }
}

# Process Copilot logs
if ($Tools -contains "copilot") {
    Write-Host "[Copilot] Processing logs..." -ForegroundColor Green
    try {
        Get-ChildItem "$HOME\.copilot\logs\session-*.log" -ErrorAction SilentlyContinue | ForEach-Object {
            $sessionId = $_.BaseName -replace '^session-', ''
            $fileTime = $_.LastWriteTime
            
            # Check if file is in date range
            if (Test-InDateRange -Timestamp $fileTime -Start $startDateTime -End $endDateTime) {
                $logEntries = @()
                Get-Content $_.FullName | ForEach-Object {
                    # Parse log line format: 2025-11-27T10:32:55.364Z [INFO] Message
                    if ($_ -match '(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\s+\[(\w+)\]\s+(.+)') {
                        try {
                            $entryTimestamp = [datetime]::Parse($Matches[1])
                            $level = $Matches[2]
                            $message = $Matches[3]
                            
                            if (Test-InDateRange -Timestamp $entryTimestamp -Start $startDateTime -End $endDateTime) {
                                $logEntries += @{
                                    timestamp = $entryTimestamp.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
                                    level = $level
                                    message = $message
                                }
                            }
                        } catch {
                            $stats.errors++
                        }
                    }
                }
                
                # Write summary entry for this session
                if ($logEntries.Count -gt 0) {
                    Write-AggregatedLog -Tool "copilot" -Type "session" `
                        -Timestamp $fileTime -SessionId $sessionId `
                        -Data @{ 
                            session_file = $_.Name
                            entry_count = $logEntries.Count
                            sample_entries = $logEntries | Select-Object -First 10
                        }
                }
            } else {
                $stats.skipped++
            }
        }

        # Process command history
        if (Test-Path "$HOME\.copilot\command-history-state.json") {
            $cmdHistoryFile = Get-Item "$HOME\.copilot\command-history-state.json"
            if (Test-InDateRange -Timestamp $cmdHistoryFile.LastWriteTime -Start $startDateTime -End $endDateTime) {
                try {
                    $cmdHistory = Get-Content $cmdHistoryFile.FullName | ConvertFrom-Json
                    Write-AggregatedLog -Tool "copilot" -Type "command-history" `
                        -Timestamp $cmdHistoryFile.LastWriteTime -Data $cmdHistory
                } catch {
                    $stats.errors++
                }
            }
        }

        Write-Host "  Processed: $($stats.copilot) entries" -ForegroundColor Gray
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
        $stats.errors++
    }
}

# Process Aider logs
if ($Tools -contains "aider") {
    Write-Host "[Aider] Processing logs..." -ForegroundColor Green
    try {
        # Process chat history
        if (Test-Path "$HOME\Documents\aider-config\history\.aider.chat.history.md") {
            $content = Get-Content "$HOME\Documents\aider-config\history\.aider.chat.history.md" -Raw
            Write-AggregatedLog -Tool "aider" -Type "chat-history" `
                -Timestamp (Get-Item "$HOME\Documents\aider-config\history\.aider.chat.history.md").LastWriteTime `
                -Data @{ content = $content; size_mb = [math]::Round((Get-Item "$HOME\Documents\aider-config\history\.aider.chat.history.md").Length / 1MB, 2) }
        }

        # Process LLM history
        if (Test-Path "$HOME\Documents\aider-config\history\.aider.llm.history") {
            $content = Get-Content "$HOME\Documents\aider-config\history\.aider.llm.history" -Raw
            Write-AggregatedLog -Tool "aider" -Type "llm-history" `
                -Timestamp (Get-Item "$HOME\Documents\aider-config\history\.aider.llm.history").LastWriteTime `
                -Data @{ content = $content; size_mb = [math]::Round((Get-Item "$HOME\Documents\aider-config\history\.aider.llm.history").Length / 1MB, 2) }
        }

        # Process input history
        if (Test-Path "$HOME\Documents\aider-config\history\.aider.input.history") {
            Get-Content "$HOME\Documents\aider-config\history\.aider.input.history" | ForEach-Object {
                Write-AggregatedLog -Tool "aider" -Type "input" `
                    -Timestamp (Get-Date) -Data @{ input = $_ }
            }
        }

        Write-Host "  Processed: $($stats.aider) entries" -ForegroundColor Gray
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
        $stats.errors++
    }
}

# Process Gemini logs
if ($Tools -contains "gemini") {
    Write-Host "[Gemini] Processing logs..." -ForegroundColor Yellow
    Write-Host "  Note: Gemini has minimal logging. Consider enabling verbose mode." -ForegroundColor Yellow

    # Check for any tmp files that might contain useful data
    Get-ChildItem "$HOME\.gemini\tmp\*" -ErrorAction SilentlyContinue | ForEach-Object {
        Write-AggregatedLog -Tool "gemini" -Type "temp-file" `
            -Timestamp $_.LastWriteTime `
            -Data @{ file = $_.Name; size = $_.Length }
        $stats.gemini++
    }

    Write-Host "  Processed: $($stats.gemini) entries" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "Aggregation Complete!" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "Total Entries: $($stats.total)"
Write-Host "  Claude:  $($stats.claude)"
Write-Host "  Codex:   $($stats.codex)"
Write-Host "  Copilot: $($stats.copilot)"
Write-Host "  Aider:   $($stats.aider)"
Write-Host "  Gemini:  $($stats.gemini)"
Write-Host "Skipped (out of date range): $($stats.skipped)"
Write-Host "Errors: $($stats.errors)"
Write-Host ""
Write-Host "Output: $aggregatedLog"

# Display file size
if (Test-Path $aggregatedLog) {
    $fileSize = (Get-Item $aggregatedLog).Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
    Write-Host "File Size: $fileSizeMB MB"
}

# Compress if requested
if ($Compress) {
    Write-Host ""
    Write-Host "Compressing logs..." -ForegroundColor Cyan
    $zipFile = "$OutputDir\aggregated-$timestamp.zip"
    Compress-Archive -Path $aggregatedLog -DestinationPath $zipFile -Force
    Remove-Item $aggregatedLog
    Write-Host "Compressed: $zipFile"
    $zipSize = (Get-Item $zipFile).Length
    $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
    Write-Host "Compressed Size: $zipSizeMB MB"
}

# Generate summary file
$summary = @{
    timestamp = Get-Date -Format "o"
    dateRange = @{
        start = $StartDate
        end = $EndDate
    }
    tools = $Tools
    statistics = $stats
    outputFile = $aggregatedLog
} | ConvertTo-Json -Depth 5

$summary | Out-File "$OutputDir\summary-$timestamp.json" -Encoding utf8

Write-Host ""
Write-Host "Run './scripts/analyze-logs.ps1 -LogFile `"$aggregatedLog`"' to analyze" -ForegroundColor Green
