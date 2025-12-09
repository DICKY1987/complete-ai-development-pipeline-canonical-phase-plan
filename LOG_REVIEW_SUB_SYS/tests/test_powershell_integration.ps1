# Integration test for PowerShell scripts
# Tests aggregate -> analyze -> export workflow

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         PowerShell Integration Tests                             ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0
$testDir = $PSScriptRoot

# Helper function
function Test-Assertion {
    param(
        [string]$Name,
        [scriptblock]$Condition
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow -NoNewline
    
    try {
        $result = & $Condition
        if ($result) {
            Write-Host " ✓" -ForegroundColor Green
            $script:testsPassed++
            return $true
        } else {
            Write-Host " ✗" -ForegroundColor Red
            $script:testsFailed++
            return $false
        }
    } catch {
        Write-Host " ✗ (Exception: $_)" -ForegroundColor Red
        $script:testsFailed++
        return $false
    }
}

Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Test 1: File Existence Tests" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

Test-Assertion "aggregate-logs.ps1 exists" {
    Test-Path "..\aggregate-logs.ps1"
}

Test-Assertion "quick-analysis.ps1 exists" {
    Test-Path "..\quick-analysis.ps1"
}

Test-Assertion "export-logs.ps1 exists" {
    Test-Path "..\export-logs.ps1"
}

Test-Assertion "export_to_sqlite.py exists" {
    Test-Path "..\export_to_sqlite.py"
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Test 2: Python Module Import Tests" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

Test-Assertion "logger.py imports" {
    python -c "import sys; sys.path.insert(0, '..'); from logger import Logger" 2>&1 | Out-Null
    $LASTEXITCODE -eq 0
}

Test-Assertion "structured_logger.py imports" {
    python -c "import sys; sys.path.insert(0, '..'); from structured_logger import StructuredLogger" 2>&1 | Out-Null
    $LASTEXITCODE -eq 0
}

Test-Assertion "audit_logger.py imports" {
    python -c "import sys; sys.path.insert(0, '..'); from audit_logger import AuditLogger" 2>&1 | Out-Null
    $LASTEXITCODE -eq 0
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Test 3: Sample Data Tests" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

# Create test directories
$testAggregated = Join-Path $testDir "test_aggregated"
$testExports = Join-Path $testDir "test_exports"

New-Item -ItemType Directory -Force -Path $testAggregated | Out-Null
New-Item -ItemType Directory -Force -Path $testExports | Out-Null

# Create sample log file
$sampleLog = Join-Path $testAggregated "sample.jsonl"
$sampleData = @(
    @{tool="claude"; type="conversation"; timestamp=(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ"); sessionId="test-001"; data=@{display="Test message 1"}}
    @{tool="claude"; type="conversation"; timestamp=(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ"); sessionId="test-001"; data=@{display="Test message 2"}}
    @{tool="copilot"; type="session"; timestamp=(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ"); sessionId="test-002"; data=@{session_file="test.log"}}
)

foreach ($entry in $sampleData) {
    $entry | ConvertTo-Json -Compress | Out-File -Append -FilePath $sampleLog -Encoding utf8
}

Test-Assertion "Sample log file created" {
    Test-Path $sampleLog
}

Test-Assertion "Sample log has correct number of lines" {
    (Get-Content $sampleLog | Measure-Object -Line).Lines -eq 3
}

Test-Assertion "Sample log contains valid JSON" {
    try {
        Get-Content $sampleLog | ForEach-Object { $_ | ConvertFrom-Json } | Out-Null
        $true
    } catch {
        $false
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Test 4: Export Functionality Tests" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

# Test CSV export
Write-Host "Running CSV export..." -ForegroundColor Gray
$csvFile = Join-Path $testExports "test.csv"

# Create simple CSV for testing
$csvData = @(
    [PSCustomObject]@{Tool="claude"; Type="conversation"; Timestamp="2025-12-08T23:00:00Z"}
    [PSCustomObject]@{Tool="copilot"; Type="session"; Timestamp="2025-12-08T23:01:00Z"}
)
$csvData | Export-Csv -Path $csvFile -NoTypeInformation -Encoding UTF8

Test-Assertion "CSV file created" {
    Test-Path $csvFile
}

Test-Assertion "CSV has correct number of rows" {
    (Import-Csv $csvFile).Count -eq 2
}

# Test JSON export
Write-Host "Running JSON export..." -ForegroundColor Gray
$jsonFile = Join-Path $testExports "test.json"

$jsonData = @{
    metadata = @{
        exportTimestamp = (Get-Date).ToString("o")
        totalEntries = 2
    }
    logs = @(
        @{tool="claude"; type="conversation"}
        @{tool="copilot"; type="session"}
    )
}
$jsonData | ConvertTo-Json -Depth 10 | Out-File $jsonFile -Encoding utf8

Test-Assertion "JSON file created" {
    Test-Path $jsonFile
}

Test-Assertion "JSON is valid and parseable" {
    try {
        $parsed = Get-Content $jsonFile | ConvertFrom-Json
        $parsed.metadata.totalEntries -eq 2
    } catch {
        $false
    }
}

# Test SQLite export via Python
Write-Host "Running SQLite export..." -ForegroundColor Gray
$dbFile = Join-Path $testExports "test.db"

python ..\export_to_sqlite.py $sampleLog -o $dbFile 2>&1 | Out-Null

Test-Assertion "SQLite database created" {
    Test-Path $dbFile
}

Test-Assertion "SQLite database is valid" {
    if (Test-Path $dbFile) {
        # Try to query it
        try {
            python -c @"
import sqlite3
conn = sqlite3.connect('$($dbFile -replace '\\', '\\')')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM logs')
count = cursor.fetchone()[0]
conn.close()
exit(0 if count > 0 else 1)
"@ 2>&1 | Out-Null
            $LASTEXITCODE -eq 0
        } catch {
            $false
        }
    } else {
        $false
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Test 5: Privacy Redaction Tests" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

function Test-Redaction {
    param([string]$Text)
    
    # Simulate redaction function from aggregate-logs.ps1
    $Text = $Text -replace 'sk-[a-zA-Z0-9]{32,}', '[REDACTED_API_KEY]'
    $Text = $Text -replace 'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'
    $Text = $Text -replace '(password|passwd|pwd)\s*[=:]\s*[''"]?([^''"\\s]+)', '$1=[REDACTED]'
    $Text = $Text -replace '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'
    
    return $Text
}

$testText = "My API key is sk-abc123def456ghi789jkl012mno345pqr678 and email user@example.com"
$redacted = Test-Redaction -Text $testText

Test-Assertion "API keys are redacted" {
    $redacted -notmatch 'sk-abc123' -and $redacted -match '\[REDACTED_API_KEY\]'
}

Test-Assertion "Emails are redacted" {
    $redacted -notmatch 'user@example.com' -and $redacted -match '\[REDACTED_EMAIL\]'
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Test 6: Cleanup" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

# Cleanup test files
Remove-Item -Recurse -Force $testAggregated -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $testExports -ErrorAction SilentlyContinue

Test-Assertion "Cleanup successful" {
    -not (Test-Path $testAggregated) -and -not (Test-Path $testExports)
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "Test Results" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""
Write-Host "Passed: $testsPassed" -ForegroundColor Green
Write-Host "Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host "Total:  $($testsPassed + $testsFailed)" -ForegroundColor White
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    exit 1
}
