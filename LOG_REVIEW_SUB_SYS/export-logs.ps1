# DOC_LINK: DOC-SCRIPT-EXPORT-LOGS-PS1-001
# Export AI Logs to Various Formats
# Exports aggregated logs to CSV, JSON, or SQLite for external analysis

[CmdletBinding()]
param(
    [string]$LogFile,
    [ValidateSet("csv", "json", "sqlite", "all")]
    [string]$Format = "csv",
    [string]$OutputDir = ".\exports"
)

$ErrorActionPreference = "Stop"

# Find latest log file if not specified
if (-not $LogFile) {
    $LogFile = Get-ChildItem ".\aggregated\aggregated-*.jsonl" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1 -ExpandProperty FullName
}

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

if (-not $LogFile -or -not (Test-Path $LogFile)) {
    Write-Host "Error: No log file found. Run aggregate-logs.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "AI Tools Log Exporter" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "Source: $(Split-Path -Leaf $LogFile)"
Write-Host "Format: $Format"
Write-Host "Output: $OutputDir"
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

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$formats = if ($Format -eq "all") { @("csv", "json", "sqlite") } else { @($Format) }

foreach ($fmt in $formats) {
    switch ($fmt) {
        "csv" {
            $outputFile = "$OutputDir\ai-logs-$timestamp.csv"
            Write-Host "Exporting to CSV..." -ForegroundColor Cyan

            # Flatten data for CSV with better extraction
            $csvData = $logs | ForEach-Object {
                $displayText = ""
                if ($_.data.display) {
                    $displayText = $_.data.display.Substring(0, [Math]::Min(200, $_.data.display.Length))
                } elseif ($_.data.message) {
                    $displayText = $_.data.message.Substring(0, [Math]::Min(200, $_.data.message.Length))
                } elseif ($_.data.log) {
                    $displayText = $_.data.log.Substring(0, [Math]::Min(200, $_.data.log.Length))
                }

                [PSCustomObject]@{
                    Tool = $_.tool
                    Type = $_.type
                    Timestamp = $_.timestamp
                    SessionId = $_.sessionId
                    Display = $displayText
                    Project = $_.data.project
                    FileName = $_.data.file
                    ContentSize = if ($_.data.content) { $_.data.content.Length } else { 0 }
                }
            }

            $csvData | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8
            $csvSize = [math]::Round((Get-Item $outputFile).Length / 1KB, 2)
            Write-Host "  ✓ CSV exported: $outputFile ($csvSize KB)" -ForegroundColor Green

            # Generate statistics CSV
            $statsFile = "$OutputDir\ai-logs-stats-$timestamp.csv"
            $stats = $logs | Group-Object tool | ForEach-Object {
                [PSCustomObject]@{
                    Tool = $_.Name
                    TotalEntries = $_.Count
                    UniqueTypes = ($_.Group | Select-Object -ExpandProperty type -Unique).Count
                    Sessions = ($_.Group | Select-Object -ExpandProperty sessionId -Unique | Where-Object { $_ }).Count
                    FirstEntry = ($_.Group | Select-Object -First 1).timestamp
                    LastEntry = ($_.Group | Select-Object -Last 1).timestamp
                }
            }
            $stats | Export-Csv -Path $statsFile -NoTypeInformation -Encoding UTF8
            Write-Host "  ✓ Statistics CSV: $statsFile" -ForegroundColor Green
        }

        "json" {
            $outputFile = "$OutputDir\ai-logs-$timestamp.json"
            Write-Host "Exporting to JSON..." -ForegroundColor Cyan

            # Group by tool for better organization
            $byTool = @{}
            foreach ($log in $logs) {
                if (-not $byTool.ContainsKey($log.tool)) {
                    $byTool[$log.tool] = @()
                }
                $byTool[$log.tool] += $log
            }

            $export = @{
                metadata = @{
                    exportTimestamp = Get-Date -Format "o"
                    sourceFile = (Split-Path -Leaf $LogFile)
                    totalEntries = $logs.Count
                    tools = ($logs | Select-Object -ExpandProperty tool -Unique)
                    dateRange = @{
                        first = ($logs | ForEach-Object { try { [datetime]::Parse($_.timestamp) } catch { $null } } | Where-Object { $_ } | Sort-Object | Select-Object -First 1).ToString("o")
                        last = ($logs | ForEach-Object { try { [datetime]::Parse($_.timestamp) } catch { $null } } | Where-Object { $_ } | Sort-Object -Descending | Select-Object -First 1).ToString("o")
                    }
                }
                logsByTool = $byTool
                allLogs = $logs
            }

            $export | ConvertTo-Json -Depth 10 | Out-File $outputFile -Encoding utf8
            $jsonSize = [math]::Round((Get-Item $outputFile).Length / 1KB, 2)
            Write-Host "  ✓ JSON exported: $outputFile ($jsonSize KB)" -ForegroundColor Green
        }

        "sqlite" {
            $outputFile = "$OutputDir\ai-logs-$timestamp.db"
            Write-Host "Exporting to SQLite..." -ForegroundColor Cyan

            # Create database using .NET System.Data.SQLite (more reliable than sqlite3 CLI)
            try {
                Add-Type -AssemblyName System.Data.SQLite -ErrorAction Stop
                $connectionString = "Data Source=$outputFile;Version=3;New=True;"
                $connection = New-Object System.Data.SQLite.SQLiteConnection($connectionString)
                $connection.Open()

                $command = $connection.CreateCommand()

                # Create tables
                $command.CommandText = @"
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool TEXT NOT NULL,
    type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    session_id TEXT,
    data_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tool ON logs(tool);
CREATE INDEX IF NOT EXISTS idx_type ON logs(type);
CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_session ON logs(session_id);

CREATE TABLE IF NOT EXISTS summary (
    tool TEXT PRIMARY KEY,
    total_entries INTEGER,
    unique_sessions INTEGER,
    first_entry TEXT,
    last_entry TEXT
);
"@
                [void]$command.ExecuteNonQuery()

                # Insert logs
                $insertCmd = $connection.CreateCommand()
                $insertCmd.CommandText = "INSERT INTO logs (tool, type, timestamp, session_id, data_json) VALUES (@tool, @type, @timestamp, @session, @data)"
                
                $insertCmd.Parameters.Add((New-Object System.Data.SQLite.SQLiteParameter("@tool", [System.Data.DbType]::String)))
                $insertCmd.Parameters.Add((New-Object System.Data.SQLite.SQLiteParameter("@type", [System.Data.DbType]::String)))
                $insertCmd.Parameters.Add((New-Object System.Data.SQLite.SQLiteParameter("@timestamp", [System.Data.DbType]::String)))
                $insertCmd.Parameters.Add((New-Object System.Data.SQLite.SQLiteParameter("@session", [System.Data.DbType]::String)))
                $insertCmd.Parameters.Add((New-Object System.Data.SQLite.SQLiteParameter("@data", [System.Data.DbType]::String)))

                $transaction = $connection.BeginTransaction()
                $count = 0
                
                foreach ($log in $logs) {
                    $insertCmd.Parameters["@tool"].Value = $log.tool
                    $insertCmd.Parameters["@type"].Value = $log.type
                    $insertCmd.Parameters["@timestamp"].Value = $log.timestamp
                    $insertCmd.Parameters["@session"].Value = if ($log.sessionId) { $log.sessionId } else { [DBNull]::Value }
                    $insertCmd.Parameters["@data"].Value = ($log.data | ConvertTo-Json -Compress -Depth 10)
                    
                    [void]$insertCmd.ExecuteNonQuery()
                    $count++
                    
                    if ($count % 100 -eq 0) {
                        Write-Host "  Inserted $count entries..." -ForegroundColor Gray -NoNewline
                        Write-Host "`r" -NoNewline
                    }
                }
                
                $transaction.Commit()
                Write-Host "  Inserted $count entries                " -ForegroundColor Gray

                # Insert summary data
                $summaryCmd = $connection.CreateCommand()
                $tools = $logs | Group-Object tool
                
                foreach ($toolGroup in $tools) {
                    $sessions = ($toolGroup.Group | Select-Object -ExpandProperty sessionId -Unique | Where-Object { $_ }).Count
                    $summaryCmd.CommandText = @"
INSERT INTO summary (tool, total_entries, unique_sessions, first_entry, last_entry)
VALUES ('$($toolGroup.Name)', $($toolGroup.Count), $sessions, 
        '$($toolGroup.Group[0].timestamp)', 
        '$($toolGroup.Group[-1].timestamp)');
"@
                    [void]$summaryCmd.ExecuteNonQuery()
                }

                $connection.Close()
                
                $dbSize = [math]::Round((Get-Item $outputFile).Length / 1KB, 2)
                Write-Host "  ✓ SQLite database: $outputFile ($dbSize KB)" -ForegroundColor Green
                Write-Host ""
                Write-Host "  Query examples:" -ForegroundColor Cyan
                Write-Host "    # Total entries by tool" -ForegroundColor Gray
                Write-Host "    SELECT * FROM summary;" -ForegroundColor DarkGray
                Write-Host ""
                Write-Host "    # Recent conversations" -ForegroundColor Gray
                Write-Host "    SELECT tool, type, timestamp FROM logs WHERE type='conversation' ORDER BY timestamp DESC LIMIT 10;" -ForegroundColor DarkGray
                Write-Host ""
                Write-Host "    # Session activity" -ForegroundColor Gray
                Write-Host "    SELECT session_id, COUNT(*) as count FROM logs WHERE session_id IS NOT NULL GROUP BY session_id ORDER BY count DESC LIMIT 10;" -ForegroundColor DarkGray

            } catch {
                Write-Host "  Error: $_" -ForegroundColor Red
                Write-Host "  Note: System.Data.SQLite not available. Trying alternative method..." -ForegroundColor Yellow
                
                # Fallback: Create simple text-based format
                $txtFile = "$OutputDir\ai-logs-$timestamp.txt"
                $logs | ForEach-Object {
                    "$($_.timestamp) [$($_.tool)/$($_.type)] Session: $($_.sessionId)" | Out-File $txtFile -Append -Encoding utf8
                }
                Write-Host "  ✓ Text export (fallback): $txtFile" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Export complete!" -ForegroundColor Green
Write-Host "Output location: $OutputDir" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
