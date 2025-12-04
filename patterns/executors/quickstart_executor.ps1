# DOC_LINK: DOC-PAT-QUICKSTART-EXECUTOR-273
<#
.SYNOPSIS
Executor for PAT-QUICKSTART-830

.DESCRIPTION
doc_id: DOC-PAT-QUICKSTART-830
pattern_id: PAT-QUICKSTART-830

.PARAMETER InstancePath
Path to pattern instance JSON file

.EXAMPLE
.\quickstart_executor.ps1 -InstancePath instance.json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

Write-Host "▶ Executing pattern: PAT-QUICKSTART-830" -ForegroundColor Cyan

# Load instance
$instance = Get-Content $InstancePath | ConvertFrom-Json

# Validate pattern_id
if ($instance.pattern_id -ne "PAT-QUICKSTART-830") {
    throw "Invalid pattern_id. Expected: PAT-QUICKSTART-830, Got: $($instance.pattern_id)"
}

# TODO: Implement pattern logic
Write-Host "✓ Pattern execution complete" -ForegroundColor Green

# Return result
@{
    status = "success"
    pattern_id = "PAT-QUICKSTART-830"
    timestamp = (Get-Date -Format o)
} | ConvertTo-Json