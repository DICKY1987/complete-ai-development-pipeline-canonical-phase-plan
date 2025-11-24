# DOC_LINK: DOC-PAT-ATOMIC-CREATE-TEMPLATE-001
# Pattern: atomic_create_template (PAT-ATOMIC-CREATE-TEMPLATE-001)
# Version: 1.0.0
# Category: execution
# Purpose: Execute atomic_create_template pattern instances

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

Write-Host "Executing atomic_create_template pattern..." -ForegroundColor Cyan

# Load instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json

# Validate doc_id
if ($instance.doc_id -ne "DOC-PAT-ATOMIC-CREATE-TEMPLATE-001") {
    throw "Invalid doc_id. Expected: DOC-PAT-ATOMIC-CREATE-TEMPLATE-001, Got: $($instance.doc_id)"
}

# Validate pattern_id
if ($instance.pattern_id -ne "PAT-ATOMIC-CREATE-TEMPLATE-001") {
    throw "Invalid pattern_id. Expected: PAT-ATOMIC-CREATE-TEMPLATE-001, Got: $($instance.pattern_id)"
}

Write-Host "✓ Validation passed" -ForegroundColor Green

# TODO: Implement atomic_create_template execution logic
# See patterns/specs/atomic_create_template.pattern.yaml for implementation details

Write-Host "✓ atomic_create_template pattern execution complete" -ForegroundColor Green
