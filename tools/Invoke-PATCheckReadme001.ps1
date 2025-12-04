<#
.SYNOPSIS
  Wrapper for PAT-CHECK-README-001 (phase README validator).

.DESCRIPTION
  - Locates Python
  - Invokes pat_check_readme_001.py with root + report path
  - Surfaces pass/fail status and basic stats
  - Returns non-zero exit code on failure (CI / orchestrator gate)

.PARAMETER Root
  Repository root to scan. Defaults to current directory.

.PARAMETER PythonPath
  Optional explicit python executable path. Defaults to 'python'.

.PARAMETER ReportPath
  Path to JSON report. Defaults to '.reports/pat_check_readme_001.json'.

.EXAMPLE
  # Basic usage
  powershell -File tools/Invoke-PATCheckReadme001.ps1

.EXAMPLE
  # Custom root + report path
  powershell -File tools/Invoke-PATCheckReadme001.ps1 -Root "C:\repo" -ReportPath ".reports\readme_check.json"
#>

[CmdletBinding()]
param(
    [string]$Root = ".",
    [string]$PythonPath = "python",
    [string]$ReportPath = ".reports/pat_check_readme_001.json"
)

$ErrorActionPreference = "Stop"

Write-Host "=== PAT-CHECK-README-001 ===" -ForegroundColor Cyan
Write-Host "Root       : $Root"
Write-Host "PythonPath : $PythonPath"
Write-Host "ReportPath : $ReportPath"
Write-Host ""

# Resolve paths
$rootFull = (Resolve-Path -Path $Root).Path
$reportFull = Join-Path -Path $rootFull -ChildPath $ReportPath

# Ensure script exists
$scriptPath = Join-Path -Path $rootFull -ChildPath "tools\pat_check_readme_001.py"
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: pat_check_readme_001.py not found at: $scriptPath" -ForegroundColor Red
    exit 1
}

# Ensure report directory exists
$reportDir = Split-Path -Path $reportFull -Parent
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

# Build arguments
$arguments = @(
    "`"$scriptPath`"",
    "--root", "`"$rootFull`"",
    "--report", "`"$reportFull`""
)

Write-Host "Invoking: $PythonPath $($arguments -join ' ')" -ForegroundColor DarkGray

# Invoke Python
& $PythonPath $arguments
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0 -and $exitCode -ne $null) {
    Write-Host ""
    Write-Host "PAT-CHECK-README-001 FAILED (exit code $exitCode)" -ForegroundColor Red
} else {
    Write-Host ""
    Write-Host "PAT-CHECK-README-001 PASSED" -ForegroundColor Green
}

# Try to show a quick summary from the JSON report
if (Test-Path $reportFull) {
    try {
        $json = Get-Content -Raw -Path $reportFull | ConvertFrom-Json

        $results = $json.results
        if ($results) {
            Write-Host ""
            Write-Host "Summary:" -ForegroundColor Cyan

            $table = $results | Select-Object `
                @{Name="Status"; Expression={ $_.status } },
                @{Name="Phase";  Expression={ $_.title } },
                @{Name="Path";   Expression={ $_.path } },
                @{Name="Issues"; Expression={ $_.issue_count } }

            $table | Format-Table -AutoSize
        }
    } catch {
        Write-Host "Warning: Could not parse report JSON at $reportFull" -ForegroundColor Yellow
    }
}

exit $exitCode
