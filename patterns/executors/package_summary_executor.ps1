# DOC_LINK: DOC-PAT-PACKAGE-SUMMARY-EXECUTOR-260
<#
.SYNOPSIS
Executor for PAT-PACKAGE-SUMMARY-803

.DESCRIPTION
doc_id: DOC-PAT-PACKAGE-SUMMARY-803
pattern_id: PAT-PACKAGE-SUMMARY-803

.PARAMETER InstancePath
Path to pattern instance JSON file

.EXAMPLE
.\package_summary_executor.ps1 -InstancePath instance.json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

Write-Host "▶ Executing pattern: PAT-PACKAGE-SUMMARY-803" -ForegroundColor Cyan

# Load instance
$instance = Get-Content $InstancePath | ConvertFrom-Json

# Validate pattern_id
if ($instance.pattern_id -ne "PAT-PACKAGE-SUMMARY-803") {
    throw "Invalid pattern_id. Expected: PAT-PACKAGE-SUMMARY-803, Got: $($instance.pattern_id)"
}

# TODO: Implement pattern logic
Write-Host "✓ Pattern execution complete" -ForegroundColor Green

# Return result
@{
    status = "success"
    pattern_id = "PAT-PACKAGE-SUMMARY-803"
    timestamp = (Get-Date -Format o)
} | ConvertTo-Json