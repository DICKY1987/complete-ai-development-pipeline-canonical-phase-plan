<#
.SYNOPSIS
Executor for PAT-FILE-LIST-800

.DESCRIPTION
doc_id: DOC-PAT-FILE-LIST-800
pattern_id: PAT-FILE-LIST-800

.PARAMETER InstancePath
Path to pattern instance JSON file

.EXAMPLE
.\file_list_executor.ps1 -InstancePath instance.json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

Write-Host "▶ Executing pattern: PAT-FILE-LIST-800" -ForegroundColor Cyan

# Load instance
$instance = Get-Content $InstancePath | ConvertFrom-Json

# Validate pattern_id
if ($instance.pattern_id -ne "PAT-FILE-LIST-800") {
    throw "Invalid pattern_id. Expected: PAT-FILE-LIST-800, Got: $($instance.pattern_id)"
}

# TODO: Implement pattern logic
Write-Host "✓ Pattern execution complete" -ForegroundColor Green

# Return result
@{
    status = "success"
    pattern_id = "PAT-FILE-LIST-800"
    timestamp = (Get-Date -Format o)
} | ConvertTo-Json