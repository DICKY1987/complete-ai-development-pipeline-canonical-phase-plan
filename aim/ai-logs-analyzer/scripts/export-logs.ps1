# DOC_LINK: DOC-SCRIPT-EXPORT-LOGS-079
# Export AI Logs to Various Formats
# Exports aggregated logs to CSV, JSON, or SQLite for external analysis

[CmdletBinding()]
param(
    [string]$LogFile = (Get-ChildItem "$HOME\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\ai-logs-analyzer\aggregated\aggregated-*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName,
    [ValidateSet("csv", "json", "sqlite")]
    [string]$Format = "csv",
    [string]$OutputDir = "$HOME\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\ai-logs-analyzer\exports"
)

$ErrorActionPreference = "Stop"

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

if (-not $LogFile -or -not (Test-Path $LogFile)) {
    Write-Host "Error: No log file found. Run aggregate-logs.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "AI Tools Log Exporter" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "Source: $LogFile"
Write-Host "Format: $Format"
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

switch ($Format) {
    "csv" {
        $outputFile = "$OutputDir\ai-logs-$timestamp.csv"
        Write-Host "Exporting to CSV..." -ForegroundColor Cyan

        # Flatten data for CSV
        $csvData = $logs | ForEach-Object {
            [PSCustomObject]@{
                Tool = $_.tool
                Type = $_.type
                Timestamp = $_.timestamp
                SessionId = $_.sessionId
                DataType = $_.data.GetType().Name
                DataSize = if ($_.data.content) { $_.data.content.Length } else { 0 }
                HasContent = [bool]$_.data.content
                FileName = $_.data.file
                LogEntry = if ($_.data.log) { $_.data.log.Substring(0, [Math]::Min(100, $_.data.log.Length)) } else { "" }
            }
        }

        $csvData | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8
        Write-Host "CSV exported: $outputFile" -ForegroundColor Green

        # Generate statistics CSV
        $statsFile = "$OutputDir\ai-logs-stats-$timestamp.csv"
        $stats = $logs | Group-Object tool | ForEach-Object {
            [PSCustomObject]@{
                Tool = $_.Name
                TotalEntries = $_.Count
                Sessions = ($_.Group | Select-Object -ExpandProperty sessionId -Unique | Where-Object { $_ }).Count
                FirstEntry = ($_.Group | Select-Object -First 1).timestamp
                LastEntry = ($_.Group | Select-Object -Last 1).timestamp
            }
        }
        $stats | Export-Csv -Path $statsFile -NoTypeInformation -Encoding UTF8
        Write-Host "Statistics CSV: $statsFile" -ForegroundColor Green
    }

    "json" {
        $outputFile = "$OutputDir\ai-logs-$timestamp.json"
        Write-Host "Exporting to JSON..." -ForegroundColor Cyan

        $export = @{
            exportTimestamp = Get-Date -Format "o"
            sourceFile = $LogFile
            totalEntries = $logs.Count
            tools = ($logs | Select-Object -ExpandProperty tool -Unique)
            logs = $logs
        }

        $export | ConvertTo-Json -Depth 10 | Out-File $outputFile -Encoding utf8
        Write-Host "JSON exported: $outputFile" -ForegroundColor Green
    }

    "sqlite" {
        $outputFile = "$OutputDir\ai-logs-$timestamp.db"
        Write-Host "Exporting to SQLite..." -ForegroundColor Cyan

        # Check if sqlite3 is available
        try {
            $sqliteVersion = sqlite3 -version 2>&1
            Write-Host "Using SQLite version: $sqliteVersion" -ForegroundColor Gray
        } catch {
            Write-Host "Error: sqlite3 not found in PATH" -ForegroundColor Red
            Write-Host "Install SQLite from: https://www.sqlite.org/download.html" -ForegroundColor Yellow
            exit 1
        }

        # Create SQL file for import
        $sqlFile = "$OutputDir\temp-import-$timestamp.sql"

        $sqlCommands = @"
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool TEXT NOT NULL,
    type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    session_id TEXT,
    data_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_tool ON logs(tool);
CREATE INDEX IF NOT EXISTS idx_type ON logs(type);
CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_session ON logs(session_id);

"@

        foreach ($log in $logs) {
            $dataJson = ($log.data | ConvertTo-Json -Compress -Depth 10).Replace("'", "''")
            $sessionId = if ($log.sessionId) { "'$($log.sessionId.Replace("'", "''"))'" } else { "NULL" }

            $sqlCommands += @"
INSERT INTO logs (tool, type, timestamp, session_id, data_json)
VALUES ('$($log.tool)', '$($log.type)', '$($log.timestamp)', $sessionId, '$dataJson');

"@
        }

        $sqlCommands | Out-File $sqlFile -Encoding utf8

        # Execute SQL
        sqlite3 $outputFile < $sqlFile

        Remove-Item $sqlFile
        Write-Host "SQLite database: $outputFile" -ForegroundColor Green
        Write-Host ""
        Write-Host "Query examples:" -ForegroundColor Cyan
        Write-Host "  sqlite3 '$outputFile' 'SELECT tool, COUNT(*) FROM logs GROUP BY tool;'"
        Write-Host "  sqlite3 '$outputFile' 'SELECT * FROM logs WHERE tool=\"claude\" LIMIT 10;'"
    }
}

Write-Host ""
Write-Host "Export complete!" -ForegroundColor Cyan
Write-Host "Output location: $OutputDir" -ForegroundColor Gray
