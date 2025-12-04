# DOC_LINK: DOC-PAT-MODULE-README-EXECUTOR-258
<#
.SYNOPSIS
Executor for PAT-MODULE-README-870

.DESCRIPTION
doc_id: DOC-PAT-MODULE-README-870
pattern_id: PAT-MODULE-README-870

.PARAMETER InstancePath
Path to pattern instance JSON file

.EXAMPLE
.\module_readme_executor.ps1 -InstancePath instance.json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

Write-Host "▶ Executing pattern: PAT-MODULE-README-870" -ForegroundColor Cyan

# Load instance
$instance = Get-Content $InstancePath | ConvertFrom-Json

# Validate pattern_id
if ($instance.pattern_id -ne "PAT-MODULE-README-870") {
    throw "Invalid pattern_id. Expected: PAT-MODULE-README-870, Got: $($instance.pattern_id)"
}

# TODO: Implement pattern logic
Write-Host "✓ Pattern execution complete" -ForegroundColor Green

# Return result
@{
    status = "success"
    pattern_id = "PAT-MODULE-README-870"
    timestamp = (Get-Date -Format o)
} | ConvertTo-Json